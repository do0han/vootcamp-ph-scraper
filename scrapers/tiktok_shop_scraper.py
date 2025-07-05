#!/usr/bin/env python3
"""
TikTok Shop Philippines Scraper
TikTok Shop 필리핀 스크래퍼 - Top Products, Flash Sale, Category Products 수집
"""

import time
import random
import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import sys

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium.webdriver.common.action_chains import ActionChains
except ImportError as e:
    print(f"Selenium import error: {e}")

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import quote, urljoin, urlparse

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class TikTokShopScraper:
    """TikTok Shop Philippines 스크래퍼"""
    
    def __init__(
        self,
        base_url: str = "https://www.tiktok.com/shop/ph",
        use_undetected: bool = True,
        headless: bool = True
    ):
        self.base_url = base_url
        self.use_undetected = use_undetected
        self.headless = headless
        self.driver = None
        self.user_agent = UserAgent()
        self.collection_date = datetime.now()
        self.wait_timeout = 30
        
        # TikTok Shop 특화 설정 (실제 확인된 구조 기반)
        self.shop_sections = {
            "top_products": "",  # 메인 페이지가 top products
            "flash_sale": "/flash-sale", 
            "categories": "/category",
            "trending": "/trending",
            "search": "/search"
        }
        
        logger.info("🎬 TikTok Shop Scraper initialized")
    
    def _setup_driver(self):
        """TikTok Shop 최적화된 브라우저 설정"""
        try:
            if self.use_undetected:
                options = uc.ChromeOptions()
                
                if self.headless:
                    options.add_argument('--headless=new')
                
                # 기본 스텔스 옵션
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--window-size=1366,768')
                
                # TikTok 특화 설정
                options.add_argument('--disable-features=VizDisplayCompositor')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-plugins')
                options.add_argument('--disable-images')  # 이미지 로딩 비활성화로 속도 향상
                
                # Philippines 지역 설정
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                options.add_argument(f'--user-agent={user_agent}')
                options.add_argument('--lang=en-PH,en-US,en')
                options.add_argument('--accept-lang=en-PH,en-US,en')
                
                # 지리적 위치 설정 (Philippines)
                prefs = {
                    "profile.default_content_setting_values.geolocation": 1,
                    "profile.managed_default_content_settings.images": 2  # 이미지 차단
                }
                options.add_experimental_option("prefs", prefs)
                
                self.driver = uc.Chrome(options=options, version_main=None)
            
            # WebDriver 탐지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.set_page_load_timeout(60)
            
            logger.info("✅ TikTok Shop WebDriver setup completed")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup WebDriver: {e}")
            raise
    
    def _wait_and_scroll(self, wait_time: int = 10, scroll_count: int = 3):
        """TikTok Shop 페이지 로드 대기 및 스크롤링"""
        try:
            time.sleep(wait_time)
            
            # 페이지 완전 로드 확인
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # TikTok Shop 특화 로딩 대기
            # 상품 그리드나 리스트가 로드될 때까지 대기
            potential_selectors = [
                '[data-testid="product-card"]',
                '.product-item',
                '.shop-product-card',
                '[class*="product"]',
                '[class*="item-card"]'
            ]
            
            loaded = False
            for selector in potential_selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✅ Products loaded with selector: {selector}")
                    loaded = True
                    break
                except TimeoutException:
                    continue
            
            if not loaded:
                logger.warning("⚠️ No product elements detected with common selectors")
            
            # 점진적 스크롤링으로 동적 콘텐츠 로드
            for i in range(scroll_count):
                scroll_position = (i + 1) * 800
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(random.uniform(2, 4))
                
                # 새로운 상품이 로딩되었는지 확인
                try:
                    self.driver.execute_script("return document.querySelector('[data-testid=\"loading\"]')")
                    time.sleep(2)  # 로딩 완료 대기
                except:
                    pass
            
            # 맨 위로 다시 스크롤
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            logger.info("✅ TikTok Shop page loading and scrolling completed")
            
        except Exception as e:
            logger.warning(f"⚠️ Scroll and wait warning: {e}")
    
    def _extract_price_value(self, price_text: str) -> Optional[float]:
        """가격 문자열에서 숫자 값 추출 (₱ 또는 PHP)"""
        try:
            if not price_text:
                return None
            # ₱ 기호와 쉼표 제거, 숫자만 추출
            price_clean = re.sub(r'[₱PHP,\s]', '', str(price_text))
            price_match = re.search(r'(\d+(?:\.\d+)?)', price_clean)
            if price_match:
                return float(price_match.group(1))
            return None
        except:
            return None
    
    def _extract_number_value(self, text: str) -> Optional[int]:
        """텍스트에서 숫자 값 추출 (판매량, 리뷰 수 등)"""
        try:
            if not text:
                return None
            # 1.2k -> 1200, 5.8M -> 5800000 변환
            text_clean = str(text).lower().replace(',', '')
            
            # k, m 단위 처리
            if 'k' in text_clean:
                number_match = re.search(r'(\d+(?:\.\d+)?)k', text_clean)
                if number_match:
                    return int(float(number_match.group(1)) * 1000)
            elif 'm' in text_clean:
                number_match = re.search(r'(\d+(?:\.\d+)?)m', text_clean)
                if number_match:
                    return int(float(number_match.group(1)) * 1000000)
            else:
                # 일반 숫자
                number_match = re.search(r'(\d+)', text_clean)
                if number_match:
                    return int(number_match.group(1))
            
            return None
        except:
            return None
    
    def _extract_rating_value(self, rating_text: str) -> Optional[float]:
        """평점 추출 (별점 또는 숫자)"""
        try:
            if not rating_text:
                return None
            rating_match = re.search(r'(\d+\.?\d*)', str(rating_text))
            if rating_match:
                rating = float(rating_match.group(1))
                return min(rating, 5.0)  # 5.0 이하로 제한
            return None
        except:
            return None
    
    def get_top_products(self, limit: int = 20) -> List[Dict[str, Any]]:
        """TikTok Shop Top Products 수집"""
        try:
            if not self.driver:
                self._setup_driver()
            
            # Top Products 페이지로 이동
            top_products_url = f"{self.base_url}{self.shop_sections['top_products']}"
            logger.info(f"🎯 Navigating to Top Products: {top_products_url}")
            
            self.driver.get(top_products_url)
            self._wait_and_scroll(15, 4)
            
            # 봇 감지 확인
            if self._check_bot_detection():
                logger.warning("❌ Bot detection triggered on Top Products page")
                return []
            
            # 상품 요소 찾기
            product_elements = self._find_product_elements()
            
            if not product_elements:
                logger.warning("❌ No product elements found on Top Products page")
                return []
            
            # 상품 데이터 추출
            products = self._extract_products_data(product_elements, "top_products", limit)
            
            logger.info(f"✅ Extracted {len(products)} top products from TikTok Shop")
            return products
            
        except Exception as e:
            logger.error(f"❌ Error getting top products: {e}")
            return []
    
    def get_flash_sale_products(self, limit: int = 15) -> List[Dict[str, Any]]:
        """TikTok Shop Flash Sale 제품 수집"""
        try:
            if not self.driver:
                self._setup_driver()
            
            # Flash Sale 페이지로 이동
            flash_sale_url = f"{self.base_url}{self.shop_sections['flash_sale']}"
            logger.info(f"⚡ Navigating to Flash Sale: {flash_sale_url}")
            
            self.driver.get(flash_sale_url)
            self._wait_and_scroll(15, 3)
            
            # 봇 감지 확인
            if self._check_bot_detection():
                logger.warning("❌ Bot detection triggered on Flash Sale page")
                return []
            
            # 상품 요소 찾기
            product_elements = self._find_product_elements()
            
            if not product_elements:
                logger.warning("❌ No product elements found on Flash Sale page")
                return []
            
            # Flash Sale 특화 데이터 추출
            products = self._extract_products_data(product_elements, "flash_sale", limit)
            
            logger.info(f"✅ Extracted {len(products)} flash sale products from TikTok Shop")
            return products
            
        except Exception as e:
            logger.error(f"❌ Error getting flash sale products: {e}")
            return []
    
    def get_category_products(self, category: str, limit: int = 15) -> List[Dict[str, Any]]:
        """TikTok Shop 카테고리별 제품 수집"""
        try:
            if not self.driver:
                self._setup_driver()
            
            # 카테고리 검색 URL 구성
            category_url = f"{self.base_url}/search?q={quote(category)}"
            logger.info(f"📂 Navigating to Category '{category}': {category_url}")
            
            self.driver.get(category_url)
            self._wait_and_scroll(15, 3)
            
            # 봇 감지 확인
            if self._check_bot_detection():
                logger.warning("❌ Bot detection triggered on Category page")
                return []
            
            # 상품 요소 찾기
            product_elements = self._find_product_elements()
            
            if not product_elements:
                logger.warning(f"❌ No product elements found for category '{category}'")
                return []
            
            # 카테고리 특화 데이터 추출
            products = self._extract_products_data(product_elements, f"category_{category}", limit)
            
            logger.info(f"✅ Extracted {len(products)} products from category '{category}'")
            return products
            
        except Exception as e:
            logger.error(f"❌ Error getting category products: {e}")
            return []
    
    def _check_bot_detection(self) -> bool:
        """봇 감지 여부 확인"""
        try:
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # 일반적인 봇 감지 패턴
            bot_indicators = [
                'captcha', 'verify', 'robot', 'automation',
                'blocked', 'access denied', 'suspicious'
            ]
            
            for indicator in bot_indicators:
                if indicator in page_source or indicator in current_url.lower():
                    return True
            
            # TikTok 특화 감지 패턴
            tiktok_blocks = [
                'please verify', 'security check', 'unusual traffic'
            ]
            
            for block in tiktok_blocks:
                if block in page_source:
                    return True
            
            return False
            
        except:
            return False
    
    def _find_product_elements(self) -> List:
        """TikTok Shop 상품 요소 찾기 (실제 페이지 구조 기반)"""
        
        # 실제 TikTok Shop 페이지에서 발견된 패턴 기반 선택자
        product_selectors = [
            # 분석에서 발견된 product 클래스들 (435개)
            '[class*="product"]',
            'div[class*="product"]',
            
            # item 클래스들 (126개)  
            '[class*="item"]',
            'div[class*="item"]',
            
            # 일반적인 상품 컨테이너
            '[class*="card"]',
            '[class*="Card"]',
            
            # TikTok 특화 data 속성
            '[data-e2e*="product"]',
            '[data-e2e*="item"]',
            '[data-testid*="product"]',
            '[data-testid*="item"]',
            
            # 링크 기반 상품 (a 태그 안의 상품들)
            'a[href*="/product/"]',
            'a[class*="product"]',
            
            # 이미지와 가격이 함께 있는 요소들
            'div:has(img):has([class*="price"])',
            'div:has(img):has(span:contains("₱"))',
            
            # 마지막 수단: 구조적 접근
            'div > div > div:has(img)',  # 3단계 depth의 이미지 포함 div
            'div[class]:has(img):has(span)'  # 클래스가 있고 이미지와 span을 포함
        ]
        
        found_elements = []
        
        for selector in product_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) >= 3:  # 최소 3개 이상 발견되면 유효
                    found_elements = elements
                    logger.info(f"✅ Found {len(elements)} product elements using: {selector}")
                    break
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        return found_elements
    
    def _extract_products_data(self, elements: List, source_type: str, limit: int) -> List[Dict[str, Any]]:
        """상품 요소에서 데이터 추출"""
        products = []
        
        for i, element in enumerate(elements[:limit]):
            try:
                product_data = {
                    'collection_date': self.collection_date.isoformat(),
                    'source_type': source_type,
                    'platform': 'tiktok_shop',
                    'product_name': 'Unknown Product',
                    'product_url': '',
                    'price': '',
                    'price_numeric': None,
                    'original_price': '',
                    'original_price_numeric': None,
                    'discount_percentage': None,
                    'rating': None,
                    'rating_numeric': None,
                    'review_count': None,
                    'review_count_numeric': None,
                    'sales_count': None,
                    'sales_count_numeric': None,
                    'image_url': '',
                    'category': '',
                    'brand': '',
                    'seller_info': '',
                    'creator_info': None  # 제휴 크리에이터 정보 (나중에 확장)
                }
                
                # 제품명 추출
                name_selectors = [
                    '[data-testid="product-title"]',
                    '.product-title',
                    '.product-name', 
                    'h3', 'h4', 'h5',
                    '[class*="title"]',
                    '[class*="name"]'
                ]
                
                for selector in name_selectors:
                    try:
                        name_element = element.find_element(By.CSS_SELECTOR, selector)
                        name = name_element.text or name_element.get_attribute('title')
                        if name and name.strip():
                            product_data['product_name'] = name.strip()
                            break
                    except:
                        continue
                
                # 가격 추출
                price_selectors = [
                    '[data-testid="product-price"]',
                    '.price',
                    '.current-price',
                    '[class*="price"]',
                    '.cost'
                ]
                
                for selector in price_selectors:
                    try:
                        price_element = element.find_element(By.CSS_SELECTOR, selector)
                        price_text = price_element.text
                        if price_text and ('₱' in price_text or 'PHP' in price_text or price_text.isdigit()):
                            product_data['price'] = price_text.strip()
                            product_data['price_numeric'] = self._extract_price_value(price_text)
                            break
                    except:
                        continue
                
                # URL 추출
                try:
                    link_element = element.find_element(By.TAG_NAME, 'a')
                    href = link_element.get_attribute('href')
                    if href:
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
                    '[data-testid="rating"]',
                    '.rating',
                    '.star-rating',
                    '[class*="rating"]',
                    '[class*="star"]'
                ]
                
                for selector in rating_selectors:
                    try:
                        rating_element = element.find_element(By.CSS_SELECTOR, selector)
                        rating_text = rating_element.text or rating_element.get_attribute('title')
                        if rating_text:
                            product_data['rating'] = rating_text
                            product_data['rating_numeric'] = self._extract_rating_value(rating_text)
                            break
                    except:
                        continue
                
                # 리뷰 수 추출
                review_selectors = [
                    '[data-testid="review-count"]',
                    '.review-count',
                    '.reviews',
                    '[class*="review"]'
                ]
                
                for selector in review_selectors:
                    try:
                        review_element = element.find_element(By.CSS_SELECTOR, selector)
                        review_text = review_element.text
                        if review_text:
                            product_data['review_count'] = review_text
                            product_data['review_count_numeric'] = self._extract_number_value(review_text)
                            break
                    except:
                        continue
                
                # 판매량 추출
                sales_selectors = [
                    '[data-testid="sales-count"]',
                    '.sales-count',
                    '.sold',
                    '[class*="sold"]',
                    '[class*="sales"]'
                ]
                
                for selector in sales_selectors:
                    try:
                        sales_element = element.find_element(By.CSS_SELECTOR, selector)
                        sales_text = sales_element.text
                        if sales_text and 'sold' in sales_text.lower():
                            product_data['sales_count'] = sales_text
                            product_data['sales_count_numeric'] = self._extract_number_value(sales_text)
                            break
                    except:
                        continue
                
                # 유효한 제품인지 확인
                if (product_data['product_name'] != 'Unknown Product' and 
                    product_data['product_url'] and 
                    'tiktok' in product_data['product_url']):
                    
                    products.append(product_data)
                    logger.debug(f"✅ Extracted product: {product_data['product_name'][:50]}...")
                
            except Exception as e:
                logger.debug(f"⚠️ Error extracting product {i}: {e}")
                continue
        
        return products
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("✅ TikTok Shop scraper browser closed")


def main():
    """TikTok Shop 스크래퍼 테스트"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scraper = TikTokShopScraper(use_undetected=True, headless=True)
    
    try:
        print("🎬 Testing TikTok Shop Scraper...")
        print("=" * 50)
        
        # Top Products 테스트
        print("🎯 Testing Top Products...")
        top_products = scraper.get_top_products(limit=5)
        
        print(f"\n✅ Found {len(top_products)} top products")
        if top_products:
            print("\n🏆 Top Products:")
            for i, product in enumerate(top_products[:3]):
                name = product.get('product_name', 'Unknown')[:40]
                price = product.get('price_numeric', 0)
                rating = product.get('rating_numeric', 0)
                print(f"{i+1}. {name}...")
                print(f"   💰 ₱{price} | ⭐ {rating}")
        
        # Flash Sale 테스트 (시간이 허락하면)
        print(f"\n⚡ Testing Flash Sale...")
        flash_products = scraper.get_flash_sale_products(limit=3)
        
        print(f"\n✅ Found {len(flash_products)} flash sale products")
        
        # 카테고리 테스트
        print(f"\n📂 Testing Category Search...")
        category_products = scraper.get_category_products("beauty", limit=3)
        
        print(f"\n✅ Found {len(category_products)} beauty category products")
        
        return top_products + flash_products + category_products
        
    except Exception as e:
        print(f"❌ Error testing TikTok Shop scraper: {e}")
        return []
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()