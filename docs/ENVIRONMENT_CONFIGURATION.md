# Environment Configuration Guide

This document describes how to configure the Karnataka Power Outage Forecasting System for different environments.

## Overview

The application uses environment variables to configure both backend and frontend components. This allows for easy deployment across development, staging, and production environments without code changes.

## Directory Structure

```
/
├── .env                           # Backend environment variables
├── .env.template                  # Backend template with defaults
├── frontend/
│   ├── .env.template             # Frontend template
│   ├── .env.local               # Frontend local development (git-ignored)
│   ├── .env.development         # Frontend development environment
│   ├── .env.production          # Frontend production environment
│   └── src/config/config.js     # Centralized configuration utility
```

## Backend Environment Variables

### Critical Configuration

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG_MODE=false

# Weather API Keys (Required for real-time data)
OPENWEATHER_API_KEY=your_openweather_api_key_here
WEATHERAPI_KEY=your_weatherapi_key_here

# Database Configuration
DATABASE_URL=sqlite:///./karnataka_outages.db
# OR for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/karnataka_outages
```

### Optional Configuration

```bash
# Model Configuration
MODEL_PATH=models/karnataka_outage_model.joblib
DEFAULT_PREDICTION_HOURS=24
MAX_PREDICTION_HOURS=48

# Monitoring
ENABLE_PERFORMANCE_MONITORING=true
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Notifications (Optional)
ENABLE_EMAIL_ALERTS=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

## Frontend Environment Variables

### Critical Configuration

```bash
# API Connection
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000

# Application Info
REACT_APP_NAME=Karnataka Power Outage Forecasting System
REACT_APP_VERSION=1.0.0
```

### Map Configuration

```bash
# Default map center (Karnataka)
REACT_APP_DEFAULT_LATITUDE=15.3173
REACT_APP_DEFAULT_LONGITUDE=75.7139
REACT_APP_MAP_ZOOM_LEVEL=7
REACT_APP_DEFAULT_CITY=Bengaluru

# Map services (optional)
REACT_APP_MAPBOX_TOKEN=your_mapbox_token_here
REACT_APP_GOOGLE_MAPS_KEY=your_google_maps_key_here
```

### Feature Flags

```bash
# Enable/disable features
REACT_APP_ENABLE_HEATMAP=true
REACT_APP_ENABLE_WHAT_IF=true
REACT_APP_ENABLE_METRICS=true
REACT_APP_ENABLE_ADVISORIES=true
REACT_APP_ENABLE_BATCH_PREDICTIONS=true
```

### Development Settings

```bash
# Development features
REACT_APP_DEBUG_MODE=true
REACT_APP_ENABLE_CONSOLE_LOGS=true
REACT_APP_ENABLE_LOCATION_SERVICES=true

# Update intervals (milliseconds)
REACT_APP_REFRESH_INTERVAL=300000        # 5 minutes
REACT_APP_WEATHER_UPDATE_INTERVAL=900000 # 15 minutes
```

## Environment Setup Instructions

### 1. Backend Setup

```bash
# 1. Copy the template
cp .env.template .env

# 2. Edit the .env file with your values
nano .env

# 3. Set critical variables
OPENWEATHER_API_KEY=your_actual_api_key
DATABASE_URL=your_database_connection_string
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# 1. Copy the template for local development
cp .env.template .env.local

# 2. Edit with your local API URL
echo "REACT_APP_API_URL=http://localhost:8000" >> .env.local

# 3. Enable debug mode for development
echo "REACT_APP_DEBUG_MODE=true" >> .env.local
```

### 3. Production Setup

For production deployment, create environment-specific files:

```bash
# Frontend production environment
# frontend/.env.production
REACT_APP_API_URL=https://your-production-api.com
REACT_APP_DEBUG_MODE=false
REACT_APP_ENABLE_CONSOLE_LOGS=false
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_GOOGLE_ANALYTICS_ID=your_ga_id
```

## Configuration Validation

The application includes automatic configuration validation:

### Backend Validation
- Validates critical API keys are present
- Checks database connectivity
- Verifies model files exist

### Frontend Validation
- Validates API URL accessibility
- Checks required environment variables
- Warns about missing optional configurations
- Logs configuration summary in development

## Environment-Specific Configurations

### Development Environment

```bash
# Backend (.env)
DEBUG_MODE=true
LOG_LEVEL=DEBUG
ENABLE_PERFORMANCE_MONITORING=true

# Frontend (.env.local)
REACT_APP_DEBUG_MODE=true
REACT_APP_ENABLE_CONSOLE_LOGS=true
REACT_APP_API_URL=http://localhost:8000
```

### Staging Environment

```bash
# Backend
DEBUG_MODE=false
LOG_LEVEL=INFO
ENABLE_PERFORMANCE_MONITORING=true

# Frontend (.env.staging)
REACT_APP_DEBUG_MODE=false
REACT_APP_ENABLE_CONSOLE_LOGS=false
REACT_APP_API_URL=https://staging-api.yourdomain.com
```

### Production Environment

```bash
# Backend
DEBUG_MODE=false
LOG_LEVEL=WARNING
ENABLE_EMAIL_ALERTS=true
ENABLE_PERFORMANCE_MONITORING=true

# Frontend (.env.production)
REACT_APP_DEBUG_MODE=false
REACT_APP_ENABLE_CONSOLE_LOGS=false
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_API_URL=https://api.yourdomain.com
```

## Common Issues and Solutions

### 1. API Connection Issues

**Problem**: Frontend cannot connect to backend
**Solution**: Check `REACT_APP_API_URL` matches backend `API_HOST:API_PORT`

```bash
# Backend is running on localhost:8000
# Frontend should have:
REACT_APP_API_URL=http://localhost:8000
```

### 2. Weather Data Not Loading

**Problem**: Weather API calls failing
**Solution**: Verify `OPENWEATHER_API_KEY` is valid

```bash
# Test API key manually:
curl "https://api.openweathermap.org/data/2.5/weather?q=Bengaluru&appid=YOUR_API_KEY"
```

### 3. Map Not Displaying

**Problem**: Map component not rendering
**Solution**: Check map service configuration

```bash
# For Mapbox:
REACT_APP_MAPBOX_TOKEN=your_mapbox_token

# Or use free alternatives in development:
REACT_APP_MAP_STYLE=openstreetmap
```

### 4. Features Not Available

**Problem**: Certain features like metrics page not showing
**Solution**: Check feature flags

```bash
REACT_APP_ENABLE_METRICS=true
REACT_APP_ENABLE_HEATMAP=true
```

## Security Considerations

### Environment Variable Security

1. **Never commit `.env` files**: Use `.env.template` for examples
2. **Use different keys per environment**: Don't share production keys
3. **Rotate API keys regularly**: Update keys in all environments
4. **Limit API key permissions**: Only grant necessary permissions

### Frontend Security Notes

- Frontend environment variables are exposed to users
- Never put sensitive data in `REACT_APP_*` variables
- Use backend proxy for sensitive API calls
- Validate all user inputs

## Deployment Commands

### Development

```bash
# Backend
export $(cat .env | xargs) && python start_server.py

# Frontend
cd frontend && npm start
```

### Production

```bash
# Backend with production settings
export NODE_ENV=production
export $(cat .env | xargs) && python start_server.py

# Frontend build with production environment
cd frontend && npm run build
```

### Docker Deployment

```dockerfile
# Use environment files with Docker
docker-compose --env-file .env up -d
```

## Monitoring Configuration

Monitor your environment variables:

```bash
# Check loaded environment
python -c "
import os
from config.settings import settings
print(f'API Host: {settings.api_host}')
print(f'Debug Mode: {settings.debug}')
print(f'OpenWeather Key Set: {bool(settings.openweather_api_key)}')
"
```

## Environment Migration

When moving between environments:

1. **Export current configuration**:
   ```bash
   env | grep -E "(REACT_APP_|OPENWEATHER_|DATABASE_)" > current_config.txt
   ```

2. **Update URLs and keys** for new environment

3. **Test configuration**:
   ```bash
   npm run test:config  # Custom script to validate config
   ```

4. **Deploy and verify** all features work

## Support

If you encounter configuration issues:

1. Check this documentation
2. Verify all required variables are set
3. Test API connectivity manually
4. Check application logs for validation errors
5. Contact the development team with specific error messages

---

For additional help, see:
- [API Documentation](../README.md#api-endpoints)
- [Deployment Guide](../RUN_INSTRUCTIONS.md)
- [Troubleshooting Guide](../docs/troubleshooting.md)