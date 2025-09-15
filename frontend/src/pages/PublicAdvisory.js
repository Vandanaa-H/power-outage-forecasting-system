import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';

function PublicAdvisory() {
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedRegion, setSelectedRegion] = useState('all');

  const { data: advisories, isLoading } = useQuery(
    ['advisories', selectedSeverity, selectedRegion],
    () => apiService.getAdvisories({ 
      severity: selectedSeverity === 'all' ? undefined : selectedSeverity,
      region: selectedRegion === 'all' ? undefined : selectedRegion
    }),
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

  const severityColors = {
    'Critical': 'bg-red-100 text-red-800 border-red-200',
    'High': 'bg-orange-100 text-orange-800 border-orange-200',
    'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'Low': 'bg-green-100 text-green-800 border-green-200',
    'Info': 'bg-blue-100 text-blue-800 border-blue-200'
  };

  const mockAdvisories = [
    {
      id: 1,
      title: 'Thunderstorm Warning - Bangalore Urban',
      description: 'Severe thunderstorms expected in Bangalore Urban district. High probability of power outages due to lightning strikes and strong winds.',
      severity: 'High',
      region: 'Bangalore Urban',
      issued_at: '2024-01-15T14:30:00Z',
      valid_until: '2024-01-15T22:00:00Z',
      affected_areas: ['Electronic City', 'Whitefield', 'Koramangala', 'Indiranagar'],
      recommendations: [
        'Avoid outdoor activities during peak storm hours (6-9 PM)',
        'Charge electronic devices as backup',
        'Keep emergency supplies ready'
      ]
    },
    {
      id: 2,
      title: 'Scheduled Maintenance - Mysore District',
      description: 'Planned maintenance work on major transmission lines. Some areas may experience power interruptions.',
      severity: 'Medium',
      region: 'Mysore',
      issued_at: '2024-01-15T10:00:00Z',
      valid_until: '2024-01-16T06:00:00Z',
      affected_areas: ['Mysore City', 'Srirangapatna', 'Mandya'],
      recommendations: [
        'Plan activities that do not require electricity',
        'Use UPS/backup systems if available',
        'Report any extended outages to MESCOM'
      ]
    },
    {
      id: 3,
      title: 'Heat Wave Alert - Northern Districts',
      description: 'Extreme temperatures expected to increase power demand. Possible strain on grid infrastructure.',
      severity: 'Medium',
      region: 'Belgaum',
      issued_at: '2024-01-15T08:00:00Z',
      valid_until: '2024-01-17T20:00:00Z',
      affected_areas: ['Belgaum', 'Bijapur', 'Bagalkot'],
      recommendations: [
        'Use air conditioning efficiently',
        'Avoid peak hour usage (2-6 PM)',
        'Report power quality issues immediately'
      ]
    }
  ];

  const regions = [
    'Bangalore Urban', 'Bangalore Rural', 'Mysore', 'Mandya', 'Hassan',
    'Belgaum', 'Hubli-Dharwad', 'Bijapur', 'Bagalkot', 'Gulbarga',
    'Mangalore', 'Udupi', 'Shimoga', 'Davangere', 'Bellary'
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
          <h1 className="text-3xl font-bold text-neutral-900">Public Advisory</h1>
          <p className="text-neutral-600 mt-1">
            Real-time alerts and recommendations for power outage preparedness
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
            <option value="Info">Info</option>
          </select>
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Regions</option>
            {regions.map(region => (
              <option key={region} value={region}>{region}</option>
            ))}
          </select>
        </div>
      </motion.div>

      {/* Active Alerts Summary */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center text-white font-bold">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.998-.833-2.768 0L3.046 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
            </div>
            <div className="ml-3">
              <p className="text-base font-semibold text-red-800">Critical</p>
              <p className="text-2xl font-bold text-red-900">0</p>
            </div>
          </div>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.998-.833-2.768 0L3.046 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
            </div>
            <div className="ml-3">
              <p className="text-base font-semibold text-orange-800">High</p>
              <p className="text-2xl font-bold text-orange-900">1</p>
            </div>
          </div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center text-white font-bold">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
            <div className="ml-3">
              <p className="text-base font-semibold text-yellow-800">Medium</p>
              <p className="text-2xl font-bold text-yellow-900">2</p>
            </div>
          </div>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="ml-3">
              <p className="text-base font-semibold text-blue-800">Total Active</p>
              <p className="text-2xl font-bold text-blue-900">3</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Advisory List */}
      <div className="space-y-4">
        {mockAdvisories.map((advisory, index) => (
          <motion.div
            key={advisory.id}
            variants={itemVariants}
            className={`border rounded-lg p-6 ${severityColors[advisory.severity]}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-lg font-semibold">{advisory.title}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${severityColors[advisory.severity]}`}>
                    {advisory.severity}
                  </span>
                </div>
                <p className="text-sm mb-3">{advisory.description}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-xs font-medium mb-1">Issued:</p>
                    <p className="text-sm">{new Date(advisory.issued_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium mb-1">Valid Until:</p>
                    <p className="text-sm">{new Date(advisory.valid_until).toLocaleString()}</p>
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-xs font-medium mb-2">Affected Areas:</p>
                  <div className="flex flex-wrap gap-2">
                    {advisory.affected_areas.map((area, idx) => (
                      <span key={idx} className="px-2 py-1 bg-white bg-opacity-50 rounded text-xs">
                        {area}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-xs font-medium mb-2">Recommendations:</p>
                  <ul className="text-sm space-y-1">
                    {advisory.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-xs mr-2">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Emergency Contacts */}
      <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Emergency Contacts</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-neutral-50 rounded-lg">
            <h4 className="font-medium text-neutral-900">BESCOM</h4>
            <p className="text-sm text-neutral-600">Bangalore</p>
            <p className="text-lg font-bold text-primary-600">1912</p>
          </div>
          <div className="text-center p-4 bg-neutral-50 rounded-lg">
            <h4 className="font-medium text-neutral-900">MESCOM</h4>
            <p className="text-sm text-neutral-600">Mangalore</p>
            <p className="text-lg font-bold text-primary-600">1912</p>
          </div>
          <div className="text-center p-4 bg-neutral-50 rounded-lg">
            <h4 className="font-medium text-neutral-900">HESCOM</h4>
            <p className="text-sm text-neutral-600">Hubli</p>
            <p className="text-lg font-bold text-primary-600">1912</p>
          </div>
          <div className="text-center p-4 bg-neutral-50 rounded-lg">
            <h4 className="font-medium text-neutral-900">GESCOM</h4>
            <p className="text-sm text-neutral-600">Gulbarga</p>
            <p className="text-lg font-bold text-primary-600">1912</p>
          </div>
        </div>
      </motion.div>

      {/* Preparedness Tips */}
      <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Power Outage Preparedness Tips</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-neutral-900 mb-3">Before an Outage</h4>
            <ul className="space-y-2 text-sm text-neutral-700">
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                <span>Keep flashlights and batteries readily available</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                <span>Charge all electronic devices regularly</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                <span>Store drinking water and non-perishable food</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                <span>Know the location of your circuit breakers</span>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-neutral-900 mb-3">During an Outage</h4>
            <ul className="space-y-2 text-sm text-neutral-700">
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                <span>Report outages to your local electricity board</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                <span>Avoid opening refrigerator and freezer doors</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                <span>Unplug electrical appliances to prevent damage</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                <span>Use generators outdoors only, never indoors</span>
              </li>
            </ul>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default PublicAdvisory;
