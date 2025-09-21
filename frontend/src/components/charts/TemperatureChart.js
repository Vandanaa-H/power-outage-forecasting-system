import React from 'react';
import { Line } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend,
  Filler 
} from 'chart.js';

ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend,
  Filler
);

const TemperatureChart = ({ weatherData }) => {
  // Transform forecast data to chart format
  let processedData;
  
  if (weatherData && weatherData.items) {
    // Real forecast data from API
    const items = weatherData.items.slice(0, 8); // Get first 8 hours
    processedData = {
      labels: items.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: false 
        });
      }),
      temperatures: items.map(item => Math.round(item.temperature * 10) / 10),
      minTemp: Math.min(...items.map(item => item.temperature)),
      maxTemp: Math.max(...items.map(item => item.temperature))
    };
  } else {
    // Fallback data
    processedData = {
      labels: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
      temperatures: [24, 23, 22, 25, 28, 30, 29, 26],
      minTemp: 22,
      maxTemp: 30
    };
  }

  const data = processedData;

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: 'Temperature (°C)',
        data: data.temperatures,
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: 'rgb(239, 68, 68)',
        pointRadius: 4,
        pointHoverRadius: 6
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
          pointStyle: 'circle',
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
            return `Temperature: ${context.parsed.y}°C`;
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
          color: '#6b7280'
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
          color: '#6b7280',
          callback: function(value) {
            return value + '°C';
          }
        },
        min: Math.max(0, (data.minTemp || 20) - 5),
        max: (data.maxTemp || 35) + 5,
      }
    },
    interaction: {
      mode: 'index',
      intersect: false,
    },
    elements: {
      line: {
        tension: 0.4
      }
    }
  };

  return (
    <div className="h-64 w-full">
      <Line data={chartData} options={options} />
      
      {/* Temperature Stats */}
      <div className="flex justify-between mt-4 text-sm">
        <div>
          <span className="text-neutral-500">Min:</span> 
          <span className="ml-1 font-medium text-blue-600">{data.minTemp || 22}°C</span>
        </div>
        <div>
          <span className="text-neutral-500">Avg:</span>
          <span className="ml-1 font-medium text-purple-600">
            {Math.round(((data.temperatures || []).reduce((a, b) => a + b, 0) / (data.temperatures || []).length) * 10) / 10}°C
          </span>
        </div>
        <div>
          <span className="text-neutral-500">Max:</span>
          <span className="ml-1 font-medium text-red-600">{data.maxTemp || 30}°C</span>
        </div>
      </div>
    </div>
  );
};

export default TemperatureChart;