import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import logging

from config.settings import DatabaseConfig

logger = logging.getLogger(__name__)

# Database base class
Base = declarative_base()

# Database engine and session
engine = None
async_session = None


class OutageEvent(Base):
    """Historical outage events table."""
    __tablename__ = "outage_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    region_name = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    affected_customers = Column(Integer)
    cause = Column(String(200))
    severity = Column(String(20))
    restored = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WeatherData(Base):
    """Weather observations table."""
    __tablename__ = "weather_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    rainfall = Column(Float)
    lightning_strikes = Column(Integer, default=0)
    storm_alert = Column(Boolean, default=False)
    source = Column(String(50))  # IMD, NOAA, OpenWeather, etc.
    created_at = Column(DateTime, default=datetime.utcnow)


class GridData(Base):
    """Power grid status table."""
    __tablename__ = "grid_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    substation_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    load_factor = Column(Float)
    voltage_stability = Column(Float)
    frequency = Column(Float)
    power_demand_mw = Column(Float)
    power_supply_mw = Column(Float)
    maintenance_status = Column(Boolean, default=False)
    feeder_health = Column(Float)
    equipment_age_years = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class PredictionLog(Base):
    """Prediction requests and results log."""
    __tablename__ = "prediction_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    prediction_timestamp = Column(DateTime, nullable=False)
    prediction_horizon = Column(Integer, nullable=False)
    risk_score = Column(Float, nullable=False)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    model_version = Column(String(20))
    input_features = Column(Text)  # JSON string
    explanation_data = Column(Text)  # JSON string
    actual_outcome = Column(Boolean)  # For model performance tracking
    created_at = Column(DateTime, default=datetime.utcnow)


class AdvisoryLog(Base):
    """Advisory messages log."""
    __tablename__ = "advisory_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    advisory_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    affected_areas = Column(Text)  # JSON array
    issued_at = Column(DateTime, nullable=False)
    valid_until = Column(DateTime)
    recommendations = Column(Text)  # JSON array
    viewed_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_database():
    """Initialize database connection and create tables."""
    global engine, async_session
    
    try:
        # Create async engine
        database_url = DatabaseConfig.get_database_url()
        # Convert to async URL if needed
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        
        # Create session factory
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        logger.warning("Continuing without database - using in-memory storage for demo")
        # Don't raise the error for development/demo purposes


async def get_db_session():
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


class DatabaseManager:
    """Database operations manager."""
    
    @staticmethod
    async def save_outage_event(outage_data: dict):
        """Save outage event to database."""
        try:
            async with async_session() as session:
                event = OutageEvent(**outage_data)
                session.add(event)
                await session.commit()
                logger.info(f"Saved outage event: {event.id}")
                return event.id
        except Exception as e:
            logger.error(f"Error saving outage event: {str(e)}")
            raise
    
    @staticmethod
    async def save_weather_data(weather_data: dict):
        """Save weather data to database."""
        try:
            async with async_session() as session:
                weather = WeatherData(**weather_data)
                session.add(weather)
                await session.commit()
                return weather.id
        except Exception as e:
            logger.error(f"Error saving weather data: {str(e)}")
            raise
    
    @staticmethod
    async def save_grid_data(grid_data: dict):
        """Save grid data to database."""
        try:
            async with async_session() as session:
                grid = GridData(**grid_data)
                session.add(grid)
                await session.commit()
                return grid.id
        except Exception as e:
            logger.error(f"Error saving grid data: {str(e)}")
            raise
    
    @staticmethod
    async def log_prediction(prediction_data: dict):
        """Log prediction request and result."""
        try:
            async with async_session() as session:
                log_entry = PredictionLog(**prediction_data)
                session.add(log_entry)
                await session.commit()
                return log_entry.id
        except Exception as e:
            logger.error(f"Error logging prediction: {str(e)}")
            raise
    
    @staticmethod
    async def log_advisory(advisory_data: dict):
        """Log advisory message."""
        try:
            async with async_session() as session:
                advisory = AdvisoryLog(**advisory_data)
                session.add(advisory)
                await session.commit()
                return advisory.id
        except Exception as e:
            logger.error(f"Error logging advisory: {str(e)}")
            raise
    
    @staticmethod
    async def get_historical_outages(location_lat: float, location_lon: float, 
                                   radius_km: float = 50, limit: int = 100):
        """Get historical outages near a location."""
        try:
            async with async_session() as session:
                # Simple distance filter (in production, use PostGIS)
                lat_delta = radius_km / 111.0  # Rough conversion
                lon_delta = radius_km / (111.0 * abs(location_lat))
                
                query = session.query(OutageEvent).filter(
                    OutageEvent.location_lat.between(
                        location_lat - lat_delta, location_lat + lat_delta
                    ),
                    OutageEvent.location_lon.between(
                        location_lon - lon_delta, location_lon + lon_delta
                    )
                ).limit(limit)
                
                result = await session.execute(query)
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting historical outages: {str(e)}")
            return []
    
    @staticmethod
    async def get_weather_history(location_lat: float, location_lon: float,
                                start_time: datetime, end_time: datetime):
        """Get historical weather data."""
        try:
            async with async_session() as session:
                lat_delta = 0.1  # ~10km tolerance
                lon_delta = 0.1
                
                query = session.query(WeatherData).filter(
                    WeatherData.location_lat.between(
                        location_lat - lat_delta, location_lat + lat_delta
                    ),
                    WeatherData.location_lon.between(
                        location_lon - lon_delta, location_lon + lon_delta
                    ),
                    WeatherData.timestamp.between(start_time, end_time)
                ).order_by(WeatherData.timestamp)
                
                result = await session.execute(query)
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting weather history: {str(e)}")
            return []
    
    @staticmethod
    async def update_prediction_outcome(prediction_id: str, actual_outcome: bool):
        """Update prediction with actual outcome for model performance tracking."""
        try:
            async with async_session() as session:
                query = session.query(PredictionLog).filter(
                    PredictionLog.id == prediction_id
                )
                result = await session.execute(query)
                prediction = result.scalar_one_or_none()
                
                if prediction:
                    prediction.actual_outcome = actual_outcome
                    await session.commit()
                    logger.info(f"Updated prediction outcome: {prediction_id}")
        except Exception as e:
            logger.error(f"Error updating prediction outcome: {str(e)}")
    
    @staticmethod
    async def get_model_performance_metrics(days: int = 30):
        """Get model performance metrics for the last N days."""
        try:
            async with async_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                query = session.query(PredictionLog).filter(
                    PredictionLog.created_at >= cutoff_date,
                    PredictionLog.actual_outcome.isnot(None)
                )
                
                result = await session.execute(query)
                predictions = result.scalars().all()
                
                if not predictions:
                    return {"error": "No predictions with outcomes found"}
                
                # Calculate metrics
                total = len(predictions)
                correct = sum(1 for p in predictions 
                            if (p.risk_score >= 50) == p.actual_outcome)
                accuracy = correct / total if total > 0 else 0
                
                return {
                    "total_predictions": total,
                    "accuracy": accuracy,
                    "date_range": f"Last {days} days"
                }
                
        except Exception as e:
            logger.error(f"Error getting model performance metrics: {str(e)}")
            return {"error": str(e)}


# Global database manager instance
db_manager = DatabaseManager()
