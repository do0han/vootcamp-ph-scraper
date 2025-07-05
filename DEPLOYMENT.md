# 🚀 Vootcamp PH - 배포 가이드

이 문서는 Vootcamp PH AI 콘텐츠 아이디어 생성기의 배포 방법을 설명합니다.

## 📋 사전 요구사항

### 시스템 요구사항
- **Node.js**: 18.x 이상
- **Python**: 3.8 이상
- **Docker**: 20.x 이상 (권장)
- **Docker Compose**: 2.x 이상

### 외부 서비스
- **Supabase**: 데이터베이스 (무료 계층 사용 가능)
- **OpenAI API**: AI 리포트 생성 (유료)

## 🛠️ 배포 방법

### 1. Docker를 이용한 배포 (권장)

#### 환경 변수 설정
```bash
# .env.production을 .env.local로 복사
cp .env.production .env.local

# 필요한 값들을 편집
nano .env.local
```

#### 원클릭 배포
```bash
# 배포 스크립트 실행
./scripts/deploy.sh
```

#### 수동 배포
```bash
# 이미지 빌드
docker-compose build

# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f app
```

### 2. 개발 환경 배포

#### 의존성 설치
```bash
# Node.js 패키지 설치
npm install

# Python 패키지 설치
pip install -r requirements.txt
```

#### 개발 서버 실행
```bash
# Next.js 개발 서버
npm run dev

# 또는 프로덕션 빌드
npm run build
npm start
```

## 🔧 환경 변수 설정

### 필수 환경 변수

```env
# Next.js
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://your-domain.com

# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key
```

### 선택적 환경 변수

```env
# Analytics
NEXT_PUBLIC_GA_ID=your_google_analytics_id

# Security
NEXTAUTH_SECRET=your_random_secret

# Rate Limiting
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token
```

## 🌐 클라우드 배포

### Vercel 배포

1. **Vercel CLI 설치**
   ```bash
   npm i -g vercel
   ```

2. **프로젝트 배포**
   ```bash
   vercel --prod
   ```

3. **환경 변수 설정**
   - Vercel 대시보드에서 환경 변수 추가
   - Python 백엔드는 별도 서버 필요

### Railway 배포

1. **Railway CLI 설치**
   ```bash
   npm install -g @railway/cli
   ```

2. **프로젝트 배포**
   ```bash
   railway login
   railway deploy
   ```

### AWS/GCP/Azure 배포

Docker 이미지를 사용하여 각 클라우드 서비스에 배포 가능:

```bash
# 이미지 빌드 및 태그
docker build -t vootcamp-ph .
docker tag vootcamp-ph your-registry/vootcamp-ph:latest

# 레지스트리에 푸시
docker push your-registry/vootcamp-ph:latest
```

## 🔍 헬스 체크

배포 후 다음 엔드포인트로 서비스 상태 확인:

```bash
curl http://localhost:3000/api/health
```

응답 예시:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-05T10:30:00.000Z",
  "version": "1.0.0",
  "environment": "production",
  "uptime": 3600,
  "memory": {
    "used": 45.2,
    "total": 64.0
  }
}
```

## 📊 모니터링

### 로그 확인
```bash
# Docker 로그
docker-compose logs -f app

# 애플리케이션 로그
tail -f logs/app.log
```

### 성능 모니터링
- **메모리 사용량**: 일반적으로 64MB 이하
- **응답 시간**: API 요청 < 2초
- **업타임**: 99.9% 목표

## 🔧 문제 해결

### 일반적인 문제

1. **포트 충돌**
   ```bash
   # 다른 포트 사용
   PORT=3001 npm start
   ```

2. **Python 모듈 오류**
   ```bash
   # 의존성 재설치
   pip install -r requirements.txt --force-reinstall
   ```

3. **Docker 빌드 실패**
   ```bash
   # 캐시 없이 재빌드
   docker-compose build --no-cache
   ```

### 로그 분석

중요한 로그 패턴:
- `✅ Successfully generated report`: 정상 리포트 생성
- `💥 Error in generate API`: API 오류
- `🚀 Cache hit`: 캐시 적중

## 🔒 보안 고려사항

1. **환경 변수 보안**
   - `.env` 파일은 절대 커밋하지 않음
   - 프로덕션에서는 보안 저장소 사용

2. **API 키 관리**
   - OpenAI API 키 사용량 모니터링
   - 필요시 API 키 로테이션

3. **네트워크 보안**
   - HTTPS 사용 필수
   - 방화벽 설정

## 📈 확장성

### 수평 확장
```bash
# 여러 인스턴스 실행
docker-compose up --scale app=3
```

### 성능 최적화
- Redis 캐싱 활성화
- CDN 사용 (이미지, 정적 파일)
- 로드 밸런서 설정

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 헬스 체크 엔드포인트
2. 애플리케이션 로그
3. 환경 변수 설정
4. 외부 서비스 상태 (Supabase, OpenAI)

---

**🎉 배포 완료 후 http://localhost:3000 에서 애플리케이션을 확인하세요!**