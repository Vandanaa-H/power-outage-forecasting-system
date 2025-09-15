import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const PredictionMap = () => {
  const navigate = useNavigate();
  const [selectedDistrict, setSelectedDistrict] = useState(null);
  const [riskLevel, setRiskLevel] = useState('all');
  const [timeFilter, setTimeFilter] = useState('24h');
  const [isMapReady, setIsMapReady] = useState(false);
  const [activeAlerts, setActiveAlerts] = useState([
    { id: 1, district: 'Bangalore Urban', type: 'High Risk', severity: 'warning', message: 'Thunderstorm expected, high outage probability' },
    { id: 2, district: 'Gulbarga', type: 'High Risk', severity: 'danger', message: 'Equipment maintenance required, potential outages' },
    { id: 3, district: 'Mangalore', type: 'Medium Risk', severity: 'info', message: 'Weather conditions may affect power supply' }
  ]);

  // Karnataka districts with coordinates and risk data
  const districtData = {
    'Bangalore Urban': { risk: 'high', outageProb: 85, lat: 12.9716, lng: 77.5946, population: 13200000 },
    'Mysore': { risk: 'medium', outageProb: 45, lat: 12.2958, lng: 76.6394, population: 3000000 },
    'Hubli-Dharwad': { risk: 'low', outageProb: 20, lat: 15.3647, lng: 75.1240, population: 1150000 },
    'Mangalore': { risk: 'medium', outageProb: 60, lat: 12.9141, lng: 74.8560, population: 650000 },
    'Gulbarga': { risk: 'high', outageProb: 78, lat: 17.3297, lng: 76.8343, population: 2560000 },
    'Belgaum': { risk: 'medium', outageProb: 55, lat: 15.8497, lng: 74.4977, population: 4800000 },
    'Tumkur': { risk: 'low', outageProb: 25, lat: 13.3379, lng: 77.1022, population: 2680000 },
    'Shimoga': { risk: 'medium', outageProb: 40, lat: 13.9299, lng: 75.5681, population: 1750000 },
    'Davangere': { risk: 'low', outageProb: 30, lat: 14.4644, lng: 75.9218, population: 1940000 },
    'Bellary': { risk: 'high', outageProb: 72, lat: 15.1394, lng: 76.9214, population: 2452000 }
  };

  const filteredDistricts = Object.entries(districtData).filter(([name, data]) => {
    if (riskLevel === 'all') return true;
    return data.risk === riskLevel;
  });

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'high': return '#EF4444';
      case 'medium': return '#F59E0B';
      case 'low': return '#10B981';
      default: return '#6B7280';
    }
  };

  const getRiskColorClass = (risk) => {
    switch (risk) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getMarkerSize = (risk) => {
    switch (risk) {
      case 'high': return 25;
      case 'medium': return 20;
      case 'low': return 15;
      default: return 15;
    }
  };

  useEffect(() => {
    // Simulate map loading
    const timer = setTimeout(() => {
      setIsMapReady(true);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  const MapComponent = () => {
    if (!isMapReady) {
      return (
        <div className="bg-gray-100 rounded-lg flex items-center justify-center" style={{ height: '60vh', minHeight: '400px' }}>
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600 text-lg">Loading Karnataka Districts Map...</p>
          </div>
        </div>
      );
    }

    return (
      <MapContainer
        center={[15.3173, 75.7139]} // Karnataka center
        zoom={7}
        style={{ height: '60vh', minHeight: '400px', width: '100%' }}
        className="rounded-lg z-10"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {filteredDistricts.map(([name, data]) => (
          <CircleMarker
            key={name}
            center={[data.lat, data.lng]}
            radius={getMarkerSize(data.risk)}
            fillColor={getRiskColor(data.risk)}
            color="white"
            weight={2}
            opacity={1}
            fillOpacity={0.8}
            eventHandlers={{
              click: () => setSelectedDistrict({ name, ...data }),
            }}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-semibold text-lg text-gray-900 mb-2">{name}</h3>
                <div className="space-y-1 text-sm">
                  <div><strong>Risk Level:</strong> <span className="capitalize">{data.risk}</span></div>
                  <div><strong>Outage Probability:</strong> {data.outageProb}%</div>
                  <div><strong>Population:</strong> {data.population.toLocaleString()}</div>
                  <div><strong>Estimated Affected:</strong> {Math.round(data.population * data.outageProb / 100).toLocaleString()}</div>
                </div>
              </div>
            </Popup>
            <Tooltip permanent={false} direction="top" offset={[0, -10]}>
              {name}: {data.outageProb}%
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
    );
  };

  return (
    <div className="space-y-6 lg:space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 lg:p-8"
      >
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6 lg:mb-8">
          <div>
            <h1 className="text-3xl lg:text-5xl font-bold text-gray-900 mb-2 lg:mb-3">Prediction Risk Map</h1>
            <p className="text-lg lg:text-xl text-gray-600 mb-4">Real-time power outage risk visualization for Karnataka districts</p>
            
            {/* Quick Actions */}
            <div className="flex flex-wrap gap-3 mb-4">
              <button
                onClick={() => {
                  console.log('Navigating to /advisory');
                  navigate('/advisory');
                }}
                className="inline-flex items-center px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                View Public Advisory
              </button>
              
              <button
                onClick={() => window.open('tel:1800-xxx-xxxx')}
                className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                Emergency Helpline
              </button>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 mt-6 lg:mt-0">
            <select
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              className="px-6 py-4 text-lg font-medium border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm hover:border-gray-400 transition-colors"
            >
              <option value="6h">Next 6 Hours</option>
              <option value="12h">Next 12 Hours</option>
              <option value="24h">Next 24 Hours</option>
              <option value="48h">Next 48 Hours</option>
            </select>
            
            <select
              value={riskLevel}
              onChange={(e) => setRiskLevel(e.target.value)}
              className="px-6 py-4 text-lg font-medium border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm hover:border-gray-400 transition-colors"
            >
              <option value="all">All Risk Levels</option>
              <option value="high">High Risk Only</option>
              <option value="medium">Medium Risk Only</option>
              <option value="low">Low Risk Only</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 lg:gap-6 xl:gap-8">
          {/* Interactive Map */}
          <div className="lg:col-span-3 order-1 lg:order-1">
            <div className="bg-white rounded-xl overflow-hidden border-2 border-gray-200 shadow-lg">
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 lg:px-6 py-3 lg:py-4">
                <h2 className="text-lg lg:text-xl font-bold text-white">Karnataka Power Outage Risk Map</h2>
                <p className="text-blue-100 text-xs lg:text-sm mt-1">Real-time district-wise power outage predictions</p>
              </div>
              <MapComponent />
            </div>
          </div>

          {/* District Info Panel */}
          <div className="space-y-4 lg:space-y-6 order-2 lg:order-2">
            {/* Active Alerts Section */}
            <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4 lg:p-6">
              <div className="flex items-center justify-between mb-3 lg:mb-4">
                <h3 className="text-lg lg:text-xl font-semibold text-red-900">Active Alerts</h3>
                <Link
                  to="/advisory"
                  className="text-red-700 hover:text-red-900 font-medium text-sm lg:text-base underline"
                >
                  View All →
                </Link>
              </div>
              <div className="space-y-3">
                {activeAlerts.slice(0, 2).map(alert => (
                  <div key={alert.id} className="bg-white rounded-lg p-4 border border-red-200">
                    <div className="flex items-start gap-3">
                      <div className={`w-3 h-3 rounded-full mt-1 ${
                        alert.severity === 'danger' ? 'bg-red-500' :
                        alert.severity === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`}></div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 text-base">{alert.district}</h4>
                        <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                        <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-2 ${
                          alert.severity === 'danger' ? 'bg-red-100 text-red-800' :
                          alert.severity === 'warning' ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'
                        }`}>
                          {alert.type}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Districts Overview */}
            <div className="bg-white border-2 border-gray-200 rounded-xl p-4 lg:p-6">
              <h3 className="text-lg lg:text-xl font-semibold text-gray-900 mb-3 lg:mb-4">Districts Overview</h3>
              
              <div className="space-y-2 lg:space-y-3 max-h-64 lg:max-h-80 overflow-y-auto custom-scrollbar">
                {filteredDistricts.map(([name, data], index) => (
                  <motion.div
                    key={name}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-3 lg:p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-all duration-200 border border-gray-200 hover:border-gray-300 hover:shadow-md"
                    onClick={() => setSelectedDistrict({ name, ...data })}
                  >
                  <div className="flex justify-between items-center mb-2 lg:mb-3">
                    <h4 className="font-semibold text-gray-900 text-base lg:text-lg">{name}</h4>
                    <span className={`px-2 lg:px-4 py-1 lg:py-2 rounded-full text-sm lg:text-base font-semibold ${getRiskColorClass(data.risk)}`}>
                      {data.risk.charAt(0).toUpperCase() + data.risk.slice(1)}
                    </span>
                  </div>
                  <div className="text-sm lg:text-base text-gray-600 mb-2 lg:mb-4">
                    Outage Probability: <span className="font-semibold text-base lg:text-lg">{data.outageProb}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 lg:h-4">
                    <div
                      className="h-3 lg:h-4 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${data.outageProb}%`,
                        backgroundColor: getRiskColor(data.risk)
                      }}
                    ></div>
                  </div>
                </motion.div>
              ))}
              </div>
            </div>

            {selectedDistrict && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-8 bg-blue-50 rounded-xl border-2 border-blue-200"
              >
                <div className="flex items-center justify-between mb-6">
                  <h4 className="font-bold text-blue-900 text-2xl">
                    {selectedDistrict.name} Details
                  </h4>
                  <Link
                    to="/advisory"
                    state={{ district: selectedDistrict.name }}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                  >
                    View Alerts
                  </Link>
                </div>
                <div className="space-y-4">
                  <div className="flex justify-between items-center py-2">
                    <span className="text-blue-700 font-semibold text-lg">Risk Level:</span>
                    <span className="font-bold text-blue-900 text-lg">
                      {selectedDistrict.risk.charAt(0).toUpperCase() + selectedDistrict.risk.slice(1)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-blue-700 font-semibold text-lg">Outage Probability:</span>
                    <span className="font-bold text-blue-900 text-xl">{selectedDistrict.outageProb}%</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-blue-700 font-semibold text-lg">Population:</span>
                    <span className="font-bold text-blue-900 text-lg">
                      {selectedDistrict.population.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-blue-700 font-semibold text-lg">Estimated Affected:</span>
                    <span className="font-bold text-blue-900 text-lg">
                      {Math.round(selectedDistrict.population * selectedDistrict.outageProb / 100).toLocaleString()}
                    </span>
                  </div>
                  
                  {/* Preparedness Tips */}
                  <div className="mt-6 p-4 bg-white rounded-lg border border-blue-200">
                    <h5 className="font-semibold text-blue-900 mb-3 text-lg">Preparedness Tips:</h5>
                    <ul className="text-blue-800 space-y-2 text-base">
                      <li>• Keep emergency supplies ready</li>
                      <li>• Charge essential devices</li>
                      <li>• Have backup lighting available</li>
                      <li>• Monitor updates regularly</li>
                    </ul>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Legend and Map Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-8"
      >
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-8">Risk Level Legend</h3>
          <div className="space-y-6">
            <div className="flex items-center gap-6">
              <div className="w-8 h-8 bg-red-500 rounded-full border-2 border-white shadow-md"></div>
              <div>
                <div className="font-semibold text-gray-900 text-lg">High Risk</div>
                <div className="text-base text-gray-600">70%+ outage probability</div>
              </div>
            </div>
            <div className="flex items-center gap-6">
              <div className="w-8 h-8 bg-yellow-500 rounded-full border-2 border-white shadow-md"></div>
              <div>
                <div className="font-semibold text-gray-900 text-lg">Medium Risk</div>
                <div className="text-base text-gray-600">30-70% outage probability</div>
              </div>
            </div>
            <div className="flex items-center gap-6">
              <div className="w-8 h-8 bg-green-500 rounded-full border-2 border-white shadow-md"></div>
              <div>
                <div className="font-semibold text-gray-900 text-lg">Low Risk</div>
                <div className="text-base text-gray-600">0-30% outage probability</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-8">Map Instructions</h3>
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="w-3 h-3 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div className="text-gray-700 text-lg">Click on district markers for detailed information</div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-3 h-3 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div className="text-gray-700 text-lg">Use time filter to adjust prediction window</div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-3 h-3 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div className="text-gray-700 text-lg">Filter by risk level to focus on specific areas</div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-3 h-3 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div className="text-gray-700 text-lg">Real-time updates every 15 minutes</div>
            </div>
          </div>
          
          <div className="mt-8 pt-6 border-t border-gray-200">
            <button
              onClick={() => navigate('/advisory')}
              className="w-full py-4 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl text-lg"
            >
              Access Public Advisory & Alerts →
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default PredictionMap;
