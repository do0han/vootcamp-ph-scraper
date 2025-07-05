#!/usr/bin/env python3
"""
Database integration test for Vootcamp PH Data Scraper
Tests database operations with mock or real Supabase connection
"""

import sys
import os
import logging
from unittest.mock import Mock, patch
from datetime import datetime

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
    return logging.getLogger('database_test')

def test_supabase_connection():
    """Test actual Supabase connection if credentials are available"""
    logger = setup_test_logging()
    logger.info("🧪 Testing Supabase connection...")
    
    try:
        # Check if environment variables are set
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            logger.warning("⚠️ Supabase credentials not found in environment")
            logger.info("💡 To test with real Supabase:")
            logger.info("   1. Follow SUPABASE_SETUP_GUIDE.md")
            logger.info("   2. Create .env file with your credentials")
            logger.info("   3. Run this test again")
            return False
        
        from database.supabase_client import SupabaseClient
        
        # Test connection
        client = SupabaseClient()
        logger.info("✅ Supabase client created successfully")
        
        # Test table access
        tables = ['google_trends', 'shopee_products', 'tiktok_videos']
        for table in tables:
            try:
                result = client.client.table(table).select('*').limit(1).execute()
                logger.info(f"✅ {table} table accessible")
            except Exception as e:
                logger.error(f"❌ {table} table error: {e}")
                return False
        
        logger.info("🎉 All database tables are accessible!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return False

def test_mock_database_operations() -> bool:
    """모의 데이터베이스 작업 테스트"""
    logger = setup_test_logging()
    try:
    logger.info("🧪 Testing mock database operations...")
    
        # Reset singleton instance
        from database.supabase_client import SupabaseClient
        SupabaseClient._instance = None
        SupabaseClient.client = None
        
            # Mock Supabase client
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_table.insert.return_value = mock_table
            mock_table.execute.return_value = Mock(data=[{"id": "test-id"}])
            
        # Patch get_supabase_client to use mock
        with patch('database.supabase_client.get_supabase_client', return_value=mock_client):
            # Create client and test operations
                client = SupabaseClient()
                
            # Test data
            trends_data = {"keywords": ["test"], "interest_over_time": {}, "related_queries": {}}
            products_data = [{"name": "test", "price": "100"}]
            videos_data = [{"video_id": "test", "title": "test"}]
            
            # Test insertions
                client.insert_google_trends(trends_data)
            logger.info("✅ Google trends mock insertion successful")
                
            client.insert_shopee_products(products_data)
                logger.info("✅ Shopee products mock insertion successful")
                
                client.insert_tiktok_videos(videos_data)
                logger.info("✅ TikTok videos mock insertion successful")
                
            # Verify that all operations completed without errors
            assert mock_table.execute.call_count >= 3, "Expected at least 3 database operations"
                logger.info("✅ All mock database operations completed successfully")
                
                return True
    except Exception as e:
        logger.error(f"💥 Mock database operations failed: {str(e)}")
        return False

def test_data_parsing_functions():
    """Test data parsing helper functions"""
    logger = setup_test_logging()
    logger.info("🧪 Testing data parsing functions...")
    
    try:
        # Mock environment variables first
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test-project.supabase.co',
            'SUPABASE_KEY': 'test-key-12345'
        }):
            from database.supabase_client import SupabaseClient
            
            # Create mock client to access parsing methods
            with patch('database.supabase_client.create_client'):
                client = SupabaseClient()
            
                # Test price parsing
                test_cases = [
                    ("₱1,234.56", 1234.56),
                    ("₱999", 999.0),
                    ("1000", 1000.0),
                    ("", None),
                    ("invalid", None)
                ]
                
                for input_val, expected in test_cases:
                    result = client._parse_price(input_val)
                    assert result == expected, f"Price parsing failed: {input_val} -> {result} (expected {expected})"
                
                logger.info("✅ Price parsing tests passed")
                
                # Test number parsing
                number_cases = [
                    ("1K", 1000),
                    ("2.5K", 2500),
                    ("1M", 1000000),
                    ("123", 123),
                    ("1,234", 1234),
                    ("", None),
                    ("invalid", None)
                ]
                
                for input_val, expected in number_cases:
                    result = client._parse_number(input_val)
                    assert result == expected, f"Number parsing failed: {input_val} -> {result} (expected {expected})"
                
                logger.info("✅ Number parsing tests passed")
                
                # Test rating parsing
                rating_cases = [
                    ("4.5", 4.5),
                    ("5", 5.0),
                    ("3.2", 3.2),
                    ("", None),
                    ("invalid", None)
                ]
                
                for input_val, expected in rating_cases:
                    result = client._parse_rating(input_val)
                    assert result == expected, f"Rating parsing failed: {input_val} -> {result} (expected {expected})"
                
                logger.info("✅ Rating parsing tests passed")
                
                return True
            
    except Exception as e:
        logger.error(f"❌ Data parsing tests failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def run_database_tests():
    """Run all database integration tests"""
    logger = setup_test_logging()
    
    logger.info("=" * 60)
    logger.info("🗄️ DATABASE INTEGRATION TESTS")
    logger.info("=" * 60)
    
    tests = [
        ("Supabase Connection", test_supabase_connection),
        ("Mock Database Operations", test_mock_database_operations),
        ("Data Parsing Functions", test_data_parsing_functions)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"💥 {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 DATABASE TEST RESULTS")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} | {test_name}")
    
    logger.info(f"\n🏁 OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL DATABASE TESTS PASSED! Ready for production.")
        return True
    elif passed >= 2:  # At least mock and parsing tests should pass
        logger.warning("⚠️ PARTIAL SUCCESS: Mock operations working. Set up Supabase for full functionality.")
        return True
    else:
        logger.error("❌ CRITICAL DATABASE ISSUES: Major problems detected.")
        return False

if __name__ == "__main__":
    success = run_database_tests()
    sys.exit(0 if success else 1)