import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import useStore from '../store/useStore';
import { apiService } from '../services/api';
import { 
  ModelAccuracyChart, 
  PredictionVolumeChart, 
  RiskDistributionChart, 
  ResponseTimeChart,
  PredictionTrendsChart
} from '../components/charts/AnalyticsCharts';
import { 
  FiTrendingUp, 
  FiClock, 
  FiActivity, 
  FiTarget,
  FiBarChart,
  FiPieChart,
  FiDownload,
  FiRefreshCw
} from 'react-icons/fi';

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
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mb-4 mx-auto shadow"></div>
          <div className="text-xl font-semibold text-gray-700 mb-2">Loading Analytics...</div>
          <div className="text-sm text-gray-500">Fetching performance data</div>
        </motion.div>
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
      <motion.div variants={itemVariants} className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
          <p className="text-gray-600">
            System performance metrics and prediction accuracy analysis
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[150px]"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <button className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors flex items-center space-x-2 text-sm">
            <FiRefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 text-sm">
            <FiDownload className="w-4 h-4" />
            <span>Export Report</span>
          </button>
        </div>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {kpiData.map((kpi, index) => (
          <motion.div
            key={kpi.label}
            variants={itemVariants}
            className="relative group"
            whileHover={{ scale: 1.02, y: -4 }}
            transition={{ duration: 0.3 }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-600 rounded-lg transform rotate-1 group-hover:rotate-2 transition-transform duration-300"></div>
            <div className="relative bg-white rounded-lg shadow border border-gray-100 p-6 group-hover:shadow-md transition-all duration-300">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">{kpi.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
                </div>
                <div className="text-right">
                  <div className={`inline-flex items-center px-3 py-1.5 rounded-md text-xs font-medium shadow ${
                    kpi.trend === 'up' ? 'bg-green-100 text-green-800' :
                    kpi.trend === 'down' && (kpi.label.includes('Response Time') || kpi.label.includes('False Positives')) ? 'bg-green-100 text-green-800' :
                    kpi.trend === 'down' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    <span className="text-sm mr-1">
                      {kpi.trend === 'up' ? '↗' : kpi.trend === 'down' ? '↘' : '→'}
                    </span>
                    {kpi.change}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FiTrendingUp className="w-5 h-5 text-blue-500 mr-2" />
              Model Accuracy Trend
            </h3>
            <div className="flex items-center space-x-2 text-sm text-gray-600 bg-blue-50 px-3 py-1.5 rounded-md">
              <FiTarget className="w-4 h-4" />
              <span className="font-medium">Target: 95%</span>
            </div>
          </div>
          <div className="h-96">
            <ModelAccuracyChart />
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FiActivity className="w-5 h-5 text-green-500 mr-2" />
              Prediction Volume
            </h3>
            <div className="flex items-center space-x-2 text-sm text-gray-600 bg-green-50 px-3 py-1.5 rounded-md">
              <FiBarChart className="w-4 h-4" />
              <span className="font-medium">24h View</span>
            </div>
          </div>
          <div className="h-80">
            <PredictionVolumeChart />
          </div>
        </motion.div>
      </div>

      {/* Secondary Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FiPieChart className="w-5 h-5 text-purple-500 mr-2" />
              Risk Distribution
            </h3>
            <div className="text-sm text-gray-600 bg-purple-50 px-3 py-1.5 rounded-md font-medium">
              Current Period
            </div>
          </div>
          <div className="h-80">
            <RiskDistributionChart />
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FiClock className="w-5 h-5 text-orange-500 mr-2" />
              Response Time Analysis
            </h3>
            <div className="text-sm text-gray-600 bg-orange-50 px-3 py-1.5 rounded-md font-medium">
              Last 7 Days
            </div>
          </div>
          <div className="h-80">
            <ResponseTimeChart />
          </div>
        </motion.div>
      </div>

      {/* Full-width Chart */}
      <motion.div variants={itemVariants} className="bg-white rounded-lg shadow border border-gray-100 p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <FiBarChart className="w-5 h-5 text-indigo-500 mr-2" />
            Prediction Trends & Alert Generation
          </h3>
          <div className="text-sm text-gray-600 bg-indigo-50 px-3 py-1.5 rounded-md font-medium">
            7-Day Overview
          </div>
        </div>
        <div className="h-80">
          <PredictionTrendsChart />
        </div>
      </motion.div>

      {/* Performance Table */}
      <motion.div variants={itemVariants} className="bg-white rounded-lg shadow border border-gray-100 p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <FiActivity className="w-5 h-5 text-blue-500 mr-2" />
          Recent Performance
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-gray-50 to-blue-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Accuracy
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Predictions
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Alerts Generated
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentPerformance.map((day, index) => (
                <motion.tr 
                  key={day.date} 
                  className="hover:bg-blue-50 transition-colors duration-300"
                  whileHover={{ scale: 1.02 }}
                  transition={{ duration: 0.2 }}
                >
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                    {new Date(day.date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    <span className={`inline-flex px-2.5 py-1 rounded text-xs font-medium shadow ${
                      day.accuracy >= 95 ? 'bg-green-100 text-green-800' :
                      day.accuracy >= 90 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {day.accuracy}%
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                    {day.predictions}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                    {day.alerts}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`inline-flex px-2.5 py-1 rounded text-xs font-medium shadow ${
                      day.accuracy >= 95 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {day.accuracy >= 95 ? 'Excellent' : 'Good'}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Feature Importance */}
      <motion.div variants={itemVariants} className="bg-white rounded-lg shadow border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <FiTarget className="w-5 h-5 text-purple-500 mr-2" />
          Model Feature Importance (SHAP)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Top Contributing Features</h4>
            <div className="space-y-3">
              {[
                { feature: 'Weather Conditions', importance: 0.35, color: 'bg-blue-500' },
                { feature: 'Historical Patterns', importance: 0.28, color: 'bg-green-500' },
                { feature: 'Grid Load', importance: 0.18, color: 'bg-yellow-500' },
                { feature: 'Maintenance Schedule', importance: 0.12, color: 'bg-red-500' },
                { feature: 'Seasonal Factors', importance: 0.07, color: 'bg-purple-500' }
              ].map((item, index) => (
                <motion.div 
                  key={item.feature} 
                  className="flex items-center"
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="w-40 text-xs font-medium text-gray-700">{item.feature}</div>
                  <div className="flex-1 mx-3">
                    <div className="bg-gray-200 rounded-full h-3 shadow-inner">
                      <motion.div
                        className={`h-3 rounded-full ${item.color} shadow`}
                        initial={{ width: 0 }}
                        animate={{ width: `${item.importance * 100}%` }}
                        transition={{ duration: 1, delay: index * 0.1 }}
                      ></motion.div>
                    </div>
                  </div>
                  <div className="text-xs font-medium text-gray-700 w-12 text-right">
                    {(item.importance * 100).toFixed(0)}%
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
          <div className="flex items-center justify-center text-gray-600">
            <motion.div 
              className="text-center"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
            >
              <div className="w-20 h-20 mx-auto mb-3 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center shadow">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <p className="text-base font-semibold text-gray-700 mb-1">AI Model Insights</p>
              <p className="text-sm text-gray-500">Feature importance and decision explanations</p>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default Analytics;
