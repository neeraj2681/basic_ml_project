from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
import joblib
import os
from src.utils.logger import Logger

class Model(ABC):
    """Abstract base class for models."""
    
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
    
    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train the model."""
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        pass
    
    @abstractmethod
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Evaluate the model."""
        pass

class SklearnModel(Model):
    """Wrapper for scikit-learn models."""
    
    def __init__(self, model: Any):
        super().__init__()
        self.model = model
        self.logger.info(f"Initializing SklearnModel with {model.__class__.__name__}")
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train the model."""
        self.logger.info(f"Training {self.model.__class__.__name__}")
        self.model.fit(X_train, y_train)
        self.logger.info("Training completed")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        self.logger.debug("Making predictions")
        return self.model.predict(X)
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Evaluate the model."""
        self.logger.info("Evaluating model performance")
        y_pred = self.predict(X)
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, average='weighted'),
            'recall': recall_score(y, y_pred, average='weighted'),
            'f1': f1_score(y, y_pred, average='weighted')
        }
        
        self.logger.info(f"Evaluation metrics: {metrics}")
        return metrics

class ModelTrainer:
    """Class for training and evaluating multiple models."""
    
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.models = {
            'logistic_regression': SklearnModel(LogisticRegression(max_iter=1000)),
            'random_forest': SklearnModel(RandomForestClassifier()),
            'gradient_boosting': SklearnModel(GradientBoostingClassifier()),
            'svm': SklearnModel(SVC(probability=True))
        }
        self.best_model = None
        self.best_score = -np.inf
        self.logger.info("Initialized ModelTrainer with 4 models")
    
    def train_and_evaluate(self, X: pd.DataFrame, y: pd.Series, mlflow_tracking: bool = False) -> Dict[str, Dict[str, float]]:
        """Train and evaluate all models, with optional MLflow tracking."""
        self.logger.info("Starting model training and evaluation")
        from sklearn.utils import estimator_html_repr
        import mlflow
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        self.logger.info(f"Split data into train ({len(X_train)} samples) and test ({len(X_test)} samples) sets")
        results = {}
        for name, model in self.models.items():
            self.logger.info(f"\nTraining and evaluating {name}")
            # Train model
            model.train(X_train, y_train)
            # Evaluate model
            metrics = model.evaluate(X_test, y_test)
            results[name] = metrics
            # MLflow logging for each model
            if mlflow_tracking:
                with mlflow.start_run(run_name=name, nested=True):
                    mlflow.log_param("model_type", name)
                    if hasattr(model.model, 'get_params'):
                        mlflow.log_params(model.model.get_params())
                    for metric_name, value in metrics.items():
                        mlflow.log_metric(metric_name, value)
            # Update best model
            if metrics['f1'] > self.best_score:
                self.best_score = metrics['f1']
                self.best_model = model
                self.logger.info(f"New best model: {name} with F1 score: {self.best_score:.4f}")
        return results
    
    def save_best_model(self, filepath: str) -> None:
        """Save the best performing model."""
        if self.best_model is None:
            error_msg = "No model has been trained yet"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info(f"Saving best model to {filepath}")
        joblib.dump(self.best_model.model, filepath)
        self.logger.info("Model saved successfully")
    
    def load_model(self, path: str) -> None:
        """Load a model from disk."""
        self.best_model = SklearnModel(joblib.load(path)) 