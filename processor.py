"""
Data Processing Core Module
Handles all data manipulation, cleaning, and analysis operations
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class SpreadsheetProcessor:
    """
    Core processor for spreadsheet data manipulation
    
    This class handles loading, cleaning, transforming, and analyzing
    data from Excel and CSV files.
    
    Attributes:
        raw_data (DataFrame): Original loaded data
        processed_data (DataFrame): Data after processing
        metrics (dict): Calculated data metrics
        history (list): Action history log
        validations (dict): Applied validations
    """
    
    def __init__(self):
        """Initialize the processor with empty data containers"""
        self.raw_data = None
        self.processed_data = None
        self.metrics = {}
        self.history = []
        self.validations = {}
        
    def load_data(self, file_path):
        """
        Load data from Excel or CSV file
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if successful
            
        Raises:
            Exception: If file cannot be loaded
        """
        try:
            if file_path.endswith('.csv'):
                self.raw_data = pd.read_csv(file_path)
            else:
                self.raw_data = pd.read_excel(file_path, sheet_name=0)
            
            self.processed_data = self.raw_data.copy()
            self._register_action("Data loaded", f"{len(self.raw_data)} records")
            return True
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def _register_action(self, action, details):
        """
        Register an action in the history log
        
        Args:
            action (str): Action name
            details (str): Action details
        """
        self.history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': action,
            'details': details
        })
    
    def clean_data(self):
        """
        Clean and standardize the data
        
        Operations performed:
            - Remove completely empty rows
            - Standardize column names (uppercase, no spaces, remove accents)
            - Remove extra whitespace from text data
            - Replace string null values with None
        
        Returns:
            bool: True if successful
            
        Raises:
            Exception: If no data loaded
        """
        if self.raw_data is None:
            raise Exception("No data loaded for cleaning")
            
        df = self.processed_data.copy()
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Standardize column names
        df.columns = df.columns.str.strip().str.upper()
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.replace('ç', 'c')
        df.columns = df.columns.str.replace('ã', 'a')
        df.columns = df.columns.str.replace('á', 'a')
        df.columns = df.columns.str.replace('é', 'e')
        df.columns = df.columns.str.replace('í', 'i')
        df.columns = df.columns.str.replace('ó', 'o')
        df.columns = df.columns.str.replace('ú', 'u')
        
        # Remove extra spaces in text data
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['nan', 'None', '', 'NaN'], None)
        
        self.processed_data = df
        self._register_action("Data cleaned", "Standardization applied")
        return True
    
    def handle_null_values(self, strategy='mean'):
        """
        Handle null values in the data
        
        Args:
            strategy (str): Strategy for handling nulls
                Options: 'mean', 'median', 'mode', 'zero', 'forward', 'backward'
        
        Returns:
            bool: True if successful
            
        Raises:
            Exception: If no data loaded
        """
        if self.processed_data is None:
            raise Exception("No data loaded for handling")
            
        df = self.processed_data.copy()
        nulls_before = df.isnull().sum().sum()
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                if strategy == 'mean':
                    df[col] = df[col].fillna(df[col].mean())
                elif strategy == 'median':
                    df[col] = df[col].fillna(df[col].median())
                elif strategy == 'mode':
                    df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 0)
                elif strategy == 'zero':
                    df[col] = df[col].fillna(0)
                elif strategy == 'forward':
                    df[col] = df[col].fillna(method='ffill')
                elif strategy == 'backward':
                    df[col] = df[col].fillna(method='bfill')
            else:
                if strategy == 'mode':
                    df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'UNKNOWN')
                else:
                    df[col] = df[col].fillna('UNKNOWN')
        
        nulls_after = df.isnull().sum().sum()
        self.processed_data = df
        self._register_action("Null values handled", 
                           f"Strategy: {strategy}, Nulls handled: {nulls_before - nulls_after}")
        return True
    
    def remove_duplicates(self):
        """
        Remove duplicate rows from the data
        
       
