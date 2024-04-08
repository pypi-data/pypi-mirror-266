import os
import gc
import tensorflow as tf
import keras
import keras.mixed_precision


def use_gpu(use_gpu=True, mixed_precision=True):
    """
    :param use_gpu: when True, sets up the GPU (and makes sure it's there)
    :param mixed_precision: when True, enables mixed-precision speedup
    """

    physical_devices = tf.config.list_physical_devices('GPU')
    if use_gpu and len(physical_devices):
        print(f"TF version: {tf.__version__}")
        # print(f"keras version: {keras.__version__}")

        for gpu in physical_devices:
            print(f"Found GPU: {gpu}")
            try:
                tf.config.experimental.set_memory_growth(gpu, True)
            except RuntimeError:
                pass

        if mixed_precision:
            policy = keras.mixed_precision.Policy('mixed_float16')
            keras.mixed_precision.set_global_policy(policy)

    else:
        print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
        assert not use_gpu
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


def free_memory():
    keras.backend.clear_session()
    gc.collect()
    keras.backend.clear_session()
    gc.collect()
