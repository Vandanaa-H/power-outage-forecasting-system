#!/usr/bin/env python3
"""
Simple client to test the Power Outage Forecasting API.
"""

import requests
import json
from datetime import datetime

def test_api():
    """Test the running API server."""
    base_url = "http://127.0.0.1:8000"
    
    print("🔮 POWER OUTAGE FORECASTING API CLIENT")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("Server is healthy!")
            health_data = response.json()
            print(f"   App: {health_data['app_name']}")
            print(f"   Version: {health_data['version']}")
        else:
            print(f"Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"Cannot connect to server: {e}")
        print("Make sure the server is running with: python run_server.py")
        return
    
    # Test live prediction for Bengaluru
    print("\n2. Testing Live Prediction for Bengaluru...")
    live_request = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "grid_data": {
            "substation_id": "BESCOM_BLR_001",
            "load_factor": 0.75,
            "voltage_stability": 0.85,
            "historical_outages": 3,
            "maintenance_status": False,
            "feeder_health": 0.8
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/predict/live", 
            json=live_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Live prediction successful!")
            print(f"   Risk Score: {result['risk_score']:.1f}%")
            print(f"   Confidence: {result['confidence_interval']['lower']:.1f}% - {result['confidence_interval']['upper']:.1f}%")
            print(f"   Risk Level: {result['risk_level']}")
            print(f"   Factors: {', '.join(result['contributing_factors'])}")
            print(f"   Timestamp: {result['prediction_timestamp']}")
        else:
            print(f"Prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"Prediction request failed: {e}")
    
    # Test prediction with high-risk scenario
    print("\n3. Testing High-Risk Scenario...")
    high_risk_request = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "grid_data": {
            "substation_id": "BESCOM_BLR_001",
            "load_factor": 0.95,  # Very high load
            "voltage_stability": 0.60,  # Poor stability
            "historical_outages": 8,  # Many past outages
            "maintenance_status": True,  # Under maintenance
            "feeder_health": 0.50  # Poor health
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/predict/live", 
            json=high_risk_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("High-risk prediction successful!")
            print(f"   Risk Score: {result['risk_score']:.1f}%")
            print(f"   Confidence: {result['confidence_interval']['lower']:.1f}% - {result['confidence_interval']['upper']:.1f}%")
            print(f"   Risk Level: {result['risk_level']}")
            print(f"   Factors: {', '.join(result['contributing_factors'])}")
        else:
            print(f"High-risk prediction failed: {response.status_code}")
    except Exception as e:
        print(f"High-risk request failed: {e}")
    
    print(f"\nAPI Documentation: {base_url}/docs")
    print(f"Health Check: {base_url}/health")
    print(f"🔮 All Endpoints: {base_url}/api/v1/")
    print("\nAPI Testing Complete!")

if __name__ == "__main__":
    test_api()