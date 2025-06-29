"""
Anti-bot system configuration
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class BrowserConfig:
    """브라우저 설정"""
    viewport_width: int = 1920
    viewport_height: int = 1080
    locale: str = "en-PH"
    timezone: str = "Asia/Manila"
    platform: str = "Windows"
    user_agent_type: str = "desktop"

@dataclass
class ProxyRotationConfig:
    """프록시 로테이션 설정"""
    min_rotation_interval: timedelta = timedelta(minutes=30)
    max_consecutive_failures: int = 3
    blocked_timeout: timedelta = timedelta(hours=1)

@dataclass
class ScrapingBehaviorConfig:
    """스크래핑 동작 설정"""
    min_request_delay: float = 2.0
    max_request_delay: float = 5.0
    min_scroll_delay: float = 1.0
    max_scroll_delay: float = 3.0
    scroll_chunk_size: int = 500
    max_retries: int = 3
    session_duration: int = 300  # seconds

@dataclass
class ErrorHandlingConfig:
    """오류 처리 설정"""
    max_consecutive_errors: int = 5
    error_cooldown: timedelta = timedelta(minutes=15)
    max_daily_errors: int = 100

@dataclass
class AntiBotConfig:
    """안티봇 시스템 통합 설정"""
    browser: BrowserConfig = BrowserConfig()
    proxy_rotation: ProxyRotationConfig = ProxyRotationConfig()
    scraping_behavior: ScrapingBehaviorConfig = ScrapingBehaviorConfig()
    error_handling: ErrorHandlingConfig = ErrorHandlingConfig()
    
    # 봇 감지 패턴
    bot_detection_patterns: List[str] = [
        "captcha",
        "verify",
        "robot",
        "security-check",
        "blocked",
        "challenge"
    ]
    
    # 요청 헤더
    default_headers: Dict[str, str] = {
        "Accept-Language": "en-PH,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    # 차단된 리소스 타입
    blocked_resource_types: List[str] = [
        "image",
        "media",
        "font",
        "stylesheet"
    ]
    
    # 성능 모니터링 설정
    monitoring: Dict[str, Any] = {
        "enabled": True,
        "log_directory": "logs/performance",
        "metrics_interval": 300,  # seconds
        "alert_thresholds": {
            "error_rate": 0.1,
            "block_rate": 0.05,
            "response_time": 5.0
        }
    }

# 기본 설정 인스턴스
default_config = AntiBotConfig() 