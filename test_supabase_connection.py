#!/usr/bin/env python3
"""
Supabase 연결 테스트 스크립트
"""
import os
import sys
from supabase import create_client, Client

def test_supabase_connection():
    """Supabase 연결을 테스트합니다"""
    
    # 환경변수에서 Supabase 설정 읽기 (.env 파일의 올바른 키 사용)
    supabase_url = "https://rbsqmvhkfwtwqcdsgqdt.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJic3FtdmhrZnd0d3FjZHNncWR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExNzI0ODYsImV4cCI6MjA2Njc0ODQ4Nn0.w5--VSUuDQMPcvYhl7B152XplPsSCTlyMjrNo281ACA"
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase URL 또는 Key가 설정되지 않았습니다.")
            return False
        
    try:
        # Supabase 클라이언트 생성
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase 클라이언트 생성 성공")
        
        # 간단한 연결 테스트 - 존재하지 않는 테이블 조회로 연결 확인
        try:
            response = supabase.table('test_connection').select('*').limit(1).execute()
            print("✅ Supabase 연결 성공!")
        except Exception as e:
            if "does not exist" in str(e):
                print("✅ Supabase 연결 성공! (테이블이 없는 것은 정상)")
            else:
                raise e
        
        # TikTok Shop 테이블 존재 여부 확인
        tiktok_tables = [
            'tiktok_shop_products',
            'tiktok_shop_sellers', 
            'tiktok_shop_categories',
            'google_trends',
            'shopee_products'
        ]
        
        print("\n🔍 필요한 테이블 존재 확인:")
        existing_tables = []
        for table_name in tiktok_tables:
            try:
                response = supabase.table(table_name).select('*').limit(1).execute()
                existing_tables.append(table_name)
                print(f"  ✅ {table_name} - 존재함")
        except Exception as e:
                if "does not exist" in str(e):
                    print(f"  ❌ {table_name} - 생성 필요")
                else:
                    print(f"  ⚠️ {table_name} - 확인 중 오류: {e}")
        
        if existing_tables:
            print(f"\n🎯 기존 테이블 {len(existing_tables)}개 발견!")
        else:
            print(f"\n📝 마이그레이션이 필요합니다.")
            
        return True
        
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return False

def check_environment():
    """환경 설정을 확인합니다"""
    print("🔍 환경 설정 확인:")
    print(f"  - Python 버전: {sys.version}")
    
    try:
        import supabase
        print(f"  - Supabase 라이브러리: {supabase.__version__}")
    except ImportError:
        print("  - ❌ Supabase 라이브러리가 설치되지 않았습니다.")
        return False
    except AttributeError:
        print("  - ✅ Supabase 라이브러리 설치됨 (버전 확인 불가)")
    
    return True

if __name__ == "__main__":
    print("=== Supabase 연결 테스트 ===\n")
    
    if not check_environment():
        print("\n❌ 환경 설정에 문제가 있습니다.")
        sys.exit(1)
    
    if test_supabase_connection():
        print("\n🎉 Supabase 연동이 성공적으로 완료되었습니다!")
    else:
        print("\n💥 Supabase 연동에 실패했습니다.")
        sys.exit(1)