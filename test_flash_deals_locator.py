#!/usr/bin/env python3
"""
Test script for Flash Deals and Trending Products section locator methods
"""
import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.shopee import ShopeeScraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_section_locators():
    """Test the dynamic section locator methods"""
    scraper = None
    try:
        print("🚀 Testing Shopee Section Locators...")
        
        # Initialize scraper with non-headless mode for better debugging
        scraper = ShopeeScraper(headless=False)
        
        print("📍 Testing locate_dynamic_sections() method...")
        sections = scraper.locate_dynamic_sections()
        
        print(f"\n📊 Results:")
        print(f"   Flash Deals section: {'✅ Found' if sections.get('flash_deals') else '❌ Not found'}")
        print(f"   Trending Products section: {'✅ Found' if sections.get('trending_products') else '❌ Not found'}")
        
        # If sections found, get some basic info
        if sections.get('flash_deals'):
            flash_section = sections['flash_deals']
            print(f"   Flash Deals element tag: {flash_section.tag_name}")
            print(f"   Flash Deals class: {flash_section.get_attribute('class')}")
            
        if sections.get('trending_products'):
            trending_section = sections['trending_products']
            print(f"   Trending Products element tag: {trending_section.tag_name}")
            print(f"   Trending Products class: {trending_section.get_attribute('class')}")
        
        # Wait a bit to observe the page
        print("\n⏳ Waiting 10 seconds for observation...")
        time.sleep(10)
        
        print("✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.exception("Full error details:")
        
    finally:
        if scraper:
            scraper.close()
            print("🔒 Browser closed")

if __name__ == "__main__":
    test_section_locators() 