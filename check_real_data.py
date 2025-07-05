#!/usr/bin/env python3
"""
실제 데이터 확인 스크립트
Supabase에 저장된 실제 Lazada 데이터를 확인합니다
"""

import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

# Supabase 클라이언트
from database.supabase_client import SupabaseClient

def check_real_data():
    """저장된 실제 데이터 확인"""
    
    print("🔍 Supabase에 저장된 실제 데이터 확인")
    print("=" * 60)
    
    try:
        # Supabase 연결
        db_client = SupabaseClient()
        print("✅ Supabase 연결 성공!")
        
        # 최근 데이터 조회 (플랫폼별)
        print("\n📊 최근 저장된 제품 데이터:")
        
        # 전체 데이터 조회
        all_products = db_client.client.table('shopee_products')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(20)\
            .execute()
        
        if all_products.data:
            print(f"✅ 총 {len(all_products.data)}개 제품 발견 (최근 20개)")
            
            # 플랫폼별 분류
            shopee_count = 0
            lazada_count = 0
            sample_count = 0
            real_count = 0
            
            print("\n📦 제품 목록:")
            for i, product in enumerate(all_products.data):
                platform = product.get('discount_info', {}).get('platform', 'shopee')
                is_real = product.get('discount_info', {}).get('is_real_data', False)
                scrape_method = product.get('discount_info', {}).get('scrape_method', 'unknown')
                
                print(f"\n{i+1:2d}. {product['product_name'][:50]}...")
                print(f"    💰 가격: ₱{product['price']}")
                print(f"    🏪 플랫폼: {platform}")
                print(f"    ✅ 실제 데이터: {is_real}")
                print(f"    🔧 수집 방법: {scrape_method}")
                print(f"    📅 수집 시간: {product['created_at'][:19]}")
                
                if platform == 'lazada':
                    lazada_count += 1
                else:
                    shopee_count += 1
                
                if is_real:
                    real_count += 1
                else:
                    sample_count += 1
                
                if product.get('product_url'):
                    print(f"    🔗 URL: {product['product_url'][:70]}...")
            
            print(f"\n📈 통계:")
            print(f"  🛒 Shopee 데이터: {shopee_count}개")
            print(f"  🛍️ Lazada 데이터: {lazada_count}개")
            print(f"  ✅ 실제 데이터: {real_count}개")
            print(f"  🎭 샘플 데이터: {sample_count}개")
            
            # 실제 데이터만 필터링
            if real_count > 0:
                print(f"\n🎉 성공! {real_count}개의 실제 데이터가 수집되었습니다!")
                
                # 실제 데이터만 다시 조회
                real_products = db_client.client.table('shopee_products')\
                    .select('*')\
                    .contains('discount_info', {'is_real_data': True})\
                    .order('created_at', desc=True)\
                    .limit(10)\
                    .execute()
                
                if real_products.data:
                    print(f"\n🔥 실제 수집된 제품 Top {len(real_products.data)}:")
                    for i, product in enumerate(real_products.data):
                        platform = product.get('discount_info', {}).get('platform', 'unknown')
                        print(f"  {i+1}. [{platform.upper()}] {product['product_name'][:40]}... - ₱{product['price']}")
            else:
                print("\n⚠️ 실제 데이터가 아직 없습니다. 샘플 데이터만 있습니다.")
        else:
            print("⚠️ 저장된 데이터가 없습니다.")
            
    except Exception as e:
        print(f"❌ 데이터 확인 중 오류: {e}")
    
    print("\n" + "=" * 60)


def check_database_schema():
    """데이터베이스 스키마 확인"""
    print("\n🗄️ 데이터베이스 스키마 확인:")
    
    try:
        db_client = SupabaseClient()
        
        # 샘플 데이터로 스키마 확인
        sample = db_client.client.table('shopee_products')\
            .select('*')\
            .limit(1)\
            .execute()
        
        if sample.data:
            print("✅ shopee_products 테이블 구조:")
            for key in sample.data[0].keys():
                print(f"  - {key}")
        else:
            print("⚠️ 테이블이 비어있어 스키마를 확인할 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 스키마 확인 오류: {e}")


if __name__ == "__main__":
    check_real_data()
    check_database_schema()