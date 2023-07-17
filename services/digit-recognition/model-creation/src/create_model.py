import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout


def unstringify_arr(df):
    unstringify = lambda li: [float(i) for i in li[1:-1].split('; ')]  # noqa: E731
    return np.array([unstringify(li) for li in df])


# Load le dataset mnist depuis le csv custom
def load_mnist_from_csv(train_file, test_file):
    df_train = pd.read_csv(train_file)
    df_test = pd.read_csv(test_file)

    x_train_str, y_train_num = df_train['inputs'], df_train['labels']
    x_test_str, y_test_num = df_test['inputs'], df_test['labels']

    x_train = unstringify_arr(x_train_str)
    x_test = unstringify_arr(x_test_str)

    print(x_train.shape, x_test.shape)

    input_size = x_train.shape[1]
    num_labels = np.unique(y_test_num).shape[0]

    # convert them to one-hot
    y_train = to_categorical(y_train_num, num_classes=num_labels)
    y_test = to_categorical(y_test_num, num_classes=num_labels)

    return x_train, x_test, y_train, y_test, input_size, num_labels


#
#  Building the model
#

def build_model(input_size, num_labels, hidden_units, dropout):
    # MLP with ReLU and Dropout
    model = Sequential()

    model.add(Dense(hidden_units, input_dim=input_size))
    model.add(Activation('relu'))
    model.add(Dropout(dropout))

    model.add(Dense(hidden_units))
    model.add(Activation('relu'))
    model.add(Dropout(dropout))

    model.add(Dense(num_labels))

    # Activation for output layer
    model.add(Activation('softmax'))

    # Optimization
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return model


#
#   Main
#
DATASETS_PATH = os.path.join("datasets")
GRAPHS_PATH = os.path.join("graphs")

# Load data from CSV
ftrain = f"{DATASETS_PATH}/train.csv"
ftest = f"{DATASETS_PATH}/test.csv"

x_train, x_test, y_train, y_test, input_size, num_labels = load_mnist_from_csv(ftrain, ftest)

# Train
hidden_units = 256
dropout = 0.45

# print(input_size, num_labels)
model = build_model(input_size, num_labels, hidden_units, dropout)
model.summary()

# Training
batch_size = 128
history = model.fit(x_train, y_train, epochs=15, batch_size=batch_size)

# Save accuracy and loss graphs
os.makedirs(GRAPHS_PATH, exist_ok=True)

plt.plot(history.history['accuracy'], color='b', label='train set')
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend()
plt.savefig(f"{GRAPHS_PATH}/model_accuracy.jpg")
plt.clf()

plt.plot(history.history['loss'], color='r', label='train set')
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend()
plt.savefig(f'{GRAPHS_PATH}/model_loss.jpg')
plt.clf()

# Evaluation
loss, acc = model.evaluate(x_test, y_test, batch_size=batch_size, verbose=0)
print("\nAccuracy on test set : %.1f%%\n" % (100.0 * acc))

model.save('mnist_model.h5')
