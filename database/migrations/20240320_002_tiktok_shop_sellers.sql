-- Create TikTok Shop Sellers Table
CREATE TABLE IF NOT EXISTS public.tiktok_shop_sellers (
    -- Primary Key and Timestamps
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Seller Information
    seller_id VARCHAR(255) NOT NULL UNIQUE,
    seller_name VARCHAR(255) NOT NULL,
    shop_name VARCHAR(255),
    shop_url TEXT,
    
    -- Shop Statistics
    total_products INTEGER DEFAULT 0,
    total_followers INTEGER DEFAULT 0,
    rating DECIMAL(3,2),
    review_count INTEGER DEFAULT 0,
    
    -- Shop Details
    location JSONB,
    shop_created_at TIMESTAMPTZ,
    is_verified BOOLEAN DEFAULT FALSE,
    badges JSONB, -- Shop badges/achievements
    
    -- Metadata
    last_scraped_at TIMESTAMPTZ,
    metadata JSONB -- Additional flexible metadata storage
);

-- Create indexes
CREATE INDEX idx_tiktok_sellers_seller_id ON public.tiktok_shop_sellers(seller_id);
CREATE INDEX idx_tiktok_sellers_shop_name ON public.tiktok_shop_sellers(shop_name);
CREATE INDEX idx_tiktok_sellers_rating ON public.tiktok_shop_sellers(rating);

-- Create updated_at trigger
CREATE TRIGGER update_tiktok_shop_sellers_updated_at
    BEFORE UPDATE ON public.tiktok_shop_sellers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE public.tiktok_shop_sellers ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Enable read access for authenticated users" ON public.tiktok_shop_sellers
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Enable insert for service role only" ON public.tiktok_shop_sellers
    FOR INSERT
    TO service_role
    WITH CHECK (true);

CREATE POLICY "Enable update for service role only" ON public.tiktok_shop_sellers
    FOR UPDATE
    TO service_role
    USING (true)
    WITH CHECK (true); 