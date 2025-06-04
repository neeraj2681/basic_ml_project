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
        # mlflow.log_param("n_samples", n_samples)
        
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
                # mlflow.log_metric(f"{model_name}_{metric_name}", value)
        
        # Save and log best model
        best_model_path = 'models/best_model.joblib'
        model_trainer.save_best_model(best_model_path)
        
        # Log the model with the preprocessor and signature
        mlflow.sklearn.log_model(
            model_trainer.best_model.model,
            "best_model",
            signature=mlflow.models.infer_signature(X, y),
            input_example=X.head(),
            registered_model_name="CustomerChurnModel"
        )
        # mlflow.log_artifact(best_model_path)
        logger.info("Best model saved to 'models/best_model.joblib'")
        
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
            # mlflow.log_artifact(feature_path)
        
        logger.info("ML pipeline completed successfully")
        # mlflow.log_artifact('data/customer_churn_data.csv')
        # mlflow.log_artifact('logs')

if __name__ == "__main__":
    main() 