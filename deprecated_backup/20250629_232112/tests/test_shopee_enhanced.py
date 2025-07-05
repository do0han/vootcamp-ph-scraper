#!/usr/bin/env python3
"""
Test script for enhanced Shopee Flash Deals and Trending Products functionality
"""
import sys
import time
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.shopee import ShopeeScraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_flash_deals():
    """Test the flash deals functionality"""
    scraper = None
    try:
        print("🔥 Testing Flash Deals Collection...")
        scraper = ShopeeScraper(headless=True)
        
        flash_products = scraper.get_flash_deal_products(limit=10)
        
        print(f"\n📊 Flash Deals Results:")
        print(f"   Products found: {len(flash_products)}")
        
        if flash_products:
            print(f"   Sample product:")
            sample = flash_products[0]
            print(f"     - Name: {sample.get('product_name', 'N/A')}")
            print(f"     - Price: {sample.get('price', 'N/A')}")
            print(f"     - Type: {sample.get('product_type', 'N/A')}")
            print(f"     - Keyword: {sample.get('search_keyword', 'N/A')}")
        
        return len(flash_products)
        
    except Exception as e:
        print(f"❌ Error in flash deals test: {e}")
        return 0
    finally:
        if scraper:
            scraper.close()

def test_trending_products():
    """Test the trending products functionality"""
    scraper = None
    try:
        print("\n📈 Testing Trending Products Collection...")
        scraper = ShopeeScraper(headless=True)
        
        trending_products = scraper.get_trending_products_by_category(limit=10)
        
        print(f"\n📊 Trending Products Results:")
        print(f"   Products found: {len(trending_products)}")
        
        if trending_products:
            print(f"   Sample product:")
            sample = trending_products[0]
            print(f"     - Name: {sample.get('product_name', 'N/A')}")
            print(f"     - Price: {sample.get('price', 'N/A')}")
            print(f"     - Category: {sample.get('category', 'N/A')}")
            print(f"     - Type: {sample.get('product_type', 'N/A')}")
        
        return len(trending_products)
        
    except Exception as e:
        print(f"❌ Error in trending products test: {e}")
        return 0
    finally:
        if scraper:
            scraper.close()

def test_comprehensive_scraping():
    """Test the comprehensive scraping functionality"""
    scraper = None
    try:
        print("\n🌟 Testing Comprehensive Data Collection...")
        scraper = ShopeeScraper(headless=True)
        
        results = scraper.scrape_comprehensive_data(
            include_flash_deals=True,
            include_trending=True,
            limit_per_type=5
        )
        
        print(f"\n📊 Comprehensive Results:")
        print(f"   Flash deals: {len(results['flash_deals'])}")
        print(f"   Trending products: {len(results['trending_products'])}")
        print(f"   Search results: {len(results['search_results'])}")
        print(f"   Total products: {results['total_products']}")
        
        # Save results to file for inspection
        with open('shopee_comprehensive_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"   Results saved to: shopee_comprehensive_results.json")
        
        return results['total_products']
        
    except Exception as e:
        print(f"❌ Error in comprehensive test: {e}")
        return 0
    finally:
        if scraper:
            scraper.close()

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Shopee Functionality Tests...")
    print("=" * 60)
    
    total_products = 0
    
    # Test 1: Flash Deals
    flash_count = test_flash_deals()
    total_products += flash_count
    time.sleep(5)  # Brief pause between tests
    
    # Test 2: Trending Products  
    trending_count = test_trending_products()
    total_products += trending_count
    time.sleep(5)  # Brief pause between tests
    
    # Test 3: Comprehensive Scraping
    comprehensive_count = test_comprehensive_scraping()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 Test Summary:")
    print(f"   Flash deals collected: {flash_count}")
    print(f"   Trending products collected: {trending_count}")
    print(f"   Comprehensive test total: {comprehensive_count}")
    print(f"   Grand total products: {total_products + comprehensive_count}")
    
    if total_products > 0:
        print("✅ Enhanced Shopee functionality is working!")
    else:
        print("⚠️ No products collected - check implementation")

if __name__ == "__main__":
    main() 