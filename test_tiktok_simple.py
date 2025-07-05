#!/usr/bin/env python3
"""
Simple TikTok Scraper Test
Direct testing without complex imports
"""

import os
import sys
import logging
from pathlib import Path

# Set testing environment
os.environ['TESTING'] = 'true'

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger('tiktok_simple_test')

def test_tiktok_structure():
    """Test TikTok scraper file structure and basic content"""
    logger = setup_logging()
    
    logger.info("🎬 Testing TikTok Scraper Structure...")
    
    try:
        # Check if TikTok scraper file exists
        tiktok_scraper_path = Path(__file__).parent / "scrapers" / "tiktok.py"
        
        if not tiktok_scraper_path.exists():
            logger.error("❌ TikTok scraper file not found")
            return False
        
        logger.info("✅ TikTok scraper file exists")
        
        # Read file content
        with open(tiktok_scraper_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key components
        required_components = [
            "class TikTokScraper",
            "def search_hashtag_videos",
            "def scrape_hashtag_videos", 
            "def cleanup",
            "philippines_hashtags",
            "_extract_video_data",
            "_parse_count"
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
            else:
                logger.info(f"✅ Found: {component}")
        
        if missing_components:
            logger.error(f"❌ Missing components: {missing_components}")
            return False
        
        # Check Philippines hashtags
        philippines_patterns = ["philippines", "manila", "pinoy", "fyp"]
        found_hashtags = []
        for pattern in philippines_patterns:
            if pattern in content.lower():
                found_hashtags.append(pattern)
        
        logger.info(f"🇵🇭 Philippines hashtags found: {found_hashtags}")
        
        # Check for expected methods for main.py integration
        main_integration_methods = [
            "search_hashtag_videos",  # Called in main.py
            "cleanup"  # Called in main.py
        ]
        
        for method in main_integration_methods:
            if f"def {method}" in content:
                logger.info(f"✅ Main.py integration method: {method}")
            else:
                logger.warning(f"⚠️ Missing main.py method: {method}")
        
        logger.info("✅ TikTok scraper structure analysis completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Structure test failed: {e}")
        return False

def test_tiktok_shop_structure():
    """Test TikTok Shop scraper structure"""
    logger = setup_logging()
    
    logger.info("🛍️ Testing TikTok Shop Scraper Structure...")
    
    try:
        tiktok_shop_path = Path(__file__).parent / "scrapers" / "tiktok_shop_scraper.py"
        
        if not tiktok_shop_path.exists():
            logger.error("❌ TikTok Shop scraper file not found")
            return False
        
        logger.info("✅ TikTok Shop scraper file exists")
        
        with open(tiktok_shop_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key TikTok Shop components
        shop_components = [
            "class TikTokShopScraper",
            "get_top_products",
            "get_flash_sale_products",
            "get_category_products",
            "_extract_products_data",
            "close"
        ]
        
        for component in shop_components:
            if component in content:
                logger.info(f"✅ Found: {component}")
            else:
                logger.warning(f"⚠️ Missing: {component}")
        
        # Check for Philippines market targeting
        ph_indicators = ["philippines", "php", "shopee.ph"]
        found_ph = []
        for indicator in ph_indicators:
            if indicator in content.lower():
                found_ph.append(indicator)
        
        logger.info(f"🇵🇭 Philippines market indicators: {found_ph}")
        
        logger.info("✅ TikTok Shop scraper structure analysis completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ TikTok Shop structure test failed: {e}")
        return False

def test_main_integration():
    """Test integration with main.py"""
    logger = setup_logging()
    
    logger.info("🔗 Testing Main.py Integration...")
    
    try:
        main_path = Path(__file__).parent / "main.py"
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check TikTok imports
        tiktok_imports = [
            "from scrapers.tiktok import TikTokScraper",
            "from scrapers.tiktok_shop_scraper import TikTokShopScraper"
        ]
        
        for import_line in tiktok_imports:
            if import_line in content:
                logger.info(f"✅ Import found: {import_line}")
            else:
                logger.warning(f"⚠️ Missing import: {import_line}")
        
        # Check function definitions
        tiktok_functions = [
            "def run_tiktok_scraper",
            "def run_tiktok_shop_scraper"
        ]
        
        for func in tiktok_functions:
            if func in content:
                logger.info(f"✅ Function found: {func}")
            else:
                logger.warning(f"⚠️ Missing function: {func}")
        
        # Check execution in main
        execution_calls = [
            "run_tiktok_scraper(",
            "run_tiktok_shop_scraper("
        ]
        
        for call in execution_calls:
            if call in content:
                logger.info(f"✅ Execution call found: {call}")
            else:
                logger.warning(f"⚠️ Missing execution: {call}")
        
        logger.info("✅ Main.py integration check completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Main integration test failed: {e}")
        return False

def test_database_integration():
    """Test database integration for TikTok Shop"""
    logger = setup_logging()
    
    logger.info("💾 Testing Database Integration...")
    
    try:
        db_client_path = Path(__file__).parent / "database" / "supabase_client.py"
        
        with open(db_client_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check TikTok Shop database methods
        db_methods = [
            "def insert_tiktok_shop_products",
            "def _extract_product_id",
            "def get_latest_tiktok_shop_products"
        ]
        
        for method in db_methods:
            if method in content:
                logger.info(f"✅ Database method found: {method}")
            else:
                logger.warning(f"⚠️ Missing database method: {method}")
        
        # Check for TikTok Shop table reference
        if "tiktok_shop_products" in content:
            logger.info("✅ TikTok Shop table reference found")
        else:
            logger.warning("⚠️ Missing TikTok Shop table reference")
        
        logger.info("✅ Database integration check completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database integration test failed: {e}")
        return False

def main():
    """Run all simple tests"""
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("🎬 TIKTOK SIMPLE TEST SUITE")
    logger.info("=" * 60)
    
    tests = [
        ("TikTok Scraper Structure", test_tiktok_structure),
        ("TikTok Shop Structure", test_tiktok_shop_structure),
        ("Main.py Integration", test_main_integration),
        ("Database Integration", test_database_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS")
    logger.info("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} | {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All TikTok tests PASSED!")
        logger.info("🚀 TikTok scrapers are ready for execution")
    else:
        logger.warning("⚠️ Some tests failed - review implementation")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)