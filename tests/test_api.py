import pytest
from fastapi.testclient import TestClient  # This is now correct
from scripts.deploy_api import app
import numpy as np
from datetime import datetime

client = TestClient(app)

def test_latest_forecast_endpoint():
    """Test the /api/latest-forecast endpoint"""
    response = client.get("/api/latest-forecast")
    
    # Test response status
    assert response.status_code == 200
    
    # Test response structure
    data = response.json()
    assert all(key in data for key in [
        "actual_load", 
        "entsoe_forecast", 
        "model_forecast", 
        "timestamp"
    ])
    
    # Test data types and shapes
    assert isinstance(data["actual_load"], list)
    assert isinstance(data["entsoe_forecast"], list)
    assert isinstance(data["model_forecast"], list)
    assert len(data["actual_load"]) == 24  # We expect 24 hours of data
    
    # Test timestamp format
    try:
        datetime.fromisoformat(data["timestamp"])
    except ValueError:
        pytest.fail("Invalid timestamp format")

def test_cors_headers():
    """Test CORS headers are properly set"""
    response = client.get(
        "/api/latest-forecast",
        headers={"Origin": "https://yourusername.github.io"}
    )
    assert response.headers["access-control-allow-origin"] == "https://yourusername.github.io"