#!/usr/bin/env python3
"""
Main.py Dry Run Integration Test
main.py 건식 실행 통합 테스트
"""

import os
import sys
import logging
import time
import traceback
import subprocess
from datetime import datetime
from pathlib import Path
import json

def setup_test_logging():
    """테스트용 로깅 설정"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/main_dry_run_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger('main_dry_run_test')

class MainDryRunTest:
    """Main.py 건식 실행 테스트"""
    
    def __init__(self):
        self.logger = setup_test_logging()
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "Main.py Dry Run Integration Test",
            "overall_status": "PENDING",
            "execution_results": {},
            "performance_metrics": {},
            "issues_found": [],
            "recommendations": []
        }
    
    def run_syntax_check(self) -> dict:
        """Python 문법 검사"""
        self.logger.info("🔍 Running Python syntax check on main.py...")
        
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', 'main.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Syntax check passed")
                return {"status": "SUCCESS", "message": "No syntax errors"}
            else:
                self.logger.error(f"❌ Syntax errors found: {result.stderr}")
                return {"status": "FAILED", "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"status": "FAILED", "error": "Syntax check timeout"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def check_import_availability(self) -> dict:
        """필수 import 가능성 검사"""
        self.logger.info("📦 Checking import availability...")
        
        # Create a minimal test script
        test_script = '''
import sys
sys.path.append(".")

try:
    # Test core imports
    from dotenv import load_dotenv
    load_dotenv()
    
    from config.settings import Settings
    from database.supabase_client import SupabaseClient
    from scrapers.google_trends import GoogleTrendsScraper
    from scrapers.lazada_persona_scraper import LazadaPersonaScraper
    from scrapers.tiktok_shop_scraper import TikTokShopScraper
    from utils.anti_bot_system import AntiBotSystem
    from utils.ethical_scraping import ScrapingPolicy
    
    print("SUCCESS: All core imports available")
    sys.exit(0)
    
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"OTHER_ERROR: {e}")
    sys.exit(2)
'''
        
        try:
            # Write temporary test file
            test_file = Path(__file__).parent / "temp_import_test.py"
            with open(test_file, 'w') as f:
                f.write(test_script)
            
            # Run import test
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Cleanup
            test_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                self.logger.info("✅ All imports available")
                return {"status": "SUCCESS", "message": "All core imports successful"}
            elif result.returncode == 1:
                self.logger.warning(f"⚠️ Import issues: {result.stdout}")
                return {"status": "IMPORT_ISSUES", "error": result.stdout}
            else:
                self.logger.error(f"❌ Other import errors: {result.stdout}")
                return {"status": "FAILED", "error": result.stdout}
                
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def run_main_execution_test(self) -> dict:
        """Main.py 실행 테스트 (짧은 timeout으로 초기화 확인)"""
        self.logger.info("🚀 Testing main.py execution (with early timeout)...")
        
        try:
            start_time = time.time()
            
            # Run main.py with short timeout to test initialization
            result = subprocess.run(
                [sys.executable, 'main.py'],
                capture_output=True,
                text=True,
                timeout=45  # 45 seconds timeout to check initialization
            )
            
            duration = time.time() - start_time
            
            # Since we expect timeout, check if initialization messages appear
            output = result.stdout + result.stderr
            
            initialization_checks = {
                "logging_setup": "VOOTCAMP PH CORE 3 SCRAPERS" in output,
                "config_validation": "Configuration validation" in output or "Validating configuration" in output,
                "database_init": "database" in output.lower() or "supabase" in output.lower(),
                "scraper_start": "Starting" in output and ("Google Trends" in output or "Lazada" in output or "TikTok" in output),
                "core_3_focus": "CORE 3" in output or "Google Trends" in output
            }
            
            passed_checks = sum(initialization_checks.values())
            
            self.logger.info(f"⏱️ Execution duration: {duration:.1f}s")
            self.logger.info(f"✅ Initialization checks passed: {passed_checks}/5")
            
            return {
                "status": "SUCCESS" if passed_checks >= 3 else "PARTIAL",
                "duration": duration,
                "initialization_checks": initialization_checks,
                "passed_checks": passed_checks,
                "output_preview": output[:500] + "..." if len(output) > 500 else output,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired as e:
            # Timeout is expected - check if we got initialization output
            duration = 45.0
            output = e.stdout + e.stderr if e.stdout and e.stderr else ""
            
            if "VOOTCAMP PH CORE 3 SCRAPERS" in output or "Starting" in output:
                self.logger.info("✅ Main.py started successfully (timeout expected)")
                return {
                    "status": "SUCCESS",
                    "duration": duration,
                    "message": "Main execution started successfully (timed out as expected)",
                    "output_preview": output[:500] + "..." if len(output) > 500 else output
                }
            else:
                self.logger.warning("⚠️ Main.py may have startup issues")
                return {
                    "status": "PARTIAL",
                    "duration": duration,
                    "message": "Main execution started but unclear status",
                    "output_preview": output[:500] + "..." if len(output) > 500 else output
                }
                
        except Exception as e:
            return {"status": "FAILED", "duration": 0, "error": str(e)}
    
    def analyze_code_structure(self) -> dict:
        """코드 구조 분석"""
        self.logger.info("📊 Analyzing code structure...")
        
        try:
            main_path = Path(__file__).parent / "main.py"
            
            with open(main_path, 'r') as f:
                content = f.read()
            
            structure_analysis = {
                "total_lines": len(content.splitlines()),
                "function_count": content.count("def "),
                "core_scrapers_mentioned": {
                    "google_trends": "google_trends" in content.lower(),
                    "lazada_persona": "lazada_persona" in content.lower(),
                    "tiktok_shop": "tiktok_shop" in content.lower()
                },
                "deprecated_removed": {
                    "no_shopee_basic": "from scrapers.shopee import" not in content,
                    "no_tiktok_basic": "from scrapers.tiktok import TikTokScraper" not in content,
                    "no_lazada_basic": "from scrapers.lazada_scraper import" not in content
                },
                "optimization_features": {
                    "optimized_delays": "time.sleep(5)  # Optimized delay" in content,
                    "performance_tracking": "performance" in content.lower(),
                    "core_3_focus": "CORE 3 SCRAPERS" in content,
                    "error_handling": content.count("try:") >= 3
                }
            }
            
            # Calculate quality score
            quality_checks = [
                structure_analysis["core_scrapers_mentioned"]["google_trends"],
                structure_analysis["core_scrapers_mentioned"]["lazada_persona"],
                structure_analysis["core_scrapers_mentioned"]["tiktok_shop"],
                structure_analysis["deprecated_removed"]["no_shopee_basic"],
                structure_analysis["deprecated_removed"]["no_tiktok_basic"],
                structure_analysis["optimization_features"]["optimized_delays"],
                structure_analysis["optimization_features"]["core_3_focus"]
            ]
            
            quality_score = sum(quality_checks) / len(quality_checks)
            
            self.logger.info(f"📊 Code quality score: {quality_score:.1%}")
            
            return {
                "status": "SUCCESS",
                "structure_analysis": structure_analysis,
                "quality_score": quality_score,
                "total_lines": structure_analysis["total_lines"],
                "function_count": structure_analysis["function_count"]
            }
            
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def run_full_dry_run_test(self) -> dict:
        """전체 건식 실행 테스트"""
        self.logger.info("=" * 70)
        self.logger.info("🧪 MAIN.PY DRY RUN INTEGRATION TEST")
        self.logger.info("🎯 Testing: Syntax + Imports + Execution + Structure")
        self.logger.info("=" * 70)
        
        # Run all tests
        tests = {
            "syntax_check": self.run_syntax_check,
            "import_availability": self.check_import_availability,
            "main_execution": self.run_main_execution_test,
            "code_structure": self.analyze_code_structure
        }
        
        for test_name, test_func in tests.items():
            try:
                self.logger.info(f"\n🔧 Running {test_name}...")
                result = test_func()
                self.test_results["execution_results"][test_name] = result
                
                status_emoji = "✅" if result["status"] == "SUCCESS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
                self.logger.info(f"{status_emoji} {test_name}: {result['status']}")
                
            except Exception as e:
                self.logger.error(f"💥 {test_name} failed: {e}")
                self.test_results["execution_results"][test_name] = {"status": "FAILED", "error": str(e)}
        
        # Generate final report
        self.generate_dry_run_report()
        
        return self.test_results
    
    def generate_dry_run_report(self):
        """건식 실행 테스트 리포트 생성"""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📊 DRY RUN TEST REPORT")
        self.logger.info("=" * 70)
        
        # Calculate overall status
        results = self.test_results["execution_results"]
        total_tests = len(results)
        success_tests = len([r for r in results.values() if r["status"] == "SUCCESS"])
        partial_tests = len([r for r in results.values() if r["status"] == "PARTIAL"])
        
        if success_tests == total_tests:
            self.test_results["overall_status"] = "SUCCESS"
            overall_emoji = "✅"
        elif success_tests + partial_tests >= total_tests * 0.75:
            self.test_results["overall_status"] = "MOSTLY_SUCCESS"
            overall_emoji = "⚠️"
        else:
            self.test_results["overall_status"] = "FAILED"
            overall_emoji = "❌"
        
        # Display results
        self.logger.info(f"{overall_emoji} Overall Status: {self.test_results['overall_status']}")
        self.logger.info(f"📈 Success Rate: {success_tests}/{total_tests} ({success_tests/total_tests:.1%})")
        
        # Individual results
        self.logger.info("\n📋 Test Results:")
        for test_name, result in results.items():
            status_emoji = "✅" if result["status"] == "SUCCESS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
            self.logger.info(f"{status_emoji} {test_name}: {result['status']}")
            
            if "duration" in result:
                self.logger.info(f"    └─ Duration: {result['duration']:.1f}s")
            if "quality_score" in result:
                self.logger.info(f"    └─ Quality Score: {result['quality_score']:.1%}")
            if "error" in result:
                self.logger.info(f"    └─ Error: {result['error'][:100]}...")
        
        # Performance metrics
        main_execution = results.get("main_execution", {})
        if main_execution.get("duration"):
            self.test_results["performance_metrics"] = {
                "startup_time": main_execution["duration"],
                "initialization_success": main_execution.get("passed_checks", 0) >= 3
            }
        
        # Generate recommendations
        self.generate_dry_run_recommendations()
        
        if self.test_results["recommendations"]:
            self.logger.info(f"\n💡 Recommendations:")
            for rec in self.test_results["recommendations"]:
                self.logger.info(f"    • {rec}")
        
        # Save report
        self.save_dry_run_report()
        
        self.logger.info("=" * 70)
    
    def generate_dry_run_recommendations(self):
        """건식 실행 테스트 기반 추천사항"""
        recommendations = []
        results = self.test_results["execution_results"]
        
        # Check specific test results
        if results.get("syntax_check", {}).get("status") != "SUCCESS":
            recommendations.append("Fix Python syntax errors before deployment")
        
        if results.get("import_availability", {}).get("status") != "SUCCESS":
            recommendations.append("Resolve import and dependency issues")
        
        main_exec = results.get("main_execution", {})
        if main_exec.get("status") not in ["SUCCESS", "PARTIAL"]:
            recommendations.append("Debug main.py execution startup issues")
        elif main_exec.get("passed_checks", 0) < 3:
            recommendations.append("Improve main.py initialization reliability")
        
        code_struct = results.get("code_structure", {})
        if code_struct.get("quality_score", 0) < 0.8:
            recommendations.append("Consider additional code structure improvements")
        
        # Performance recommendations
        if main_exec.get("duration", 0) > 30:
            recommendations.append("Consider further startup time optimization")
        
        if not recommendations:
            recommendations.append("Dry run tests passed - main.py architecture is sound")
            recommendations.append("Ready for live execution with proper Supabase connection")
            recommendations.append("Consider running full integration test with live data")
        
        self.test_results["recommendations"] = recommendations
    
    def save_dry_run_report(self):
        """건식 실행 테스트 리포트 저장"""
        try:
            report_path = Path(__file__).parent / "logs" / f"main_dry_run_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            self.logger.info(f"📄 Dry run test report saved: {report_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save dry run report: {e}")

def main():
    """메인 실행 함수"""
    
    # Create and run dry run test
    dry_run_test = MainDryRunTest()
    results = dry_run_test.run_full_dry_run_test()
    
    # Exit with appropriate code
    if results["overall_status"] == "SUCCESS":
        sys.exit(0)
    elif results["overall_status"] == "MOSTLY_SUCCESS":
        sys.exit(1)  # Mostly successful
    else:
        sys.exit(2)  # Failed

if __name__ == "__main__":
    main()