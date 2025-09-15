import React from 'react';
import { motion } from 'framer-motion';

function AlertsList({ alerts = [] }) {
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const mockAlerts = [
    {
      id: 1,
      title: 'High Wind Warning',
      description: 'Strong winds expected in coastal areas',
      severity: 'High',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      location: 'Mangalore'
    },
    {
      id: 2,
      title: 'Grid Maintenance',
      description: 'Scheduled maintenance in Electronics City',
      severity: 'Medium',
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
      location: 'Bangalore'
    },
    {
      id: 3,
      title: 'Load Increase',
      description: 'Higher than normal power demand detected',
      severity: 'Low',
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
      location: 'Mysore'
    }
  ];

  const alertsToShow = alerts.length > 0 ? alerts : mockAlerts;

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
      case 'critical':
        return 'bg-red-100 text-red-800 border-l-red-500';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-l-yellow-500';
      case 'low':
        return 'bg-green-100 text-green-800 border-l-green-500';
      default:
        return 'bg-blue-100 text-blue-800 border-l-blue-500';
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInHours = Math.floor((now - time) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours === 1) return '1 hour ago';
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays === 1) return '1 day ago';
    return `${diffInDays} days ago`;
  };

  if (alertsToShow.length === 0) {
    return (
      <div className="text-center py-12 text-neutral-500">
        <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-neutral-700">No Active Alerts</h3>
        <p className="text-sm text-neutral-500">All systems operating normally</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {alertsToShow.slice(0, 5).map((alert, index) => (
        <motion.div
          key={alert.id || index}
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: index * 0.1 }}
          className={`p-4 rounded-lg border-l-4 ${getSeverityColor(alert.severity)}`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="font-medium text-sm">{alert.title}</h4>
              <p className="text-xs text-neutral-600 mt-1">{alert.description}</p>
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-neutral-500">{alert.location}</span>
                <span className="text-xs text-neutral-500">{formatTimeAgo(alert.timestamp)}</span>
              </div>
            </div>
            <span className={`ml-3 px-2 py-1 rounded-full text-xs font-medium ${
              getSeverityColor(alert.severity).replace('border-l-', 'bg-').replace('bg-', '').includes('red') ? 'bg-red-100 text-red-800' :
              getSeverityColor(alert.severity).replace('border-l-', 'bg-').replace('bg-', '').includes('yellow') ? 'bg-yellow-100 text-yellow-800' :
              getSeverityColor(alert.severity).replace('border-l-', 'bg-').replace('bg-', '').includes('green') ? 'bg-green-100 text-green-800' :
              'bg-blue-100 text-blue-800'
            }`}>
              {alert.severity}
            </span>
          </div>
        </motion.div>
      ))}
      
      {alertsToShow.length > 5 && (
        <div className="text-center pt-2">
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            View all alerts ({alertsToShow.length})
          </button>
        </div>
      )}
    </div>
  );
}

export default AlertsList;
