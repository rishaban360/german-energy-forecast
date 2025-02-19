from enum import Enum
from typing import List, Optional, Dict
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

class RenewableType(Enum):
    """Enum for renewable energy types and their ENTSO-E codes"""
    SOLAR = "B16"
    WIND_OFFSHORE = "B18"
    WIND_ONSHORE = "B19"
    BIOMASS = "B01"
    HYDRO_WATER_RESERVOIR = "B05"
    HYDRO_RUN_OF_RIVER = "B11"

class RenewableClient:
    """Client for fetching renewable generation data from ENTSO-E"""
    
    def __init__(self, api_key: str = ENTSOE_API_KEY, country_code: str = COUNTRY_CODE):
        """Initialize ENTSO-E client for renewable data"""
        self.client = EntsoePandasClient(api_key=api_key)
        self.country_code = country_code
        self.tz = pytz.timezone('Europe/Berlin')
    
    def fetch_renewable_data(
        self,
        start_date: str,
        end_date: str,
        renewable_types: Optional[List[RenewableType]] = None,
        chunk_size: int = 30,
        max_retries: int = 5
    ) -> pd.DataFrame:
        """Fetch renewable data with improved error handling"""
        try:
            if renewable_types is None:
                renewable_types = list(RenewableType)
            
            # Clean and validate dates
            start_date = start_date.strip()
            end_date = end_date.strip()
            
            start = self.tz.localize(datetime.strptime(start_date, '%Y%m%d'))
            end = self.tz.localize(datetime.strptime(end_date, '%Y%m%d'))
            
            # Calculate total operations
            total_days = (end - start).days
            num_chunks = (total_days + chunk_size - 1) // chunk_size
            total_operations = num_chunks * len(renewable_types)
            
            all_data = {}
            current_start = start
            
            with tqdm(total=total_operations, desc="Fetching Renewable Data") as pbar:
                while current_start < end:
                    current_end = min(current_start + timedelta(days=chunk_size), end)
                    
                    for r_type in renewable_types:
                        if r_type.name.lower() not in all_data:
                            all_data[r_type.name.lower()] = []
                        
                        success = False
                        for attempt in range(max_retries):
                            try:
                                logger.info(f"Fetching {r_type.name} data from {current_start} to {current_end}")
                                chunk_data = self.client.query_generation(
                                    country_code=self.country_code,
                                    start=pd.Timestamp(current_start),
                                    end=pd.Timestamp(current_end),
                                    psr_type=r_type.value
                                )
                                
                                if not isinstance(chunk_data, pd.DataFrame):
                                    raise ValueError(f"Invalid data received for {r_type.name}")
                                
                                if not chunk_data.empty:
                                    all_data[r_type.name.lower()].append(chunk_data)
                                    success = True
                                    break
                                else:
                                    logger.warning(f"Empty data received for {r_type.name}")
                                    
                            except requests.exceptions.RequestException as e:
                                wait_time = min(2 ** attempt, 60)  # Cap wait time at 60 seconds
                                logger.warning(f"Request failed for {r_type.name}, attempt {attempt + 1}/{max_retries}. Error: {str(e)}")
                                logger.warning(f"Waiting {wait_time} seconds before retry...")
                                time.sleep(wait_time)
                                
                            except Exception as e:
                                logger.error(f"Error fetching {r_type.name}: {str(e)}")
                                break
                        
                        if not success:
                            logger.error(f"Failed to fetch data for {r_type.name} after {max_retries} attempts")
                        
                        pbar.update(1)
                    
                    current_start = current_end
            
            # Process successful data
            combined_df = pd.DataFrame()
            for r_type, data_list in all_data.items():
                if data_list:
                    try:
                        df = pd.concat(data_list)
                        
                        # Handle different data formats based on renewable type
                        if r_type.lower() == 'wind_offshore':
                            # Wind Offshore has a simple column name
                            if 'Wind Offshore' in df.columns:
                                combined_df[f'{r_type}_generation'] = df['Wind Offshore']
                                logger.info(f"Successfully processed {r_type} data")
                        else:
                            # Solar and Wind Onshore have MultiIndex columns
                            if isinstance(df.columns, pd.MultiIndex):
                                type_name = r_type.replace('_', ' ').title()
                                if (type_name, 'Actual Aggregated') in df.columns:
                                    combined_df[f'{r_type}_generation'] = df[(type_name, 'Actual Aggregated')]
                                    logger.info(f"Successfully processed {r_type} data")
                            else:
                                logger.warning(f"Unexpected column format for {r_type}: {df.columns}")
                    
                    except Exception as e:
                        logger.error(f"Error processing {r_type} data: {str(e)}")
                        logger.error(f"Data type: {type(df)}")
                        logger.error(f"Columns: {df.columns}")
            
            if combined_df.empty:
                logger.error("No renewable data was successfully fetched")
                return combined_df
            
            # Ensure the index is timezone-aware
            if combined_df.index.tz is None:
                combined_df.index = combined_df.index.tz_localize(self.tz)
            
            # Sort the index to ensure chronological order
            combined_df = combined_df.sort_index()
            
            # Save to CSV
            filename = f'renewable_generation_{start_date}_{end_date}.csv'
            save_data(combined_df, filename)
            
            return combined_df
            
        except Exception as e:
            logger.error(f"Error in renewable data collection: {str(e)}")
            raise
    
    def get_latest_renewable_data(
        self,
        renewable_types: Optional[List[RenewableType]] = None
    ) -> pd.DataFrame:
        """
        Fetch the most recent renewable generation data (last 24 hours)
        
        Args:
            renewable_types (List[RenewableType], optional): Types to fetch
            
        Returns:
            pd.DataFrame: Latest renewable generation data
        """
        try:
            end = datetime.now(self.tz)
            start = end - timedelta(days=1)
            
            # Convert to string format for fetch_renewable_data
            start_date = start.strftime('%Y%m%d')
            end_date = end.strftime('%Y%m%d')
            
            return self.fetch_renewable_data(
                start_date=start_date,
                end_date=end_date,
                renewable_types=renewable_types,
                chunk_size=1
            )
            
        except Exception as e:
            logger.error(f"Error fetching latest renewable data: {str(e)}")
            raise