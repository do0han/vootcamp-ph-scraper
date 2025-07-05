#!/usr/bin/env python3
"""
빠른 실제 데이터 테스트
Lazada에서 소량의 실제 데이터를 수집하고 저장
"""

import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

# Supabase 클라이언트
from database.supabase_client import SupabaseClient

# Lazada 스크래퍼
from scrapers.lazada_scraper import LazadaScraper

def quick_test():
    """빠른 실제 데이터 테스트"""
    
    print("⚡ 빠른 실제 데이터 수집 테스트")
    print("=" * 50)
    
    try:
        # Supabase 연결
        print("1️⃣ Supabase 연결...")
        db_client = SupabaseClient()
        print("✅ 연결 성공!")
        
        # Lazada 스크래퍼 초기화
        print("\n2️⃣ Lazada 스크래퍼 초기화...")
        scraper = LazadaScraper(use_undetected=True)
        print("✅ 스크래퍼 준비 완료!")
        
        # 단일 카테고리 테스트
        print("\n3️⃣ 'beauty' 카테고리에서 2개 제품 수집...")
        products = scraper.search_products("beauty", limit=2)
        
        if products:
            print(f"✅ {len(products)}개 실제 제품 수집됨!")
            
            # 제품 정보 출력
            for i, product in enumerate(products):
                print(f"\n📦 제품 {i+1}:")
                print(f"  이름: {product['product_name'][:50]}...")
                print(f"  가격: {product['price']}")
                print(f"  URL: {product['product_url'][:60]}...")
            
            # 데이터베이스 저장용 포맷팅
            print("\n4️⃣ 데이터베이스 저장 중...")
            
            formatted_products = []
            for product in products:
                formatted_product = {
                    'collection_date': datetime.now().isoformat(),
                    'search_keyword': 'quick_test_beauty',
                    'product_name': product.get('product_name', 'Unknown Product'),
                    'seller_name': 'Lazada Seller',
                    'price': extract_price(product.get('price', '0')),
                    'currency': 'PHP',
                    'rating': product.get('rating'),
                    'review_count': product.get('review_count'),
                    'product_url': product.get('product_url'),
                    'image_url': product.get('image_url'),
                    'category': 'beauty',
                    'discount_info': {
                        'platform': 'lazada',
                        'is_real_data': True,
                        'scrape_method': 'quick_test',
                        'collection_timestamp': datetime.now().isoformat()
                    }
                }
                formatted_products.append(formatted_product)
            
            # Supabase에 저장
            success = db_client.insert_shopee_products(formatted_products)
            
            if success:
                print(f"✅ {len(formatted_products)}개 실제 제품이 저장되었습니다!")
                
                # 저장 확인
                print("\n5️⃣ 저장 확인...")
                recent = db_client.client.table('shopee_products')\
                    .select('*')\
                    .order('created_at', desc=True)\
                    .limit(len(formatted_products))\
                    .execute()
                
                if recent.data:
                    print("✅ 저장 확인됨:")
                    for item in recent.data:
                        platform = item.get('discount_info', {}).get('platform', 'unknown')
                        is_real = item.get('discount_info', {}).get('is_real_data', False)
                        print(f"  - [{platform.upper()}] {item['product_name'][:30]}... (실제: {is_real})")
                
            else:
                print("❌ 저장 실패")
        else:
            print("❌ 제품을 찾지 못했습니다")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        
    finally:
        try:
            if 'scraper' in locals():
                scraper.close()
                print("\n✅ 브라우저 정리 완료")
        except:
            pass
    
    print("\n" + "=" * 50)
    print("🎉 빠른 테스트 완료!")


def extract_price(price_str):
    """가격 문자열에서 숫자 추출"""
    try:
        if not price_str:
            return None
        import re
        match = re.search(r'[\d,]+\.?\d*', str(price_str).replace(',', ''))
        if match:
            return float(match.group())
        return None
    except:
        return None


if __name__ == "__main__":
    quick_test()