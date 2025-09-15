import React, { useState, useEffect } from 'react';
import { 
  ExclamationTriangleIcon, 
  InformationCircleIcon,
  CheckCircleIcon,
  XCircleIcon,
  BoltIcon,
  CloudIcon,
  MapPinIcon
} from '@heroicons/react/24/outline';
import RiskMetricsCard from '../components/RiskMetricsCard';
import WeatherWidget from '../components/WeatherWidget';
import AlertsList from '../components/AlertsList';
import QuickActions from '../components/QuickActions';
import RecentPredictions from '../components/RecentPredictions';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

function Dashboard() {
  const [systemHealth, setSystemHealth] = useState(null);
  const [recentAdvisories, setRecentAdvisories] = useState([]);
  const [quickStats, setQuickStats] = useState({
    totalPredictions: 0,
    highRiskAreas: 0,
    activeAlerts: 0,
    systemUptime: '99.9%'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load system health
      const healthResponse = await apiService.getSystemHealth();
      setSystemHealth(healthResponse);

      // Load recent advisories
      const advisoriesResponse = await apiService.getAdvisories({ limit: 5 });
      setRecentAdvisories(advisoriesResponse.advisories || []);

      // Load quick stats (mock data for now)
      setQuickStats({
        totalPredictions: 1247,
        highRiskAreas: 3,
        activeAlerts: advisoriesResponse.active_count || 0,
        systemUptime: '99.9%'
      });

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getSystemStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-6 w-6 text-yellow-500" />;
      case 'error':
        return <XCircleIcon className="h-6 w-6 text-red-500" />;
      default:
        return <InformationCircleIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const getSystemStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-50 border-green-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Power Outage Forecasting Dashboard</h1>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={loadDashboardData}
            className="inline-flex items-center px-6 py-3 border border-gray-300 rounded-md shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh Data
          </button>
        </div>
      </div>

      {/* System Status */}
      {systemHealth && (
        <div className={`rounded-lg border p-4 ${getSystemStatusColor(systemHealth.status)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              {getSystemStatusIcon(systemHealth.status)}
              <div className="ml-3">
                <h3 className="text-lg font-medium text-gray-900">
                  System Status: {systemHealth.status.toUpperCase()}
                </h3>
                <p className="text-sm text-gray-600">
                  Last updated: {new Date(systemHealth.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
            {systemHealth.warnings && (
              <div className="text-sm text-gray-600">
                {systemHealth.warnings} warning(s)
              </div>
            )}
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BoltIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Predictions</p>
              <p className="text-2xl font-bold text-gray-900">{quickStats.totalPredictions}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">High Risk Areas</p>
              <p className="text-2xl font-bold text-gray-900">{quickStats.highRiskAreas}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CloudIcon className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Alerts</p>
              <p className="text-2xl font-bold text-gray-900">{quickStats.activeAlerts}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">System Uptime</p>
              <p className="text-2xl font-bold text-gray-900">{quickStats.systemUptime}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Metrics */}
        <div className="lg:col-span-2">
          <RiskMetricsCard />
        </div>

        {/* Weather Widget */}
        <div>
          <WeatherWidget />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Advisories */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Advisories</h3>
          <AlertsList alerts={recentAdvisories} />
        </div>

        {/* Quick Actions */}
        <div>
          <QuickActions />
        </div>
      </div>

      {/* Recent Predictions */}
      <div className="bg-white rounded-lg shadow">
        <RecentPredictions />
      </div>
    </div>
  );
}

export default Dashboard;
