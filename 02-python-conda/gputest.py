#!/usr/bin/env python
# suppress tensorflow output, not useful when running computational tasks
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from timeit import default_timer as timer

# define dataset globally to use for performance tests
mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
print('mnist data loaded and split into train/test')
NUM_TRIALS = 3

def test_cpu_performance():
    print('test_cpu_performance: testing using only device /CPU:0')
    with tf.device('/CPU:0'):
        model_cpu_base = tf.keras.models.Sequential([
            tf.layers.Input(shape=(28, 28)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(1024, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10)
        ])

    for trial in range(NUM_TRIALS):
        print('=' * 70)
        print('cpu performance trial: ', trial + 1)
        
        with tf.device('/CPU:0'):
            model_cpu = tf.keras.models.clone_model(model_cpu_base)
            model_cpu.compile(optimizer='adam',
                              loss=loss_fn,
                              metrics=['accuracy'])

            start = timer()
            model_cpu.fit(x_train, y_train, epochs=5, verbose=2)
            end = timer()
            
            print('cpu elapsed time: ', end - start)
            print('=' * 70)
            print('')

        
def test_gpu_performance():
    print('test_gpu_performance: testing using single gpu device /GPU:0')
    with tf.device('/GPU:0'):
        model_gpu_base = tf.keras.models.Sequential([
            tf.layers.Input(shape=(28, 28)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(1024, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10)
        ])

    for trial in range(NUM_TRIALS):
        print('=' * 70)
        print('gpu performance trial: ', trial + 1)

        with tf.device('/GPU:0'):
                model_gpu = tf.keras.models.clone_model(model_gpu_base)
                model_gpu.compile(optimizer='adam',
                                  loss=loss_fn,
                                  metrics=['accuracy'])

                start = timer()
                model_gpu.fit(x_train, y_train, epochs=5, verbose=2)
                end = timer()
        
                print('gpu elapsed time: ', end - start)
                print('=' * 70)
                print('')

    
def main():
    print('Available Devices : ', tf.config.list_physical_devices())
    print('Num GPUs Available: ', len(tf.config.list_physical_devices('GPU')))    

    test_cpu_performance()
    test_gpu_performance()
    
if __name__ == "__main__":
    main()
