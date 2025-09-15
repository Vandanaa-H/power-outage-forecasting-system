import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import useStore from '../store/useStore';
import { apiService } from '../services/api';

function WeatherData() {
  const { weatherData, filters } = useStore();
  const [selectedLocation, setSelectedLocation] = useState('Bangalore');
  const [timeRange, setTimeRange] = useState('24h');

  const { data: currentWeather, isLoading: weatherLoading } = useQuery(
    ['weather', selectedLocation],
    () => apiService.getWeatherData(selectedLocation),
    {
      refetchInterval: 300000, // Refresh every 5 minutes
    }
  );

  const { data: historicalWeather } = useQuery(
    ['weather', 'historical', selectedLocation, timeRange],
    () => apiService.getHistoricalWeather(selectedLocation, timeRange)
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

  const cities = [
    'Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Gulbarga',
    'Davangere', 'Bellary', 'Bijapur', 'Shimoga', 'Tumkur', 'Raichur'
  ];

  const weatherMetrics = currentWeather ? [
    { label: 'Temperature', value: `${currentWeather.temperature}°C`, trend: '+2°C' },
    { label: 'Humidity', value: `${currentWeather.humidity}%`, trend: '-5%' },
    { label: 'Wind Speed', value: `${currentWeather.wind_speed} km/h`, trend: '+3 km/h' },
    { label: 'Pressure', value: `${currentWeather.pressure} hPa`, trend: '-2 hPa' },
    { label: 'Visibility', value: `${currentWeather.visibility || 10} km`, trend: 'Normal' },
    { label: 'UV Index', value: currentWeather.uv_index || 5, trend: 'Moderate' }
  ] : [];

  if (weatherLoading) {
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
          <h1 className="text-3xl font-bold text-neutral-900">Weather Data</h1>
          <p className="text-neutral-600 mt-1">
            Real-time weather monitoring and historical analysis
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedLocation}
            onChange={(e) => setSelectedLocation(e.target.value)}
            className="border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {cities.map(city => (
              <option key={city} value={city}>{city}</option>
            ))}
          </select>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>
      </motion.div>

      {/* Current Weather Overview */}
      <motion.div variants={itemVariants} className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-sm p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{selectedLocation}</h2>
            <p className="text-blue-100">Current Weather Conditions</p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{currentWeather?.temperature || '--'}°C</div>
            <p className="text-blue-100">{currentWeather?.description || 'Loading...'}</p>
          </div>
        </div>
      </motion.div>

      {/* Weather Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {weatherMetrics.map((metric, index) => (
          <motion.div
            key={metric.label}
            variants={itemVariants}
            className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-600">{metric.label}</p>
                <p className="text-2xl font-bold text-neutral-900 mt-1">{metric.value}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-neutral-500">Change</p>
                <p className={`text-sm font-medium ${
                  metric.trend.includes('+') ? 'text-green-600' :
                  metric.trend.includes('-') ? 'text-red-600' :
                  'text-neutral-600'
                }`}>
                  {metric.trend}
                </p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Weather Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">Temperature Trend</h3>
          <div className="h-64 flex items-center justify-center bg-gradient-to-br from-orange-50 to-red-50 rounded-lg">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-orange-500 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-lg font-medium text-neutral-700">Advanced weather charts coming soon</p>
              <p className="text-sm text-neutral-500">Real-time temperature tracking and forecasting</p>
            </div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">Precipitation & Humidity</h3>
          <div className="h-64 flex items-center justify-center bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-blue-500 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <p className="text-lg font-medium text-neutral-700">Precipitation monitoring system</p>
              <p className="text-sm text-neutral-500">Humidity levels and rainfall predictions</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Weather Alerts */}
      <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Weather Alerts & Warnings</h3>
        <div className="space-y-3">
          <div className="flex items-center p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.998-.833-2.768 0L3.046 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-base font-semibold text-yellow-800">Thunderstorm Warning</p>
              <p className="text-sm text-yellow-700">Expected in the next 2-4 hours for {selectedLocation}</p>
            </div>
          </div>
          <div className="flex items-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-base font-semibold text-blue-800">Heavy Rain Advisory</p>
              <p className="text-sm text-blue-700">Moderate to heavy rainfall expected tomorrow</p>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default WeatherData;
