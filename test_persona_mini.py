#!/usr/bin/env python3
"""
미니 페르소나 스크래퍼 테스트 (빠른 버전)
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

from scrapers.lazada_persona_scraper import LazadaPersonaScraper

def quick_persona_test():
    """빠른 페르소나 테스트 (1개 카테고리만)"""
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎯 빠른 페르소나 타겟 테스트 시작")
    print("=" * 50)
    
    try:
        # 페르소나 스크래퍼 초기화
        scraper = LazadaPersonaScraper(persona_name="young_filipina", use_undetected=True)
        
        print(f"📊 타겟 페르소나: {scraper.persona.name}")
        print(f"👥 연령대: {scraper.persona.age_group.value}")
        print(f"💰 최대 가격: ₱{scraper.persona_filters.get('max_price', 2000)}")
        print()
        
        # 단일 카테고리 테스트 (K-beauty)
        print("🔍 테스트 카테고리: K-beauty")
        products = scraper.search_persona_products("K-beauty", limit=3)
        
        print(f"\n✅ 수집 완료: {len(products)}개 제품")
        
        if products:
            print("\n🎯 페르소나 매칭 결과:")
            for i, product in enumerate(products, 1):
                name = product.get('product_name', 'Unknown')[:40]
                price = product.get('price_numeric', 0)
                score = product.get('persona_score', 0)
                rating = product.get('rating_numeric', 0)
                brand_bonus = "🏷️" if product.get('brand_bonus', False) else ""
                
                print(f"{i}. {name}...")
                print(f"   💰 ₱{price} | ⭐ {rating} | 🎯 {score:.1f}/100 {brand_bonus}")
            
            # 데이터베이스 저장 테스트
            print(f"\n💾 데이터베이스 저장 테스트...")
            success = scraper._save_to_supabase(products)
            if success:
                print("✅ 데이터베이스 저장 성공!")
            else:
                print("❌ 데이터베이스 저장 실패")
        else:
            print("⚠️ 페르소나 매칭 제품 없음")
        
        return products
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return []
    
    finally:
        try:
            scraper.close()
        except:
            pass
        print("\n" + "=" * 50)
        print("🏁 빠른 페르소나 테스트 완료")

if __name__ == "__main__":
    quick_persona_test()