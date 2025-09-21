import React from 'react';
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

const PrecipitationChart = ({ weatherData }) => {
  // Transform forecast data to chart format
  let processedData;
  
  if (weatherData && weatherData.items) {
    // Real forecast data from API
    const items = weatherData.items.slice(0, 8);
    processedData = {
      labels: items.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: false 
        });
      }),
      precipitation: items.map(item => Math.round((item.rainfall || 0) * 10) / 10),
      maxPrecipitation: Math.max(...items.map(item => item.rainfall || 0))
    };
  } else {
    // Fallback data for demo stability
    processedData = {
      labels: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
      precipitation: [0, 0.5, 1.2, 0, 0, 2.1, 0.8, 0],
      maxPrecipitation: 2.1
    };
  }

  const data = processedData;
  
  const getBarColor = (value) => {
    if (value < 2) return 'rgba(59, 130, 246, 0.7)';
    if (value < 5) return 'rgba(99, 102, 241, 0.7)';
    return 'rgba(67, 56, 202, 0.7)';
  };

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: 'Precipitation (mm)',
        data: data.precipitation,
        backgroundColor: data.precipitation.map(getBarColor),
        borderColor: data.precipitation.map(value => {
          const color = getBarColor(value);
          return color.replace('0.7', '1');
        }),
        borderWidth: 1,
        borderRadius: 4,
        barThickness: 20,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        align: 'end',
        labels: {
          boxWidth: 15,
          usePointStyle: true,
          pointStyle: 'rect',
          font: {
            size: 12
          }
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
          label: function(context) {
            const value = context.parsed.y;
            let intensity = 'No rain';
            
            if (value > 0 && value < 2) intensity = 'Light rain';
            else if (value >= 2 && value < 5) intensity = 'Moderate rain';
            else if (value >= 5) intensity = 'Heavy rain';
            
            return [`Precipitation: ${value} mm`, `Intensity: ${intensity}`];
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
          borderDash: [5, 5],
        },
        ticks: {
          font: {
            size: 11
          },
          color: '#6b7280'
        }
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
          borderDash: [5, 5],
        },
        ticks: {
          font: {
            size: 11
          },
          color: '#6b7280',
          callback: function(value) {
            return value + ' mm';
          }
        },
        min: 0,
        max: Math.max(10, (data.maxPrecipitation || 0) * 1.2),
        title: {
          display: true,
          text: 'Precipitation (mm)',
          color: '#6b7280',
          font: {
            size: 12
          }
        }
      }
    }
  };

  const totalPrecipitation = (data.precipitation || []).reduce((a, b) => a + b, 0);

  return (
    <div className="h-64 w-full">
      <Bar data={chartData} options={options} />
      
      <div className="flex justify-between mt-4 text-sm">
        <div>
          <span className="text-neutral-500">Total:</span> 
          <span className="ml-1 font-medium text-blue-600">{totalPrecipitation.toFixed(1)} mm</span>
        </div>
        <div>
          <span className="text-neutral-500">Max Intensity:</span>
          <span className="ml-1 font-medium text-indigo-600">{(data.maxPrecipitation || 0).toFixed(1)} mm</span>
        </div>
        <div>
          <span className="text-neutral-500">Status:</span>
          <span className={`ml-1 font-medium ${totalPrecipitation > 5 ? 'text-indigo-800' : totalPrecipitation > 1 ? 'text-indigo-600' : 'text-blue-500'}`}>
            {totalPrecipitation > 10 ? 'Heavy Rain' : totalPrecipitation > 5 ? 'Moderate Rain' : totalPrecipitation > 1 ? 'Light Rain' : 'Minimal'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default PrecipitationChart;
