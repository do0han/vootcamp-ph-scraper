#!/usr/bin/env python3
"""
Core 3 Scrapers Standalone Integration Testing
핵심 3개 스크래퍼 독립 실행 통합 테스트
"""

import os
import sys
import logging
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def setup_test_logging():
    """테스트용 로깅 설정"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/standalone_integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger('standalone_integration_test')

class StandaloneCore3IntegrationTest:
    """독립 실행형 핵심 3개 스크래퍼 통합 테스트"""
    
    def __init__(self):
        self.logger = setup_test_logging()
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "Standalone Integration Test",
            "tests": {},
            "overall_status": "PENDING",
            "issues_found": [],
            "recommendations": [],
            "execution_summary": {}
        }
        
    def test_file_structure(self) -> Dict[str, Any]:
        """파일 구조 및 존재 여부 테스트"""
        test_name = "File Structure Validation"
        self.logger.info(f"📁 Testing {test_name}...")
        
        test_result = {
            "name": test_name,
            "status": "FAILED",
            "duration": 0,
            "details": {},
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            project_root = Path(__file__).parent
            
            # Core files to check
            required_files = {
                "main.py": "Main execution file",
                "scrapers/google_trends.py": "Google Trends scraper",
                "scrapers/lazada_persona_scraper.py": "Lazada Persona scraper",
                "scrapers/tiktok_shop_scraper.py": "TikTok Shop scraper",
                "database/supabase_client.py": "Database client",
                "config/settings.py": "Configuration settings",
                "utils/anti_bot_system.py": "Anti-bot protection",
                "utils/ethical_scraping.py": "Scraping policy",
                "utils/enhanced_error_handler.py": "Enhanced error handler",
                "utils/performance_monitoring.py": "Performance monitoring"
            }
            
            # Check file existence
            existing_files = {}
            missing_files = {}
            
            for file_path, description in required_files.items():
                full_path = project_root / file_path
                if full_path.exists():
                    existing_files[file_path] = {
                        "description": description,
                        "size": full_path.stat().st_size,
                        "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
                    }
                else:
                    missing_files[file_path] = description
            
            # Check configuration files
            config_files = {
                "config/performance_config.json": "Performance configuration",
                ".env": "Environment variables",
                "requirements.txt": "Python dependencies"
            }
            
            config_status = {}
            for file_path, description in config_files.items():
                full_path = project_root / file_path
                config_status[file_path] = {
                    "exists": full_path.exists(),
                    "description": description
                }
            
            test_result["details"] = {
                "existing_files": existing_files,
                "missing_files": missing_files,
                "config_files": config_status,
                "total_required": len(required_files),
                "total_existing": len(existing_files)
            }
            
            if not missing_files:
                test_result["status"] = "SUCCESS"
                self.logger.info(f"✅ {test_name} passed - all {len(existing_files)} core files found")
            else:
                test_result["issues"] = [f"Missing files: {list(missing_files.keys())}"]
                self.logger.warning(f"⚠️ {test_name} - {len(missing_files)} files missing")
        
        except Exception as e:
            test_result["issues"].append(f"File structure test exception: {str(e)}")
            self.logger.error(f"❌ {test_name} failed: {e}")
        
        finally:
            test_result["duration"] = round(time.time() - start_time, 2)
        
        return test_result
    
    def test_import_structure(self) -> Dict[str, Any]:
        """Import 구조 및 의존성 테스트"""
        test_name = "Import Structure Validation"
        self.logger.info(f"📦 Testing {test_name}...")
        
        test_result = {
            "name": test_name,
            "status": "FAILED",
            "duration": 0,
            "details": {},
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            # Test core imports
            import_tests = {
                "config.settings": "Settings configuration",
                "scrapers.google_trends": "Google Trends scraper",
                "scrapers.lazada_persona_scraper": "Lazada Persona scraper", 
                "scrapers.tiktok_shop_scraper": "TikTok Shop scraper",
                "utils.anti_bot_system": "Anti-bot system",
                "utils.ethical_scraping": "Ethical scraping policy"
            }
            
            successful_imports = {}
            failed_imports = {}
            
            for module_name, description in import_tests.items():
                try:
                    # Attempt to import the module
                    __import__(module_name)
                    successful_imports[module_name] = description
                    self.logger.debug(f"✅ Successfully imported {module_name}")
                except ImportError as e:
                    failed_imports[module_name] = {"description": description, "error": str(e)}
                    self.logger.warning(f"⚠️ Failed to import {module_name}: {e}")
                except Exception as e:
                    failed_imports[module_name] = {"description": description, "error": f"Unexpected error: {str(e)}"}
                    self.logger.warning(f"⚠️ Unexpected error importing {module_name}: {e}")
            
            # Test optional imports
            optional_imports = {
                "utils.enhanced_error_handler": "Enhanced error handling",
                "utils.performance_monitoring": "Performance monitoring"
            }
            
            optional_status = {}
            for module_name, description in optional_imports.items():
                try:
                    __import__(module_name)
                    optional_status[module_name] = {"available": True, "description": description}
                except:
                    optional_status[module_name] = {"available": False, "description": description}
            
            test_result["details"] = {
                "successful_imports": successful_imports,
                "failed_imports": failed_imports,
                "optional_imports": optional_status,
                "success_rate": len(successful_imports) / len(import_tests)
            }
            
            if not failed_imports:
                test_result["status"] = "SUCCESS"
                self.logger.info(f"✅ {test_name} passed - all {len(successful_imports)} core imports successful")
            else:
                test_result["issues"] = [f"Failed imports: {list(failed_imports.keys())}"]
                self.logger.warning(f"⚠️ {test_name} - {len(failed_imports)} imports failed")
        
        except Exception as e:
            test_result["issues"].append(f"Import test exception: {str(e)}")
            self.logger.error(f"❌ {test_name} failed: {e}")
        
        finally:
            test_result["duration"] = round(time.time() - start_time, 2)
        
        return test_result
    
    def test_configuration_validation(self) -> Dict[str, Any]:
        """설정 파일 및 환경 변수 검증"""
        test_name = "Configuration Validation"
        self.logger.info(f"⚙️ Testing {test_name}...")
        
        test_result = {
            "name": test_name,
            "status": "FAILED",
            "duration": 0,
            "details": {},
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            # Load environment variables
            from dotenv import load_dotenv
            load_dotenv()
            
            # Check required environment variables
            required_env_vars = {
                "SUPABASE_URL": "Supabase database URL",
                "SUPABASE_KEY": "Supabase API key"
            }
            
            env_status = {}
            missing_env = []
            
            for var_name, description in required_env_vars.items():
                value = os.getenv(var_name)
                if value:
                    env_status[var_name] = {
                        "available": True,
                        "description": description,
                        "length": len(value),
                        "masked_value": value[:10] + "..." if len(value) > 10 else "***"
                    }
                else:
                    env_status[var_name] = {"available": False, "description": description}
                    missing_env.append(var_name)
            
            # Check optional configuration files
            config_files_status = {}
            project_root = Path(__file__).parent
            
            config_files = {
                "config/performance_config.json": "Performance settings",
                "logs/optimization_plan.json": "Optimization plan"
            }
            
            for file_path, description in config_files.items():
                full_path = project_root / file_path
                if full_path.exists():
                    try:
                        with open(full_path, 'r') as f:
                            config_data = json.load(f)
                        config_files_status[file_path] = {
                            "available": True,
                            "description": description,
                            "keys": list(config_data.keys()) if isinstance(config_data, dict) else "Non-dict data"
                        }
                    except Exception as e:
                        config_files_status[file_path] = {
                            "available": False,
                            "description": description,
                            "error": f"Failed to parse: {str(e)}"
                        }
                else:
                    config_files_status[file_path] = {
                        "available": False,
                        "description": description,
                        "error": "File not found"
                    }
            
            test_result["details"] = {
                "environment_variables": env_status,
                "missing_env_vars": missing_env,
                "config_files": config_files_status
            }
            
            if not missing_env:
                test_result["status"] = "SUCCESS"
                self.logger.info(f"✅ {test_name} passed - all environment variables configured")
            else:
                test_result["issues"] = [f"Missing environment variables: {missing_env}"]
                self.logger.warning(f"⚠️ {test_name} - missing env vars: {missing_env}")
        
        except Exception as e:
            test_result["issues"].append(f"Configuration test exception: {str(e)}")
            self.logger.error(f"❌ {test_name} failed: {e}")
        
        finally:
            test_result["duration"] = round(time.time() - start_time, 2)
        
        return test_result
    
    def test_scraper_initialization(self) -> Dict[str, Any]:
        """스크래퍼 초기화 테스트"""
        test_name = "Scraper Initialization"
        self.logger.info(f"🤖 Testing {test_name}...")
        
        test_result = {
            "name": test_name,
            "status": "FAILED",
            "duration": 0,
            "details": {},
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            # Import scrapers
            from scrapers.google_trends import GoogleTrendsScraper
            from scrapers.lazada_persona_scraper import LazadaPersonaScraper
            from scrapers.tiktok_shop_scraper import TikTokShopScraper
            from utils.anti_bot_system import AntiBotSystem
            from utils.ethical_scraping import ScrapingPolicy
            
            # Mock anti-bot system for testing
            from unittest.mock import Mock
            mock_anti_bot = Mock()
            mock_anti_bot.simulate_human_behavior = Mock()
            mock_anti_bot.get_driver = Mock()
            
            scraping_policy = ScrapingPolicy()
            
            scraper_tests = {}
            
            # Test Google Trends Scraper
            try:
                google_scraper = GoogleTrendsScraper(mock_anti_bot, scraping_policy)
                scraper_tests["Google Trends"] = {
                    "initialized": True,
                    "class_name": google_scraper.__class__.__name__,
                    "has_get_trends": hasattr(google_scraper, 'get_trends')
                }
                self.logger.info("✅ Google Trends scraper initialized successfully")
            except Exception as e:
                scraper_tests["Google Trends"] = {"initialized": False, "error": str(e)}
                self.logger.warning(f"⚠️ Google Trends scraper failed: {e}")
            
            # Test Lazada Persona Scraper
            try:
                lazada_scraper = LazadaPersonaScraper(persona_name="young_filipina", use_undetected=True)
                scraper_tests["Lazada Persona"] = {
                    "initialized": True,
                    "class_name": lazada_scraper.__class__.__name__,
                    "persona_name": lazada_scraper.persona.name if hasattr(lazada_scraper, 'persona') else "Unknown",
                    "has_get_products": hasattr(lazada_scraper, 'get_persona_trending_products')
                }
                self.logger.info("✅ Lazada Persona scraper initialized successfully")
                
                # Cleanup
                if hasattr(lazada_scraper, 'driver') and lazada_scraper.driver:
                    lazada_scraper.driver.quit()
                    
            except Exception as e:
                scraper_tests["Lazada Persona"] = {"initialized": False, "error": str(e)}
                self.logger.warning(f"⚠️ Lazada Persona scraper failed: {e}")
            
            # Test TikTok Shop Scraper
            try:
                tiktok_scraper = TikTokShopScraper(use_undetected=True, headless=True)
                scraper_tests["TikTok Shop"] = {
                    "initialized": True,
                    "class_name": tiktok_scraper.__class__.__name__,
                    "has_get_products": hasattr(tiktok_scraper, 'get_top_products'),
                    "has_close": hasattr(tiktok_scraper, 'close')
                }
                self.logger.info("✅ TikTok Shop scraper initialized successfully")
                
                # Cleanup
                tiktok_scraper.close()
                
            except Exception as e:
                scraper_tests["TikTok Shop"] = {"initialized": False, "error": str(e)}
                self.logger.warning(f"⚠️ TikTok Shop scraper failed: {e}")
            
            test_result["details"] = {
                "scraper_tests": scraper_tests,
                "total_scrapers": len(scraper_tests),
                "successful_inits": len([s for s in scraper_tests.values() if s.get("initialized", False)])
            }
            
            successful_inits = len([s for s in scraper_tests.values() if s.get("initialized", False)])
            if successful_inits == len(scraper_tests):
                test_result["status"] = "SUCCESS"
                self.logger.info(f"✅ {test_name} passed - all {successful_inits} scrapers initialized")
            else:
                failed_scrapers = [name for name, data in scraper_tests.items() if not data.get("initialized", False)]
                test_result["issues"] = [f"Failed to initialize: {failed_scrapers}"]
                self.logger.warning(f"⚠️ {test_name} - {len(failed_scrapers)} scrapers failed to initialize")
        
        except Exception as e:
            test_result["issues"].append(f"Scraper initialization test exception: {str(e)}")
            self.logger.error(f"❌ {test_name} failed: {e}")
        
        finally:
            test_result["duration"] = round(time.time() - start_time, 2)
        
        return test_result
    
    def test_main_execution_flow(self) -> Dict[str, Any]:
        """main.py 실행 흐름 검증"""
        test_name = "Main Execution Flow"
        self.logger.info(f"🔄 Testing {test_name}...")
        
        test_result = {
            "name": test_name,
            "status": "FAILED",
            "duration": 0,
            "details": {},
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            # Read and analyze main.py
            main_path = Path(__file__).parent / "main.py"
            
            with open(main_path, 'r') as f:
                main_content = f.read()
            
            # Check for key functions and patterns
            flow_checks = {
                "setup_logging": "def setup_logging(" in main_content,
                "initialize_components": "def initialize_components(" in main_content,
                "run_google_trends_scraper": "def run_google_trends_scraper(" in main_content,
                "run_lazada_persona_scraper": "def run_lazada_persona_scraper(" in main_content,
                "run_tiktok_shop_scraper": "def run_tiktok_shop_scraper(" in main_content,
                "generate_summary_report": "def generate_summary_report(" in main_content,
                "main_function": "def main():" in main_content,
                "core_3_scrapers_focus": "CORE 3 SCRAPERS" in main_content,
                "optimized_delays": "time.sleep(5)  # Optimized delay" in main_content
            }
            
            # Check import statements
            import_checks = {
                "google_trends_import": "from scrapers.google_trends import GoogleTrendsScraper" in main_content,
                "lazada_persona_import": "from scrapers.lazada_persona_scraper import LazadaPersonaScraper" in main_content,
                "tiktok_shop_import": "from scrapers.tiktok_shop_scraper import TikTokShopScraper" in main_content,
                "supabase_import": "from database.supabase_client import SupabaseClient" in main_content,
                "no_deprecated_shopee": "from scrapers.shopee" not in main_content,
                "no_deprecated_tiktok": "from scrapers.tiktok import TikTokScraper" not in main_content
            }
            
            # Check execution sequence
            sequence_checks = {
                "google_first": main_content.find("run_google_trends_scraper") < main_content.find("run_lazada_persona_scraper"),
                "lazada_second": main_content.find("run_lazada_persona_scraper") < main_content.find("run_tiktok_shop_scraper"),
                "has_delays": "time.sleep(" in main_content,
                "performance_tracking": "optimization" in main_content.lower() or "performance" in main_content.lower()
            }
            
            all_checks = {**flow_checks, **import_checks, **sequence_checks}
            passed_checks = sum(all_checks.values())
            total_checks = len(all_checks)
            
            test_result["details"] = {
                "flow_checks": flow_checks,
                "import_checks": import_checks,
                "sequence_checks": sequence_checks,
                "passed_checks": passed_checks,
                "total_checks": total_checks,
                "success_rate": passed_checks / total_checks
            }
            
            if passed_checks >= total_checks * 0.9:  # 90% pass rate
                test_result["status"] = "SUCCESS"
                self.logger.info(f"✅ {test_name} passed - {passed_checks}/{total_checks} checks passed")
            else:
                failed_checks = [name for name, passed in all_checks.items() if not passed]
                test_result["issues"] = [f"Failed checks: {failed_checks}"]
                self.logger.warning(f"⚠️ {test_name} - {total_checks - passed_checks} checks failed")
        
        except Exception as e:
            test_result["issues"].append(f"Main execution flow test exception: {str(e)}")
            self.logger.error(f"❌ {test_name} failed: {e}")
        
        finally:
            test_result["duration"] = round(time.time() - start_time, 2)
        
        return test_result
    
    def run_standalone_integration_test(self) -> Dict[str, Any]:
        """독립 실행형 통합 테스트 실행"""
        self.logger.info("=" * 80)
        self.logger.info("🧪 CORE 3 SCRAPERS STANDALONE INTEGRATION TEST")
        self.logger.info("🎯 Validating: File Structure + Imports + Configuration + Scrapers")
        self.logger.info("=" * 80)
        
        # Run all tests
        tests = [
            self.test_file_structure,
            self.test_import_structure,
            self.test_configuration_validation,
            self.test_scraper_initialization,
            self.test_main_execution_flow
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                self.test_results["tests"][result["name"]] = result
                
                # Brief delay between tests
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"💥 Test execution failed: {e}")
                self.test_results["issues_found"].append(f"Test execution error: {str(e)}")
        
        # Generate final report
        self.generate_standalone_report()
        
        return self.test_results
    
    def generate_standalone_report(self):
        """독립 실행형 테스트 리포트 생성"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("📊 STANDALONE INTEGRATION TEST REPORT")
        self.logger.info("=" * 80)
        
        # Calculate metrics
        total_tests = len(self.test_results["tests"])
        passed_tests = len([t for t in self.test_results["tests"].values() if t["status"] == "SUCCESS"])
        total_duration = sum(t.get("duration", 0) for t in self.test_results["tests"].values())
        
        # Overall status
        if passed_tests == total_tests:
            self.test_results["overall_status"] = "SUCCESS"
            overall_emoji = "✅"
        elif passed_tests >= total_tests * 0.8:  # 80% pass rate
            self.test_results["overall_status"] = "MOSTLY_SUCCESS"
            overall_emoji = "⚠️"
        else:
            self.test_results["overall_status"] = "FAILED"
            overall_emoji = "❌"
        
        # Display results
        self.logger.info(f"{overall_emoji} Overall Status: {self.test_results['overall_status']}")
        self.logger.info(f"📈 Tests Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests:.1%})")
        self.logger.info(f"⏱️ Total Duration: {total_duration:.2f} seconds")
        
        # Individual test results
        self.logger.info("\n📋 Individual Test Results:")
        for test_name, result in self.test_results["tests"].items():
            status_emoji = "✅" if result["status"] == "SUCCESS" else "❌"
            self.logger.info(f"{status_emoji} {test_name}: {result['status']} ({result.get('duration', 0):.1f}s)")
            
            if result.get("issues"):
                for issue in result["issues"][:2]:  # Show first 2 issues only
                    self.logger.info(f"    └─ Issue: {issue}")
        
        # Generate recommendations
        self.generate_standalone_recommendations()
        
        if self.test_results["recommendations"]:
            self.logger.info(f"\n💡 Recommendations:")
            for rec in self.test_results["recommendations"]:
                self.logger.info(f"    • {rec}")
        
        # Create execution summary
        self.test_results["execution_summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_duration": total_duration,
            "test_timestamp": datetime.now().isoformat()
        }
        
        # Save report
        self.save_standalone_report()
        
        self.logger.info("=" * 80)
    
    def generate_standalone_recommendations(self):
        """독립 실행형 테스트 기반 추천사항"""
        recommendations = []
        
        # Check for failed tests
        failed_tests = [name for name, result in self.test_results["tests"].items() 
                       if result["status"] != "SUCCESS"]
        
        if failed_tests:
            recommendations.append(f"Address {len(failed_tests)} failed test(s): {', '.join(failed_tests)}")
        
        # Check specific test results
        file_test = self.test_results["tests"].get("File Structure Validation")
        if file_test and file_test.get("details", {}).get("missing_files"):
            recommendations.append("Create missing required files before running scrapers")
        
        import_test = self.test_results["tests"].get("Import Structure Validation")
        if import_test and import_test.get("details", {}).get("failed_imports"):
            recommendations.append("Fix import issues and dependency problems")
        
        config_test = self.test_results["tests"].get("Configuration Validation")
        if config_test and config_test.get("details", {}).get("missing_env_vars"):
            recommendations.append("Configure missing environment variables in .env file")
        
        scraper_test = self.test_results["tests"].get("Scraper Initialization")
        if scraper_test and scraper_test.get("details", {}).get("successful_inits", 0) < 3:
            recommendations.append("Debug scraper initialization issues before production")
        
        if not recommendations:
            recommendations.append("All standalone tests passed - system architecture is sound")
            recommendations.append("Ready for live data collection testing with proper Supabase connection")
        
        self.test_results["recommendations"] = recommendations
    
    def save_standalone_report(self):
        """독립 실행형 테스트 리포트 저장"""
        try:
            report_path = Path(__file__).parent / "logs" / f"standalone_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            self.logger.info(f"📄 Standalone integration report saved: {report_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save standalone report: {e}")

def main():
    """메인 실행 함수"""
    
    # Create and run standalone integration test
    integration_test = StandaloneCore3IntegrationTest()
    results = integration_test.run_standalone_integration_test()
    
    # Exit with appropriate code
    if results["overall_status"] == "SUCCESS":
        sys.exit(0)
    elif results["overall_status"] == "MOSTLY_SUCCESS":
        sys.exit(1)  # Mostly successful - minor issues
    else:
        sys.exit(2)  # Failed

if __name__ == "__main__":
    main()