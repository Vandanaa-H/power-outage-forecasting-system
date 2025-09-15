import React from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';

function RecentPredictions() {
  const { data: predictions, isLoading } = useQuery(
    ['predictions', 'recent'],
    () => apiService.getRecentPredictions(),
    {
      refetchInterval: 60000, // Refresh every minute
    }
  );

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const mockPredictions = [
    {
      id: 1,
      location: 'Bangalore Urban - Electronic City',
      prediction_time: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 min ago
      risk_level: 'High',
      outage_probability: 0.78,
      confidence: 0.92,
      contributing_factors: ['Thunderstorm Warning', 'High Load']
    },
    {
      id: 2,
      location: 'Mysore - City Center',
      prediction_time: new Date(Date.now() - 45 * 60 * 1000).toISOString(), // 45 min ago
      risk_level: 'Medium',
      outage_probability: 0.45,
      confidence: 0.88,
      contributing_factors: ['Maintenance Scheduled', 'Normal Weather']
    },
    {
      id: 3,
      location: 'Mangalore - Port Area',
      prediction_time: new Date(Date.now() - 60 * 60 * 1000).toISOString(), // 1 hour ago
      risk_level: 'Low',
      outage_probability: 0.15,
      confidence: 0.95,
      contributing_factors: ['Stable Weather', 'Low Load']
    },
    {
      id: 4,
      location: 'Hubli - Industrial Zone',
      prediction_time: new Date(Date.now() - 75 * 60 * 1000).toISOString(), // 1.25 hours ago
      risk_level: 'Medium',
      outage_probability: 0.52,
      confidence: 0.89,
      contributing_factors: ['High Temperature', 'Grid Stress']
    },
    {
      id: 5,
      location: 'Belgaum - Residential',
      prediction_time: new Date(Date.now() - 90 * 60 * 1000).toISOString(), // 1.5 hours ago
      risk_level: 'Low',
      outage_probability: 0.22,
      confidence: 0.91,
      contributing_factors: ['Normal Conditions']
    }
  ];

  const predictionsToShow = predictions || mockPredictions;

  const getRiskColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'high':
      case 'critical':
        return 'text-red-600 bg-red-50';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50';
      case 'low':
        return 'text-green-600 bg-green-50';
      default:
        return 'text-neutral-600 bg-neutral-50';
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now - time) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-neutral-200 rounded w-1/3"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-neutral-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      variants={itemVariants}
      className="p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-neutral-900">Recent Predictions</h3>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View All
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="border-b border-neutral-200">
              <th className="text-left py-3 px-4 font-medium text-neutral-700">Location</th>
              <th className="text-left py-3 px-4 font-medium text-neutral-700">Risk Level</th>
              <th className="text-left py-3 px-4 font-medium text-neutral-700">Probability</th>
              <th className="text-left py-3 px-4 font-medium text-neutral-700">Confidence</th>
              <th className="text-left py-3 px-4 font-medium text-neutral-700">Time</th>
              <th className="text-left py-3 px-4 font-medium text-neutral-700">Factors</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {predictionsToShow.slice(0, 10).map((prediction, index) => (
              <motion.tr
                key={prediction.id}
                variants={itemVariants}
                initial="hidden"
                animate="visible"
                transition={{ delay: index * 0.05 }}
                className="hover:bg-neutral-50"
              >
                <td className="py-3 px-4">
                  <div>
                    <p className="font-medium text-neutral-900 text-sm">{prediction.location}</p>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(prediction.risk_level)}`}>
                    {prediction.risk_level}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-neutral-900">
                      {(prediction.outage_probability * 100).toFixed(1)}%
                    </span>
                    <div className="w-16 bg-neutral-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          prediction.outage_probability >= 0.7 ? 'bg-red-500' :
                          prediction.outage_probability >= 0.4 ? 'bg-yellow-500' :
                          'bg-green-500'
                        }`}
                        style={{ width: `${prediction.outage_probability * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className="text-sm text-neutral-700">
                    {(prediction.confidence * 100).toFixed(0)}%
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span className="text-sm text-neutral-600">
                    {formatTimeAgo(prediction.prediction_time)}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <div className="flex flex-wrap gap-1">
                    {prediction.contributing_factors?.slice(0, 2).map((factor, idx) => (
                      <span 
                        key={idx}
                        className="px-1 py-0.5 bg-neutral-100 text-neutral-600 text-xs rounded"
                      >
                        {factor}
                      </span>
                    ))}
                    {prediction.contributing_factors?.length > 2 && (
                      <span className="px-1 py-0.5 bg-neutral-100 text-neutral-600 text-xs rounded">
                        +{prediction.contributing_factors.length - 2} more
                      </span>
                    )}
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {predictionsToShow.length === 0 && (
        <div className="text-center py-16 text-neutral-500">
          <div className="w-20 h-20 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
            <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-neutral-700 mb-2">No predictions yet</h3>
          <p className="text-base text-neutral-500">Run your first prediction to see results here</p>
        </div>
      )}
    </motion.div>
  );
}

export default RecentPredictions;
