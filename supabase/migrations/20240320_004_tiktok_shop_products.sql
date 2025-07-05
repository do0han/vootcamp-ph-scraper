-- Create TikTok Shop Products Table
CREATE TABLE IF NOT EXISTS public.tiktok_shop_products (
    -- Primary Key and Timestamps
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Basic Product Information
    product_id VARCHAR(255) NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    seller_id UUID NOT NULL REFERENCES public.tiktok_shop_sellers(id),
    category_id UUID NOT NULL REFERENCES public.tiktok_shop_categories(id),
    
    -- Pricing Information
    price DECIMAL(10,2) NOT NULL,
    original_price DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'PHP',
    discount_percentage DECIMAL(5,2),
    
    -- Product Status
    status product_status DEFAULT 'active',
    stock_count INTEGER NOT NULL DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2),
    review_count INTEGER DEFAULT 0,
    
    -- Product Details
    description TEXT,
    product_url TEXT,
    image_urls TEXT[], -- Array of image URLs
    video_urls TEXT[], -- Array of video URLs
    specifications JSONB, -- Product specifications
    variants JSONB, -- Product variants/options
    
    -- Shipping Information
    shipping_info JSONB, -- Detailed shipping options
    is_free_shipping BOOLEAN DEFAULT FALSE,
    is_cod_available BOOLEAN DEFAULT FALSE,
    shipping_methods shipping_method[],
    
    -- SEO and Marketing
    keywords TEXT[],
    tags TEXT[],
    
    -- Collection Information
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB -- Additional flexible metadata storage
);

-- Create indexes
CREATE INDEX idx_tiktok_products_product_id ON public.tiktok_shop_products(product_id);
CREATE INDEX idx_tiktok_products_seller_id ON public.tiktok_shop_products(seller_id);
CREATE INDEX idx_tiktok_products_category_id ON public.tiktok_shop_products(category_id);
CREATE INDEX idx_tiktok_products_status ON public.tiktok_shop_products(status);
CREATE INDEX idx_tiktok_products_price ON public.tiktok_shop_products(price);
CREATE INDEX idx_tiktok_products_rating ON public.tiktok_shop_products(rating);
CREATE INDEX idx_tiktok_products_sales_count ON public.tiktok_shop_products(sales_count);
CREATE INDEX idx_tiktok_products_collection_date ON public.tiktok_shop_products(collection_date);
CREATE INDEX idx_tiktok_products_product_name_trgm ON public.tiktok_shop_products USING GIN (product_name gin_trgm_ops);
CREATE INDEX idx_tiktok_products_keywords ON public.tiktok_shop_products USING GIN (keywords);

-- Create updated_at trigger
CREATE TRIGGER update_tiktok_shop_products_updated_at
    BEFORE UPDATE ON public.tiktok_shop_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE public.tiktok_shop_products ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Enable read access for authenticated users" ON public.tiktok_shop_products
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Enable insert for service role only" ON public.tiktok_shop_products
    FOR INSERT
    TO service_role
    WITH CHECK (true);

CREATE POLICY "Enable update for service role only" ON public.tiktok_shop_products
    FOR UPDATE
    TO service_role
    USING (true)
    WITH CHECK (true); 