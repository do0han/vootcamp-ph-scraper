"""
Persona-targeted Lazada Philippines scraper
페르소나 타겟 Lazada 스크래퍼 - 20-35세 필리핀 여성 타겟
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

# Import project modules
try:
    from database.supabase_client import SupabaseClient
except ImportError:
    SupabaseClient = None
    print("⚠️ SupabaseClient not available - data will not be saved to database")

from config.persona_config import (
    TARGET_PERSONAS, 
    get_persona_keywords, 
    get_persona_filters,
    get_current_persona,
    ACTIVE_PERSONA
)

logger = logging.getLogger(__name__)


class LazadaPersonaScraper:
    """페르소나 타겟 Lazada 스크래퍼"""
    
    def __init__(
        self,
        persona_name: str = ACTIVE_PERSONA,
        base_url: str = "https://www.lazada.com.ph",
        use_undetected: bool = True
    ):
        self.persona_name = persona_name
        self.persona = TARGET_PERSONAS.get(persona_name)
        self.persona_filters = get_persona_filters(persona_name)
        
        if not self.persona:
            raise ValueError(f"Unknown persona: {persona_name}")
        
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
        
        logger.info(f"🎯 Initialized persona scraper for: {self.persona.name}")
    
    def _setup_driver(self):
        """브라우저 설정"""
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
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            
            logger.info("✅ Persona-targeted WebDriver setup completed")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup WebDriver: {e}")
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
            
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            logger.info("✅ Page loading and scrolling completed")
            
        except Exception as e:
            logger.warning(f"⚠️ Scroll and wait warning: {e}")
    
    def _extract_price_value(self, price_text: str) -> Optional[float]:
        """가격 문자열에서 숫자 값 추출"""
        try:
            if not price_text:
                return None
            # ₱ 기호와 쉼표 제거, 숫자만 추출
            price_match = re.search(r'[\\d,]+\\.?\\d*', str(price_text).replace(',', ''))
            if price_match:
                return float(price_match.group())
            return None
        except:
            return None
    
    def _extract_rating_value(self, rating_text: str) -> Optional[float]:
        """평점 문자열에서 숫자 값 추출"""
        try:
            if not rating_text:
                return None
            rating_match = re.search(r'(\\d+\\.?\\d*)', str(rating_text))
            if rating_match:
                rating = float(rating_match.group(1))
                return min(rating, 5.0)  # 5.0 이하로 제한
            return None
        except:
            return None
    
    def _extract_review_count(self, review_text: str) -> Optional[int]:
        """리뷰 수 추출"""
        try:
            if not review_text:
                return None
            # 숫자만 추출 (1.2k -> 1200 변환 등)
            review_match = re.search(r'(\\d+(?:\\.\\d+)?)(k|K)?', str(review_text))
            if review_match:
                number = float(review_match.group(1))
                multiplier = review_match.group(2)
                if multiplier and multiplier.lower() == 'k':
                    number *= 1000
                return int(number)
            return None
        except:
            return None
    
    def _is_persona_relevant(self, product_data: Dict[str, Any]) -> bool:
        """페르소나 타겟에 적합한 제품인지 확인"""
        try:
            # 가격 체크
            price = product_data.get('price_numeric')
            if price:
                price_in_range = False
                for price_range in self.persona_filters.get('price_ranges', []):
                    if price_range[0] <= price <= price_range[1]:
                        price_in_range = True
                        break
                
                # 최대 가격 체크
                max_price = self.persona_filters.get('max_price', 10000)
                if price > max_price:
                    return False
                    
                if not price_in_range and price > max_price * 0.5:  # 최대 가격의 50% 이상이면 엄격하게
                    return False
            
            # 평점 체크
            rating = product_data.get('rating_numeric')
            min_rating = self.persona_filters.get('min_rating', 3.5)
            if rating and rating < min_rating:
                return False
            
            # 리뷰 수 체크
            reviews = product_data.get('review_count_numeric')
            min_reviews = self.persona_filters.get('min_reviews', 10)
            if reviews and reviews < min_reviews:
                return False
            
            # 브랜드 선호도 체크 (보너스 점수)
            product_name = product_data.get('product_name', '').lower()
            preferred_brands = [brand.lower() for brand in self.persona_filters.get('preferred_brands', [])]
            
            brand_bonus = any(brand in product_name for brand in preferred_brands)
            product_data['brand_bonus'] = brand_bonus
            
            return True
            
        except Exception as e:
            logger.debug(f"Error checking persona relevance: {e}")
            return False
    
    def _calculate_persona_score(self, product_data: Dict[str, Any]) -> float:
        """페르소나 적합도 점수 계산 (0-100)"""
        score = 0.0
        
        try:
            # 가격 점수 (30점 만점)
            price = product_data.get('price_numeric')
            if price:
                # 페르소나 선호 가격대에 있으면 높은 점수
                price_score = 0
                for price_range in self.persona_filters.get('price_ranges', []):
                    if price_range[0] <= price <= price_range[1]:
                        # 가격대 중간에 가까울수록 높은 점수
                        mid_price = (price_range[0] + price_range[1]) / 2
                        distance_ratio = abs(price - mid_price) / (price_range[1] - price_range[0])
                        price_score = max(price_score, 30 * (1 - distance_ratio))
                        break
                score += price_score
            
            # 평점 점수 (25점 만점)
            rating = product_data.get('rating_numeric')
            if rating:
                score += min(25, (rating / 5.0) * 25)
            
            # 리뷰 수 점수 (20점 만점)
            reviews = product_data.get('review_count_numeric')
            if reviews:
                # 로그 스케일로 리뷰 수 점수 계산
                import math
                review_score = min(20, math.log10(max(1, reviews)) * 5)
                score += review_score
            
            # 브랜드 보너스 (15점)
            if product_data.get('brand_bonus', False):
                score += 15
            
            # 키워드 매칭 보너스 (10점)
            product_name = product_data.get('product_name', '').lower()
            persona_keywords = [kw.lower() for kw in self.persona.keywords[:20]]  # 상위 20개 키워드
            
            keyword_matches = sum(1 for kw in persona_keywords if kw in product_name)
            keyword_score = min(10, keyword_matches * 2)
            score += keyword_score
            
        except Exception as e:
            logger.debug(f"Error calculating persona score: {e}")
        
        return min(100, score)
    
    def _extract_product_data(self, product_elements: list) -> List[Dict[str, Any]]:
        """제품 요소에서 페르소나 타겟 데이터 추출"""
        products = []
        
        for i, element in enumerate(product_elements):
            try:
                product_data = {
                    'collection_date': self.collection_date.isoformat(),
                    'search_keyword': '',
                    'product_name': 'Unknown Product',
                    'product_url': '',
                    'price': '',
                    'price_numeric': None,
                    'seller_name': 'Unknown Seller',
                    'rating': None,
                    'rating_numeric': None,
                    'review_count': None,
                    'review_count_numeric': None,
                    'image_url': '',
                    'platform': 'lazada',
                    'persona_target': self.persona_name,
                    'persona_score': 0
                }
                
                # 제품명 추출
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
                
                # 가격 추출
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
                    '.rating-star',
                    '.score-average',
                    '[data-qa-locator="product-rating"]'
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
                    '.review-count',
                    '.reviews',
                    '[data-qa-locator="reviews"]'
                ]
                
                for selector in review_selectors:
                    try:
                        review_element = element.find_element(By.CSS_SELECTOR, selector)
                        review_text = review_element.text
                        if review_text:
                            product_data['review_count'] = review_text
                            product_data['review_count_numeric'] = self._extract_review_count(review_text)
                            break
                    except:
                        continue
                
                # 페르소나 적합성 체크
                if self._is_persona_relevant(product_data):
                    # 페르소나 점수 계산
                    product_data['persona_score'] = self._calculate_persona_score(product_data)
                    
                    # 유효한 제품인지 확인
                    if (product_data['product_name'] != 'Unknown Product' and 
                        product_data['product_url'] and 
                        'lazada.com.ph' in product_data['product_url']):
                        
                        products.append(product_data)
                        logger.debug(f"✅ Persona-matched product: {product_data['product_name'][:50]}... (Score: {product_data['persona_score']:.1f})")
                
            except Exception as e:
                logger.debug(f"⚠️ Error extracting product {i}: {e}")
                continue
        
        # 페르소나 점수 기준으로 정렬
        products.sort(key=lambda x: x['persona_score'], reverse=True)
        
        return products
    
    def search_persona_products(self, base_keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """페르소나 타겟 제품 검색"""
        try:
            if not self.driver:
                self._setup_driver()
            
            # 페르소나 기반 키워드 생성
            persona_keywords = get_persona_keywords(self.persona_name, base_keyword)
            search_keyword = random.choice(persona_keywords[:10])  # 상위 10개 중 랜덤 선택
            
            # 검색 URL 구성 (가격 필터 포함)
            max_price = self.persona_filters.get('max_price', 5000)
            search_url = f"{self.base_url}/catalog/?q={quote(search_keyword)}&sort=priceasc&priceto={max_price}"
            
            logger.info(f"🎯 Persona search for: {search_keyword} (max ₱{max_price})")
            logger.info(f"📍 Navigating to: {search_url}")
            
            # 페이지 로드
            self.driver.get(search_url)
            self._wait_and_scroll(15)
            
            # 봇 감지 확인
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            if 'captcha' in page_source or 'verify' in current_url:
                logger.warning("❌ Bot detection triggered")
                return []
            
            # 제품 요소 찾기
            product_selectors = [
                '[data-qa-locator="product-item"]',
                '.product-item',
                '.item-box',
                '.product-card'
            ]
            
            found_elements = []
            for selector in product_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) >= 3:
                        found_elements = elements
                        logger.info(f"✅ Found {len(elements)} product elements using: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not found_elements:
                logger.warning("❌ No product elements found")
                return []
            
            # 페르소나 타겟 데이터 추출
            products = self._extract_product_data(found_elements)
            
            # 검색 키워드 설정
            for product in products:
                product['search_keyword'] = search_keyword
                product['base_category'] = base_keyword
            
            # 제한된 수만 반환 (고득점 순)
            final_products = products[:limit]
            
            logger.info(f"✅ Found {len(final_products)} persona-targeted products for '{search_keyword}'")
            
            if final_products:
                avg_score = sum(p['persona_score'] for p in final_products) / len(final_products)
                logger.info(f"📊 Average persona score: {avg_score:.1f}/100")
            
            return final_products
            
        except Exception as e:
            logger.error(f"❌ Error in persona product search: {e}")
            return []
    
    def get_persona_trending_products(self, limit: int = 20, save_to_db: bool = True) -> List[Dict[str, Any]]:
        """페르소나 타겟 트렌딩 제품 수집"""
        try:
            logger.info(f"📈 Collecting persona-targeted products for: {self.persona.name}")
            
            # 페르소나 관심사 기반 카테고리
            categories = self.persona.interests[:6]  # 상위 6개 관심사
            
            all_products = []
            products_per_category = max(1, limit // len(categories))
            
            for category in categories:
                try:
                    logger.info(f"🏷️ Searching persona category: {category}")
                    products = self.search_persona_products(category, limit=products_per_category)
                    
                    # 카테고리 정보 추가
                    for product in products:
                        product['persona_category'] = category
                        product['product_type'] = f'persona_trending_{self.persona_name}'
                        
                    all_products.extend(products)
                    
                    # 카테고리 간 대기
                    time.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error with category '{category}': {e}")
                    continue
            
            # 중복 제거 (URL 기준)
            seen_urls = set()
            unique_products = []
            for product in all_products:
                url = product.get('product_url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_products.append(product)
            
            # 페르소나 점수 기준으로 재정렬 및 제한
            unique_products.sort(key=lambda x: x['persona_score'], reverse=True)
            final_products = unique_products[:limit]
            
            logger.info(f"✅ Collected {len(final_products)} persona-targeted products")
            
            if final_products:
                avg_score = sum(p['persona_score'] for p in final_products) / len(final_products)
                high_score_count = sum(1 for p in final_products if p['persona_score'] > 70)
                logger.info(f"📊 Persona targeting stats:")
                logger.info(f"   - Average score: {avg_score:.1f}/100")
                logger.info(f"   - High relevance (>70): {high_score_count}/{len(final_products)}")
            
            # 데이터베이스 저장
            if save_to_db and final_products:
                self._save_to_supabase(final_products)
            
            return final_products
            
        except Exception as e:
            logger.error(f"❌ Error collecting persona trending products: {e}")
            return []
    
    def _save_to_supabase(self, products: List[Dict[str, Any]]) -> bool:
        """페르소나 타겟 제품을 Supabase에 저장"""
        if not self.supabase_client:
            logger.warning("⚠️ Supabase client not available - skipping database save")
            return False
        
        if not products:
            logger.info("ℹ️ No persona products to save to database")
            return True
        
        try:
            logger.info(f"💾 Saving {len(products)} persona-targeted products to Supabase...")
            
            # 데이터 포맷팅
            formatted_products = []
            for product in products:
                formatted_product = {
                    'collection_date': product.get('collection_date', self.collection_date.isoformat()),
                    'search_keyword': product.get('search_keyword', 'persona_search'),
                    'product_name': product.get('product_name', 'Unknown Product'),
                    'seller_name': product.get('seller_name', 'Lazada Seller'),
                    'price': product.get('price_numeric'),
                    'currency': 'PHP',
                    'rating': product.get('rating_numeric'),
                    'review_count': product.get('review_count_numeric'),
                    'product_url': product.get('product_url'),
                    'image_url': product.get('image_url'),
                    'category': product.get('persona_category', product.get('base_category', 'general')),
                    'discount_info': {
                        'platform': 'lazada',
                        'is_real_data': True,
                        'scrape_method': 'persona_targeted',
                        'persona_name': self.persona_name,
                        'persona_score': product.get('persona_score', 0),
                        'brand_bonus': product.get('brand_bonus', False),
                        'collection_timestamp': self.collection_date.isoformat()
                    }
                }
                formatted_products.append(formatted_product)
            
            # 데이터베이스 저장
            success = self.supabase_client.insert_shopee_products(formatted_products)
            
            if success:
                logger.info(f"✅ Successfully saved {len(formatted_products)} persona-targeted products")
                return True
            else:
                logger.error("❌ Failed to save persona products to Supabase")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error saving persona products to Supabase: {e}")
            return False
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("✅ Persona scraper browser closed")


def main():
    """페르소나 타겟 스크래퍼 테스트"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Young Filipina 페르소나로 테스트
    scraper = LazadaPersonaScraper(persona_name="young_filipina", use_undetected=True)
    
    try:
        print("🎯 Testing Persona-Targeted Lazada scraper...")
        print(f"Target: {scraper.persona.name}")
        print(f"Age: {scraper.persona.age_group.value}")
        print(f"Interests: {scraper.persona.interests[:5]}")
        
        # 페르소나 타겟 제품 수집
        products = scraper.get_persona_trending_products(limit=10)
        
        print(f"\\n✅ Found {len(products)} persona-targeted products")
        
        if products:
            print("\\n🎯 Top persona-matched products:")
            for i, product in enumerate(products[:5]):
                score = product.get('persona_score', 0)
                price = product.get('price_numeric', 0)
                rating = product.get('rating_numeric', 0)
                print(f"{i+1}. {product['product_name'][:40]}...")
                print(f"   💰 ₱{price} | ⭐ {rating} | 🎯 Score: {score:.1f}/100")
                print(f"   🏷️ Category: {product.get('persona_category', 'N/A')}")
                print()
        
        return products
        
    except Exception as e:
        print(f"❌ Error testing persona scraper: {e}")
        return []
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()