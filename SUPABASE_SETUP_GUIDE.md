# 🗄️ Supabase 설정 가이드

이 가이드는 Vootcamp PH 스크래퍼에 Supabase 데이터베이스를 설정하는 방법을 안내합니다.

## 📋 빠른 설정 체크리스트

- [ ] Supabase 계정 생성
- [ ] 새 프로젝트 생성
- [ ] 데이터베이스 스키마 적용
- [ ] 환경 변수 설정
- [ ] 연결 테스트 성공

## 🚀 단계별 설정

### 1. Supabase 계정 및 프로젝트 생성

1. [supabase.com](https://supabase.com)에서 무료 계정 생성
2. "New Project" 클릭
3. 프로젝트 이름: `vootcamp-ph-scraper`
4. 데이터베이스 비밀번호 설정 (안전한 곳에 저장!)
5. Region: `Southeast Asia (Singapore)` 권장 (필리핀과 가까움)
6. 프로젝트 생성 완료까지 대기 (약 2분)

### 2. API 키 확인

프로젝트 생성 후:
1. 프로젝트 대시보드에서 **Settings** > **API** 이동
2. 다음 정보 복사:
   - **Project URL**: `https://your-project-ref.supabase.co`
   - **anon public key**: `eyJhbGc...` (공개키)
   - **service_role key**: `eyJhbGc...` (비밀키)

### 3. 데이터베이스 스키마 적용

1. Supabase 대시보드에서 **SQL Editor** 이동
2. **New query** 클릭
3. `database/schema.sql` 파일의 내용을 복사하여 붙여넣기
4. **Run** 버튼 클릭
5. 성공 메시지 확인

### 4. 환경 변수 설정

```bash
# 1. 환경 변수 파일 생성
cp env.example .env

# 2. .env 파일 편집
# 최소한 다음 두 항목은 반드시 설정:
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-public-key-here
```

### 5. 연결 테스트

```bash
# 데이터베이스 연결 테스트
python test_database.py
```

성공하면 다음과 같은 메시지가 출력됩니다:
```
✅ Supabase connection successful!
✅ Google Trends: Inserted 1 records
✅ Shopee Products: Inserted 1 records  
✅ TikTok Videos: Inserted 1 records
🎉 All database tests passed successfully!
```

## 🏗️ 생성된 테이블 구조

| 테이블명 | 설명 | 주요 필드 |
|---------|------|-----------|
| `google_trends` | Google 트렌드 데이터 | keyword, search_volume, region |
| `shopee_products` | Shopee 상품 정보 | product_name, price, rating, sales_count |
| `tiktok_videos` | TikTok 영상 데이터 | video_url, view_count, hashtag |

## 🔧 고급 설정 (선택사항)

### Row Level Security (RLS) 활성화

보안을 위해 RLS를 활성화하려면:

```sql
-- 각 테이블에 RLS 활성화
ALTER TABLE google_trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopee_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE tiktok_videos ENABLE ROW LEVEL SECURITY;

-- 모든 사용자에게 읽기 권한 부여 (개발 단계)
CREATE POLICY "Enable read access for all users" ON google_trends
    FOR SELECT USING (true);
    
CREATE POLICY "Enable read access for all users" ON shopee_products
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON tiktok_videos
    FOR SELECT USING (true);
```

### 자동 데이터 정리 설정

30일 이상 된 데이터 자동 삭제:

   ```sql
-- 매일 자정에 실행되는 크론 작업 생성
SELECT cron.schedule('cleanup-old-data', '0 0 * * *', 'SELECT clean_old_data(30);');
   ```

## 🚨 문제 해결

### 연결 오류

**문제**: `ValueError: Supabase URL and key must be set`
**해결**: `.env` 파일에 올바른 URL과 키가 설정되었는지 확인

**문제**: `Invalid API key`
**해결**: Supabase 대시보드에서 API 키를 다시 복사해서 확인

**문제**: `Connection timeout`
**해결**: 인터넷 연결 확인, 프로젝트가 활성 상태인지 확인

### 스키마 오류

**문제**: `relation "table_name" does not exist`
**해결**: SQL Editor에서 `database/schema.sql` 스크립트를 다시 실행

### 권한 오류

**문제**: `insufficient_privilege`
**해결**: `service_role` 키를 사용하거나 RLS 정책 확인

## 📊 모니터링 및 관리

### 데이터 확인

```sql
-- 각 테이블의 데이터 수 확인
SELECT * FROM trending_summary;

-- 최근 24시간 데이터 확인
SELECT COUNT(*) FROM google_trends WHERE collection_date >= NOW() - INTERVAL '24 hours';
SELECT COUNT(*) FROM shopee_products WHERE collection_date >= NOW() - INTERVAL '24 hours';
SELECT COUNT(*) FROM tiktok_videos WHERE collection_date >= NOW() - INTERVAL '24 hours';
```

### 성능 최적화

- 인덱스는 자동으로 생성됨
- 대량 데이터 처리시 배치 삽입 사용
- 정기적인 `VACUUM ANALYZE` 실행 권장

## 🔗 추가 자료

- [Supabase 공식 문서](https://supabase.com/docs)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)
- [프로젝트 GitHub](https://github.com/your-repo/vootcamp-ph-scraper)

---

✅ **설정 완료 후 다음 단계**: Google Trends 스크래퍼 구현 ([Task 16](../README.md#tasks))