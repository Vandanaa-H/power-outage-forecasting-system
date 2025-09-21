#!/usr/bin/env python3
"""
Simple test to verify API startup without full server.
"""

import sys
import os
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def test_api():
    try:
        print("Testing API imports...")
        
        # Test basic imports
        from src.api.main import app
        print("✓ Main app imported successfully")
        
        # Test routes
        print("Available routes:")
        for route in app.routes:
            print(f"  {route.path}")
        
        print("\n✓ API test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api())
    sys.exit(0 if success else 1)