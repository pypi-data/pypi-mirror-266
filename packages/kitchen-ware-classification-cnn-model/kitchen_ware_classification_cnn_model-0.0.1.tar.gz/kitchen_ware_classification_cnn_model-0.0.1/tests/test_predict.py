
from cnn_model_package import __version__ as _version
from cnn_model_package.config import core
from cnn_model_package.predict import make_single_prediction, make_bulk_prediction

def test_make_single_pred(cup_dir):
    # given
    filename = '0193.jpg'
    expected_class =  'cup'

    # when
    outcome = make_single_prediction(image_name=filename, image_dir=cup_dir)

    # Then
    assert outcome['predictions'] is not None
    assert outcome['readable_predictions'] == expected_class
    assert outcome['version'] == _version
    
def test_make_multiple_preds(kitchen_items_dir):
    # given
    expected_class =  list

    # when
    outcome = make_bulk_prediction(images_data=core.TEST_DATA)

    # Then
    assert outcome['predictions'] is not None
    assert type(outcome['readable_predictions']) == expected_class
    assert outcome['version'] == _version