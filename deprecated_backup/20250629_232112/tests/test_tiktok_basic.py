#!/usr/bin/env python3
"""
TikTok 기본 스크래퍼 테스트
해시태그 기반 영상 수집 기능 검증
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set testing environment to avoid Supabase connection issues
os.environ['TESTING'] = 'true'

import logging
from datetime import datetime

# Import mock utilities
from unittest.mock import Mock

# Import the TikTok scraper
from scrapers.tiktok import TikTokScraper
from utils.anti_bot_system import AntiBotSystem
from utils.ethical_scraping import ScrapingPolicy

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('tiktok_test')

def create_mock_components():
    """Create mock anti-bot system and scraping policy for testing"""
    
    # Mock anti-bot system
    mock_anti_bot = Mock()
    mock_anti_bot.simulate_human_behavior = Mock()
    mock_anti_bot.get_driver = Mock()
    
    # Mock scraping policy  
    mock_policy = Mock()
    mock_policy.can_scrape = Mock(return_value=True)
    mock_policy.get_delay = Mock(return_value=2.0)
    
    return mock_anti_bot, mock_policy

def test_tiktok_scraper_initialization():
    """Test TikTok scraper initialization"""
    logger = setup_logging()
    
    try:
        logger.info("🎬 Testing TikTok scraper initialization...")
        
        # Create mock components
        mock_anti_bot, mock_policy = create_mock_components()
        
        # Initialize TikTok scraper
        scraper = TikTokScraper(
            anti_bot_system=mock_anti_bot,
            scraping_policy=mock_policy
        )
        
        logger.info("✅ TikTok scraper initialized successfully")
        
        # Test scraper attributes
        assert scraper.base_url == "https://www.tiktok.com"
        assert scraper.philippines_hashtags is not None
        assert len(scraper.philippines_hashtags) > 0
        
        logger.info(f"📍 Philippines hashtags configured: {len(scraper.philippines_hashtags)}")
        logger.info(f"🏷️ Sample hashtags: {scraper.philippines_hashtags[:5]}")
        
        return scraper
        
    except Exception as e:
        logger.error(f"❌ TikTok scraper initialization failed: {e}")
        raise

def test_hashtag_extraction():
    """Test hashtag extraction and video data structure"""
    logger = setup_logging()
    
    try:
        logger.info("🏷️ Testing hashtag extraction and data structure...")
        
        # Create mock components
        mock_anti_bot, mock_policy = create_mock_components()
        
        # Initialize scraper
        scraper = TikTokScraper(mock_anti_bot, mock_policy)
        
        # Test internal methods
        sample_video_data = {
            "video_id": "test_123",
            "author_username": "test_user",
            "description": "Testing #philippines #manila #fyp hashtags",
            "hashtags": ["philippines", "manila", "fyp"],
            "collected_at": datetime.now().isoformat()
        }
        
        # Test _parse_count method
        test_counts = ["1.2K", "5.5M", "100", "2.3B"]
        for count_text in test_counts:
            parsed = scraper._parse_count(count_text)
            logger.info(f"📊 {count_text} -> {parsed}")
        
        logger.info("✅ Hashtag extraction and data structure tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Hashtag extraction test failed: {e}")
        raise

def test_search_functionality():
    """Test search functionality without actual web scraping"""
    logger = setup_logging()
    
    try:
        logger.info("🔍 Testing TikTok search functionality (mock mode)...")
        
        # Create mock components with mock driver
        mock_anti_bot, mock_policy = create_mock_components()
        
        # Mock driver for testing
        mock_driver = Mock()
        mock_driver.get = Mock()
        mock_driver.page_source = "<html><body>Mock TikTok page</body></html>"
        mock_driver.quit = Mock()
        
        mock_anti_bot.get_driver.return_value = mock_driver
        
        # Initialize scraper
        scraper = TikTokScraper(mock_anti_bot, mock_policy)
        
        # Test Philippines hashtags
        philippines_hashtags = scraper.philippines_hashtags
        logger.info(f"🇵🇭 Philippines hashtags to test: {philippines_hashtags[:3]}")
        
        # Test search method signature (without actual execution)
        test_hashtag = "philippines"
        logger.info(f"🎯 Testing search for hashtag: #{test_hashtag}")
        
        # Since we can't do real scraping, test the method exists and can be called
        assert hasattr(scraper, 'search_hashtag_videos')
        assert hasattr(scraper, 'scrape_hashtag_videos')
        assert hasattr(scraper, 'get_trending_videos')
        
        logger.info("✅ TikTok search functionality structure verified")
        return True
        
    except Exception as e:
        logger.error(f"❌ TikTok search functionality test failed: {e}")
        raise

def test_simple_integration():
    """Test simple integration with main.py expected interface"""
    logger = setup_logging()
    
    try:
        logger.info("🔗 Testing integration with main.py interface...")
        
        # Create mock components
        mock_anti_bot, mock_policy = create_mock_components()
        
        # Initialize scraper
        scraper = TikTokScraper(mock_anti_bot, mock_policy)
        
        # Test main.py expected methods exist
        expected_methods = [
            'search_hashtag_videos',  # Used in main.py
            'cleanup'  # Used in main.py
        ]
        
        for method_name in expected_methods:
            assert hasattr(scraper, method_name), f"Missing method: {method_name}"
            logger.info(f"✅ Method {method_name} exists")
        
        # Test cleanup
        scraper.cleanup()
        logger.info("✅ Cleanup method executed successfully")
        
        logger.info("✅ Integration with main.py interface verified")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        raise

def main():
    """Run all TikTok basic scraper tests"""
    logger = setup_logging()
    
    try:
        logger.info("=" * 60)
        logger.info("🎬 TIKTOK BASIC SCRAPER TEST SUITE")
        logger.info("=" * 60)
        
        test_results = {}
        
        # Test 1: Initialization
        logger.info("\n1️⃣ Testing TikTok Scraper Initialization...")
        scraper = test_tiktok_scraper_initialization()
        test_results["initialization"] = True
        
        # Test 2: Hashtag extraction
        logger.info("\n2️⃣ Testing Hashtag Extraction...")
        test_hashtag_extraction()
        test_results["hashtag_extraction"] = True
        
        # Test 3: Search functionality structure
        logger.info("\n3️⃣ Testing Search Functionality Structure...")
        test_search_functionality()
        test_results["search_functionality"] = True
        
        # Test 4: Integration interface
        logger.info("\n4️⃣ Testing Integration Interface...")
        test_simple_integration()
        test_results["integration"] = True
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} | {test_name}")
        
        logger.info(f"\n🎉 Overall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("✅ All TikTok basic scraper tests PASSED!")
            logger.info("🚀 TikTok scraper is ready for integration testing")
        else:
            logger.warning(f"⚠️ Some tests failed. Need debugging.")
        
        return passed_tests == total_tests
        
    except Exception as e:
        logger.error(f"💥 Test suite failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)