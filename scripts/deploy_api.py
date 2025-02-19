from fastapi import FastAPI
# Set project root to path
import sys
from pathlib import Path
import pandas as pd
import os
import numpy as np

# Get the absolute path to the project root
current_dir = Path().absolute()
project_root = current_dir.parent if 'notebooks' in str(current_dir) else current_dir

# Add the project root to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"Project root added to path: {project_root}")
from src.models.forecaster import EnergyForecaster
from src.data.data_loader import EntsoeClient
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()
forecaster = EnergyForecaster()

# Train the model with some dummy data for testing
dates = pd.date_range(start='2024-01-01', periods=24, freq='h')
training_data = pd.DataFrame({
    'load': [50000 + np.random.normal(0, 1000) for _ in range(24)]
}, index=dates)
forecaster.train(training_data)  # Train the model before using it

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourusername.github.io"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Only initialize EntsoeClient if API key is available
try:
    from src.data.entsoe_client import EntsoeClient
    api_key = os.getenv('ENTSOE_API_KEY')
    if api_key:
        client = EntsoeClient(api_key=api_key)
    else:
        client = None
except ImportError:
    client = None

@app.get("/api/latest-forecast")
async def get_latest_forecast():
    if client:
        # Use real ENTSOE data if client is available
        actual_load, forecast_load = client.get_load_data()
    else:
        # Use mock data for testing
        dates = pd.date_range(start='2024-01-01', periods=24, freq='h')
        mock_data = pd.DataFrame({
            'load': [50000 + i * 1000 for i in range(24)]
        }, index=dates)
        actual_load = mock_data['load']
        forecast_load = [x * 1.1 for x in actual_load]  # Mock forecast
    
    # Generate model forecasts using the trained model
    model_forecast = forecaster.predict(mock_data)
    
    return {
        "actual_load": actual_load.tolist(),
        "entsoe_forecast": forecast_load,
        "model_forecast": model_forecast.tolist(),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 