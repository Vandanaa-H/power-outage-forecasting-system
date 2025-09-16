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
  Legend 
} from 'chart.js';

ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend
);

const WindChart = ({ weatherData }) => {
  // If no data is provided, use mock data
  const mockData = {
    labels: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
    windSpeed: [10, 15, 25, 30, 40, 35, 20, 15],
    windGust: [15, 25, 35, 45, 55, 50, 30, 25],
    maxWindSpeed: 40,
    maxWindGust: 55
  };

  const data = weatherData || mockData;

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: 'Wind Speed (km/h)',
        data: data.windSpeed,
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.5)',
        borderWidth: 2,
        pointBackgroundColor: 'rgb(34, 197, 94)',
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.4
      },
      {
        label: 'Wind Gust (km/h)',
        data: data.windGust,
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.5)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointBackgroundColor: 'rgb(245, 158, 11)',
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.4
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
            const value = context.parsed.y;
            let description = '';
            
            if (context.dataset.label.includes('Speed')) {
              if (value < 20) description = 'Light breeze';
              else if (value < 40) description = 'Moderate wind';
              else if (value < 60) description = 'Strong wind';
              else description = 'Gale force wind';
              
              return `Wind Speed: ${value} km/h (${description})`;
            } else {
              return `Wind Gust: ${value} km/h`;
            }
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
            return value + ' km/h';
          }
        },
        min: 0,
        max: Math.max(60, Math.max((data.maxWindSpeed || 0), (data.maxWindGust || 0)) * 1.2),
        title: {
          display: true,
          text: 'Wind Speed (km/h)',
          color: '#6b7280',
          font: {
            size: 12
          }
        }
      }
    },
    interaction: {
      mode: 'index',
      intersect: false,
    }
  };

  // Get max wind speed and its description
  const maxWindSpeed = Math.max(...(data.windSpeed || []));
  let windDescription = 'Calm';
  if (maxWindSpeed >= 60) windDescription = 'Gale force';
  else if (maxWindSpeed >= 40) windDescription = 'Strong';
  else if (maxWindSpeed >= 20) windDescription = 'Moderate';
  else if (maxWindSpeed > 0) windDescription = 'Light';

  return (
    <div className="h-64 w-full">
      <Line data={chartData} options={options} />
      
      {/* Wind Stats */}
      <div className="flex justify-between mt-4 text-sm">
        <div>
          <span className="text-neutral-500">Max Wind:</span> 
          <span className="ml-1 font-medium text-green-600">{maxWindSpeed} km/h</span>
        </div>
        <div>
          <span className="text-neutral-500">Max Gust:</span>
          <span className="ml-1 font-medium text-amber-600">{Math.max(...(data.windGust || []))} km/h</span>
        </div>
        <div>
          <span className="text-neutral-500">Condition:</span>
          <span className={`ml-1 font-medium ${
            maxWindSpeed >= 60 ? 'text-red-600' : 
            maxWindSpeed >= 40 ? 'text-amber-600' : 
            maxWindSpeed >= 20 ? 'text-green-600' : 
            'text-blue-600'
          }`}>
            {windDescription}
          </span>
        </div>
      </div>
    </div>
  );
};

export default WindChart;