import structlog
import logging
import sys
from datetime import datetime
from typing import Any, Dict
import json

from config.settings import settings


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for logging."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def setup_logging():
    """Setup structured logging configuration."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(serializer=json.dumps, cls=CustomJSONEncoder)
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper())
    )
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str):
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggingContext:
    """Context manager for adding context to logs."""
    
    def __init__(self, **context):
        self.context = context
        self.logger = structlog.get_logger()
    
    def __enter__(self):
        self.logger = self.logger.bind(**self.context)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error("Exception occurred", 
                           exc_info=(exc_type, exc_val, exc_tb))


def log_function_call(func):
    """Decorator to log function calls."""
    def wrapper(*args, **kwargs):
        logger = structlog.get_logger(func.__module__)
        logger.info("Function called", 
                   function=func.__name__, 
                   args=len(args), 
                   kwargs=list(kwargs.keys()))
        
        try:
            result = func(*args, **kwargs)
            logger.info("Function completed", function=func.__name__)
            return result
        except Exception as e:
            logger.error("Function failed", 
                        function=func.__name__, 
                        error=str(e))
            raise
    
    return wrapper


def log_api_request(request_data: Dict[str, Any], response_data: Dict[str, Any] = None):
    """Log API request and response."""
    logger = structlog.get_logger("api")
    
    # Log request
    logger.info("API request", 
               endpoint=request_data.get("endpoint"),
               method=request_data.get("method"),
               user_agent=request_data.get("user_agent"),
               ip_address=request_data.get("ip_address"))
    
    # Log response if provided
    if response_data:
        logger.info("API response",
                   endpoint=request_data.get("endpoint"),
                   status_code=response_data.get("status_code"),
                   response_time_ms=response_data.get("response_time_ms"))


def log_model_prediction(prediction_data: Dict[str, Any]):
    """Log model prediction for monitoring."""
    logger = structlog.get_logger("model")
    
    logger.info("Model prediction",
               model_version=prediction_data.get("model_version"),
               risk_score=prediction_data.get("risk_score"),
               confidence=prediction_data.get("confidence"),
               features=prediction_data.get("feature_count"),
               processing_time_ms=prediction_data.get("processing_time_ms"))


def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log error with context."""
    logger = structlog.get_logger("error")
    
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if context:
        error_data.update(context)
    
    logger.error("Application error", **error_data)


def log_performance_metric(metric_name: str, value: float, unit: str = "", tags: Dict[str, str] = None):
    """Log performance metric."""
    logger = structlog.get_logger("metrics")
    
    metric_data = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if tags:
        metric_data["tags"] = tags
    
    logger.info("Performance metric", **metric_data)
