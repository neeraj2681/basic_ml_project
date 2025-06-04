from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional
import os
from pathlib import Path
from src.utils.logger import Logger

class DataIngestion(ABC):
    """Abstract base class for data ingestion."""
    
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
    
    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        """Load data from source."""
        pass
    
    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate the loaded data."""
        pass

class CSVDataIngestion(DataIngestion):
    """Concrete implementation for CSV data ingestion."""
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.logger.info(f"Initializing CSV data ingestion for file: {file_path}")
        
    def load_data(self) -> pd.DataFrame:
        """Load data from CSV file."""
        try:
            self.logger.info(f"Attempting to load data from {self.file_path}")
            data = pd.read_csv(self.file_path)
            
            if self.validate_data(data):
                self.logger.info(f"Successfully loaded data with {len(data)} rows and {len(data.columns)} columns")
                return data
            
            self.logger.error("Data validation failed")
            raise ValueError("Data validation failed")
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise Exception(f"Error loading data: {str(e)}")
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate the loaded data."""
        self.logger.debug("Starting data validation")
        
        if data.empty:
            self.logger.warning("Data is empty")
            return False
            
        missing_values = data.isnull().sum().sum()
        missing_percentage = (missing_values / (len(data) * len(data.columns))) * 100
        
        if missing_percentage > 50:
            self.logger.warning(f"Too many missing values: {missing_percentage:.2f}%")
            return False
            
        self.logger.info(f"Data validation passed. Missing values: {missing_percentage:.2f}%")
        return True

class DataIngestionFactory:
    """Factory class for creating data ingestion instances."""
    
    @staticmethod
    def create_data_ingestion(file_path: str) -> DataIngestion:
        """
        Create appropriate data ingestion instance based on file extension.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            DataIngestion: Instance of appropriate data ingestion class
        """
        logger = Logger("DataIngestionFactory")
        logger.info(f"Creating data ingestion instance for file: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.csv':
            logger.info("Creating CSV data ingestion instance")
            return CSVDataIngestion(file_path)
        else:
            error_msg = f"Unsupported file extension: {file_extension}"
            logger.error(error_msg)
            raise ValueError(error_msg) 