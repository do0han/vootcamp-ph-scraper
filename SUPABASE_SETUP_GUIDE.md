# 🚀 Supabase 설정 가이드

Vootcamp PH Data Scraper를 위한 Supabase 데이터베이스 설정 가이드입니다.

## 1단계: Supabase 프로젝트 생성

### 1. Supabase 계정 생성 및 프로젝트 생성
1. **[Supabase](https://supabase.com)** 웹사이트 접속
2. **"Start your project"** 클릭
3. GitHub 계정으로 로그인
4. **"New project"** 클릭
5. Organization 선택 (개인 계정 사용 권장)
6. 프로젝트 정보 입력:
   - **Name**: `vootcamp-ph-scraper`
   - **Database Password**: 강력한 패스워드 생성 (저장 필수!)
   - **Region**: `Southeast Asia (Singapore)` (필리핀과 가장 가까운 리전)
7. **"Create new project"** 클릭

### 2. 프로젝트 생성 대기
- 프로젝트 생성에 1-2분 소요
- 완료되면 프로젝트 대시보드로 이동됩니다

## 2단계: 데이터베이스 스키마 생성

### 1. SQL Editor 접속
1. 왼쪽 메뉴에서 **"SQL Editor"** 클릭
2. **"New query"** 클릭

### 2. 스키마 SQL 실행
아래 SQL을 복사해서 SQL Editor에 붙여넣고 실행하세요:

```sql
-- Google Trends Table
CREATE TABLE IF NOT EXISTS google_trends (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    collection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trend_type VARCHAR(50) NOT NULL,
    keyword VARCHAR(255) NOT NULL,
    search_volume INTEGER,
    related_topics JSONB,
    region VARCHAR(10) DEFAULT 'PH',
    category VARCHAR(100),
    timeframe VARCHAR(50),
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
    used_hashtags JSONB,
    sound_info JSONB,
    duration_seconds INTEGER,
    upload_date TIMESTAMPTZ,
    is_trending BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_google_trends_collection_date ON google_trends(collection_date);
CREATE INDEX IF NOT EXISTS idx_google_trends_keyword ON google_trends(keyword);
CREATE INDEX IF NOT EXISTS idx_shopee_products_collection_date ON shopee_products(collection_date);
CREATE INDEX IF NOT EXISTS idx_shopee_products_search_keyword ON shopee_products(search_keyword);
CREATE INDEX IF NOT EXISTS idx_tiktok_videos_collection_date ON tiktok_videos(collection_date);
CREATE INDEX IF NOT EXISTS idx_tiktok_videos_hashtag ON tiktok_videos(hashtag);

-- Trending Summary View
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
```

3. **"RUN"** 버튼 클릭하여 실행
4. 성공 메시지 확인 후 **"Table Editor"**에서 테이블들이 생성되었는지 확인

## 3단계: API 키 확보

### 1. Project API 키 복사
1. 왼쪽 메뉴에서 **"Settings"** → **"API"** 클릭
2. **Project URL** 복사 (예: `https://abcdefgh.supabase.co`)
3. **anon public** 키 복사 (eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... 형식)

## 4단계: 환경 변수 설정

### 1. .env 파일 생성
vootcamp_ph_scraper 폴더에서:

```bash
cp env.example .env
```

### 2. .env 파일 편집
```bash
# Supabase Configuration
SUPABASE_URL=https://여기에-당신의-프로젝트-url.supabase.co
SUPABASE_KEY=여기에-당신의-anon-public-키

# Scraping Configuration (이미 설정된 값들)
USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
HEADLESS_MODE=true
MAX_RETRIES=3
DELAY_BETWEEN_REQUESTS=2
LOG_LEVEL=INFO
SHOPEE_BASE_URL=https://shopee.ph
GOOGLE_TRENDS_REGION=PH
```

## 5단계: 연결 테스트

### 1. 데이터베이스 연결 테스트
```bash
python3 -c "
from database.supabase_client import SupabaseClient
try:
    client = SupabaseClient()
    print('✅ Supabase 연결 성공!')
except Exception as e:
    print(f'❌ 연결 실패: {e}')
"
```

### 2. 테이블 확인 테스트
```bash
python3 -c "
from database.supabase_client import SupabaseClient
client = SupabaseClient()

# 각 테이블 확인
tables = ['google_trends', 'shopee_products', 'tiktok_videos']
for table in tables:
    try:
        result = client.client.table(table).select('*').limit(1).execute()
        print(f'✅ {table} 테이블 정상')
    except Exception as e:
        print(f'❌ {table} 테이블 오류: {e}')
"
```

## 6단계: 보안 설정 (선택사항)

### Row Level Security (RLS) 활성화
더 강화된 보안을 원한다면:

```sql
-- RLS 활성화
ALTER TABLE google_trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopee_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE tiktok_videos ENABLE ROW LEVEL SECURITY;

-- 모든 사용자에게 읽기 권한 부여 (필요에 따라 조정)
CREATE POLICY "Allow read access" ON google_trends FOR SELECT USING (true);
CREATE POLICY "Allow read access" ON shopee_products FOR SELECT USING (true);
CREATE POLICY "Allow read access" ON tiktok_videos FOR SELECT USING (true);

-- 삽입 권한 부여 (스크래퍼용)
CREATE POLICY "Allow insert access" ON google_trends FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow insert access" ON shopee_products FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow insert access" ON tiktok_videos FOR INSERT WITH CHECK (true);
```

## 7단계: 대시보드에서 데이터 확인

### Supabase 대시보드에서 실시간 모니터링
1. **"Table Editor"** → 각 테이블에서 데이터 확인
2. **"SQL Editor"**에서 trending_summary 뷰 조회:
   ```sql
   SELECT * FROM trending_summary;
   ```

## 🎉 설정 완료!

이제 Vootcamp PH Data Scraper가 Supabase에 연결되어 필리핀 시장 데이터를 자동으로 수집하고 저장할 준비가 완료되었습니다!

### 다음 단계
```bash
# 전체 시스템 테스트 실행
python3 main.py
```

## 📞 문제 해결

### 일반적인 오류들:

1. **"Authentication failed"**: API 키가 올바른지 확인
2. **"relation does not exist"**: SQL 스키마가 제대로 실행되었는지 확인
3. **"permission denied"**: RLS 정책 확인 (위의 6단계 참조)

### 도움이 필요하시면:
- Supabase 공식 문서: https://supabase.com/docs
- 프로젝트 이슈: GitHub Issues에 문의