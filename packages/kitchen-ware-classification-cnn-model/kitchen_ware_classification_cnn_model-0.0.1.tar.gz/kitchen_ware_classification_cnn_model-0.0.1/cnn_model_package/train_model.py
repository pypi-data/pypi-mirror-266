from logging import config
import joblib
from keras.callbacks import ReduceLROnPlateau, ModelCheckpoint


from cnn_model_package.config import core
from cnn_model_package.processing import data_manager as dm 
from cnn_model_package.processing import preprocessors as pp
from cnn_model_package import model as m 


checkpoint = ModelCheckpoint(core.MODEL_PATH, monitor='accuracy', verbose=1,
                             save_best_only=True, mode='max')

reduce_lr = ReduceLROnPlateau(monitor='accuracy', factor=0.5, patience=1,
                                   verbose=1, mode='max', min_lr=0.00001)


callbacks_list = [checkpoint, reduce_lr]


def run_training(save_results: bool = True):
    """ train a convolutional neural network"""

    train_data = dm.load_img_paths(filename = core.TRAINING_DATA)
    x_train, x_val, y_train, y_val = dm.get_train_test_target(train_data)
    x_train_norm = dm.resize_and_create_dataset(x_train,core.IMAGE_SIZE)
    x_val_norm = dm.resize_and_create_dataset(x_val,core.IMAGE_SIZE)

    encoder =  pp.TargetEncoder()
    encoder.fit(y_train)
    train_y =  encoder.transform(y_train)
    val_y =  encoder.transform(y_val)

    # let's compile the model
    model = m.cnn_model(
        kernel_size = (3,3),
        pool_size= (2,2),
        first_filters = 32,
        second_filters = 64,
        third_filters = 128,
        fourth_filters = 256,
        dropout_conv = 0.3,
        dropout_dense = 0.3,
        img_size =  core.IMAGE_SIZE
    )

    model.fit(x = x_train_norm, y = train_y,
                        batch_size=core.BATCH_SIZE,
                        epochs=core.EPOCHS,
                        validation_data=(x_val_norm, val_y),
                        verbose=2,
                        callbacks=callbacks_list)

if __name__ == '__main__':
    run_training(save_results=True)




