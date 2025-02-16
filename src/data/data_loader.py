from entsoe import EntsoePandasClient
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import logging
from pathlib import Path
import time
from typing import Optional, Tuple
import pytz
import requests
from entsoe.exceptions import NoMatchingDataError
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.config import ENTSOE_API_KEY, COUNTRY_CODE, RAW_DATA_PATH

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("entsoe_client.log")
    ],
)
logger = logging.getLogger(__name__)

class EntsoeClient:
    """Enhanced ENTSO-E client with robust data fetching capabilities"""
    
    def __init__(self, api_key: str, country_code: str = "DE") -> None:
        """Initialize the ENTSO-E client.
        
        Args:
            api_key (str): ENTSO-E API key
            country_code (str): Country code (default: "DE" for Germany)
        """
        if not api_key:
            logger.error("API key cannot be None")
            raise ValueError("API key is required")
            
        self.country_code = country_code
        self._client = EntsoePandasClient(api_key=api_key)
        
    def _query_load_and_forecast(
        self,
        start_ts: pd.Timestamp,
        end_ts: Optional[pd.Timestamp] = None,
        max_retries: int = 10,
    ) -> pd.DataFrame:
        """Query load and forecast data with retry logic"""
        if end_ts is None:
            end_ts = pd.Timestamp(
                datetime.now() + timedelta(hours=24), 
                tz="Europe/Berlin"
            )
        
        # Split query into smaller chunks to avoid timeouts
        start_end_timestamps = []
        curr_start = start_ts
        
        while curr_start < end_ts:
            curr_end = min(end_ts, curr_start + timedelta(days=7))
            start_end_timestamps.append((curr_start, curr_end))
            curr_start = curr_end

        fetched_dfs = []
        # Use tqdm to show progress bar instead of logging each fetch
        for curr_start, curr_end in tqdm(start_end_timestamps, desc="Fetching load data"):
            for attempt in range(max_retries):
                try:
                    df = self._client.query_load_and_forecast(
                        country_code="DE",
                        start=curr_start,
                        end=curr_end
                    )
                    if not df.empty:
                        if 'Actual Load' not in df.columns and 'Load' in df.columns:
                            df = df.rename(columns={'Load': 'Actual Load'})
                        if 'Forecasted Load' not in df.columns and 'Load Forecast' in df.columns:
                            df = df.rename(columns={'Load Forecast': 'Forecasted Load'})
                    fetched_dfs.append(df)
                    break
                except NoMatchingDataError:
                    df = pd.DataFrame(
                        columns=['Actual Load', 'Forecasted Load'],
                        dtype=float,
                        index=pd.DatetimeIndex([], tz="Europe/Berlin")
                    )
                    fetched_dfs.append(df)
                    break
                except requests.ConnectionError as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                        raise
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)

        # Combine all data
        combined_df = pd.concat(fetched_dfs) if fetched_dfs else pd.DataFrame(
            columns=['Actual Load', 'Forecasted Load'],
            dtype=float,
            index=pd.DatetimeIndex([], tz="Europe/Berlin")
        )
        
        # Only log the final summary
        logger.info(f"Data collection completed. Shape: {combined_df.shape}")
        
        return combined_df

    def get_load_data(
        self,
        hours_back: int = 48,
        forecast_hours: int = 24
    ) -> Tuple[pd.Series, pd.Series]:
        """Get actual and forecasted load data."""
        now = datetime.now(pytz.timezone("Europe/Berlin"))
        now_ts = pd.Timestamp(now)
        
        # Use datetime.timedelta for time calculations
        start_ts = now_ts - timedelta(hours=hours_back)
        end_ts = now_ts + timedelta(hours=forecast_hours)
        
        df = self._query_load_and_forecast(
            start_ts=start_ts,
            end_ts=end_ts
        )
        
        # Split into actual and forecast with debug logging
        actual_load = df['Actual Load'].dropna()
        forecast_load = df['Forecasted Load'].dropna()
        
        logger.info(f"Actual load points: {len(actual_load)}")
        logger.info(f"Forecast load points: {len(forecast_load)}")
        
        if actual_load.empty:
            logger.warning("No actual load data available")
        if forecast_load.empty:
            logger.warning("No forecast load data available")
            
        return actual_load, forecast_load

def get_entsoe_client():
    """Initialize ENTSO-E client"""
    if not ENTSOE_API_KEY:
        raise ValueError("ENTSOE_API_KEY not found in environment variables")
    return EntsoePandasClient(api_key=ENTSOE_API_KEY)

def fetch_load_data(start_date: str, end_date: str, chunk_size: int = 30):
    """
    Fetch load data from ENTSO-E in chunks to handle large date ranges
    
    Args:
        start_date (str): Start date in format YYYYMMDD
        end_date (str): End date in format YYYYMMDD
        chunk_size (int): Number of days per request
    
    Returns:
        pd.DataFrame: Combined load data for the entire period
    """
    client = get_entsoe_client()
    
    # Convert string dates to timezone-aware datetime objects
    tz = pytz.timezone('Europe/Berlin')
    start = tz.localize(datetime.strptime(start_date, '%Y%m%d'))
    end = tz.localize(datetime.strptime(end_date, '%Y%m%d'))
    
    all_data = []
    current_start = start
    
    while current_start < end:
        current_end = min(current_start + timedelta(days=chunk_size), end)
        
        try:
            logger.info(f"Fetching data from {current_start} to {current_end}")
            chunk_data = client.query_load_and_forecast(
                country_code=COUNTRY_CODE,
                start=pd.Timestamp(current_start, tz='Europe/Berlin'),
                end=pd.Timestamp(current_end, tz='Europe/Berlin')
            )
            all_data.append(chunk_data)
            
        except Exception as e:
            logger.error(f"Error fetching data for period {current_start} - {current_end}: {str(e)}")
            # Continue with next chunk instead of failing completely
            
        current_start = current_end
        
    if not all_data:
        logger.error("No data was successfully fetched")
        return None
        
    # Combine all chunks
    combined_data = pd.concat(all_data)
    
    # Save to CSV
    try:
        Path(RAW_DATA_PATH).mkdir(parents=True, exist_ok=True)
        filename = f'load_data_{start_date}_{end_date}.csv'
        filepath = Path(RAW_DATA_PATH) / filename
        combined_data.to_csv(filepath)
        logger.info(f"Data saved to {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
    
    return combined_data

def validate_data(df: pd.DataFrame) -> bool:
    """
    Basic validation of the fetched data
    
    Args:
        df (pd.DataFrame): DataFrame to validate
    
    Returns:
        bool: True if validation passes
    """
    if df is None or df.empty:
        logger.error("Data validation failed: Empty DataFrame")
        return False
        
    # Check for missing values
    missing_pct = df.isnull().mean() * 100
    if missing_pct.max() > 10:  # More than 10% missing values
        logger.warning(f"High percentage of missing values: {missing_pct.max():.2f}%")
        
    return True

# if __name__ == "__main__":
#     # Example usage
#     data = fetch_load_data('20230101', '20240301')
#     if data is not None and validate_data(data):
#         logger.info("Data collection completed successfully")