# To achieve reproducibility, the code snippets below are important

# With this snippet of code, you wouldn't have to specify any other seed or random_state in numpy, 
# scikit-learn or tensorflow/keras functions, because with the source code below 
# we set globally their pseudo-random generators at a fixed value.  

# Seed value
seed_value= 0
 
# 1. Set `PYTHONHASHSEED` environment variable at a fixed value
from glob import glob
import os
os.environ['PYTHONHASHSEED']=str(seed_value)
 
# 2. Set `python` built-in pseudo-random generator at a fixed value
import random
random.seed(seed_value)
 
# 3. Set `numpy` pseudo-random generator at a fixed value
import numpy as np
np.random.seed(seed_value)
 
# 4. Set `tensorflow` pseudo-random generator at a fixed value
import tensorflow as tf
# tf.set_random_seed(seed_value)
 
# 5. Configure a new global `tensorflow` session
# from keras import backend as K
# session_conf = tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
# sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
# K.set_session(sess)


#====== importing useful libraries =========#

import pandas as pd
import cv2

from keras.models import load_model
from pathlib import Path
import joblib

import os
import typing as t
from sklearn.model_selection import train_test_split

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from tensorflow.keras.utils import load_img
from tensorflow.keras.utils import img_to_array
from tensorflow.keras.utils import normalize

import numpy as np

from config import core
from cnn_model_package import model

def load_single_img(data_folder: str, filename: str) -> pd.DataFrame:
    """Make a DataFrame with image path and filename"""
    image_list = []

    for image in glob(os.path.join(data_folder, f'{filename}')):
        # Create a DataFrame for each image and its target
        tmp = pd.DataFrame([[image, 'unknown']], columns=['image', 'target'])
        image_list.append(tmp)

    # Combine the list of DataFrames by concatenating them to form a new DataFrame
    final_df = pd.concat(image_list, ignore_index=True)
    
    return final_df


def load_img_paths(*, filename: str) -> t.Union[pd.DataFrame, pd.Series]:
    """ this function is responsible for creating the dataframe with full
    image path and target."""
    dataframe = pd.read_csv(Path(f'{core.DATA_FOLDER}/{filename}'), dtype={'Id': str})
    dataframe['image'] =  f'{core.DATA_FOLDER}/{core.IMAGES}/' + dataframe['Id'] + '.jpg'
    
    dataframe.drop('Id', axis=1, inplace=True)
    return dataframe['image']

def get_train_test_target(df: pd.DataFrame):
    x_train, x_val, y_train, y_val = train_test_split(df['image'], 
                                                      df['label'], 
                                                      test_size=0.2, 
                                                      random_state=1)
    
    # reset the index of the train and test sets for both features and target variables

    x_train.reset_index(inplace=True, drop=True)
    x_val.reset_index(inplace=True, drop=True)
    y_train.reset_index(inplace=True, drop=True)
    y_val.reset_index(inplace=True, drop=True)

    return x_train, x_val, y_train, y_val

def resize_and_create_dataset(df: pd.DataFrame , img_size):

    img_list =  []
    for image in df:
        # loading and resizing
        obj_img = load_img(image, target_size=(img_size, img_size))
        # converting images to array
        obj_arr = img_to_array(obj_img, dtype='float64')
        img_list.append(obj_arr)

    final_img_array = np.array(img_list)
        # normalizing the dataset
    dataset_norm = normalize( final_img_array, axis=-1, order=2)
    return dataset_norm

def load_encoder() -> LabelEncoder:
    encoder = joblib.load(core.ENCODER_PATH)
    return encoder


def remove_old_models(*, files_to_keep: t.List[str]) -> None:
    """ remove old models, encoders and classes."""
    do_not_delete = files_to_keep + ['__init__.py']
    for model_file in Path(core.TRAINED_MODEL_DIR).iterdir():
        if model_file.name not in do_not_delete:
            model_file.unlink()


def load_cnn_model() -> Pipeline:
    """ Load a keras model from disk"""
    build_model = load_model(core.MODEL_PATH)
    return build_model

    
    
