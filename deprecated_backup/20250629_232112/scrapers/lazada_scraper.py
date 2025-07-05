"""
Lazada Philippines scraper as alternative to Shopee
실제 Lazada 데이터를 수집하는 스크래퍼
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
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

logger = logging.getLogger(__name__)


class LazadaScraper:
    """Lazada Philippines 스크래퍼 - Shopee 대안"""
    
    def __init__(
        self,
        base_url: str = "https://www.lazada.com.ph",
        use_undetected: bool = True
    ):
        self.base_url = base_url
        self.use_undetected = use_undetected
        self.driver = None
        self.user_agent = UserAgent()
        self.collection_date = datetime.now()
        self.wait_timeout = 30
        
        # Initialize Supabase client if available
        self.supabase_client = None
        if SupabaseClient:
            try:
                self.supabase_client = SupabaseClient()
                logger.info("✅ Supabase client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Supabase client: {e}")
                self.supabase_client = None
    
    def _setup_driver(self):
        """Lazada용 크롬 드라이버 설정"""
        try:
            if self.use_undetected:
                options = uc.ChromeOptions()
                options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--window-size=1366,768')
                
                # Philippines 지역 설정
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                options.add_argument(f'--user-agent={user_agent}')
                options.add_argument('--lang=en-PH,en-US,en')
                
                self.driver = uc.Chrome(options=options, version_main=None)
            
            # 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            
            logger.info("✅ Lazada WebDriver setup completed")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Lazada WebDriver: {e}")
            raise
    
    def _wait_and_scroll(self, wait_time: int = 10):
        """페이지 로드 대기 및 스크롤링"""
        try:
            time.sleep(wait_time)
            
            # 페이지 완전 로드 확인
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 스크롤링으로 동적 콘텐츠 로드
            for i in range(3):
                scroll_position = (i + 1) * 800
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(random.uniform(2, 4))
            
            # 맨 위로 돌아가기
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            logger.info("✅ Lazada page loading and scrolling completed")
            
        except Exception as e:
            logger.warning(f"⚠️ Lazada scroll and wait warning: {e}")
    
    def _extract_lazada_products(self, product_elements: list) -> List[Dict[str, Any]]:
        """Lazada 제품 요소에서 데이터 추출"""
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
                    'platform': 'lazada'
                }
                
                # 제품명 추출 (Lazada 특화)
                name_selectors = [
                    '[data-qa-locator="product-item"] .title',
                    '.title-wrapper a',
                    '.product-card .title',
                    'a[title]',
                    '.item-title'
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
                
                # 가격 추출 (Lazada 특화)
                price_selectors = [
                    '.price-current',
                    '.currency',
                    '.price',
                    '[data-qa-locator="product-price"]'
                ]
                
                for selector in price_selectors:
                    try:
                        price_element = element.find_element(By.CSS_SELECTOR, selector)
                        price_text = price_element.text
                        if price_text and ('₱' in price_text or 'PHP' in price_text):
                            product_data['price'] = price_text.strip()
                            break
                    except:
                        continue
                
                # URL 추출
                try:
                    link_element = element.find_element(By.TAG_NAME, 'a')
                    href = link_element.get_attribute('href')
                    if href:
                        # 상대 URL을 절대 URL로 변환
                        if href.startswith('/'):
                            href = self.base_url + href
                        product_data['product_url'] = href
                except:
                    pass
                
                # 이미지 URL 추출
                try:
                    img_element = element.find_element(By.TAG_NAME, 'img')
                    img_src = img_element.get_attribute('src') or img_element.get_attribute('data-src')
                    if img_src:
                        product_data['image_url'] = img_src
                except:
                    pass
                
                # 평점 추출
                rating_selectors = [
                    '.rating-star',
                    '.score-average',
                    '[data-qa-locator="product-rating"]'
                ]
                
                for selector in rating_selectors:
                    try:
                        rating_element = element.find_element(By.CSS_SELECTOR, selector)
                        rating_text = rating_element.text or rating_element.get_attribute('title')
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            product_data['rating'] = float(rating_match.group(1))
                            break
                    except:
                        continue
                
                # 유효한 제품인지 확인
                if (product_data['product_name'] != 'Unknown Product' and 
                    product_data['product_url'] and 
                    'lazada.com.ph' in product_data['product_url']):
                    products.append(product_data)
                    logger.debug(f"✅ Extracted Lazada product: {product_data['product_name'][:50]}...")
                
            except Exception as e:
                logger.debug(f"⚠️ Error extracting Lazada product {i}: {e}")
                continue
        
        return products
    
    def search_products(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Lazada 제품 검색"""
        try:
            if not self.driver:
                self._setup_driver()
            
            # Lazada 검색 URL 구성
            search_url = f"{self.base_url}/catalog/?q={quote(keyword)}&sort=priceasc"
            
            logger.info(f"🔍 Lazada search for: {keyword}")
            logger.info(f"📍 Navigating to: {search_url}")
            
            # 페이지 로드
            self.driver.get(search_url)
            
            # 페이지 로드 및 스크롤 대기
            self._wait_and_scroll(15)
            
            # 봇 감지 확인
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            if 'captcha' in page_source or 'verify' in current_url:
                logger.warning("❌ Lazada bot detection triggered")
                return []
            
            # Lazada 제품 요소 찾기
            lazada_selectors = [
                '[data-qa-locator="product-item"]',
                '.product-item',
                '.item-box',
                '.product-card',
                '.list-item',
                '.item'
            ]
            
            products = []
            found_elements = []
            
            for selector in lazada_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) >= 3:  # 충분한 요소를 찾았을 때
                        found_elements = elements
                        logger.info(f"✅ Found {len(elements)} Lazada product elements using: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Lazada selector {selector} failed: {e}")
                    continue
            
            if not found_elements:
                logger.warning("❌ No Lazada product elements found")
                return []
            
            # 제품 데이터 추출
            products = self._extract_lazada_products(found_elements[:limit])
            
            # 검색 키워드 설정
            for product in products:
                product['search_keyword'] = keyword
            
            logger.info(f"✅ Successfully extracted {len(products)} real Lazada products for '{keyword}'")
            return products
            
        except Exception as e:
            logger.error(f"❌ Error in Lazada product search: {e}")
            return []
    
    def get_trending_products(self, categories: List[str] = None, limit: int = 20, save_to_db: bool = True) -> List[Dict[str, Any]]:
        """Lazada 트렌딩 제품 수집"""
        try:
            logger.info("📈 Lazada Trending Products collection starting...")
            
            if not categories:
                categories = [
                    "beauty",
                    "fashion", 
                    "electronics",
                    "skincare",
                    "phone",
                    "laptop"
                ]
            
            all_products = []
            products_per_category = max(1, limit // len(categories))
            
            for category in categories:
                try:
                    logger.info(f"🏷️ Searching Lazada trending: {category}")
                    products = self.search_products(category, limit=products_per_category)
                    
                    # 트렌딩 마킹
                    for product in products:
                        product['search_keyword'] = f"lazada_trending_{category}"
                        product['product_type'] = 'trending'
                        product['category'] = category
                        
                    all_products.extend(products)
                    
                    # 카테고리 간 대기
                    time.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error with Lazada category '{category}': {e}")
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
            logger.info(f"✅ Collected {len(final_products)} unique Lazada trending products")
            
            # 데이터베이스 저장
            if save_to_db and final_products:
                self._save_to_supabase(final_products)
            
            return final_products
            
        except Exception as e:
            logger.error(f"❌ Error collecting Lazada trending products: {e}")
            return []
    
    def _save_to_supabase(self, products: List[Dict[str, Any]]) -> bool:
        """Supabase에 Lazada 제품 저장"""
        if not self.supabase_client:
            logger.warning("⚠️ Supabase client not available - skipping database save")
            return False
        
        if not products:
            logger.info("ℹ️ No Lazada products to save to database")
            return True
        
        try:
            logger.info(f"💾 Saving {len(products)} real Lazada products to Supabase...")
            
            # 데이터 포맷팅 (Shopee 테이블 구조에 맞춰 저장)
            formatted_products = []
            for product in products:
                formatted_product = {
                    'collection_date': product.get('collection_date', self.collection_date.isoformat()),
                    'search_keyword': product.get('search_keyword', 'unknown'),
                    'product_name': product.get('product_name', 'Unknown Product'),
                    'seller_name': product.get('seller_name', 'Lazada Seller'),
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
                        'scrape_method': 'lazada_scraper',
                        'platform': 'lazada',
                        'is_real_data': True  # 실제 데이터임을 표시
                    }
                }
                formatted_products.append(formatted_product)
            
            # 데이터베이스 저장 (shopee_products 테이블에 저장)
            success = self.supabase_client.insert_shopee_products(formatted_products)
            
            if success:
                logger.info(f"✅ Successfully saved {len(formatted_products)} real Lazada products to Supabase")
                return True
            else:
                logger.error("❌ Failed to save Lazada products to Supabase")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error saving Lazada products to Supabase: {e}")
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
            logger.info("✅ Lazada browser closed")


def main():
    """Lazada 스크래퍼 테스트 함수"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scraper = LazadaScraper(use_undetected=True)
    
    try:
        print("🛒 Testing Lazada scraper...")
        
        # 테스트 검색
        test_keyword = "skincare"
        products = scraper.search_products(test_keyword, limit=5)
        
        print(f"✅ Found {len(products)} real Lazada products for '{test_keyword}'")
        
        if products:
            print("\n📦 Real Lazada products found:")
            for i, product in enumerate(products):
                print(f"{i+1}. {product['product_name'][:50]}... - {product['price']}")
                print(f"   URL: {product['product_url'][:80]}...")
                print()
        
        return products
        
    except Exception as e:
        print(f"❌ Error testing Lazada scraper: {e}")
        return []
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()