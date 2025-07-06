from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
from typing import List, Dict, Any, Optional
import os
import sys
import logging

# Add src directory to Python path for model loading
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Customer Churn Prediction API",
    description="API for predicting customer churn using ML model",
    version="1.0.0"
)

# Global variables for model and preprocessor
model: Optional[Any] = None
preprocessor: Optional[Any] = None
model_loaded = False

class CustomerData(BaseModel):
    """Input schema for customer data"""
    tenure: float
    monthly_charges: float
    total_charges: float
    contract_type: str
    payment_method: str
    paperless_billing: str
    internet_service: str
    online_security: str
    online_backup: str
    device_protection: str
    tech_support: str
    streaming_tv: str
    streaming_movies: str

class PredictionResponse(BaseModel):
    """Response schema for predictions"""
    churn_probability: float
    churn_prediction: str
    confidence: str

def load_model_and_preprocessor():
    """Load model and create preprocessor"""
    global model, preprocessor, model_loaded
    
    try:
        logger.info("Attempting to load model and create preprocessor...")
        
        # Load the model
        if os.path.exists("models/best_model.joblib"):
            logger.info("Loading model from local file...")
            model = joblib.load("models/best_model.joblib")
            logger.info(f"Model loaded successfully: {type(model).__name__}")
        else:
            logger.error("Model file not found")
            model_loaded = False
            return
        
        # Create the preprocessor using the function instead of loading from file
        try:
            from src.features.prediction_preprocessor import create_simple_preprocessor
            logger.info("Creating preprocessor using create_simple_preprocessor...")
            preprocessor = create_simple_preprocessor()
            logger.info(f"Preprocessor created successfully: {type(preprocessor).__name__}")
        except Exception as e:
            logger.error(f"Failed to create preprocessor: {e}")
            model_loaded = False
            return
        
        model_loaded = True
        logger.info("Model and preprocessor setup completed successfully")
        
        # Test the loaded model and preprocessor
        logger.info("Testing loaded model and preprocessor...")
        test_data = pd.DataFrame([{
            'tenure': 12, 'monthly_charges': 50, 'total_charges': 600,
            'contract_type': 'Month-to-month', 'payment_method': 'Electronic check',
            'paperless_billing': 'Yes', 'internet_service': 'DSL',
            'online_security': 'No', 'online_backup': 'No', 'device_protection': 'No',
            'tech_support': 'No', 'streaming_tv': 'No', 'streaming_movies': 'No'
        }])
        
        # Use the transform method for prediction preprocessing
        processed_data = preprocessor.preprocess(test_data)
        test_pred = model.predict_proba(processed_data)[0]
        logger.info(f"Test prediction successful: {test_pred[1]:.3f}")
        
    except Exception as e:
        logger.error(f"Failed to load model and preprocessor: {e}")
        model_loaded = False

@app.on_event("startup")
async def startup_event():
    """Load model and preprocessor on startup"""
    logger.info("Starting up API...")
    load_model_and_preprocessor()
    if model_loaded:
        logger.info("API startup completed successfully with model loaded")
    else:
        logger.warning("API started but model loading failed - predictions will not work")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Customer Churn Prediction API", 
        "status": "running",
        "model_loaded": model_loaded
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "preprocessor_loaded": preprocessor is not None
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_churn(customer_data: CustomerData):
    """Predict customer churn"""
    if not model_loaded or model is None or preprocessor is None:
        raise HTTPException(
            status_code=503, 
            detail="Model or preprocessor not loaded. Check /health endpoint for status."
        )
    
    try:
        # Convert input to DataFrame
        input_data = pd.DataFrame([customer_data.dict()])
        
        logger.info(f"Input data: {input_data.to_dict('records')[0]}")
        
        # Preprocess the data
        processed_data = preprocessor.preprocess(input_data)
        
        logger.info(f"Processed data shape: {processed_data.shape}")
        logger.info(f"Processed data sample: {processed_data.iloc[0].to_dict()}")
        
        # Make prediction
        prediction_proba = model.predict_proba(processed_data)[0]
        churn_probability = float(prediction_proba[1])  # Probability of churn (class 1)
        
        logger.info(f"Raw prediction probabilities: {prediction_proba}")
        logger.info(f"Churn probability: {churn_probability}")
        
        # Determine prediction and confidence
        churn_prediction = "Yes" if churn_probability > 0.5 else "No"
        
        if churn_probability > 0.7 or churn_probability < 0.3:
            confidence = "High"
        elif churn_probability > 0.6 or churn_probability < 0.4:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return PredictionResponse(
            churn_probability=churn_probability,
            churn_prediction=churn_prediction,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict_batch")
async def predict_batch(customers: List[CustomerData]):
    """Predict churn for multiple customers"""
    if not model_loaded or model is None or preprocessor is None:
        raise HTTPException(
            status_code=503, 
            detail="Model or preprocessor not loaded. Check /health endpoint for status."
        )
    
    try:
        # Convert input to DataFrame
        input_data = pd.DataFrame([customer.dict() for customer in customers])
        
        # Preprocess the data
        processed_data = preprocessor.preprocess(input_data)
        
        # Make predictions
        predictions_proba = model.predict_proba(processed_data)
        
        results = []
        for i, proba in enumerate(predictions_proba):
            churn_probability = float(proba[1])
            churn_prediction = "Yes" if churn_probability > 0.5 else "No"
            
            if churn_probability > 0.7 or churn_probability < 0.3:
                confidence = "High"
            elif churn_probability > 0.6 or churn_probability < 0.4:
                confidence = "Medium"
            else:
                confidence = "Low"
            
            results.append({
                "customer_index": i,
                "churn_probability": churn_probability,
                "churn_prediction": churn_prediction,
                "confidence": confidence
            })
        
        return {"predictions": results}
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@app.get("/model_info")
async def get_model_info():
    """Get information about the loaded model"""
    return {
        "model_loaded": model_loaded,
        "model_type": type(model).__name__ if model else None,
        "preprocessor_loaded": preprocessor is not None,
        "preprocessor_type": type(preprocessor).__name__ if preprocessor else None,
        "api_version": "1.0.0"
    }

@app.post("/reload_model")
async def reload_model():
    """Reload the model and preprocessor"""
    logger.info("Manual model reload requested")
    load_model_and_preprocessor()
    return {
        "status": "success" if model_loaded else "failed",
        "model_loaded": model_loaded,
        "message": "Model reloaded successfully" if model_loaded else "Model reload failed"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Customer Churn Prediction API...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 