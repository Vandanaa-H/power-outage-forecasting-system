#!/usr/bin/env python3
"""
Simple server runner that stays up.
"""

import os
import sys
import uvicorn

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("Starting Power Outage Forecasting API...")
    print("📡 Server will run on: http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("Health Check: http://127.0.0.1:8000/health")
    print("🔮 Live Predictions: http://127.0.0.1:8000/api/v1/predict/live")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )