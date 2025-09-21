import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';
import { useQuery } from 'react-query';
import ShapBarChart from '../components/charts/ShapBarChart';

function WhatIfSimulator() {
  const [scenario, setScenario] = useState({
    weather: {
      temperature: 25,
      humidity: 60,
      windSpeed: 10,
      precipitation: 0,
      stormProbability: 0
    },
    grid: {
      loadFactor: 75,
      maintenanceScheduled: false,
      gridStability: 95
    },
    external: {
      publicHoliday: false,
      majorEvent: false,
      season: 'summer'
    }
  });

  const [results, setResults] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const runSimulation = async () => {
    setIsSimulating(true);
    try {
      // In a real application, we would use:
      // const response = await apiService.runWhatIfSimulation(scenario);
      
      // For the demo, we'll generate mock data based on the scenario
      const mockResponse = generateMockResults(scenario);
      setResults(mockResponse);
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setTimeout(() => {
        setIsSimulating(false);
      }, 1000); // Add a slight delay to simulate API call
    }
  };

  // Generate mock results based on the input scenario
  const generateMockResults = (scenario) => {
    // Calculate a base probability based on the scenario
    let baseProbability = 0.2; // Start with a base probability
    
    // Weather factors
    const temperatureImpact = (scenario.weather.temperature - 25) * 0.005;
    const humidityImpact = (scenario.weather.humidity - 60) * 0.002;
    const windSpeedImpact = scenario.weather.windSpeed * 0.005;
    const precipitationImpact = scenario.weather.precipitation * 0.003;
    const stormImpact = scenario.weather.stormProbability * 0.008;
    
    // Grid factors
    const loadFactorImpact = (scenario.grid.loadFactor - 75) * 0.004;
    const maintenanceImpact = scenario.grid.maintenanceScheduled ? 0.1 : 0;
    const stabilityImpact = (100 - scenario.grid.gridStability) * 0.005;
    
    // External factors
    const seasonImpact = {
      'summer': 0.05,
      'monsoon': 0.15,
      'winter': 0.02,
      'spring': 0.01
    }[scenario.external.season];
    
    const holidayImpact = scenario.external.publicHoliday ? 0.03 : 0;
    const eventImpact = scenario.external.majorEvent ? 0.04 : 0;
    
    // Sum all impacts to get the final probability
    const outageProbability = Math.min(0.95, Math.max(0.05, baseProbability + 
      temperatureImpact + humidityImpact + windSpeedImpact + precipitationImpact + stormImpact +
      loadFactorImpact + maintenanceImpact + stabilityImpact + 
      seasonImpact + holidayImpact + eventImpact));
    
    // Determine risk level based on the probability
    let riskLevel;
    if (outageProbability < 0.3) riskLevel = 'Low';
    else if (outageProbability < 0.6) riskLevel = 'Medium';
    else if (outageProbability < 0.8) riskLevel = 'High';
    else riskLevel = 'Severe';
    
    // Generate fake SHAP values
    const shapValues = [
      { feature: 'temperature', value: temperatureImpact * 2, originalValue: scenario.weather.temperature + '°C' },
      { feature: 'humidity', value: humidityImpact * 2, originalValue: scenario.weather.humidity + '%' },
      { feature: 'wind_speed', value: windSpeedImpact * 2, originalValue: scenario.weather.windSpeed + ' km/h' },
      { feature: 'precipitation', value: precipitationImpact * 2, originalValue: scenario.weather.precipitation + ' mm' },
      { feature: 'storm_probability', value: stormImpact * 2, originalValue: scenario.weather.stormProbability + '%' },
      { feature: 'load_factor', value: loadFactorImpact * 2, originalValue: scenario.grid.loadFactor + '%' },
      { feature: 'maintenance_scheduled', value: maintenanceImpact * 2, originalValue: scenario.grid.maintenanceScheduled ? 'Yes' : 'No' },
      { feature: 'grid_stability', value: -stabilityImpact * 2, originalValue: scenario.grid.gridStability + '%' },
      { feature: 'season', value: seasonImpact * 2, originalValue: scenario.external.season.charAt(0).toUpperCase() + scenario.external.season.slice(1) },
      { feature: 'public_holiday', value: holidayImpact * 2, originalValue: scenario.external.publicHoliday ? 'Yes' : 'No' },
      { feature: 'major_event', value: eventImpact * 2, originalValue: scenario.external.majorEvent ? 'Yes' : 'No' },
      { feature: 'time_of_day', value: -0.02, originalValue: 'Afternoon' },
      { feature: 'historical_outages', value: 0.03, originalValue: 'Moderate' },
      { feature: 'equipment_age', value: 0.05, originalValue: '8 years' },
      { feature: 'grid_type', value: -0.01, originalValue: 'Urban' },
      { feature: 'vegetation_density', value: 0.02, originalValue: 'Medium' }
    ];
    
    // Sort SHAP values by absolute magnitude
    shapValues.sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
    
    // Generate contributing factors based on the top SHAP values
    const contributingFactors = shapValues
      .slice(0, 5)
      .map(item => ({
        factor: item.feature.replace(/_/g, ' '),
        impact: item.value
      }));
    
    // Generate recommendations based on the scenario
    const recommendations = [];
    
    if (windSpeedImpact > 0.05) {
      recommendations.push('Secure loose equipment and inspect overhead lines due to high wind conditions');
    }
    
    if (precipitationImpact > 0.1) {
      recommendations.push('Monitor drainage systems and consider proactive measures for flood protection');
    }
    
    if (stormImpact > 0.2) {
      recommendations.push('Deploy additional maintenance crews and prepare for potential lightning damage to transformers');
    }
    
    if (loadFactorImpact > 0.05) {
      recommendations.push('Implement load shedding protocols to reduce grid stress during peak hours');
    }
    
    if (maintenanceImpact > 0.05) {
      recommendations.push('Reschedule non-critical maintenance to improve system resilience');
    }
    
    if (outageProbability > 0.6) {
      recommendations.push('Activate emergency response teams and ensure backup systems are operational');
    }
    
    if (recommendations.length === 0) {
      recommendations.push('Continue routine monitoring of system parameters');
      recommendations.push('Ensure preventive maintenance schedules are up to date');
    }
    
    return {
      outage_probability: outageProbability,
      risk_level: riskLevel,
      confidence_score: 85 + Math.random() * 10,
      contributing_factors: contributingFactors,
      shap_values: shapValues,
      recommendations: recommendations,
      base_value: 0.2,
      predicted_value: outageProbability
    };
  };

  const resetScenario = () => {
    setScenario({
      weather: {
        temperature: 25,
        humidity: 60,
        windSpeed: 10,
        precipitation: 0,
        stormProbability: 0
      },
      grid: {
        loadFactor: 75,
        maintenanceScheduled: false,
        gridStability: 95
      },
      external: {
        publicHoliday: false,
        majorEvent: false,
        season: 'summer'
      }
    });
    setResults(null);
  };

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

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">What-If Simulator</h1>
          <p className="text-neutral-600 mt-1">
            Test different scenarios to understand their impact on power outage risk
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={resetScenario}
            className="px-4 py-2 border border-neutral-300 rounded-md text-neutral-700 hover:bg-neutral-50 transition-colors"
          >
            Reset
          </button>
          <button
            onClick={runSimulation}
            disabled={isSimulating}
            className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {isSimulating ? 'Simulating...' : 'Run Simulation'}
          </button>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scenario Configuration */}
        <div className="space-y-6">
          {/* Weather Parameters */}
          <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Weather Conditions</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Temperature: {scenario.weather.temperature}°C
                </label>
                <input
                  type="range"
                  min="10"
                  max="45"
                  value={scenario.weather.temperature}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    weather: { ...prev.weather, temperature: parseInt(e.target.value) }
                  }))}
                  className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Humidity: {scenario.weather.humidity}%
                </label>
                <input
                  type="range"
                  min="20"
                  max="100"
                  value={scenario.weather.humidity}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    weather: { ...prev.weather, humidity: parseInt(e.target.value) }
                  }))}
                  className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Wind Speed: {scenario.weather.windSpeed} km/h
                </label>
                <input
                  type="range"
                  min="0"
                  max="60"
                  value={scenario.weather.windSpeed}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    weather: { ...prev.weather, windSpeed: parseInt(e.target.value) }
                  }))}
                  className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Precipitation: {scenario.weather.precipitation} mm
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={scenario.weather.precipitation}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    weather: { ...prev.weather, precipitation: parseInt(e.target.value) }
                  }))}
                  className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Storm Probability: {scenario.weather.stormProbability}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={scenario.weather.stormProbability}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    weather: { ...prev.weather, stormProbability: parseInt(e.target.value) }
                  }))}
                  className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
          </motion.div>

          {/* Grid Parameters */}
          <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Grid Conditions</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Load Factor: {scenario.grid.loadFactor}%
                </label>
                <input
                  type="range"
                  min="30"
                  max="100"
                  value={scenario.grid.loadFactor}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    grid: { ...prev.grid, loadFactor: parseInt(e.target.value) }
                  }))}
                  className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Grid Stability: {scenario.grid.gridStability}%
                </label>
                <input
                  type="range"
                  min="60"
                  max="100"
                  value={scenario.grid.gridStability}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    grid: { ...prev.grid, gridStability: parseInt(e.target.value) }
                  }))}
                  className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={scenario.grid.maintenanceScheduled}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    grid: { ...prev.grid, maintenanceScheduled: e.target.checked }
                  }))}
                  className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                />
                <label className="ml-2 text-sm text-neutral-700">Maintenance Scheduled</label>
              </div>
            </div>
          </motion.div>

          {/* External Factors */}
          <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">External Factors</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">Season</label>
                <select
                  value={scenario.external.season}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    external: { ...prev.external, season: e.target.value }
                  }))}
                  className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="summer">Summer</option>
                  <option value="monsoon">Monsoon</option>
                  <option value="winter">Winter</option>
                  <option value="spring">Spring</option>
                </select>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={scenario.external.publicHoliday}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    external: { ...prev.external, publicHoliday: e.target.checked }
                  }))}
                  className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                />
                <label className="ml-2 text-sm text-neutral-700">Public Holiday</label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={scenario.external.majorEvent}
                  onChange={(e) => setScenario(prev => ({
                    ...prev,
                    external: { ...prev.external, majorEvent: e.target.checked }
                  }))}
                  className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                />
                <label className="ml-2 text-sm text-neutral-700">Major Event/Festival</label>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Results */}
        <div className="space-y-6">
          <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Simulation Results</h3>
            {results ? (
              <div className="space-y-4">
                <div className="text-center p-6 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg">
                  <div className="text-3xl font-bold text-blue-900">
                    {(results.outage_probability * 100).toFixed(1)}%
                  </div>
                  <p className="text-blue-700 mt-1">Outage Probability</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-neutral-50 rounded-lg">
                    <div className="text-lg font-semibold text-neutral-900">
                      {results.risk_level}
                    </div>
                    <p className="text-sm text-neutral-600">Risk Level</p>
                  </div>
                  <div className="text-center p-4 bg-neutral-50 rounded-lg">
                    <div className="text-lg font-semibold text-neutral-900">
                      {results.confidence_score.toFixed(1)}%
                    </div>
                    <p className="text-sm text-neutral-600">Confidence</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <h4 className="font-medium text-neutral-900">Contributing Factors</h4>
                  {results.contributing_factors?.map((factor, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-neutral-50 rounded-lg">
                      <span className="text-sm text-neutral-700">{factor.feature || factor.factor}</span>
                      <span className={`text-sm font-medium ${
                        factor.impact > 0 ? 'text-red-600' : 'text-green-600'
                      }`}>
                        {factor.impact > 0 ? '+' : ''}{(factor.impact * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
                {/* SHAP Bar Chart Visualization */}
                {results.shap_values && results.shap_values.length > 0 && (
                  <ShapBarChart 
                    shapValues={results.shap_values} 
                    predictedValue={results.predicted_value}
                    baseValue={results.base_value}
                  />
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-neutral-500">
                <div className="text-xl mb-2">
                  <svg className="w-8 h-8 mx-auto text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p>Configure scenario parameters and run simulation to see results</p>
              </div>
            )}
          </motion.div>

          {/* Recommendations */}
          {results && (
            <motion.div variants={itemVariants} className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">Recommendations</h3>
              <div className="space-y-3">
                {results.recommendations?.map((rec, index) => (
                  <div key={index} className="flex items-start p-3 bg-blue-50 rounded-lg">
                    <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <p className="ml-3 text-sm text-blue-800">{rec}</p>
                  </div>
                )) || [
                  <div className="flex items-start p-3 bg-blue-50 rounded-lg">
                    <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <p className="ml-3 text-sm text-blue-800">Monitor weather conditions closely</p>
                  </div>,
                  <div className="flex items-start p-3 bg-blue-50 rounded-lg">
                    <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <p className="ml-3 text-sm text-blue-800">Ensure backup systems are ready</p>
                  </div>
                ]}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export default WhatIfSimulator;
