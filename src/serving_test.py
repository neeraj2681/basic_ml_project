import logging
from data.sample_data_generator import generate_customer_data

import mlflow 
logged_model = 'runs:/d481226f35714e9c9c5d420f175b4493/best_model'

# Load model as a PyFuncModel.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


loaded_model = mlflow.pyfunc.load_model(logged_model)
logger.info("Generating sample data for testing")
test_data = generate_customer_data(n_samples=100)
    
# Remove target variable if it exists
if 'churn' in test_data.columns:
    test_data = test_data.drop('churn', axis=1)
# Predict on a Pandas DataFrame.
import pandas as pd
predictions = loaded_model.predict_proba(pd.DataFrame(test_data)) 
logger.info("Predictions: %s", predictions)