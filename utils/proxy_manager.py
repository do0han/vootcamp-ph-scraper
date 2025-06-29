"""
프록시 관리 및 로테이션
"""

import logging
import random
from typing import List, Optional, Dict, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlparse
from .proxy_config import ProxyConfig

logger = logging.getLogger(__name__)

@dataclass
class ProxyStats:
    """프록시 통계"""
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    blocked_until: Optional[datetime] = None

class ProxyManager:
    """프록시 관리"""
    
    def __init__(self, proxies: List[Union[str, ProxyConfig]]):
        """
        프록시 매니저 초기화
        
        Args:
            proxies: 프록시 설정 목록 (URL 문자열 또는 ProxyConfig 객체)
        """
        self.proxies = []
        for proxy in proxies:
            if isinstance(proxy, str):
                parsed = urlparse(proxy)
                self.proxies.append(ProxyConfig(
                    host=parsed.hostname or "",
                    port=parsed.port or 80
                ))
            else:
                self.proxies.append(proxy)
                
        self.current_index = 0
        self.last_rotation = datetime.now()
        self.proxy_stats = {}
        self.max_consecutive_failures = 3
        self.min_rotation_interval = timedelta(seconds=5)
        self.blocked_timeout = timedelta(minutes=5)
        
        # 프록시 통계 초기화
        for proxy in self.proxies:
            proxy_id = self._get_proxy_id(proxy)
            self.proxy_stats[proxy_id] = {
                "success_count": 0,
                "error_count": 0,
                "last_used": None,
                "blocked_until": None,
                "total_requests": 0,
                "average_response_time": 0.0
            }
    
    def _get_proxy_id(self, proxy: Union[str, ProxyConfig]) -> str:
        """프록시 식별자 생성"""
        if isinstance(proxy, str):
            parsed = urlparse(proxy)
            return f"{parsed.hostname or ''}:{parsed.port or 80}"
        else:
            return f"{proxy.host}:{proxy.port}"
    
    def _is_proxy_available(self, proxy: Union[str, ProxyConfig]) -> bool:
        """프록시 사용 가능 여부 확인"""
        proxy_id = self._get_proxy_id(proxy)
        stats = self.proxy_stats[proxy_id]
        
        # 차단된 프록시 확인
        if stats["blocked_until"] and datetime.now() < stats["blocked_until"]:
            return False
            
        # 연속 실패 횟수 확인
        if stats["error_count"] >= self.max_consecutive_failures:
            return False
            
        # 최소 로테이션 간격 확인
        if (stats["last_used"] and 
            datetime.now() - stats["last_used"] < self.min_rotation_interval):
            return False
            
        return True
    
    def get_next_proxy(self) -> Optional[Union[str, ProxyConfig]]:
        """다음 사용 가능한 프록시 반환"""
        attempts = 0
        max_attempts = len(self.proxies)
        
        while attempts < max_attempts:
            self.current_index = (self.current_index + 1) % len(self.proxies)
            proxy = self.proxies[self.current_index]
            
            if self._is_proxy_available(proxy):
                proxy_id = self._get_proxy_id(proxy)
                self.proxy_stats[proxy_id]["last_used"] = datetime.now()
                return proxy
                
            attempts += 1
            
        logger.warning("사용 가능한 프록시가 없습니다.")
        return None
    
    def report_success(self, proxy: Union[str, ProxyConfig]):
        """프록시 성공 보고"""
        proxy_id = self._get_proxy_id(proxy)
        stats = self.proxy_stats[proxy_id]
        stats["success_count"] += 1
        stats["error_count"] = 0  # 연속 실패 카운트 리셋
    
    def report_failure(self, proxy: Union[str, ProxyConfig], is_blocked: bool = False):
        """프록시 실패 보고"""
        proxy_id = self._get_proxy_id(proxy)
        stats = self.proxy_stats[proxy_id]
        stats["error_count"] += 1
        stats["last_failure"] = datetime.now()
        
        if is_blocked or stats["error_count"] >= self.max_consecutive_failures:
            stats["blocked_until"] = datetime.now() + self.blocked_timeout
            logger.warning(f"프록시 차단됨: {proxy_id}, 차단 해제: {stats['blocked_until']}")
    
    def get_proxy_stats(self) -> Dict[str, Dict]:
        """프록시 통계 반환"""
        return self.proxy_stats 