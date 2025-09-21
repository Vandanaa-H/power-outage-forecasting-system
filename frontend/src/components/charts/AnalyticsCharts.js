import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// Mock data for charts
const accuracyData = [
  { date: '1/15', accuracy: 96.2, predictions: 45, alerts: 3 },
  { date: '1/14', accuracy: 94.8, predictions: 52, alerts: 5 },
  { date: '1/13', accuracy: 95.1, predictions: 38, alerts: 2 },
  { date: '1/12', accuracy: 97.3, predictions: 41, alerts: 4 },
  { date: '1/11', accuracy: 93.9, predictions: 48, alerts: 6 },
  { date: '1/10', accuracy: 95.5, predictions: 35, alerts: 3 },
  { date: '1/9', accuracy: 96.8, predictions: 42, alerts: 2 }
];

const predictionVolumeData = [
  { time: '00:00', predictions: 12, successful: 11 },
  { time: '04:00', predictions: 8, successful: 8 },
  { time: '08:00', predictions: 25, successful: 23 },
  { time: '12:00', predictions: 35, successful: 32 },
  { time: '16:00', predictions: 28, successful: 26 },
  { time: '20:00', predictions: 22, successful: 21 }
];

const riskDistributionData = [
  { name: 'Low Risk', value: 65, color: '#10B981' },
  { name: 'Medium Risk', value: 25, color: '#F59E0B' },
  { name: 'High Risk', value: 8, color: '#EF4444' },
  { name: 'Critical Risk', value: 2, color: '#DC2626' }
];

const responseTimeData = [
  { date: '1/15', avgTime: 1.2, p95Time: 2.1 },
  { date: '1/14', avgTime: 1.5, p95Time: 2.8 },
  { date: '1/13', avgTime: 1.1, p95Time: 1.9 },
  { date: '1/12', avgTime: 1.3, p95Time: 2.3 },
  { date: '1/11', avgTime: 1.6, p95Time: 3.1 },
  { date: '1/10', avgTime: 1.4, p95Time: 2.5 },
  { date: '1/9', avgTime: 1.0, p95Time: 1.8 }
];

export const ModelAccuracyChart = () => (
  <ResponsiveContainer width="100%" height={320}>
    <LineChart data={accuracyData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
      <XAxis 
        dataKey="date" 
        stroke="#6B7280"
        fontSize={14}
        fontWeight={500}
      />
      <YAxis 
        domain={[90, 100]}
        stroke="#6B7280"
        fontSize={14}
        fontWeight={500}
      />
      <Tooltip 
        contentStyle={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        }}
      />
      <Legend />
      <Line 
        type="monotone" 
        dataKey="accuracy" 
        stroke="#3B82F6" 
        strokeWidth={3}
        dot={{ fill: '#3B82F6', strokeWidth: 2, r: 6 }}
        activeDot={{ r: 8, stroke: '#3B82F6', strokeWidth: 2 }}
        name="Model Accuracy (%)"
      />
    </LineChart>
  </ResponsiveContainer>
);

export const PredictionVolumeChart = () => (
  <ResponsiveContainer width="100%" height={320}>
    <AreaChart data={predictionVolumeData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
      <XAxis 
        dataKey="time"
        stroke="#6B7280"
        fontSize={14}
        fontWeight={500}
      />
      <YAxis 
        stroke="#6B7280"
        fontSize={14}
        fontWeight={500}
      />
      <Tooltip 
        contentStyle={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        }}
      />
      <Legend />
      <Area 
        type="monotone" 
        dataKey="predictions" 
        stackId="1"
        stroke="#10B981" 
        fill="#10B981"
        fillOpacity={0.3}
        name="Total Predictions"
      />
      <Area 
        type="monotone" 
        dataKey="successful" 
        stackId="2"
        stroke="#059669" 
        fill="#059669"
        fillOpacity={0.6}
        name="Successful Predictions"
      />
    </AreaChart>
  </ResponsiveContainer>
);

export const RiskDistributionChart = () => (
  <ResponsiveContainer width="100%" height={320}>
    <PieChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
      <Pie
        data={riskDistributionData}
        cx="50%"
        cy="50%"
        labelLine={false}
        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
        outerRadius={100}
        fill="#8884d8"
        dataKey="value"
      >
        {riskDistributionData.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={entry.color} />
        ))}
      </Pie>
      <Tooltip 
        contentStyle={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        }}
      />
      <Legend />
    </PieChart>
  </ResponsiveContainer>
);

export const ResponseTimeChart = () => (
  <ResponsiveContainer width="100%" height={320}>
    <BarChart data={responseTimeData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
      <XAxis 
        dataKey="date"
        stroke="#6B7280"
        fontSize={14}
        fontWeight={500}
      />
      <YAxis 
        stroke="#6B7280"
        fontSize={14}
        fontWeight={500}
      />
      <Tooltip 
        contentStyle={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        }}
      />
      <Legend />
      <Bar 
        dataKey="avgTime" 
        fill="#8B5CF6" 
        name="Average Response Time (s)"
        radius={[4, 4, 0, 0]}
      />
      <Bar 
        dataKey="p95Time" 
        fill="#A78BFA" 
        name="95th Percentile (s)"
        radius={[4, 4, 0, 0]}
      />
    </BarChart>
  </ResponsiveContainer>
);

export const PredictionTrendsChart = () => (
  <ResponsiveContainer width="100%" height={320}>
    <LineChart data={accuracyData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
      <XAxis 
        dataKey="date"
        stroke="#6B7280"
        fontSize={14}
        fontWeight={500}
      />
      <YAxis 
        stroke="#6B7280"
        fontSize={14}
        fontWeight={500}
      />
      <Tooltip 
        contentStyle={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        }}
      />
      <Legend />
      <Line 
        type="monotone" 
        dataKey="predictions" 
        stroke="#F59E0B" 
        strokeWidth={3}
        dot={{ fill: '#F59E0B', strokeWidth: 2, r: 6 }}
        name="Daily Predictions"
      />
      <Line 
        type="monotone" 
        dataKey="alerts" 
        stroke="#EF4444" 
        strokeWidth={3}
        dot={{ fill: '#EF4444', strokeWidth: 2, r: 6 }}
        name="Alerts Generated"
      />
    </LineChart>
  </ResponsiveContainer>
);