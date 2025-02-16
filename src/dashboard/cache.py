from functools import lru_cache
from datetime import datetime, timedelta


from src.dashboard.config import Config
from src.dashboard.entsoe_client import EntsoeClient



@lru_cache(maxsize=1)
def get_cached_data(timestamp_key):
    """Cache data for 5 minutes using timestamp as key"""
    client = EntsoeClient(api_key=Config.ENTSOE_API_KEY)
    return client.get_load_data()

def get_timestamp_key():
    """Generate key based on 5-minute intervals"""
    now = datetime.now()
    return now.replace(second=0, microsecond=0).strftime('%Y%m%d%H%M') 