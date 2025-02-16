from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
ROOT_DIR = Path(__file__).parent.parent  # Gets the project root directory
DATA_DIR = ROOT_DIR / 'data'
RAW_DATA_PATH = DATA_DIR / 'raw'
CACHE_DIR = DATA_DIR / 'cache'

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# Dashboard Settings
DASHBOARD_HOST = "127.0.0.1"
DASHBOARD_PORT = 8050

# Data Settings
COUNTRY_CODE = "DE"
TIMEZONE = "Europe/Berlin"

# API Keys
ENTSOE_API_KEY = os.getenv("ENTSOE_API_KEY")

# Endpoints
API_BASE_URL = f"http://localhost:{API_PORT}"

class Config:
    # API Configuration
    ENTSOE_API_KEY = ENTSOE_API_KEY
    COUNTRY_CODE = COUNTRY_CODE
    
    # Dashboard Configuration
    DASHBOARD_HOST = DASHBOARD_HOST
    DASHBOARD_PORT = DASHBOARD_PORT
    UPDATE_INTERVAL = 15  # minutes
    
    # Data Configuration
    DATA_DIR = DATA_DIR
    CACHE_DIR = CACHE_DIR
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)

# # src/config.py
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # API Configuration
# ENTSOE_API_KEY = os.getenv('ENTSOE_API_KEY')
# WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')  # if we decide to use weather data

# # Country Configuration
# COUNTRY_CODE = 'DE'  # Germany's country code for ENTSO-E

# # Time Configuration
# DEFAULT_START_DATE = '20230101'  # Format: YYYYMMDD
# DEFAULT_END_DATE = '20240301'    # Format: YYYYMMDD

# # Data paths
# RAW_DATA_PATH = 'data/raw'
# PROCESSED_DATA_PATH = 'data/processed'

