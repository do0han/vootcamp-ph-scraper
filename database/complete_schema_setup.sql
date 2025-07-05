-- VOOTCAMP PH - Complete Database Schema Setup
-- Execute this script in Supabase SQL Editor to create all required tables

-- 1. TikTok Shop Products Table (MISSING TABLE 1/2)
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

-- 2. Local Events Table (MISSING TABLE 2/2)
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

-- 3. Create Indexes for TikTok Shop Products
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_collection_date ON tiktok_shop_products(collection_date);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_source_type ON tiktok_shop_products(source_type);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_price ON tiktok_shop_products(price);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_rating ON tiktok_shop_products(rating);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_category ON tiktok_shop_products(category);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_is_flash_sale ON tiktok_shop_products(is_flash_sale);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_is_trending ON tiktok_shop_products(is_trending);

-- 4. Create Indexes for Local Events
CREATE INDEX IF NOT EXISTS idx_local_events_collection_date ON local_events(collection_date);
CREATE INDEX IF NOT EXISTS idx_local_events_source_website ON local_events(source_website);
CREATE INDEX IF NOT EXISTS idx_local_events_event_type ON local_events(event_type);
CREATE INDEX IF NOT EXISTS idx_local_events_parsed_start_date ON local_events(parsed_start_date);
CREATE INDEX IF NOT EXISTS idx_local_events_location ON local_events(event_location);

-- 5. Update trending_summary view to include new tables
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

-- 6. Update cleanup function to include new tables
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

-- 7. Verification queries (run after setup to confirm)
-- Uncomment and run these individually to test

-- SELECT 'Tables Created Successfully' as status;
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('tiktok_shop_products', 'local_events');
-- SELECT * FROM trending_summary;
-- SELECT clean_old_data(30);

-- 8. Sample data insertion test (optional)
-- INSERT INTO tiktok_shop_products (source_type, product_name, price, seller_name) 
-- VALUES ('test', 'Test Product', 99.99, 'Test Seller');
-- 
-- INSERT INTO local_events (event_name, event_location, source_url, source_website, event_type) 
-- VALUES ('Test Event', 'Manila', 'https://test.com', 'test_site', 'test');

SELECT 'VOOTCAMP PH Schema Setup Complete!' as message; 