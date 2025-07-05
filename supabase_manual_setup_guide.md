# Supabase TikTok Shop 테이블 수동 생성 가이드

## 현재 상태
✅ **Supabase 연결 성공**  
✅ **기존 테이블**: `google_trends`, `shopee_products`  
❌ **생성 필요**: `tiktok_shop_products`, `tiktok_shop_sellers`, `tiktok_shop_categories`

## 수동 테이블 생성 방법

### 1. Supabase 대시보드 접속
1. https://supabase.com/dashboard 에 로그인
2. `vootcamp-ph-scraper` 프로젝트 선택
3. 좌측 메뉴에서 **SQL Editor** 클릭

### 2. 마이그레이션 SQL 실행

아래 SQL을 SQL Editor에서 순서대로 실행하세요:

#### Step 1: 기본 설정 및 ENUM 타입 생성
```sql
-- Basic setup for TikTok Shop integration
-- Enums for product status, seller verification, etc.

-- Enum for product status
DO $$ BEGIN
    CREATE TYPE product_status AS ENUM (
        'active',
        'inactive', 
        'out_of_stock',
        'discontinued'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Enum for seller verification status
DO $$ BEGIN
    CREATE TYPE seller_verification_status AS ENUM (
        'unverified',
        'pending',
        'verified',
        'rejected'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Enum for category status
DO $$ BEGIN
    CREATE TYPE category_status AS ENUM (
        'active',
        'inactive',
        'featured'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
```

#### Step 2: TikTok Shop Sellers 테이블
```sql
-- TikTok Shop Sellers table
CREATE TABLE IF NOT EXISTS tiktok_shop_sellers (
    id BIGSERIAL PRIMARY KEY,
    seller_id TEXT UNIQUE NOT NULL,
    seller_name TEXT NOT NULL,
    seller_username TEXT,
    verification_status seller_verification_status DEFAULT 'unverified',
    follower_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.0,
    total_products INTEGER DEFAULT 0,
    joined_date DATE,
    location TEXT,
    description TEXT,
    profile_image_url TEXT,
    cover_image_url TEXT,
    shop_url TEXT,
    contact_info JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_sellers_seller_id ON tiktok_shop_sellers(seller_id);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_sellers_verification ON tiktok_shop_sellers(verification_status);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_sellers_rating ON tiktok_shop_sellers(rating DESC);

-- Create trigger
DROP TRIGGER IF EXISTS update_tiktok_shop_sellers_updated_at ON tiktok_shop_sellers;
CREATE TRIGGER update_tiktok_shop_sellers_updated_at
    BEFORE UPDATE ON tiktok_shop_sellers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

#### Step 3: TikTok Shop Categories 테이블
```sql
-- TikTok Shop Categories table  
CREATE TABLE IF NOT EXISTS tiktok_shop_categories (
    id BIGSERIAL PRIMARY KEY,
    category_id TEXT UNIQUE NOT NULL,
    category_name TEXT NOT NULL,
    parent_category_id TEXT,
    level INTEGER DEFAULT 1,
    status category_status DEFAULT 'active',
    description TEXT,
    image_url TEXT,
    sort_order INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraint for parent category
    CONSTRAINT fk_parent_category 
        FOREIGN KEY (parent_category_id) 
        REFERENCES tiktok_shop_categories(category_id)
        ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_categories_category_id ON tiktok_shop_categories(category_id);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_categories_parent ON tiktok_shop_categories(parent_category_id);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_categories_status ON tiktok_shop_categories(status);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_categories_level ON tiktok_shop_categories(level);

-- Create trigger
DROP TRIGGER IF EXISTS update_tiktok_shop_categories_updated_at ON tiktok_shop_categories;
CREATE TRIGGER update_tiktok_shop_categories_updated_at
    BEFORE UPDATE ON tiktok_shop_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

#### Step 4: TikTok Shop Products 테이블
```sql
-- TikTok Shop Products table
CREATE TABLE IF NOT EXISTS tiktok_shop_products (
    id BIGSERIAL PRIMARY KEY,
    product_id TEXT UNIQUE NOT NULL,
    seller_id TEXT NOT NULL,
    category_id TEXT,
    product_name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(12,2) NOT NULL,
    original_price DECIMAL(12,2),
    currency TEXT DEFAULT 'PHP',
    discount_percentage INTEGER DEFAULT 0,
    status product_status DEFAULT 'active',
    stock_quantity INTEGER DEFAULT 0,
    min_order_quantity INTEGER DEFAULT 1,
    rating DECIMAL(3,2) DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    wishlist_count INTEGER DEFAULT 0,
    product_url TEXT,
    images JSONB DEFAULT '[]',
    variations JSONB DEFAULT '[]',
    shipping_info JSONB DEFAULT '{}',
    attributes JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    collection_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_price_update TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraints
    CONSTRAINT fk_tiktok_shop_products_seller 
        FOREIGN KEY (seller_id) 
        REFERENCES tiktok_shop_sellers(seller_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_tiktok_shop_products_category 
        FOREIGN KEY (category_id) 
        REFERENCES tiktok_shop_categories(category_id) 
        ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_product_id ON tiktok_shop_products(product_id);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_seller ON tiktok_shop_products(seller_id);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_category ON tiktok_shop_products(category_id);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_price ON tiktok_shop_products(price);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_rating ON tiktok_shop_products(rating DESC);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_sales ON tiktok_shop_products(sales_count DESC);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_status ON tiktok_shop_products(status);
CREATE INDEX IF NOT EXISTS idx_tiktok_shop_products_collection_date ON tiktok_shop_products(collection_date DESC);

-- Create trigger
DROP TRIGGER IF EXISTS update_tiktok_shop_products_updated_at ON tiktok_shop_products;
CREATE TRIGGER update_tiktok_shop_products_updated_at
    BEFORE UPDATE ON tiktok_shop_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 3. 테이블 생성 확인

각 단계 실행 후, 다음 SQL로 테이블이 성공적으로 생성되었는지 확인:

```sql
-- 생성된 테이블 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE 'tiktok_shop_%'
ORDER BY table_name;
```

### 4. 완료 후 연결 테스트

터미널에서 다시 연결 테스트를 실행:
```bash
python3 test_supabase_connection.py
```

## 대안: CLI를 통한 마이그레이션 (Service Role 키 필요)

만약 Service Role 키가 있다면:
1. `.env` 파일에 `SUPABASE_SERVICE_ROLE_KEY` 추가
2. MCP 설정에서 해당 키 사용
3. `mcp_supabase_apply_migration` 도구로 자동 적용

## 문제 해결

### 권한 오류 발생 시
- Supabase 대시보드의 **Settings > API**에서 키 확인
- RLS (Row Level Security) 정책이 차단하는지 확인

### 마이그레이션 실패 시  
- 각 SQL 블록을 개별적으로 실행
- 오류 메시지를 확인하여 의존성 문제 해결

---

이 가이드를 따라 테이블 생성을 완료하면, TikTok Shop 스크래퍼가 정상적으로 데이터를 저장할 수 있습니다. 