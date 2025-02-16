import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Class responsible for processing and cleaning the raw data."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def _enforce_data_quality(df: pd.DataFrame) -> pd.DataFrame:
        """Enforce data quality checks on the dataframe.

        Args:
            df (pd.DataFrame): Input dataframe to check

        Raises:
            ValueError: If data quality checks fail

        Returns:
            pd.DataFrame: Cleaned dataframe
        """
        # Check index
        if not isinstance(df.index, pd.DatetimeIndex):
            logger.error(f"Index must be DatetimeIndex, got {type(df.index)}")
            raise ValueError
        
        # Handle duplicates
        if not df.index.is_unique:
            logger.warning("Duplicate indices found. Aggregating with median...")
            df = df.groupby(df.index).median()
            
        # Sort index
        if not df.index.is_monotonic_increasing:
            logger.warning("Index not monotonic. Sorting...")
            df = df.sort_index()

        return df

    @staticmethod
    def _handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataframe.

        Args:
            df (pd.DataFrame): Input dataframe

        Returns:
            pd.DataFrame: Dataframe with handled missing values
        """
        # Log missing value stats
        missing_stats = df.isnull().sum()
        if missing_stats.any():
            logger.info(f"Missing values per column:\n{missing_stats}")

        # Forward fill limited to 1 hour gaps
        df = df.fillna(method='ffill', limit=1)
        
        return df

    @staticmethod
    def _remove_outliers(df: pd.DataFrame, columns: list, threshold: float = 3) -> pd.DataFrame:
        """Remove outliers using z-score method.

        Args:
            df (pd.DataFrame): Input dataframe
            columns (list): Columns to check for outliers
            threshold (float): Z-score threshold

        Returns:
            pd.DataFrame: Dataframe with outliers removed
        """
        df_clean = df.copy()
        
        for col in columns:
            if col in df.columns:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                mask = z_scores < threshold
                df_clean.loc[~mask, col] = np.nan
                removed = (~mask).sum()
                if removed > 0:
                    logger.warning(f"Removed {removed} outliers from {col}")

        return df_clean

    def process_data(self, input_path: str, output_path: str) -> None:
        """Main method to process the data.

        Args:
            input_path (str): Path to input data file
            output_path (str): Path to save processed data
        """
        logger.info(f"Processing data from {input_path}")

        # Read data
        df = pd.read_csv(input_path, parse_dates=['timestamp'], index_col='timestamp')

        # Apply processing steps
        df = self._enforce_data_quality(df)
        df = self._handle_missing_values(df)
        
        # Remove outliers from numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df = self._remove_outliers(df, columns=numeric_columns)

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save processed data
        df.to_csv(output_path)
        logger.info(f"Processed data saved to {output_path}")