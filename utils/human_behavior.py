"""
Human behavior simulation module for anti-bot system.
Simulates human-like interactions with web elements.
"""
from typing import Optional, Tuple, List, Dict
import time
import random
import numpy as np
from datetime import datetime, timedelta
from collections import deque
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
import asyncio

class HumanBehaviorSimulator:
    """사람과 유사한 웹 상호작용을 시뮬레이션하는 클래스"""
    
    def __init__(self, min_delay: float = 0.1, max_delay: float = 2.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.request_history = deque(maxlen=100)  # Store last 100 requests
        self.session_start = datetime.now()
        self.last_burst_time = datetime.now()
        self.burst_count = 0
        self.max_burst_size = 5
        
        # Time-of-day patterns (multipliers)
        self.time_patterns = {
            "early_morning": (0, 6, 1.5),    # 12AM-6AM: 50% slower
            "morning_rush": (6, 9, 0.8),     # 6AM-9AM: 20% faster
            "work_hours": (9, 17, 1.0),      # 9AM-5PM: normal
            "evening_rush": (17, 22, 0.7),   # 5PM-10PM: 30% faster
            "late_night": (22, 24, 1.3),     # 10PM-12AM: 30% slower
        }
        
        # Activity burst patterns
        self.burst_patterns = {
            "quick_browse": {"duration": 30, "intensity": 0.7},
            "deep_dive": {"duration": 120, "intensity": 1.2},
            "casual_scroll": {"duration": 60, "intensity": 0.9}
        }
    
    def get_time_multiplier(self) -> float:
        """Get delay multiplier based on time of day"""
        current_hour = datetime.now().hour
        
        for _, (start, end, multiplier) in self.time_patterns.items():
            if start <= current_hour < end:
                # Add small random variation to multiplier
                variation = random.uniform(-0.1, 0.1)
                return multiplier + variation
                
        return 1.0
    
    def should_start_burst(self) -> bool:
        """Determine if we should start a burst of activity"""
        if self.burst_count >= self.max_burst_size:
            return False
            
        time_since_last = (datetime.now() - self.last_burst_time).total_seconds()
        if time_since_last < 300:  # Minimum 5 minutes between bursts
            return False
            
        return random.random() < 0.2  # 20% chance of starting a burst
    
    def get_burst_delay(self) -> float:
        """Get delay during activity burst"""
        pattern = random.choice(list(self.burst_patterns.values()))
        base_delay = random.uniform(self.min_delay, self.max_delay)
        return base_delay * pattern["intensity"]
    
    def update_request_history(self, delay: float):
        """Update request timing history"""
        self.request_history.append({
            "timestamp": datetime.now(),
            "delay": delay
        })
    
    def get_natural_delay(self) -> float:
        """Generate natural delay based on patterns and history"""
        # Get base delay
        base_delay = random.uniform(self.min_delay, self.max_delay)
        
        # Apply time-of-day pattern
        time_multiplier = self.get_time_multiplier()
        delay = base_delay * time_multiplier
        
        # Check for activity burst
        if self.should_start_burst():
            self.burst_count += 1
            self.last_burst_time = datetime.now()
            delay = self.get_burst_delay()
        elif self.burst_count > 0:
            # Gradually return to normal delays
            self.burst_count = max(0, self.burst_count - 1)
            
        # Consider request history
        if len(self.request_history) > 0:
            last_request = self.request_history[-1]
            time_since_last = (datetime.now() - last_request["timestamp"]).total_seconds()
            
            # Avoid too quick successive requests
            if time_since_last < 1:
                delay += random.uniform(1, 2)
            
            # Add natural variance based on recent history
            if len(self.request_history) >= 3:
                recent_delays = [r["delay"] for r in list(self.request_history)[-3:]]
                avg_delay = sum(recent_delays) / len(recent_delays)
                variance = random.uniform(-0.2, 0.2) * avg_delay
                delay += variance
        
        # Update history
        self.update_request_history(delay)
        
        return max(self.min_delay, min(self.max_delay * 2, delay))
    
    def human_like_delay(self) -> None:
        """Apply human-like delay"""
        delay = self.get_natural_delay()
        time.sleep(delay)
    
    def human_like_click(self, element: WebElement) -> None:
        """Simulate human-like click with natural mouse movement"""
        if not element.is_displayed():
            return
            
        # Natural pre-click pause
        self.human_like_delay()
        
        # Click with potential double-click mistake (0.5% chance)
        element.click()
        if random.random() < 0.005:
            time.sleep(random.uniform(0.1, 0.2))
            element.click()
            time.sleep(random.uniform(0.2, 0.3))
            # Correct "mistake" with opposite action
            element.click()
        
        # Post-click pause
        self.human_like_delay()
    
    async def simulate_typing(self, element: WebElement, text: str):
        """
        사람다운 타이핑 시뮬레이션
        
        Args:
            element: 입력할 웹 요소
            text: 입력할 텍스트
        """
        # 자주 사용되는 문자 조합
        common_pairs = {
            'th': 0.8, 'he': 0.8, 'an': 0.8, 'in': 0.8, 'er': 0.8,
            'on': 0.8, 'at': 0.8, 'en': 0.8, 'es': 0.8, 'or': 0.8
        }
        
        # 특수문자와 대문자는 더 느리게
        special_chars = set('!@#$%^&*()_+-=[]{}|;:,.<>?~`\'\"')
        
        for i, char in enumerate(text):
            # 이전 문자와의 조합 확인
            if i > 0:
                pair = text[i-1:i+1]
                if pair in common_pairs:
                    delay = random.uniform(0.05, 0.1) * common_pairs[pair]
                else:
                    delay = random.uniform(0.1, 0.2)
            else:
                delay = random.uniform(0.1, 0.2)
            
            # 특수문자나 대문자는 더 느리게
            if char in special_chars or char.isupper():
                delay *= 1.5
            
            # 무작위 오타 (1% 확률)
            if random.random() < 0.01:
                # 오타 입력
                wrong_char = chr(ord(char) + random.randint(-1, 1))
                element.send_keys(wrong_char)
                await asyncio.sleep(delay)
                
                # 오타 수정
                element.send_keys('\b')  # Backspace
                await asyncio.sleep(delay)
                
                # 올바른 문자 입력
                element.send_keys(char)
            else:
                element.send_keys(char)
            
            await asyncio.sleep(delay)
    
    def human_like_scroll(self, driver: WebDriver, distance: Optional[int] = None) -> None:
        """Simulate human-like scrolling behavior"""
        if distance is None:
            # Random scroll distance if not specified
            distance = random.randint(300, 700)
        
        # Break down scroll into smaller chunks
        remaining = abs(distance)
        direction = 1 if distance > 0 else -1
        
        while remaining > 0:
            # Variable chunk size
            chunk = min(remaining, random.randint(50, 150))
            
            # Execute scroll
            driver.execute_script(f"window.scrollBy(0, {chunk * direction});")
            
            # Natural pause between scroll chunks
            time.sleep(random.uniform(0.1, 0.3))
            
            # Occasional longer pause (5% chance)
            if random.random() < 0.05:
                time.sleep(random.uniform(0.5, 1.0))
            
            remaining -= chunk
        
        # Final pause after scrolling
        self.human_like_delay()
    
    def _generate_human_curve(self, start: Tuple[int, int], 
                            end: Tuple[int, int],
                            control_points: int = 3) -> List[Tuple[int, int]]:
        """베지어 곡선을 사용한 자연스러운 마우스 이동 경로 생성"""
        # 제어점 생성
        points = [start]
        for _ in range(control_points):
            x = random.randint(min(start[0], end[0]), max(start[0], end[0]))
            y = random.randint(min(start[1], end[1]), max(start[1], end[1]))
            points.append((x, y))
        points.append(end)
        
        # 베지어 곡선 계산
        curve_points = []
        steps = 50
        for t in np.linspace(0, 1, steps):
            point = self._bezier_curve(points, t)
            curve_points.append(point)
            
        return curve_points
    
    def _bezier_curve(self, points: List[Tuple[int, int]], t: float) -> Tuple[int, int]:
        """베지어 곡선의 한 점 계산"""
        n = len(points) - 1
        x = y = 0
        for i, point in enumerate(points):
            coefficient = self._binomial(n, i) * (1 - t)**(n - i) * t**i
            x += coefficient * point[0]
            y += coefficient * point[1]
        return (int(x), int(y))
    
    def _binomial(self, n: int, k: int) -> int:
        """이항 계수 계산"""
        if k > n:
            return 0
        if k == 0 or k == n:
            return 1
            
        k = min(k, n - k)
        result = 1
        for i in range(k):
            result *= (n - i)
            result //= (i + 1)
        return result 