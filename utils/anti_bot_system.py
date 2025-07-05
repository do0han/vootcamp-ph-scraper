"""
Centralized anti-bot system for Vootcamp PH Data Scraper.
Integrates all anti-bot components into a unified system.
"""
from typing import Optional, Dict, Any, Union, Tuple, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
import random
from selenium.common.exceptions import WebDriverException
from playwright.sync_api import sync_playwright, Browser, Page
from fake_useragent import UserAgent
from dataclasses import dataclass
import asyncio
import json

from .anti_bot import AntiBotConfig
from .browser_fingerprint import BrowserFingerprintRandomizer
from .human_behavior import HumanBehaviorSimulator
from .proxy_manager import ProxyManager, ProxyStats
from .proxy_config import ProxyConfig
from .session_manager import SessionManager, SessionData
from .error_handler import ErrorHandler, ErrorContext, ErrorSeverity
from .performance_monitor import PerformanceMonitor, BlockingEvent
from .ethical_scraping import EthicalScrapingManager, ScrapingPolicy
from .fingerprint_randomizer import FingerprintRandomizer
try:
    from ..config.settings import settings
except ImportError:
    # Fallback for when running as script
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from config.settings import settings
from .behavior_simulator import BehaviorSimulator

@dataclass
class ProxyConfig:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None

class AntiBotSystem:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.settings = settings
            self.proxy_manager = ProxyManager(proxies=self.settings.PROXY.PROXY_LIST)
            self.fingerprint_randomizer = FingerprintRandomizer()
            self.behavior_simulator = BehaviorSimulator()
            self.session_start = datetime.now()
            self.request_count = 0
            self.initialized = True
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
            ]
    
    def get_user_agent(self) -> str:
        """랜덤 User-Agent 반환"""
        return random.choice(self.user_agents)

    def get_proxy(self) -> Optional[str]:
        """프록시 URL 반환"""
        return self.proxy_manager.get_proxy()
    
    def prepare_request(self, url: str) -> Dict[str, Any]:
        """요청 전 안티봇 대응 준비"""
        # 세션 유효성 검사
        self._validate_session()
        
        # 프록시 설정
        if self.settings.PROXY.ENABLE_PROXY_ROTATION:
            proxy = self.proxy_manager.get_proxy()
        else:
            proxy = None
            
        # 브라우저 지문 무작위화
        if self.settings.BROWSER.ENABLE_FINGERPRINT_RANDOMIZATION:
            headers = self.fingerprint_randomizer.get_random_headers()
        else:
            headers = self.settings.DEFAULT_HEADERS.copy()
            
        # 인간 행동 시뮬레이션
        if self.settings.BROWSER.ENABLE_BEHAVIOR_SIMULATION:
            delay = self.behavior_simulator.get_next_delay()
        else:
            delay = self.settings.SCRAPING.MIN_REQUEST_DELAY
            
        return {
            'proxy': proxy,
            'headers': headers,
            'delay': delay
        }
    
    def _validate_session(self):
        """세션 상태 검증"""
        # 세션 지속 시간 체크
        session_duration = (datetime.now() - self.session_start).total_seconds()
        if session_duration > self.settings.SCRAPING.MAX_SESSION_DURATION:
            self._reset_session()
            
        # 요청 수 체크
        if self.request_count >= self.settings.SCRAPING.MAX_REQUESTS_PER_SESSION:
            self._reset_session()
    
    def _reset_session(self):
        """세션 초기화"""
        self.session_start = datetime.now()
        self.request_count = 0
        self.proxy_manager.rotate_proxy()
        self.fingerprint_randomizer.reset()
        self.behavior_simulator.reset()
    
    def handle_response(self, response: Any) -> bool:
        """응답 처리 및 봇 감지 확인"""
        self.request_count += 1
        
        # 봇 감지 패턴 확인
        response_text = str(response.text).lower()
        for pattern in self.settings.BOT_DETECTION_PATTERNS:
            if pattern in response_text:
                self._handle_bot_detection()
                return False
        return True
    
    def _handle_bot_detection(self):
        """봇 감지 대응"""
        self.proxy_manager.mark_current_proxy_blocked()
        self._reset_session()

    def _rotate_proxy(self) -> ProxyConfig:
        """프록시를 순환하여 반환합니다."""
        if not self.proxy_manager:
            return None
        
        proxy = self.proxy_manager.get_next_proxy()
        if proxy:
            self.current_proxy = proxy
            return proxy
        
        return None
    
    def _random_delay(self):
        """자연스러운 지연 시간을 생성합니다."""
        delay = random.uniform(2.0, 5.0)
        time.sleep(delay)
    
    def _get_browser_args(self, proxy: Optional[ProxyConfig] = None) -> List[str]:
        """브라우저 시작 인자를 생성합니다."""
        args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-blink-features=AutomationControlledInHeadless',
            f'--window-size={self.browser_fingerprints["viewport"]["width"]},{self.browser_fingerprints["viewport"]["height"]}'
        ]
        
        if proxy:
            proxy_str = f"{proxy.host}:{proxy.port}"
            if proxy.username and proxy.password:
                proxy_str = f"{proxy.username}:{proxy.password}@{proxy_str}"
            args.append(f'--proxy-server={proxy_str}')
        
        return args
    
    def _get_browser_fingerprint(self) -> Dict[str, Any]:
        """실제 브라우저와 유사한 지문을 생성합니다."""
        return {
            "viewport": {
                "width": random.choice([1366, 1440, 1536, 1920, 2560]),
                "height": random.choice([768, 900, 864, 1080, 1440])
            },
            "webgl": {
                "vendor": random.choice([
                    "Google Inc. (NVIDIA)",
                    "Google Inc. (Intel)",
                    "Google Inc. (AMD)",
                    "Apple GPU"
                ]),
                "renderer": random.choice([
                    "ANGLE (NVIDIA GeForce GTX 1660 Direct3D11 vs_5_0 ps_5_0)",
                    "ANGLE (Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
                    "ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)",
                    "Apple M1"
                ])
            },
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            "userAgent": self.user_agent.random,
            "language": random.choice(["en-US", "en-PH", "en-GB", "fil-PH"]),
            "timezone": random.choice([
                "Asia/Manila",
                "Asia/Singapore",
                "Asia/Hong_Kong",
                "Asia/Kuala_Lumpur"
            ]),
            "screen": {
                "width": random.choice([1366, 1440, 1536, 1920, 2560]),
                "height": random.choice([768, 900, 864, 1080, 1440]),
                "colorDepth": 24,
                "pixelDepth": 24
            }
        }

    async def init_browser(self):
        """Playwright 브라우저를 초기화합니다."""
        try:
            playwright = sync_playwright().start()
            proxy = self._rotate_proxy()
            fingerprint = self._get_browser_fingerprint()
            
            browser_args = self._get_browser_args(proxy)
            browser_args.extend([
                f"--lang={fingerprint['language']}",
                "--disable-blink-features=AutomationControlled",
                "--disable-blink-features=AutomationControlledInHeadless"
            ])
            
            self.browser = playwright.chromium.launch(
                headless=True,
                args=browser_args
            )
            
            context = self.browser.new_context(
                viewport=fingerprint["viewport"],
                user_agent=fingerprint["userAgent"],
                locale=fingerprint["language"],
                timezone_id=fingerprint["timezone"],
                screen=fingerprint["screen"]
            )
            
            self.page = context.new_page()
            
            # WebGL 지문 설정
            await self.page.add_init_script(f"""
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    if (parameter === 37445) {{
                        return "{fingerprint['webgl']['vendor']}";
                    }}
                    if (parameter === 37446) {{
                        return "{fingerprint['webgl']['renderer']}";
                    }}
                    return getParameter.apply(this, arguments);
                }};
            """)
            
            # 자동화 감지 방지
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            """)
            
            return self.page
            
        except Exception as e:
            logger.error(f"브라우저 초기화 실패: {e}")
            raise
    
    async def close_browser(self):
        """브라우저를 종료합니다."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
    
    def add_proxy(self, proxy: ProxyConfig):
        """프록시를 추가합니다."""
        self.proxy_manager.add_proxy(proxy)
    
    def clear_proxies(self):
        """프록시 목록을 초기화합니다."""
        self.proxy_manager.clear_proxies()
    
    async def get_page_with_retry(self, url: str) -> Optional[str]:
        """페이지를 가져오는 시도를 여러 번 합니다."""
        for attempt in range(3):
            try:
                await self.page.goto(url)
                self._random_delay()
                
                # 봇 감지 체크
                if await self._is_bot_detected():
                    logger.warning(f"봇 감지됨 (시도 {attempt + 1}/3)")
                    await self._handle_bot_detection()
                    continue
                
                return await self.page.content()
                
            except Exception as e:
                logger.error(f"페이지 로드 실패 (시도 {attempt + 1}/3): {e}")
                if attempt < 2:
                    await self._handle_error()
                    continue
        
        return None
    
    async def _is_bot_detected(self) -> bool:
        """봇 감지 여부를 확인합니다."""
        try:
            # Shopee의 봇 감지 패턴 확인
            bot_indicators = [
                "captcha",
                "verify",
                "robot",
                "security-check",
                "blocked",
                "challenge"
            ]
            
            # URL 체크
            current_url = self.page.url
            if any(indicator in current_url.lower() for indicator in bot_indicators):
                return True
            
            # 페이지 내용 체크
            content = await self.page.content()
            if any(indicator in content.lower() for indicator in bot_indicators):
                return True
            
            # 특정 요소 체크
            for indicator in bot_indicators:
                element = await self.page.query_selector(f"[class*='{indicator}'], [id*='{indicator}']")
                if element:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"봇 감지 확인 중 오류 발생: {e}")
            return True  # 안전을 위해 True 반환
    
    async def _handle_error(self, error: Exception) -> bool:
        """에러 처리 및 복구를 시도합니다."""
        try:
            error_type = type(error).__name__
            logger.error(f"에러 발생: {error_type} - {str(error)}")
            
            # 에러 유형별 처리
            if error_type in ["TimeoutError", "NetworkError"]:
                await self._handle_network_error()
            elif "Captcha" in str(error) or "Security" in str(error):
                await self._handle_captcha_error()
            elif "Blocked" in str(error) or "Access Denied" in str(error):
                await self._handle_blocking_error()
            else:
                await self._handle_general_error()
                
            return True
            
        except Exception as e:
            logger.error(f"에러 처리 중 추가 오류 발생: {e}")
            return False
            
    async def _handle_network_error(self):
        """네트워크 관련 에러 처리"""
        # 연결 재시도
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                await asyncio.sleep(random.uniform(5, 10))
                await self.page.reload()
                return
            except Exception:
                retry_count += 1
                
        # 프록시 변경
        if self.proxy_manager:
            await self._rotate_proxy()
            
    async def _handle_captcha_error(self):
        """캡차 발생 시 처리"""
        # 브라우저 재시작
        await self.close_browser()
        await asyncio.sleep(random.uniform(30, 60))
        
        # 새로운 브라우저 지문 생성
        self._browser_fingerprint = self._get_browser_fingerprint()
        
        # 브라우저 재시작
        await self.init_browser()
        
    async def _handle_blocking_error(self):
        """차단 발생 시 처리"""
        # 현재 세션 정보 저장
        self._save_blocked_session_info()
        
        # 프록시 변경
        if self.proxy_manager:
            await self._rotate_proxy()
            
        # 쿠키 및 캐시 삭제
        await self._clear_browser_data()
        
        # 더 긴 대기 시간 적용
        await asyncio.sleep(random.uniform(180, 300))
        
    async def _handle_general_error(self):
        """일반적인 에러 처리"""
        await asyncio.sleep(random.uniform(10, 20))
        await self.page.reload()
        
    async def _clear_browser_data(self):
        """브라우저 데이터 삭제"""
        try:
            await self.page.evaluate("""() => {
                localStorage.clear();
                sessionStorage.clear();
                document.cookie.split(";").forEach(function(c) {
                    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
                });
            }""")
        except Exception as e:
            logger.error(f"브라우저 데이터 삭제 중 오류: {e}")
            
    def _save_blocked_session_info(self):
        """차단된 세션 정보 저장"""
        blocked_info = {
            "timestamp": datetime.now().isoformat(),
            "proxy": self.current_proxy,
            "user_agent": self.page.evaluate("() => navigator.userAgent"),
            "url": self.page.url
        }
        
        # 파일에 저장
        with open("blocked_sessions.json", "a") as f:
            json.dump(blocked_info, f)
            f.write("\n")
        
    def setup_browser(self) -> WebDriver:
        """브라우저 설정"""
        try:
            # 새로운 세션 설정
            self.current_user_agent = self.fingerprint_randomizer.generate_user_agent()
            self.current_proxy = self.proxy_manager.get_proxy().get_url() if self.proxy_manager else None
            
            start_time = self.performance_monitor.start_request(
                user_agent=self.current_user_agent,
                proxy=self.current_proxy
            )
            
            options = Options()
            if self.config.ENABLE_FINGERPRINT_RANDOMIZATION:
                self.current_fingerprint = self.fingerprint_randomizer.generate_fingerprint()
                # 브라우저 지문 설정 적용
                for key, value in self.current_fingerprint.items():
                    options.add_argument(f'--{key}={value}')
                options.add_argument(f'user-agent={self.current_user_agent}')
            
            if self.current_proxy:
                options.add_argument(f'--proxy-server={self.current_proxy}')
            
            driver = webdriver.Chrome(options=options)
            
            self.performance_monitor.end_request(
                start_time,
                success=True,
                user_agent=self.current_user_agent,
                proxy=self.current_proxy
            )
            return driver
            
        except Exception as e:
            self.performance_monitor.end_request(
                start_time,
                success=False,
                user_agent=self.current_user_agent,
                proxy=self.current_proxy
            )
            error_context = ErrorContext(
                error=e,
                timestamp=datetime.now(),
                action="setup_browser"
            )
            self.error_handler.handle_error(error_context)
            self._handle_blocking_event("browser_setup_error", "", e)
            raise
    
    def can_scrape_url(self, url: str) -> bool:
        """URL 스크래핑 가능 여부 확인"""
        if not self.ethical_manager.validate_url(url):
            self.ethical_manager.log_ethical_violation("invalid_url", f"유효하지 않은 URL: {url}")
            return False
            
        if not self.ethical_manager.check_robots_txt(url, self.current_user_agent):
            self.ethical_manager.log_ethical_violation("robots_txt_violation", f"robots.txt 위반: {url}")
            return False
            
        if not self.ethical_manager.check_rate_limit():
            self.ethical_manager.log_ethical_violation("rate_limit_violation", f"레이트 리밋 초과: {url}")
            return False
            
        return True
    
    def perform_action(self, action_type: str, element: Optional[WebElement] = None,
                      url: str = "", **kwargs) -> None:
        """사용자 행동 수행"""
        try:
            # 윤리적 검사
            if url and not self.can_scrape_url(url):
                raise ValueError(f"윤리적 제한으로 인해 {url} 스크래핑이 불가능합니다.")
            
            # 권장 지연 시간 적용
            delay = self.ethical_manager.get_recommended_delay()
            if delay > 0:
                time.sleep(delay)
            
            start_time = self.performance_monitor.start_request(
                user_agent=self.current_user_agent,
                proxy=self.current_proxy
            )
            
            if action_type == "click":
                self.behavior_simulator.human_like_click(element)
            elif action_type == "type":
                self.behavior_simulator.human_like_type(element, kwargs.get("text", ""))
            elif action_type == "scroll":
                self.behavior_simulator.human_like_scroll(kwargs.get("driver"), kwargs.get("distance"))
            
            # 요청 기록
            self.ethical_manager.record_request()
            
            self.performance_monitor.end_request(
                start_time,
                success=True,
                user_agent=self.current_user_agent,
                proxy=self.current_proxy
            )
            
        except Exception as e:
            self.performance_monitor.end_request(
                start_time,
                success=False,
                user_agent=self.current_user_agent,
                proxy=self.current_proxy
            )
            error_context = ErrorContext(
                error=e,
                timestamp=datetime.now(),
                action=f"perform_action_{action_type}"
            )
            self.error_handler.handle_error(error_context)
            self._handle_blocking_event(f"{action_type}_error", url, e)
            raise
    
    def process_scraped_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """스크래핑된 데이터 처리"""
        return self.ethical_manager.apply_fair_use_policy(data)
    
    def _handle_blocking_event(self, error_type: str, url: str, error: Exception) -> None:
        """차단 이벤트 처리"""
        if not self.current_user_agent or not url:
            return
            
        # 차단 이벤트 기록
        self.performance_monitor.record_blocking_event(
            error_type=error_type,
            url=url,
            user_agent=self.current_user_agent,
            proxy=self.current_proxy
        )
        
        # 복구 시도
        recovery_start = time.time()
        success = self._attempt_recovery(error_type)
        recovery_time = time.time() - recovery_start
        
        # 복구 시도 기록
        latest_event = self.performance_monitor.metrics.blocking_events[-1]
        self.performance_monitor.record_recovery_attempt(
            event=latest_event,
            success=success,
            recovery_time=recovery_time
        )
    
    def _attempt_recovery(self, error_type: str) -> bool:
        """차단 복구 시도"""
        try:
            if 'captcha' in error_type.lower():
                # 캡차 발생 시 세션 재생성
                self.session_manager.create_new_session()
                time.sleep(random.uniform(30, 60))  # 캡차 후 대기
            elif 'rate' in error_type.lower():
                # 레이트 리밋 시 대기 시간 증가
                time.sleep(random.uniform(60, 120))
            elif 'ip' in error_type.lower() and self.proxy_manager:
                # IP 차단 시 프록시 변경
                self.current_proxy = self.proxy_manager.get_proxy().get_url()
                self.current_user_agent = self.fingerprint_randomizer.generate_user_agent()
            
            return True
        except Exception as e:
            logger.error(f"Recovery attempt failed: {str(e)}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        return self.performance_monitor.get_metrics_summary()
    
    def save_performance_metrics(self) -> None:
        """성능 메트릭 저장"""
        self.performance_monitor.save_metrics()
    
    def cleanup(self) -> None:
        """시스템 정리"""
        try:
            if self.proxy_manager:
                self.proxy_manager.cleanup()
            if self.session_manager:
                self.session_manager.cleanup()
            self.save_performance_metrics()
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            raise 

    async def _handle_request(self, route):
        """요청을 처리하고 필터링합니다."""
        try:
            request = route.request
            
            # 리소스 타입 필터링
            if request.resource_type in ["image", "media", "font", "other"]:
                await route.abort()
                return
                
            # 요청 헤더 수정
            headers = {
                **request.headers,
                "Accept-Language": "en-PH,en;q=0.9,fil;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
                "sec-ch-ua-platform": "Windows",
                "sec-ch-ua-mobile": "?0",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
            
            # 요청 타이밍 제어
            await self._control_request_timing()
            
            # 요청 전송
            await route.continue_(headers=headers)
            
        except Exception as e:
            logger.error(f"요청 처리 중 오류 발생: {e}")
            await route.abort()
            
    async def _control_request_timing(self):
        """요청 타이밍을 자연스럽게 제어합니다."""
        # 기본 지연 시간
        delay = random.uniform(2.0, 5.0)
        
        # 시간대별 지연 시간 조정
        hour = datetime.now().hour
        if 0 <= hour < 6:  # 새벽
            delay *= 1.5
        elif 6 <= hour < 9:  # 아침
            delay *= 0.8
        elif 17 <= hour < 22:  # 저녁
            delay *= 0.7
            
        # 이전 요청과의 간격 확인
        if hasattr(self, '_last_request_time'):
            time_since_last = (datetime.now() - self._last_request_time).total_seconds()
            if time_since_last < 1:
                delay += random.uniform(1, 2)
                
        self._last_request_time = datetime.now()
        await asyncio.sleep(delay)
        
    async def _add_human_behavior(self):
        """인간과 유사한 행동 패턴을 추가합니다."""
        try:
            # 랜덤한 마우스 움직임
            await self._random_mouse_movement()
            
            # 랜덤한 스크롤
            await self._random_scroll()
            
            # 랜덤한 지연 시간
            await self._random_delay()
            
        except Exception as e:
            logger.error(f"인간 행동 패턴 추가 중 오류: {e}")
            
    async def _random_mouse_movement(self):
        """랜덤한 마우스 움직임을 생성합니다."""
        try:
            # 페이지 크기 가져오기
            page_dimensions = await self.page.evaluate("""() => {
                return {
                    width: document.documentElement.clientWidth,
                    height: document.documentElement.clientHeight
                }
            }""")
            
            # 랜덤한 위치로 마우스 이동
            for _ in range(random.randint(2, 5)):
                x = random.randint(0, page_dimensions["width"])
                y = random.randint(0, page_dimensions["height"])
                
                # 자연스러운 마우스 이동
                await self.page.mouse.move(x, y, steps=random.randint(10, 20))
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
        except Exception as e:
            logger.error(f"마우스 움직임 생성 중 오류: {e}")
            
    async def _random_scroll(self):
        """자연스러운 스크롤 동작을 수행합니다."""
        try:
            # 페이지 높이 가져오기
            total_height = await self.page.evaluate("document.body.scrollHeight")
            viewport_height = await self.page.evaluate("window.innerHeight")
            
            current_position = 0
            while current_position < total_height:
                # 스크롤 거리 계산
                scroll_amount = random.randint(100, 300)
                current_position = min(current_position + scroll_amount, total_height)
                
                # 스크롤 수행
                await self.page.evaluate(f"window.scrollTo(0, {current_position})")
                
                # 자연스러운 지연
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                # 가끔 위로 스크롤
                if random.random() < 0.1:
                    up_amount = random.randint(50, 200)
                    current_position = max(0, current_position - up_amount)
                    await self.page.evaluate(f"window.scrollTo(0, {current_position})")
                    await asyncio.sleep(random.uniform(0.3, 0.7))
                    
        except Exception as e:
            logger.error(f"스크롤 동작 수행 중 오류: {e}")
            
    async def _random_delay(self):
        """자연스러운 지연 시간을 생성합니다."""
        # 기본 지연 시간
        base_delay = random.uniform(2.0, 5.0)
        
        # 추가 랜덤 지연 (10% 확률)
        if random.random() < 0.1:
            additional_delay = random.uniform(2, 5)
            base_delay += additional_delay
            
        await asyncio.sleep(base_delay)
        
    async def _simulate_human_typing(self, text: str):
        """인간과 유사한 타이핑 패턴을 시뮬레이션합니다."""
        for char in text:
            # 각 문자 입력 사이의 지연 시간
            delay = random.uniform(0.1, 0.3)
            
            # 특수 문자나 대문자의 경우 추가 지연
            if not char.isalnum() or char.isupper():
                delay += random.uniform(0.1, 0.2)
                
            # 가끔 오타를 내고 수정 (5% 확률)
            if random.random() < 0.05:
                wrong_char = random.choice("qwertyuiop")
                await self.page.keyboard.press(wrong_char)
                await asyncio.sleep(random.uniform(0.2, 0.4))
                await self.page.keyboard.press("Backspace")
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
            await self.page.keyboard.press(char)
            await asyncio.sleep(delay)

    async def apply_delay(self):
        """요청 간 딜레이 적용"""
        delay = random.uniform(2.0, 5.0)
        await asyncio.sleep(delay)

    def get_headers(self) -> Dict[str, str]:
        """HTTP 헤더 생성"""
        return {
            "User-Agent": self.get_user_agent(),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

    def report_success(self, proxy: str):
        """프록시 성공 보고"""
        self.proxy_manager.report_success(proxy)

    def report_failure(self, proxy: str):
        """프록시 실패 보고"""
        self.proxy_manager.report_failure(proxy) 