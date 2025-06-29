"""
Test Shopee scraper implementation
"""
import asyncio
import logging
import os
import sys
from typing import List
import random

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from vootcamp_ph_scraper.scrapers.shopee_scraper import ShopeeScraper
from vootcamp_ph_scraper.utils.anti_bot_system import AntiBotSystem
from vootcamp_ph_scraper.utils.proxy_manager import ProxyManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
TEST_PROXIES = [
    "http://103.148.72.126:80",  # Philippines proxy
    "http://103.148.72.192:80",  # Philippines proxy
    "http://103.148.72.193:80"   # Philippines proxy
]

TEST_KEYWORDS = [
    "iphone",
    "samsung galaxy",
    "nintendo switch",
    "laptop",
    "headphones"
]

async def scrape_shopee_data():
    """실제 Shopee 데이터 수집"""
    try:
        # Initialize components
        anti_bot = AntiBotSystem()  # 싱글톤 패턴 사용
        proxy_manager = ProxyManager(proxies=TEST_PROXIES)
        
        # Initialize scraper
        scraper = ShopeeScraper(
            anti_bot_system=anti_bot,
            proxy_manager=proxy_manager
        )
        
        # Search products for each keyword
        all_products = []
        for keyword in TEST_KEYWORDS:
            logger.info(f"\n검색어: {keyword}")
            
            # Get products
            products = await scraper.search_products(keyword, limit=10)
            
            if products:
                logger.info(f"{len(products)}개의 상품을 찾았습니다:")
                for i, product in enumerate(products, 1):
                    logger.info(f"\n상품 {i}:")
                    logger.info(f"이름: {product['name']}")
                    logger.info(f"가격: PHP {product['price']:.2f}")
                    logger.info(f"평점: {product['rating']:.1f}")
                    logger.info(f"판매량: {product['sold']}")
                    logger.info(f"위치: {product['shop_location']}")
                    logger.info(f"URL: {product['url']}")
                    
                    # Get detailed information
                    details = await scraper.get_product_details(product['url'])
                    if details:
                        logger.info("\n상세 정보:")
                        logger.info(f"설명: {details.get('description', 'N/A')[:200]}...")
                        logger.info(f"이미지 URL: {details.get('image_url', 'N/A')}")
                    
                    all_products.append({**product, "details": details})
                    
                    # Add delay between products
                    await asyncio.sleep(random.uniform(2, 4))
            else:
                logger.warning(f"'{keyword}' 검색어로 상품을 찾지 못했습니다.")
            
            # Add longer delay between keywords
            await asyncio.sleep(5)
            
        return all_products
            
    except Exception as e:
        logger.error(f"데이터 수집 실패: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the scraper
    products = asyncio.run(scrape_shopee_data())
    
    # Save results to file
    if products:
        import json
        from datetime import datetime
        
        filename = f"shopee_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        logger.info(f"\n수집된 데이터를 {filename}에 저장했습니다.") 