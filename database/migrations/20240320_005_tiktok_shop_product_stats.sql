-- Create TikTok Shop Product Statistics Table
CREATE TABLE IF NOT EXISTS public.tiktok_shop_product_stats (
    -- Primary Key and Timestamps
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- References
    product_id UUID NOT NULL REFERENCES public.tiktok_shop_products(id),
    
    -- Time-series Data
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Price Information
    price DECIMAL(10,2) NOT NULL,
    original_price DECIMAL(10,2),
    discount_percentage DECIMAL(5,2),
    
    -- Statistics
    stock_count INTEGER NOT NULL DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2),
    review_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    
    -- Engagement Metrics
    likes_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    
    -- Additional Metrics
    conversion_rate DECIMAL(5,2), -- sales/views * 100
    
    -- Metadata
    metadata JSONB -- Additional flexible metadata storage
);

-- Create indexes
CREATE INDEX idx_tiktok_product_stats_product_id ON public.tiktok_shop_product_stats(product_id);
CREATE INDEX idx_tiktok_product_stats_collection_date ON public.tiktok_shop_product_stats(collection_date);
CREATE INDEX idx_tiktok_product_stats_price ON public.tiktok_shop_product_stats(price);
CREATE INDEX idx_tiktok_product_stats_sales_count ON public.tiktok_shop_product_stats(sales_count);

-- Enable RLS
ALTER TABLE public.tiktok_shop_product_stats ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Enable read access for authenticated users" ON public.tiktok_shop_product_stats
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Enable insert for service role only" ON public.tiktok_shop_product_stats
    FOR INSERT
    TO service_role
    WITH CHECK (true);

-- Note: We don't need update policy for this table as it's time-series data 