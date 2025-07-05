#!/usr/bin/env python3
"""
Live test for Google Trends scraper without database
"""

import sys
import os
import logging
from unittest.mock import Mock

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def setup_test_logging():
    """Setup logging for test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger('google_trends_test')

def test_google_trends_live():
    """Test Google Trends scraper with real data"""
    logger = setup_test_logging()
    
    logger.info("🧪 Testing Google Trends scraper with real data...")
    
    try:
        from scrapers.google_trends import GoogleTrendsScraper
        from utils.anti_bot_system import AntiBotSystem
        from utils.ethical_scraping import ScrapingPolicy
        
        # Create mock instances for dependencies
        mock_anti_bot = Mock(spec=AntiBotSystem)
        mock_anti_bot.simulate_human_behavior = Mock()
        
        mock_policy = Mock(spec=ScrapingPolicy)
        mock_policy.wait_for_rate_limit = Mock()
        
        # Initialize scraper
        scraper = GoogleTrendsScraper(mock_anti_bot, mock_policy)
        
        # Test with simple keywords (one at a time for reliability)
        test_keywords = ["covid"]
        logger.info(f"Testing with keywords: {test_keywords}")
        
        # Get trends data
        trends_data = scraper.get_trends(test_keywords)
        
        if trends_data:
            logger.info(f"✅ Successfully collected trends data!")
            logger.info(f"📊 Keywords: {trends_data.get('keywords', [])}")
            
            # Check data structure
            if 'interest_over_time' in trends_data:
                logger.info(f"📈 Interest over time data: Available")
            
            if 'related_queries' in trends_data:
                logger.info(f"🔗 Related queries data: Available")
                
            logger.info(f"🕒 Collection timestamp: {trends_data.get('collected_at', 'Not set')}")
            
            return True
        else:
            logger.warning("⚠️ No trends data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Google Trends test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger = setup_test_logging()
    
    logger.info("=" * 50)
    logger.info("🔍 GOOGLE TRENDS LIVE TEST")
    logger.info("=" * 50)
    
    success = test_google_trends_live()
    
    if success:
        logger.info("🎉 Google Trends scraper is working correctly!")
    else:
        logger.error("❌ Google Trends scraper has issues")
    
    sys.exit(0 if success else 1)