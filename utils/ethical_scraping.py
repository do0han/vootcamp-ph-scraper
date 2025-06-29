"""
Ethical scraping guidelines and implementation.
웹 스크래핑의 윤리적 고려사항을 구현하는 모듈입니다.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json
import re
from urllib.parse import urlparse
import requests

@dataclass
class ScrapingPolicy:
    """스크래핑 정책 설정"""
    max_requests_per_second: float = 1.0  # 초당 최대 요청 수
    max_requests_per_minute: int = 30    # 분당 최대 요청 수
    max_requests_per_hour: int = 500     # 시간당 최대 요청 수
    respect_robots_txt: bool = True      # robots.txt 준수 여부
    check_terms_of_service: bool = True  # 서비스 약관 확인
    store_minimal_data: bool = True      # 최소한의 데이터만 저장
    enable_rate_limiting: bool = True    # 레이트 리밋 적용
    enable_fair_use: bool = True         # 공정 사용 정책 적용
    
    def wait_for_rate_limit(self):
        """레이트 리밋을 위한 간단한 대기"""
        if self.enable_rate_limiting:
            time.sleep(1.0 / self.max_requests_per_second)

class EthicalScrapingManager:
    """윤리적 스크래핑 관리자"""
    
    def __init__(self, policy: Optional[ScrapingPolicy] = None):
        self.policy = policy or ScrapingPolicy()
        self.logger = logging.getLogger(__name__)
        self.robots_txt_cache: Dict[str, Dict[str, Any]] = {}
        self.request_history: List[datetime] = []
        
    def check_robots_txt(self, url: str, user_agent: str) -> bool:
        """robots.txt 규칙 확인"""
        if not self.policy.respect_robots_txt:
            return True
            
        try:
            domain = urlparse(url).netloc
            if domain not in self.robots_txt_cache:
                robots_url = f"https://{domain}/robots.txt"
                response = requests.get(robots_url, timeout=10)
                if response.status_code == 200:
                    rules = self._parse_robots_txt(response.text)
                    self.robots_txt_cache[domain] = rules
                else:
                    self.robots_txt_cache[domain] = {"allow_all": True}
            
            rules = self.robots_txt_cache[domain]
            if rules.get("allow_all"):
                return True
                
            path = urlparse(url).path
            for disallow in rules.get("disallow", []):
                if path.startswith(disallow):
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.warning(f"robots.txt 확인 중 오류 발생: {str(e)}")
            return True
    
    def _parse_robots_txt(self, content: str) -> Dict[str, Any]:
        """robots.txt 파싱"""
        rules = {"disallow": [], "allow_all": False}
        lines = content.split('\n')
        current_agent = None
        
        for line in lines:
            line = line.strip().lower()
            if not line or line.startswith('#'):
                continue
                
            if line.startswith('user-agent:'):
                agent = line.split(':', 1)[1].strip()
                if agent == '*':
                    current_agent = 'all'
                else:
                    current_agent = agent
            elif current_agent == 'all' and line.startswith('disallow:'):
                path = line.split(':', 1)[1].strip()
                if path:
                    rules["disallow"].append(path)
            elif current_agent == 'all' and line.startswith('allow:'):
                path = line.split(':', 1)[1].strip()
                if not path:
                    rules["allow_all"] = True
        
        return rules
    
    def check_rate_limit(self) -> bool:
        """레이트 리밋 확인"""
        if not self.policy.enable_rate_limiting:
            return True
            
        now = datetime.now()
        self.request_history = [t for t in self.request_history if now - t < timedelta(hours=1)]
        
        # 시간당 제한 확인
        if len(self.request_history) >= self.policy.max_requests_per_hour:
            return False
            
        # 분당 제한 확인
        requests_last_minute = len([t for t in self.request_history if now - t < timedelta(minutes=1)])
        if requests_last_minute >= self.policy.max_requests_per_minute:
            return False
            
        # 초당 제한 확인
        requests_last_second = len([t for t in self.request_history if now - t < timedelta(seconds=1)])
        if requests_last_second >= self.policy.max_requests_per_second:
            return False
            
        return True
    
    def record_request(self) -> None:
        """요청 기록"""
        self.request_history.append(datetime.now())
    
    def apply_fair_use_policy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """공정 사용 정책 적용"""
        if not self.policy.enable_fair_use:
            return data
            
        # 필수 데이터만 유지
        essential_fields = {
            'id', 'title', 'description', 'url', 'timestamp',
            'category', 'price', 'rating', 'review_count'
        }
        
        return {k: v for k, v in data.items() if k in essential_fields}
    
    def get_recommended_delay(self) -> float:
        """권장 지연 시간 계산"""
        if not self.policy.enable_rate_limiting:
            return 0.0
            
        now = datetime.now()
        recent_requests = len([t for t in self.request_history if now - t < timedelta(seconds=10)])
        
        if recent_requests > 0:
            return max(1.0 / self.policy.max_requests_per_second, 
                      60.0 / self.policy.max_requests_per_minute)
        return 0.0
    
    def validate_url(self, url: str) -> bool:
        """URL 유효성 검증"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def log_ethical_violation(self, violation_type: str, details: str) -> None:
        """윤리적 위반 사항 로깅"""
        self.logger.warning(f"윤리적 위반 발생: {violation_type} - {details}") 