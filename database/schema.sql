-- Vootcamp PH Data Scraper Database Schema
-- Execute these commands in your Supabase SQL editor

-- Enable RLS (Row Level Security) if needed
-- ALTER TABLE tablename ENABLE ROW LEVEL SECURITY;

-- Google Trends Table
CREATE TABLE IF NOT EXISTS google_trends (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trend_type VARCHAR(50) NOT NULL, -- 'trending_now', 'related_queries', etc.
    keyword VARCHAR(255) NOT NULL,
    search_volume INTEGER,
    related_topics JSONB,
    region VARCHAR(10) DEFAULT 'PH',
    category VARCHAR(100),
    timeframe VARCHAR(50), -- '24h', '7d', '30d', etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shopee Products Table
CREATE TABLE IF NOT EXISTS shopee_products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    search_keyword VARCHAR(255) NOT NULL,
    product_name TEXT NOT NULL,
    seller_name VARCHAR(255),
    price DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'PHP',
    rating DECIMAL(2,1),
    review_count INTEGER,
    sales_count INTEGER,
    product_url TEXT,
    image_url TEXT,
    category VARCHAR(100),
    location VARCHAR(100),
    shipping_info JSONB,
    discount_info JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- TikTok Videos Table
CREATE TABLE IF NOT EXISTS tiktok_videos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    hashtag VARCHAR(255) NOT NULL,
    video_url TEXT,
    video_id VARCHAR(255),
    uploader_name VARCHAR(255),
    uploader_username VARCHAR(255),
    view_count BIGINT,
    like_count INTEGER,
    comment_count INTEGER,
    share_count INTEGER,
    video_title TEXT,
    video_description TEXT,
    used_hashtags JSONB, -- Array of hashtags as JSON
    sound_info JSONB, -- Sound/music information as JSON
    duration_seconds INTEGER,
    upload_date TIMESTAMPTZ,
    is_trending BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_google_trends_collection_date ON google_trends(collection_date);
CREATE INDEX IF NOT EXISTS idx_google_trends_keyword ON google_trends(keyword);
CREATE INDEX IF NOT EXISTS idx_google_trends_trend_type ON google_trends(trend_type);

CREATE INDEX IF NOT EXISTS idx_shopee_products_collection_date ON shopee_products(collection_date);
CREATE INDEX IF NOT EXISTS idx_shopee_products_search_keyword ON shopee_products(search_keyword);
CREATE INDEX IF NOT EXISTS idx_shopee_products_price ON shopee_products(price);
CREATE INDEX IF NOT EXISTS idx_shopee_products_rating ON shopee_products(rating);

CREATE INDEX IF NOT EXISTS idx_tiktok_videos_collection_date ON tiktok_videos(collection_date);
CREATE INDEX IF NOT EXISTS idx_tiktok_videos_hashtag ON tiktok_videos(hashtag);
CREATE INDEX IF NOT EXISTS idx_tiktok_videos_view_count ON tiktok_videos(view_count);
CREATE INDEX IF NOT EXISTS idx_tiktok_videos_is_trending ON tiktok_videos(is_trending);

-- Create a view for trending analysis
CREATE OR REPLACE VIEW trending_summary AS
SELECT 
    'google_trends' as source,
    COUNT(*) as total_records,
    COUNT(DISTINCT keyword) as unique_keywords,
    MAX(collection_date) as last_updated
FROM google_trends
WHERE collection_date >= NOW() - INTERVAL '24 hours'

UNION ALL

SELECT 
    'shopee_products' as source,
    COUNT(*) as total_records,
    COUNT(DISTINCT search_keyword) as unique_keywords,
    MAX(collection_date) as last_updated
FROM shopee_products
WHERE collection_date >= NOW() - INTERVAL '24 hours'

UNION ALL

SELECT 
    'tiktok_videos' as source,
    COUNT(*) as total_records,
    COUNT(DISTINCT hashtag) as unique_keywords,
    MAX(collection_date) as last_updated
FROM tiktok_videos
WHERE collection_date >= NOW() - INTERVAL '24 hours';

-- Create a function to clean old data (optional, for data retention)
CREATE OR REPLACE FUNCTION clean_old_data(retention_days INTEGER DEFAULT 30)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    cutoff_date TIMESTAMPTZ;
    deleted_count INTEGER;
    result_text TEXT := '';
BEGIN
    cutoff_date := NOW() - (retention_days || ' days')::INTERVAL;
    
    -- Delete old Google Trends data
    DELETE FROM google_trends WHERE collection_date < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    result_text := result_text || 'Deleted ' || deleted_count || ' old Google Trends records. ';
    
    -- Delete old Shopee data
    DELETE FROM shopee_products WHERE collection_date < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    result_text := result_text || 'Deleted ' || deleted_count || ' old Shopee products records. ';
    
    -- Delete old TikTok data
    DELETE FROM tiktok_videos WHERE collection_date < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    result_text := result_text || 'Deleted ' || deleted_count || ' old TikTok videos records.';
    
    RETURN result_text;
END;
$$;

-- Grant permissions (adjust as needed for your use case)
-- GRANT ALL ON google_trends TO authenticated;
-- GRANT ALL ON shopee_products TO authenticated;
-- GRANT ALL ON tiktok_videos TO authenticated; 