from enum import Enum
from typing import List, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
from pathlib import Path
from tqdm import tqdm
from wetterdienst.provider.dwd.observation import DwdObservationRequest

from src.config import RAW_DATA_PATH
from src.data.utils import save_data

logger = logging.getLogger(__name__)

class WeatherStation(Enum):
    """Enum for major German weather stations"""
    BERLIN = "00433"     # Berlin-Tempelhof (Northeast)
    HAMBURG = "01975"    # Hamburg-Fuhlsbüttel (North)
    FRANKFURT = "03379"  # Frankfurt/Main (Central/West)

class WeatherClient:
    """Client for fetching weather data from DWD"""
    
    def __init__(self):
        """Initialize weather client with station IDs"""
        self.stations = [station.value for station in WeatherStation]
    
    def fetch_temperature_data(
        self,
        start_date: str,
        end_date: str,
        max_retries: int = 3,
        chunk_size: int = 30
    ) -> pd.DataFrame:
        """
        Fetch hourly temperature data from DWD for major German cities
        
        Args:
            start_date (str): Start date in format YYYYMMDD
            end_date (str): End date in format YYYYMMDD
            max_retries (int): Maximum number of retry attempts
            chunk_size (int): Number of days per request
            
        Returns:
            pd.DataFrame: Hourly temperature data for all stations
        """
        try:
            logger.info("Initiating weather data fetch from DWD")
            
            # Clean and validate dates
            start_date = start_date.strip()
            end_date = end_date.strip()
            
            if not (len(start_date) == 8 and len(end_date) == 8):
                raise ValueError("Dates must be in YYYYMMDD format")
            
            # Convert to datetime
            start = datetime.strptime(start_date, '%Y%m%d')
            end = datetime.strptime(end_date, '%Y%m%d')
            
            if end <= start:
                raise ValueError("End date must be after start date")
            
            # Calculate number of chunks
            total_days = (end - start).days
            num_chunks = (total_days + chunk_size - 1) // chunk_size
            
            all_data = []
            current_start = start
            
            with tqdm(total=num_chunks * len(self.stations), 
                     desc="Fetching Weather Data") as pbar:
                
                while current_start < end:
                    current_end = min(current_start + timedelta(days=chunk_size), end)
                    chunk_start = current_start.strftime('%Y%m%d')
                    chunk_end = current_end.strftime('%Y%m%d')
                    
                    for attempt in range(max_retries):
                        try:
                            # Create request for hourly temperature data
                            request = DwdObservationRequest(
                                parameter="temperature_air",
                                resolution="hourly",
                                start_date=chunk_start,
                                end_date=chunk_end
                            )
                            
                            # Get values for selected stations and convert to pandas
                            values = request.filter_by_station_id(
                                self.stations
                            ).values.all().df
                            
                            if len(values) > 0:
                                # Convert Polars DataFrame to Pandas DataFrame
                                pandas_df = values.to_pandas()
                                all_data.append(pandas_df)
                                pbar.update(len(self.stations))
                                break
                                
                        except Exception as e:
                            if attempt == max_retries - 1:
                                logger.error(f"Failed chunk {chunk_start}-{chunk_end}: {str(e)}")
                                pbar.update(len(self.stations))
                            else:
                                wait_time = 2 ** attempt
                                logger.warning(f"Attempt {attempt + 1} failed, waiting {wait_time}s")
                                time.sleep(wait_time)
                    
                    current_start = current_end
            
            if not all_data:
                logger.error("No weather data was successfully fetched")
                return pd.DataFrame()
            
            # Combine all chunks
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Process combined data
            df_pivoted = combined_df.pivot_table(
                index='date',
                columns='station_id',
                values='value',
                aggfunc='mean'
            )
            
            # Rename columns to city names
            df_pivoted.columns = [
                f"temperature_{station.name.lower()}"
                for station in WeatherStation
            ]
            
            # Convert temperature from Kelvin to Celsius
            for col in df_pivoted.columns:
                df_pivoted[col] = df_pivoted[col] - 273.15
                logger.info(f"Converted {col} from Kelvin to Celsius")
            
            # Save processed data
            filename = f'weather_temperature_{start_date}_{end_date}.csv'
            save_data(df_pivoted, filename)
            
            return df_pivoted
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            raise
    
    def get_latest_temperature(self) -> pd.DataFrame:
        """
        Fetch the most recent temperature data (last 24 hours)
        
        Returns:
            pd.DataFrame: Latest temperature data
        """
        try:
            # Get today and yesterday's date
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now().date() - pd.Timedelta(days=1)).strftime('%Y%m%d')
            
            return self.fetch_temperature_data(
                start_date=start_date,
                end_date=end_date,
                chunk_size=1  # Small chunk size for recent data
            )
            
        except Exception as e:
            logger.error(f"Error fetching latest temperature data: {str(e)}")
            raise 