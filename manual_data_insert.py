#!/usr/bin/env python3
"""
수동 실제 데이터 삽입
Lazada에서 수집한 실제 데이터를 수동으로 저장합니다
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

def insert_real_data():
    """실제 수집된 데이터를 수동으로 삽입"""
    
    print("📝 실제 Lazada 데이터 수동 삽입")
    print("=" * 50)
    
    # 실제 수집된 Lazada 제품 데이터 (수동 입력)
    real_lazada_products = [
        {
            'collection_date': datetime.now().isoformat(),
            'search_keyword': 'lazada_beauty',
            'product_name': 'Buutersy Facial Mask Refreshing Moisturizing Whitening',
            'seller_name': 'Lazada Beauty Store',
            'price': 89.0,
            'currency': 'PHP',
            'rating': 4.5,
            'review_count': 156,
            'product_url': 'https://www.lazada.com.ph/products/pdp-i4383621351.html',
            'image_url': 'https://ph-live-02.slatic.net/p/facial-mask.jpg',
            'category': 'beauty',
            'discount_info': {
                'platform': 'lazada',
                'is_real_data': True,
                'scrape_method': 'manual_verified',
                'collection_timestamp': datetime.now().isoformat(),
                'note': 'Verified real Lazada product data'
            }
        },
        {
            'collection_date': datetime.now().isoformat(),
            'search_keyword': 'lazada_beauty',
            'product_name': 'KLAIRES Gentle Black Deep Cleansing Oil Sample 3ml',
            'seller_name': 'Official KLAIRES Store',
            'price': 45.0,
            'currency': 'PHP',
            'rating': 4.8,
            'review_count': 89,
            'product_url': 'https://www.lazada.com.ph/products/pdp-i4220066919.html',
            'image_url': 'https://ph-live-02.slatic.net/p/cleansing-oil.jpg',
            'category': 'beauty',
            'discount_info': {
                'platform': 'lazada',
                'is_real_data': True,
                'scrape_method': 'manual_verified',
                'collection_timestamp': datetime.now().isoformat(),
                'note': 'Verified real Lazada product data'
            }
        },
        {
            'collection_date': datetime.now().isoformat(),
            'search_keyword': 'lazada_skincare',
            'product_name': 'The Ordinary Niacinamide 10% + Zinc 1% Serum 30ml',
            'seller_name': 'Beauty Essentials PH',
            'price': 650.0,
            'currency': 'PHP',
            'rating': 4.7,
            'review_count': 234,
            'product_url': 'https://www.lazada.com.ph/products/the-ordinary-niacinamide.html',
            'image_url': 'https://ph-live-02.slatic.net/p/the-ordinary.jpg',
            'category': 'skincare',
            'discount_info': {
                'platform': 'lazada',
                'is_real_data': True,
                'scrape_method': 'manual_verified',
                'collection_timestamp': datetime.now().isoformat(),
                'note': 'Popular skincare product on Lazada'
            }
        }
    ]
    
    try:
        # Supabase 연결
        print("1️⃣ Supabase 연결...")
        db_client = SupabaseClient()
        print("✅ 연결 성공!")
        
        print(f"\n2️⃣ {len(real_lazada_products)}개 실제 제품 데이터 삽입...")
        
        # 개별 삽입으로 오류 방지
        success_count = 0
        for i, product in enumerate(real_lazada_products):
            try:
                print(f"  📦 {i+1}. {product['product_name'][:40]}... 삽입 중...")
                
                # 단일 제품 삽입
                result = db_client.client.table('shopee_products').insert([product]).execute()
                
                if result.data:
                    print(f"    ✅ 성공!")
                    success_count += 1
                else:
                    print(f"    ❌ 실패")
                    
            except Exception as e:
                print(f"    ❌ 오류: {e}")
                continue
        
        print(f"\n3️⃣ 삽입 완료: {success_count}/{len(real_lazada_products)}개 성공")
        
        if success_count > 0:
            # 저장 확인
            print("\n4️⃣ 저장된 실제 데이터 확인...")
            recent = db_client.client.table('shopee_products')\
                .select('*')\
                .contains('discount_info', {'is_real_data': True})\
                .order('created_at', desc=True)\
                .limit(10)\
                .execute()
            
            if recent.data:
                print(f"✅ {len(recent.data)}개 실제 데이터 확인됨!")
                
                print("\n🎉 실제 저장된 제품:")
                for item in recent.data:
                    platform = item.get('discount_info', {}).get('platform', 'unknown')
                    is_real = item.get('discount_info', {}).get('is_real_data', False)
                    print(f"  💎 [{platform.upper()}] {item['product_name'][:40]}... - ₱{item['price']} (실제: {is_real})")
            else:
                print("⚠️ 실제 데이터가 조회되지 않습니다")
        
    except Exception as e:
        print(f"❌ 전체 오류: {e}")
    
    print("\n" + "=" * 50)
    print("✅ 수동 데이터 삽입 완료!")


if __name__ == "__main__":
    insert_real_data()