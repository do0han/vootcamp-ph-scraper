"""
Advanced Shopee scraper with real data extraction capabilities
실제 Shopee 데이터를 추출하는 고급 스크래퍼
"""

import time
import random
import logging
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    import undetected_chromedriver as uc
except ImportError as e:
    print(f"Selenium import error: {e}")

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import quote, urljoin

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import SupabaseClient
try:
    from database.supabase_client import SupabaseClient
except ImportError:
    SupabaseClient = None
    print("⚠️ SupabaseClient not available - data will not be saved to database")

# from utils.anti_bot_system import AntiBotSystem
# from utils.ethical_scraping import ScrapingPolicy

logger = logging.getLogger(__name__)


class AdvancedShopeeScraper:
    """고급 Shopee 스크래퍼 - 실제 데이터 추출"""
    
    def __init__(
        self,
        anti_bot_system = None,
        scraping_policy = None,
        base_url: str = "https://shopee.ph",
        use_undetected: bool = True
    ):
        self.base_url = base_url
        self.use_undetected = use_undetected
        self.driver = None
        self.user_agent = UserAgent()
        self.collection_date = datetime.now()
        self.wait_timeout = 30
        
        # Initialize anti-bot system
        self.anti_bot_system = anti_bot_system
        if not self.anti_bot_system:
            # Create a simple mock system
            class MockAntiBot:
                def apply_delay(self):
                    time.sleep(random.uniform(2, 5))
            self.anti_bot_system = MockAntiBot()
        
        # Initialize scraping policy
        self.scraping_policy = scraping_policy
        if not self.scraping_policy:
            class MockPolicy:
                def wait_for_rate_limit(self):
                    time.sleep(1)
            self.scraping_policy = MockPolicy()
        
        # Initialize Supabase client if available
        self.supabase_client = None
        if SupabaseClient:
            try:
                self.supabase_client = SupabaseClient()
                logger.info("✅ Supabase client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Supabase client: {e}")
                self.supabase_client = None
    
    def _setup_advanced_driver(self):
        """고급 크롬 드라이버 설정 (undetected-chromedriver 사용)"""
        try:
            if self.use_undetected:
                # undetected-chromedriver 사용 (간소화된 옵션)
                options = uc.ChromeOptions()
                options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--window-size=1366,768')
                
                # User-Agent 설정
                user_agent = self.user_agent.random
                options.add_argument(f'--user-agent={user_agent}')
                
                self.driver = uc.Chrome(options=options, version_main=None)
                
            else:
                # 일반 Selenium 사용
                options = Options()
                options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument(f'--user-agent={self.user_agent.random}')
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            
            # 자동화 감지 방지 스크립트
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            
            logger.info("✅ Advanced WebDriver setup completed")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup advanced WebDriver: {e}")
            raise
    
    def _wait_and_scroll(self, wait_time: int = 10):
        """페이지 로드 대기 및 스크롤링"""
        try:
            # 초기 대기
            time.sleep(wait_time)
            
            # 페이지 완전 로드 확인
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 점진적 스크롤링으로 동적 콘텐츠 로드
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            scroll_increment = 500
            
            while current_position < total_height:
                # 스크롤 다운
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(random.uniform(1, 3))
                current_position += scroll_increment
                
                # 페이지 높이 재확인 (동적 로딩으로 인한 변화)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height > total_height:
                    total_height = new_height
            
            # 맨 위로 스크롤
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            logger.info("✅ Page scrolling and loading completed")
            
        except Exception as e:
            logger.warning(f"⚠️ Scroll and wait warning: {e}")
    
    def _extract_product_data(self, product_elements: list) -> List[Dict[str, Any]]:
        """제품 요소에서 실제 데이터 추출"""
        products = []
        
        for i, element in enumerate(product_elements):
            try:
                product_data = {
                    'collection_date': self.collection_date.isoformat(),
                    'search_keyword': '',
                    'product_name': 'Unknown Product',
                    'product_url': '',
                    'price': '',
                    'seller_name': 'Unknown Seller',
                    'rating': None,
                    'review_count': None,
                    'image_url': '',
                    'discount_info': {}
                }
                
                # 제품명 추출 (여러 선택자 시도)
                name_selectors = [
                    '[data-sqe="name"]',
                    '.shopee-search-item-result__text',
                    'a[data-sqe="link"] span',
                    '.item-name',
                    '[title]'
                ]
                
                for selector in name_selectors:
                    try:
                        name_element = element.find_element(By.CSS_SELECTOR, selector)
                        name = name_element.get_attribute('title') or name_element.text
                        if name and name.strip():
                            product_data['product_name'] = name.strip()
                            break
                    except:
                        continue
                
                # 가격 추출
                price_selectors = [
                    '.shopee-price',
                    '[data-sqe="price"]',
                    '.price',
                    '.item-price'
                ]
                
                for selector in price_selectors:
                    try:
                        price_element = element.find_element(By.CSS_SELECTOR, selector)
                        price_text = price_element.text
                        if price_text and '₱' in price_text:
                            product_data['price'] = price_text.strip()
                            break
                    except:
                        continue
                
                # URL 추출
                try:
                    link_element = element.find_element(By.TAG_NAME, 'a')
                    href = link_element.get_attribute('href')
                    if href:
                        product_data['product_url'] = href
                except:
                    pass
                
                # 이미지 URL 추출
                try:
                    img_element = element.find_element(By.TAG_NAME, 'img')
                    img_src = img_element.get_attribute('src')
                    if img_src:
                        product_data['image_url'] = img_src
                except:
                    pass
                
                # 평점 추출
                rating_selectors = [
                    '.shopee-rating',
                    '[data-sqe="rating"]',
                    '.rating'
                ]
                
                for selector in rating_selectors:
                    try:
                        rating_element = element.find_element(By.CSS_SELECTOR, selector)
                        rating_text = rating_element.text
                        # 숫자만 추출
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            product_data['rating'] = float(rating_match.group(1))
                            break
                    except:
                        continue
                
                # 유효한 제품인지 확인 (제품명이 있고 URL이 있는 경우)
                if (product_data['product_name'] != 'Unknown Product' and 
                    product_data['product_url'] and 
                    'shopee.ph' in product_data['product_url']):
                    products.append(product_data)
                    logger.debug(f"✅ Extracted product: {product_data['product_name'][:50]}...")
                
            except Exception as e:
                logger.debug(f"⚠️ Error extracting product {i}: {e}")
                continue
        
        return products
    
    def search_products_advanced(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """고급 제품 검색 - 실제 데이터 추출"""
        try:
            if not self.driver:
                self._setup_advanced_driver()
            
            # 검색 URL 구성
            search_url = f"{self.base_url}/search?keyword={quote(keyword)}&sortBy=sales"
            
            logger.info(f"🔍 Advanced search for: {keyword}")
            logger.info(f"📍 Navigating to: {search_url}")
            
            # 페이지 로드
            self.driver.get(search_url)
            
            # 페이지 로드 및 스크롤 대기
            self._wait_and_scroll(15)
            
            # 제품 요소 찾기 (여러 선택자 시도)
            product_selectors = [
                '[data-sqe="item"]',
                '.shopee-search-item-result__item',
                '.col-xs-2-4.shopee-search-item-result__item',
                '.item-card-wrapper',
                'div[data-sqe="item"]',
                'a[data-sqe="link"]'
            ]
            
            products = []
            found_elements = []
            
            for selector in product_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) >= 5:  # 충분한 요소를 찾았을 때
                        found_elements = elements
                        logger.info(f"✅ Found {len(elements)} product elements using: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not found_elements:
                logger.warning("❌ No product elements found with any selector")
                return []
            
            # 제품 데이터 추출
            products = self._extract_product_data(found_elements[:limit])
            
            # 검색 키워드 설정
            for product in products:
                product['search_keyword'] = keyword
            
            logger.info(f"✅ Successfully extracted {len(products)} real products for '{keyword}'")
            return products
            
        except Exception as e:
            logger.error(f"❌ Error in advanced product search: {e}")
            return []
    
    def get_flash_deal_products_advanced(self, limit: int = 20, save_to_db: bool = True) -> List[Dict[str, Any]]:
        """고급 플래시 딜 제품 수집"""
        try:
            logger.info("🔥 Advanced Flash Deal collection starting...")
            
            # 플래시 딜 관련 키워드
            flash_keywords = [
                "sale",
                "discount", 
                "promo",
                "deal",
                "clearance"
            ]
            
            all_products = []
            products_per_keyword = max(1, limit // len(flash_keywords))
            
            for keyword in flash_keywords:
                try:
                    logger.info(f"🔍 Searching flash deals: {keyword}")
                    products = self.search_products_advanced(keyword, limit=products_per_keyword)
                    
                    # 플래시 딜 마킹
                    for product in products:
                        product['search_keyword'] = f"flash_deal_{keyword}"
                        product['product_type'] = 'flash_deal'
                        
                    all_products.extend(products)
                    
                    # 키워드 간 대기
                    self.anti_bot_system.apply_delay()
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error with flash keyword '{keyword}': {e}")
                    continue
            
            # 중복 제거
            seen_urls = set()
            unique_products = []
            for product in all_products:
                url = product.get('product_url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_products.append(product)
            
            final_products = unique_products[:limit]
            logger.info(f"✅ Collected {len(final_products)} unique flash deal products")
            
            # 데이터베이스 저장
            if save_to_db and final_products:
                self._save_to_supabase(final_products)
            
            return final_products
            
        except Exception as e:
            logger.error(f"❌ Error collecting advanced flash deals: {e}")
            return []
    
    def get_trending_products_advanced(self, categories: List[str] = None, limit: int = 20, save_to_db: bool = True) -> List[Dict[str, Any]]:
        """고급 트렌딩 제품 수집"""
        try:
            logger.info("📈 Advanced Trending Products collection starting...")
            
            if not categories:
                categories = [
                    "beauty",
                    "fashion", 
                    "electronics",
                    "skincare",
                    "phone"
                ]
            
            all_products = []
            products_per_category = max(1, limit // len(categories))
            
            for category in categories:
                try:
                    logger.info(f"🏷️ Searching trending: {category}")
                    products = self.search_products_advanced(category, limit=products_per_category)
                    
                    # 트렌딩 마킹
                    for product in products:
                        product['search_keyword'] = f"trending_{category}"
                        product['product_type'] = 'trending'
                        product['category'] = category
                        
                    all_products.extend(products)
                    
                    # 카테고리 간 대기
                    self.anti_bot_system.apply_delay()
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error with category '{category}': {e}")
                    continue
            
            # 중복 제거
            seen_urls = set()
            unique_products = []
            for product in all_products:
                url = product.get('product_url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_products.append(product)
            
            final_products = unique_products[:limit]
            logger.info(f"✅ Collected {len(final_products)} unique trending products")
            
            # 데이터베이스 저장
            if save_to_db and final_products:
                self._save_to_supabase(final_products)
            
            return final_products
            
        except Exception as e:
            logger.error(f"❌ Error collecting advanced trending products: {e}")
            return []
    
    def _save_to_supabase(self, products: List[Dict[str, Any]]) -> bool:
        """Supabase에 제품 저장"""
        if not self.supabase_client:
            logger.warning("⚠️ Supabase client not available - skipping database save")
            return False
        
        if not products:
            logger.info("ℹ️ No products to save to database")
            return True
        
        try:
            logger.info(f"💾 Saving {len(products)} real products to Supabase...")
            
            # 데이터 포맷팅
            formatted_products = []
            for product in products:
                formatted_product = {
                    'collection_date': product.get('collection_date', self.collection_date.isoformat()),
                    'search_keyword': product.get('search_keyword', 'unknown'),
                    'product_name': product.get('product_name', 'Unknown Product'),
                    'seller_name': product.get('seller_name', 'Unknown Seller'),
                    'price': self._extract_price_value(product.get('price', '0')),
                    'currency': 'PHP',
                    'rating': product.get('rating'),
                    'review_count': product.get('review_count'),
                    'product_url': product.get('product_url'),
                    'image_url': product.get('image_url'),
                    'category': product.get('category', product.get('product_type', 'general')),
                    'discount_info': {
                        'product_type': product.get('product_type'),
                        'original_keyword': product.get('search_keyword'),
                        'scrape_method': 'advanced_shopee_scraper',
                        'is_real_data': True  # 실제 데이터임을 표시
                    }
                }
                formatted_products.append(formatted_product)
            
            # 데이터베이스 저장
            success = self.supabase_client.insert_shopee_products(formatted_products)
            
            if success:
                logger.info(f"✅ Successfully saved {len(formatted_products)} real products to Supabase")
                return True
            else:
                logger.error("❌ Failed to save products to Supabase")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error saving to Supabase: {e}")
            return False
    
    def _extract_price_value(self, price_str: str) -> Optional[float]:
        """가격 문자열에서 숫자 값 추출"""
        try:
            if not price_str or price_str == 'N/A':
                return None
            # 통화 기호와 쉼표 제거, 숫자만 추출
            import re
            price_match = re.search(r'[\d,]+\.?\d*', str(price_str).replace(',', ''))
            if price_match:
                return float(price_match.group())
            return None
        except:
            return None
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("✅ Browser closed")


def main():
    """테스트 함수"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scraper = AdvancedShopeeScraper(use_undetected=True)
    
    try:
        print("🛒 Testing Advanced Shopee scraper...")
        
        # 테스트 검색
        test_keyword = "skincare"
        products = scraper.search_products_advanced(test_keyword, limit=5)
        
        print(f"✅ Found {len(products)} real products for '{test_keyword}'")
        
        if products:
            print("\n📦 Real products found:")
            for i, product in enumerate(products):
                print(f"{i+1}. {product['product_name'][:50]}... - {product['price']}")
                print(f"   URL: {product['product_url'][:80]}...")
                print()
        
        return products
        
    except Exception as e:
        print(f"❌ Error testing scraper: {e}")
        return []
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()