#!/usr/bin/env python3
"""
실제 Supabase 연결 테스트 스크립트
"""

import os
import sys
from database.supabase_client import SupabaseClient

def test_supabase_connection():
    """Supabase 연결 테스트"""
    print('🧪 실제 Supabase 연결 테스트를 시작합니다...')
    print()

    # 환경변수 확인
    print('📋 설정된 자격증명:')
    url = os.getenv('SUPABASE_URL', '설정되지 않음')
    key = os.getenv('SUPABASE_KEY', '설정되지 않음')
    
    print(f'URL: {url}')
    if key != '설정되지 않음':
        print(f'KEY: {key[:20]}...{key[-10:]}')
    else:
        print('KEY: 설정되지 않음')
    print()

    if url == '설정되지 않음' or key == '설정되지 않음':
        print('❌ 환경변수가 설정되지 않았습니다!')
        return False

    try:
        # Supabase 클라이언트 생성
        client = SupabaseClient()
        print('✅ Supabase 연결 성공!')
        print()
        
        # 테이블 존재 여부 확인
        print('📊 테이블 상태 확인:')
        tables = ['google_trends', 'shopee_products', 'tiktok_videos']
        
        table_status = {}
        for table in tables:
            try:
                result = client.client.table(table).select('*').limit(1).execute()
                print(f'  ✅ {table} 테이블 정상 (레코드 수: {len(result.data)})')
                table_status[table] = True
            except Exception as e:
                print(f'  ❌ {table} 테이블 오류: {e}')
                if 'relation' in str(e).lower() and 'does not exist' in str(e).lower():
                    print(f'     → 스키마가 생성되지 않았습니다.')
                table_status[table] = False
        
        print()
        
        # 결과 요약
        working_tables = sum(table_status.values())
        total_tables = len(table_status)
        
        if working_tables == total_tables:
            print('🎉 모든 테이블이 정상적으로 작동합니다!')
            return True
        elif working_tables > 0:
            print(f'⚠️ {working_tables}/{total_tables} 테이블이 작동합니다.')
            print('나머지 테이블을 위해 SQL 스키마를 실행하세요.')
            return True
        else:
            print('❌ 모든 테이블에 문제가 있습니다.')
            print('SUPABASE_SETUP_GUIDE.md의 2단계를 확인하여 스키마를 생성하세요.')
            return False
        
    except Exception as e:
        print(f'❌ 연결 실패: {e}')
        print()
        print('🔧 가능한 원인:')
        print('1. 자격증명이 올바르지 않음')
        print('2. 프로젝트가 활성화되지 않음')
        print('3. 네트워크 연결 문제')
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)