-- Create TikTok Shop Categories Table
CREATE TABLE IF NOT EXISTS public.tiktok_shop_categories (
    -- Primary Key and Timestamps
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Category Information
    category_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES public.tiktok_shop_categories(id),
    level INTEGER NOT NULL, -- Hierarchy level (1 = root)
    path_ids UUID[] NOT NULL, -- Array of ancestor IDs
    path_names TEXT[] NOT NULL, -- Array of ancestor names
    
    -- Category Statistics
    product_count INTEGER DEFAULT 0,
    active_product_count INTEGER DEFAULT 0,
    
    -- Category Details
    description TEXT,
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER,
    
    -- Metadata
    metadata JSONB -- Additional flexible metadata storage
);

-- Create indexes
CREATE INDEX idx_tiktok_categories_category_id ON public.tiktok_shop_categories(category_id);
CREATE INDEX idx_tiktok_categories_parent_id ON public.tiktok_shop_categories(parent_id);
CREATE INDEX idx_tiktok_categories_path_ids ON public.tiktok_shop_categories USING GIN(path_ids);
CREATE INDEX idx_tiktok_categories_level ON public.tiktok_shop_categories(level);

-- Create updated_at trigger
CREATE TRIGGER update_tiktok_shop_categories_updated_at
    BEFORE UPDATE ON public.tiktok_shop_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE public.tiktok_shop_categories ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Enable read access for authenticated users" ON public.tiktok_shop_categories
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Enable insert for service role only" ON public.tiktok_shop_categories
    FOR INSERT
    TO service_role
    WITH CHECK (true);

CREATE POLICY "Enable update for service role only" ON public.tiktok_shop_categories
    FOR UPDATE
    TO service_role
    USING (true)
    WITH CHECK (true); 