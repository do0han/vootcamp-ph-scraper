-- Setup TikTok Shop Database Configuration
-- Enable necessary extensions and configurations

-- Enable Row Level Security
ALTER DATABASE postgres SET row_level_security = on;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Create custom types
CREATE TYPE product_status AS ENUM (
    'active',
    'out_of_stock',
    'discontinued',
    'hidden'
);

CREATE TYPE shipping_method AS ENUM (
    'standard',
    'express',
    'next_day'
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql'; 