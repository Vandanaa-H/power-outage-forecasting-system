from prometheus_client import Counter, Histogram, Gauge, generate_latest
from typing import Dict, Any
import time
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method', 'status'])
request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['endpoint'])
prediction_count = Counter('predictions_total', 'Total predictions made', ['model_version', 'risk_level'])
prediction_accuracy = Gauge('prediction_accuracy', 'Model prediction accuracy')
cache_hits = Counter('cache_hits_total', 'Total cache hits')
cache_misses = Counter('cache_misses_total', 'Total cache misses')
active_connections = Gauge('active_db_connections', 'Active database connections')
model_inference_time = Histogram('model_inference_seconds', 'Model inference time')


async def track_api_request(endpoint: str, method: str, status_code: int, duration: float):
    """Track API request metrics."""
    try:
        request_count.labels(endpoint=endpoint, method=method, status=str(status_code)).inc()
        request_duration.labels(endpoint=endpoint).observe(duration)
    except Exception as e:
        logger.error(f"Error tracking API request metrics: {str(e)}")


async def track_prediction_request(request_data: Dict[str, Any]):
    """Track prediction request metrics."""
    try:
        model_version = request_data.get('model_version', 'unknown')
        risk_score = request_data.get('risk_score', 0)
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = 'critical'
        elif risk_score >= 60:
            risk_level = 'high'
        elif risk_score >= 30:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        prediction_count.labels(model_version=model_version, risk_level=risk_level).inc()
        
    except Exception as e:
        logger.error(f"Error tracking prediction metrics: {str(e)}")


async def track_model_inference(inference_time: float):
    """Track model inference time."""
    try:
        model_inference_time.observe(inference_time)
    except Exception as e:
        logger.error(f"Error tracking inference time: {str(e)}")


async def track_cache_operation(operation: str):
    """Track cache hit/miss."""
    try:
        if operation == 'hit':
            cache_hits.inc()
        elif operation == 'miss':
            cache_misses.inc()
    except Exception as e:
        logger.error(f"Error tracking cache metrics: {str(e)}")


def get_metrics():
    """Get all metrics in Prometheus format."""
    return generate_latest()


class PerformanceMonitor:
    """Performance monitoring and alerting."""
    
    def __init__(self):
        self.alert_thresholds = {
            'response_time_ms': 1000,
            'error_rate_percent': 5.0,
            'memory_usage_percent': 80.0,
            'cpu_usage_percent': 70.0
        }
        self.alerts = []
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        try:
            health_status = {
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'healthy',
                'checks': {}
            }
            
            # Check API response time
            avg_response_time = await self._get_average_response_time()
            health_status['checks']['api_response_time'] = {
                'value': avg_response_time,
                'status': 'healthy' if avg_response_time < self.alert_thresholds['response_time_ms'] else 'warning',
                'threshold': self.alert_thresholds['response_time_ms']
            }
            
            # Check error rate
            error_rate = await self._get_error_rate()
            health_status['checks']['error_rate'] = {
                'value': error_rate,
                'status': 'healthy' if error_rate < self.alert_thresholds['error_rate_percent'] else 'warning',
                'threshold': self.alert_thresholds['error_rate_percent']
            }
            
            # Check model performance
            model_accuracy = await self._get_model_accuracy()
            health_status['checks']['model_accuracy'] = {
                'value': model_accuracy,
                'status': 'healthy' if model_accuracy > 0.7 else 'warning',
                'threshold': 0.7
            }
            
            # Determine overall status
            warning_checks = [check for check in health_status['checks'].values() 
                            if check['status'] == 'warning']
            if warning_checks:
                health_status['status'] = 'warning'
                health_status['warnings'] = len(warning_checks)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    async def _get_average_response_time(self) -> float:
        """Get average API response time."""
        # This would calculate from actual metrics
        # For now, return mock value
        return 250.0  # milliseconds
    
    async def _get_error_rate(self) -> float:
        """Get API error rate percentage."""
        # This would calculate from actual metrics
        # For now, return mock value
        return 2.3  # percent
    
    async def _get_model_accuracy(self) -> float:
        """Get model accuracy from recent predictions."""
        # This would query actual prediction outcomes
        # For now, return mock value
        return 0.85  # 85% accuracy
    
    async def generate_alert(self, alert_type: str, message: str, severity: str = 'warning'):
        """Generate system alert."""
        try:
            alert = {
                'id': f"alert_{int(time.time())}",
                'type': alert_type,
                'message': message,
                'severity': severity,
                'timestamp': datetime.utcnow().isoformat(),
                'acknowledged': False
            }
            
            self.alerts.append(alert)
            logger.warning(f"Generated alert: {alert_type} - {message}")
            
            # In production, this would send notifications
            # (email, Slack, SMS, etc.)
            
            return alert
            
        except Exception as e:
            logger.error(f"Error generating alert: {str(e)}")
    
    async def get_active_alerts(self) -> list:
        """Get active (unacknowledged) alerts."""
        return [alert for alert in self.alerts if not alert['acknowledged']]
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        try:
            for alert in self.alerts:
                if alert['id'] == alert_id:
                    alert['acknowledged'] = True
                    alert['acknowledged_at'] = datetime.utcnow().isoformat()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error acknowledging alert: {str(e)}")
            return False


# Global performance monitor
performance_monitor = PerformanceMonitor()


class MetricsCollector:
    """Collect and aggregate custom metrics."""
    
    def __init__(self):
        self.custom_metrics = {}
    
    async def collect_business_metrics(self) -> Dict[str, Any]:
        """Collect business-specific metrics."""
        try:
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'predictions_last_hour': await self._count_recent_predictions(hours=1),
                'predictions_last_day': await self._count_recent_predictions(hours=24),
                'high_risk_predictions': await self._count_high_risk_predictions(),
                'average_risk_score': await self._get_average_risk_score(),
                'top_affected_regions': await self._get_top_affected_regions(),
                'model_performance': await self._get_model_performance_summary()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting business metrics: {str(e)}")
            return {'error': str(e)}
    
    async def _count_recent_predictions(self, hours: int) -> int:
        """Count predictions in the last N hours."""
        # This would query the database
        # For now, return mock value
        return 1250 if hours == 1 else 28500
    
    async def _count_high_risk_predictions(self) -> int:
        """Count high-risk predictions (>60% risk)."""
        # This would query the database
        # For now, return mock value
        return 125
    
    async def _get_average_risk_score(self) -> float:
        """Get average risk score from recent predictions."""
        # This would query the database
        # For now, return mock value
        return 42.7
    
    async def _get_top_affected_regions(self) -> list:
        """Get regions with highest risk scores."""
        # This would query the database
        # For now, return mock data
        return [
            {'region': 'Bengaluru Urban', 'avg_risk': 72.5, 'prediction_count': 145},
            {'region': 'Mumbai Suburban', 'avg_risk': 68.3, 'prediction_count': 132},
            {'region': 'Chennai', 'avg_risk': 45.8, 'prediction_count': 98}
        ]
    
    async def _get_model_performance_summary(self) -> Dict[str, Any]:
        """Get model performance summary."""
        # This would analyze actual predictions vs outcomes
        # For now, return mock data
        return {
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.78,
            'f1_score': 0.80,
            'last_updated': datetime.utcnow().isoformat()
        }


# Global metrics collector
metrics_collector = MetricsCollector()
