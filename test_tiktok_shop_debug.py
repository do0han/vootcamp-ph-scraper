#!/usr/bin/env python3
"""
TikTok Shop 페이지 구조 분석 및 디버깅
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

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
except ImportError as e:
    print(f"Selenium import error: {e}")

def debug_tiktok_shop():
    """TikTok Shop 페이지 구조 분석"""
    
    print("🔍 TikTok Shop 페이지 구조 분석 시작")
    print("=" * 50)
    
    # 브라우저 설정
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1366,768')
    
    # headless 모드 비활성화 (페이지 확인용)
    # options.add_argument('--headless=new')
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    options.add_argument(f'--user-agent={user_agent}')
    
    driver = None
    
    try:
        driver = uc.Chrome(options=options, version_main=None)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # TikTok Shop 페이지들 테스트
        test_urls = [
            "https://shop.tiktok.com/ph",
            "https://shop.tiktok.com/ph/discover", 
            "https://www.tiktok.com/shop",
            "https://shop.tiktok.com"
        ]
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n{i}. 테스트 URL: {url}")
            
            try:
                driver.get(url)
                time.sleep(10)  # 페이지 로딩 대기
                
                # 기본 정보 수집
                current_url = driver.current_url
                title = driver.title
                print(f"   현재 URL: {current_url}")
                print(f"   페이지 제목: {title}")
                
                # 페이지 소스 일부 확인
                page_source = driver.page_source
                print(f"   페이지 크기: {len(page_source)} 문자")
                
                # 일반적인 요소들 확인
                common_elements = [
                    "div", "span", "a", "img", "button",
                    "[class*='product']", "[class*='item']", 
                    "[class*='card']", "[data-testid]"
                ]
                
                print("   발견된 요소들:")
                for element_type in common_elements:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, element_type)
                        if elements:
                            print(f"     {element_type}: {len(elements)}개")
                    except:
                        pass
                
                # 특별한 키워드 검색
                keywords = ["shop", "product", "price", "₱", "PHP", "buy", "cart"]
                found_keywords = []
                
                for keyword in keywords:
                    if keyword.lower() in page_source.lower():
                        found_keywords.append(keyword)
                
                if found_keywords:
                    print(f"   발견된 키워드: {', '.join(found_keywords)}")
                
                # 접근 가능한지 확인
                if "tiktok" in current_url.lower() and len(page_source) > 1000:
                    print("   ✅ 페이지 접근 성공")
                    
                    # 처음 몇 개 div의 클래스명 출력
                    try:
                        divs = driver.find_elements(By.TAG_NAME, "div")[:10]
                        print("   상위 div 클래스들:")
                        for div in divs:
                            class_name = div.get_attribute("class")
                            if class_name:
                                print(f"     .{class_name[:50]}...")
                    except:
                        pass
                    
                    break  # 성공한 URL에서 중단
                else:
                    print("   ❌ 페이지 접근 실패 또는 제한됨")
                
            except Exception as e:
                print(f"   ❌ 오류: {e}")
                continue
        
        # 페이지 스크린샷 저장 (디버깅용)
        try:
            driver.save_screenshot("tiktok_shop_debug.png")
            print(f"\n📸 스크린샷 저장: tiktok_shop_debug.png")
        except:
            pass
            
    except Exception as e:
        print(f"❌ 전체 오류: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    print("\n" + "=" * 50)
    print("🔍 TikTok Shop 분석 완료")

if __name__ == "__main__":
    debug_tiktok_shop()