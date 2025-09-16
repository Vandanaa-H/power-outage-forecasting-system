import React, { useState, useEffect, useRef } from 'react';
import { Bar } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';

ChartJS.register(
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend
);

const ShapBarChart = ({ shapValues, predictedValue, baseValue }) => {
  const canvasRef = useRef(null);
  const [chartData, setChartData] = useState(null);
  
  // Sort the SHAP values by absolute magnitude for better visualization
  const sortedShapValues = shapValues ? 
    [...shapValues].sort((a, b) => Math.abs(b.value) - Math.abs(a.value)) : 
    [];

  // Process SHAP values and prepare chart data
  useEffect(() => {
    if (!shapValues || shapValues.length === 0) return;

    // Get top 10 features by impact
    const topFeatures = sortedShapValues.slice(0, 10);
    
    // Prepare data for the chart
    const data = {
      labels: topFeatures.map(item => formatFeatureName(item.feature)),
      datasets: [
        {
          label: 'SHAP Value (Impact)',
          data: topFeatures.map(item => item.value),
          backgroundColor: topFeatures.map(item => 
            item.value >= 0 ? 'rgba(52, 152, 219, 0.7)' : 'rgba(231, 76, 60, 0.7)'
          ),
          borderColor: topFeatures.map(item => 
            item.value >= 0 ? 'rgba(52, 152, 219, 1)' : 'rgba(231, 76, 60, 1)'
          ),
          borderWidth: 1,
          borderRadius: 4
        }
      ]
    };

    setChartData(data);
  }, [shapValues]);

  // Format feature names for better readability
  const formatFeatureName = (name) => {
    // Replace underscores with spaces and capitalize each word
    return name
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Chart options
  const options = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          boxWidth: 15,
          usePointStyle: true,
          pointStyle: 'rect'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#1f2937',
        bodyColor: '#4b5563',
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 13
        },
        padding: 12,
        boxWidth: 10,
        boxHeight: 10,
        usePointStyle: true,
        borderColor: 'rgba(0, 0, 0, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          title: function(tooltipItems) {
            return formatFeatureName(sortedShapValues[tooltipItems[0].dataIndex].feature);
          },
          label: function(context) {
            const value = context.parsed.x;
            const impact = value >= 0 ? 'Increases' : 'Decreases';
            const magnitude = Math.abs(value).toFixed(4);
            return `${impact} outage probability by ${magnitude}`;
          },
          afterLabel: function(context) {
            const feature = sortedShapValues[context.dataIndex].feature;
            const featureValue = sortedShapValues[context.dataIndex].originalValue;
            return `Current value: ${featureValue}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
          borderDash: [5, 5]
        },
        ticks: {
          font: {
            size: 11
          },
          color: '#6b7280',
          callback: function(value) {
            return value.toFixed(3);
          }
        },
        title: {
          display: true,
          text: 'SHAP Value (Feature Impact)',
          color: '#6b7280',
          font: {
            size: 12,
            weight: 'normal'
          },
          padding: {top: 10, bottom: 0}
        }
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
          borderDash: [5, 5]
        },
        ticks: {
          font: {
            size: 11
          },
          color: '#6b7280'
        }
      }
    }
  };

  return (
    <div className="relative">
      <div className="h-96">
        {chartData ? (
          <Bar ref={canvasRef} data={chartData} options={options} />
        ) : (
          <div className="flex items-center justify-center h-full bg-gray-50 rounded-lg">
            <p className="text-gray-500">No SHAP values available</p>
          </div>
        )}
      </div>

      {predictedValue !== undefined && baseValue !== undefined && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Base Value (Average Prediction)</p>
              <p className="text-xl font-semibold">{baseValue.toFixed(4)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Current Prediction</p>
              <p className={`text-xl font-semibold ${
                predictedValue > baseValue ? 'text-red-600' : 'text-green-600'
              }`}>
                {predictedValue.toFixed(4)}
                <span className="text-sm font-normal ml-2">
                  ({predictedValue > baseValue ? '+' : ''}{(predictedValue - baseValue).toFixed(4)})
                </span>
              </p>
            </div>
          </div>
          
          <div className="mt-3">
            <p className="text-sm text-gray-600 mb-1">Outage Probability</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className={`h-2.5 rounded-full ${
                  predictedValue > 0.75 ? 'bg-red-600' :
                  predictedValue > 0.5 ? 'bg-orange-500' :
                  predictedValue > 0.25 ? 'bg-yellow-500' :
                  'bg-green-600'
                }`} 
                style={{ width: `${predictedValue * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between mt-1 text-xs text-gray-500">
              <span>Low (0.0)</span>
              <span>Medium (0.5)</span>
              <span>High (1.0)</span>
            </div>
          </div>
        </div>
      )}

      {shapValues && shapValues.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">How to interpret this chart:</h4>
          <ul className="text-sm text-gray-600 space-y-1 list-disc pl-5">
            <li>Blue bars show features that <span className="text-blue-600 font-medium">increase</span> the probability of a power outage</li>
            <li>Red bars show features that <span className="text-red-600 font-medium">decrease</span> the probability of a power outage</li>
            <li>Longer bars indicate stronger impact on the prediction</li>
            <li>The base value represents the average prediction for all data points</li>
            <li>Your current prediction shows how the specific input values affect the outcome</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ShapBarChart;