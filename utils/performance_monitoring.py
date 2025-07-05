#!/usr/bin/env python3
"""
Performance Monitoring for Core 3 Scrapers
핵심 3개 스크래퍼 성능 모니터링
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any
import json
from pathlib import Path

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger('performance_monitor')
        self.metrics = {
            "execution_times": {},
            "success_rates": {},
            "data_collection": {},
            "errors": []
        }
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """타이머 시작"""
        self.start_times[operation] = time.time()
        self.logger.debug(f"⏱️ Timer started: {operation}")
    
    def end_timer(self, operation: str) -> float:
        """타이머 종료 및 시간 반환"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.metrics["execution_times"][operation] = duration
            self.logger.info(f"⏱️ {operation}: {duration:.2f}s")
            return duration
        return 0.0
    
    def record_success(self, scraper: str, data_count: int):
        """성공 기록"""
        if scraper not in self.metrics["success_rates"]:
            self.metrics["success_rates"][scraper] = {"attempts": 0, "successes": 0}
        
        self.metrics["success_rates"][scraper]["attempts"] += 1
        self.metrics["success_rates"][scraper]["successes"] += 1
        self.metrics["data_collection"][scraper] = data_count
        
        success_rate = self.metrics["success_rates"][scraper]["successes"] / self.metrics["success_rates"][scraper]["attempts"]
        self.logger.info(f"✅ {scraper} success: {data_count} items, {success_rate:.1%} rate")
    
    def record_failure(self, scraper: str, error: str):
        """실패 기록"""
        if scraper not in self.metrics["success_rates"]:
            self.metrics["success_rates"][scraper] = {"attempts": 0, "successes": 0}
        
        self.metrics["success_rates"][scraper]["attempts"] += 1
        self.metrics["errors"].append({
            "scraper": scraper,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        success_rate = self.metrics["success_rates"][scraper]["successes"] / self.metrics["success_rates"][scraper]["attempts"]
        self.logger.warning(f"❌ {scraper} failed: {error}, {success_rate:.1%} rate")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        total_execution = sum(self.metrics["execution_times"].values())
        total_data = sum(self.metrics["data_collection"].values())
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_execution_time": total_execution,
            "total_data_collected": total_data,
            "scrapers": {},
            "overall_success_rate": 0,
            "performance_grade": "Unknown"
        }
        
        total_attempts = 0
        total_successes = 0
        
        for scraper, rates in self.metrics["success_rates"].items():
            success_rate = rates["successes"] / rates["attempts"] if rates["attempts"] > 0 else 0
            total_attempts += rates["attempts"]
            total_successes += rates["successes"]
            
            report["scrapers"][scraper] = {
                "execution_time": self.metrics["execution_times"].get(scraper, 0),
                "success_rate": success_rate,
                "data_collected": self.metrics["data_collection"].get(scraper, 0),
                "attempts": rates["attempts"]
            }
        
        report["overall_success_rate"] = total_successes / total_attempts if total_attempts > 0 else 0
        
        # Performance grading
        if report["overall_success_rate"] >= 0.9 and total_execution < 300:
            report["performance_grade"] = "A"
        elif report["overall_success_rate"] >= 0.8 and total_execution < 360:
            report["performance_grade"] = "B"
        elif report["overall_success_rate"] >= 0.7:
            report["performance_grade"] = "C"
        else:
            report["performance_grade"] = "D"
        
        return report
    
    def save_report(self, filename: str = None):
        """리포트 저장"""
        if not filename:
            filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_path = Path(__file__).parent.parent / "logs" / filename
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.get_performance_report(), f, indent=2)
        
        self.logger.info(f"📊 Performance report saved: {report_path}")
        return report_path

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
