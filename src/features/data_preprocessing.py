from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Tuple, List, Optional
from src.utils.logger import Logger

class DataPreprocessor(ABC):
    """Abstract base class for data preprocessing."""
    
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
    
    @abstractmethod
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the data."""
        pass
    
    @abstractmethod
    def split_features_target(self, data: pd.DataFrame, target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Split features and target variables."""
        pass

class StandardDataPreprocessor(DataPreprocessor):
    """Standard implementation of data preprocessing."""
    
    def __init__(self):
        super().__init__()
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.fitted = False
        self.feature_columns = None
        self.categorical_columns = []
        self.numerical_columns = []
        self.logger.info("Initializing StandardDataPreprocessor")
        
    def preprocess(self, data: pd.DataFrame, target_column: str = 'churn') -> pd.DataFrame:
        """Preprocess the data."""
        self.logger.info("Starting data preprocessing")
        try:
            df = data.copy()

            # Drop customer_id if present
            if 'customer_id' in df.columns:
                self.logger.info("Dropping customer_id column")
                df = df.drop(columns=['customer_id'])

            # Handle missing values
            self.logger.info("Handling missing values")
            df = self._handle_missing_values(df)

            # Store column information before encoding
            if not self.fitted:
                self.categorical_columns = [col for col in df.select_dtypes(include=['object']).columns if col != target_column]
                self.numerical_columns = [col for col in df.select_dtypes(include=[np.number]).columns if col != target_column]

            # Encode categorical variables (excluding target)
            self.logger.info("Encoding categorical variables")
            df = self._encode_categorical_variables(df, exclude_columns=[target_column])

            # Encode target column if it's object type
            if target_column in df.columns and df[target_column].dtype == 'object':
                self.logger.info(f"Encoding target column: {target_column}")
                if target_column not in self.label_encoders:
                    self.label_encoders[target_column] = LabelEncoder()
                    df[target_column] = self.label_encoders[target_column].fit_transform(df[target_column])
                else:
                    # For prediction, use transform only
                    df[target_column] = self.label_encoders[target_column].transform(df[target_column])

            # Scale numerical variables (excluding target)
            self.logger.info("Scaling numerical variables")
            df = self._scale_numerical_variables(df, exclude_columns=[target_column])

            # Store feature column order after first fit
            if not self.fitted:
                self.feature_columns = [col for col in df.columns if col != target_column]
                self.fitted = True

            self.logger.info("Preprocessing completed successfully")
            return df

        except Exception as e:
            self.logger.error(f"Preprocessing failed: {str(e)}")
            raise
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using fitted preprocessors (for prediction)."""
        if not self.fitted:
            raise ValueError("Preprocessor must be fitted before transforming new data")
        
        self.logger.info("Transforming new data for prediction")
        try:
            df = data.copy()

            # Drop customer_id if present
            if 'customer_id' in df.columns:
                df = df.drop(columns=['customer_id'])

            # Handle missing values
            df = self._handle_missing_values(df)

            # Transform categorical variables using fitted encoders
            for col in self.categorical_columns:
                if col in df.columns and col in self.label_encoders:
                    encoder = self.label_encoders[col]
                    # Handle unseen categories
                    unseen_mask = ~df[col].isin(encoder.classes_)
                    if unseen_mask.any():
                        self.logger.warning(f"Found unseen categories in {col}, replacing with first class")
                        df.loc[unseen_mask, col] = encoder.classes_[0]
                    df[col] = encoder.transform(df[col])

            # Add missing columns with default values
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0

            # Reorder columns to match training data
            df = df[self.feature_columns]

            # Scale numerical variables using fitted scaler
            if len(self.numerical_columns) > 0:
                cols_to_scale = [col for col in self.numerical_columns if col in df.columns]
                if cols_to_scale:
                    df[cols_to_scale] = self.scaler.transform(df[cols_to_scale])

            self.logger.info("Data transformation completed successfully")
            return df

        except Exception as e:
            self.logger.error(f"Data transformation failed: {str(e)}")
            raise
    
    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset."""
        self.logger.debug("Handling missing values")
        
        # For numerical columns, fill with median
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            missing_count = data[col].isnull().sum()
            if missing_count > 0:
                self.logger.info(f"Filling {missing_count} missing values in {col} with median")
                median_value = data[col].median()
                if pd.isna(median_value):  # If median is also NaN
                    median_value = 0.0  # Use 0 as fallback
                data[col] = data[col].fillna(median_value)
        
        # For categorical columns, fill with mode
        categorical_cols = data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            missing_count = data[col].isnull().sum()
            if missing_count > 0:
                self.logger.info(f"Filling {missing_count} missing values in {col} with mode")
                mode_values = data[col].mode()
                if len(mode_values) > 0:
                    data[col] = data[col].fillna(mode_values[0])
                else:
                    # If no mode exists, use the most frequent value or a default
                    most_frequent = data[col].value_counts().index[0] if len(data[col].value_counts()) > 0 else 'Unknown'
                    data[col] = data[col].fillna(most_frequent)
        
        return data
    
    def _encode_categorical_variables(self, data: pd.DataFrame, exclude_columns: list = None) -> pd.DataFrame:
        """Encode categorical variables using label encoding, excluding specified columns."""
        self.logger.debug("Encoding categorical variables")
        exclude_columns = exclude_columns or []
        categorical_cols = [col for col in data.select_dtypes(include=['object']).columns if col not in exclude_columns]
        
        for col in categorical_cols:
            self.logger.info(f"Encoding categorical column: {col}")
            if col not in self.label_encoders:
                # First time - fit the encoder
                self.label_encoders[col] = LabelEncoder()
                data[col] = self.label_encoders[col].fit_transform(data[col])
            else:
                # Subsequent times - use transform only
                # Handle unseen categories
                unseen_mask = ~data[col].isin(self.label_encoders[col].classes_)
                if unseen_mask.any():
                    self.logger.warning(f"Found unseen categories in {col}, replacing with first class")
                    data.loc[unseen_mask, col] = self.label_encoders[col].classes_[0]
                data[col] = self.label_encoders[col].transform(data[col])
        
        return data
    
    def _scale_numerical_variables(self, data: pd.DataFrame, exclude_columns: list = None) -> pd.DataFrame:
        """Scale numerical variables using StandardScaler, excluding specified columns."""
        self.logger.debug("Scaling numerical variables")
        exclude_columns = exclude_columns or []
        numerical_cols = [col for col in data.select_dtypes(include=[np.number]).columns if col not in exclude_columns]
        
        if len(numerical_cols) > 0:
            self.logger.info(f"Scaling {len(numerical_cols)} numerical columns")
            if not self.fitted:
                # First time - fit the scaler
                data[numerical_cols] = self.scaler.fit_transform(data[numerical_cols])
            else:
                # Subsequent times - use transform only
                data[numerical_cols] = self.scaler.transform(data[numerical_cols])
        
        return data
    
    def split_features_target(self, data: pd.DataFrame, target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Split features and target variables."""
        self.logger.info(f"Splitting features and target variable: {target_column}")
        
        if target_column not in data.columns:
            error_msg = f"Target column '{target_column}' not found in data"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        self.logger.info(f"Split complete: {len(X)} features, {len(y)} target values")
        return X, y 