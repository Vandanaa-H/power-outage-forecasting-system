import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';

function WeatherWidget() {
  const [userLocation, setUserLocation] = useState(null); // No default fallback - will be detected
  const [locationLoading, setLocationLoading] = useState(true);

  // Get user's current location on component mount
  useEffect(() => {
    const getUserLocation = async () => {
      try {
        const location = await apiService.getCurrentLocation();
        setUserLocation(location.city);
      } catch (error) {
        console.warn('Could not get user location:', error.message);
        // Set a generic fallback location or keep null to show "Location Unknown"
        setUserLocation('Current Location');
      } finally {
        setLocationLoading(false);
      }
    };

    getUserLocation();
  }, []);

  const { data: weatherData, isLoading } = useQuery(
    ['weather', 'current', userLocation],
    () => apiService.getWeatherData(userLocation),
    {
      refetchInterval: 300000, // Refresh every 5 minutes
      enabled: !locationLoading, // Only fetch weather after location is determined
    }
  );

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const mockWeather = {
    location: userLocation || 'Unknown Location',
    temperature: 26,
    description: 'Partly Cloudy',
    humidity: 68,
    wind_speed: 12,
    pressure: 1013,
    feels_like: 29
  };

  if (isLoading || locationLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-neutral-200 rounded w-1/2"></div>
          <div className="h-32 bg-neutral-200 rounded"></div>
        </div>
      </div>
    );
  }

  const data = weatherData || mockWeather;

  return (
    <motion.div
      variants={itemVariants}
      className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-sm p-6 text-white"
    >
      <h3 className="text-lg font-semibold mb-4">Current Weather</h3>
      
      <div className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-1">
            <p className="text-blue-100 text-sm">{data.location}</p>
            {locationLoading && <span className="text-blue-200 text-xs">Detecting location...</span>}
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-3xl font-bold">{data.temperature}°C</p>
              <p className="text-blue-100 text-sm">Feels like {data.feels_like}°C</p>
            </div>
            <div className="text-right">
              <div className="text-2xl mb-1 text-white font-bold">
                {data.description?.toLowerCase().includes('cloud') ? 'CLOUDY' :
                 data.description?.toLowerCase().includes('rain') ? 'RAINY' :
                 data.description?.toLowerCase().includes('sun') ? 'SUNNY' :
                 'PARTLY CLOUDY'}
              </div>
            </div>
          </div>
          <p className="text-blue-100 text-sm mt-1">{data.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-blue-400">
          <div>
            <p className="text-blue-100 text-xs">Humidity</p>
            <p className="text-lg font-semibold">{data.humidity}%</p>
          </div>
          <div>
            <p className="text-blue-100 text-xs">Wind</p>
            <p className="text-lg font-semibold">{data.wind_speed} km/h</p>
          </div>
          <div>
            <p className="text-blue-100 text-xs">Pressure</p>
            <p className="text-lg font-semibold">{data.pressure} hPa</p>
          </div>
          <div>
            <p className="text-blue-100 text-xs">Visibility</p>
            <p className="text-lg font-semibold">{data.visibility || 10} km</p>
          </div>
        </div>

        <div className="pt-4 border-t border-blue-400">
          <div className="flex items-center justify-between text-sm">
            <span className="text-blue-100">Impact on Grid</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              data.temperature > 35 || data.wind_speed > 25 ? 'bg-red-100 text-red-800' :
              data.temperature > 30 || data.wind_speed > 15 ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {data.temperature > 35 || data.wind_speed > 25 ? 'High Risk' :
               data.temperature > 30 || data.wind_speed > 15 ? 'Medium Risk' :
               'Low Risk'}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default WeatherWidget;
