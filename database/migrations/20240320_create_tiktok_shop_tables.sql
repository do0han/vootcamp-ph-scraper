-- Migration: Create TikTok Shop Tables
-- Description: Creates the necessary tables and structures for TikTok Shop data

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create enum types
CREATE TYPE product_status AS ENUM ('active', 'out_of_stock', 'discontinued');
CREATE TYPE shipping_method AS ENUM ('standard', 'express', 'next_day');

-- Create sellers table first (for foreign key references)
CREATE TABLE IF NOT EXISTS public.tiktok_shop_sellers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    seller_id VARCHAR(255) NOT NULL UNIQUE,
    seller_name VARCHAR(255) NOT NULL,
    shop_url TEXT,
    rating DECIMAL(3,2),
    total_products INTEGER DEFAULT 0,
    total_followers INTEGER DEFAULT 0,
    join_date DATE,
    
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create categories table
CREATE TABLE IF NOT EXISTS public.tiktok_shop_categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    category_id VARCHAR(255) NOT NULL UNIQUE,
    parent_category_id VARCHAR(255),
    category_name VARCHAR(255) NOT NULL,
    level INTEGER NOT NULL,
    is_leaf BOOLEAN DEFAULT false,
    
    FOREIGN KEY (parent_category_id) REFERENCES tiktok_shop_categories(category_id)
);

-- Create main products table
CREATE TABLE IF NOT EXISTS public.tiktok_shop_products (
    -- Primary Key and Timestamps
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Basic Product Information
    product_id VARCHAR(255) NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    seller_id UUID NOT NULL REFERENCES tiktok_shop_sellers(id),
    category_id UUID NOT NULL REFERENCES tiktok_shop_categories(id),
    
    -- Pricing Information
    price DECIMAL(10,2) NOT NULL,
    original_price DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'PHP',
    discount_percentage DECIMAL(5,2),
    
    -- Product Status
    status product_status DEFAULT 'active',
    stock_count INTEGER,
    
    -- Product Details
    description TEXT,
    specifications JSONB DEFAULT '{}'::jsonb,
    image_urls TEXT[],
    product_url TEXT,
    
    -- Shipping Information
    shipping_methods shipping_method[],
    is_free_shipping BOOLEAN DEFAULT false,
    shipping_fee DECIMAL(10,2),
    estimated_days_to_deliver INTEGER,
    
    -- Additional Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create product statistics table (for time-series data)
CREATE TABLE IF NOT EXISTS public.tiktok_shop_product_stats (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    product_id UUID NOT NULL REFERENCES tiktok_shop_products(id),
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Statistics
    views_count INTEGER DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    rating DECIMAL(2,1),
    likes_count INTEGER DEFAULT 0,
    
    -- Price at collection time
    current_price DECIMAL(10,2),
    
    UNIQUE(product_id, collection_date)
);

-- Create indexes for better query performance
CREATE INDEX idx_products_product_id ON tiktok_shop_products(product_id);
CREATE INDEX idx_products_seller_id ON tiktok_shop_products(seller_id);
CREATE INDEX idx_products_category_id ON tiktok_shop_products(category_id);
CREATE INDEX idx_products_collection_date ON tiktok_shop_products(collection_date);
CREATE INDEX idx_products_price ON tiktok_shop_products(price);
CREATE INDEX idx_products_status ON tiktok_shop_products(status);
CREATE INDEX idx_product_name_trgm ON tiktok_shop_products USING gin (product_name gin_trgm_ops);

CREATE INDEX idx_sellers_seller_id ON tiktok_shop_sellers(seller_id);
CREATE INDEX idx_sellers_rating ON tiktok_shop_sellers(rating);

CREATE INDEX idx_categories_parent_id ON tiktok_shop_categories(parent_category_id);
CREATE INDEX idx_categories_level ON tiktok_shop_categories(level);

CREATE INDEX idx_product_stats_product_date ON tiktok_shop_product_stats(product_id, collection_date);

-- Add triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON tiktok_shop_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sellers_updated_at
    BEFORE UPDATE ON tiktok_shop_sellers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON tiktok_shop_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE tiktok_shop_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE tiktok_shop_sellers ENABLE ROW LEVEL SECURITY;
ALTER TABLE tiktok_shop_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE tiktok_shop_product_stats ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies (default to allow all for now, can be restricted later)
CREATE POLICY "Allow all" ON tiktok_shop_products FOR ALL USING (true);
CREATE POLICY "Allow all" ON tiktok_shop_sellers FOR ALL USING (true);
CREATE POLICY "Allow all" ON tiktok_shop_categories FOR ALL USING (true);
CREATE POLICY "Allow all" ON tiktok_shop_product_stats FOR ALL USING (true); 