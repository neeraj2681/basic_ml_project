from sklearn.base import BaseEstimator
import numpy as np

class ProbabilityModelWrapper(BaseEstimator):
    """Wrapper class to ensure predict_proba is used for predictions."""
    
    def __init__(self, model):
        self.model = model
    
    def predict(self, X):
        """Return class predictions."""
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """Return probability predictions."""
        return self.model.predict_proba(X)
    
    def fit(self, X, y=None):
        """Fit the model."""
        self.model.fit(X, y)
        return self
    
    def get_params(self, deep=True):
        """Get parameters for this estimator."""
        return {'model': self.model}
    
    def set_params(self, **parameters):
        """Set parameters for this estimator."""
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self 