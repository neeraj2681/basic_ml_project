import os
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from data.data_ingestion import DataIngestionFactory
from features.data_preprocessing import StandardDataPreprocessor
from models.model_trainer import ModelTrainer
from data.sample_data_generator import generate_customer_data
from utils.logger import Logger
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder

def create_fixed_preprocessor(preprocessor, X_columns):
    """Create a fixed preprocessor that doesn't have module dependency issues"""
    from features.prediction_preprocessor import PredictionPreprocessor
    
    # Create a new preprocessor that won't have import issues
    fixed_preprocessor = PredictionPreprocessor()
    
    # Copy the fitted transformers (avoid deep copy issues)
    fixed_preprocessor.scaler = preprocessor.scaler  # Just use the same scaler object
    fixed_preprocessor.label_encoders = preprocessor.label_encoders.copy()
    fixed_preprocessor.categorical_columns = list(preprocessor.label_encoders.keys())
    fixed_preprocessor.numerical_columns = ['tenure', 'monthly_charges', 'total_charges']
    
    # Ensure feature columns match the scaler's expected input
    # The scaler was fitted on all columns, so we need to preserve this order
    fixed_preprocessor.feature_columns = list(X_columns)
    fixed_preprocessor.fitted = True
    
    return fixed_preprocessor

def main():
    mlflow.sklearn.autolog()
    # MLflow experiment setup
    mlflow.set_experiment("CustomerChurnPipeline")
    with mlflow.start_run() as run:
        
        logger = Logger("Main")
        logger.info("Starting ML pipeline (MLflow run: %s)" % run.info.run_id)
        
        # Create necessary directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Generate and save sample dataset
        logger.info("Generating customer churn dataset")
        n_samples = 1000
        df = generate_customer_data(n_samples=n_samples)
        df.to_csv('data/customer_churn_data.csv', index=False)
        logger.info("Dataset saved to 'data/customer_churn_data.csv'")
        
        # Initialize components
        logger.info("Initializing pipeline components")
        data_ingestion = DataIngestionFactory.create_data_ingestion('data/customer_churn_data.csv')
        preprocessor = StandardDataPreprocessor()
        model_trainer = ModelTrainer()
        
        # Load and preprocess data
        logger.info("Loading and preprocessing data")
        data = data_ingestion.load_data()
        processed_data = preprocessor.preprocess(data)
        X, y = preprocessor.split_features_target(processed_data, 'churn')
        
        # Train and evaluate models
        logger.info("Starting model training and evaluation")
        results = model_trainer.train_and_evaluate(X, y, mlflow_tracking=True)
        
        # Log results to MLflow
        logger.info("Model Evaluation Results:")
        for model_name, metrics in results.items():
            logger.info(f"\n{model_name.upper()}:")
            for metric_name, value in metrics.items():
                logger.info(f"{metric_name}: {value:.4f}")
        
        # Save the model WITHOUT complex wrappers to avoid dependency issues
        logger.info("Saving best model without complex wrappers")
        best_model_path = 'models/best_model.joblib'
        
        # Save just the sklearn model directly - no wrappers
        joblib.dump(model_trainer.best_model.model, best_model_path)
        logger.info("Best model saved to 'models/best_model.joblib'")
        
        # Create and save a fixed preprocessor that won't have import issues
        logger.info("Creating dependency-free preprocessor")
        fixed_preprocessor = create_fixed_preprocessor(preprocessor, X.columns)
        
        preprocessor_path = 'models/preprocessor.joblib'
        joblib.dump(fixed_preprocessor, preprocessor_path)
        logger.info("Fixed preprocessor saved to 'models/preprocessor.joblib'")
        
        # Test the saved model to ensure it works
        logger.info("Testing saved model and preprocessor...")
        try:
            test_model = joblib.load(best_model_path)
            test_preprocessor = joblib.load(preprocessor_path)
            
            # Create test cases
            test_data_high_risk = pd.DataFrame([{
                'tenure': 1, 'monthly_charges': 80, 'total_charges': 80,
                'contract_type': 'Month-to-month', 'payment_method': 'Electronic check',
                'paperless_billing': 'Yes', 'internet_service': 'Fiber optic',
                'online_security': 'No', 'online_backup': 'No', 'device_protection': 'No',
                'tech_support': 'No', 'streaming_tv': 'No', 'streaming_movies': 'No'
            }])
            
            test_data_low_risk = pd.DataFrame([{
                'tenure': 60, 'monthly_charges': 35, 'total_charges': 2100,
                'contract_type': 'Two year', 'payment_method': 'Credit card (automatic)',
                'paperless_billing': 'No', 'internet_service': 'DSL',
                'online_security': 'Yes', 'online_backup': 'Yes', 'device_protection': 'Yes',
                'tech_support': 'Yes', 'streaming_tv': 'Yes', 'streaming_movies': 'Yes'
            }])
            
            # Test predictions
            processed_high_risk = test_preprocessor.preprocess(test_data_high_risk)
            processed_low_risk = test_preprocessor.preprocess(test_data_low_risk)
            
            pred_high_risk = test_model.predict_proba(processed_high_risk)[0]
            pred_low_risk = test_model.predict_proba(processed_low_risk)[0]
            
            logger.info(f"High-risk test case - Churn probability: {pred_high_risk[1]:.3f}")
            logger.info(f"Low-risk test case - Churn probability: {pred_low_risk[1]:.3f}")
            
            # Verify they're different
            if abs(pred_high_risk[1] - pred_low_risk[1]) > 0.01:
                logger.info("✅ Model test PASSED - Different predictions for different inputs")
            else:
                logger.warning("⚠️ Model test FAILED - Same predictions for different inputs")
                
        except Exception as e:
            logger.error(f"Model testing failed: {e}")
        
        # Log to MLflow (simplified)
        try:
            # Log the preprocessor to MLflow
            mlflow.log_artifact(preprocessor_path, "preprocessor")
            
            # Log the model with signature and conda environment
            mlflow.sklearn.log_model(
                test_model,
                "best_model",
                signature=mlflow.models.infer_signature(data.drop('churn', axis=1), y),
                input_example=data.drop('churn', axis=1).head(),
                registered_model_name="CustomerChurnModel"
            )
            
        except Exception as e:
            logger.warning(f"MLflow logging failed (non-critical): {e}")
        
        # Log feature importance for the best model
        if hasattr(model_trainer.best_model.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': model_trainer.best_model.model.feature_importances_
            })
            feature_importance = feature_importance.sort_values('importance', ascending=False)
            logger.info("\nTop 5 Most Important Features:")
            logger.info(str(feature_importance.head()))
            # Save and log feature importance
            feature_path = "models/feature_importance.csv"
            feature_importance.to_csv(feature_path, index=False)
        
        logger.info("ML pipeline completed successfully")

if __name__ == "__main__":
    main() 