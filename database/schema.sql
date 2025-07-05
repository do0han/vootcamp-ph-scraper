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

-- TikTok Shop Products Table (Philippines TikTok Shop product data)
CREATE TABLE IF NOT EXISTS tiktok_shop_products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_type VARCHAR(50) NOT NULL, -- 'top_products', 'flash_sale', 'category', 'trending'
    product_name TEXT NOT NULL,
    price DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'PHP',
    discount_price DECIMAL(10,2),
    discount_percentage INTEGER,
    seller_name VARCHAR(255),
    seller_id VARCHAR(255),
    rating DECIMAL(2,1),
    sales_count INTEGER,
    product_url TEXT,
    image_url TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    is_flash_sale BOOLEAN DEFAULT FALSE,
    is_trending BOOLEAN DEFAULT FALSE,
    is_sponsored BOOLEAN DEFAULT FALSE,
    product_tags JSONB, -- Array of product tags
    product_description TEXT,
    shipping_info JSONB,
    stock_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Local Events Table (Philippine lifestyle events, bazaars, pop-ups)
CREATE TABLE IF NOT EXISTS local_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_name TEXT NOT NULL,
    event_dates VARCHAR(255), -- e.g., "July 11-13, 2025" or "Every Saturday"
    event_location VARCHAR(255), -- e.g., "BGC, Manila" or "Bonifacio Global City"
    event_description TEXT, -- Short summary of the event
    source_url TEXT NOT NULL, -- URL of the source article
    source_website VARCHAR(100) NOT NULL, -- 'nylon_manila', 'spot_ph', 'when_in_manila'
    event_type VARCHAR(100), -- 'bazaar', 'pop_up', 'market', 'festival', 'exhibition', etc.
    event_tags JSONB, -- Array of tags like ['food', 'fashion', 'art', 'music']
    is_recurring BOOLEAN DEFAULT FALSE, -- True for weekly/monthly events
    parsed_start_date DATE, -- Parsed start date if extractable
    parsed_end_date DATE, -- Parsed end date if extractable
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure we don't duplicate events from the same source
    UNIQUE(source_url, event_name)
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

-- TikTok Shop Products Indexes
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_collection_date ON tiktok_shop_products(collection_date);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_source_type ON tiktok_shop_products(source_type);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_price ON tiktok_shop_products(price);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_rating ON tiktok_shop_products(rating);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_category ON tiktok_shop_products(category);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_is_flash_sale ON tiktok_shop_products(is_flash_sale);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_is_trending ON tiktok_shop_products(is_trending);

-- Local Events Indexes
CREATE INDEX IF NOT EXISTS idx_local_events_collection_date ON local_events(collection_date);
CREATE INDEX IF NOT EXISTS idx_local_events_source_website ON local_events(source_website);
CREATE INDEX IF NOT EXISTS idx_local_events_event_type ON local_events(event_type);
CREATE INDEX IF NOT EXISTS idx_local_events_parsed_start_date ON local_events(parsed_start_date);
CREATE INDEX IF NOT EXISTS idx_local_events_location ON local_events(event_location);

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
WHERE collection_date >= NOW() - INTERVAL '24 hours'

UNION ALL

SELECT 
    'tiktok_shop_products' as source,
    COUNT(*) as total_records,
    COUNT(DISTINCT product_name) as unique_keywords,
    MAX(collection_date) as last_updated
FROM tiktok_shop_products
WHERE collection_date >= NOW() - INTERVAL '24 hours'

UNION ALL

SELECT 
    'local_events' as source,
    COUNT(*) as total_records,
    COUNT(DISTINCT event_name) as unique_keywords,
    MAX(collection_date) as last_updated
FROM local_events
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
    result_text := result_text || 'Deleted ' || deleted_count || ' old TikTok videos records. ';
    
    -- Delete old TikTok Shop data
    DELETE FROM tiktok_shop_products WHERE collection_date < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    result_text := result_text || 'Deleted ' || deleted_count || ' old TikTok Shop products records. ';
    
    -- Delete old Local Events data
    DELETE FROM local_events WHERE collection_date < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    result_text := result_text || 'Deleted ' || deleted_count || ' old Local Events records.';
    
    RETURN result_text;
END;
$$;

-- Grant permissions (adjust as needed for your use case)
-- GRANT ALL ON google_trends TO authenticated;
-- GRANT ALL ON shopee_products TO authenticated;
-- GRANT ALL ON tiktok_videos TO authenticated; 
-- GRANT ALL ON local_events TO authenticated; 