"""
Shopee 실제 데이터 수집 테스트 및 디버깅
"""

import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from dotenv import load_dotenv

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_shopee_access():
    """Shopee 접근 테스트"""
    driver = None
    try:
        print("🚀 Shopee 실제 데이터 수집 테스트 시작...")
        
        # 간단한 Chrome 설정
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1366,768')
        
        # headless 비활성화로 실제 페이지 확인
        # options.add_argument('--headless=new')
        
        user_agent = UserAgent().random
        options.add_argument(f'--user-agent={user_agent}')
        
        driver = uc.Chrome(options=options, version_main=None)
        
        print("✅ 브라우저 시작됨")
        
        # Shopee 메인 페이지 접근
        url = "https://shopee.ph/search?keyword=skincare&sortBy=sales"
        print(f"📍 접근 중: {url}")
        
        driver.get(url)
        print("⏳ 페이지 로딩 대기 중...")
        time.sleep(15)
        
        # 페이지 제목 확인
        title = driver.title
        print(f"📄 페이지 제목: {title}")
        
        # 현재 URL 확인
        current_url = driver.current_url
        print(f"🔗 현재 URL: {current_url}")
        
        # 봇 감지 여부 확인
        page_source = driver.page_source
        bot_indicators = ["captcha", "verify", "robot", "security", "blocked"]
        
        found_indicators = []
        for indicator in bot_indicators:
            if indicator.lower() in page_source.lower():
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"⚠️ 봇 감지 신호: {found_indicators}")
        else:
            print("✅ 봇 감지 신호 없음")
        
        # 페이지 소스 일부 저장 (디버깅용)
        with open('shopee_page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("📝 페이지 소스를 shopee_page_source.html에 저장됨")
        
        # 제품 요소 찾기 시도
        selectors_to_test = [
            '[data-sqe="item"]',
            '.shopee-search-item-result__item',
            '.col-xs-2-4.shopee-search-item-result__item',
            '.item-card-wrapper',
            'div[data-sqe="item"]',
            'a[data-sqe="link"]',
            '[class*="item"]',
            '[class*="product"]',
            'img[src*="product"]',
            'a[href*="/product/"]'
        ]
        
        print("\n🔍 제품 요소 검색 중...")
        for i, selector in enumerate(selectors_to_test):
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"{i+1:2d}. {selector:<40} → {len(elements):3d} 개 요소")
                
                if len(elements) > 0:
                    # 첫 번째 요소의 정보 출력
                    first_element = elements[0]
                    element_text = first_element.text[:100] if first_element.text else "텍스트 없음"
                    element_tag = first_element.tag_name
                    print(f"     첫 번째 요소: <{element_tag}> {element_text}...")
                    
                    # 이미지나 링크가 있는지 확인
                    try:
                        img = first_element.find_element(By.TAG_NAME, 'img')
                        img_src = img.get_attribute('src')
                        print(f"     이미지 URL: {img_src[:80]}...")
                    except:
                        pass
                    
                    try:
                        link = first_element.find_element(By.TAG_NAME, 'a')
                        link_href = link.get_attribute('href')
                        print(f"     링크 URL: {link_href[:80]}...")
                    except:
                        pass
                        
            except Exception as e:
                print(f"{i+1:2d}. {selector:<40} → 오류: {str(e)[:50]}")
        
        # 스크롤링 테스트
        print("\n⬇️ 페이지 스크롤링 중...")
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {(i+1)*1000});")
            time.sleep(3)
            print(f"   스크롤 {i+1}/3 완료")
        
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # 다시 요소 검색
        print("\n🔍 스크롤 후 재검색...")
        best_selector = None
        max_elements = 0
        
        for selector in selectors_to_test[:5]:  # 상위 5개만 재검사
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) > max_elements:
                    max_elements = len(elements)
                    best_selector = selector
            except:
                pass
        
        if best_selector and max_elements > 0:
            print(f"✅ 최적 선택자: {best_selector} ({max_elements}개 요소)")
            
            # 실제 제품 데이터 추출 시도
            print("\n📦 제품 데이터 추출 시도...")
            elements = driver.find_elements(By.CSS_SELECTOR, best_selector)
            
            for i, element in enumerate(elements[:3]):  # 처음 3개만 테스트
                try:
                    print(f"\n제품 {i+1}:")
                    
                    # 제품명 추출
                    try:
                        name_element = element.find_element(By.CSS_SELECTOR, '[title], span, div')
                        name = name_element.get_attribute('title') or name_element.text
                        print(f"  제품명: {name[:50]}...")
                    except:
                        print("  제품명: 추출 실패")
                    
                    # 가격 추출
                    try:
                        price_element = element.find_element(By.CSS_SELECTOR, '[class*="price"], span, div')
                        price_text = price_element.text
                        if '₱' in price_text:
                            print(f"  가격: {price_text}")
                    except:
                        print("  가격: 추출 실패")
                    
                    # URL 추출
                    try:
                        link_element = element.find_element(By.TAG_NAME, 'a')
                        href = link_element.get_attribute('href')
                        print(f"  URL: {href[:60]}...")
                    except:
                        print("  URL: 추출 실패")
                        
                except Exception as e:
                    print(f"  제품 {i+1} 처리 오류: {e}")
        else:
            print("❌ 제품 요소를 찾을 수 없습니다")
        
        print("\n⏸️ 10초 대기 (수동 확인용)...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("✅ 브라우저 종료")

if __name__ == "__main__":
    test_shopee_access()