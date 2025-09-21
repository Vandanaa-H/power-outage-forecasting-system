import React, { useState, useEffect } from 'react';
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
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Prediction Risk Map</h1>
          <p className="text-gray-600">Real-time power outage risk visualization for Karnataka districts</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg p-4 mb-6 shadow border">
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              className="px-3 py-2 border rounded-md bg-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-w-[180px]"
            >
              <option value="6h">Next 6 Hours</option>
              <option value="12h">Next 12 Hours</option>
              <option value="24h">Next 24 Hours</option>
              <option value="48h">Next 48 Hours</option>
            </select>
            
            <select
              value={riskLevel}
              onChange={(e) => setRiskLevel(e.target.value)}
              className="px-3 py-2 border rounded-md bg-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-w-[180px]"
            >
              <option value="all">All Risk Levels</option>
              <option value="high">High Risk Only</option>
              <option value="medium">Medium Risk Only</option>
              <option value="low">Low Risk Only</option>
            </select>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Map Section */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg border shadow">
              <div className="bg-blue-600 px-4 py-3 rounded-t-lg">
                <h2 className="text-lg font-semibold text-white">Karnataka Power Outage Risk Map</h2>
              </div>
              <div className="p-4">
                <MapComponent />
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Active Alerts Section */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 lg:p-4 min-h-[160px]">
              <div className="flex items-center justify-between mb-3 lg:mb-4">
                <h3 className="text-base lg:text-lg font-semibold text-red-900">Active Alerts</h3>
                <Link
                  to="/advisory"
                  className="text-red-700 hover:text-red-900 font-medium text-xs lg:text-sm underline"
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
            <div className="bg-white border border-gray-200 rounded-lg p-4 lg:p-4 min-h-[260px]">
              <h3 className="text-base lg:text-lg font-semibold text-gray-900 mb-3 lg:mb-3">Districts Overview</h3>
              
              <div className="space-y-2 lg:space-y-3 max-h-64 lg:max-h-80 overflow-y-auto custom-scrollbar">
                {filteredDistricts.map(([name, data], index) => (
                  <div
                    key={name}
                        className="p-3 lg:p-3 bg-gray-50 rounded-md hover:bg-gray-100 cursor-pointer transition-all duration-200 border border-gray-200 hover:border-gray-300 hover:shadow"
                    onClick={() => setSelectedDistrict({ name, ...data })}
                  >
                  <div className="flex justify-between items-center mb-2 lg:mb-3">
                        <h4 className="font-semibold text-gray-900 text-sm lg:text-base">{name}</h4>
                        <span className={`px-2 lg:px-3 py-0.5 lg:py-1.5 rounded-full text-xs lg:text-sm font-medium ${getRiskColorClass(data.risk)}`}>
                      {data.risk.charAt(0).toUpperCase() + data.risk.slice(1)}
                    </span>
                  </div>
                      <div className="text-xs lg:text-sm text-gray-600 mb-2 lg:mb-3">
                        Outage Probability: <span className="font-semibold text-sm lg:text-base">{data.outageProb}%</span>
                  </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 lg:h-3">
                    <div
                          className="h-2 lg:h-3 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${data.outageProb}%`,
                        backgroundColor: getRiskColor(data.risk)
                      }}
                    ></div>
                  </div>
                </div>
              ))}
              </div>
            </div>

            {selectedDistrict && (
              <div
                className="p-4 bg-blue-50 rounded-lg border border-blue-200"
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-blue-900 text-lg">
                    {selectedDistrict.name} Details
                  </h4>
                  <Link
                    to="/advisory"
                    state={{ district: selectedDistrict.name }}
                    className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors text-sm"
                  >
                    View Alerts
                  </Link>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center py-2">
                    <span className="text-blue-700 font-medium text-sm">Risk Level:</span>
                    <span className="font-semibold text-blue-900 text-sm">
                      {selectedDistrict.risk.charAt(0).toUpperCase() + selectedDistrict.risk.slice(1)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-blue-700 font-medium text-sm">Outage Probability:</span>
                    <span className="font-semibold text-blue-900 text-base">{selectedDistrict.outageProb}%</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-blue-700 font-medium text-sm">Population:</span>
                    <span className="font-semibold text-blue-900 text-sm">
                      {selectedDistrict.population.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-blue-700 font-medium text-sm">Estimated Affected:</span>
                    <span className="font-semibold text-blue-900 text-sm">
                      {Math.round(selectedDistrict.population * selectedDistrict.outageProb / 100).toLocaleString()}
                    </span>
                  </div>
                  
                  {/* Preparedness Tips */}
                  <div className="mt-3 p-3 bg-white rounded-md border border-blue-200">
                    <h5 className="font-semibold text-blue-900 mb-2 text-sm">Preparedness Tips:</h5>
                    <ul className="text-blue-800 space-y-1 text-sm">
                      <li>• Keep emergency supplies ready</li>
                      <li>• Charge essential devices</li>
                      <li>• Have backup lighting available</li>
                      <li>• Monitor updates regularly</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Legend and Map Controls */}
      <div className="max-w-7xl mx-auto mt-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Level Legend</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-8 h-8 bg-red-500 rounded-full border-2 border-white shadow-md"></div>
              <div>
                <div className="font-semibold text-gray-900 text-sm">High Risk</div>
                <div className="text-xs text-gray-600">70%+ outage probability</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-8 h-8 bg-yellow-500 rounded-full border-2 border-white shadow-md"></div>
              <div>
                <div className="font-semibold text-gray-900 text-sm">Medium Risk</div>
                <div className="text-xs text-gray-600">30-70% outage probability</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-8 h-8 bg-green-500 rounded-full border-2 border-white shadow-md"></div>
              <div>
                <div className="font-semibold text-gray-900 text-sm">Low Risk</div>
                <div className="text-xs text-gray-600">0-30% outage probability</div>
              </div>
            </div>
          </div>
  </div>

  <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Map Instructions</h3>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="w-2.5 h-2.5 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></div>
              <div className="text-gray-700 text-sm">Click on district markers for detailed information</div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2.5 h-2.5 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></div>
              <div className="text-gray-700 text-sm">Use time filter to adjust prediction window</div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2.5 h-2.5 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></div>
              <div className="text-gray-700 text-sm">Filter by risk level to focus on specific areas</div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2.5 h-2.5 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></div>
              <div className="text-gray-700 text-sm">Real-time updates every 15 minutes</div>
            </div>
          </div>
          
          <div className="mt-6 pt-4 border-t border-gray-200">
            <button
              onClick={() => navigate('/advisory')}
              className="w-full py-2.5 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-medium rounded-md transition-all duration-200 shadow hover:shadow-md text-sm"
            >
              Access Public Advisory & Alerts →
            </button>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionMap;
