-- TikTok Shop Products Schema
-- Execute these commands in your Supabase SQL editor

-- Create TikTok Shop Products Table
CREATE TABLE IF NOT EXISTS tiktok_shop_products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    product_id VARCHAR(255) NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    seller_name VARCHAR(255),
    seller_id VARCHAR(255),
    price DECIMAL(10,2),
    original_price DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'PHP',
    rating DECIMAL(2,1),
    review_count INTEGER,
    sales_count INTEGER,
    stock_count INTEGER,
    product_url TEXT,
    image_urls JSONB, -- Array of image URLs
    category_path JSONB, -- Category hierarchy as JSON array
    description TEXT,
    specifications JSONB, -- Product specifications as JSON
    shipping_info JSONB, -- Shipping details
    discount_info JSONB, -- Discount information
    is_cod_available BOOLEAN DEFAULT FALSE,
    is_free_shipping BOOLEAN DEFAULT FALSE,
    is_preferred_seller BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_collection_date 
    ON tiktok_shop_products(collection_date);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_product_id 
    ON tiktok_shop_products(product_id);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_seller_id 
    ON tiktok_shop_products(seller_id);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_price 
    ON tiktok_shop_products(price);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_rating 
    ON tiktok_shop_products(rating);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_sales_count 
    ON tiktok_shop_products(sales_count);

-- Add trigger for updating updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tiktok_shop_products_updated_at
    BEFORE UPDATE ON tiktok_shop_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed)
-- GRANT ALL ON tiktok_shop_products TO authenticated;