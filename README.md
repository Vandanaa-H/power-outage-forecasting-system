# 24-Hour Power Outage Forecasting System

## Overview
An AI-powered early warning system that predicts power outages 24 hours in advance using weather data and power grid data. This system transforms outage handling from reactive to proactive, enabling utilities and citizens to prepare before outages occur.

## Features
- ✅ Risk Score + Confidence intervals instead of binary classification
- ✅ Explainability using SHAP for feature attribution
- ✅ Location Pinpointing on interactive maps
- ✅ Real-time Dashboard for utilities and public
- ✅ Natural Language Advisories for citizen alerts
- ✅ What-If Scenario Simulator
- ✅ RESTful API for integration

## Project Structure
```
├── src/                    # Source code
│   ├── api/               # FastAPI application
│   ├── models/            # ML models and training
│   ├── data/              # Data processing modules
│   └── utils/             # Utility functions
├── frontend/              # React.js dashboard
├── data/                  # Data storage
│   ├── raw/              # Raw data files
│   └── processed/        # Processed datasets
├── notebooks/             # Jupyter notebooks for EDA
├── config/               # Configuration files
├── tests/                # Test files
├── docker/               # Docker configurations
└── docs/                 # Documentation
```

## Tech Stack
- **Backend**: Python, FastAPI, PostgreSQL/TimescaleDB
- **ML/AI**: TensorFlow, XGBoost, SHAP, Scikit-learn
- **Frontend**: React.js, TailwindCSS, Leaflet.js
- **Data**: Pandas, GeoPandas, Apache Airflow
- **Deployment**: Docker, Kubernetes, AWS/GCP

## Quick Start

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# PostgreSQL with TimescaleDB extension
docker run -d --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=password timescale/timescaledb:latest-pg14
```

### 3. Configuration
```bash
# Copy environment template
cp config/env.template .env
# Edit .env with your API keys and database credentials
```

### 4. Run the Application
```bash
# Start the API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Start the frontend (in another terminal)
cd frontend
npm install
npm start
```

## API Endpoints
- `POST /predict` - Get outage risk predictions
- `GET /heatmap` - Get GeoJSON risk map data
- `GET /advisories` - Get plain text advisories
- `POST /what-if` - Run scenario simulations
- `GET /health` - Health check endpoint

## Data Sources
- **Weather**: IMD, NOAA, OpenWeather API
- **Grid**: Historical outage logs, SCADA data
- **Geospatial**: District shapefiles (GeoJSON)
- **Alerts**: IMD storm warnings, lightning alerts

## Development

### Running Tests
```bash
pytest tests/ -v --cov=src
```

### Code Quality
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License
MIT License - see LICENSE file for details.
