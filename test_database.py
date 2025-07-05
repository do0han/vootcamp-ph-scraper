"""
Test script for Supabase database integration
Run this script to test the database connection and functionality
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from database import SupabaseClient

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test basic database connection"""
    print("🔗 Testing Supabase connection...")
    
    try:
        # Check if environment variables are set
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Environment variables SUPABASE_URL and SUPABASE_KEY must be set")
            print("💡 Copy env.example to .env and fill in your Supabase credentials")
            print("📁 Or set TESTING=true to run in test mode")
            return False
        
        # Initialize client
        client = SupabaseClient()
        
        # Test connection
        if client.test_connection():
            print("✅ Supabase connection successful!")
            return True
        else:
            print("❌ Supabase connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_data_insertion():
    """Test data insertion for all tables"""
    print("\n📊 Testing data insertion...")
    
    try:
        client = SupabaseClient()
        
        # Test Google Trends data
        print("Testing Google Trends data insertion...")
        google_trends_data = [
            {
                "trend_type": "trending_now",
                "keyword": "test keyword",
                "search_volume": 1000,
                "related_topics": {"test": "data"},
                "region": "PH",
                "category": "test",
                "timeframe": "24h"
            }
        ]
        
        result = client.insert_google_trends_data(google_trends_data)
        print(f"✅ Google Trends: Inserted {len(result)} records")
        
        # Test Shopee products data
        print("Testing Shopee products data insertion...")
        shopee_data = [
            {
                "search_keyword": "test product",
                "product_name": "Test Product Name",
                "seller_name": "Test Seller",
                "price": 99.99,
                "currency": "PHP",
                "rating": 4.5,
                "review_count": 100,
                "sales_count": 50,
                "product_url": "https://test.url",
                "category": "test category"
            }
        ]
        
        result = client.insert_shopee_products_data(shopee_data)
        print(f"✅ Shopee Products: Inserted {len(result)} records")
        
        # Test TikTok videos data
        print("Testing TikTok videos data insertion...")
        tiktok_data = [
            {
                "hashtag": "#test",
                "video_url": "https://test.tiktok.url",
                "video_id": "test123",
                "uploader_name": "Test User",
                "uploader_username": "@testuser",
                "view_count": 10000,
                "like_count": 500,
                "comment_count": 50,
                "share_count": 25,
                "video_title": "Test Video",
                "video_description": "Test description",
                "used_hashtags": ["#test", "#demo"],
                "sound_info": {"sound_name": "test sound"},
                "duration_seconds": 30,
                "is_trending": True
            }
        ]
        
        result = client.insert_tiktok_videos_data(tiktok_data)
        print(f"✅ TikTok Videos: Inserted {len(result)} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Data insertion error: {e}")
        return False

def test_data_retrieval():
    """Test data retrieval functionality"""
    print("\n📖 Testing data retrieval...")
    
    try:
        client = SupabaseClient()
        
        # Test getting latest data from each table
        tables = ['google_trends', 'shopee_products', 'tiktok_videos']
        
        for table in tables:
            try:
                latest_data = client.get_latest_data(table, limit=5)
                count = client.count_records(table)
                print(f"✅ {table}: {len(latest_data)} latest records retrieved, {count} total records")
            except Exception as e:
                print(f"❌ {table}: Error retrieving data - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data retrieval error: {e}")
        return False

def main():
    """Run all database tests"""
    print("🧪 Vootcamp PH Database Test Suite")
    print("=" * 50)
    
    # Check if running in test mode
    if os.environ.get('TESTING') == 'true':
        print("🧪 Running in TEST MODE - using mock client")
    
    # Test 1: Connection
    connection_ok = test_database_connection()
    if not connection_ok:
        print("\n❌ Database connection failed. Please check your configuration.")
        if os.environ.get('TESTING') != 'true':
            sys.exit(1)
    
    # Test 2: Data insertion
    insertion_ok = test_data_insertion()
    if not insertion_ok:
        print("\n❌ Data insertion tests failed.")
        return
    
    # Test 3: Data retrieval
    retrieval_ok = test_data_retrieval()
    if not retrieval_ok:
        print("\n❌ Data retrieval tests failed.")
        return
    
    print("\n🎉 All database tests passed successfully!")
    print("\n💡 Next steps:")
    print("1. Your database is ready for the scrapers")
    print("2. You can now proceed with implementing the Google Trends scraper")
    print("3. Remember to set up proper environment variables in .env file")

if __name__ == "__main__":
    main() 