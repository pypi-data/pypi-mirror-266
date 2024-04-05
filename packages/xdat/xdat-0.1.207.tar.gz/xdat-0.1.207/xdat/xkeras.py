import hashlib
from functools import reduce
import operator

from . import xparallel, xcv, xsettings

try:
    import tensorflow_probability as tfp
except ImportError:
    pass

from scriptine import path
import tensorflow as tf
import keras
from keras import backend as K
from keras.layers import Conv2D
from keras.layers import Layer, Dense, GlobalAveragePooling2D, GlobalMaxPooling2D, Reshape, Activation, add, multiply

from keras.models import clone_model
import numpy as np
import pandas as pd
from keras.preprocessing.image import load_img
from keras.utils import Sequence, register_keras_serializable
import imgaug.augmenters as iaa


def clone_keras_model(model):
    # Clone the model's architecture
    cloned_model = clone_model(model)

    # Compile the cloned model (use the same parameters as the original model)
    cloned_model.compile(optimizer=model.optimizer,
                         loss=model.loss,
                         metrics=model.metrics)

    return cloned_model


class ImageDataGenerator(Sequence):
    """
    batch_size=32
    target_size=(224,224)

    generator = ImageDataGenerator(df, batch_size, target_size)
    model.fit(generator, epochs=epochs)

    generator_for_prediction = ImageDataGenerator(df, batch_size, target_size, target_col=None, shuffle=False)
    predictions = model.predict(generator_for_prediction)

    There's a convenience function to put everything in memory (undo generator):
    X, y = generator.as_full_memory()
    """

    def __init__(self, dataframe, batch_size, target_size_hw=None, target_size_wh=None, shuffle=True, image_path_col='image_path', target_col='target', weight_col=None, process_image=None, aug_y=None, mult_input_proc=None, file_cache=None, rgb=True, scale_colors=True, with_aug=False, aug_seq=None, zoom=1, mode=None, check_cache_on_init=True, n_jobs=-1, parallel_one_epoch_only=True, dtype=np.float16):
        """
        :param dataframe:
        :param batch_size:
        :param target_size_hw: (height, width)
        :param target_size_wh: (width, height)
        :param shuffle: should be False for predictions
        :param image_path_col: where to find images
        :param target_col: target
        :param weight_col: weight (optional)
        :param process_image: how to process the image (optional)
        :param aug_y: how to augment y (in training only)
        :param zoom: how much to zoom in center (2 is twice as much)
        :param file_cache: (str, optional) path to save file cache
        :param mode: 'fit', 'val', 'predict-train', 'predict-test', 'memory'
        """

        if weight_col:
            assert target_col

        self.dataframe = dataframe
        self.batch_size = batch_size

        assert sum([bool(target_size_wh), bool(target_size_hw)]) == 1
        if target_size_wh:
            target_size_hw = tuple(reversed(target_size_wh))

        self.target_size_hw = target_size_hw
        self.target_size_wh = tuple(reversed(self.target_size_hw))

        self.shuffle = shuffle
        self.image_path_col = image_path_col
        self.target_col = target_col
        self.weight_col = weight_col
        self.file_cache = file_cache
        self.rgb = rgb
        self.scale_colors = scale_colors
        self.with_aug = with_aug
        self.zoom = zoom
        self.mult_input_proc = mult_input_proc
        self.check_cache_on_init = check_cache_on_init
        self.n_jobs = n_jobs
        self.parallel_one_epoch_only = parallel_one_epoch_only
        self.dtype = dtype
        self.very_first_batch = True

        self.aug_seq = aug_seq
        if self.aug_seq is None:
            self.aug_seq = iaa.geometric.Affine(
                scale=(1.0, 1.5),
                rotate=(0, 360),
                shear=(-20, 20),
            )

        if self.file_cache:
            self.file_cache = path(self.file_cache)
            self.file_cache.ensure_dir()

        self.indices = np.arange(len(dataframe))
        if process_image is not None:
            self.process_image = process_image

        self.aug_y = aug_y

        if mode == 'fit':
            self.set_mode_fit()
        elif mode in ['val', 'validation']:
            self.set_mode_validation()
        elif mode == 'predict-train':
            self.set_mode_predict(new_dataset=False)
        elif mode in ['predict-test', 'test']:
            self.set_mode_predict(new_dataset=True)
        elif mode == 'memory':
            self.set_mode_memory()
        else:
            raise ValueError(mode)

        print(f'- INFO: generator mode={mode}, shuffle={"on" if self.shuffle else "off"}, aug={"on" if self.with_aug else "off"}, aug_y={"on" if self.aug_y else "off"}, parallel={"off" if self.n_jobs == 1 else "on"}, file_cache={"on" if self.file_cache else "off"}')

        if self.shuffle:
            np.random.shuffle(self.indices)

    def set_mode_fit(self):
        self.shuffle = True
        if self.with_aug:
            self.file_cache = False

        self.n_jobs = -1
        assert self.target_col is not None

    def set_mode_validation(self):
        self.shuffle = False
        self.n_jobs = -1
        self.with_aug = False
        self.aug_y = None

    def set_mode_predict(self, new_dataset=True):
        self.shuffle = False
        self.n_jobs = -1 if new_dataset else 1
        self.target_col = None
        self.with_aug = False
        self.aug_y = None

    def set_mode_memory(self):
        self.shuffle = False
        self.n_jobs = -1

    def __len__(self):
        return int(np.ceil(len(self.dataframe) / float(self.batch_size)))

    def __getitem__(self, idx):
        batch_indices = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_rows = [self.dataframe.iloc[i] for i in batch_indices]
        df_batch = pd.DataFrame(batch_rows)

        if self.very_first_batch and self.n_jobs != 1 and self.check_cache_on_init:
            num_cache = sum([self.load_and_preprocess_image(p, is_from_cache=True) for p in df_batch[self.image_path_col].tolist()])
            if num_cache == len(df_batch):
                print("- INFO: disabling parallel, all images in cache")
                self.n_jobs = 1

        self.very_first_batch = False

        images = xparallel.x_on_iter(batch_rows, lambda row: self.load_and_preprocess_image(row[self.image_path_col]), with_tqdm=False, n_jobs=self.n_jobs)
        images = np.array(images)
        X = images

        if self.mult_input_proc:
            X = self.mult_input_proc(df_batch, images)
            assert isinstance(X, list), type(X)
            assert len(X) > 1, len(X)

        if self.target_col is None:
            if not self.mult_input_proc:
                return X

            assert isinstance(X, list), type(X)
            assert len(X) > 1, len(X)
            # TODO: FIX THIS HELL:
            return X, df_batch.index.values

        res = [X]

        if isinstance(self.target_col, list) or isinstance(self.target_col, tuple):
            yy = df_batch[self.target_col].to_numpy()
            yy = [c for c in yy.T]
            yy2 = []
            for y in yy:
                if isinstance(y[0], list):
                    y = np.array(y.tolist(), dtype=self.dtype)
                else:
                    y = np.array(y, dtype=self.dtype)
                yy2.append(y)

            labels = yy2
        else:
            labels = df_batch[self.target_col].to_numpy()
            if isinstance(labels[0], list):
                labels = np.array(labels.tolist())
            labels = self.wrap_aug_y(labels)

        res.append(labels)

        if self.weight_col:
            if isinstance(self.weight_col, dict):
                weights = {k:df_batch[v].to_numpy() for k, v in self.weight_col.items()}
            else:
                weights = df_batch[self.weight_col].to_numpy()
            res.append(weights)

        return tuple(res)

    def as_full_memory(self, n_jobs=-1):
        self.indices = np.arange(len(self.dataframe))

        i0 = self[0]
        if self.target_col is not None:
            i0 = i0[0]

        img_shape = list(i0.shape)[1:]
        n_samples = len(self.dataframe)
        full_shape = [n_samples] + list(img_shape)
        mem_size = reduce(operator.mul, full_shape, 1)
        mem_size_mb = 4*mem_size / 1000000
        print(f"{mem_size_mb:.1f}Mb")

        X = np.zeros(full_shape, dtype=np.float32)

        def calc(batch_num):
            X_batch = self[batch_num]
            return batch_num, X_batch

        num_batches = len(self)
        for batch_num, X_batch in xparallel.x_on_iter_as_gen(range(num_batches), calc, total=num_batches, n_jobs=n_jobs):
            if self.target_col is not None:
                X_batch, y_batch = X_batch

            start_index = batch_num*self.batch_size
            X[start_index:start_index + X_batch.shape[0], :, :, :] = X_batch

        if not self.target_col:
            return X

        res = [X]
        res.append(self.dataframe[self.target_col])
        if self.weight_col:
            res.append(self.dataframe[self.weight_col])

        return tuple(res)

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)

        if self.n_jobs != 1 and self.file_cache and self.parallel_one_epoch_only and not self.with_aug:
            print('- INFO: disabling parallelism in generator')
            self.n_jobs = 1

    def load_and_preprocess_image(self, image_path, is_from_cache=False):
        if self.file_cache:
            hash = hashlib.md5(image_path.encode()).hexdigest()
            hash_path = self.file_cache.joinpath(f"{hash}.npy")
            if hash_path.exists():
                if is_from_cache:
                    return True

                return np.load(hash_path)

            if is_from_cache:
                return False

            val = self._load_and_preprocess_image_do(image_path)
            np.save(hash_path, val)
            return val

        else:
            if is_from_cache:
                return False

            val = self._load_and_preprocess_image_do(image_path)
            return val

    def do_augmentation(self, img):
        img = self.aug_seq(images=[img])[0]
        return img

    def _load_and_preprocess_image_do(self, image_path):
        img = load_img(image_path)

        if self.zoom > 1:
            img = xcv.crop_zoom_center(img, factor=self.zoom)

        if self.rgb:
            img = img.convert('RGB')

        img = np.array(img)

        if self.with_aug:
            img = self.do_augmentation(img)

        img = xcv.resize_and_center_crop(img, self.target_size_wh)

        if self.scale_colors:
            img = img / 255

        img = self.process_image(img)
        assert img.shape[:2] == self.target_size_hw, img.shape
        return img.astype(np.float32)

    def process_image(self, img):
        return img

    def wrap_aug_y(self, y):
        if not self.aug_y:
            return y

        return self.aug_y(y)


class SpatialAttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(SpatialAttentionLayer, self).__init__(**kwargs)
        # Initialize the Conv2D layer with a single filter for spatial attention
        self.conv2d = Conv2D(1, (3, 3), activation='sigmoid', padding='same')

    def call(self, input_feature):
        # Apply the Conv2D layer to learn spatial attention
        attention = self.conv2d(input_feature)
        return attention * input_feature

    def get_config(self):
        return super(SpatialAttentionLayer, self).get_config()


class ChannelAttentionLayer(Layer):
    def __init__(self, ratio=8, **kwargs):
        super(ChannelAttentionLayer, self).__init__(**kwargs)
        self.ratio = ratio
        self.shared_layer_one = None
        self.shared_layer_two = None

    def build(self, input_shape):
        channel = input_shape[-1]
        # Initialize shared layers in the build method to ensure the channel dimension is known
        self.shared_layer_one = Dense(channel // self.ratio, activation='relu', kernel_initializer='he_normal', use_bias=True, bias_initializer='zeros')
        self.shared_layer_two = Dense(channel, kernel_initializer='he_normal', use_bias=True, bias_initializer='zeros')
        super(ChannelAttentionLayer, self).build(input_shape)

    def call(self, input_feature):
        channel = input_feature.shape[-1]
        avg_pool = GlobalAveragePooling2D()(input_feature)
        avg_pool = Reshape((1, 1, channel))(avg_pool)
        avg_pool = self.shared_layer_one(avg_pool)
        avg_pool = self.shared_layer_two(avg_pool)

        max_pool = GlobalMaxPooling2D()(input_feature)
        max_pool = Reshape((1, 1, channel))(max_pool)
        max_pool = self.shared_layer_one(max_pool)
        max_pool = self.shared_layer_two(max_pool)

        attention = add([avg_pool, max_pool])
        attention = Activation('sigmoid')(attention)

        return multiply([input_feature, attention])

    def get_config(self):
        config = super(ChannelAttentionLayer, self).get_config()
        config.update({"ratio": self.ratio})
        return config


class QuantileLayer(tf.keras.layers.Layer):
    """
    Computes quantiles for each channel, preserving the batch dimension.
    Input shape: (batch_size, height, width, channels)
    Output shape: (batch_size, channels, num_quantiles)
    """

    def __init__(self, num_quantiles, with_ends=False, **kwargs):
        super(QuantileLayer, self).__init__(**kwargs)
        self.num_quantiles = num_quantiles
        self.with_ends = with_ends

        if with_ends:
            self.quantiles = tf.linspace(0.0, 1.0, self.num_quantiles)
        else:
            self.quantiles = tf.linspace(0.0, 1.0, self.num_quantiles+2)[1:-1]

    def call(self, inputs):
        input_shape = tf.shape(inputs)
        batch_size = input_shape[0]
        channels = input_shape[-1]

        # Flatten the spatial dimensions and keep channels separate
        inputs_flat = tf.reshape(inputs, [batch_size, -1, channels])

        quantiles = tf.cast(self.quantiles, inputs.dtype)


        quantile_values = tf.map_fn(lambda x: tfp.stats.percentile(inputs_flat[..., x], quantiles * 100, axis=1, interpolation='linear'), elems=tf.range(channels), dtype=inputs.dtype)

        # quantile_values shape: [channels, num_quantiles, batch_size]

        # output shape is [batch_size, channels, num_quantiles]
        quantile_values = tf.transpose(quantile_values, [2, 0, 1])
        return quantile_values

    def compute_output_shape(self, input_shape):
        out_shape = (input_shape[0], input_shape[-1], self.num_quantiles)
        return out_shape

    @classmethod
    def test_layer(cls):
        l = QuantileLayer(num_quantiles=10)
        x1 = tf.random.normal(shape=(1, 5, 5, 1)) * 10
        x2 = tf.random.normal(shape=(1, 5, 5, 1))
        x = tf.concat([x1, x2], axis=3)
        y = l(x)
        print(y)


class ShuffleLayer(Layer):
    def __init__(self, **kwargs):
        super(ShuffleLayer, self).__init__(**kwargs)

    def call(self, inputs, training=None):
        if training:
            # Shuffle along the batch dimension
            return tf.random.shuffle(inputs)
        else:
            return inputs


class GradientReversalLayer(tf.keras.layers.Layer):
    """
    Useful for adversarial networks.
    """

    def __init__(self, alpha=-1.0, **kwargs):
        super().__init__(**kwargs)
        self.alpha = alpha
        self.is_enabled = True

    def call(self, inputs, *args, **kwargs):
        if self.is_enabled:
            return self.grad_reversal(inputs)
        else:
            return tf.identity(inputs)

    @tf.custom_gradient
    def grad_reversal(self, x):
        identity = tf.identity(x)
        return identity, self.custom_grad

    def custom_grad(self, dy):
        if self.is_enabled:
            return self.alpha * dy
        else:
            return dy

    def enable(self):
        self.is_enabled = True

    def disable(self):
        self.is_enabled = False

    def toggle(self):
        self.is_enabled = not self.is_enabled


class RGBtoHSVLayer(Layer):
    def __init__(self, **kwargs):
        super(RGBtoHSVLayer, self).__init__(**kwargs)

    def call(self, inputs):
        return tf.image.rgb_to_hsv(inputs)


class BestValReduceLRCallback(keras.callbacks.Callback):
    """
    Checks validation loss, if increases, can either reduce learning rate or stop the training.

    Either way, it ends the training with weights of epoch with min validation loss.
    """

    def __init__(self, start_on=1, patience=0, reduce_rate=0.4, min_lr=1e-5, stop_on_incr=False, metric='val_loss', save_best=None):
        super().__init__()
        self.start_on = start_on
        self.patience = patience
        self.reduce_rate = reduce_rate   # closer to 0, faster the reduce rate.
        self.min_lr = min_lr
        self.stop_on_incr = stop_on_incr
        self.metric = metric
        self.save_best = save_best

        self.best_weights = None        # best weights
        self.wait = None                # how much we are waiting (patiently)
        self.best_loss = None           # our best loss thus far
        self.best_epoch = None

    def on_train_begin(self, logs=None):
        self.wait = 0
        self.best_loss = np.Inf

    def on_train_end(self, logs=None):
        if self.save_best and isinstance(self.save_best, str):
            self.model.save(self.save_best)

        elif self.save_best is True:
            self.model.save(xsettings.OUTPUT_PATH.joinpath("best_model.h5"))

    def rollback_to_best(self):
        self.model.set_weights(self.best_weights)

    def on_epoch_end(self, epoch, logs=None):
        current_val_loss = logs.get(self.metric)
        if np.less(current_val_loss, self.best_loss):
            self.best_loss = current_val_loss
            self.wait = 0
            self.best_weights = self.model.get_weights()
            self.best_epoch = epoch
        else:
            self.wait += 1
            if epoch < self.start_on:
                pass
            elif self.wait >= self.patience:
                # Restoring model weights from the end of the best epoch.
                self.rollback_to_best()

                if self.stop_on_incr:
                    self.model.stop_training = True
                    print("\nBestValReduceLRCallback: validation increased, restoring best weights and stopping the training.")
                    return

                # Reduce learning rate
                lr = float(keras.backend.get_value(self.model.optimizer.lr))
                new_lr = max(lr * self.reduce_rate, self.min_lr)
                if new_lr < lr:
                    keras.backend.set_value(self.model.optimizer.lr, new_lr)
                    print(f"\nBestValReduceLRCallback: Restoring best weights & reduced learning rate to {new_lr:.10f} (best {self.metric}={self.best_loss:.4f}, on epoch={self.best_epoch})\n")

                else:
                    print(f"\nBestValReduceLRCallback: reached minimum LR, but still not improving val. Restoring best weights & stopping the training")
                    self.model.stop_training = True
                    return

                self.wait = 0


@register_keras_serializable()
def mape_loss(y_true, y_pred):
    epsilon = 1e-10  # Small constant to avoid division by zero
    return tf.reduce_mean(tf.abs(100*(y_true - y_pred) / (y_true + epsilon)))
    # return tf.reduce_mean(tf.abs((y_true - y_pred) / y_true))


@register_keras_serializable()
def ordinal_crossentropy_loss(y_true, y_pred):
    """
    Ordinal cross-entropy loss for ordinal regression.
    NOTE: NOT TESTED (GPT)

    Parameters:
    - y_true: A tensor of true labels, shape (batch_size, 1),
              where each label is an integer representing the ordinal class.
    - y_pred: A tensor of predicted probabilities, shape (batch_size, N),
              where N is the number of ordinal classes. Each row represents
              the cumulative probability of being in or below a given class.

    Returns:
    - A scalar tensor representing the average loss.
    """
    # Ensure y_pred is cumulative
    y_pred_cumulative = tf.cumsum(y_pred, axis=1)

    # Convert y_true to a binary matrix representation
    y_true_expanded = tf.cast(tf.range(1, tf.shape(y_pred)[1] + 1), dtype=y_true.dtype)
    y_true_expanded = tf.less_equal(y_true_expanded, tf.cast(tf.expand_dims(y_true, -1), y_true_expanded.dtype))
    y_true_expanded = tf.cast(y_true_expanded, dtype=y_pred.dtype)

    # Compute binary cross-entropy loss for each ordinal step
    losses = tf.keras.losses.binary_crossentropy(y_true_expanded, y_pred_cumulative, from_logits=False)

    # Average loss over all ordinal steps
    return tf.reduce_mean(losses)


@register_keras_serializable()
def r_squared(y_true, y_pred):
    SS_res =  K.sum(K.square(y_true - y_pred))
    SS_tot = K.sum(K.square(y_true - K.mean(y_true)))
    return (1 - SS_res/(SS_tot + K.epsilon()))


@register_keras_serializable()
def p_corr(y_true, y_pred):
    """
    Pearson correlation coefficient as a metric.
    """
    # Subtract the mean from both true and predicted values
    y_true_mean_subtracted = y_true - tf.reduce_mean(y_true)
    y_pred_mean_subtracted = y_pred - tf.reduce_mean(y_pred)

    # Calculate the numerator: the dot product of deviations
    numerator = tf.reduce_sum(y_true_mean_subtracted * y_pred_mean_subtracted)

    # Calculate the denominator
    denominator = tf.sqrt(tf.reduce_sum(tf.square(y_true_mean_subtracted))) * tf.sqrt(
        tf.reduce_sum(tf.square(y_pred_mean_subtracted)))

    # Pearson correlation coefficient
    correlation = numerator / denominator

    # To avoid NaN in division, handle cases where denominator is zero
    return tf.where(tf.math.is_nan(correlation), tf.zeros_like(correlation), correlation)
