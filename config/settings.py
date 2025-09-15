import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application
    app_name: str = "24-Hour Power Outage Forecasting System"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database (SQLite for demo - no Docker required)
    database_url: str = "sqlite+aiosqlite:///./power_outage_db.sqlite"
    timescale_url: Optional[str] = None
    redis_url: str = "redis://localhost:6379/0"
    
    # Weather APIs (demo mode - no keys required)
    openweather_api_key: str = "demo_key"
    noaa_api_key: Optional[str] = None
    imd_api_key: Optional[str] = None
    
    # Security (demo defaults)
    secret_key: str = "demo-secret-key-for-development-only-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Model Configuration
    model_update_interval: int = 3600  # seconds
    prediction_horizon: int = 24  # hours
    confidence_threshold: float = 0.7
    
    # Geographic Configuration
    default_latitude: float = 20.5937
    default_longitude: float = 78.9629
    map_zoom_level: int = 6
    
    # External Services
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    email_user: Optional[str] = None
    email_password: Optional[str] = None
    
    # Cloud Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket: Optional[str] = None
    
    # Monitoring
    prometheus_port: int = 9090
    grafana_port: int = 3001
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            raise ValueError('Database URL is required')
        return v
        return v


# Global settings instance
settings = Settings()


# Database configuration
class DatabaseConfig:
    """Database connection configuration."""
    
    @staticmethod
    def get_database_url():
        return settings.database_url
    
    @staticmethod
    def get_timescale_url():
        return settings.timescale_url or settings.database_url


# Model configuration
class ModelConfig:
    """ML Model configuration."""
    
    # Feature columns
    WEATHER_FEATURES = [
        'temperature', 'humidity', 'wind_speed', 'rainfall',
        'lightning_strikes', 'storm_alert'
    ]
    
    GRID_FEATURES = [
        'load_factor', 'voltage_stability', 'historical_outages',
        'maintenance_status', 'feeder_health'
    ]
    
    TEMPORAL_FEATURES = [
        'hour_of_day', 'day_of_week', 'month', 'season'
    ]
    
    # Model parameters
    LSTM_SEQUENCE_LENGTH = 24  # 24-hour sequence
    BATCH_SIZE = 32
    EPOCHS = 100
    LEARNING_RATE = 0.001
    
    # XGBoost parameters
    XGBOOST_PARAMS = {
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 100,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42
    }


# API configuration
class APIConfig:
    """API configuration."""
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    
    # Response configuration
    MAX_PREDICTION_POINTS = 1000
    DEFAULT_CONFIDENCE_LEVEL = 0.95
    
    # Cache configuration
    CACHE_TTL = 300  # 5 minutes
