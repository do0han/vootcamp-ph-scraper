#!/usr/bin/env python3
"""
TikTok Shop 간단한 테이블 생성 및 샘플 데이터 삽입
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

from database.supabase_client import SupabaseClient

def create_tiktok_shop_table_simple():
    """기존 shopee_products 테이블을 TikTok Shop 데이터에도 활용"""
    
    print("🎬 TikTok Shop 데이터 생성 (기존 테이블 활용)")
    print("=" * 60)
    
    try:
        # Supabase 클라이언트 초기화
        supabase_client = SupabaseClient()
        print("✅ Supabase 연결 성공")
        
        # 기존 shopee_products 테이블 구조 확인
        try:
            existing_test = supabase_client.client.table('shopee_products').select('*').limit(1).execute()
            print("✅ 기존 shopee_products 테이블 확인 완료")
            print("💡 TikTok Shop 데이터를 shopee_products 테이블에 저장합니다")
        except Exception as e:
            print(f"❌ shopee_products 테이블 접근 실패: {e}")
            return False
        
        # TikTok Shop 샘플 데이터 생성
        tiktok_sample_products = [
            # Young Filipina 타겟 제품들
            {
                'collection_date': datetime.now().isoformat(),
                'search_keyword': 'k-beauty',
                'product_name': 'COSRX Advanced Snail 96 Mucin Power Essence',
                'seller_name': 'COSRX Official TikTok Shop',
                'price': 899.00,
                'currency': 'PHP',
                'rating': 4.8,
                'review_count': 1580,
                'sales_count': 5200,
                'product_url': 'https://www.tiktok.com/shop/ph/product/cosrx-snail-essence-001',
                'image_url': 'https://example.com/cosrx-snail-essence.jpg',
                'category': 'beauty',
                'discount_info': {
                    'platform': 'tiktok_shop',
                    'is_real_data': False,
                    'scrape_method': 'sample_data',
                    'source_type': 'top_products',
                    'persona_name': 'young_filipina',
                    'persona_score': 92.5,
                    'brand': 'COSRX',
                    'is_viral': True,
                    'tiktok_mentions': 1250,
                    'original_price': 1200.00,
                    'discount_percentage': 25,
                    'creator_info': {
                        'creator_name': 'Maria Beauty PH',
                        'creator_username': '@mariabeautyph',
                        'follower_count': 250000
                    }
                }
            },
            {
                'collection_date': datetime.now().isoformat(),
                'search_keyword': 'korean skincare',
                'product_name': 'The Ordinary Niacinamide 10% + Zinc 1%',
                'seller_name': 'The Ordinary TikTok Shop',
                'price': 450.00,
                'currency': 'PHP',
                'rating': 4.6,
                'review_count': 890,
                'sales_count': 3100,
                'product_url': 'https://www.tiktok.com/shop/ph/product/the-ordinary-niacinamide-002',
                'image_url': 'https://example.com/the-ordinary-niacinamide.jpg',
                'category': 'beauty',
                'discount_info': {
                    'platform': 'tiktok_shop',
                    'is_real_data': False,
                    'scrape_method': 'sample_data',
                    'source_type': 'flash_sale',
                    'persona_name': 'young_filipina',
                    'persona_score': 88.3,
                    'brand': 'The Ordinary',
                    'is_viral': True,
                    'tiktok_mentions': 980,
                    'original_price': 650.00,
                    'discount_percentage': 31,
                    'creator_info': {
                        'creator_name': 'Maria Beauty PH',
                        'creator_username': '@mariabeautyph',
                        'follower_count': 250000
                    }
                }
            },
            {
                'collection_date': datetime.now().isoformat(),
                'search_keyword': 'innisfree',
                'product_name': 'Innisfree Green Tea Seed Serum',
                'seller_name': 'Innisfree Philippines',
                'price': 750.00,
                'currency': 'PHP',
                'rating': 4.7,
                'review_count': 2100,
                'sales_count': 4500,
                'product_url': 'https://www.tiktok.com/shop/ph/product/innisfree-green-tea-003',
                'image_url': 'https://example.com/innisfree-green-tea.jpg',
                'category': 'beauty',
                'discount_info': {
                    'platform': 'tiktok_shop',
                    'is_real_data': False,
                    'scrape_method': 'sample_data',
                    'source_type': 'category_beauty',
                    'persona_name': 'young_filipina',
                    'persona_score': 85.2,
                    'brand': 'Innisfree',
                    'is_viral': False,
                    'tiktok_mentions': 650,
                    'original_price': 950.00,
                    'discount_percentage': 21
                }
            },
            
            # Productivity Seeker 타겟 제품들
            {
                'collection_date': datetime.now().isoformat(),
                'search_keyword': 'ergonomic mouse',
                'product_name': 'Ergonomic Bluetooth Wireless Mouse',
                'seller_name': 'Logitech Official',
                'price': 1250.00,
                'currency': 'PHP',
                'rating': 4.5,
                'review_count': 320,
                'sales_count': 1200,
                'product_url': 'https://www.tiktok.com/shop/ph/product/logitech-mouse-004',
                'image_url': 'https://example.com/logitech-mouse.jpg',
                'category': 'tech',
                'discount_info': {
                    'platform': 'tiktok_shop',
                    'is_real_data': False,
                    'scrape_method': 'sample_data',
                    'source_type': 'top_products',
                    'persona_name': 'productivity_seeker',
                    'persona_score': 78.9,
                    'brand': 'Logitech',
                    'is_viral': False,
                    'tiktok_mentions': 180,
                    'original_price': 1500.00,
                    'discount_percentage': 17,
                    'creator_info': {
                        'creator_name': 'Tech Guy Manila',
                        'creator_username': '@techguymnl',
                        'follower_count': 180000
                    }
                }
            },
            {
                'collection_date': datetime.now().isoformat(),
                'search_keyword': 'blue light glasses',
                'product_name': 'Blue Light Blocking Gaming Glasses',
                'seller_name': 'Gaming Accessories Store',
                'price': 580.00,
                'currency': 'PHP',
                'rating': 4.3,
                'review_count': 150,
                'sales_count': 800,
                'product_url': 'https://www.tiktok.com/shop/ph/product/blue-light-glasses-005',
                'image_url': 'https://example.com/blue-light-glasses.jpg',
                'category': 'tech',
                'discount_info': {
                    'platform': 'tiktok_shop',
                    'is_real_data': False,
                    'scrape_method': 'sample_data',
                    'source_type': 'category_tech',
                    'persona_name': 'productivity_seeker',
                    'persona_score': 72.1,
                    'brand': 'Generic',
                    'is_viral': True,
                    'tiktok_mentions': 420,
                    'original_price': 800.00,
                    'discount_percentage': 28
                }
            },
            {
                'collection_date': datetime.now().isoformat(),
                'search_keyword': 'laptop stand',
                'product_name': 'Laptop Stand Adjustable Aluminum',
                'seller_name': 'UGREEN Official Store',
                'price': 1850.00,
                'currency': 'PHP',
                'rating': 4.6,
                'review_count': 280,
                'sales_count': 950,
                'product_url': 'https://www.tiktok.com/shop/ph/product/ugreen-laptop-stand-006',
                'image_url': 'https://example.com/ugreen-laptop-stand.jpg',
                'category': 'tech',
                'discount_info': {
                    'platform': 'tiktok_shop',
                    'is_real_data': False,
                    'scrape_method': 'sample_data',
                    'source_type': 'flash_sale',
                    'persona_name': 'productivity_seeker',
                    'persona_score': 81.7,
                    'brand': 'UGREEN',
                    'is_viral': False,
                    'tiktok_mentions': 95,
                    'original_price': 2500.00,
                    'discount_percentage': 26
                }
            },
            
            # Urban Professional 타겟 제품들
            {
                'collection_date': datetime.now().isoformat(),
                'search_keyword': 'noise cancelling headphones',
                'product_name': 'Premium Wireless Noise-Cancelling Headphones',
                'seller_name': 'Sony Official',
                'price': 3200.00,
                'currency': 'PHP',
                'rating': 4.8,
                'review_count': 450,
                'sales_count': 600,
                'product_url': 'https://www.tiktok.com/shop/ph/product/sony-headphones-007',
                'image_url': 'https://example.com/sony-headphones.jpg',
                'category': 'tech',
                'discount_info': {
                    'platform': 'tiktok_shop',
                    'is_real_data': False,
                    'scrape_method': 'sample_data',
                    'source_type': 'top_products',
                    'persona_name': 'urban_professional',
                    'persona_score': 89.3,
                    'brand': 'Sony',
                    'is_viral': False,
                    'tiktok_mentions': 75,
                    'original_price': 4000.00,
                    'discount_percentage': 20
                }
            },
            {
                'collection_date': datetime.now().isoformat(),
                'search_keyword': 'laptop bag',
                'product_name': 'Minimalist Leather Laptop Bag',
                'seller_name': 'Bellroy Official',
                'price': 2800.00,
                'currency': 'PHP',
                'rating': 4.7,
                'review_count': 180,
                'sales_count': 400,
                'product_url': 'https://www.tiktok.com/shop/ph/product/bellroy-laptop-bag-008',
                'image_url': 'https://example.com/bellroy-laptop-bag.jpg',
                'category': 'lifestyle',
                'discount_info': {
                    'platform': 'tiktok_shop',
                    'is_real_data': False,
                    'scrape_method': 'sample_data',
                    'source_type': 'category_lifestyle',
                    'persona_name': 'urban_professional',
                    'persona_score': 84.6,
                    'brand': 'Bellroy',
                    'is_viral': False,
                    'tiktok_mentions': 45,
                    'original_price': 3500.00,
                    'discount_percentage': 20
                }
            }
        ]
        
        print(f"\n📦 TikTok Shop 샘플 데이터 {len(tiktok_sample_products)}개 삽입 중...")
        
        # 기존 shopee_products 테이블에 TikTok Shop 데이터 삽입
        try:
            result = supabase_client.client.table('shopee_products').insert(tiktok_sample_products).execute()
            print(f"✅ TikTok Shop 샘플 데이터 {len(tiktok_sample_products)}개 삽입 완료!")
        except Exception as e:
            print(f"❌ 데이터 삽입 실패: {e}")
            return False
        
        # 삽입된 데이터 확인
        print("\n🔍 TikTok Shop 데이터 확인...")
        
        try:
            # TikTok Shop 데이터만 필터링해서 확인
            tiktok_data = supabase_client.client.table('shopee_products')\
                .select('*')\
                .contains('discount_info', {'platform': 'tiktok_shop'})\
                .order('created_at', desc=True)\
                .limit(5)\
                .execute()
            
            if tiktok_data.data:
                print(f"✅ 확인된 TikTok Shop 데이터: {len(tiktok_data.data)}개")
                
                print("\n🎯 상위 5개 TikTok Shop 제품:")
                for i, product in enumerate(tiktok_data.data, 1):
                    name = product.get('product_name', 'Unknown')[:40]
                    price = product.get('price', 0)
                    persona = product.get('discount_info', {}).get('persona_name', 'N/A')
                    score = product.get('discount_info', {}).get('persona_score', 0)
                    is_viral = product.get('discount_info', {}).get('is_viral', False)
                    viral_icon = "🔥" if is_viral else "📦"
                    
                    print(f"   {i}. {viral_icon} {name}...")
                    print(f"      💰 ₱{price} | 🎯 {persona} ({score}점)")
                
                return True
            else:
                print("❌ TikTok Shop 데이터를 찾을 수 없습니다")
                return False
                
        except Exception as e:
            print(f"❌ 데이터 확인 실패: {e}")
            return False
        
    except Exception as e:
        print(f"❌ TikTok Shop 데이터 생성 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    
    logging.basicConfig(level=logging.WARNING)  # 로깅 최소화
    
    success = create_tiktok_shop_table_simple()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ TikTok Shop 데이터베이스 설정 완료!")
        print("🎯 다음 단계:")
        print("   - 페르소나 타겟팅 로직 연동")
        print("   - AI 리포트에 TikTok Shop 데이터 포함")
        print("   - 대시보드 API에 TikTok Shop 엔드포인트 추가")
    else:
        print("\n" + "=" * 60)
        print("❌ TikTok Shop 데이터베이스 설정 실패")

if __name__ == "__main__":
    main()