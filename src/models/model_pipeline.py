from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
from features.data_preprocessing import StandardDataPreprocessor

class PreprocessingTransformer(BaseEstimator, TransformerMixin):
    """Wrapper for StandardDataPreprocessor to make it compatible with sklearn Pipeline."""
    
    def __init__(self):
        self.preprocessor = StandardDataPreprocessor()
    
    def fit(self, X, y=None):
        """Fit the preprocessor."""
        self.preprocessor.preprocess(X)
        return self
    
    def transform(self, X):
        """Transform the data using the preprocessor."""
        return self.preprocessor.preprocess(X)

def create_model_pipeline(model):
    """
    Create a scikit-learn Pipeline that combines preprocessing and model.
    
    Args:
        model: The trained model (classifier)
    
    Returns:
        sklearn.Pipeline: A pipeline that combines preprocessing and model
    """
    # Ensure the model has predict_proba
    if not hasattr(model, 'predict_proba'):
        raise ValueError("Model must support predict_proba method")
    
    return Pipeline([
        ('preprocessor', PreprocessingTransformer()),
        ('classifier', model)
    ]) 