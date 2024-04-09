from sklearn.preprocessing import LabelEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from tensorflow.keras.utils import to_categorical
import numpy as np



class TargetEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, encoder =  LabelEncoder()):
        self.encoder = encoder

    def fit(self, X, y=None):
        # note that x is the target in this case
        self.encoder.fit(X)
        return self
    
    def transform(self, X):
        X =  X.copy()
        X = to_categorical(self.encoder.transform(X))
        return X



