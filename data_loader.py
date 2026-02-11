"""
Data Loader Module
Handles loading and initial validation of datasets
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads and validates tabular data from various sources
    """
    
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        
    def load_file(self, file_path: str) -> pd.DataFrame:
        """
        Load data from CSV or Excel file
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Loaded DataFrame
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Loading file: {file_path}")
        
        # Load based on file extension
        if file_path.suffix.lower() == '.csv':
            self.data = pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            self.data = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Generate metadata
        self._generate_metadata()
        
        logger.info(f"Data loaded successfully: {self.data.shape[0]} rows, {self.data.shape[1]} columns")
        
        return self.data
    
    def _generate_metadata(self):
        """Generate metadata about the loaded dataset"""
        if self.data is None:
            return
        
        self.metadata = {
            "rows": len(self.data),
            "columns": len(self.data.columns),
            "column_names": self.data.columns.tolist(),
            "dtypes": self.data.dtypes.astype(str).to_dict(),
            "missing_values": self.data.isnull().sum().to_dict(),
            "memory_usage": f"{self.data.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
        }
        
        # Identify column types
        self.metadata["numeric_columns"] = self.data.select_dtypes(
            include=[np.number]
        ).columns.tolist()
        
        self.metadata["categorical_columns"] = self.data.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()
        
        self.metadata["datetime_columns"] = self.data.select_dtypes(
            include=['datetime64']
        ).columns.tolist()
    
    def get_sample(self, n: int = 5) -> pd.DataFrame:
        """
        Get a sample of the data
        
        Args:
            n: Number of rows to return
            
        Returns:
            Sample DataFrame
        """
        if self.data is None:
            raise ValueError("No data loaded")
        
        return self.data.head(n)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get dataset metadata
        
        Returns:
            Metadata dictionary
        """
        return self.metadata
    
    def validate_data(self) -> Tuple[bool, list]:
        """
        Validate the loaded data
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if self.data is None:
            return False, ["No data loaded"]
        
        # Check for empty dataset
        if len(self.data) == 0:
            issues.append("Dataset is empty")
        
        # Check for columns with all missing values
        all_missing = self.data.columns[self.data.isnull().all()].tolist()
        if all_missing:
            issues.append(f"Columns with all missing values: {all_missing}")
        
        # Check for duplicate rows
        duplicates = self.data.duplicated().sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate rows")
        
        # Check for columns with single unique value
        single_value_cols = [
            col for col in self.data.columns 
            if self.data[col].nunique() == 1
        ]
        if single_value_cols:
            issues.append(f"Columns with single value: {single_value_cols}")
        
        is_valid = len(issues) == 0
        
        return is_valid, issues
