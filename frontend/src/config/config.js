/**
 * Environment configuration utility
 * Centralizes access to environment variables with fallbacks
 */

class Config {
  constructor() {
    // Validate critical environment variables
    this.validateConfig();
  }

  // API Configuration
  get apiUrl() {
    return process.env.REACT_APP_API_URL || 'http://localhost:8002';
  }

  get apiTimeout() {
    return parseInt(process.env.REACT_APP_API_TIMEOUT) || 30000;
  }

  get apiVersion() {
    return 'v1';
  }

  get fullApiUrl() {
    return `${this.apiUrl}/api/${this.apiVersion}`;
  }

  // Application Information
  get appName() {
    return process.env.REACT_APP_NAME || 'Karnataka Power Outage Forecasting System';
  }

  get appVersion() {
    return process.env.REACT_APP_VERSION || '1.0.0';
  }

  // Map Configuration
  get defaultLatitude() {
    return parseFloat(process.env.REACT_APP_DEFAULT_LATITUDE) || 15.3173;
  }

  get defaultLongitude() {
    return parseFloat(process.env.REACT_APP_DEFAULT_LONGITUDE) || 75.7139;
  }

  get mapZoomLevel() {
    return parseInt(process.env.REACT_APP_MAP_ZOOM_LEVEL) || 7;
  }

  get mapStyle() {
    return process.env.REACT_APP_MAP_STYLE || 'mapbox://styles/mapbox/light-v10';
  }

  // Feature Flags
  get isHeatmapEnabled() {
    return this.getBooleanEnv('REACT_APP_ENABLE_HEATMAP', true);
  }

  get isWhatIfEnabled() {
    return this.getBooleanEnv('REACT_APP_ENABLE_WHAT_IF', true);
  }

  get isMetricsEnabled() {
    return this.getBooleanEnv('REACT_APP_ENABLE_METRICS', true);
  }

  get isAdvisoriesEnabled() {
    return this.getBooleanEnv('REACT_APP_ENABLE_ADVISORIES', true);
  }

  get isBatchPredictionsEnabled() {
    return this.getBooleanEnv('REACT_APP_ENABLE_BATCH_PREDICTIONS', true);
  }

  // UI Configuration
  get theme() {
    return process.env.REACT_APP_THEME || 'light';
  }

  get language() {
    return process.env.REACT_APP_LANGUAGE || 'en';
  }

  get refreshInterval() {
    return parseInt(process.env.REACT_APP_REFRESH_INTERVAL) || 300000; // 5 minutes
  }

  get maxPredictionHours() {
    return parseInt(process.env.REACT_APP_MAX_PREDICTION_HOURS) || 48;
  }

  // Weather Configuration
  get weatherUpdateInterval() {
    return parseInt(process.env.REACT_APP_WEATHER_UPDATE_INTERVAL) || 900000; // 15 minutes
  }

  get isLocationServicesEnabled() {
    return this.getBooleanEnv('REACT_APP_ENABLE_LOCATION_SERVICES', true);
  }

  get defaultCity() {
    return process.env.REACT_APP_DEFAULT_CITY || 'Bengaluru';
  }

  // Development Settings
  get isDebugMode() {
    return this.getBooleanEnv('REACT_APP_DEBUG_MODE', false);
  }

  get enableConsoleLogs() {
    return this.getBooleanEnv('REACT_APP_ENABLE_CONSOLE_LOGS', false);
  }

  get isDevelopment() {
    return process.env.NODE_ENV === 'development';
  }

  get isProduction() {
    return process.env.NODE_ENV === 'production';
  }

  // Third-party Services
  get mapboxToken() {
    return process.env.REACT_APP_MAPBOX_TOKEN;
  }

  get googleMapsKey() {
    return process.env.REACT_APP_GOOGLE_MAPS_KEY;
  }

  // Analytics
  get googleAnalyticsId() {
    return process.env.REACT_APP_GOOGLE_ANALYTICS_ID;
  }

  get isAnalyticsEnabled() {
    return this.getBooleanEnv('REACT_APP_ENABLE_ANALYTICS', false);
  }

  // Error Reporting
  get sentryDsn() {
    return process.env.REACT_APP_SENTRY_DSN;
  }

  get isErrorReportingEnabled() {
    return this.getBooleanEnv('REACT_APP_ENABLE_ERROR_REPORTING', false);
  }

  // Utility Methods
  getBooleanEnv(key, defaultValue = false) {
    const value = process.env[key];
    if (value === undefined) return defaultValue;
    return value.toLowerCase() === 'true' || value === '1';
  }

  getNumberEnv(key, defaultValue = 0) {
    const value = process.env[key];
    if (value === undefined) return defaultValue;
    const parsed = parseInt(value);
    return isNaN(parsed) ? defaultValue : parsed;
  }

  getFloatEnv(key, defaultValue = 0) {
    const value = process.env[key];
    if (value === undefined) return defaultValue;
    const parsed = parseFloat(value);
    return isNaN(parsed) ? defaultValue : parsed;
  }

  // Configuration validation
  validateConfig() {
    const warnings = [];
    const errors = [];

    // Check critical configurations
    if (!this.apiUrl) {
      errors.push('REACT_APP_API_URL is not set');
    }

    // Check optional but recommended configurations
    if (!this.mapboxToken && this.isDevelopment) {
      warnings.push('REACT_APP_MAPBOX_TOKEN is not set - map functionality may be limited');
    }

    if (this.isAnalyticsEnabled && !this.googleAnalyticsId) {
      warnings.push('Analytics enabled but REACT_APP_GOOGLE_ANALYTICS_ID is not set');
    }

    if (this.isErrorReportingEnabled && !this.sentryDsn) {
      warnings.push('Error reporting enabled but REACT_APP_SENTRY_DSN is not set');
    }

    // Log warnings and errors
    if (warnings.length > 0 && this.isDevelopment) {
      console.warn('Configuration warnings:');
      warnings.forEach(warning => console.warn(`  - ${warning}`));
    }

    if (errors.length > 0) {
      console.error('Configuration errors:');
      errors.forEach(error => console.error(`  - ${error}`));
      
      if (!this.isDevelopment) {
        throw new Error('Critical configuration errors found');
      }
    }
  }

  // Get all configuration for debugging
  getAllConfig() {
    return {
      // API
      apiUrl: this.apiUrl,
      apiTimeout: this.apiTimeout,
      fullApiUrl: this.fullApiUrl,
      
      // App
      appName: this.appName,
      appVersion: this.appVersion,
      
      // Map
      defaultLatitude: this.defaultLatitude,
      defaultLongitude: this.defaultLongitude,
      mapZoomLevel: this.mapZoomLevel,
      
      // Features
      features: {
        heatmap: this.isHeatmapEnabled,
        whatIf: this.isWhatIfEnabled,
        metrics: this.isMetricsEnabled,
        advisories: this.isAdvisoriesEnabled,
        batchPredictions: this.isBatchPredictionsEnabled,
      },
      
      // UI
      theme: this.theme,
      language: this.language,
      refreshInterval: this.refreshInterval,
      
      // Development
      isDevelopment: this.isDevelopment,
      isDebugMode: this.isDebugMode,
      enableConsoleLogs: this.enableConsoleLogs,
    };
  }

  // Print configuration summary
  printConfigSummary() {
    if (!this.isDevelopment && !this.isDebugMode) return;

    console.group('🔧 Application Configuration');
    console.log('API URL:', this.apiUrl);
    console.log('Environment:', this.isDevelopment ? 'Development' : 'Production');
    console.log('Debug Mode:', this.isDebugMode);
    console.log('Enabled Features:');
    console.log('  - Heatmap:', this.isHeatmapEnabled);
    console.log('  - What-If Analysis:', this.isWhatIfEnabled);
    console.log('  - Metrics Dashboard:', this.isMetricsEnabled);
    console.log('  - Advisories:', this.isAdvisoriesEnabled);
    console.log('  - Batch Predictions:', this.isBatchPredictionsEnabled);
    console.groupEnd();
  }
}

// Create and export singleton instance
const config = new Config();

// Print configuration summary in development
if (config.isDevelopment) {
  config.printConfigSummary();
}

export default config;

// Export specific config groups for convenience
export const apiConfig = {
  baseUrl: config.apiUrl,
  fullUrl: config.fullApiUrl,
  timeout: config.apiTimeout,
  version: config.apiVersion,
};

export const mapConfig = {
  defaultCenter: [config.defaultLatitude, config.defaultLongitude],
  defaultZoom: config.mapZoomLevel,
  style: config.mapStyle,
};

export const featureFlags = {
  heatmap: config.isHeatmapEnabled,
  whatIf: config.isWhatIfEnabled,
  metrics: config.isMetricsEnabled,
  advisories: config.isAdvisoriesEnabled,
  batchPredictions: config.isBatchPredictionsEnabled,
};

export const uiConfig = {
  theme: config.theme,
  language: config.language,
  refreshInterval: config.refreshInterval,
  maxPredictionHours: config.maxPredictionHours,
};