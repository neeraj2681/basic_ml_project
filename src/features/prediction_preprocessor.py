import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, Any
import joblib
import logging

class PredictionPreprocessor:
    """Preprocessor specifically designed for making predictions on new data."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.fitted = False
        self.feature_columns = None
        self.categorical_columns = []
        self.numerical_columns = []
        
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data for prediction using fitted scalers and encoders.
        This should NOT refit the transformers.
        """
        try:
            df = data.copy()
            
            # Drop customer_id if present
            if 'customer_id' in df.columns:
                df = df.drop(columns=['customer_id'])
            
            # Handle missing values
            df = self._handle_missing_values(df)
            
            # Encode categorical variables using fitted encoders
            df = self._transform_categorical_variables(df)
            
            # Ensure all required columns exist and are in the right order
            if self.feature_columns is not None:
                # Add missing columns with default values
                for col in self.feature_columns:
                    if col not in df.columns:
                        df[col] = 0
                
                # Reorder columns to match training data
                df = df[self.feature_columns]
            
            # Scale all features (the scaler expects all 13 features)
            if self.fitted and hasattr(self.scaler, 'mean_'):
                try:
                    df_scaled = pd.DataFrame(
                        self.scaler.transform(df), 
                        columns=df.columns,
                        index=df.index
                    )
                    return df_scaled
                except Exception as e:
                    logging.warning(f"Scaling failed: {e}, returning unscaled data")
                    return df
            
            return df
            
        except Exception as e:
            logging.error(f"Preprocessing failed: {str(e)}")
            raise
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Alias for preprocess for compatibility"""
        return self.preprocess(data)
    
    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values using simple strategies."""
        df = data.copy()
        
        # For numerical columns, fill with 0
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna(0)
        
        # For categorical columns, fill with the first class from encoders
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isnull().any():
                if col in self.label_encoders:
                    classes = self.label_encoders[col].classes_
                    df[col] = df[col].fillna(classes[0] if len(classes) > 0 else 'Unknown')
                else:
                    df[col] = df[col].fillna('Unknown')
        
        return df
    
    def _transform_categorical_variables(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform categorical variables using fitted label encoders."""
        df = data.copy()
        
        for col in self.categorical_columns:
            if col in df.columns and col in self.label_encoders:
                encoder = self.label_encoders[col]
                # Handle unseen categories
                unseen_mask = ~df[col].isin(encoder.classes_)
                if unseen_mask.any():
                    logging.warning(f"Found unseen categories in {col}, replacing with first class")
                    df.loc[unseen_mask, col] = encoder.classes_[0]
                
                # Transform using fitted encoder
                df[col] = encoder.transform(df[col])
        
        return df

# Create a simple preprocessor for immediate use
def create_simple_preprocessor():
    """Create a simple preprocessor with predefined mappings."""
    preprocessor = PredictionPreprocessor()
    
    # Define expected categorical mappings based on your model
    categorical_mappings = {
        'contract_type': ['Month-to-month', 'One year', 'Two year'],
        'payment_method': ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'],
        'paperless_billing': ['No', 'Yes'],  # Note: 'No' first to match typical encoding
        'internet_service': ['DSL', 'Fiber optic', 'No'],
        'online_security': ['No', 'No internet service', 'Yes'],
        'online_backup': ['No', 'No internet service', 'Yes'],
        'device_protection': ['No', 'No internet service', 'Yes'],
        'tech_support': ['No', 'No internet service', 'Yes'],
        'streaming_tv': ['No', 'No internet service', 'Yes'],
        'streaming_movies': ['No', 'No internet service', 'Yes']
    }
    
    # Create label encoders
    for col, values in categorical_mappings.items():
        encoder = LabelEncoder()
        encoder.fit(values)
        preprocessor.label_encoders[col] = encoder
    
    preprocessor.categorical_columns = list(categorical_mappings.keys())
    preprocessor.numerical_columns = ['tenure', 'monthly_charges', 'total_charges']
    
    # Set feature order (numerical first, then categorical)
    preprocessor.feature_columns = (
        preprocessor.numerical_columns + 
        preprocessor.categorical_columns
    )
    
    # Create and fit a scaler with reasonable sample data
    sample_data = {
        'tenure': [1, 12, 24, 36, 48, 60, 72],
        'monthly_charges': [20, 40, 60, 80, 100, 120, 140],
        'total_charges': [20, 500, 1500, 3000, 5000, 7500, 10000],
        'contract_type': [0, 1, 2, 0, 1, 2, 0],
        'payment_method': [0, 1, 2, 3, 0, 1, 2],
        'paperless_billing': [0, 1, 0, 1, 0, 1, 0],
        'internet_service': [0, 1, 2, 0, 1, 2, 0],
        'online_security': [0, 1, 2, 0, 1, 2, 0],
        'online_backup': [0, 1, 2, 0, 1, 2, 0],
        'device_protection': [0, 1, 2, 0, 1, 2, 0],
        'tech_support': [0, 1, 2, 0, 1, 2, 0],
        'streaming_tv': [0, 1, 2, 0, 1, 2, 0],
        'streaming_movies': [0, 1, 2, 0, 1, 2, 0]
    }
    
    sample_df = pd.DataFrame(sample_data)
    sample_df = sample_df[preprocessor.feature_columns]
    
    preprocessor.scaler = StandardScaler()
    preprocessor.scaler.fit(sample_df)
    
    preprocessor.fitted = True
    return preprocessor 