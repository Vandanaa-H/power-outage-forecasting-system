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

const HumidityChart = ({ weatherData }) => {
  // If no data is provided, use mock data
  const mockData = {
    labels: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
    humidity: [85, 90, 95, 80, 70, 65, 75, 80]
  };

  const data = weatherData || mockData;

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: 'Humidity (%)',
        data: data.humidity,
        borderColor: 'rgb(56, 189, 248)',
        backgroundColor: 'rgba(56, 189, 248, 0.2)',
        fill: true,
        borderWidth: 2,
        pointBackgroundColor: 'rgb(56, 189, 248)',
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
            let condition = '';
            
            if (value < 30) condition = 'Very Dry';
            else if (value < 50) condition = 'Dry';
            else if (value < 70) condition = 'Comfortable';
            else if (value < 90) condition = 'Humid';
            else condition = 'Very Humid';
            
            return [`Humidity: ${value}%`, `Condition: ${condition}`];
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
            return value + '%';
          }
        },
        min: Math.max(0, Math.min(...(data.humidity || [40])) - 10),
        max: Math.min(100, Math.max(...(data.humidity || [80])) + 10),
        title: {
          display: true,
          text: 'Relative Humidity (%)',
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

  // Calculate stats
  const humidityValues = data.humidity || [];
  const avgHumidity = Math.round(humidityValues.reduce((a, b) => a + b, 0) / humidityValues.length);
  const minHumidity = Math.min(...humidityValues);
  const maxHumidity = Math.max(...humidityValues);
  
  // Determine overall humidity condition
  let overallCondition = '';
  if (avgHumidity < 30) overallCondition = 'Very Dry';
  else if (avgHumidity < 50) overallCondition = 'Dry';
  else if (avgHumidity < 70) overallCondition = 'Comfortable';
  else if (avgHumidity < 90) overallCondition = 'Humid';
  else overallCondition = 'Very Humid';

  return (
    <div className="h-64 w-full">
      <Line data={chartData} options={options} />
      
      {/* Humidity Stats */}
      <div className="flex justify-between mt-4 text-sm">
        <div>
          <span className="text-neutral-500">Min:</span> 
          <span className="ml-1 font-medium text-blue-600">{minHumidity}%</span>
        </div>
        <div>
          <span className="text-neutral-500">Avg:</span>
          <span className="ml-1 font-medium text-sky-600">{avgHumidity}%</span>
        </div>
        <div>
          <span className="text-neutral-500">Max:</span>
          <span className="ml-1 font-medium text-cyan-600">{maxHumidity}%</span>
        </div>
        <div>
          <span className="text-neutral-500">Condition:</span>
          <span className={`ml-1 font-medium ${
            avgHumidity >= 90 ? 'text-blue-800' : 
            avgHumidity >= 70 ? 'text-blue-600' : 
            avgHumidity >= 50 ? 'text-green-600' : 
            avgHumidity >= 30 ? 'text-amber-600' : 
            'text-red-600'
          }`}>
            {overallCondition}
          </span>
        </div>
      </div>
    </div>
  );
};

export default HumidityChart;