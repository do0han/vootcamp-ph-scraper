"""
Error handling module for anti-bot system.
Handles various web scraping errors and implements recovery strategies.
"""
from typing import Optional, Dict, Any, Callable, List
from enum import Enum
import time
import logging
from datetime import datetime
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException
)

class ErrorSeverity(Enum):
    """에러 심각도 레벨"""
    LOW = 1      # 일시적인 문제, 자동 복구 가능
    MEDIUM = 2   # 주의 필요, 복구 시도 가능
    HIGH = 3     # 심각한 문제, 수동 개입 필요
    CRITICAL = 4 # 즉시 중단 필요

class ErrorContext:
    """에러 컨텍스트 정보"""
    def __init__(
        self,
        error: Exception,
        operation: str,
        severity: ErrorSeverity,
        timestamp: datetime = None,
        additional_info: Dict[str, Any] = None
    ):
        self.error = error
        self.operation = operation
        self.severity = severity
        self.timestamp = timestamp or datetime.now()
        self.additional_info = additional_info or {}
        self.recovery_attempts = 0
        self.resolved = False

class ErrorHandler:
    """에러 처리 및 복구 시스템"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.error_history: Dict[str, List[ErrorContext]] = {}
        self.logger = logging.getLogger(__name__)
        
        # 에러 타입별 심각도 매핑
        self.severity_mapping = {
            TimeoutException: ErrorSeverity.LOW,
            StaleElementReferenceException: ErrorSeverity.LOW,
            ElementClickInterceptedException: ErrorSeverity.MEDIUM,
            NoSuchElementException: ErrorSeverity.MEDIUM,
            WebDriverException: ErrorSeverity.HIGH
        }
        
        # 에러 타입별 처리 전략
        self.error_strategies = {
            TimeoutException: self._handle_timeout,
            StaleElementReferenceException: self._handle_stale_element,
            ElementClickInterceptedException: self._handle_intercepted_click,
            NoSuchElementException: self._handle_missing_element,
            WebDriverException: self._handle_webdriver_error
        }
    
    def handle_error(
        self,
        error: Exception,
        operation: str,
        additional_info: Dict[str, Any] = None
    ) -> bool:
        """에러 처리 및 복구 시도"""
        # 에러 컨텍스트 생성
        severity = self.severity_mapping.get(
            type(error),
            ErrorSeverity.HIGH
        )
        context = ErrorContext(
            error=error,
            operation=operation,
            severity=severity,
            additional_info=additional_info
        )
        
        # 에러 이력 기록
        if operation not in self.error_history:
            self.error_history[operation] = []
        self.error_history[operation].append(context)
        
        # 로깅
        self.logger.error(
            f"Error in operation '{operation}': {str(error)}",
            extra={'severity': severity.name}
        )
        
        # 복구 전략 실행
        strategy = self.error_strategies.get(type(error))
        if strategy and context.recovery_attempts < self.max_retries:
            try:
                strategy(context)
                context.resolved = True
                return True
            except Exception as recovery_error:
                self.logger.error(
                    f"Recovery failed for {operation}: {str(recovery_error)}"
                )
                context.recovery_attempts += 1
        
        # 심각도가 CRITICAL이면 즉시 False 반환
        if severity == ErrorSeverity.CRITICAL:
            return False
            
        return context.resolved
    
    def _handle_timeout(self, context: ErrorContext) -> None:
        """타임아웃 에러 처리"""
        time.sleep(2 ** context.recovery_attempts)  # 지수 백오프
    
    def _handle_stale_element(self, context: ErrorContext) -> None:
        """stale element 에러 처리"""
        time.sleep(1)  # 페이지 갱신 대기
    
    def _handle_intercepted_click(self, context: ErrorContext) -> None:
        """클릭 인터셉트 에러 처리"""
        time.sleep(1)  # 페이지 로딩 대기
    
    def _handle_missing_element(self, context: ErrorContext) -> None:
        """요소 미발견 에러 처리"""
        time.sleep(2)  # 페이지 로딩 대기
    
    def _handle_webdriver_error(self, context: ErrorContext) -> None:
        """WebDriver 에러 처리"""
        if context.recovery_attempts >= self.max_retries - 1:
            raise Exception("Maximum WebDriver recovery attempts exceeded")
        time.sleep(5)  # WebDriver 안정화 대기
    
    def get_error_stats(self) -> Dict[str, Any]:
        """에러 통계 정보 반환"""
        stats = {
            'total_errors': 0,
            'resolved_errors': 0,
            'errors_by_severity': {
                severity.name: 0 for severity in ErrorSeverity
            },
            'errors_by_type': {},
            'operation_stats': {}
        }
        
        for operation, errors in self.error_history.items():
            operation_stats = {
                'total': len(errors),
                'resolved': sum(1 for e in errors if e.resolved),
                'by_severity': {
                    severity.name: 0 for severity in ErrorSeverity
                }
            }
            
            for error in errors:
                stats['total_errors'] += 1
                if error.resolved:
                    stats['resolved_errors'] += 1
                
                error_type = type(error.error).__name__
                if error_type not in stats['errors_by_type']:
                    stats['errors_by_type'][error_type] = 0
                stats['errors_by_type'][error_type] += 1
                
                severity_name = error.severity.name
                stats['errors_by_severity'][severity_name] += 1
                operation_stats['by_severity'][severity_name] += 1
            
            stats['operation_stats'][operation] = operation_stats
        
        return stats 