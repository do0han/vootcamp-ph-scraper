#!/usr/bin/env python3
"""
Supabase 연결 테스트 스크립트 (간단 버전)
"""

import sys
from supabase import create_client, Client

def main():
    """Supabase 연결을 테스트합니다"""
    
    print("=== Supabase 연결 테스트 ===")
    
    # Supabase 설정
    supabase_url = "https://rbsqmvhkfwtwqcdsgqdt.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJic3FtdmhrZnd0d3FjZHNncWR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExNzI0ODYsImV4cCI6MjA2Njc0ODQ4Nn0.w5--VSUuDQMPcvYhl7B152XplPsSCTlyMjrNo281ACA"
    
    try:
        # Supabase 클라이언트 생성
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase 클라이언트 생성 성공")
        
        # 테이블 존재 확인
        tables_to_check = ['google_trends', 'shopee_products', 'tiktok_shop_products']
        
        for table_name in tables_to_check:
            try:
                response = supabase.table(table_name).select('*').limit(1).execute()
                count = len(response.data)
                print(f"✅ {table_name}: {count}개 레코드")
            except Exception as e:
                if "does not exist" in str(e):
                    print(f"❌ {table_name}: 테이블 없음")
                else:
                    print(f"⚠️ {table_name}: 오류 - {e}")
        
        print("\n🎉 Supabase 연결 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return False

if __name__ == "__main__":
    main() 