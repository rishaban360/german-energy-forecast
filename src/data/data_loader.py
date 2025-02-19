from typing import Dict, Optional, List
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

from src.data.clients.entsoe_client import EntsoeClient
from src.data.clients.weather_client import WeatherClient
from src.data.clients.renewable_client import RenewableClient, RenewableType
from src.config import RAW_DATA_PATH

logger = logging.getLogger(__name__)

class DataLoader:
    """Combined data loader for all data sources"""
    
    def __init__(self):
        """Initialize all clients"""
        self.entsoe_client = EntsoeClient()
        self.weather_client = WeatherClient()
        self.renewable_client = RenewableClient()
    
    def fetch_all_data(
        self,
        start_date: str,
        end_date: str,
        renewable_types: Optional[List[RenewableType]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch all required data from all sources with progress bars
        
        Args:
            start_date (str): Start date in format YYYYMMDD
            end_date (str): End date in format YYYYMMDD
            renewable_types (List[RenewableType], optional): Specific renewable types to fetch
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all fetched data
        """
        try:
            logger.info(f"Starting comprehensive data collection from {start_date} to {end_date}")
            
            # Create progress bar for overall process
            with tqdm(total=3, desc="Overall Progress") as pbar:
                # Fetch load data
                logger.info("Fetching load data...")
                load_data = self.entsoe_client.fetch_load_data(
                    start_date=start_date,
                    end_date=end_date
                )
                pbar.update(1)
                
                # Fetch weather data
                logger.info("Fetching weather data...")
                weather_data = self.weather_client.fetch_temperature_data(
                    start_date=start_date,
                    end_date=end_date
                )
                pbar.update(1)
                
                # Fetch renewable data
                logger.info("Fetching renewable generation data...")
                renewable_data = self.renewable_client.fetch_renewable_data(
                    start_date=start_date,
                    end_date=end_date,
                    renewable_types=renewable_types
                )
                pbar.update(1)
            
            # Standardize timezones to Europe/Berlin
            weather_data.index = weather_data.index.tz_convert('Europe/Berlin')
            
            return {
                'load': load_data,
                'weather': weather_data,
                'renewable': renewable_data
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive data collection: {str(e)}")
            raise
    
    def fetch_latest_data(
        self,
        renewable_types: Optional[List[RenewableType]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch the most recent data from all sources (last 24 hours)
        
        Args:
            renewable_types (List[RenewableType], optional): Specific renewable types to fetch
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing latest data
        """
        try:
            logger.info("Fetching latest data from all sources")
            
            latest_load = self.entsoe_client.get_latest_load()
            latest_weather = self.weather_client.get_latest_temperature()
            latest_renewable = self.renewable_client.get_latest_renewable_data(
                renewable_types=renewable_types
            )
            
            return {
                'load': latest_load,
                'weather': latest_weather,
                'renewable': latest_renewable
            }
            
        except Exception as e:
            logger.error(f"Error fetching latest data: {str(e)}")
            raise
    
    def load_cached_data(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, pd.DataFrame]:
        """
        Load previously saved data from CSV files
        
        Args:
            start_date (str): Start date in format YYYYMMDD
            end_date (str): End date in format YYYYMMDD
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing cached data
        """
        try:
            data = {}
            
            # Load each data type
            for data_type in ['load', 'weather', 'renewable']:
                filename = f"{data_type}_{'generation_' if data_type == 'renewable' else ''}{start_date}_{end_date}.csv"
                filepath = Path(RAW_DATA_PATH) / filename
                
                if filepath.exists():
                    logger.info(f"Loading cached {data_type} data from {filepath}")
                    data[data_type] = pd.read_csv(filepath, index_col=0, parse_dates=True)
                else:
                    logger.warning(f"No cached {data_type} data found at {filepath}")
                    data[data_type] = pd.DataFrame()
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading cached data: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    try:
        # Initialize loader
        data_loader = DataLoader()
        
        # Example date range
        start_date = "20230101"
        end_date = "20240301"
        
        # Fetch all historical data
        historical_data = data_loader.fetch_all_data(
            start_date=start_date,
            end_date=end_date,
            renewable_types=[
                RenewableType.SOLAR,
                RenewableType.WIND_OFFSHORE,
                RenewableType.WIND_ONSHORE
            ]
        )
        
        # Fetch latest data
        latest_data = data_loader.fetch_latest_data()
        
        # Load cached data
        cached_data = data_loader.load_cached_data(
            start_date=start_date,
            end_date=end_date
        )
        
        # Print summaries
        for data_type, df in historical_data.items():
            if not df.empty:
                print(f"\n=== {data_type.title()} Data Summary ===")
                print(f"Time range: {df.index.min()} to {df.index.max()}")
                print(f"Data shape: {df.shape}")
                print(f"Columns: {df.columns.tolist()}")
                print("\nSample data:")
                print(df.head())
                
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")