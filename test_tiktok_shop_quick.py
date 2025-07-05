#!/usr/bin/env python3
"""
TikTok Shop 스크래퍼 빠른 테스트
"""

import sys
import time
import logging
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

from scrapers.tiktok_shop_scraper import TikTokShopScraper

def quick_test():
    """TikTok Shop 스크래퍼 빠른 테스트"""
    
    print("🎬 TikTok Shop 스크래퍼 빠른 테스트")
    print("=" * 50)
    
    # 로깅 최소화
    logging.basicConfig(level=logging.WARNING)
    
    scraper = TikTokShopScraper(use_undetected=True, headless=True)
    
    try:
        # 메인 페이지 (Top Products) 테스트만
        print("🎯 TikTok Shop 메인 페이지 테스트...")
        products = scraper.get_top_products(limit=3)
        
        print(f"\n✅ 수집 결과: {len(products)}개 제품")
        
        if products:
            print("\n🛍️ 발견된 제품들:")
            for i, product in enumerate(products, 1):
                name = product.get('product_name', 'Unknown')[:40]
                price = product.get('price_numeric', 0) or 'N/A'
                url = product.get('product_url', '')
                rating = product.get('rating_numeric', 0) or 'N/A'
                
                print(f"{i}. {name}...")
                print(f"   💰 가격: ₱{price}")
                print(f"   ⭐ 평점: {rating}")
                print(f"   🔗 URL: {url[:50]}..." if url else "   🔗 URL: N/A")
                print()
        else:
            print("⚠️ 제품을 찾지 못했습니다.")
            print("💡 가능한 원인:")
            print("   - TikTok Shop 페이지 구조 변경")
            print("   - 지역 접근 제한")
            print("   - 동적 로딩 대기 시간 부족")
        
        return products
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return []
    
    finally:
        scraper.close()
        print("\n✅ 테스트 완료")

if __name__ == "__main__":
    quick_test()