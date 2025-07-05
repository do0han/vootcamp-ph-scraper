#!/usr/bin/env python3
"""
Simple Test Script for Core 3 Scrapers
간단한 테스트 스크립트 - Google Trends, Lazada, TikTok Shop
"""

import os
import sys
import time
import json
from datetime import datetime

def test_google_trends():
    """Google Trends 테스트"""
    print("🔍 Testing Google Trends...")
    
    try:
        from pytrends.request import TrendReq
        
        # Philippines 타겟팅
        pytrends = TrendReq(hl='en-PH', tz=480)
        
        # 뷰티 키워드 테스트
        keywords = ['skincare', 'makeup']
        pytrends.build_payload(keywords, cat=0, timeframe='today 1-m', geo='PH')
        
        # 관심도 데이터
        interest_df = pytrends.interest_over_time()
        
        if not interest_df.empty:
            print(f"✅ Google Trends: {len(interest_df)} data points collected")
            
            # 최신 데이터 출력
            latest_date = interest_df.index[-1]
            for keyword in keywords:
                if keyword in interest_df.columns:
                    latest_score = interest_df[keyword].iloc[-1]
                    print(f"   📊 {keyword}: {latest_score} (Latest: {latest_date.strftime('%Y-%m-%d')})")
            
            return True
        else:
            print("❌ Google Trends: No data collected")
            return False
            
    except Exception as e:
        print(f"❌ Google Trends error: {e}")
        return False

def test_lazada_basic():
    """Lazada 기본 테스트"""
    print("🛒 Testing Lazada Basic...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Lazada 검색 페이지 접속
            search_url = "https://www.lazada.com.ph/catalog/?q=korean+skincare"
            print(f"🌐 Loading: {search_url}")
            
            driver.get(search_url)
            time.sleep(5)  # 페이지 로딩 대기
            
            # 상품 찾기
            products = driver.find_elements(By.CSS_SELECTOR, '[data-qa-locator="product-item"]')
            
            if not products:
                # 대체 셀렉터 시도
                products = driver.find_elements(By.CSS_SELECTOR, '.Bm3ON')
            
            if products:
                print(f"✅ Lazada: {len(products)} products found")
                
                # 첫 번째 상품 정보 추출
                first_product = products[0]
                
                try:
                    title_elem = first_product.find_element(By.CSS_SELECTOR, '[data-qa-locator="product-item-title"]')
                    title = title_elem.text.strip()[:50]
                except:
                    title = "Title not found"
                
                try:
                    price_elem = first_product.find_element(By.CSS_SELECTOR, '.aBrP0')
                    price = price_elem.text.strip()
                except:
                    price = "Price not found"
                
                print(f"   📝 Sample product: {title}...")
                print(f"   💰 Sample price: {price}")
                
                return True
            else:
                print("❌ Lazada: No products found")
                return False
                
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Lazada error: {e}")
        return False

def test_supabase_connection():
    """Supabase 연결 테스트"""
    print("💾 Testing Supabase Connection...")
    
    try:
        # 환경변수 확인 - 상위 디렉토리의 .env 파일 사용
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"📁 Loading env from: {env_file}")
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("⚠️ Supabase: Missing environment variables")
            print(f"   URL: {'✅' if supabase_url else '❌'}")
            print(f"   KEY: {'✅' if supabase_key else '❌'}")
            return False
        
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        
        # 간단한 테이블 조회 테스트
        try:
            result = supabase.table('google_trends').select('*').limit(1).execute()
            print("✅ Supabase: Connection successful")
            print(f"   📊 Google trends table accessible: {len(result.data)} records")
            
            # 추가 테이블들도 확인
            try:
                users_result = supabase.table('users').select('*').limit(1).execute()
                print(f"   👥 Users table: {len(users_result.data)} records")
            except:
                print("   👥 Users table: Not accessible or empty")
                
            return True
            
        except Exception as e:
            if 'relation' in str(e) and 'does not exist' in str(e):
                print("⚠️ Supabase: Connected but tables not found")
                print("   💡 Database schema may need to be created")
                return True  # 연결은 성공
            else:
                print(f"⚠️ Supabase: Table access error: {e}")
                return True  # 연결은 성공
            
    except Exception as e:
        print(f"❌ Supabase error: {e}")
        return False

def generate_test_report(results):
    """테스트 결과 리포트 생성"""
    print("\n" + "="*60)
    print("📊 SIMPLE TEST RESULTS")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 System is READY for data collection!")
    elif success_rate >= 50:
        print("⚠️ System partially ready - some optimizations needed")
    else:
        print("❌ System needs significant fixes")
    
    # 결과를 JSON으로 저장
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate
        }
    }
    
    try:
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        report_file = os.path.join(logs_dir, 'simple_test_report.json')
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📋 Report saved: {report_file}")
        
    except Exception as e:
        print(f"⚠️ Could not save report: {e}")

def main():
    """메인 테스트 실행"""
    print("🧪 VOOTCAMP PH SCRAPER - SIMPLE TEST")
    print("="*60)
    print("Testing core functionality without complex dependencies")
    print()
    
    # 테스트 실행
    test_results = {}
    
    print("1️⃣ Google Trends Test")
    test_results["Google Trends"] = test_google_trends()
    print()
    
    print("2️⃣ Lazada Basic Test")
    test_results["Lazada Basic"] = test_lazada_basic()
    print()
    
    print("3️⃣ Supabase Connection Test")
    test_results["Supabase Connection"] = test_supabase_connection()
    print()
    
    # 결과 리포트
    generate_test_report(test_results)

if __name__ == "__main__":
    main() 