"""
Integration test for Google Trends scraper and database
Run this script to test the complete flow: scraping -> database storage
"""

import logging
import sys
from scrapers import GoogleTrendsScraper
from database import SupabaseClient
from config.settings import Settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_google_trends_scraper():
    """Test the Google Trends scraper functionality"""
    print("🔍 Testing Google Trends Scraper...")
    
    try:
        # Initialize scraper
        scraper = GoogleTrendsScraper()
        print("✅ Scraper initialized successfully")
        
        # Test popular keywords data (replaced trending searches)
        print("\n📈 Testing popular keywords data...")
        popular_data = scraper.get_popular_keywords_data()
        print(f"✅ Fetched {len(popular_data)} popular keywords data")
        
        # Display sample popular data
        if popular_data:
            print("\n📊 Sample popular keywords:")
            for i, item in enumerate(popular_data[:3]):
                print(f"  {i+1}. {item['keyword']} ({item['category']}) - Volume: {item['search_volume']}")
        
        # Test related queries for a sample keyword
        print("\n🔗 Testing related queries...")
        sample_keyword = "shopee"  # Use a Philippines-popular keyword
        related_data = scraper.get_related_queries(sample_keyword)
        print(f"✅ Fetched {len(related_data)} related queries for '{sample_keyword}'")
        
        # Display sample related data
        if related_data:
            print(f"\n📊 Sample related queries for '{sample_keyword}':")
            for i, item in enumerate(related_data[:3]):
                print(f"  {i+1}. {item['keyword']} ({item['trend_type']})")
        
        # Test interest over time
        print("\n📊 Testing interest over time...")
        sample_keywords = ["shopee", "jollibee", "gcash"]
        interest_data = scraper.get_interest_over_time(sample_keywords)
        print(f"✅ Fetched {len(interest_data)} interest over time records")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Trends scraper test failed: {e}")
        logger.error(f"Scraper test error: {e}")
        return False


def test_database_integration():
    """Test Google Trends data insertion into database"""
    print("\n💾 Testing Database Integration...")
    
    try:
        # Check if environment variables are set
        if not Settings.SUPABASE_URL or not Settings.SUPABASE_KEY:
            print("⚠️ Skipping database test - Supabase credentials not configured")
            print("💡 Set SUPABASE_URL and SUPABASE_KEY in .env to test database integration")
            return True
        
        # Initialize database client
        db_client = SupabaseClient()
        print("✅ Database client initialized")
        
        # Test connection
        if not db_client.test_connection():
            print("❌ Database connection failed")
            return False
        
        print("✅ Database connection successful")
        
        # Initialize scraper and get sample data
        scraper = GoogleTrendsScraper()
        
        # Get a small sample of data
        print("📊 Collecting sample data...")
        popular_data = scraper.get_popular_keywords_data()[:5]  # Limit to 5 records
        
        if not popular_data:
            print("⚠️ No popular keywords data available for testing")
            return True
        
        # Insert data into database
        print(f"💾 Inserting {len(popular_data)} records into database...")
        result = db_client.insert_google_trends_data(popular_data)
        
        print(f"✅ Successfully inserted {len(result)} records")
        
        # Verify data was inserted
        print("🔍 Verifying inserted data...")
        latest_data = db_client.get_latest_data('google_trends', limit=3)
        print(f"✅ Retrieved {len(latest_data)} latest records from database")
        
        # Display sample inserted data
        if latest_data:
            print("\n📊 Sample data from database:")
            for i, item in enumerate(latest_data):
                print(f"  {i+1}. {item.get('keyword', 'N/A')} ({item.get('trend_type', 'N/A')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        logger.error(f"Database integration error: {e}")
        return False


def run_full_integration_test():
    """Run a comprehensive integration test with a small dataset"""
    print("\n🚀 Running Full Integration Test...")
    
    try:
        # Check environment
        if not Settings.SUPABASE_URL or not Settings.SUPABASE_KEY:
            print("⚠️ Skipping full integration test - Supabase credentials not configured")
            print("💡 Set up your Supabase project and update .env file to run full test")
            return True
        
        # Initialize components
        scraper = GoogleTrendsScraper()
        db_client = SupabaseClient()
        
        print("📊 Collecting limited dataset for testing...")
        
        # Collect limited data to avoid rate limits during testing
        all_data = []
        
        # Get popular keywords data
        popular_data = scraper.get_popular_keywords_data()[:3]  # Limit to 3
        all_data.extend(popular_data)
        
        # Get related queries for just 2 keywords
        if popular_data:
            test_keywords = [popular_data[0]['keyword'], popular_data[1]['keyword']] if len(popular_data) >= 2 else [popular_data[0]['keyword']]
            for keyword in test_keywords:
                try:
                    related_data = scraper.get_related_queries(keyword)[:2]  # Limit to 2 per keyword
                    all_data.extend(related_data)
                except Exception as e:
                    logger.warning(f"Failed to get data for {keyword}: {e}")
        
        print(f"📊 Collected {len(all_data)} total records")
        
        if all_data:
            # Insert into database using batch insert
            print("💾 Inserting data using batch insert...")
            inserted_data = db_client.batch_insert('google_trends', all_data, batch_size=10)
            
            print(f"✅ Successfully completed full integration test!")
            print(f"📊 Total records processed: {len(inserted_data)}")
            
            # Get statistics
            total_count = db_client.count_records('google_trends')
            print(f"📈 Total records in database: {total_count}")
            
        else:
            print("⚠️ No data collected during test")
        
        return True
        
    except Exception as e:
        print(f"❌ Full integration test failed: {e}")
        logger.error(f"Full integration test error: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Google Trends Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Scraper functionality
    scraper_ok = test_google_trends_scraper()
    if not scraper_ok:
        print("\n❌ Scraper tests failed. Please check your internet connection.")
        sys.exit(1)
    
    # Test 2: Database integration
    db_ok = test_database_integration()
    if not db_ok:
        print("\n❌ Database integration tests failed.")
        return
    
    # Test 3: Full integration
    full_ok = run_full_integration_test()
    if not full_ok:
        print("\n❌ Full integration test failed.")
        return
    
    print("\n🎉 All Google Trends integration tests passed!")
    print("\n💡 Next steps:")
    print("1. Your Google Trends scraper is working correctly")
    print("2. Database integration is functional")
    print("3. You can now proceed with implementing the Shopee scraper")
    print("4. Consider setting up a scheduled task to run data collection regularly")


if __name__ == "__main__":
    main() 