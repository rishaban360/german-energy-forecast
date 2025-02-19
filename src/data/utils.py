import pandas as pd
from pathlib import Path
import logging

from src.config import RAW_DATA_PATH

logger = logging.getLogger(__name__)

def save_data(df: pd.DataFrame, filename: str) -> None:
    """
    Save DataFrame to CSV file
    
    Args:
        df (pd.DataFrame): DataFrame to save
        filename (str): Name of the file
    """
    try:
        Path(RAW_DATA_PATH).mkdir(parents=True, exist_ok=True)
        filepath = Path(RAW_DATA_PATH) / filename
        df.to_csv(filepath)
        logger.info(f"Data saved to {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        raise 