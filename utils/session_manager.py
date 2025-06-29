"""
Session management utility for anti-bot system.
"""
from typing import Dict, Any, Optional, List
import time
from dataclasses import dataclass
import json
import os
import logging
from datetime import datetime, timedelta
import uuid
from selenium.webdriver.remote.webdriver import WebDriver

@dataclass
class SessionData:
    """세션 데이터"""
    session_id: str
    start_time: datetime
    last_activity: datetime
    request_count: int
    cookies: Dict[str, str]
    user_agent: str
    proxy: Optional[str] = None
    browser_fingerprint: Optional[Dict[str, Any]] = None
    performance_metrics: Dict[str, float] = None
    
    @property
    def session_age(self) -> timedelta:
        """세션 수명"""
        return datetime.now() - self.start_time
    
    @property
    def idle_time(self) -> timedelta:
        """마지막 활동 이후 경과 시간"""
        return datetime.now() - self.last_activity
    
    @property
    def requests_per_minute(self) -> float:
        """분당 요청 수"""
        minutes = self.session_age.total_seconds() / 60
        return self.request_count / minutes if minutes > 0 else 0

class SessionManager:
    """세션 관리 시스템"""
    
    def __init__(self, max_session_duration: int = 1800,
                 max_requests_per_session: int = 1000,
                 max_idle_time: int = 300):
        self.max_session_duration = max_session_duration  # 30분
        self.max_requests_per_session = max_requests_per_session
        self.max_idle_time = max_idle_time  # 5분
        self.sessions: Dict[str, SessionData] = {}
        self.logger = logging.getLogger(__name__)
        
    def create_session(self, user_agent: str, proxy: Optional[str] = None,
                      browser_fingerprint: Optional[Dict[str, Any]] = None) -> SessionData:
        """새 세션 생성"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = SessionData(
            session_id=session_id,
            start_time=now,
            last_activity=now,
            request_count=0,
            cookies={},
            user_agent=user_agent,
            proxy=proxy,
            browser_fingerprint=browser_fingerprint,
            performance_metrics={
                'average_response_time': 0.0,
                'total_response_time': 0.0,
                'min_response_time': float('inf'),
                'max_response_time': 0.0
            }
        )
        
        self.sessions[session_id] = session
        self.logger.info(f"새 세션 생성: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """세션 조회"""
        return self.sessions.get(session_id)
    
    def update_session_activity(self, session_id: str,
                              response_time: Optional[float] = None) -> None:
        """세션 활동 업데이트"""
        session = self.sessions.get(session_id)
        if not session:
            return
            
        session.last_activity = datetime.now()
        session.request_count += 1
        
        if response_time is not None:
            metrics = session.performance_metrics
            metrics['total_response_time'] += response_time
            metrics['average_response_time'] = (
                metrics['total_response_time'] / session.request_count
            )
            metrics['min_response_time'] = min(
                metrics['min_response_time'],
                response_time
            )
            metrics['max_response_time'] = max(
                metrics['max_response_time'],
                response_time
            )
    
    def update_session_cookies(self, session_id: str,
                             cookies: Dict[str, str]) -> None:
        """세션 쿠키 업데이트"""
        session = self.sessions.get(session_id)
        if session:
            session.cookies.update(cookies)
    
    def should_rotate_session(self, session_id: str) -> bool:
        """세션 교체가 필요한지 확인"""
        session = self.sessions.get(session_id)
        if not session:
            return True
            
        # 세션 수명 초과
        if session.session_age.total_seconds() >= self.max_session_duration:
            self.logger.info(f"세션 {session_id} 수명 초과")
            return True
            
        # 요청 수 초과
        if session.request_count >= self.max_requests_per_session:
            self.logger.info(f"세션 {session_id} 최대 요청 수 초과")
            return True
            
        # 장시간 미사용
        if session.idle_time.total_seconds() >= self.max_idle_time:
            self.logger.info(f"세션 {session_id} 장시간 미사용")
            return True
            
        return False
    
    def apply_session_to_driver(self, session_id: str,
                              driver: WebDriver) -> None:
        """세션 정보를 웹드라이버에 적용"""
        session = self.sessions.get(session_id)
        if not session:
            return
            
        # 쿠키 설정
        for name, value in session.cookies.items():
            driver.add_cookie({'name': name, 'value': value})
            
        # User-Agent 설정
        driver.execute_cdp_cmd('Network.setUserAgentOverride',
                             {"userAgent": session.user_agent})
            
        # 브라우저 지문 설정
        if session.browser_fingerprint:
            driver.execute_cdp_cmd('Page.setBypassCSP', {"enabled": True})
            driver.execute_script("""
                const fingerprint = arguments[0];
                Object.defineProperty(navigator, 'platform', {
                    get: () => fingerprint.platform
                });
                Object.defineProperty(navigator, 'userAgent', {
                    get: () => fingerprint.userAgent
                });
                Object.defineProperty(screen, 'width', {
                    get: () => fingerprint.screenWidth
                });
                Object.defineProperty(screen, 'height', {
                    get: () => fingerprint.screenHeight
                });
            """, session.browser_fingerprint)
    
    def get_session_stats(self) -> Dict[str, Dict[str, Any]]:
        """모든 세션의 통계 정보 반환"""
        stats = {}
        for session_id, session in self.sessions.items():
            stats[session_id] = {
                'age': session.session_age.total_seconds(),
                'idle_time': session.idle_time.total_seconds(),
                'request_count': session.request_count,
                'requests_per_minute': session.requests_per_minute,
                'performance_metrics': session.performance_metrics
            }
        return stats
    
    def cleanup_expired_sessions(self) -> None:
        """만료된 세션 정리"""
        expired_sessions = [
            session_id for session_id in self.sessions
            if self.should_rotate_session(session_id)
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            self.logger.info(f"만료된 세션 제거: {session_id}")
    
    def get_active_sessions_count(self) -> int:
        """활성 세션 수 반환"""
        return len(self.sessions)

    def save_sessions(self, filepath: str) -> None:
        """세션 저장"""
        sessions_data = {
            sid: {
                "session_id": s.session_id,
                "start_time": s.start_time.isoformat(),
                "last_activity": s.last_activity.isoformat(),
                "request_count": s.request_count,
                "cookies": s.cookies,
                "user_agent": s.user_agent,
                "proxy": s.proxy,
                "browser_fingerprint": s.browser_fingerprint,
                "performance_metrics": s.performance_metrics
            }
            for sid, s in self.sessions.items()
        }
        
        with open(filepath, 'w') as f:
            json.dump(sessions_data, f, indent=2)
            
    def load_sessions(self, filepath: str) -> None:
        """세션 로드"""
        if not os.path.exists(filepath):
            return
            
        with open(filepath, 'r') as f:
            sessions_data = json.load(f)
            
        for sid, data in sessions_data.items():
            self.sessions[sid] = SessionData(
                session_id=data['session_id'],
                start_time=datetime.fromisoformat(data['start_time']),
                last_activity=datetime.fromisoformat(data['last_activity']),
                request_count=data['request_count'],
                cookies=data['cookies'],
                user_agent=data['user_agent'],
                proxy=data['proxy'],
                browser_fingerprint=data['browser_fingerprint'],
                performance_metrics=data['performance_metrics']
            ) 