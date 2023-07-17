#
# Create a new training set based on the numbers passed in parameters,
# but keep test set as default to verify the accuracy with all the other numbers
#

from tensorflow.keras.datasets import mnist
import numpy as np
import os
import pandas as pd
import yaml

params = yaml.safe_load(open("params.yaml"))["prepare"]

print(params['numbers'])


#
# Dataset MNIST
#

def load_mnist_from_keras():
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    # Labels
    num_labels = len(np.unique(y_train))
    print("total de labels: {}".format(num_labels))
    print("labels:   {0}".format(np.unique(y_train)))

    # Dataset check + setup
    image_size = x_train.shape[1]
    input_size = image_size * image_size

    print("x_train: {}".format(x_train.shape))
    print("x_test:  {}".format(x_test.shape))

    x_train = np.reshape(x_train, [-1, input_size])
    x_train = x_train.astype('float32') / 255

    x_test = np.reshape(x_test, [-1, input_size])
    x_test = x_test.astype('float32') / 255

    print("x_train: {}".format(x_train.shape))
    print("x_test:  {}".format(x_test.shape))

    return x_train, x_test, y_train, y_test


def extract_nb(masks, arr):
    mask, _ = masks[0]
    for m, i in masks:
        mask = np.ma.mask_or(mask, m)
    sub = arr[mask]
    return sub


def stringify_arr(arr):
    return ["[" + "; ".join(str(i) for i in img) + "]" for img in arr]


NB_MIN = 0
NB_MAX = 9
OUTPUT_PATH = os.path.join("datasets")

numbers = [int(n) for n in params['numbers']]
numbers.sort()
if (numbers[0] < NB_MIN or numbers[-1] > NB_MAX):
    print(f"[ERROR] No correct number as input, must be contained in [{NB_MIN}, {NB_MAX}]")
    exit()

num_selected = numbers

x_train, x_test, y_train, y_test = load_mnist_from_keras()

masks_train = [(y_train == nb, nb) for nb in num_selected]
masks_test = [(y_test == nb, nb) for nb in num_selected]

# Based on the numbers we want
new_x_train = extract_nb(masks_train, x_train)
new_y_train = extract_nb(masks_train, y_train)

# Default numbers
new_x_test = x_test
new_y_test = y_test

new_x_train = stringify_arr(new_x_train)
new_x_test = stringify_arr(new_x_test)

df_train = pd.DataFrame({'inputs': new_x_train, 'labels': new_y_train})
df_test = pd.DataFrame({'inputs': new_x_test, 'labels': new_y_test})

os.makedirs(OUTPUT_PATH, exist_ok=True)

df_train.to_csv(f'{OUTPUT_PATH}/train.csv')
df_test.to_csv(f'{OUTPUT_PATH}/test.csv')
