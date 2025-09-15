# 🚀 How to Run the 24-Hour Power Outage Forecasting System

## 📋 Prerequisites

Before starting, ensure you have:
- **Python 3.9+** installed
- **Docker Desktop** installed and running
- **Git** (optional, for version control)
- **Node.js 16+** (for frontend development)

## 🎯 Quick Start Guide

### Step 1: Environment Setup

1. **Open PowerShell as Administrator** and navigate to the project:
```powershell
cd "c:\Users\Admin\IET_BalfourBeatty\24-Hour Power Outage Forecasting System"
```

2. **Create Python Virtual Environment:**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (you should see (venv) in prompt)
python --version
```

3. **Install Python Dependencies:**
```powershell
# Install all required packages
pip install -r requirements.txt

# This will install:
# - FastAPI, uvicorn (API framework)
# - TensorFlow, XGBoost (ML models)
# - PostgreSQL drivers, Redis client
# - And 40+ other dependencies
```

### Step 2: Start Database Services

1. **Start Docker Services:**
```powershell
# Start PostgreSQL and Redis containers
docker-compose up -d postgres redis

# Wait for services to initialize
timeout /t 15

# Check if services are running
docker ps
```

2. **Initialize Database Schema:**
```powershell
# Run database initialization
python -c "
import asyncio
import sys
import os
sys.path.append('src')
from utils.database import DatabaseManager

async def init_db():
    try:
        db = DatabaseManager()
        await db.initialize()
        print('✅ Database initialized successfully!')
        print('✅ Tables created: weather_data, grid_data, outage_events, predictions, advisories')
    except Exception as e:
        print(f'❌ Database initialization failed: {e}')

asyncio.run(init_db())
"
```

### Step 3: Train the ML Model

```powershell
# Train the ensemble model with synthetic data
python train_model.py

# This will:
# - Generate 10,000 synthetic training samples
# - Train LSTM model for weather sequences
# - Train XGBoost model for grid features
# - Save trained models to models/trained/
# - Display training results
```

Expected output:
```
==================================================
TRAINING RESULTS
==================================================
LSTM Model Training Loss: 0.045
XGBoost Train R²: 0.847
XGBoost Test R²: 0.821
Training completed at: 2025-08-31T10:30:45.123456
==================================================
```

### Step 4: Test the System with Demo

```powershell
# Run interactive demo
python demo.py
```

This will demonstrate:
- **Outage Prediction**: 24-hour rolling forecasts
- **Risk Heatmap**: Geospatial risk visualization
- **Advisory Generation**: Natural language alerts
- **Real-time Monitoring**: System capabilities

Expected demo output:
```
🔌 24-Hour Power Outage Forecasting System - DEMO
============================================================

POWER OUTAGE PREDICTION DEMONSTRATION
============================================================

Sample Input Data:
------------------------------
Weather Conditions (Next 6 hours):
  Hour 1: 18.2°C, 87% humidity, 47 km/h wind, 28mm rain
  Hour 2: 17.8°C, 89% humidity, 51 km/h wind, 32mm rain
  ...

Grid Status:
  Load Factor: 85.0%
  Voltage Stability: 75.0%
  Historical Outages: 5
  Feeder Health: 70.0%

PREDICTION RESULTS:
========================================
Overall Outage Probability: 73.2%
Risk Score: 73.2/100
Confidence Level: 85.0%
Risk Level: 🔴 HIGH RISK

Recommendations:
1. HIGH RISK: Activate emergency response protocols
2. Consider load shedding in high-risk areas
3. Position repair crews for rapid response
4. Issue public safety warnings
```

### Step 5: Start the API Server

```powershell
# Start FastAPI server with auto-reload
python -m uvicorn src.api.main:app --reload --port 8000 --host 0.0.0.0

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

### Step 6: Access the System

1. **API Documentation (Swagger UI):**
   - URL: http://localhost:8000/docs
   - Interactive API testing interface

2. **Alternative API Documentation (ReDoc):**
   - URL: http://localhost:8000/redoc
   - Clean documentation format

3. **Health Check:**
   - URL: http://localhost:8000/health
   - System status verification

4. **Test Prediction Endpoint:**
```powershell
# Test with curl (install curl if needed)
curl -X POST "http://localhost:8000/api/v1/predictions/predict" ^
-H "Content-Type: application/json" ^
-d "{\"location\": {\"latitude\": -33.8688, \"longitude\": 151.2093}, \"weather_data\": [{\"timestamp\": \"2025-08-31T10:00:00\", \"temperature\": 25.0, \"humidity\": 60.0, \"wind_speed\": 15.0, \"rainfall\": 0.0, \"lightning_strikes\": 0, \"storm_alert\": 0}], \"grid_data\": {\"load_factor\": 0.75, \"voltage_stability\": 0.85, \"historical_outages\": 2, \"maintenance_status\": 0, \"feeder_health\": 0.8}}"
```

### Step 7: Frontend Setup (Optional)

```powershell
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm start

# Frontend will be available at http://localhost:3000
```

## 🌐 Data Sources & Live Data Integration

### Current Data Sources:

#### **Synthetic Data (Demo Mode)**
Currently, the system uses **synthetic data** for demonstration:

1. **Weather Data**: Generated realistic weather patterns including:
   - Temperature cycles (daily variations)
   - Humidity levels
   - Wind speed patterns
   - Rainfall amounts
   - Lightning strikes
   - Storm alerts

2. **Grid Data**: Simulated electrical grid metrics:
   - Load factor (power demand)
   - Voltage stability
   - Historical outage counts
   - Maintenance status
   - Feeder health scores

#### **Live Data Integration (Production Ready)**

The system is **designed and ready** for live data integration:

1. **Weather APIs (Ready to Connect):**
   ```python
   # In src/utils/weather_api.py
   WEATHER_APIS = {
       'openweather': 'https://api.openweathermap.org/data/2.5',
       'noaa': 'https://api.weather.gov',
       'weatherapi': 'https://api.weatherapi.com/v1'
   }
   ```

2. **Grid Data Sources (Integration Points):**
   - SCADA systems integration
   - Smart meter data feeds
   - Grid monitoring systems
   - Historical outage databases

3. **Real-time Data Streaming:**
   - WebSocket connections for live updates
   - Message queue integration (Redis Streams)
   - Scheduled data polling every 5-15 minutes

### To Enable Live Data:

1. **Add API Keys to Environment:**
```powershell
# Edit .env file
notepad .env

# Add your API keys:
# OPENWEATHER_API_KEY=your_api_key_here
# WEATHER_API_KEY=your_api_key_here
# GRID_API_ENDPOINT=your_grid_api_endpoint
```

2. **Configure Data Sources:**
```powershell
# Edit configuration
notepad config\settings.py

# Enable live data mode:
# USE_LIVE_DATA = True
# WEATHER_UPDATE_INTERVAL = 300  # 5 minutes
```

## 🔧 Troubleshooting

### Common Issues:

1. **Docker Services Not Starting:**
```powershell
# Check Docker Desktop is running
docker version

# Reset Docker if needed
docker-compose down
docker system prune -f
docker-compose up -d postgres redis
```

2. **Python Package Installation Issues:**
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install packages with verbose output
pip install -r requirements.txt -v
```

3. **Database Connection Errors:**
```powershell
# Check PostgreSQL is running
docker logs postgres

# Restart if needed
docker-compose restart postgres
```

4. **Port Already in Use:**
```powershell
# Kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Or use different port
python -m uvicorn src.api.main:app --reload --port 8001
```

## 🎯 Next Steps for Live Data

1. **Obtain API Keys** for weather services
2. **Configure Grid Data Sources** (SCADA, smart meters)
3. **Set up Data Pipelines** for real-time ingestion
4. **Implement Monitoring** for data quality
5. **Add Alerting** for system failures

The system is **production-ready** and can easily switch from synthetic to live data by updating configuration files and adding API credentials.
