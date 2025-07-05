#!/usr/bin/env python3
"""
Enhanced Error Handler for Core 3 Scrapers
핵심 3개 스크래퍼용 강화된 에러 핸들러
"""

import logging
import time
import traceback
from functools import wraps
from typing import Any, Callable

class ScraperErrorHandler:
    """스크래퍼 전용 에러 핸들러"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logging.getLogger('scraper_error_handler')
    
    def retry_with_backoff(self, func: Callable) -> Callable:
        """지수 백오프를 사용한 재시도 데코레이터"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == self.max_retries:
                        self.logger.error(f"❌ Final attempt failed for {func.__name__}: {e}")
                        raise
                    
                    delay = self.base_delay * (2 ** attempt)
                    self.logger.warning(f"⚠️ Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
            
        return wrapper
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> tuple[bool, Any]:
        """안전한 함수 실행"""
        try:
            result = func(*args, **kwargs)
            return True, result
        except Exception as e:
            self.logger.error(f"❌ Safe execution failed for {func.__name__}: {e}")
            self.logger.debug(traceback.format_exc())
            return False, str(e)
    
    def circuit_breaker(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        """서킷 브레이커 패턴"""
        def decorator(func: Callable) -> Callable:
            func._failure_count = 0
            func._last_failure_time = 0
            func._is_open = False
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                current_time = time.time()
                
                # Check if circuit is open and recovery time has passed
                if func._is_open:
                    if current_time - func._last_failure_time > recovery_timeout:
                        func._is_open = False
                        func._failure_count = 0
                        self.logger.info(f"🔄 Circuit breaker reset for {func.__name__}")
                    else:
                        raise Exception(f"Circuit breaker open for {func.__name__}")
                
                try:
                    result = func(*args, **kwargs)
                    func._failure_count = 0  # Reset on success
                    return result
                except Exception as e:
                    func._failure_count += 1
                    func._last_failure_time = current_time
                    
                    if func._failure_count >= failure_threshold:
                        func._is_open = True
                        self.logger.error(f"🚨 Circuit breaker opened for {func.__name__}")
                    
                    raise
            
            return wrapper
        return decorator

# Global error handler instance
error_handler = ScraperErrorHandler()
