#!/usr/bin/env python3
"""
생산성 추구자 페르소나 테스트 (Just Elias 시나리오)
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

from config.persona_config import (
    TARGET_PERSONAS, 
    get_persona_keywords, 
    get_persona_filters,
    PERSONA_SEARCH_STRATEGIES
)

def test_productivity_persona():
    """생산성 추구자 페르소나 시스템 테스트"""
    
    print("🎯 생산성 추구자 페르소나 테스트 (Just Elias 시나리오)")
    print("=" * 60)
    
    # 페르소나 확인
    persona_name = "productivity_seeker"
    persona = TARGET_PERSONAS.get(persona_name)
    
    if not persona:
        print(f"❌ 페르소나 '{persona_name}'를 찾을 수 없습니다!")
        return
    
    filters = get_persona_filters(persona_name)
    strategy = PERSONA_SEARCH_STRATEGIES.get(persona_name, {})
    
    print(f"📊 페르소나: {persona.name}")
    print(f"👥 연령대: {persona.age_group.value}")
    print(f"⚧ 성별: {persona.gender.value}")
    print(f"💰 가격대: {filters.get('price_ranges', [])} (최대 ₱{filters.get('max_price', 0)})")
    print(f"⭐ 최소 평점: {filters.get('min_rating', 0)}")
    print(f"📝 최소 리뷰: {filters.get('min_reviews', 0)}")
    
    print(f"\n🏷️ 관심사 (상위 8개):")
    for i, interest in enumerate(persona.interests[:8], 1):
        print(f"  {i:2d}. {interest}")
    
    print(f"\n🔍 핵심 키워드 (상위 15개):")
    for i, keyword in enumerate(persona.keywords[:15], 1):
        print(f"  {i:2d}. {keyword}")
    
    print(f"\n🏪 선호 브랜드 (상위 10개):")
    for i, brand in enumerate(persona.preferred_brands[:10], 1):
        print(f"  {i:2d}. {brand}")
    
    print(f"\n📱 사용 플랫폼:")
    for i, platform in enumerate(persona.social_media_platforms, 1):
        print(f"  {i}. {platform}")
    
    print(f"\n🛒 쇼핑 행동:")
    for i, behavior in enumerate(persona.shopping_behaviors, 1):
        print(f"  {i}. {behavior}")
    
    # 카테고리별 키워드 생성 테스트
    print(f"\n🎯 카테고리별 키워드 생성 테스트:")
    test_categories = ["productivity tools", "ergonomic furniture", "tech gadgets"]
    
    for category in test_categories:
        keywords = get_persona_keywords(persona_name, category)
        print(f"  📂 {category}: {len(keywords)}개 키워드")
        print(f"     상위 5개: {keywords[:5]}")
    
    # 검색 전략 확인
    print(f"\n🔍 검색 전략:")
    print(f"  주요 카테고리: {strategy.get('primary_categories', [])}")
    print(f"  트렌드 수식어: {strategy.get('trending_modifiers', [])}")
    print(f"  가격 수식어: {strategy.get('price_modifiers', [])}")
    print(f"  품질 필터: {strategy.get('quality_filters', {})}")
    
    # Just Elias 시나리오 시뮬레이션
    print(f"\n🎓 Just Elias 시나리오 시뮬레이션:")
    print("상황: 시험 기간이 다가오고 있어 집중력을 높일 아이템을 찾고 있음")
    
    # 가상의 제품 데이터로 매칭 테스트
    test_products = [
        {
            "product_name": "Ergonomic Study Chair with Lumbar Support",
            "price_numeric": 2500.0,
            "rating_numeric": 4.3,
            "review_count_numeric": 156,
            "brand": "IKEA"
        },
        {
            "product_name": "Blue Light Blocking Glasses for Computer",
            "price_numeric": 450.0,
            "rating_numeric": 4.1,
            "review_count_numeric": 89,
            "brand": "Generic"
        },
        {
            "product_name": "Premium Standing Desk Converter",
            "price_numeric": 8500.0,
            "rating_numeric": 4.8,
            "review_count_numeric": 234,
            "brand": "Uplift"
        },
        {
            "product_name": "Wireless Noise-Cancelling Headphones",
            "price_numeric": 1200.0,
            "rating_numeric": 4.5,
            "review_count_numeric": 312,
            "brand": "Anker"
        }
    ]
    
    print(f"\n🧪 제품 매칭 시뮬레이션:")
    for i, product in enumerate(test_products, 1):
        print(f"\n  제품 {i}: {product['product_name']}")
        print(f"    💰 가격: ₱{product['price_numeric']}")
        print(f"    ⭐ 평점: {product['rating_numeric']}")
        print(f"    📝 리뷰: {product['review_count_numeric']}개")
        print(f"    🏷️ 브랜드: {product['brand']}")
        
        # 페르소나 적합성 체크
        is_suitable = check_productivity_suitability(product, filters, persona)
        score = calculate_productivity_score(product, filters, persona)
        
        print(f"    🎯 페르소나 적합: {'✅ YES' if is_suitable else '❌ NO'}")
        print(f"    📊 추천 점수: {score:.1f}/100")
        
        if is_suitable:
            print(f"    💡 Elias 추천: '시험 기간 집중력 향상에 도움!'")

def check_productivity_suitability(product, filters, persona):
    """생산성 페르소나 적합성 체크"""
    
    # 가격 체크
    price = product.get('price_numeric', 0)
    if price > filters.get('max_price', 5000):
        return False
    
    # 평점 체크
    rating = product.get('rating_numeric', 0)
    if rating < filters.get('min_rating', 4.0):
        return False
    
    # 리뷰 수 체크
    reviews = product.get('review_count_numeric', 0)
    if reviews < filters.get('min_reviews', 15):
        return False
    
    return True

def calculate_productivity_score(product, filters, persona):
    """생산성 페르소나 점수 계산"""
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
    brand = product.get('brand', '').lower()
    preferred_brands = [b.lower() for b in persona.preferred_brands]
    if any(pb in brand for pb in preferred_brands):
        score += 15
    
    # 키워드 매칭 (10점)
    product_name = product.get('product_name', '').lower()
    persona_keywords = [kw.lower() for kw in persona.keywords[:20]]
    keyword_matches = sum(1 for kw in persona_keywords if kw in product_name)
    score += min(10, keyword_matches * 2)
    
    return min(100, score)

if __name__ == "__main__":
    test_productivity_persona()
    print("\n" + "=" * 60)
    print("✅ 생산성 추구자 페르소나 테스트 완료!")
    print("💡 Just Elias가 로그인하면 이런 맞춤형 데이터를 받게 됩니다!")