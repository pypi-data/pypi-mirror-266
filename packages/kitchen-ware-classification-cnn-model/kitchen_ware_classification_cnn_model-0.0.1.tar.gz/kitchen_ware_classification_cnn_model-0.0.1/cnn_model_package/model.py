from logging import config
from keras.models import Sequential
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten
from keras.optimizers import Adam
# from scikeras.wrappers import KerasClassifier
from cnn_model_package.config import core


def cnn_model( pool_size, 
              first_filters, 
              second_filters, 
              third_filters,
              fourth_filters, 
              dropout_conv, 
              dropout_dense, 
              kernel_size, 
              img_size):


    model =  Sequential(name="my_sequential")
    model.add(Conv2D(first_filters, kernel_size, activation='relu', input_shape= (img_size, img_size, 3)))
    model.add(Conv2D(first_filters, kernel_size, activation='relu'))
    model.add(MaxPooling2D(pool_size=pool_size))
    model.add(Dropout(dropout_conv))

    model.add(Conv2D(second_filters, kernel_size, activation='relu'))
    model.add(Conv2D(second_filters, kernel_size, activation='relu'))
    model.add(MaxPooling2D(pool_size=pool_size))
    model.add(Dropout(dropout_conv))

    model.add(Conv2D(third_filters, kernel_size, activation='relu'))
    model.add(Conv2D(third_filters, kernel_size, activation='relu'))
    model.add(MaxPooling2D(pool_size=pool_size))
    model.add(Dropout(dropout_conv))

    model.add(Conv2D(fourth_filters, kernel_size, activation='relu'))
    model.add(MaxPooling2D(pool_size=pool_size))
    model.add(Dropout(dropout_conv))


    model.add(Flatten())
    model.add(Dense(256, activation = "relu"))
    model.add(Dropout(dropout_dense))
    model.add(Dense(125, activation = "relu"))
    model.add(Dropout(dropout_dense))
    model.add(Dense(6, activation = "softmax"))


    # compile the model
    model.compile(Adam(learning_rate=0.0001), loss='binary_crossentropy',
                metrics = ['accuracy'])

    return model