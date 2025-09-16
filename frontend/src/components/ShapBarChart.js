import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function ShapBarChart({ shapValues }) {
  if (!shapValues || shapValues.length === 0) return null;

  const labels = shapValues.map(f => f.feature);
  const data = {
    labels,
    datasets: [
      {
        label: 'SHAP Value',
        data: shapValues.map(f => f.value),
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: 'Feature Attribution (SHAP)',
        color: '#1e293b',
        font: { size: 18 },
      },
      tooltip: {
        callbacks: {
          label: ctx => `Impact: ${ctx.parsed.x.toFixed(3)}`,
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: 'SHAP Value', color: '#1e293b' },
        grid: { color: '#e5e7eb' },
      },
      y: {
        title: { display: true, text: 'Feature', color: '#1e293b' },
        grid: { color: '#e5e7eb' },
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow border p-4 my-4">
      <Bar data={data} options={options} height={300} />
    </div>
  );
}

export default ShapBarChart;
