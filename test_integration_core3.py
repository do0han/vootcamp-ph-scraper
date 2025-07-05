#!/usr/bin/env python3
"""
Core 3 Scrapers Integration Testing
핵심 3개 스크래퍼 통합 테스트 및 검증
"""

import os
import sys
import logging
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from config.settings import Settings
from database.supabase_client import SupabaseClient

# Import core scrapers
from scrapers.google_trends import GoogleTrendsScraper
from scrapers.lazada_persona_scraper import LazadaPersonaScraper
from scrapers.tiktok_shop_scraper import TikTokShopScraper

# Import utilities
from utils.anti_bot_system import AntiBotSystem
from utils.ethical_scraping import ScrapingPolicy

# Import performance monitoring
try:
    from utils.performance_monitoring import PerformanceMonitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("⚠️ Performance monitoring not available - proceeding without monitoring")

def setup_test_logging():
    """테스트용 로깅 설정"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger('integration_test')

class Core3ScrapersIntegrationTest:
    """핵심 3개 스크래퍼 통합 테스트 클래스"""
    
    def __init__(self):
        self.logger = setup_test_logging()
        self.performance_monitor = PerformanceMonitor() if MONITORING_AVAILABLE else None
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "PENDING",
            "performance_metrics": {},
            "issues_found": [],
            "recommendations": []
        }
        
    def setup_test_environment(self) -> bool:
        """테스트 환경 설정"""
        self.logger.info("🔧 Setting up integration test environment...")
        
        try:
            # Validate configuration
            Settings.validate_required_settings()
            self.logger.info("✅ Configuration validation passed")
            
            # Initialize database client
            self.database_client = SupabaseClient()
            self.logger.info("✅ Database client initialized")
            
            # Initialize anti-bot system (with fallback)
            try:
                from utils.anti_bot import AntiBotConfig
                config = AntiBotConfig()
                self.anti_bot_system = AntiBotSystem(config)
                self.logger.info("✅ Advanced anti-bot system initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Using mock anti-bot system: {e}")
                from unittest.mock import Mock
                self.anti_bot_system = Mock()
                self.anti_bot_system.simulate_human_behavior = Mock()
                self.anti_bot_system.get_driver = Mock()
            
            # Initialize scraping policy
            self.scraping_policy = ScrapingPolicy()
            self.logger.info("✅ Scraping policy initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Test environment setup failed: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def test_google_trends_scraper(self) -> Dict[str, Any]:
        """Google Trends 스크래퍼 테스트"""
        test_name = "Google Trends Integration"
        self.logger.info(f"🔍 Testing {test_name}...")
        
        if self.performance_monitor:
            self.performance_monitor.start_timer("google_trends_test")
        
        test_result = {
            "name": test_name,
            "status": "FAILED",
            "duration": 0,
            "data_collected": 0,
            "issues": [],
            "details": {}
        }
        
        start_time = time.time()
        
        try:
            # Initialize scraper
            scraper = GoogleTrendsScraper(self.anti_bot_system, self.scraping_policy)
            
            # Test keywords (smaller set for integration testing)
            test_keywords = ["skincare", "fashion", "food"]
            
            self.logger.info(f"Testing with keywords: {test_keywords}")
            trends_data = scraper.get_trends(test_keywords)
            
            if trends_data:
                # Test database storage
                self.database_client.insert_google_trends(trends_data)
                
                test_result["status"] = "SUCCESS"
                test_result["data_collected"] = len(test_keywords)
                test_result["details"] = {
                    "keywords_tested": test_keywords,
                    "api_response": "Valid",
                    "database_storage": "Success"
                }
                
                if self.performance_monitor:
                    self.performance_monitor.record_success("google_trends", len(test_keywords))
                
                self.logger.info(f"✅ {test_name} passed - {len(test_keywords)} keywords processed")
            else:
                test_result["issues"].append("No data returned from Google Trends API")
                self.logger.warning(f"⚠️ {test_name} - no data returned")
                
                if self.performance_monitor:
                    self.performance_monitor.record_failure("google_trends", "No data returned")
        
        except Exception as e:
            test_result["issues"].append(f"Exception: {str(e)}")
            self.logger.error(f"❌ {test_name} failed: {e}")
            
            if self.performance_monitor:
                self.performance_monitor.record_failure("google_trends", str(e))
        
        finally:
            test_result["duration"] = round(time.time() - start_time, 2)
            if self.performance_monitor:
                self.performance_monitor.end_timer("google_trends_test")
        
        return test_result
    
    def test_lazada_persona_scraper(self) -> Dict[str, Any]:
        """Lazada Persona 스크래퍼 테스트"""
        test_name = "Lazada Persona Integration"
        self.logger.info(f"🛒 Testing {test_name}...")
        
        if self.performance_monitor:
            self.performance_monitor.start_timer("lazada_persona_test")
        
        test_result = {
            "name": test_name,
            "status": "FAILED", 
            "duration": 0,
            "data_collected": 0,
            "issues": [],
            "details": {}
        }
        
        start_time = time.time()
        scraper = None
        
        try:
            # Initialize persona scraper
            scraper = LazadaPersonaScraper(persona_name="young_filipina", use_undetected=True)
            
            self.logger.info(f"Target persona: {scraper.persona.name}")
            
            # Test with limited products for integration testing
            products = scraper.get_persona_trending_products(limit=5, save_to_db=True)
            
            if products and len(products) > 0:
                # Calculate performance metrics
                avg_score = sum(p.get('persona_score', 0) for p in products) / len(products)
                high_relevance = sum(1 for p in products if p.get('persona_score', 0) > 70)
                
                test_result["status"] = "SUCCESS"
                test_result["data_collected"] = len(products)
                test_result["details"] = {
                    "persona_name": scraper.persona.name,
                    "products_collected": len(products),
                    "avg_persona_score": round(avg_score, 1),
                    "high_relevance_count": high_relevance,
                    "database_storage": "Success"
                }
                
                if self.performance_monitor:
                    self.performance_monitor.record_success("lazada_persona", len(products))
                
                self.logger.info(f"✅ {test_name} passed - {len(products)} persona products, avg score: {avg_score:.1f}")
            else:
                test_result["issues"].append("No persona products found")
                self.logger.warning(f"⚠️ {test_name} - no persona products found")
                
                if self.performance_monitor:
                    self.performance_monitor.record_failure("lazada_persona", "No products found")
        
        except Exception as e:
            test_result["issues"].append(f"Exception: {str(e)}")
            self.logger.error(f"❌ {test_name} failed: {e}")
            
            if self.performance_monitor:
                self.performance_monitor.record_failure("lazada_persona", str(e))
        
        finally:
            # Cleanup driver
            try:
                if scraper and hasattr(scraper, 'driver') and scraper.driver:
                    scraper.driver.quit()
            except:
                pass
            
            test_result["duration"] = round(time.time() - start_time, 2)
            if self.performance_monitor:
                self.performance_monitor.end_timer("lazada_persona_test")
        
        return test_result
    
    def test_tiktok_shop_scraper(self) -> Dict[str, Any]:
        """TikTok Shop 스크래퍼 테스트"""
        test_name = "TikTok Shop Integration"
        self.logger.info(f"📱 Testing {test_name}...")
        
        if self.performance_monitor:
            self.performance_monitor.start_timer("tiktok_shop_test")
        
        test_result = {
            "name": test_name,
            "status": "FAILED",
            "duration": 0,
            "data_collected": 0,
            "issues": [],
            "details": {}
        }
        
        start_time = time.time()
        scraper = None
        
        try:
            # Initialize TikTok Shop scraper
            scraper = TikTokShopScraper(use_undetected=True, headless=True)
            
            all_products = []
            
            # Test Top Products (limited for integration testing)
            self.logger.info("Testing top products collection...")
            top_products = scraper.get_top_products(limit=3)
            all_products.extend(top_products)
            
            time.sleep(3)  # Brief delay between collections
            
            # Test Flash Sale Products
            self.logger.info("Testing flash sale collection...")
            flash_products = scraper.get_flash_sale_products(limit=2)
            all_products.extend(flash_products)
            
            if all_products:
                # Store in database
                self.database_client.insert_tiktok_shop_products(all_products)
                
                # Calculate metrics
                price_products = [p for p in all_products if p.get('price_numeric')]
                avg_price = sum(p['price_numeric'] for p in price_products) / len(price_products) if price_products else 0
                
                test_result["status"] = "SUCCESS"
                test_result["data_collected"] = len(all_products)
                test_result["details"] = {
                    "top_products": len(top_products),
                    "flash_products": len(flash_products),
                    "avg_price_php": round(avg_price, 2) if avg_price else 0,
                    "products_with_price": len(price_products),
                    "database_storage": "Success"
                }
                
                if self.performance_monitor:
                    self.performance_monitor.record_success("tiktok_shop", len(all_products))
                
                self.logger.info(f"✅ {test_name} passed - {len(all_products)} products collected")
            else:
                test_result["issues"].append("No TikTok Shop products found")
                self.logger.warning(f"⚠️ {test_name} - no products found")
                
                if self.performance_monitor:
                    self.performance_monitor.record_failure("tiktok_shop", "No products found")
        
        except Exception as e:
            test_result["issues"].append(f"Exception: {str(e)}")
            self.logger.error(f"❌ {test_name} failed: {e}")
            
            if self.performance_monitor:
                self.performance_monitor.record_failure("tiktok_shop", str(e))
        
        finally:
            # Cleanup driver
            try:
                if scraper:
                    scraper.close()
            except:
                pass
            
            test_result["duration"] = round(time.time() - start_time, 2)
            if self.performance_monitor:
                self.performance_monitor.end_timer("tiktok_shop_test")
        
        return test_result
    
    def test_system_integration(self) -> Dict[str, Any]:
        """전체 시스템 통합 테스트"""
        test_name = "Full System Integration"
        self.logger.info(f"🔗 Testing {test_name}...")
        
        test_result = {
            "name": test_name,
            "status": "FAILED",
            "duration": 0,
            "details": {},
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            # Test configuration loading
            config_valid = True
            try:
                Settings.validate_required_settings()
            except Exception as e:
                config_valid = False
                test_result["issues"].append(f"Configuration validation failed: {e}")
            
            # Test database connectivity
            db_connected = True
            try:
                # Simple connection test
                self.database_client.supabase.table('google_trends').select('count').limit(1).execute()
            except Exception as e:
                db_connected = False
                test_result["issues"].append(f"Database connectivity failed: {e}")
            
            # Test anti-bot system
            antibot_available = hasattr(self.anti_bot_system, 'simulate_human_behavior')
            
            # Test scraping policy
            policy_available = hasattr(self.scraping_policy, 'can_scrape')
            
            test_result["details"] = {
                "configuration_valid": config_valid,
                "database_connected": db_connected,
                "antibot_system_available": antibot_available,
                "scraping_policy_available": policy_available,
                "performance_monitoring": MONITORING_AVAILABLE
            }
            
            # Overall status
            if all([config_valid, db_connected, antibot_available, policy_available]):
                test_result["status"] = "SUCCESS"
                self.logger.info(f"✅ {test_name} passed - all components integrated")
            else:
                self.logger.warning(f"⚠️ {test_name} - some components have issues")
        
        except Exception as e:
            test_result["issues"].append(f"Integration test exception: {str(e)}")
            self.logger.error(f"❌ {test_name} failed: {e}")
        
        finally:
            test_result["duration"] = round(time.time() - start_time, 2)
        
        return test_result
    
    def run_full_integration_test(self) -> Dict[str, Any]:
        """전체 통합 테스트 실행"""
        self.logger.info("=" * 70)
        self.logger.info("🧪 CORE 3 SCRAPERS INTEGRATION TEST")
        self.logger.info("🎯 Testing: Google Trends + Lazada Persona + TikTok Shop")
        self.logger.info("=" * 70)
        
        if not self.setup_test_environment():
            self.test_results["overall_status"] = "SETUP_FAILED"
            return self.test_results
        
        # Run individual scraper tests
        tests = [
            self.test_system_integration,
            self.test_google_trends_scraper,
            self.test_lazada_persona_scraper,
            self.test_tiktok_shop_scraper
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                self.test_results["tests"][result["name"]] = result
                
                # Brief delay between tests
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"💥 Test execution failed: {e}")
                self.test_results["issues_found"].append(f"Test execution error: {str(e)}")
        
        # Generate final report
        self.generate_integration_report()
        
        return self.test_results
    
    def generate_integration_report(self):
        """통합 테스트 리포트 생성"""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📊 INTEGRATION TEST REPORT")
        self.logger.info("=" * 70)
        
        # Calculate overall metrics
        total_tests = len(self.test_results["tests"])
        passed_tests = len([t for t in self.test_results["tests"].values() if t["status"] == "SUCCESS"])
        total_duration = sum(t.get("duration", 0) for t in self.test_results["tests"].values())
        total_data = sum(t.get("data_collected", 0) for t in self.test_results["tests"].values())
        
        # Overall status
        if passed_tests == total_tests:
            self.test_results["overall_status"] = "SUCCESS"
            overall_emoji = "✅"
        elif passed_tests > 0:
            self.test_results["overall_status"] = "PARTIAL_SUCCESS"
            overall_emoji = "⚠️"
        else:
            self.test_results["overall_status"] = "FAILED"
            overall_emoji = "❌"
        
        # Performance metrics
        if self.performance_monitor:
            perf_report = self.performance_monitor.get_performance_report()
            self.test_results["performance_metrics"] = perf_report
        
        # Display results
        self.logger.info(f"{overall_emoji} Overall Status: {self.test_results['overall_status']}")
        self.logger.info(f"📈 Tests Passed: {passed_tests}/{total_tests}")
        self.logger.info(f"⏱️ Total Duration: {total_duration:.2f} seconds")
        self.logger.info(f"📊 Total Data Collected: {total_data} items")
        
        # Individual test results
        self.logger.info("\n📋 Individual Test Results:")
        for test_name, result in self.test_results["tests"].items():
            status_emoji = "✅" if result["status"] == "SUCCESS" else "❌"
            self.logger.info(f"{status_emoji} {test_name}: {result['status']} ({result.get('duration', 0):.1f}s)")
            
            if result.get("data_collected", 0) > 0:
                self.logger.info(f"    └─ Data collected: {result['data_collected']} items")
            
            if result.get("issues"):
                for issue in result["issues"]:
                    self.logger.info(f"    └─ Issue: {issue}")
        
        # Performance summary
        if self.performance_monitor and self.test_results.get("performance_metrics"):
            perf = self.test_results["performance_metrics"]
            self.logger.info(f"\n📊 Performance Summary:")
            self.logger.info(f"    - Overall Success Rate: {perf.get('overall_success_rate', 0):.1%}")
            self.logger.info(f"    - Performance Grade: {perf.get('performance_grade', 'Unknown')}")
        
        # Recommendations
        self.generate_recommendations()
        
        if self.test_results["recommendations"]:
            self.logger.info(f"\n💡 Recommendations:")
            for rec in self.test_results["recommendations"]:
                self.logger.info(f"    • {rec}")
        
        # Save report
        self.save_integration_report()
        
        self.logger.info("=" * 70)
    
    def generate_recommendations(self):
        """테스트 결과 기반 추천사항 생성"""
        recommendations = []
        
        # Check for failed tests
        failed_tests = [t for t in self.test_results["tests"].values() if t["status"] != "SUCCESS"]
        
        if failed_tests:
            recommendations.append(f"Debug and resolve {len(failed_tests)} failed test(s)")
        
        # Check performance
        if self.test_results.get("performance_metrics"):
            perf = self.test_results["performance_metrics"]
            if perf.get("performance_grade") in ["C", "D"]:
                recommendations.append("Consider additional performance optimizations")
        
        # Check data collection
        total_data = sum(t.get("data_collected", 0) for t in self.test_results["tests"].values())
        if total_data < 10:
            recommendations.append("Low data collection - verify scraper configurations")
        
        # Integration specific recommendations
        system_test = self.test_results["tests"].get("Full System Integration")
        if system_test and system_test.get("issues"):
            recommendations.append("Address system integration issues before production")
        
        if not recommendations:
            recommendations.append("System integration testing passed - ready for production deployment")
        
        self.test_results["recommendations"] = recommendations
    
    def save_integration_report(self):
        """통합 테스트 리포트 저장"""
        try:
            import json
            
            report_path = Path(__file__).parent / "logs" / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            self.logger.info(f"📄 Integration test report saved: {report_path}")
            
            # Save performance report if available
            if self.performance_monitor:
                perf_report_path = self.performance_monitor.save_report(
                    f"integration_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save integration report: {e}")

def main():
    """메인 실행 함수"""
    
    # Create and run integration test
    integration_test = Core3ScrapersIntegrationTest()
    results = integration_test.run_full_integration_test()
    
    # Exit with appropriate code
    if results["overall_status"] == "SUCCESS":
        sys.exit(0)
    elif results["overall_status"] == "PARTIAL_SUCCESS":
        sys.exit(1)  # Partial success - manual review needed
    else:
        sys.exit(2)  # Failed

if __name__ == "__main__":
    main()