
# TikTok Shop Schema Application Guide

## 📋 스키마 적용 준비 완료

### ✅ 검증 완료 사항
- 스키마 파일 존재: `database/tiktok_shop_schema.sql`
- SQL 구문 검증: 12개 SQL 문장 준비완료
- 필수 요소 확인: 테이블, 인덱스, 트리거 모두 포함
- 필수 컬럼 확인: product_id, product_name, price, collection_date

### 🚀 Supabase 스키마 적용 방법

#### 1. Supabase 대시보드 접속
- https://app.supabase.com 접속
- 프로젝트 선택

#### 2. SQL Editor 열기
- 좌측 메뉴에서 "SQL Editor" 클릭
- "New query" 버튼 클릭

#### 3. 스키마 SQL 복사 및 실행
```sql
-- 아래 파일의 내용을 복사하여 SQL Editor에 붙여넣기
-- 파일 위치: vootcamp_ph_scraper/database/tiktok_shop_schema.sql

-- 주요 구성요소:
-- ✅ tiktok_shop_products 테이블 생성
-- ✅ 6개 성능 인덱스 생성
-- ✅ 자동 updated_at 트리거 생성
-- ✅ PHP 통화 기본값 설정
```

#### 4. 실행 확인
- "RUN" 버튼 클릭하여 스키마 적용
- 오류 없이 완료되면 성공

#### 5. 테이블 확인
- 좌측 메뉴에서 "Table Editor" 클릭
- `tiktok_shop_products` 테이블 확인

### 📊 생성될 테이블 구조

```
tiktok_shop_products
├── id (UUID, Primary Key)
├── collection_date (TIMESTAMPTZ)
├── product_id (VARCHAR, Unique)
├── product_name (TEXT)
├── seller_name (VARCHAR)
├── price (DECIMAL)
├── rating (DECIMAL)
├── review_count (INTEGER)
├── sales_count (INTEGER)
├── product_url (TEXT)
├── image_urls (JSONB)
├── category_path (JSONB)
├── discount_info (JSONB)
├── is_cod_available (BOOLEAN)
└── ... (20+ 컬럼)
```

### 🎯 스키마 특징
- **Philippines 시장 특화**: PHP 통화 기본값
- **JSONB 활용**: 유연한 데이터 구조
- **성능 최적화**: 6개 인덱스로 빠른 쿼리
- **자동 관리**: 타임스탬프 자동 업데이트
- **확장성**: 추후 컬럼 추가 용이

### ⚡ 성능 인덱스
1. collection_date - 수집 날짜별 조회
2. product_id - 상품 고유 ID 조회
3. seller_id - 판매자별 조회
4. price - 가격 범위 검색
5. rating - 평점 기준 정렬
6. sales_count - 판매량 기준 정렬

### 🔧 트러블슈팅
- **테이블 이미 존재**: `DROP TABLE IF EXISTS tiktok_shop_products;` 먼저 실행
- **권한 오류**: Supabase 프로젝트 owner 권한 확인
- **JSONB 오류**: PostgreSQL 버전 확인 (9.4+ 필요)

### 📝 다음 단계
1. ✅ 스키마 적용 완료
2. 🧪 main.py 실행으로 TikTok Shop 데이터 수집 테스트
3. 📊 Supabase 대시보드에서 데이터 확인
4. 🚀 프로덕션 스케줄링 설정

---
생성 시간: 2025-06-29 23:01:34