import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FiActivity, 
  FiZap, 
  FiClock, 
  FiShield, 
  FiBarChart,
  FiMap,
  FiCloud,
  FiBell,
  FiArrowRight,
  FiChevronRight,
  FiAlertTriangle,
  FiCheckCircle,
  FiTool
} from 'react-icons/fi';
import RiskMetricsCard from '../components/RiskMetricsCard';
import WeatherWidget from '../components/WeatherWidget';
import AlertsList from '../components/AlertsList';
import QuickActions from '../components/QuickActions';
import RecentPredictions from '../components/RecentPredictions';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      delayChildren: 0.3,
      staggerChildren: 0.2
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1
  }
};

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mb-4 mx-auto shadow"></div>
          <div className="text-xl font-semibold text-gray-700">Loading Dashboard...</div>
          <div className="text-sm text-gray-500 mt-2">Fetching latest data</div>
        </motion.div>
      </div>
    );
  }

  return (
    <motion.div 
      className="min-h-screen bg-gray-50 p-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div 
          className="text-center mb-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.h1 
            variants={itemVariants}
            className="text-2xl font-bold text-gray-900 mb-2"
          >
            24-Hour Power Outage Forecasting System
          </motion.h1>
          <motion.p 
            variants={itemVariants}
            className="text-sm text-gray-600"
          >
            Advanced AI-powered predictions and real-time monitoring for power grid stability
          </motion.p>
        </motion.div>

        {/* KPI Cards - Properly Aligned */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg p-4 shadow border h-full flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-blue-600">92.3%</div>
                <div className="text-sm text-gray-500">Accuracy</div>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <FiActivity className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-3 pt-3 border-t">
              <div className="text-xs text-gray-600">Model Performance</div>
              <div className="text-xs text-green-600">+2.3% from last week</div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow border h-full flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-green-600">{quickStats.activeAlerts}</div>
                <div className="text-sm text-gray-500">Active Alerts</div>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <FiZap className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="mt-3 pt-3 border-t">
              <div className="text-xs text-gray-600">Active Monitoring</div>
              <div className="text-xs text-yellow-600">12 high priority</div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow border h-full flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-purple-600">24h</div>
                <div className="text-sm text-gray-500">Forecast Window</div>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <FiClock className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <div className="mt-3 pt-3 border-t">
              <div className="text-xs text-gray-600">Prediction Range</div>
              <div className="text-xs text-blue-600">Next update: 15 min</div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow border h-full flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-orange-600">{quickStats.systemUptime}</div>
                <div className="text-sm text-gray-500">System Uptime</div>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <FiShield className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <div className="mt-3 pt-3 border-t">
              <div className="text-xs text-gray-600">System Health</div>
              <div className="text-xs text-green-600">All systems operational</div>
            </div>
          </div>
        </div>

        {/* Quick Actions - Clean Layout */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <div>
            <Link to="/analytics" className="block group h-full">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow hover:shadow-lg transition-all duration-300 min-h-[160px] flex flex-col justify-between">
                <FiBarChart className="w-8 h-8 mb-3 text-blue-100" />
                <h3 className="text-lg font-semibold mb-2">Analytics Dashboard</h3>
                <p className="text-sm text-blue-100 mb-4">
                  View detailed performance metrics, charts, and predictive analytics
                </p>
                <div className="flex items-center text-sm font-medium">
                  <span>Explore Analytics</span>
                  <FiArrowRight className="ml-2 w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>
          </div>

          <div>
            <Link to="/map" className="block group h-full">
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white shadow hover:shadow-lg transition-all duration-300 min-h-[160px] flex flex-col justify-between">
                <FiMap className="w-8 h-8 mb-3 text-green-100" />
                <h3 className="text-lg font-semibold mb-2">Interactive Map</h3>
                <p className="text-sm text-green-100 mb-4">
                  Geographic visualization of outage predictions and risk zones
                </p>
                <div className="flex items-center text-sm font-medium">
                  <span>View Map</span>
                  <FiArrowRight className="ml-2 w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>
          </div>

          <div>
            <Link to="/weather" className="block group h-full">
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white shadow hover:shadow-lg transition-all duration-300 min-h-[160px] flex flex-col justify-between">
                <FiCloud className="w-8 h-8 mb-3 text-purple-100" />
                <h3 className="text-lg font-semibold mb-2">Weather Data</h3>
                <p className="text-sm text-purple-100 mb-4">
                  Real-time weather conditions and meteorological analysis
                </p>
                <div className="flex items-center text-sm font-medium">
                  <span>Check Weather</span>
                  <FiArrowRight className="ml-2 w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>
          </div>
        </motion.div>

        {/* Recent System Activity - Clean Layout */}
        <motion.div 
          className="bg-white rounded-lg shadow border border-gray-100 p-6 mb-8"
          variants={itemVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-800 flex items-center">
              <FiBell className="w-5 h-5 text-blue-600 mr-2" />
              Recent System Activity
            </h2>
            <Link to="/analytics" className="bg-blue-600 text-white px-3 py-1 rounded text-sm font-medium hover:bg-blue-700 transition-colors">
              View All
            </Link>
          </div>
          
          <div className="space-y-3">
            {[
              { time: '2 minutes ago', message: 'High wind alert triggered for Northern Grid', type: 'warning', icon: FiAlertTriangle },
              { time: '15 minutes ago', message: 'Predictive model accuracy improved to 92.3%', type: 'success', icon: FiCheckCircle },
              { time: '1 hour ago', message: 'Scheduled maintenance completed on Bay Area sensors', type: 'info', icon: FiTool },
              { time: '3 hours ago', message: '247 new data points processed from weather stations', type: 'info', icon: FiActivity }
            ].map((activity, index) => (
              <motion.div 
                key={index}
                className="flex items-center p-3 bg-gray-50 rounded border hover:bg-gray-100 transition-colors"
                whileHover={{ x: 5 }}
              >
                <div className={`w-8 h-8 rounded flex items-center justify-center mr-3 ${
                  activity.type === 'warning' ? 'bg-yellow-500' :
                  activity.type === 'success' ? 'bg-green-500' : 'bg-blue-500'
                }`}>
                  <activity.icon className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-800">{activity.message}</div>
                  <div className="text-xs text-gray-500">{activity.time}</div>
                </div>
                <FiChevronRight className="w-4 h-4 text-gray-400" />
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Additional Components - Clean Layout */}
        <motion.div 
          className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div variants={itemVariants} className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6 h-full min-h-[280px]">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Risk Metrics</h3>
              <RiskMetricsCard />
            </div>
          </motion.div>

          <motion.div variants={itemVariants}>
            <div className="bg-white rounded-lg shadow p-6 h-full min-h-[280px]">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Weather Widget</h3>
              <WeatherWidget />
            </div>
          </motion.div>
        </motion.div>

        <motion.div 
          className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div variants={itemVariants}>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Advisories</h3>
              <AlertsList alerts={recentAdvisories} />
            </div>
          </motion.div>

          <motion.div variants={itemVariants}>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
              <QuickActions />
            </div>
          </motion.div>
        </motion.div>

        <motion.div 
          className="bg-white rounded-lg shadow p-6"
          variants={itemVariants}
          initial="hidden"
          animate="visible"
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Predictions</h3>
          <RecentPredictions />
        </motion.div>
      </div>
    </motion.div>
  );
}

export default Dashboard;
