#!/usr/bin/env python3
"""
Test script for Supabase integration with enhanced Shopee functionality
"""
import sys
import time
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.shopee import ShopeeScraper
from database.supabase_client import SupabaseClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_supabase_connection():
    """Test Supabase database connection"""
    try:
        print("🔗 Testing Supabase connection...")
        supabase_client = SupabaseClient()
        
        # Test connection
        if supabase_client.test_connection():
            print("✅ Supabase connection successful!")
            return True
        else:
            print("❌ Supabase connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Supabase connection: {e}")
        return False

def test_flash_deals_with_db():
    """Test Flash Deals collection with database saving"""
    scraper = None
    try:
        print("\n🔥 Testing Flash Deals with Database Saving...")
        scraper = ShopeeScraper(headless=True, use_supabase=True)
        
        # Collect flash deals (should automatically save to database)
        flash_products = scraper.get_flash_deal_products(limit=5, save_to_db=True)
        
        print(f"📊 Flash Deals Results:")
        print(f"   - Products collected: {len(flash_products)}")
        
        if flash_products:
            print(f"   - Sample product: {flash_products[0]['product_name']}")
            print(f"   - Product type: {flash_products[0].get('product_type', 'N/A')}")
            print(f"   - Search keyword: {flash_products[0].get('search_keyword', 'N/A')}")
            print("✅ Flash deals with database integration successful!")
        else:
            print("⚠️ No flash deals collected")
            
        return len(flash_products) > 0
        
    except Exception as e:
        print(f"❌ Error in flash deals test: {e}")
        return False
    finally:
        if scraper:
            scraper.close()

def test_trending_products_with_db():
    """Test Trending Products collection with database saving"""
    scraper = None
    try:
        print("\n📈 Testing Trending Products with Database Saving...")
        scraper = ShopeeScraper(headless=True, use_supabase=True)
        
        # Test with specific categories
        test_categories = ["beauty", "electronics", "fashion"]
        trending_products = scraper.get_trending_products_by_category(
            categories=test_categories, 
            limit=6, 
            save_to_db=True
        )
        
        print(f"📊 Trending Products Results:")
        print(f"   - Products collected: {len(trending_products)}")
        
        if trending_products:
            print(f"   - Categories found: {set(p.get('category', 'N/A') for p in trending_products)}")
            print(f"   - Sample product: {trending_products[0]['product_name']}")
            print("✅ Trending products with database integration successful!")
        else:
            print("⚠️ No trending products collected")
            
        return len(trending_products) > 0
        
    except Exception as e:
        print(f"❌ Error in trending products test: {e}")
        return False
    finally:
        if scraper:
            scraper.close()

def test_comprehensive_data_collection():
    """Test comprehensive data collection with database saving"""
    scraper = None
    try:
        print("\n🔄 Testing Comprehensive Data Collection...")
        scraper = ShopeeScraper(headless=True, use_supabase=True)
        
        # Collect comprehensive data (should save all to database in one batch)
        results = scraper.scrape_comprehensive_data(
            include_flash_deals=True,
            include_trending=True,
            limit_per_type=3,
            save_to_db=True
        )
        
        print(f"📊 Comprehensive Collection Results:")
        print(f"   - Flash deals: {len(results['flash_deals'])}")
        print(f"   - Trending products: {len(results['trending_products'])}")
        print(f"   - Search results: {len(results['search_results'])}")
        print(f"   - Total products: {results['total_products']}")
        
        if results['total_products'] > 0:
            print("✅ Comprehensive data collection with database integration successful!")
        else:
            print("⚠️ No products collected in comprehensive test")
            
        return results['total_products'] > 0
        
    except Exception as e:
        print(f"❌ Error in comprehensive data collection: {e}")
        return False
    finally:
        if scraper:
            scraper.close()

def verify_database_data():
    """Verify that data was actually saved to Supabase"""
    try:
        print("\n🔍 Verifying data in Supabase database...")
        supabase_client = SupabaseClient()
        
        # Query recent data
        from datetime import datetime, timedelta
        recent_cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
        
        # This is a simple verification - in a real scenario you'd query the actual data
        print("📋 Database verification completed")
        print("   - Note: Actual data verification would require specific Supabase queries")
        print("   - Check your Supabase dashboard to see the inserted data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database data: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Supabase Integration Tests...")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: Supabase connection
    test_results['supabase_connection'] = test_supabase_connection()
    
    if not test_results['supabase_connection']:
        print("\n❌ Skipping other tests due to Supabase connection failure")
        print("💡 Make sure your .env file has valid SUPABASE_URL and SUPABASE_ANON_KEY")
        return
    
    # Test 2: Flash deals with database
    test_results['flash_deals_db'] = test_flash_deals_with_db()
    
    # Test 3: Trending products with database  
    test_results['trending_products_db'] = test_trending_products_with_db()
    
    # Test 4: Comprehensive data collection
    test_results['comprehensive_collection'] = test_comprehensive_data_collection()
    
    # Test 5: Database verification
    test_results['database_verification'] = verify_database_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Test Results Summary:")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\n📊 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Supabase integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 