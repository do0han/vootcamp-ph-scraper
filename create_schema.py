#!/usr/bin/env python3
"""
Supabase 데이터베이스 스키마를 자동으로 생성하는 스크립트
"""

import os
import sys
from database.supabase_client import SupabaseClient

def create_database_schema():
    """데이터베이스 스키마 생성"""
    print('🛠️ Supabase 데이터베이스 스키마를 생성합니다...')
    print()

    try:
        # Supabase 클라이언트 생성
        client = SupabaseClient()
        print('✅ Supabase 연결 성공!')
        print()

        # schema.sql 파일 읽기
        schema_path = 'database/schema.sql'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        print('📄 스키마 SQL 파일을 읽었습니다.')
        print()

        # SQL을 개별 명령으로 분할 (세미콜론 기준)
        sql_commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip() and not cmd.strip().startswith('--')]

        print(f'🔧 {len(sql_commands)} 개의 SQL 명령을 실행합니다...')
        print()

        # 각 SQL 명령 실행
        success_count = 0
        for i, sql in enumerate(sql_commands, 1):
            try:
                # 주석과 빈 줄 건너뛰기
                if not sql or sql.startswith('--'):
                    continue

                print(f'  [{i}/{len(sql_commands)}] 실행 중...', end=' ')
                
                # SQL 실행
                result = client.client.rpc('raw_sql', {'sql': sql}).execute()
                
                print('✅')
                success_count += 1
                
            except Exception as e:
                # 이미 존재하는 테이블이나 함수는 무시
                if 'already exists' in str(e).lower() or 'if not exists' in sql.lower():
                    print('✅ (이미 존재)')
                    success_count += 1
                else:
                    print(f'❌ 오류: {e}')

        print()
        print(f'📊 결과: {success_count}/{len(sql_commands)} 명령 성공')
        print()

        # 테이블 확인
        print('🔍 생성된 테이블 확인:')
        tables = ['google_trends', 'shopee_products', 'tiktok_videos']
        
        working_tables = 0
        for table in tables:
            try:
                result = client.client.table(table).select('*').limit(1).execute()
                print(f'  ✅ {table} 테이블 정상')
                working_tables += 1
            except Exception as e:
                print(f'  ❌ {table} 테이블 오류: {e}')

        print()
        
        if working_tables == len(tables):
            print('🎉 모든 테이블이 성공적으로 생성되었습니다!')
            print()
            print('📝 다음 단계:')
            print('1. python3 main.py 실행하여 데이터 수집 시작')
            print('2. Supabase 대시보드에서 실시간 데이터 확인')
            return True
        else:
            print('⚠️ 일부 테이블 생성에 문제가 있습니다.')
            print('Supabase 대시보드의 SQL Editor에서 수동으로 스키마를 실행해보세요.')
            return False

    except Exception as e:
        print(f'❌ 스키마 생성 실패: {e}')
        print()
        print('🔧 해결 방법:')
        print('1. Supabase 대시보드 → SQL Editor로 이동')
        print('2. database/schema.sql 파일 내용을 복사')
        print('3. SQL Editor에서 실행')
        return False

if __name__ == "__main__":
    success = create_database_schema()
    sys.exit(0 if success else 1)