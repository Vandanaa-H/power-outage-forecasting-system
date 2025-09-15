-- Initialize TimescaleDB and create necessary extensions
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create database for the application
CREATE DATABASE outage_forecast;

-- Switch to the application database
\c outage_forecast;

-- Create TimescaleDB extension in the application database
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create hypertables for time-series data
-- This will be executed after tables are created by SQLAlchemy

-- Create indexes for better performance
-- Weather data indexes
CREATE INDEX IF NOT EXISTS idx_weather_data_location ON weather_data (location_lat, location_lon);
CREATE INDEX IF NOT EXISTS idx_weather_data_timestamp ON weather_data (timestamp);

-- Grid data indexes
CREATE INDEX IF NOT EXISTS idx_grid_data_substation ON grid_data (substation_id);
CREATE INDEX IF NOT EXISTS idx_grid_data_timestamp ON grid_data (timestamp);

-- Outage events indexes
CREATE INDEX IF NOT EXISTS idx_outage_events_location ON outage_events (location_lat, location_lon);
CREATE INDEX IF NOT EXISTS idx_outage_events_time ON outage_events (start_time);

-- Prediction logs indexes
CREATE INDEX IF NOT EXISTS idx_prediction_logs_location ON prediction_logs (location_lat, location_lon);
CREATE INDEX IF NOT EXISTS idx_prediction_logs_timestamp ON prediction_logs (prediction_timestamp);

-- Advisory logs indexes
CREATE INDEX IF NOT EXISTS idx_advisory_logs_issued ON advisory_logs (issued_at);
CREATE INDEX IF NOT EXISTS idx_advisory_logs_severity ON advisory_logs (severity);

-- Create a function to convert regular tables to hypertables
-- This will be called after the application creates the tables
CREATE OR REPLACE FUNCTION create_hypertables()
RETURNS void AS $$
BEGIN
    -- Convert weather_data to hypertable
    PERFORM create_hypertable('weather_data', 'timestamp', 
                            chunk_time_interval => INTERVAL '1 day',
                            if_not_exists => TRUE);
    
    -- Convert grid_data to hypertable
    PERFORM create_hypertable('grid_data', 'timestamp', 
                            chunk_time_interval => INTERVAL '1 day',
                            if_not_exists => TRUE);
    
    -- Convert prediction_logs to hypertable
    PERFORM create_hypertable('prediction_logs', 'prediction_timestamp', 
                            chunk_time_interval => INTERVAL '1 day',
                            if_not_exists => TRUE);
    
    RAISE NOTICE 'Hypertables created successfully';
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE outage_forecast TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
