#!/usr/bin/env python3
"""
실제 데이터 수집 테스트
Lazada에서 실제 제품 데이터를 수집하고 Supabase에 저장
"""

import sys
import time
import logging
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

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/real_data_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_real_data_collection():
    """실제 데이터 수집 및 저장 테스트"""
    
    print("🚀 실제 데이터 수집 테스트 시작")
    print("=" * 60)
    
    try:
        # Supabase 연결 테스트
        print("1️⃣ Supabase 연결 테스트...")
        db_client = SupabaseClient()
        print("✅ Supabase 연결 성공!")
        
        # Lazada 스크래퍼 초기화
        print("\n2️⃣ Lazada 스크래퍼 초기화...")
        scraper = LazadaScraper(use_undetected=True)
        print("✅ Lazada 스크래퍼 준비 완료!")
        
        # 실제 데이터 수집
        print("\n3️⃣ 실제 Lazada 데이터 수집 중...")
        
        categories = ["skincare", "beauty", "phone", "laptop"]
        all_products = []
        
        for i, category in enumerate(categories):
            try:
                print(f"\n🔍 카테고리 {i+1}/{len(categories)}: {category}")
                products = scraper.search_products(category, limit=3)
                
                if products:
                    print(f"  ✅ {len(products)}개 실제 제품 발견!")
                    
                    # 제품 정보 출력
                    for j, product in enumerate(products):
                        print(f"  📦 제품 {j+1}: {product['product_name'][:40]}...")
                        print(f"     가격: {product['price']}")
                        print(f"     URL: {product['product_url'][:60]}...")
                    
                    all_products.extend(products)
                else:
                    print(f"  ⚠️ {category}에서 제품을 찾지 못했습니다")
                
                # 카테고리 간 대기
                if i < len(categories) - 1:
                    print(f"  ⏳ 3초 대기...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"  ❌ {category} 검색 중 오류: {e}")
                continue
        
        print(f"\n4️⃣ 수집 완료! 총 {len(all_products)}개 실제 제품 수집됨")
        
        if all_products:
            # 데이터베이스 저장
            print("\n5️⃣ Supabase 데이터베이스에 저장 중...")
            
            # 데이터 포맷팅
            formatted_products = []
            for product in all_products:
                formatted_product = {
                    'collection_date': datetime.now().isoformat(),
                    'search_keyword': product.get('search_keyword', 'test'),
                    'product_name': product.get('product_name', 'Unknown Product'),
                    'seller_name': 'Lazada Seller',
                    'price': extract_price(product.get('price', '0')),
                    'currency': 'PHP',
                    'rating': product.get('rating'),
                    'review_count': product.get('review_count'),
                    'product_url': product.get('product_url'),
                    'image_url': product.get('image_url'),
                    'category': product.get('category', 'general'),
                    'discount_info': {
                        'platform': 'lazada',
                        'is_real_data': True,
                        'scrape_method': 'real_data_test',
                        'collection_timestamp': datetime.now().isoformat()
                    }
                }
                formatted_products.append(formatted_product)
            
            # Supabase에 저장
            success = db_client.insert_shopee_products(formatted_products)
            
            if success:
                print(f"✅ {len(formatted_products)}개 실제 제품이 Supabase에 저장되었습니다!")
                
                # 저장된 데이터 확인
                print("\n6️⃣ 저장된 데이터 확인...")
                recent_data = db_client.client.table('shopee_products')\
                    .select('*')\
                    .order('created_at', desc=True)\
                    .limit(len(formatted_products))\
                    .execute()
                
                if recent_data.data:
                    print(f"✅ 데이터베이스에서 {len(recent_data.data)}개 제품 확인됨!")
                    
                    print("\n📋 저장된 제품 목록:")
                    for i, item in enumerate(recent_data.data[:5]):  # 처음 5개만 표시
                        print(f"  {i+1}. {item['product_name'][:40]}...")
                        print(f"     가격: ₱{item['price']} | 플랫폼: {item['discount_info'].get('platform', 'unknown')}")
                        print(f"     실제 데이터: {item['discount_info'].get('is_real_data', False)}")
                else:
                    print("⚠️ 저장된 데이터를 확인할 수 없습니다")
            else:
                print("❌ 데이터베이스 저장에 실패했습니다")
        else:
            print("⚠️ 수집된 데이터가 없어 저장하지 않습니다")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        logger.error(f"Real data test error: {e}", exc_info=True)
        
    finally:
        # 브라우저 정리
        try:
            if 'scraper' in locals():
                scraper.close()
                print("✅ 브라우저 정리 완료")
        except:
            pass
    
    print("\n" + "=" * 60)
    print("🎉 실제 데이터 수집 테스트 완료!")


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
    test_real_data_collection()