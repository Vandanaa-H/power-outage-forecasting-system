import React from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';

function RiskMetricsCard() {
  const { data: riskData, isLoading } = useQuery(
    ['risk-metrics'],
    () => apiService.getRiskMetrics(),
    {
      refetchInterval: 60000, // Refresh every minute
    }
  );

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const mockData = {
    overall_risk: 'Medium',
    risk_score: 67,
    districts: [
      { name: 'Bangalore Urban', risk: 'High', score: 85 },
      { name: 'Mysore', risk: 'Medium', score: 62 },
      { name: 'Mangalore', risk: 'Low', score: 35 },
      { name: 'Hubli', risk: 'Medium', score: 58 }
    ]
  };

  const getRiskColor = (risk) => {
    switch (risk.toLowerCase()) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-neutral-600 bg-neutral-50';
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-neutral-200 rounded w-1/2"></div>
          <div className="h-32 bg-neutral-200 rounded"></div>
        </div>
      </div>
    );
  }

  const data = riskData || mockData;

  return (
    <motion.div
      variants={itemVariants}
      className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6"
    >
      <h3 className="text-lg font-semibold text-neutral-900 mb-4">Risk Metrics</h3>
      
      {/* Overall Risk */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-neutral-700">Overall Risk Level</span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(data.overall_risk)}`}>
            {data.overall_risk}
          </span>
        </div>
        <div className="w-full bg-neutral-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all duration-500 ${
              data.risk_score >= 80 ? 'bg-red-500' :
              data.risk_score >= 50 ? 'bg-yellow-500' :
              'bg-green-500'
            }`}
            style={{ width: `${data.risk_score}%` }}
          ></div>
        </div>
        <div className="flex justify-between text-xs text-neutral-600 mt-1">
          <span>Low</span>
          <span>High</span>
        </div>
      </div>

      {/* District Breakdown */}
      <div>
        <h4 className="text-sm font-medium text-neutral-700 mb-3">District Risk Breakdown</h4>
        <div className="space-y-3">
          {data.districts.map((district, index) => (
            <div key={district.name} className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-900">{district.name}</p>
                <div className="w-24 bg-neutral-200 rounded-full h-2 mt-1">
                  <div 
                    className={`h-2 rounded-full ${
                      district.score >= 80 ? 'bg-red-500' :
                      district.score >= 50 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${district.score}%` }}
                  ></div>
                </div>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(district.risk)}`}>
                {district.risk}
              </span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

export default RiskMetricsCard;
