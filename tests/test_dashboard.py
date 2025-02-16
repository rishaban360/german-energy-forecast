import requests
import time
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.dashboard.app import app
from src.config import Config

def test_dashboard_availability():
    """Test if dashboard is accessible"""
    url = f"http://{Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}"
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def test_data_updates():
    """Test if data updates are working"""
    client = app.client
    try:
        actual_load, forecast_load = client.get_load_data()
        return len(actual_load) > 0 and len(forecast_load) > 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing dashboard...")
    
    # Test 1: Dashboard Availability
    print("\n1. Testing dashboard availability...")
    if test_dashboard_availability():
        print("✓ Dashboard is accessible")
    else:
        print("✗ Dashboard is not accessible")
    
    # Test 2: Data Updates
    print("\n2. Testing data updates...")
    if test_data_updates():
        print("✓ Data updates are working")
    else:
        print("✗ Data updates failed") 