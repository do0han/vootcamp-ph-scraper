#!/usr/bin/env python3
"""
Live Scrapers Test
실제 스크래퍼 동작 테스트
"""

import os
import sys
import logging
import time
import traceback
from datetime import datetime
from unittest.mock import Mock

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/live_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('live_test')

def test_google_trends_direct():
    """Google Trends 직접 테스트"""
    logger = setup_logging()
    logger.info("🔍 Testing Google Trends scraper directly...")
    
    try:
        # Direct pytrends test
        from pytrends.request import TrendReq
        
        pytrends = TrendReq(hl='en-US', tz=360)
        test_keywords = ["skincare", "fashion"]
        
        logger.info(f"Testing keywords: {test_keywords}")
        pytrends.build_payload(test_keywords, cat=0, timeframe='today 1-m', geo='PH', gprop='')
        
        # Get interest over time
        interest_data = pytrends.interest_over_time()
        
        if not interest_data.empty:
            logger.info(f"✅ Google Trends: {len(interest_data)} data points collected")
            logger.info(f"   Latest data: {interest_data.tail(1).to_dict()}")
            return True, len(interest_data)
        else:
            logger.warning("⚠️ Google Trends: No data returned")
            return False, 0
            
    except Exception as e:
        logger.error(f"❌ Google Trends test failed: {e}")
        return False, 0

def test_database_operations():
    """데이터베이스 작업 테스트"""
    logger = setup_logging()
    logger.info("💾 Testing database operations...")
    
    try:
        from database.supabase_client import SupabaseClient
        
        client = SupabaseClient()
        logger.info("✅ Database client created successfully")
        
        # Test data to insert
        test_data = {
            "keywords": ["test_keyword"],
            "interest_over_time": {"test_keyword": [10, 20, 30]},
            "related_queries": {},
            "collected_at": datetime.now().isoformat()
        }
        
        # Test insert operation
        client.insert_google_trends(test_data)
        logger.info("✅ Database insert operation successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_selenium_basic():
    """기본 Selenium 테스트"""
    logger = setup_logging()
    logger.info("🌐 Testing basic Selenium functionality...")
    
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.chrome.options import Options
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Create driver
        driver = uc.Chrome(options=chrome_options, version_main=None)
        
        # Test navigation
        driver.get("https://httpbin.org/ip")
        page_source = driver.page_source
        
        driver.quit()
        
        if "origin" in page_source:
            logger.info("✅ Selenium: Basic navigation successful")
            return True
        else:
            logger.warning("⚠️ Selenium: Navigation completed but unexpected content")
            return False
            
    except Exception as e:
        logger.error(f"❌ Selenium test failed: {e}")
        return False

def run_live_system_test():
    """실제 시스템 테스트 실행"""
    logger = setup_logging()
    
    logger.info("=" * 70)
    logger.info("🧪 LIVE CORE 3 SCRAPERS SYSTEM TEST")
    logger.info("🎯 Testing: Google Trends + Database + Selenium")
    logger.info("=" * 70)
    
    results = {}
    
    # Test 1: Google Trends
    logger.info("\n1️⃣ Testing Google Trends API...")
    start_time = time.time()
    trends_success, trends_data_count = test_google_trends_direct()
    trends_duration = time.time() - start_time
    
    results["google_trends"] = {
        "success": trends_success,
        "duration": trends_duration,
        "data_count": trends_data_count
    }
    
    # Brief delay
    time.sleep(2)
    
    # Test 2: Database Operations
    logger.info("\n2️⃣ Testing Database Operations...")
    start_time = time.time()
    db_success = test_database_operations()
    db_duration = time.time() - start_time
    
    results["database"] = {
        "success": db_success,
        "duration": db_duration
    }
    
    # Brief delay
    time.sleep(2)
    
    # Test 3: Selenium Basic
    logger.info("\n3️⃣ Testing Selenium WebDriver...")
    start_time = time.time()
    selenium_success = test_selenium_basic()
    selenium_duration = time.time() - start_time
    
    results["selenium"] = {
        "success": selenium_success,
        "duration": selenium_duration
    }
    
    # Generate report
    logger.info("\n" + "=" * 70)
    logger.info("📊 LIVE TEST RESULTS")
    logger.info("=" * 70)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results.values() if r["success"])
    total_duration = sum(r["duration"] for r in results.values())
    
    logger.info(f"📈 Success Rate: {successful_tests}/{total_tests} ({successful_tests/total_tests:.1%})")
    logger.info(f"⏱️ Total Duration: {total_duration:.2f} seconds")
    
    # Individual results
    for test_name, result in results.items():
        status_emoji = "✅" if result["success"] else "❌"
        logger.info(f"{status_emoji} {test_name.upper()}: {result['duration']:.1f}s")
        
        if test_name == "google_trends" and result.get("data_count"):
            logger.info(f"    └─ Data points collected: {result['data_count']}")
    
    # Overall assessment
    if successful_tests == total_tests:
        logger.info("\n🎉 ALL TESTS PASSED - Core system components working!")
        logger.info("✅ Ready for full scraper deployment")
        status = "SUCCESS"
    elif successful_tests >= 2:
        logger.info("\n⚠️ MOSTLY SUCCESSFUL - Key components working")
        logger.info("💡 Minor issues can be addressed in production")
        status = "PARTIAL_SUCCESS"
    else:
        logger.error("\n❌ CRITICAL ISSUES - Manual intervention needed")
        status = "FAILED"
    
    # Performance assessment
    if total_duration < 30:
        logger.info(f"⚡ Performance: EXCELLENT ({total_duration:.1f}s)")
    elif total_duration < 60:
        logger.info(f"⚡ Performance: GOOD ({total_duration:.1f}s)")
    else:
        logger.info(f"⚡ Performance: ACCEPTABLE ({total_duration:.1f}s)")
    
    logger.info("=" * 70)
    
    return {
        "status": status,
        "success_rate": successful_tests / total_tests,
        "total_duration": total_duration,
        "results": results
    }

def main():
    """메인 테스트 실행"""
    os.makedirs('logs', exist_ok=True)
    
    test_results = run_live_system_test()
    
    # Exit with appropriate code
    if test_results["status"] == "SUCCESS":
        sys.exit(0)
    elif test_results["status"] == "PARTIAL_SUCCESS":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()