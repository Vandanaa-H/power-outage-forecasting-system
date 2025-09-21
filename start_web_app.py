#!/usr/bin/env python3
"""
Complete application startup script - Backend + Frontend
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def start_backend():
    """Start the backend API server."""
    print("Starting Backend API Server...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "src.api.main:app", "--reload", "--port", "8000"
    ], cwd=os.getcwd())
    return backend_process

def start_frontend():
    """Start the frontend React development server."""
    print("Starting Frontend React App...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("Frontend directory not found!")
        return None
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    
    frontend_process = subprocess.Popen([
        "npm", "start"
    ], cwd=frontend_dir)
    return frontend_process

def main():
    """Main startup function."""
    print("STARTING 24-HOUR POWER OUTAGE FORECASTING SYSTEM")
    print("=" * 60)
    
    try:
        # Start backend
        backend = start_backend()
        print("Backend starting on http://127.0.0.1:8000")
        
        # Wait a moment for backend to initialize
        print("Waiting for backend to initialize...")
        time.sleep(5)
        
        # Start frontend
        frontend = start_frontend()
        print("Frontend starting on http://localhost:3000")
        
        print("\nBOTH SERVERS STARTING!")
        print("Frontend Dashboard: http://localhost:3000")
        print("Backend API: http://127.0.0.1:8000")
        print("API Docs: http://127.0.0.1:8000/docs")
        print("\nThe web browser will open automatically...")
        print("Press Ctrl+C to stop both servers")
        print("=" * 60)
        
        # Wait a bit more for frontend to start
        time.sleep(10)
        
        # Open browser to frontend
        try:
            webbrowser.open("http://localhost:3000")
        except:
            print("Please manually open: http://localhost:3000")
        
        # Wait for processes
        frontend.wait()
        backend.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        if 'backend' in locals():
            backend.terminate()
        if 'frontend' in locals():
            frontend.terminate()
        print("Servers stopped")
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Make sure Node.js is installed for the frontend")

if __name__ == "__main__":
    main()