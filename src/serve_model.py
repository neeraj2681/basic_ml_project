import mlflow
import mlflow.sklearn
import os
from dotenv import load_dotenv
import logging
from sklearn.base import BaseEstimator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def serve_model():
    # Load environment variables
    load_dotenv()
    
    # Set the MLflow tracking URI (if using remote tracking)
    # mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
    
    # Get the model URI from the latest run
    experiment_name = "CustomerChurnPipeline"
    experiment = mlflow.get_experiment_by_name(experiment_name)
    
    if experiment is None:
        raise ValueError(f"Experiment '{experiment_name}' not found")
    
    # Get the latest run
    runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
    if runs.empty:
        raise ValueError("No runs found in the experiment")
    
    latest_run = runs.iloc[0]
    model_uri = f"runs:/{latest_run.run_id}/best_model"
    
    # Load the model and wrap it
    model = mlflow.sklearn.load_model(model_uri)
    wrapped_model = ProbabilityModelWrapper(model)
    
    # Serve the wrapped model
    logger.info(f"Serving model from: {model_uri}")
    mlflow.sklearn.serve_model(
        model=wrapped_model,  # Use the wrapped model directly
        port=5010,  # Match the port in test_served_model.py
        host="0.0.0.0"  # Allow external connections
    )

if __name__ == "__main__":
    serve_model() 