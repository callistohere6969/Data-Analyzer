"""Data loading and validation utilities for CSV, Excel, and JSON files"""

import pandas as pd
import json
from pathlib import Path
from typing import Tuple, Optional, Dict, Any


def load_data_file(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load data file (CSV, Excel, or JSON) with error handling
    
    Args:
        file_path: Path to data file
    
    Returns:
        Tuple of (DataFrame, error_message)
        - DataFrame is None if error occurs
        - error_message is None if successful
    """
    try:
        file_extension = Path(file_path).suffix.lower()
        
        # Load based on file type
        if file_extension == '.csv':
            df = pd.read_csv(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, engine='openpyxl' if file_extension == '.xlsx' else None)
        elif file_extension == '.json':
            df = pd.read_json(file_path)
        else:
            return None, f"Unsupported file format: {file_extension}. Supported: .csv, .xlsx, .xls, .json"
        
        # Basic validation
        if df.empty:
            return None, "File is empty"
        
        if len(df.columns) == 0:
            return None, "File has no columns"
        
        return df, None
        
    except FileNotFoundError:
        return None, f"File not found: {file_path}"
    except pd.errors.EmptyDataError:
        return None, "File is empty"
    except pd.errors.ParserError as e:
        return None, f"Parsing error: {str(e)}"
    except json.JSONDecodeError as e:
        return None, f"JSON parsing error: {str(e)}"
    except Exception as e:
        return None, f"Error loading file: {str(e)}"


# Backward compatibility
def load_csv(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Legacy function - redirects to load_data_file"""
    return load_data_file(file_path)


def get_dataframe_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Quick summary of DataFrame for agent context
    
    Args:
        df: pandas DataFrame to summarize
    
    Returns:
        Dictionary containing shape, columns, dtypes, missing values, and sample rows
    """
    return {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        "sample_rows": df.head(3).to_dict(orient='records')
    }


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate DataFrame for analysis
    
    Args:
        df: pandas DataFrame to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if df is None:
        return False, "DataFrame is None"
    
    if df.empty:
        return False, "DataFrame is empty"
    
    if len(df.columns) == 0:
        return False, "DataFrame has no columns"
    
    if len(df) < 2:
        return False, "DataFrame has fewer than 2 rows"
    
    return True, "DataFrame is valid"
