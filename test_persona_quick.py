#!/usr/bin/env python3
"""
빠른 페르소나 타겟 시스템 테스트
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

# 페르소나 설정 import
from config.persona_config import (
    TARGET_PERSONAS, 
    get_persona_keywords, 
    get_persona_filters,
    ACTIVE_PERSONA
)

from database.supabase_client import SupabaseClient

def test_persona_system():
    """페르소나 시스템 빠른 테스트"""
    
    print("🎯 페르소나 타겟 시스템 테스트")
    print("=" * 50)
    
    # 현재 활성 페르소나 확인
    persona = TARGET_PERSONAS[ACTIVE_PERSONA]
    filters = get_persona_filters(ACTIVE_PERSONA)
    
    print(f"📊 활성 페르소나: {persona.name}")
    print(f"👥 연령대: {persona.age_group.value}")
    print(f"⚧ 성별: {persona.gender.value}")
    print(f"💰 가격대: {filters.get('price_ranges', [])}")
    print(f"⭐ 최소 평점: {filters.get('min_rating', 0)}")
    print(f"📝 최소 리뷰: {filters.get('min_reviews', 0)}")
    
    print(f"\n🏷️ 관심사 (상위 10개):")
    for i, interest in enumerate(persona.interests[:10], 1):
        print(f"  {i:2d}. {interest}")
    
    print(f"\n🔍 페르소나 키워드 (상위 15개):")
    for i, keyword in enumerate(persona.keywords[:15], 1):
        print(f"  {i:2d}. {keyword}")
    
    print(f"\n🏪 선호 브랜드 (상위 10개):")
    for i, brand in enumerate(persona.preferred_brands[:10], 1):
        print(f"  {i:2d}. {brand}")
    
    # 카테고리별 키워드 생성 테스트
    print(f"\n🎯 카테고리별 페르소나 키워드 생성:")
    test_categories = ["beauty", "skincare", "fashion"]
    
    for category in test_categories:
        keywords = get_persona_keywords(ACTIVE_PERSONA, category)
        print(f"  📂 {category}: {len(keywords)}개 키워드")
        print(f"     상위 5개: {keywords[:5]}")
    
    # 실제 데이터 시뮬레이션
    print(f"\n🧪 페르소나 제품 매칭 시뮬레이션:")
    
    # 가상의 제품 데이터
    test_products = [
        {
            "product_name": "COSRX Snail 96 Mucin Power Essence",
            "price_numeric": 890.0,
            "rating_numeric": 4.5,
            "review_count_numeric": 156
        },
        {
            "product_name": "Maybelline Fit Me Foundation",
            "price_numeric": 650.0,
            "rating_numeric": 4.2,
            "review_count_numeric": 89
        },
        {
            "product_name": "Premium Anti-Aging Serum",
            "price_numeric": 3500.0,
            "rating_numeric": 4.8,
            "review_count_numeric": 234
        },
        {
            "product_name": "Basic Moisturizer",
            "price_numeric": 150.0,
            "rating_numeric": 3.2,
            "review_count_numeric": 12
        }
    ]
    
    for i, product in enumerate(test_products, 1):
        print(f"\n  제품 {i}: {product['product_name']}")
        print(f"    💰 가격: ₱{product['price_numeric']}")
        print(f"    ⭐ 평점: {product['rating_numeric']}")
        print(f"    📝 리뷰: {product['review_count_numeric']}개")
        
        # 페르소나 적합성 체크
        is_suitable = check_persona_suitability(product, filters, persona)
        score = calculate_mock_persona_score(product, filters, persona)
        
        print(f"    🎯 페르소나 적합: {'✅ YES' if is_suitable else '❌ NO'}")
        print(f"    📊 예상 점수: {score:.1f}/100")

def check_persona_suitability(product, filters, persona):
    """페르소나 적합성 체크 (간단 버전)"""
    
    # 가격 체크
    price = product.get('price_numeric', 0)
    if price > filters.get('max_price', 5000):
        return False
    
    # 평점 체크
    rating = product.get('rating_numeric', 0)
    if rating < filters.get('min_rating', 3.5):
        return False
    
    # 리뷰 수 체크
    reviews = product.get('review_count_numeric', 0)
    if reviews < filters.get('min_reviews', 10):
        return False
    
    return True

def calculate_mock_persona_score(product, filters, persona):
    """페르소나 점수 계산 (간단 버전)"""
    score = 0.0
    
    # 가격 점수 (30점)
    price = product.get('price_numeric', 0)
    price_ranges = filters.get('price_ranges', [])
    if price_ranges:
        for price_range in price_ranges:
            if price_range[0] <= price <= price_range[1]:
                score += 30
                break
    
    # 평점 점수 (25점)
    rating = product.get('rating_numeric', 0)
    score += (rating / 5.0) * 25
    
    # 리뷰 수 점수 (20점)
    reviews = product.get('review_count_numeric', 0)
    if reviews > 0:
        import math
        review_score = min(20, math.log10(max(1, reviews)) * 10)
        score += review_score
    
    # 브랜드 보너스 (15점)
    product_name = product.get('product_name', '').lower()
    preferred_brands = [brand.lower() for brand in persona.preferred_brands]
    if any(brand in product_name for brand in preferred_brands):
        score += 15
    
    # 키워드 매칭 (10점)
    persona_keywords = [kw.lower() for kw in persona.keywords[:20]]
    keyword_matches = sum(1 for kw in persona_keywords if kw in product_name)
    score += min(10, keyword_matches * 2)
    
    return min(100, score)

def test_database_integration():
    """데이터베이스 연동 테스트"""
    print(f"\n💾 데이터베이스 연동 테스트:")
    
    try:
        db_client = SupabaseClient()
        print("✅ Supabase 연결 성공!")
        
        # 기존 페르소나 데이터 확인
        recent_data = db_client.client.table('shopee_products')\
            .select('*')\
            .contains('discount_info', {'scrape_method': 'persona_targeted'})\
            .order('created_at', desc=True)\
            .limit(5)\
            .execute()
        
        if recent_data.data:
            print(f"📊 기존 페르소나 데이터: {len(recent_data.data)}개 발견")
            for item in recent_data.data:
                persona_score = item.get('discount_info', {}).get('persona_score', 0)
                print(f"  - {item['product_name'][:40]}... (점수: {persona_score})")
        else:
            print("🆕 페르소나 데이터 없음 (새로 수집 필요)")
            
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")

if __name__ == "__main__":
    test_persona_system()
    test_database_integration()
    
    print("\n" + "=" * 50)
    print("✅ 페르소나 시스템 테스트 완료!")
    print("\n💡 다음 단계:")
    print("1. python3 scrapers/lazada_persona_scraper.py - 실제 수집 테스트")
    print("2. python3 main.py - 전체 시스템 실행")
    print("3. python3 check_real_data.py - 결과 확인")