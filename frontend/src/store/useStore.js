import { create } from 'zustand';

const useStore = create((set, get) => ({
  // UI State
  sidebarOpen: true,
  loading: false,
  error: null,
  
  // Data State
  predictions: [],
  weatherData: [],
  selectedCity: 'bangalore',
  selectedTimeRange: '24h',
  riskThreshold: 0.5,
  
  // Real-time updates
  isRealTimeEnabled: true,
  lastUpdate: null,
  socketConnected: false,
  
  // Filters and Settings
  filters: {
    riskLevel: 'all', // all, high, medium, low
    escomZone: 'all', // all, BESCOM, CHESCOM, etc.
    cityType: 'all', // all, urban, rural
  },
  
  // Actions
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  clearError: () => set({ error: null }),
  
  setPredictions: (predictions) => set({ 
    predictions, 
    lastUpdate: new Date().toISOString() 
  }),
  
  setWeatherData: (weatherData) => set({ weatherData }),
  
  setSelectedCity: (city) => set({ selectedCity: city }),
  
  setSelectedTimeRange: (timeRange) => set({ selectedTimeRange: timeRange }),
  
  setRiskThreshold: (threshold) => set({ riskThreshold: threshold }),
  
  toggleRealTime: () => set((state) => ({ 
    isRealTimeEnabled: !state.isRealTimeEnabled 
  })),
  
  setSocketConnected: (connected) => set({ socketConnected: connected }),
  
  updateFilters: (newFilters) => set((state) => ({
    filters: { ...state.filters, ...newFilters }
  })),
  
  // Computed getters
  getFilteredPredictions: () => {
    const { predictions, filters } = get();
    
    return predictions.filter(prediction => {
      if (filters.riskLevel !== 'all') {
        const riskLevel = prediction.outage_probability > 0.7 ? 'high' :
                         prediction.outage_probability > 0.4 ? 'medium' : 'low';
        if (riskLevel !== filters.riskLevel) return false;
      }
      
      if (filters.escomZone !== 'all' && prediction.escom_zone !== filters.escomZone) {
        return false;
      }
      
      if (filters.cityType !== 'all' && prediction.city_type !== filters.cityType) {
        return false;
      }
      
      return true;
    });
  },
  
  getHighRiskCities: () => {
    const { predictions } = get();
    return predictions.filter(p => p.outage_probability > 0.7);
  },
  
  getCurrentCityPrediction: () => {
    const { predictions, selectedCity } = get();
    return predictions.find(p => p.city.toLowerCase() === selectedCity.toLowerCase());
  },
}));

export default useStore;
