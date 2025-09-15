import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './pages/Dashboard';
import PredictionMap from './pages/PredictionMap';
import WeatherData from './pages/WeatherData';
import Analytics from './pages/Analytics';
import WhatIfSimulator from './pages/WhatIfSimulator';
import PublicAdvisory from './pages/PublicAdvisory';
import Settings from './pages/Settings';
import useStore from './store/useStore';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds
    },
  },
});

function App() {
  const { sidebarOpen } = useStore();

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="flex h-screen bg-neutral-50">
          <Sidebar />
          <div className={`flex-1 flex flex-col transition-all duration-300 ${
            sidebarOpen ? 'ml-64' : 'ml-16'
          }`}>
            <Navbar />
            <main className="flex-1 overflow-auto p-6">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/map" element={<PredictionMap />} />
                <Route path="/weather" element={<WeatherData />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/simulator" element={<WhatIfSimulator />} />
                <Route path="/advisory" element={<PublicAdvisory />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </main>
          </div>
        </div>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#fff',
              color: '#374151',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            },
          }}
        />
      </Router>
    </QueryClientProvider>
  );
}

export default App;
