#
# https://www.analyticsvidhya.com/blog/2020/12/mlp-multilayer-perceptron-simple-overview/
#


import numpy as np
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout





#
# Dataset MNIST
#

def load_mnist():

    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    # Labels
    num_labels = len(np.unique(y_train))
    print("total de labels: {}".format(num_labels))
    print("labels:   {0}".format(np.unique(y_train)))

    # convert them to one-hot
    from tensorflow.keras.utils import to_categorical
    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test)


    # Dataset check + setup
    image_size = x_train.shape[1] 
    input_size = image_size * image_size

    print("x_train: {}".format(x_train.shape))
    print("x_test:  {}n".format(x_test.shape))

    x_train = np.reshape(x_train, [-1, input_size])
    x_train = x_train.astype('float32') / 255

    x_test = np.reshape(x_test, [-1, input_size])
    x_test = x_test.astype('float32') / 255

    print("x_train: {}".format(x_train.shape))
    print("x_test:  {}".format(x_test.shape))

    return x_train, x_test, y_train, y_test, num_labels, input_size




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


x_train, x_test, y_train, y_test, num_labels, input_size = load_mnist()

# Parameters
# Build
hidden_units = 256
dropout = 0.45


model = build_model(input_size, num_labels, hidden_units, dropout)
model.summary()

# Training
batch_size = 128 # It is the sample size of inputs to be processed at each training stage. 
model.fit(x_train, y_train, epochs=20, batch_size=batch_size)

# Evaluation
_, acc = model.evaluate(x_test, y_test, batch_size=batch_size, verbose=0)
print("\nAccuracy: %.1f%%\n" % (100.0 * acc))

model.save('./mnist_model.h5')





