import os

# define folder directories and path
PWD = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.abspath(os.path.join(PWD, '..'))
DATASET_DIR = os.path.join(PACKAGE_ROOT, 'datasets')
TRAINED_MODEL_DIR = os.path.join(PACKAGE_ROOT, 'trained_models')
DATA_FOLDER = os.path.join(DATASET_DIR, 'kitchenware-classification')

# For model persisting
MODEL_NAME = 'cnn_model'
CLASSES_NAME = 'classes'
ENCODER_NAME =  'encoder'

CLASSES = [
    'cup', 
    'fork', 
    'glass', 
    'knife',
    'plate', 
    'spoon', 
]

# Model fitting parameters
IMAGE_SIZE = 150 # change  to 150 for final model
BATCH_SIZE =  10
EPOCHS = int(os.environ.get('EPOCHS', 45)) # change to 45 for final model

# training data
TRAINING_DATA = 'train.csv'
TEST_DATA = 'test.csv'
IMAGES = 'images'

with open(os.path.join(PACKAGE_ROOT, 'VERSION')) as _version_file:
    _version = _version_file.read().strip()

MODEL_FILE_NAME =  f'{MODEL_NAME}_{_version}.keras'
MODEL_PATH =  os.path.join(TRAINED_MODEL_DIR, MODEL_FILE_NAME)

CLASSES_FILE_NAME = f'{CLASSES_NAME}_{_version}.pkl'
CLASSES_PATH = os.path.join(TRAINED_MODEL_DIR, CLASSES_FILE_NAME)

ENCODER_FILE_NAME = f'{ENCODER_NAME}_{_version}.pkl'
ENCODER_PATH = os.path.join(TRAINED_MODEL_DIR, ENCODER_FILE_NAME)