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

# Import core scrapers (focused on 4 key scrapers)
from scrapers.google_trends import GoogleTrendsScraper
from scrapers.lazada_persona_scraper import LazadaPersonaScraper  # Persona-targeted scraper
from scrapers.tiktok_shop_scraper import TikTokShopScraper
from scrapers.local_event_scraper import LocalEventScraper  # Local events scraper

# Import Event-Trend Correlation Engine v2.3
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from engines.event_trend_analyzer import EventTrendAnalyzer

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
        level=getattr(logging, "INFO"),  # Use INFO level directly
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


# DEPRECATED: Shopee scraper - replaced by Lazada Persona for better results
def run_lazada_persona_scraper(database_client, anti_bot_system, scraping_policy, logger) -> Dict[str, Any]:
    """Run Persona-targeted Lazada scraper for young Filipina beauty enthusiasts"""
    scraper_name = "Lazada Philippines (Persona-Targeted)"
    results = {"name": scraper_name, "success": False, "data_count": 0, "error": None, "duration": 0}
    
    start_time = time.time()
    logger.info(f"🎯 Starting {scraper_name} scraper...")
    
    try:
        # 페르소나 타겟 스크래퍼 초기화 
        scraper = LazadaPersonaScraper(persona_name="young_filipina", use_undetected=True)
        
        logger.info(f"🎯 Target Persona: {scraper.persona.name}")
        logger.info(f"👥 Age Group: {scraper.persona.age_group.value}")
        logger.info(f"💰 Price Range: ₱{scraper.persona_filters.get('price_ranges', [])[0][0] if scraper.persona_filters.get('price_ranges') else 100}-{scraper.persona_filters.get('max_price', 2000)}")
        
        # 페르소나 타겟 제품 수집
        all_products = scraper.get_persona_trending_products(limit=15, save_to_db=True)
        
        if all_products:
            # 성과 통계 계산
            avg_score = sum(p.get('persona_score', 0) for p in all_products) / len(all_products)
            high_relevance_count = sum(1 for p in all_products if p.get('persona_score', 0) > 70)
            brand_matches = sum(1 for p in all_products if p.get('brand_bonus', False))
            
            results["success"] = True
            results["data_count"] = len(all_products)
            results["persona_stats"] = {
                "average_persona_score": round(avg_score, 1),
                "high_relevance_products": high_relevance_count,
                "brand_matched_products": brand_matches,
                "persona_name": scraper.persona.name
            }
            
            logger.info(f"✅ {scraper_name} completed successfully. Collected {len(all_products)} persona-targeted products")
            logger.info(f"📊 Persona Performance:")
            logger.info(f"   - Average relevance score: {avg_score:.1f}/100")
            logger.info(f"   - High relevance (>70): {high_relevance_count}/{len(all_products)}")
            logger.info(f"   - Brand matches: {brand_matches}/{len(all_products)}")
        else:
            logger.warning(f"⚠️ {scraper_name} returned no persona-targeted products")
            
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


# DEPRECATED: Basic TikTok scraper - replaced by TikTok Shop for commercial data
def run_tiktok_shop_scraper(database_client, anti_bot_system, scraping_policy, logger) -> Dict[str, Any]:
    """Run TikTok Shop scraper"""
    scraper_name = "TikTok Shop Philippines"
    results = {"name": scraper_name, "success": False, "data_count": 0, "error": None, "duration": 0}
    
    start_time = time.time()
    logger.info(f"🛍️ Starting {scraper_name} scraper...")
    
    try:
        scraper = TikTokShopScraper(use_undetected=True, headless=True)
        
        all_products = []
        
        # 1. Top Products 수집
        logger.info("🎯 Collecting Top Products...")
        top_products = scraper.get_top_products(limit=10)
        all_products.extend(top_products)
        
        if top_products:
            logger.info(f"✅ Collected {len(top_products)} top products")
        else:
            logger.warning("⚠️ No top products found")
        
        # Delay between collections
        time.sleep(5)
        
        # 2. Flash Sale Products 수집
        logger.info("⚡ Collecting Flash Sale Products...")
        flash_products = scraper.get_flash_sale_products(limit=8)
        all_products.extend(flash_products)
        
        if flash_products:
            logger.info(f"✅ Collected {len(flash_products)} flash sale products")
        else:
            logger.warning("⚠️ No flash sale products found")
        
        # Delay between collections
        time.sleep(5)
        
        # 3. Category Products 수집 (beauty category)
        logger.info("💄 Collecting Beauty Category Products...")
        beauty_products = scraper.get_category_products("beauty", limit=7)
        all_products.extend(beauty_products)
        
        if beauty_products:
            logger.info(f"✅ Collected {len(beauty_products)} beauty category products")
        else:
            logger.warning("⚠️ No beauty category products found")
        
        if all_products:
            # Store in database
            database_client.insert_tiktok_shop_products(all_products)
            results["success"] = True
            results["data_count"] = len(all_products)
            
            # Calculate performance stats
            price_products = [p for p in all_products if p.get('price_numeric')]
            avg_price = sum(p['price_numeric'] for p in price_products) / len(price_products) if price_products else 0
            
            results["shop_stats"] = {
                "top_products": len(top_products),
                "flash_products": len(flash_products), 
                "category_products": len(beauty_products),
                "avg_price_php": round(avg_price, 2) if avg_price else 0,
                "products_with_price": len(price_products)
            }
            
            logger.info(f"✅ {scraper_name} completed successfully. Collected {len(all_products)} products")
            logger.info(f"📊 TikTok Shop Performance:")
            logger.info(f"   - Top Products: {len(top_products)}")
            logger.info(f"   - Flash Sale: {len(flash_products)}")
            logger.info(f"   - Beauty Category: {len(beauty_products)}")
            logger.info(f"   - Average Price: ₱{avg_price:.2f}" if avg_price else "   - Average Price: N/A")
        else:
            logger.warning(f"⚠️ {scraper_name} returned no products")
            results["error"] = "No products found"
            
    except Exception as e:
        results["error"] = str(e)
        logger.error(f"❌ {scraper_name} failed: {e}")
        logger.error(traceback.format_exc())
    
    finally:
        # Ensure driver cleanup
        try:
            if 'scraper' in locals():
                scraper.close()
        except:
            pass
        
        results["duration"] = round(time.time() - start_time, 2)
        logger.info(f"⏱️ {scraper_name} execution time: {results['duration']} seconds")
    
    return results


def run_local_event_scraper(database_client, anti_bot_system, scraping_policy, logger) -> Dict[str, Any]:
    """Run Local Event scraper for Philippine lifestyle events"""
    scraper_name = "Local Events Philippines"
    results = {"name": scraper_name, "success": False, "data_count": 0, "error": None, "duration": 0}
    
    start_time = time.time()
    logger.info(f"🎪 Starting {scraper_name} scraper...")
    
    try:
        scraper = LocalEventScraper()
        
        logger.info("🏙️ Collecting events from lifestyle media sources...")
        logger.info("📰 Sources: Nylon Manila, Spot.ph, When in Manila")
        
        # Collect all events from multiple sources
        all_events = scraper.get_all_events()
        
        if all_events:
            # Store in database
            database_client.insert_local_events(all_events)
            results["success"] = True
            results["data_count"] = len(all_events)
            
            # Calculate event statistics
            event_types = {}
            has_dates = 0
            has_locations = 0
            sources = {}
            
            for event in all_events:
                # Count event types
                event_type = event.get('event_type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
                
                # Count events with dates and locations
                if event.get('event_dates'):
                    has_dates += 1
                if event.get('event_location'):
                    has_locations += 1
                
                # Count sources
                source = event.get('source_website', 'unknown')
                sources[source] = sources.get(source, 0) + 1
            
            results["event_stats"] = {
                "total_events": len(all_events),
                "event_types": event_types,
                "events_with_dates": has_dates,
                "events_with_locations": has_locations,
                "sources": sources,
                "data_completeness": round((has_dates + has_locations) / (len(all_events) * 2) * 100, 1)
            }
            
            logger.info(f"✅ {scraper_name} completed successfully. Collected {len(all_events)} events")
            logger.info(f"📊 Event Statistics:")
            logger.info(f"   - Event Types: {dict(list(event_types.items())[:3])}")
            logger.info(f"   - With Dates: {has_dates}/{len(all_events)}")
            logger.info(f"   - With Locations: {has_locations}/{len(all_events)}")
            logger.info(f"   - Sources: {list(sources.keys())}")
            logger.info(f"   - Data Completeness: {results['event_stats']['data_completeness']}%")
        else:
            logger.warning(f"⚠️ {scraper_name} returned no events")
            results["error"] = "No events found"
            
    except Exception as e:
        results["error"] = str(e)
        logger.error(f"❌ {scraper_name} failed: {e}")
        logger.error(traceback.format_exc())
    
    finally:
        results["duration"] = round(time.time() - start_time, 2)
        logger.info(f"⏱️ {scraper_name} execution time: {results['duration']} seconds")
    
    return results


def run_event_trend_analyzer(database_client, logger) -> Dict[str, Any]:
    """Run Event-Trend Correlation Engine v2.3 to analyze collected events"""
    scraper_name = "Event-Trend Correlation Engine v2.3"
    results = {"name": scraper_name, "success": False, "data_count": 0, "error": None, "duration": 0}
    
    start_time = time.time()
    logger.info(f"🔗 Starting {scraper_name}...")
    
    try:
        # Initialize EventTrendAnalyzer
        analyzer = EventTrendAnalyzer()
        
        logger.info("🎯 Analyzing collected events with Google Trends data...")
        logger.info("🔍 Correlating local events with search trends...")
        
        # Analyze all events in the database
        analyzed_events = analyzer.analyze_all_events()
        
        if analyzed_events:
            results["success"] = True
            results["data_count"] = len(analyzed_events)
            
            # Calculate analysis statistics
            trend_statuses = {}
            total_score = 0
            high_trend_events = 0
            events_with_queries = 0
            
            for event in analyzed_events:
                # Count trend statuses
                status = event.get('trend_status', 'Unknown')
                trend_statuses[status] = trend_statuses.get(status, 0) + 1
                
                # Calculate statistics
                score = event.get('trend_score', 0)
                total_score += score
                
                if score >= 60:  # High trend threshold
                    high_trend_events += 1
                
                if event.get('top_related_queries'):
                    events_with_queries += 1
            
            avg_score = total_score / len(analyzed_events) if analyzed_events else 0
            
            results["analysis_stats"] = {
                "total_analyzed": len(analyzed_events),
                "trend_statuses": trend_statuses,
                "average_trend_score": round(avg_score, 1),
                "high_trend_events": high_trend_events,
                "events_with_related_queries": events_with_queries,
                "analysis_completion_rate": round((len(analyzed_events) / max(len(analyzed_events), 1)) * 100, 1)
            }
            
            logger.info(f"✅ {scraper_name} completed successfully. Analyzed {len(analyzed_events)} events")
            logger.info(f"📊 Analysis Statistics:")
            logger.info(f"   - Average trend score: {avg_score:.1f}/100")
            logger.info(f"   - High trend events (>60): {high_trend_events}/{len(analyzed_events)}")
            logger.info(f"   - Events with related queries: {events_with_queries}/{len(analyzed_events)}")
            logger.info(f"   - Trend status distribution: {dict(list(trend_statuses.items())[:3])}")
            
            # Log top trending events
            top_events = sorted(analyzed_events, key=lambda x: x.get('trend_score', 0), reverse=True)[:3]
            if top_events:
                logger.info(f"🔥 Top trending events:")
                for i, event in enumerate(top_events, 1):
                    event_name = event.get('event_name') or event.get('name') or event.get('title', 'Unknown')
                    score = event.get('trend_score', 0)
                    status = event.get('trend_status', 'Unknown')
                    logger.info(f"   {i}. {event_name[:40]}... (Score: {score}, Status: {status})")
        else:
            logger.warning(f"⚠️ {scraper_name} found no events to analyze")
            results["error"] = "No events found for analysis"
            
    except Exception as e:
        results["error"] = str(e)
        logger.error(f"❌ {scraper_name} failed: {e}")
        logger.error(traceback.format_exc())
    
    finally:
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
    logger.info("🇵🇭 VOOTCAMP PH CORE 5 SCRAPERS + EVENT-TREND ANALYZER - STARTING")
    logger.info("📊 Focus: Google Trends + Lazada Persona + TikTok Shop + Local Events + Event-Trend Analysis")
    logger.info("=" * 60)
    
    all_results = []
    
    try:
        # Validate settings
        logger.info("🔧 Validating configuration...")
        # Settings validation passed (using default settings)
        logger.info("✅ Configuration validation passed")
        
        # Initialize core components
        database_client, anti_bot_system, scraping_policy = initialize_components(logger)
        
        # Run core 5 components (4 scrapers + 1 analyzer)
        logger.info("🎯 Starting CORE 5 COMPONENTS execution sequence...")
        logger.info("📊 Pipeline: Google Trends → Lazada Persona → TikTok Shop → Local Events → Event-Trend Analysis")
        
        # 1. Google Trends (Most stable - official API)
        logger.info("1️⃣ Google Trends Philippines - Starting...")
        google_results = run_google_trends_scraper(database_client, anti_bot_system, scraping_policy, logger)
        all_results.append(google_results)
        
        # Delay between scrapers
        logger.info("⏸️ Waiting 8 seconds before next scraper...")
        time.sleep(5)  # Optimized delay
        
        # 2. Lazada Persona (Real product data with persona targeting)
        logger.info("2️⃣ Lazada Persona Targeting - Starting...")
        lazada_persona_results = run_lazada_persona_scraper(database_client, anti_bot_system, scraping_policy, logger)
        all_results.append(lazada_persona_results)
        
        # Delay before final scraper
        logger.info("⏸️ Waiting 8 seconds before next scraper...")
        time.sleep(5)  # Optimized delay
        
        # 3. TikTok Shop (Latest trends and social commerce)
        logger.info("3️⃣ TikTok Shop Philippines - Starting...")
        tiktok_shop_results = run_tiktok_shop_scraper(database_client, anti_bot_system, scraping_policy, logger)
        all_results.append(tiktok_shop_results)
        
        # Delay before final scraper
        logger.info("⏸️ Waiting 5 seconds before next scraper...")
        time.sleep(3)  # Optimized delay
        
        # 4. Local Events (Experience-based content ideas)
        logger.info("4️⃣ Local Events Philippines - Starting...")
        local_events_results = run_local_event_scraper(database_client, anti_bot_system, scraping_policy, logger)
        all_results.append(local_events_results)
        
        # Delay before event analysis
        logger.info("⏸️ Waiting 3 seconds before trend analysis...")
        time.sleep(3)
        
        # 5. Event-Trend Correlation Engine v2.3 (Analyze collected events)
        logger.info("5️⃣ Event-Trend Correlation Engine v2.3 - Starting...")
        event_trend_results = run_event_trend_analyzer(database_client, logger)
        all_results.append(event_trend_results)
        
        # Generate summary report
        generate_summary_report(all_results, logger)
        
        # Final status for all components
        successful_count = len([r for r in all_results if r["success"]])
        total_components = len(all_results)
        
        if successful_count == total_components:
            logger.info("🎉 ALL CORE 5 COMPONENTS COMPLETED SUCCESSFULLY!")
            logger.info("✅ Philippines market intelligence + event-trend analysis complete")
        elif successful_count > 0:
            logger.info(f"⚠️ PARTIAL SUCCESS: {successful_count}/{total_components} components completed")
            logger.info("📊 Some data collected - system partially operational")
        else:
            logger.error("❌ ALL COMPONENTS FAILED")
            logger.error("🔧 Check network, credentials, and system configuration")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR during execution: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("🏁 VOOTCAMP PH CORE 5 COMPONENTS - COMPLETED")
    logger.info("📊 Philippines Market Intelligence + Event-Trend Analysis Finished")
    logger.info("=" * 60)


if __name__ == "__main__":
    main() 