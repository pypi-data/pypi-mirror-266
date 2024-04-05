import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import tensorflow as tf
cpu = tf.config.experimental.list_physical_devices(device_type='CPU')
tf.config.experimental.set_visible_devices(devices=cpu, device_type='CPU')

from .modelserver import main
