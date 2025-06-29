"""
성능 모니터링 및 로깅
"""

import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import statistics

logger = logging.getLogger(__name__)

@dataclass
class BlockingEvent:
    """차단 이벤트 정보"""
    timestamp: datetime
    url: str
    error_type: str
    duration: float
    recovery_successful: bool

@dataclass
class PerformanceMetrics:
    """성능 지표"""
    timestamp: datetime
    success_rate: float
    error_rate: float
    block_rate: float
    avg_response_time: float
    request_count: int
    error_count: int
    block_count: int

class PerformanceMonitor:
    """성능 모니터링"""
    
    def __init__(self, log_directory: str):
        self.start_time = datetime.now()
        self.blocking_events: List[BlockingEvent] = []
        self.response_times: List[float] = []
        self.request_count = 0
        self.error_count = 0
        self.success_count = 0
        
        # 로그 디렉토리 생성
        self.log_dir = Path(log_directory)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 파일 핸들러 추가
        log_file = self.log_dir / "performance.log"
        file_handler = logging.FileHandler(str(log_file))
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def record_request(self, response_time: float, success: bool = True):
        """요청 기록"""
        self.request_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        self.response_times.append(response_time)
    
    def record_blocking_event(self, event: BlockingEvent) -> None:
        """차단 이벤트 기록"""
        self.blocking_events.append(event)
        self.error_count += 1
        
        # 로그 파일에 기록
        log_file = self.log_dir / "blocking_events.json"
        event_data = {
            "timestamp": event.timestamp.isoformat(),
            "url": event.url,
            "error_type": event.error_type,
            "duration": event.duration,
            "recovery_successful": event.recovery_successful
        }
        
        try:
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
            else:
                events = []
                
            events.append(event_data)
            
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logging.error(f"차단 이벤트 기록 중 오류: {str(e)}")
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """현재 성능 지표 계산"""
        if self.request_count == 0:
            return PerformanceMetrics(
                timestamp=datetime.now(),
                success_rate=1.0,
                error_rate=0.0,
                block_rate=0.0,
                avg_response_time=0.0,
                request_count=0,
                error_count=0,
                block_count=0
            )
        
        recent_window = datetime.now() - timedelta(seconds=self.config["metrics_interval"])
        recent_blocks = sum(1 for e in self.blocking_events if e.timestamp >= recent_window)
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            success_rate=self.success_count / self.request_count,
            error_rate=self.error_count / self.request_count,
            block_rate=recent_blocks / self.request_count if self.request_count > 0 else 0.0,
            avg_response_time=statistics.mean(self.response_times) if self.response_times else 0.0,
            request_count=self.request_count,
            error_count=self.error_count,
            block_count=recent_blocks
        )
    
    def check_alert_conditions(self) -> List[str]:
        """경고 조건 확인"""
        metrics = self.get_current_metrics()
        alerts = []
        
        thresholds = self.config["alert_thresholds"]
        if metrics.error_rate > thresholds["error_rate"]:
            alerts.append(f"High error rate: {metrics.error_rate:.2%}")
        if metrics.block_rate > thresholds["block_rate"]:
            alerts.append(f"High block rate: {metrics.block_rate:.2%}")
        if metrics.avg_response_time > thresholds["response_time"]:
            alerts.append(f"High response time: {metrics.avg_response_time:.2f}s")
        
        return alerts
    
    def save_metrics(self):
        """현재 지표 저장"""
        metrics = self.get_current_metrics()
        metrics_file = self.log_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.jsonl"
        try:
            with open(metrics_file, "a", encoding="utf-8") as f:
                metrics_dict = asdict(metrics)
                metrics_dict["timestamp"] = metrics_dict["timestamp"].isoformat()
                json.dump(metrics_dict, f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def get_summary_report(self) -> Dict[str, Any]:
        """성능 요약 보고서 생성"""
        metrics = self.get_current_metrics()
        duration = datetime.now() - self.start_time
        
        return {
            "duration": str(duration),
            "total_requests": self.request_count,
            "success_rate": f"{metrics.success_rate:.2%}",
            "error_rate": f"{metrics.error_rate:.2%}",
            "block_rate": f"{metrics.block_rate:.2%}",
            "avg_response_time": f"{metrics.avg_response_time:.2f}s",
            "total_blocking_events": len(self.blocking_events),
            "alerts": self.check_alert_conditions()
        } 