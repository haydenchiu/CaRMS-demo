-- Initialize PostgreSQL database for CaRMS project
-- This script runs automatically when the container first starts

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a schema for analytics if needed
-- CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE carms TO carms;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO carms;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO carms;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO carms;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO carms;
