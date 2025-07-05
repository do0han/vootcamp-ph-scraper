#!/usr/bin/env python3
"""
Supabase 테이블을 직접 생성하는 스크립트
"""

import os
import sys
from supabase import create_client

def create_tables_directly():
    """테이블을 직접 생성"""
    print('🛠️ Supabase 테이블을 직접 생성합니다...')
    print()

    # 환경변수에서 자격증명 가져오기
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print('❌ 환경변수가 설정되지 않았습니다!')
        return False

    try:
        # Supabase 클라이언트 생성
        supabase = create_client(url, key)
        print('✅ Supabase 연결 성공!')
        print()

        # 테이블 생성 SQL 명령들
        table_sqls = [
            # Google Trends 테이블
            """
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
            """,
            
            # Shopee Products 테이블
            """
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
            """,
            
            # TikTok Videos 테이블
            """
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
            """
        ]

        table_names = ['google_trends', 'shopee_products', 'tiktok_videos']
        
        print('📊 테이블 생성 상태:')
        
        # 각 테이블 먼저 확인
        for i, table_name in enumerate(table_names):
            try:
                result = supabase.table(table_name).select('*').limit(1).execute()
                print(f'  ✅ {table_name} 이미 존재')
            except Exception:
                print(f'  ❌ {table_name} 생성 필요')

        print()
        print('🎯 해결 방법:')
        print('Supabase에서 자동 테이블 생성에 제한이 있습니다.')
        print('다음 중 하나의 방법을 선택하세요:')
        print()
        print('방법 1: Supabase 대시보드 사용 (권장)')
        print('1. https://supabase.com/dashboard 접속')
        print('2. 프로젝트 선택 → SQL Editor')
        print('3. 아래 SQL을 복사하여 실행:')
        print()
        
        # 전체 스키마 출력
        with open('database/schema.sql', 'r') as f:
            schema_content = f.read()
        
        print('=' * 60)
        print(schema_content)
        print('=' * 60)
        print()
        
        print('방법 2: 임시 테스트 (현재 가능)')
        print('스키마 없이 Mock 데이터로 시스템 테스트를 진행할 수 있습니다.')
        
        return False

    except Exception as e:
        print(f'❌ 오류 발생: {e}')
        return False

if __name__ == "__main__":
    success = create_tables_directly()
    sys.exit(0 if success else 1)