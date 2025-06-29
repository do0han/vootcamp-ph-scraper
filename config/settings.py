"""
Centralized configuration for Vootcamp PH Data Scraper
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import timedelta

@dataclass
class ProxyConfig:
    """프록시 설정"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    PROXY_LIST: List[str] = field(default_factory=lambda: [
        "http://103.148.72.126:80",  # Philippines proxy
        "http://103.148.72.192:80",  # Philippines proxy
        "http://103.148.72.193:80"   # Philippines proxy
    ])

@dataclass
class BrowserConfig:
    """브라우저 설정"""
    ENABLE_FINGERPRINT_RANDOMIZATION: bool = True
    ENABLE_BEHAVIOR_SIMULATION: bool = True
    USER_AGENTS: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ])
    DEFAULT_HEADERS: Dict[str, str] = field(default_factory=lambda: {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    })
    BLOCKED_RESOURCE_TYPES: List[str] = field(default_factory=lambda: [
        "image",
        "media",
        "font",
        "texttrack",
        "object",
        "beacon",
        "csp_report",
        "imageset"
    ])

@dataclass
class ProxyRotationConfig:
    """프록시 로테이션 설정"""
    ENABLE_PROXY_ROTATION: bool = True
    MIN_ROTATION_INTERVAL: timedelta = timedelta(minutes=30)
    MAX_CONSECUTIVE_FAILURES: int = 3
    BLOCKED_TIMEOUT: timedelta = timedelta(hours=1)

@dataclass
class AntiBotConfig:
    """안티봇 시스템 설정"""
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 5
    REQUEST_TIMEOUT: int = 30
    BOT_DETECTION_PATTERNS: List[str] = field(default_factory=lambda: [
        "captcha",
        "verify",
        "security check",
        "bot detected"
    ])
    BLOCKED_RESPONSE_CODES: List[int] = field(default_factory=lambda: [403, 429, 503])

@dataclass
class ScrapingConfig:
    """스크래핑 정책 설정"""
    MIN_REQUEST_INTERVAL: float = 1.0
    MAX_REQUESTS_PER_MINUTE: int = 30
    RESPECT_ROBOTS_TXT: bool = True
    USER_ACTIVITY_PATTERNS: Dict[str, List[float]] = field(default_factory=lambda: {
        "morning": [0.5, 1.5],
        "afternoon": [1.0, 2.0],
        "evening": [1.5, 2.5],
        "night": [2.0, 3.0]
    })

@dataclass
class MonitoringConfig:
    """성능 모니터링 설정"""
    ENABLE_LOGGING: bool = True
    LOG_LEVEL: str = "INFO"
    METRICS: Dict[str, Any] = field(default_factory=lambda: {
        "request_count": 0,
        "success_rate": 0.0,
        "average_response_time": 0.0,
        "blocked_requests": 0,
        "proxy_switches": 0
    })

@dataclass
class Settings:
    """전체 설정"""
    PROXY: ProxyConfig = field(default_factory=lambda: ProxyConfig(
        host="proxy.example.com",
        port=8080
    ))
    BROWSER: BrowserConfig = field(default_factory=lambda: BrowserConfig())
    ANTI_BOT: AntiBotConfig = field(default_factory=lambda: AntiBotConfig())
    SCRAPING: ScrapingConfig = field(default_factory=lambda: ScrapingConfig())
    MONITORING: MonitoringConfig = field(default_factory=lambda: MonitoringConfig())

# 전역 설정 인스턴스
settings = Settings() 