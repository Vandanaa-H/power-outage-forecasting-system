import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        return response.data;
      },
      (error) => {
        const errorMessage = error.response?.data?.message || error.message || 'An error occurred';
        console.error('API Error:', errorMessage);
        return Promise.reject(new Error(errorMessage));
      }
    );
  }

  // Health check
  async getHealth() {
    return this.client.get('/health');
  }

  async getSystemHealth() {
    return this.client.get('/system/health');
  }

  // Predictions
  async makePrediction(predictionData) {
    return this.client.post('/predict', predictionData);
  }

  async makeBatchPredictions(predictions) {
    return this.client.post('/predict/batch', predictions);
  }

  async getHistoricalPredictions(params) {
    return this.client.get('/predict/historical', { params });
  }

  // Heatmap
  async getHeatmapData(params) {
    return this.client.get('/heatmap', { params });
  }

  async getHeatmapGeoJSON(params) {
    return this.client.get('/heatmap/geojson', { params });
  }

  async getRegionalRiskSummary(regionType = 'district') {
    return this.client.get('/heatmap/regions', { 
      params: { region_type: regionType } 
    });
  }

  async getLiveRiskUpdates() {
    return this.client.get('/heatmap/live');
  }

  // Advisories
  async getAdvisories(params = {}) {
    return this.client.get('/advisories', { params });
  }

  async generateAdvisory(riskData) {
    return this.client.post('/advisories/generate', riskData);
  }

  async getAdvisoryDetails(advisoryId) {
    return this.client.get(`/advisories/${advisoryId}`);
  }

  async getPublicAdvisorySummary(location = null) {
    const params = location ? { location } : {};
    return this.client.get('/advisories/public/summary', { params });
  }

  async subscribeToAdvisories(subscriptionData) {
    return this.client.post('/advisories/subscribe', subscriptionData);
  }

  async getAdvisoryHistory(params) {
    return this.client.get('/advisories/history', { params });
  }

  // What-If Simulation
  async runWhatIfSimulation(simulationData) {
    return this.client.post('/what-if', simulationData);
  }

  async runBatchSimulations(simulations) {
    return this.client.post('/what-if/batch', simulations);
  }

  async getSimulationTemplates() {
    return this.client.get('/what-if/templates');
  }

  async runSensitivityAnalysis(params) {
    return this.client.get('/what-if/sensitivity', { params });
  }

  // Weather data
  async getCurrentWeather(lat, lon) {
    // This would integrate with weather APIs
    // For now, return mock data
    return {
      temperature: 28.5,
      humidity: 65,
      wind_speed: 15.2,
      rainfall: 2.1,
      lightning_strikes: 0,
      storm_alert: false,
      location: `${lat}, ${lon}`,
      timestamp: new Date().toISOString()
    };
  }

  // Utility methods
  async testConnection() {
    try {
      await this.getHealth();
      return true;
    } catch (error) {
      return false;
    }
  }

  // File upload for batch data
  async uploadFile(file, endpoint) {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.client.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // Export data
  async exportData(dataType, params = {}) {
    return this.client.get(`/export/${dataType}`, {
      params,
      responseType: 'blob',
    });
  }

  // Metrics and monitoring
  async getMetrics() {
    return this.client.get('/metrics');
  }

  async getBusinessMetrics() {
    return this.client.get('/analytics/business-metrics');
  }

  // Search and filtering
  async searchLocations(query) {
    return this.client.get('/search/locations', {
      params: { q: query }
    });
  }

  // Configuration
  async getConfiguration() {
    return this.client.get('/config');
  }

  async updateConfiguration(config) {
    return this.client.put('/config', config);
  }
}

// Create and export instance
export const apiService = new ApiService();

// Export class for testing
export default ApiService;
