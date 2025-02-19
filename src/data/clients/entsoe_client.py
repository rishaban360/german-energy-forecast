from typing import Dict, Optional, List
import pandas as pd
import pytz
from datetime import datetime, timedelta
import time
import requests
import logging
from pathlib import Path
from entsoe import EntsoePandasClient
from entsoe.exceptions import NoMatchingDataError
from tqdm import tqdm

from src.config import ENTSOE_API_KEY, COUNTRY_CODE, RAW_DATA_PATH
from src.data.utils import save_data

logger = logging.getLogger(__name__)

class EntsoeClient:
    """Client for fetching load data from ENTSO-E"""
    
    def __init__(self, api_key: str = ENTSOE_API_KEY, country_code: str = COUNTRY_CODE):
        """Initialize ENTSO-E client with API key and country code"""
        self.client = EntsoePandasClient(api_key=api_key)
        self.country_code = country_code
        self.tz = pytz.timezone('Europe/Berlin')
    
    def fetch_load_data(
        self,
        start_date: str,
        end_date: str,
        chunk_size: int = 30,
        max_retries: int = 3
    ) -> pd.DataFrame:
        """
        Fetch load data from ENTSO-E in chunks with retry logic
        
        Args:
            start_date (str): Start date in format YYYYMMDD
            end_date (str): End date in format YYYYMMDD
            chunk_size (int): Number of days per request
            max_retries (int): Maximum number of retry attempts
        
        Returns:
            pd.DataFrame: Combined load data for the entire period
        """
        try:
            # Clean input dates
            start_date = start_date.strip()
            end_date = end_date.strip()
            
            # Validate date format
            if not (len(start_date) == 8 and len(end_date) == 8):
                raise ValueError("Dates must be in YYYYMMDD format")
            
            start = self.tz.localize(datetime.strptime(start_date, '%Y%m%d'))
            end = self.tz.localize(datetime.strptime(end_date, '%Y%m%d'))
            
            # Validate date range
            if end <= start:
                raise ValueError("End date must be after start date")
            
            # Calculate number of chunks
            total_days = (end - start).days
            num_chunks = (total_days + chunk_size - 1) // chunk_size
            
            all_data = []
            current_start = start
            
            # Create progress bar for chunks
            with tqdm(total=num_chunks, desc="Fetching Load Data") as pbar:
                while current_start < end:
                    current_end = min(current_start + timedelta(days=chunk_size), end)
                    
                    for attempt in range(max_retries):
                        try:
                            logger.info(f"Fetching data from {current_start} to {current_end}")
                            chunk_data = self.client.query_load_and_forecast(
                                country_code=self.country_code,
                                start=pd.Timestamp(current_start),
                                end=pd.Timestamp(current_end)
                            )
                            
                            if not chunk_data.empty:
                                all_data.append(chunk_data)
                                break
                                
                        except NoMatchingDataError:
                            logger.warning(f"No data found between {current_start} and {current_end}")
                            break
                            
                        except requests.ConnectionError as e:
                            if attempt == max_retries - 1:
                                logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                                raise
                            wait_time = 2 ** attempt
                            logger.warning(f"Attempt {attempt + 1} failed, waiting {wait_time} seconds")
                            time.sleep(wait_time)
                    
                    current_start = current_end
                    pbar.update(1)
            
            if not all_data:
                logger.error("No data was successfully fetched")
                return pd.DataFrame()
            
            # Combine all chunks
            combined_data = pd.concat(all_data)
            
            # Save to CSV
            filename = f'load_data_{start_date}_{end_date}.csv'
            save_data(combined_data, filename)
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error fetching load data: {str(e)}")
            raise
    
    def get_latest_load(self) -> pd.DataFrame:
        """
        Fetch the most recent load data (last 24 hours)
        
        Returns:
            pd.DataFrame: Latest load data
        """
        try:
            end = datetime.now(self.tz)
            start = end - timedelta(days=1)
            
            data = self.client.query_load_and_forecast(
                country_code=self.country_code,
                start=pd.Timestamp(start),
                end=pd.Timestamp(end)
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching latest load data: {str(e)}")
            raise