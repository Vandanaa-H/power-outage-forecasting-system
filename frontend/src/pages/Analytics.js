import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import useStore from '../store/useStore';
import { apiService } from '../services/api';

function Analytics() {
  const [dateRange, setDateRange] = useState('7d');
  const [metricType, setMetricType] = useState('accuracy');

  const { data: analyticsData, isLoading } = useQuery(
    ['analytics', dateRange, metricType],
    () => apiService.getAnalytics({ period: dateRange, metric: metricType }),
    {
      refetchInterval: 60000, // Refresh every minute
    }
  );

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const kpiData = [
    { label: 'Model Accuracy', value: '95.6%', change: '+2.1%', trend: 'up' },
    { label: 'Predictions Made', value: '1,247', change: '+156', trend: 'up' },
    { label: 'Average Response Time', value: '1.2s', change: '-0.3s', trend: 'down' },
    { label: 'System Uptime', value: '99.9%', change: '0%', trend: 'stable' },
    { label: 'False Positives', value: '2.1%', change: '-0.5%', trend: 'down' },
    { label: 'Coverage Areas', value: '30', change: '+2', trend: 'up' }
  ];

  const recentPerformance = [
    { date: '2024-01-15', accuracy: 96.2, predictions: 45, alerts: 3 },
    { date: '2024-01-14', accuracy: 94.8, predictions: 52, alerts: 5 },
    { date: '2024-01-13', accuracy: 95.1, predictions: 38, alerts: 2 },
    { date: '2024-01-12', accuracy: 97.3, predictions: 41, alerts: 4 },
    { date: '2024-01-11', accuracy: 93.9, predictions: 48, alerts: 6 }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Analytics</h1>
          <p className="text-neutral-600 mt-1">
            System performance metrics and prediction accuracy analysis
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <button className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors">
            Export Report
          </button>
        </div>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {kpiData.map((kpi, index) => (
          <motion.div
            key={kpi.label}
            variants={itemVariants}
            className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-600">{kpi.label}</p>
                <p className="text-2xl font-bold text-neutral-900 mt-1">{kpi.value}</p>
              </div>
              <div className="text-right">
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  kpi.trend === 'up' ? 'bg-green-100 text-green-800' :
                  kpi.trend === 'down' && kpi.label.includes('Response Time') || kpi.label.includes('False Positives') ? 'bg-green-100 text-green-800' :
                  kpi.trend === 'down' ? 'bg-red-100 text-red-800' :
                  'bg-neutral-100 text-neutral-800'
                }`}>
                  {kpi.change}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Model Accuracy Trend</h3>
          <div className="h-64 flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-blue-500 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-lg font-semibold text-neutral-700">Model Accuracy Analytics</p>
              <p className="text-base text-neutral-500">Real-time performance tracking and trends</p>
            </div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Prediction Volume</h3>
          <div className="h-64 flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-green-500 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <p className="text-lg font-semibold text-neutral-700">Prediction Volume Metrics</p>
              <p className="text-base text-neutral-500">Daily prediction counts and system load</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Performance Table */}
      <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Recent Performance</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-200">
            <thead className="bg-neutral-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Accuracy
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Predictions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Alerts Generated
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-neutral-200">
              {recentPerformance.map((day, index) => (
                <tr key={day.date} className="hover:bg-neutral-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-neutral-900">
                    {new Date(day.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                      day.accuracy >= 95 ? 'bg-green-100 text-green-800' :
                      day.accuracy >= 90 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {day.accuracy}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">
                    {day.predictions}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">
                    {day.alerts}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                      day.accuracy >= 95 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {day.accuracy >= 95 ? 'Excellent' : 'Good'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Feature Importance */}
      <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Model Feature Importance (SHAP)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-neutral-700 mb-3">Top Contributing Features</h4>
            <div className="space-y-3">
              {[
                { feature: 'Weather Conditions', importance: 0.35, color: 'bg-blue-500' },
                { feature: 'Historical Patterns', importance: 0.28, color: 'bg-green-500' },
                { feature: 'Grid Load', importance: 0.18, color: 'bg-yellow-500' },
                { feature: 'Maintenance Schedule', importance: 0.12, color: 'bg-red-500' },
                { feature: 'Seasonal Factors', importance: 0.07, color: 'bg-purple-500' }
              ].map((item, index) => (
                <div key={item.feature} className="flex items-center">
                  <div className="w-24 text-xs text-neutral-600">{item.feature}</div>
                  <div className="flex-1 mx-3">
                    <div className="bg-neutral-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${item.color}`}
                        style={{ width: `${item.importance * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="text-xs text-neutral-600 w-12 text-right">
                    {(item.importance * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="flex items-center justify-center text-neutral-600">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-purple-500 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <p className="text-lg font-semibold text-neutral-700">AI Model Insights</p>
              <p className="text-base text-neutral-500">Feature importance and decision explanations</p>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default Analytics;
