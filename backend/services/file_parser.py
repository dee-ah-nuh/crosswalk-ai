"""
File parsing service for CSV/XLSX files.
"""

import pandas as pd
import json
from typing import List, Dict, Any, Tuple
from io import BytesIO
import re

class FileParser:
    """Service for parsing uploaded files and extracting column information"""
    
    @staticmethod
    def parse_file(file_content: bytes, filename: str) -> Tuple[List[str], Dict[str, Any]]:
        """
        Parse uploaded file and return column names and sample data.
        
        Returns:
            Tuple of (column_names, column_data) where column_data contains
            sample values and inferred types for each column.
        """
        try:
            # Determine file type
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(BytesIO(file_content))
            elif filename.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(BytesIO(file_content))
            else:
                raise ValueError(f"Unsupported file type: {filename}")
            
            # Get column names
            column_names = df.columns.tolist()
            
            # Extract sample data and infer types
            column_data = {}
            for col in column_names:
                # Get sample values (limit to 10 non-null values)
                sample_values = df[col].dropna().head(10).astype(str).tolist()
                
                # Infer data type
                inferred_type = FileParser._infer_column_type(df[col])
                
                column_data[col] = {
                    'sample_values': sample_values,
                    'inferred_type': inferred_type
                }
            
            return column_names, column_data
            
        except Exception as e:
            raise ValueError(f"Error parsing file: {str(e)}")
    
    @staticmethod
    def _infer_column_type(series: pd.Series) -> str:
        """Infer the data type of a pandas Series"""
        # Remove null values for type inference
        non_null_series = series.dropna()
        
        if len(non_null_series) == 0:
            return "string"
        
        # Check for boolean (common boolean string representations)
        bool_values = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
        if all(str(val).lower() in bool_values for val in non_null_series.head(20)):
            return "boolean"
        
        # Check for numeric
        try:
            pd.to_numeric(non_null_series)
            return "number"
        except:
            pass
        
        # Check for date
        try:
            pd.to_datetime(non_null_series)
            # Additional check for date-like patterns
            sample_str = str(non_null_series.iloc[0])
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            ]
            if any(re.match(pattern, sample_str) for pattern in date_patterns):
                return "date"
        except:
            pass
        
        # Default to string
        return "string"
    
    @staticmethod
    def parse_schema_list(schema_text: str) -> List[str]:
        """
        Parse a text list of column names (one per line).
        """
        lines = [line.strip() for line in schema_text.split('\n') if line.strip()]
        return lines
