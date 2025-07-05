"""
Shopee 데이터 수집 스크립트
"""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from vootcamp_ph_scraper.scrapers.shopee_scraper import ShopeeScraper
from vootcamp_ph_scraper.utils.anti_bot_system import AntiBotSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 검색할 키워드 목록
KEYWORDS = [
    "iphone",
    "samsung galaxy",
    "nike shoes",
    "adidas",
    "laptop"
]

async def collect_data():
    """Shopee 데이터 수집"""
    try:
        # 안티봇 시스템 초기화
        anti_bot = AntiBotSystem()
        
        # 스크래퍼 초기화
        scraper = ShopeeScraper(anti_bot_system=anti_bot)
        
        # 결과 저장할 디렉토리 생성
        output_dir = Path("data/shopee")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 각 키워드에 대해 데이터 수집
        for keyword in KEYWORDS:
            logger.info(f"'{keyword}' 키워드로 상품 검색 중...")
            
            # 상품 검색
            products = await scraper.search_products(keyword, limit=10)
            logger.info(f"{len(products)} 개의 상품을 찾았습니다.")
            
            # 상품 상세 정보 수집
            detailed_products = []
            for product in products:
                try:
                    details = await scraper.get_product_details(product["itemid"])
                    if details:
                        detailed_products.append(details)
                        logger.info(f"상품 정보 수집 완료: {details.get('name', 'Unknown')}")
                except Exception as e:
                    logger.error(f"상품 상세 정보 수집 실패: {str(e)}")
            
            # 결과 저장
            output_file = output_dir / f"{keyword.replace(' ', '_')}_products.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(detailed_products, f, ensure_ascii=False, indent=2)
            
            logger.info(f"'{keyword}' 데이터 저장 완료: {output_file}")
            
            # 안티봇 감지를 피하기 위한 대기
            await asyncio.sleep(5)
            
    except Exception as e:
        logger.error(f"데이터 수집 중 오류 발생: {str(e)}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(collect_data()) 