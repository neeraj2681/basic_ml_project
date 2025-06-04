import pytest
import pandas as pd
import numpy as np
from src.data.data_ingestion import CSVDataIngestion
from src.features.data_preprocessing import StandardDataPreprocessor
from src.models.model_trainer import ModelTrainer, SklearnModel
from sklearn.linear_model import LogisticRegression
import requests
import json
from src.data.sample_data_generator import generate_customer_data
import logging
import subprocess
import time
import os
import signal
import mlflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data():
    """Create a small test dataset for customer churn."""
    return pd.DataFrame({
        'customer_id': [f'CUST{i:06d}' for i in range(5)],
        'tenure': [1, 12, 24, 36, 48],
        'monthly_charges': [50, 65, 80, 95, 110],
        'total_charges': [50, 780, 1920, 3420, 5280],
        'contract_type': ['Month-to-month', 'One year', 'Two year', 'Month-to-month', 'One year'],
        'payment_method': ['Electronic check', 'Bank transfer', 'Credit card', 'Mailed check', 'Electronic check'],
        'paperless_billing': ['Yes', 'No', 'Yes', 'No', 'Yes'],
        'internet_service': ['DSL', 'Fiber optic', 'No', 'DSL', 'Fiber optic'],
        'online_security': ['Yes', 'No', 'No internet service', 'Yes', 'No'],
        'online_backup': ['No', 'Yes', 'No internet service', 'Yes', 'No'],
        'device_protection': ['Yes', 'No', 'No internet service', 'No', 'Yes'],
        'tech_support': ['No', 'Yes', 'No internet service', 'Yes', 'No'],
        'streaming_tv': ['Yes', 'No', 'No internet service', 'No', 'Yes'],
        'streaming_movies': ['No', 'Yes', 'No internet service', 'Yes', 'No'],
        'churn': ['No', 'No', 'Yes', 'Yes', 'No']
    })

def test_data_ingestion():
    """Test data ingestion component."""
    # Create test data
    df = create_test_data()
    df.to_csv('data/test_data.csv', index=False)
    
    # Test CSV ingestion
    ingestion = CSVDataIngestion('data/test_data.csv')
    loaded_data = ingestion.load_data()
    
    assert isinstance(loaded_data, pd.DataFrame)
    assert len(loaded_data) == 5
    assert all(col in loaded_data.columns for col in [
        'customer_id', 'tenure', 'monthly_charges', 'total_charges',
        'contract_type', 'payment_method', 'paperless_billing',
        'internet_service', 'online_security', 'online_backup',
        'device_protection', 'tech_support', 'streaming_tv',
        'streaming_movies', 'churn'
    ])

def test_data_preprocessing():
    """Test data preprocessing component."""
    # Create test data
    df = create_test_data()
    
    # Test preprocessing
    preprocessor = StandardDataPreprocessor()
    processed_data = preprocessor.preprocess(df)
    
    assert isinstance(processed_data, pd.DataFrame)
    assert len(processed_data) == 5
    assert not processed_data.isnull().any().any()
    assert all(col not in processed_data.columns for col in ['customer_id'])  # ID should be dropped

def test_model_training():
    """Test model training component."""
    # Create test data
    df = create_test_data()
    
    # Preprocess data
    preprocessor = StandardDataPreprocessor()
    processed_data = preprocessor.preprocess(df)
    X, y = preprocessor.split_features_target(processed_data, 'churn')
    
    # Test model training
    model = SklearnModel(LogisticRegression())
    model.train(X, y)
    predictions = model.predict(X)
    
    assert len(predictions) == len(y)
    assert all(pred in [0, 1] for pred in predictions)

def test_model_trainer():
    """Test model trainer component."""
    # Create test data
    df = create_test_data()
    
    # Preprocess data
    preprocessor = StandardDataPreprocessor()
    processed_data = preprocessor.preprocess(df)
    X, y = preprocessor.split_features_target(processed_data, 'churn')
    
    # Test model trainer
    trainer = ModelTrainer()
    results = trainer.train_and_evaluate(X, y)
    
    assert isinstance(results, dict)
    assert all(metric in ['accuracy', 'precision', 'recall', 'f1'] 
              for metrics in results.values() 
              for metric in metrics.keys())

def convert_to_json_serializable(obj):
    """Convert numpy types and handle non-JSON compliant values."""
    if isinstance(obj, (np.float32, np.float64)):
        if np.isnan(obj) or np.isinf(obj):
            return 0.0  # Replace non-JSON compliant values with 0.0
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif pd.isna(obj):  # Handle pandas NA values
        return 0.0
    return obj

# @pytest.fixture(scope="function")
# def mlflow_server():
#     """Fixture to start and stop MLflow model server for testing."""
#     # Get the latest run ID for the CustomerChurnPipeline experiment
#     experiment = mlflow.get_experiment_by_name("CustomerChurnPipeline")
#     if experiment is None:
#         raise ValueError("No experiment found with name 'CustomerChurnPipeline'")
    
#     runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
#     if runs.empty:
#         raise ValueError("No runs found in the experiment")
    
#     latest_run = runs.iloc[0]
#     run_id = latest_run['run_id']
    
#     # Start MLflow model server
#     port = 5010
#     process = subprocess.Popen(
#         ["mlflow", "models", "serve", "-m", f"runs:/{run_id}/best_model", "-p", str(port)],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE
#     )
    
#     # Wait for server to start
#     time.sleep(5)
    
#     yield port
    
#     # Stop the server
#     process.terminate()
#     process.wait()

# def test_model_serving(mlflow_server):
#     """Test model serving component."""
#     port = mlflow_server
    
#     # Generate sample data
#     logger.info("Generating sample data for testing")
#     test_data = generate_customer_data(n_samples=5)
    
#     # Prepare the data for the API
#     # Remove the target variable if it exists
#     if 'churn' in test_data.columns:
#         test_data = test_data.drop('churn', axis=1)
    
#     # Fill any missing values with 0.0
#     test_data = test_data.fillna(0.0)
    
#     # Convert to the format expected by MLflow serving
#     data = {
#         "dataframe_split": {
#             "columns": test_data.columns.tolist(),
#             "data": test_data.values.tolist()
#         }
#     }
    
#     # Convert numpy types to Python native types and handle non-JSON compliant values
#     data = convert_to_json_serializable(data)
    
#     # Make prediction request
#     logger.info("Making prediction request to the served model")
#     url = f"http://127.0.0.1:{port}/invocations"
#     headers = {'Content-Type': 'application/json'}
    
#     try:
#         # Verify data is JSON serializable before sending
#         json.dumps(data)
        
#         response = requests.post(url, json=data, headers=headers)
#         response.raise_for_status()  # Raise an exception for bad status codes
        
#         # Process the response
#         predictions = response.json()
#         logger.info("Predictions received successfully")
#         logger.info(f"Raw predictions: {predictions}")
        
#         # If the response contains probabilities
#         if isinstance(predictions, list) and len(predictions) > 0:
#             if isinstance(predictions[0], list):  # If it's a list of probabilities
#                 predictions = [pred[1] for pred in predictions]  # Get probability of class 1
        
#         # Create a DataFrame with results
#         results_df = pd.DataFrame({
#             'customer_id': test_data['customer_id'].values,
#             'churn_probability': predictions
#         })
        
#         logger.info("\nPrediction Results:")
#         logger.info("\n" + str(results_df))
        
#         return results_df
        
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error making prediction request: {str(e)}")
#         raise
#     except json.JSONDecodeError as e:
#         logger.error(f"Error decoding JSON response: {str(e)}")
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}")
#         raise

if __name__ == "__main__":
    # test_model_serving() 
    pass