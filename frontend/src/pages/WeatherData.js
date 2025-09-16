import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import useStore from '../store/useStore';
import { apiService } from '../services/api';
import TemperatureChart from '../components/charts/TemperatureChart';
import PrecipitationChart from '../components/charts/PrecipitationChart';
import WindChart from '../components/charts/WindChart';
import HumidityChart from '../components/charts/HumidityChart';
import { FiThermometer, FiDroplet, FiWind, FiSun } from 'react-icons/fi';
import { WiHumidity, WiBarometer, WiStrongWind, WiCloudy } from 'react-icons/wi';

function WeatherData() {
  const { weatherData: storeWeatherData, filters } = useStore();
  const [selectedLocation, setSelectedLocation] = useState('Bangalore');
  const [timeRange, setTimeRange] = useState('24h');
  const [mockWeatherData, setMockWeatherData] = useState(null);

  // Generate mock weather data for demonstration
  const generateMockWeatherData = () => {
    const timeLabels = ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'];
    
    // Generate temperature data (°C)
    const tempBase = 24;
    const temperatures = timeLabels.map((_, i) => {
      if (i < 2) return tempBase - Math.random() * 3; // Early morning (cooler)
      if (i >= 2 && i < 4) return tempBase + Math.random() * 5; // Morning to noon (warming)
      if (i >= 4 && i < 6) return tempBase + 5 + Math.random() * 3; // Afternoon (warmest)
      return tempBase + 2 - Math.random() * 3; // Evening (cooling down)
    }).map(t => Math.round(t * 10) / 10);
    
    // Generate precipitation data (mm)
    const isRainy = Math.random() > 0.5;
    const precipitation = timeLabels.map(() => {
      if (!isRainy) return 0;
      const rainChance = Math.random();
      if (rainChance > 0.7) return Math.round(Math.random() * 100) / 10; // Some rain
      return 0; // No rain
    });
    
    // Generate wind data (km/h)
    const windBase = 10 + Math.random() * 10;
    const windSpeed = timeLabels.map(() => Math.round(windBase + Math.random() * 20));
    const windGust = windSpeed.map(speed => Math.round(speed * (1.2 + Math.random() * 0.5)));
    
    // Generate humidity data (%)
    const humidityBase = 60 + Math.random() * 20;
    const humidity = timeLabels.map((_, i) => {
      if (i < 3) return Math.min(95, humidityBase + 10 + Math.random() * 10); // Higher in early morning
      if (i >= 3 && i < 5) return Math.max(40, humidityBase - 10 - Math.random() * 10); // Lower in afternoon
      return Math.min(90, humidityBase + Math.random() * 5); // Rising in evening
    }).map(h => Math.round(h));
    
    return {
      labels: timeLabels,
      temperatures,
      minTemp: Math.min(...temperatures),
      maxTemp: Math.max(...temperatures),
      precipitation,
      maxPrecipitation: Math.max(...precipitation),
      windSpeed,
      windGust,
      maxWindSpeed: Math.max(...windSpeed),
      maxWindGust: Math.max(...windGust),
      humidity
    };
  };

  // Generate mock data when location changes
  useEffect(() => {
    setMockWeatherData(generateMockWeatherData());
  }, [selectedLocation, timeRange]);

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
          <h3 className="text-xl font-semibold text-neutral-900 mb-4 flex items-center">
            <FiThermometer className="w-5 h-5 text-red-500 mr-2" />
            Temperature Trend
          </h3>
          {mockWeatherData ? (
            <TemperatureChart weatherData={mockWeatherData} />
          ) : (
            <div className="h-64 flex items-center justify-center bg-gradient-to-br from-orange-50 to-red-50 rounded-lg">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-orange-500 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <p className="text-lg font-medium text-neutral-700">Loading temperature data...</p>
                <p className="text-sm text-neutral-500">Please wait</p>
              </div>
            </div>
          )}
        </motion.div>

        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
          <h3 className="text-xl font-semibold text-neutral-900 mb-4 flex items-center">
            <FiDroplet className="w-5 h-5 text-blue-500 mr-2" />
            Precipitation
          </h3>
          {mockWeatherData ? (
            <PrecipitationChart weatherData={mockWeatherData} />
          ) : (
            <div className="h-64 flex items-center justify-center bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-blue-500 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                </div>
                <p className="text-lg font-medium text-neutral-700">Loading precipitation data...</p>
                <p className="text-sm text-neutral-500">Please wait</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Additional Weather Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
          <h3 className="text-xl font-semibold text-neutral-900 mb-4 flex items-center">
            <FiWind className="w-5 h-5 text-green-500 mr-2" />
            Wind Speed & Gust
          </h3>
          {mockWeatherData ? (
            <WindChart weatherData={mockWeatherData} />
          ) : (
            <div className="h-64 flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </div>
                <p className="text-lg font-medium text-neutral-700">Loading wind data...</p>
                <p className="text-sm text-neutral-500">Please wait</p>
              </div>
            </div>
          )}
        </motion.div>

        <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
          <h3 className="text-xl font-semibold text-neutral-900 mb-4 flex items-center">
            <WiHumidity className="w-6 h-6 text-blue-500 mr-1" />
            Humidity
          </h3>
          {mockWeatherData ? (
            <HumidityChart weatherData={mockWeatherData} />
          ) : (
            <div className="h-64 flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-blue-500 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                  </svg>
                </div>
                <p className="text-lg font-medium text-neutral-700">Loading humidity data...</p>
                <p className="text-sm text-neutral-500">Please wait</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Weather Alerts */}
      <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Weather Alerts & Warnings</h3>
        <div className="space-y-3">
          {mockWeatherData?.maxWindSpeed > 40 && (
            <div className="flex items-center p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center">
                  <WiStrongWind className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-base font-semibold text-amber-800">High Wind Warning</p>
                <p className="text-sm text-amber-700">Wind speeds of {mockWeatherData.maxWindSpeed} km/h expected in {selectedLocation}</p>
              </div>
            </div>
          )}
          
          {mockWeatherData?.maxPrecipitation > 5 && (
            <div className="flex items-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <FiDroplet className="w-4 h-4 text-white" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-base font-semibold text-blue-800">Heavy Rain Advisory</p>
                <p className="text-sm text-blue-700">Precipitation levels of {mockWeatherData.maxPrecipitation.toFixed(1)} mm expected</p>
              </div>
            </div>
          )}
          
          {mockWeatherData?.maxTemp > 32 && (
            <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                  <FiThermometer className="w-4 h-4 text-white" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-base font-semibold text-red-800">High Temperature Alert</p>
                <p className="text-sm text-red-700">Temperatures up to {mockWeatherData.maxTemp}°C expected in {selectedLocation}</p>
              </div>
            </div>
          )}
          
          {mockWeatherData?.humidity.some(h => h > 90) && (
            <div className="flex items-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                  <WiHumidity className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-base font-semibold text-purple-800">High Humidity Warning</p>
                <p className="text-sm text-purple-700">Humidity levels above 90% may impact electrical equipment</p>
              </div>
            </div>
          )}
          
          {!mockWeatherData?.maxWindSpeed > 40 && 
           !mockWeatherData?.maxPrecipitation > 5 && 
           !mockWeatherData?.maxTemp > 32 && 
           !mockWeatherData?.humidity.some(h => h > 90) && (
            <div className="flex items-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-base font-semibold text-green-800">No Weather Alerts</p>
                <p className="text-sm text-green-700">Weather conditions in {selectedLocation} are normal</p>
              </div>
            </div>
          )}
          
          {/* Always show standard Thunderstorm Warning as fallback */}
          {!mockWeatherData && (
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
          )}
        </div>
      </motion.div>
      
      {/* Weather Impact Analysis */}
      <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <h3 className="text-xl font-semibold text-neutral-900 mb-4">Power Outage Risk Assessment</h3>
        <p className="text-neutral-600 mb-4">
          Based on current weather conditions, here's our analysis of potential impacts on power infrastructure:
        </p>
        
        {mockWeatherData && (
          <div className="space-y-4">
            {/* Risk Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white border border-neutral-200 rounded-lg p-4 flex flex-col items-center">
                <div className="text-sm font-medium text-neutral-600 mb-1">Wind Risk</div>
                <div className={`text-xl font-bold ${
                  mockWeatherData.maxWindSpeed > 60 ? 'text-red-600' :
                  mockWeatherData.maxWindSpeed > 40 ? 'text-amber-600' :
                  mockWeatherData.maxWindSpeed > 25 ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {mockWeatherData.maxWindSpeed > 60 ? 'Severe' :
                   mockWeatherData.maxWindSpeed > 40 ? 'High' :
                   mockWeatherData.maxWindSpeed > 25 ? 'Moderate' :
                   'Low'}
                </div>
                <div className="w-full bg-neutral-100 rounded-full h-2.5 mt-2">
                  <div className={`h-2.5 rounded-full ${
                    mockWeatherData.maxWindSpeed > 60 ? 'bg-red-600' :
                    mockWeatherData.maxWindSpeed > 40 ? 'bg-amber-600' :
                    mockWeatherData.maxWindSpeed > 25 ? 'bg-yellow-500' :
                    'bg-green-600'
                  }`} style={{ width: `${Math.min(100, (mockWeatherData.maxWindSpeed / 80) * 100)}%` }}></div>
                </div>
              </div>
              
              <div className="bg-white border border-neutral-200 rounded-lg p-4 flex flex-col items-center">
                <div className="text-sm font-medium text-neutral-600 mb-1">Precipitation Risk</div>
                <div className={`text-xl font-bold ${
                  mockWeatherData.maxPrecipitation > 10 ? 'text-red-600' :
                  mockWeatherData.maxPrecipitation > 5 ? 'text-amber-600' :
                  mockWeatherData.maxPrecipitation > 2 ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {mockWeatherData.maxPrecipitation > 10 ? 'Severe' :
                   mockWeatherData.maxPrecipitation > 5 ? 'High' :
                   mockWeatherData.maxPrecipitation > 2 ? 'Moderate' :
                   'Low'}
                </div>
                <div className="w-full bg-neutral-100 rounded-full h-2.5 mt-2">
                  <div className={`h-2.5 rounded-full ${
                    mockWeatherData.maxPrecipitation > 10 ? 'bg-red-600' :
                    mockWeatherData.maxPrecipitation > 5 ? 'bg-amber-600' :
                    mockWeatherData.maxPrecipitation > 2 ? 'bg-yellow-500' :
                    'bg-green-600'
                  }`} style={{ width: `${Math.min(100, (mockWeatherData.maxPrecipitation / 15) * 100)}%` }}></div>
                </div>
              </div>
              
              <div className="bg-white border border-neutral-200 rounded-lg p-4 flex flex-col items-center">
                <div className="text-sm font-medium text-neutral-600 mb-1">Temperature Risk</div>
                <div className={`text-xl font-bold ${
                  mockWeatherData.maxTemp > 38 ? 'text-red-600' :
                  mockWeatherData.maxTemp > 32 ? 'text-amber-600' :
                  mockWeatherData.maxTemp > 28 ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {mockWeatherData.maxTemp > 38 ? 'Severe' :
                   mockWeatherData.maxTemp > 32 ? 'High' :
                   mockWeatherData.maxTemp > 28 ? 'Moderate' :
                   'Low'}
                </div>
                <div className="w-full bg-neutral-100 rounded-full h-2.5 mt-2">
                  <div className={`h-2.5 rounded-full ${
                    mockWeatherData.maxTemp > 38 ? 'bg-red-600' :
                    mockWeatherData.maxTemp > 32 ? 'bg-amber-600' :
                    mockWeatherData.maxTemp > 28 ? 'bg-yellow-500' :
                    'bg-green-600'
                  }`} style={{ width: `${Math.min(100, ((mockWeatherData.maxTemp - 20) / 25) * 100)}%` }}></div>
                </div>
              </div>
              
              <div className="bg-white border border-neutral-200 rounded-lg p-4 flex flex-col items-center">
                <div className="text-sm font-medium text-neutral-600 mb-1">Humidity Risk</div>
                <div className={`text-xl font-bold ${
                  Math.max(...mockWeatherData.humidity) > 95 ? 'text-red-600' :
                  Math.max(...mockWeatherData.humidity) > 90 ? 'text-amber-600' :
                  Math.max(...mockWeatherData.humidity) > 80 ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {Math.max(...mockWeatherData.humidity) > 95 ? 'Severe' :
                   Math.max(...mockWeatherData.humidity) > 90 ? 'High' :
                   Math.max(...mockWeatherData.humidity) > 80 ? 'Moderate' :
                   'Low'}
                </div>
                <div className="w-full bg-neutral-100 rounded-full h-2.5 mt-2">
                  <div className={`h-2.5 rounded-full ${
                    Math.max(...mockWeatherData.humidity) > 95 ? 'bg-red-600' :
                    Math.max(...mockWeatherData.humidity) > 90 ? 'bg-amber-600' :
                    Math.max(...mockWeatherData.humidity) > 80 ? 'bg-yellow-500' :
                    'bg-green-600'
                  }`} style={{ width: `${Math.min(100, (Math.max(...mockWeatherData.humidity) / 100) * 100)}%` }}></div>
                </div>
              </div>
            </div>
            
            {/* Overall Risk Assessment */}
            <div className="bg-neutral-50 p-5 rounded-lg border border-neutral-200 mt-4">
              <h4 className="font-semibold text-lg text-neutral-900 mb-2">Impact Analysis</h4>
              <div className="space-y-3">
                {mockWeatherData.maxWindSpeed > 40 && (
                  <p className="text-neutral-700">
                    <span className="font-medium text-amber-700">Wind impact:</span> Wind speeds of {mockWeatherData.maxWindSpeed} km/h may cause swinging overhead lines, possibly leading to momentary outages or damage to infrastructure in exposed areas.
                  </p>
                )}
                
                {mockWeatherData.maxPrecipitation > 5 && (
                  <p className="text-neutral-700">
                    <span className="font-medium text-blue-700">Precipitation impact:</span> Heavy rainfall ({mockWeatherData.maxPrecipitation.toFixed(1)} mm) increases the risk of water intrusion into electrical equipment and may cause localized flooding around ground-mounted transformers.
                  </p>
                )}
                
                {mockWeatherData.maxTemp > 32 && (
                  <p className="text-neutral-700">
                    <span className="font-medium text-red-700">Temperature impact:</span> High temperatures ({mockWeatherData.maxTemp}°C) may lead to thermal overload of transformers and increased demand from cooling systems, potentially triggering load-shedding.
                  </p>
                )}
                
                {Math.max(...mockWeatherData.humidity) > 90 && (
                  <p className="text-neutral-700">
                    <span className="font-medium text-purple-700">Humidity impact:</span> Very high humidity ({Math.max(...mockWeatherData.humidity)}%) can cause condensation on insulators and equipment, increasing the risk of flashovers and short circuits.
                  </p>
                )}
                
                {!mockWeatherData.maxWindSpeed > 40 && 
                 !mockWeatherData.maxPrecipitation > 5 && 
                 !mockWeatherData.maxTemp > 32 && 
                 !Math.max(...mockWeatherData.humidity) > 90 && (
                  <p className="text-neutral-700">
                    <span className="font-medium text-green-700">Favorable conditions:</span> Current weather parameters in {selectedLocation} are within normal operational limits for power infrastructure. No significant weather-related risks identified.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}

export default WeatherData;
