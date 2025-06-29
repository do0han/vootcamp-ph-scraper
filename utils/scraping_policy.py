"""
스크래핑 정책 및 제한 관리
"""

import random
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class RequestStats:
    """요청 통계"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_request_time: Optional[datetime] = None
    session_start_time: datetime = datetime.now()

class ScrapingPolicy:
    """스크래핑 정책"""
    
    def __init__(self, requests_per_minute: int = 30):
        """
        스크래핑 정책 초기화
        
        Args:
            requests_per_minute: 분당 최대 요청 수
        """
        self.requests_per_minute = requests_per_minute
        self.request_window = timedelta(minutes=1)
        self.request_times: deque = deque(maxlen=requests_per_minute)
        
        self.stats = RequestStats()
        
    def can_make_request(self) -> bool:
        """요청 가능 여부 확인"""
        now = datetime.now()
        
        # 오래된 요청 제거
        while self.request_times and (now - self.request_times[0]) > self.request_window:
            self.request_times.popleft()
        
        # 현재 윈도우의 요청 수 확인
        return len(self.request_times) < self.requests_per_minute
        
    def record_request(self):
        """요청 기록"""
        now = datetime.now()
        self.request_times.append(now)
    
    def get_current_rate(self) -> float:
        """현재 요청 속도 계산 (분당 요청 수)"""
        now = datetime.now()
        
        # 오래된 요청 제거
        while self.request_times and (now - self.request_times[0]) > self.request_window:
            self.request_times.popleft()
            
        return len(self.request_times)
        
    def get_time_until_next_request(self) -> Optional[float]:
        """다음 요청까지 대기 시간 계산 (초)"""
        if self.can_make_request():
            return 0.0
            
        now = datetime.now()
        oldest_request = self.request_times[0]
        return (oldest_request + self.request_window - now).total_seconds()
    
    def get_session_stats(self) -> Dict:
        """세션 통계 반환"""
        return {
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "success_rate": (self.stats.successful_requests / self.stats.total_requests * 100 
                           if self.stats.total_requests > 0 else 0),
            "session_duration": str(datetime.now() - self.stats.session_start_time),
            "requests_per_minute": self.get_current_rate()
        } 