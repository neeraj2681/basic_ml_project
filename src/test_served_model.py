import requests
import json
import pandas as pd
import numpy as np
from data.sample_data_generator import generate_customer_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_to_json_serializable(obj):
    if isinstance(obj, np.float32) or isinstance(obj, np.float64):
        if np.isnan(obj) or np.isinf(obj):
            return 0.0  # Replace non-JSON compliant values with 0.0
        return float(obj)
    elif isinstance(obj, np.int32) or isinstance(obj, np.int64):
        return int(obj)
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    return obj

def test_model_serving():
    # Generate sample data
    logger.info("Generating sample data for testing")
    test_data = generate_customer_data(n_samples=100)
    
    # Remove target variable if it exists
    if 'churn' in test_data.columns:
        test_data = test_data.drop('churn', axis=1)
    
    # Convert to the format expected by MLflow serving
    data = {
        "dataframe_split": {
            "columns": test_data.columns.tolist(),
            "data": test_data.values.tolist()
        }
    }
    
    # Convert numpy types to Python native types and handle non-JSON compliant values
    data = convert_to_json_serializable(data)
    
    # Ensure data is JSON serializable
    try:
        json.dumps(data)
    except ValueError as e:
        logger.error(f"Data is not JSON serializable: {str(e)}")
        raise
    
    # After converting the data to JSON serializable
    logger.info("Data to be sent: %s", data)
    logger.info("Data type: %s", type(data))
    logger.info("Data frame: %s", data['dataframe_split'])
    
    # Make prediction request
    logger.info("Making prediction request to the served model")
    url = "http://127.0.0.1:5010/invocations"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        # Make prediction request with predict_proba parameter
        response = requests.post(
            url, 
            json=data, 
            headers=headers,
            params={'predict_proba': 'true'}  # Request probability predictions
        )
        response.raise_for_status()
        
        # Process the response
        predictions = response.json()
        logger.info("Predictions received successfully")
        logger.info(f"Raw predictions: {predictions}")
        
        # Extract probabilities from the response
        if isinstance(predictions, dict) and 'predictions' in predictions:
            predictions = predictions['predictions']
            # If predictions are in format [[p0, p1], [p0, p1], ...], extract p1 (probability of class 1)
            if isinstance(predictions[0], list):
                predictions = [pred[1] for pred in predictions]  # Get probability of class 1
        
        # Create a DataFrame with results
        results_df = pd.DataFrame({
            'customer_id': test_data['customer_id'].values,
            'churn_probability': predictions
        })
        
        logger.info("\nPrediction Results:")
        logger.info("\n" + str(results_df))
        
        return results_df
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making prediction request: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

def check_results(results):
    # Check if the results are correct
    logger.info("Checking the results")
    logger.info("Unique probability values: %s", set(results['churn_probability'].values.tolist()))
    logger.info("Probability range: [%f, %f]", 
                results['churn_probability'].min(), 
                results['churn_probability'].max())

if __name__ == "__main__":
    results = test_model_serving()
    check_results(results)