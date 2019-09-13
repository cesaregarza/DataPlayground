import tensorflow as tf
import numpy as np
import csv
import functools
import pandas as pd

test_data_path = "testdata_20.csv"
train_data_path = "traindata_80.csv"
# test_data = pd.read_csv(test_data_path)
# train_data = pd.read_csv(train_data_path)

LABEL_COLUMN = 'move'
LABELS = [0, 1, 2, 3]

def get_dataset(file_path, **kwargs):
    dataset = tf.data.experimental.make_csv_dataset(
        file_path,
        batch_size = 5,
        label_name = LABEL_COLUMN,
        num_epochs = 1,
        ignore_errors = True,
        **kwargs)
    return dataset

raw_train_data = get_dataset(train_data_path)
raw_test_data = get_dataset(test_data_path)