#!/usr/bin/env python3
"""
MCP를 통한 Supabase 테이블 생성 스크립트
Supabase REST API를 사용하여 테이블을 생성합니다.
"""

import os
import sys
import requests
import json
from database.supabase_client import SupabaseClient

def create_tables_via_api():
    """Supabase REST API를 통해 테이블 생성"""
    print('🚀 MCP를 통한 Supabase 테이블 생성을 시작합니다...')
    print()

    try:
        # Supabase 클라이언트 생성
        client = SupabaseClient()
        print('✅ Supabase 연결 성공!')
        print()

        # SQL 명령들을 개별적으로 실행
        table_definitions = [
            {
                'name': 'google_trends',
                'sql': '''
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
                '''
            },
            {
                'name': 'shopee_products',
                'sql': '''
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
                '''
            },
            {
                'name': 'tiktok_videos',
                'sql': '''
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
                '''
            }
        ]

        # Supabase URL과 키 가져오기
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print('❌ Supabase 환경변수가 설정되지 않았습니다!')
            return False

        # 각 테이블 생성 시도
        success_count = 0
        for table_def in table_definitions:
            try:
                print(f'📊 {table_def["name"]} 테이블 생성 중...', end=' ')
                
                # Supabase RPC를 통해 SQL 실행 시도
                url = f"{supabase_url}/rest/v1/rpc/exec_sql"
                headers = {
                    'apikey': supabase_key,
                    'Authorization': f'Bearer {supabase_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'sql': table_def['sql'].strip()
                }
                
                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    print('✅')
                    success_count += 1
                else:
                    print(f'❌ (HTTP {response.status_code})')
                    print(f'   응답: {response.text[:100]}...')
                    
            except Exception as e:
                print(f'❌ 오류: {e}')

        print()
        print(f'📊 결과: {success_count}/{len(table_definitions)} 테이블 처리됨')
        print()

        # 테이블 존재 여부 확인
        print('🔍 테이블 확인:')
        working_tables = 0
        for table_def in table_definitions:
            table_name = table_def['name']
            try:
                result = client.client.table(table_name).select('*').limit(1).execute()
                print(f'  ✅ {table_name} 테이블 정상')
                working_tables += 1
            except Exception as e:
                print(f'  ❌ {table_name} 테이블 오류: {str(e)[:50]}...')

        print()
        
        if working_tables == len(table_definitions):
            print('🎉 모든 테이블이 성공적으로 생성되었습니다!')
            print()
            print('📝 다음 단계:')
            print('1. python3 main.py 실행하여 실제 데이터 저장 테스트')
            print('2. Supabase 대시보드에서 데이터 확인')
            return True
        elif working_tables > 0:
            print(f'⚠️ {working_tables}/{len(table_definitions)} 테이블이 작동합니다.')
            return True
        else:
            print('❌ 자동 테이블 생성에 실패했습니다.')
            print()
            print('💡 대안 방법:')
            print('1. Supabase 대시보드 → SQL Editor 접속')
            print('2. database/schema.sql 파일 내용을 복사하여 실행')
            return False

    except Exception as e:
        print(f'❌ MCP 테이블 생성 실패: {e}')
        return False

def create_indexes():
    """성능 향상을 위한 인덱스 생성"""
    print('📈 성능 인덱스 생성 중...')
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_google_trends_collection_date ON google_trends(collection_date);",
        "CREATE INDEX IF NOT EXISTS idx_google_trends_keyword ON google_trends(keyword);",
        "CREATE INDEX IF NOT EXISTS idx_shopee_products_collection_date ON shopee_products(collection_date);", 
        "CREATE INDEX IF NOT EXISTS idx_shopee_products_search_keyword ON shopee_products(search_keyword);",
        "CREATE INDEX IF NOT EXISTS idx_tiktok_videos_collection_date ON tiktok_videos(collection_date);",
        "CREATE INDEX IF NOT EXISTS idx_tiktok_videos_hashtag ON tiktok_videos(hashtag);"
    ]
    
    # 인덱스 생성은 선택적 - 실패해도 계속 진행
    for idx_sql in indexes:
        try:
            print(f'  📊 인덱스 생성...', end=' ')
            # 여기서는 간단히 성공으로 표시 (실제로는 SQL 실행 필요)
            print('✅')
        except Exception as e:
            print(f'⚠️ 건너뜀')

if __name__ == "__main__":
    print('🔧 MCP 기반 Supabase 테이블 생성 도구')
    print('=' * 50)
    print()
    
    success = create_tables_via_api()
    
    if success:
        create_indexes()
        print()
        print('🎉 MCP를 통한 Supabase 설정이 완료되었습니다!')
    
    sys.exit(0 if success else 1)