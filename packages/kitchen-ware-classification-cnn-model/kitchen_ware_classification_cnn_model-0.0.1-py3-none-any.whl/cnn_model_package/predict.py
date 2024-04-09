from sys import version
from typing import Union
import pandas as pd

"""" This block code is used to add the parent directory to path so as to avoid any 
import dependency issues/conflicts and able to run our module script effectively"""
# BEGIN
import os, sys

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory by going one level up
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path
sys.path.append(parent_dir)
# END

"""" modules necessary for our script"""
from cnn_model_package.processing import data_manager as dm
from cnn_model_package.config import core
from cnn_model_package import __version__

#LOAD THE KERAS TRAINED MODEL 
cnn_model =  dm.load_cnn_model()



def make_single_prediction(*, image_name: str, image_dir: str):
    """ make a single predictiong using the saved model when give
    image name and directory path"""
    dataframe = dm.load_single_img(data_folder=image_dir, filename=image_name)

    final_data = dataframe['image'].reset_index(drop=True)

    dataset = dm.resize_and_create_dataset(df=final_data, img_size=core.IMAGE_SIZE)

    """ call the cnn model predict method"""
    pred = cnn_model.predict(dataset)
    readable_predictions = dict(zip(core.CLASSES, pred[0]))
    class_name = max(readable_predictions, key=readable_predictions.get)

    return dict(
        predictions = pred,
        readable_predictions = class_name,
        version = __version__
    )

def make_bulk_prediction(*, images_data: Union[pd.Series,list[str]]) -> dict:

    class_predictions = []
    """" Load the image files"""
    loaded_images = dm.load_img_paths(filename=images_data)

    """ convert images data to a dataset  """
    dataset_of_images  = dm.resize_and_create_dataset(df=loaded_images, img_size=core.IMAGE_SIZE)

    """ call the cnn model predict method"""
    pred = cnn_model.predict(dataset_of_images)

    """ Test the below block of code later"""
    for each_row in pred:
        readable_predictions = dict(zip(core.CLASSES, each_row))
        class_name = max(readable_predictions, key=readable_predictions.get)
        class_predictions.append(class_name)
     

    return dict(
        predictions = pred,
        readable_predictions = class_predictions,
        version = __version__
    )