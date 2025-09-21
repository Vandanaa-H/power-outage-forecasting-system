#!/usr/bin/env python3
"""
Robust server startup script for the Power Outage Forecasting API.
"""

import os
import sys
import uvicorn
import asyncio
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_components():
    """Test key components before starting server."""
    try:
        logger.info("Testing API components...")
        
        # Test model loading
        from src.api.routes.predictions import get_model_instance
        model = get_model_instance()
        logger.info(f"✓ Model loaded: {type(model).__name__}")
        
        # Test sample prediction
        sample_data = {
            'weather': {'temperature': 25, 'humidity': 60, 'wind_speed': 10, 'rainfall': 0, 'lightning_strikes': 0, 'storm_alert': False},
            'grid': {'load_factor': 0.7, 'voltage_stability': 0.9, 'historical_outages': 2, 'transformer_load': 0.7, 'feeder_health': 0.8},
            'prediction_horizon': 24
        }
        result = await model.predict(sample_data)
        logger.info(f"✓ Sample prediction: {result['risk_score']:.1f}% risk")
        
        # Test API app creation
        from src.api.main import app
        logger.info(f"✓ API app created with {len(app.routes)} routes")
        
        logger.info("All components tested successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main server startup function."""
    logger.info("Starting 24-Hour Power Outage Forecasting System...")
    
    # Test components first
    if not asyncio.run(test_components()):
        logger.error("Component tests failed. Exiting.")
        sys.exit(1)
    
    # Start the server
    try:
        logger.info("Starting Uvicorn server on http://127.0.0.1:8000")
        
        uvicorn.run(
            "src.api.main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,  # Disable reload for stability
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()