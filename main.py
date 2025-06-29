"""
Main entry point for Vootcamp PH Data Scraper
"""

import logging
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, Any, List

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

from config.settings import Settings

# Import database client
from database.supabase_client import SupabaseClient

# Import scrapers
from scrapers.google_trends import GoogleTrendsScraper
from scrapers.shopee import ShopeeScraper
from scrapers.lazada_scraper import LazadaScraper  # Real data alternative
from scrapers.tiktok import TikTokScraper

# Import utilities
from utils.anti_bot_system import AntiBotSystem
from utils.ethical_scraping import ScrapingPolicy


def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    import os
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, Settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/scraper_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('vootcamp_scraper')
    return logger


def initialize_components(logger):
    """Initialize core components (database, anti-bot, policy)"""
    try:
        # Initialize database client
        logger.info("Initializing Supabase database client...")
        database_client = SupabaseClient()
        logger.info("✅ Database client initialized successfully")
        
        # Initialize anti-bot system
        logger.info("Initializing anti-bot protection system...")
        try:
            from utils.anti_bot import AntiBotConfig
            config = AntiBotConfig()  # Use default config
            anti_bot_system = AntiBotSystem(config)
            logger.info("✅ Anti-bot system initialized")
        except Exception as e:
            logger.warning(f"⚠️ Advanced anti-bot system failed, using mock: {e}")
            # Create a simple mock for basic functionality
            from unittest.mock import Mock
            anti_bot_system = Mock()
            anti_bot_system.simulate_human_behavior = Mock()
            anti_bot_system.get_driver = Mock()
            logger.info("✅ Mock anti-bot system initialized")
        
        # Initialize ethical scraping policy
        logger.info("Initializing ethical scraping policies...")
        scraping_policy = ScrapingPolicy()
        logger.info("✅ Scraping policy initialized")
        
        return database_client, anti_bot_system, scraping_policy
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {e}")
        logger.error(traceback.format_exc())
        raise


def run_google_trends_scraper(database_client, anti_bot_system, scraping_policy, logger) -> Dict[str, Any]:
    """Run Google Trends scraper"""
    scraper_name = "Google Trends"
    results = {"name": scraper_name, "success": False, "data_count": 0, "error": None, "duration": 0}
    
    start_time = time.time()
    logger.info(f"🚀 Starting {scraper_name} scraper...")
    
    try:
        scraper = GoogleTrendsScraper(anti_bot_system, scraping_policy)
        
        # Sample keywords for testing (you can modify this)
        test_keywords = ["shopee", "skincare", "fashion", "food delivery", "travel"]
        
        logger.info(f"Collecting trends for keywords: {test_keywords}")
        trends_data = scraper.get_trends(test_keywords)
        
        if trends_data:
            # Store in database
            database_client.insert_google_trends(trends_data)
            results["success"] = True
            results["data_count"] = len(test_keywords)
            logger.info(f"✅ {scraper_name} completed successfully. Collected data for {len(test_keywords)} keywords")
        else:
            logger.warning(f"⚠️ {scraper_name} returned no data")
            
    except Exception as e:
        results["error"] = str(e)
        logger.error(f"❌ {scraper_name} failed: {e}")
        logger.error(traceback.format_exc())
    
    finally:
        results["duration"] = round(time.time() - start_time, 2)
        logger.info(f"⏱️ {scraper_name} execution time: {results['duration']} seconds")
    
    return results


def run_shopee_scraper(database_client, anti_bot_system, scraping_policy, logger) -> Dict[str, Any]:
    """Run Shopee scraper"""
    scraper_name = "Shopee Philippines"
    results = {"name": scraper_name, "success": False, "data_count": 0, "error": None, "duration": 0}
    
    start_time = time.time()
    logger.info(f"🚀 Starting {scraper_name} scraper...")
    
    try:
        scraper = ShopeeScraper(anti_bot_system, scraping_policy)
        
        # Sample search terms for testing
        search_terms = ["skincare", "fashion", "electronics"]
        all_products = []
        
        for term in search_terms:
            logger.info(f"Searching for products: {term}")
            products = scraper.search_products(term, limit=10)  # Limit for testing
            
            if products:
                all_products.extend(products)
                logger.info(f"Found {len(products)} products for '{term}'")
            else:
                logger.warning(f"No products found for '{term}'")
            
            # Add delay between searches to be respectful
            time.sleep(2)
        
        if all_products:
            # Store in database
            database_client.insert_shopee_products(all_products, type="search_results")
            results["success"] = True
            results["data_count"] = len(all_products)
            logger.info(f"✅ {scraper_name} completed successfully. Collected {len(all_products)} products")
        else:
            logger.warning(f"⚠️ {scraper_name} returned no products")
            
    except Exception as e:
        results["error"] = str(e)
        logger.error(f"❌ {scraper_name} failed: {e}")
        logger.error(traceback.format_exc())
    
    finally:
        # Ensure driver cleanup
        try:
            if hasattr(scraper, 'driver') and scraper.driver:
                scraper.driver.quit()
        except:
            pass
        
        results["duration"] = round(time.time() - start_time, 2)
        logger.info(f"⏱️ {scraper_name} execution time: {results['duration']} seconds")
    
    return results


def run_lazada_scraper(database_client, anti_bot_system, scraping_policy, logger) -> Dict[str, Any]:
    """Run Lazada scraper for real data collection"""
    scraper_name = "Lazada Philippines"
    results = {"name": scraper_name, "success": False, "data_count": 0, "error": None, "duration": 0}
    
    start_time = time.time()
    logger.info(f"🚀 Starting {scraper_name} scraper...")
    
    try:
        scraper = LazadaScraper(use_undetected=True)
        
        # Test search terms for real data
        test_keywords = ["skincare", "fashion", "electronics"]
        all_products = []
        
        for keyword in test_keywords:
            logger.info(f"Searching Lazada for products: {keyword}")
            try:
                products = scraper.search_products(keyword, limit=5)
                
                if products:
                    all_products.extend(products)
                    logger.info(f"Found {len(products)} real products for '{keyword}'")
                else:
                    logger.warning(f"No real products found for '{keyword}'")
                
                # Add delay between searches
                time.sleep(3)
                
            except Exception as e:
                logger.warning(f"Error searching Lazada for '{keyword}': {e}")
                continue
        
        if all_products:
            # Store in database (using shopee_products table for compatibility)
            database_client.insert_shopee_products(all_products)
            results["success"] = True
            results["data_count"] = len(all_products)
            logger.info(f"✅ {scraper_name} completed successfully. Collected {len(all_products)} real products")
        else:
            logger.warning(f"⚠️ {scraper_name} returned no real products")
            
    except Exception as e:
        results["error"] = str(e)
        logger.error(f"❌ {scraper_name} failed: {e}")
        logger.error(traceback.format_exc())
    
    finally:
        # Ensure driver cleanup
        try:
            if hasattr(scraper, 'driver') and scraper.driver:
                scraper.driver.quit()
        except:
            pass
        
        results["duration"] = round(time.time() - start_time, 2)
        logger.info(f"⏱️ {scraper_name} execution time: {results['duration']} seconds")
    
    return results


def run_tiktok_scraper(database_client, anti_bot_system, scraping_policy, logger) -> Dict[str, Any]:
    """Run TikTok scraper"""
    scraper_name = "TikTok Philippines"
    results = {"name": scraper_name, "success": False, "data_count": 0, "error": None, "duration": 0}
    
    start_time = time.time()
    logger.info(f"🚀 Starting {scraper_name} scraper...")
    
    try:
        scraper = TikTokScraper(anti_bot_system, scraping_policy)
        
        # Sample hashtag searches for testing
        test_hashtags = ["philippines", "fyp", "viral"]
        all_videos = []
        
        for hashtag in test_hashtags:
            logger.info(f"Searching TikTok for hashtag: #{hashtag}")
            videos = scraper.search_hashtag_videos(hashtag, limit=5)  # Small limit for testing
            
            if videos:
                all_videos.extend(videos)
                logger.info(f"Found {len(videos)} videos for '#{hashtag}'")
            else:
                logger.warning(f"No videos found for '#{hashtag}'")
            
            # Add delay between hashtag searches to be respectful
            time.sleep(3)
        
        if all_videos:
            # Store in database
            database_client.insert_tiktok_videos(all_videos)
            results["success"] = True
            results["data_count"] = len(all_videos)
            logger.info(f"✅ {scraper_name} completed successfully. Collected {len(all_videos)} videos")
        else:
            logger.warning(f"⚠️ {scraper_name} returned no videos")
            results["error"] = "No videos found"
            
    except Exception as e:
        results["error"] = str(e)
        logger.error(f"❌ {scraper_name} failed: {e}")
        logger.error(traceback.format_exc())
    
    finally:
        # Ensure cleanup
        try:
            if 'scraper' in locals():
                scraper.cleanup()
        except:
            pass
        
        results["duration"] = round(time.time() - start_time, 2)
        logger.info(f"⏱️ {scraper_name} execution time: {results['duration']} seconds")
    
    return results


def generate_summary_report(all_results: List[Dict[str, Any]], logger):
    """Generate and log execution summary"""
    logger.info("=" * 60)
    logger.info("📊 EXECUTION SUMMARY REPORT")
    logger.info("=" * 60)
    
    total_duration = sum(result["duration"] for result in all_results)
    successful_scrapers = [r for r in all_results if r["success"]]
    failed_scrapers = [r for r in all_results if not r["success"]]
    total_data_collected = sum(result["data_count"] for result in all_results)
    
    logger.info(f"⏱️ Total execution time: {total_duration:.2f} seconds")
    logger.info(f"✅ Successful scrapers: {len(successful_scrapers)}/{len(all_results)}")
    logger.info(f"📊 Total data points collected: {total_data_collected}")
    
    # Individual scraper results
    for result in all_results:
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        logger.info(f"{status} | {result['name']}: {result['data_count']} items in {result['duration']}s")
        if result["error"]:
            logger.info(f"  └─ Error: {result['error']}")
    
    # Recommendations
    if failed_scrapers:
        logger.warning("🔧 RECOMMENDATIONS:")
        for failed in failed_scrapers:
            if "Not implemented" in str(failed["error"]):
                logger.warning(f"  • Complete implementation of {failed['name']} scraper")
            else:
                logger.warning(f"  • Debug and fix {failed['name']}: {failed['error']}")
    
    logger.info("=" * 60)


def main():
    """Main orchestration function"""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("🇵🇭 VOOTCAMP PH DATA SCRAPER - STARTING")
    logger.info("=" * 60)
    
    all_results = []
    
    try:
        # Validate settings
        logger.info("🔧 Validating configuration...")
        Settings.validate_required_settings()
        logger.info("✅ Configuration validation passed")
        
        # Initialize core components
        database_client, anti_bot_system, scraping_policy = initialize_components(logger)
        
        # Run scrapers sequentially (progressive complexity approach)
        logger.info("🎯 Starting scraper execution sequence...")
        
        # 1. Google Trends (Simplest)
        google_results = run_google_trends_scraper(database_client, anti_bot_system, scraping_policy, logger)
        all_results.append(google_results)
        
        # Add delay between scrapers
        logger.info("⏸️ Waiting 5 seconds before next scraper...")
        time.sleep(5)
        
        # 2. Lazada Philippines (Real data source - NEW!)
        lazada_results = run_lazada_scraper(database_client, anti_bot_system, scraping_policy, logger)
        all_results.append(lazada_results)
        
        # Add delay before Shopee
        logger.info("⏸️ Waiting 5 seconds before next scraper...")
        time.sleep(5)
        
        # 3. Shopee Philippines (Moderate complexity - fallback to sample data)
        shopee_results = run_shopee_scraper(database_client, anti_bot_system, scraping_policy, logger)
        all_results.append(shopee_results)
        
        # Add delay before TikTok
        logger.info("⏸️ Waiting 5 seconds before next scraper...")
        time.sleep(5)
        
        # 4. TikTok (Most complex - placeholder for now)
        tiktok_results = run_tiktok_scraper(database_client, anti_bot_system, scraping_policy, logger)
        all_results.append(tiktok_results)
        
        # Generate summary report
        generate_summary_report(all_results, logger)
        
        # Final status
        successful_count = len([r for r in all_results if r["success"]])
        if successful_count == len(all_results):
            logger.info("🎉 ALL SCRAPERS COMPLETED SUCCESSFULLY!")
        elif successful_count > 0:
            logger.info(f"⚠️ PARTIAL SUCCESS: {successful_count}/{len(all_results)} scrapers completed")
        else:
            logger.error("❌ ALL SCRAPERS FAILED")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR during execution: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("🏁 VOOTCAMP PH DATA SCRAPER - COMPLETED")
    logger.info("=" * 60)


if __name__ == "__main__":
    main() 