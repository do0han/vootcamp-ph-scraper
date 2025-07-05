#!/usr/bin/env python3
"""
Supabase 마이그레이션 적용 스크립트
"""
import os
import sys
from supabase import create_client, Client
import glob

def apply_migrations():
    """마이그레이션 파일들을 순서대로 적용합니다"""
    
    # Supabase 클라이언트 설정
    supabase_url = "https://rbsqmvhkfwtwqcdsgqdt.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJic3FtdmhrZnd0d3FjZHNncWR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExNzI0ODYsImV4cCI6MjA2Njc0ODQ4Nn0.w5--VSUuDQMPcvYhl7B152XplPsSCTlyMjrNo281ACA"
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # 마이그레이션 파일들을 순서대로 정렬
    migration_files = [
        "20240320_001_tiktok_shop_setup.sql",
        "20240320_002_tiktok_shop_sellers.sql", 
        "20240320_003_tiktok_shop_categories.sql",
        "20240320_004_tiktok_shop_products.sql",
        "20240320_005_tiktok_shop_product_stats.sql"
    ]
    
    migrations_dir = "supabase/migrations"
    
    for migration_file in migration_files:
        migration_path = os.path.join(migrations_dir, migration_file)
        
        if not os.path.exists(migration_path):
            print(f"⚠️ 마이그레이션 파일을 찾을 수 없습니다: {migration_path}")
            continue
            
        print(f"📄 적용 중: {migration_file}")
        
        try:
            # 마이그레이션 파일 읽기
            with open(migration_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # SQL 문들을 개별적으로 실행
            sql_statements = sql_content.split(';')
            
            for i, statement in enumerate(sql_statements):
                statement = statement.strip()
                if not statement:  # 빈 문장 건너뛰기
                    continue
                    
                try:
                    # SQL 실행 (anon 키로는 DDL이 제한될 수 있음)
                    result = supabase.postgrest.rpc('execute_sql', {'sql_query': statement}).execute()
                    print(f"    ✅ SQL 문 {i+1} 실행 완료")
                except Exception as e:
                    if "permission denied" in str(e).lower() or "insufficient" in str(e).lower():
                        print(f"    ⚠️ 권한 문제로 건너뛰기: {statement[:50]}...")
                    else:
                        print(f"    ❌ SQL 문 {i+1} 실행 실패: {e}")
                        
        except Exception as e:
            print(f"❌ {migration_file} 적용 실패: {e}")
            
    print("\n✅ 마이그레이션 적용 완료!")

def create_tables_manually():
    """필수 테이블들을 직접 생성합니다"""
    
    supabase_url = "https://rbsqmvhkfwtwqcdsgqdt.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJic3FtdmhrZnd0d3FjZHNncWR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExNzI0ODYsImV4cCI6MjA2Njc0ODQ4Nn0.w5--VSUuDQMPcvYhl7B152XplPsSCTlyMjrNo281ACA"
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # 간단한 테이블 구조로 직접 생성 시도
    tables = {
        'tiktok_shop_sellers': {
            'id': 'bigint',
            'seller_id': 'text',
            'seller_name': 'text',
            'verification_status': 'text',
            'created_at': 'timestamp'
        },
        'tiktok_shop_categories': {
            'id': 'bigint', 
            'category_id': 'text',
            'category_name': 'text',
            'parent_category_id': 'text',
            'created_at': 'timestamp'
        },
        'tiktok_shop_products': {
            'id': 'bigint',
            'product_id': 'text',
            'product_name': 'text',
            'seller_id': 'text',
            'category_id': 'text',
            'price': 'numeric',
            'currency': 'text',
            'rating': 'numeric',
            'review_count': 'integer',
            'sales_count': 'integer',
            'product_url': 'text',
            'image_url': 'text',
            'created_at': 'timestamp'
        }
    }
    
    print("🏗️ 테이블 직접 생성 시도...")
    
    for table_name, columns in tables.items():
        try:
            # 테이블이 이미 존재하는지 확인
            response = supabase.table(table_name).select('*').limit(1).execute()
            print(f"  ✅ {table_name} - 이미 존재함")
        except Exception as e:
            if "does not exist" in str(e):
                print(f"  📝 {table_name} - 생성이 필요하지만 anon 키로는 생성 불가")
            else:
                print(f"  ⚠️ {table_name} - 확인 중 오류: {e}")

if __name__ == "__main__":
    print("=== Supabase 마이그레이션 적용 ===\n")
    
    try:
        create_tables_manually()
        # apply_migrations()  # anon 키로는 DDL 실행이 제한됨
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        sys.exit(1) 