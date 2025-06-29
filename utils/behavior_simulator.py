"""
Human behavior simulation for anti-bot evasion
"""
import random
import time
from datetime import datetime
from typing import List, Optional, Tuple
import numpy as np

from ..config.settings import settings

class HumanBehaviorSimulator:
    """Simulates human-like behavior patterns for web scraping"""
    
    def __init__(self):
        """Initialize the behavior simulator with default patterns"""
        self.last_action_time = time.time()
        self.action_count = 0
        
        # Define natural delay patterns (in seconds)
        self.delay_patterns = {
            'quick': (0.5, 2.0),    # Quick browsing
            'normal': (2.0, 5.0),   # Normal reading
            'careful': (5.0, 10.0), # Careful examination
        }
        
        # Probability weights for different patterns
        self.pattern_weights = {
            'quick': 0.3,
            'normal': 0.5,
            'careful': 0.2
        }
        
    def get_natural_delay(self) -> float:
        """Calculate a natural delay based on behavior patterns"""
        # Select pattern based on weights
        pattern = random.choices(
            list(self.delay_patterns.keys()),
            weights=list(self.pattern_weights.values())
        )[0]
        
        # Get delay range for selected pattern
        min_delay, max_delay = self.delay_patterns[pattern]
        
        # Add some randomness to make it more natural
        base_delay = random.uniform(min_delay, max_delay)
        noise = np.random.normal(0, 0.1)  # Small random noise
        
        # Ensure delay is positive
        delay = max(0.1, base_delay + noise)
        
        # Occasionally add longer pauses
        if random.random() < 0.05:  # 5% chance
            delay += random.uniform(2.0, 5.0)
        
        self.last_action_time = time.time()
        self.action_count += 1
        
        return delay
        
    def simulate_scroll(self) -> Tuple[int, float]:
        """Simulate natural scrolling behavior"""
        # Random scroll amount (pixels)
        scroll_amount = random.randint(100, 800)
        
        # Calculate scroll duration based on amount
        base_duration = abs(scroll_amount) / 1000  # 1000 pixels per second base speed
        duration = random.uniform(base_duration * 0.8, base_duration * 1.2)  # Add variation
        
        return scroll_amount, duration
        
    def simulate_mouse_movement(self) -> List[Tuple[int, int]]:
        """Simulate natural mouse movement patterns"""
        num_points = random.randint(5, 10)
        points = []
        
        # Generate smooth curve points
        for i in range(num_points):
            x = random.randint(0, 1000)  # Screen width
            y = random.randint(0, 800)   # Screen height
            points.append((x, y))
            
        return points
        
    def should_take_break(self) -> bool:
        """Determine if a longer break should be taken"""
        # Take a break after every 50-100 actions
        if self.action_count > random.randint(50, 100):
            self.action_count = 0
            return True
            
        # Also take random breaks (0.5% chance)
        return random.random() < 0.005
        
    def get_break_duration(self) -> float:
        """Calculate duration for a break"""
        return random.uniform(30, 120)  # 30-120 seconds

class BehaviorSimulator:
    def __init__(self):
        """행동 시뮬레이터 초기화"""
        self.settings = settings
        self.last_request_time: Optional[datetime] = None
    
    def get_delay(self) -> float:
        """현재 시간대에 따른 지연 시간 계산"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            pattern = "morning"
        elif 12 <= hour < 17:
            pattern = "afternoon"
        elif 17 <= hour < 22:
            pattern = "evening"
        else:
            pattern = "night"
            
        min_delay, max_delay = self.settings.SCRAPING.USER_ACTIVITY_PATTERNS[pattern]
        return random.uniform(min_delay, max_delay)
    
    def simulate_typing(self, text: str) -> Tuple[str, float]:
        """인간다운 타이핑 패턴 시뮬레이션"""
        typed_text = ""
        total_delay = 0.0
        
        for char in text:
            # 문자별 타이핑 지연
            delay = random.uniform(0.05, 0.15)
            total_delay += delay
            time.sleep(delay)
            typed_text += char
            
            # 가끔 오타를 내고 수정
            if random.random() < 0.05:
                wrong_char = random.choice("qwertyuiop[]asdfghjkl;'zxcvbnm,./")
                typed_text += wrong_char
                time.sleep(0.2)  # 오타 인지 지연
                typed_text = typed_text[:-1]  # 백스페이스
                time.sleep(0.1)  # 수정 지연
                typed_text += char
        
        return typed_text, total_delay
    
    def simulate_scroll(self) -> float:
        """자연스러운 스크롤 패턴 시뮬레이션"""
        scroll_distance = random.randint(300, 800)
        scroll_duration = random.uniform(0.5, 2.0)
        
        # 부드러운 스크롤 시뮬레이션
        steps = int(scroll_duration * 60)  # 60fps
        for i in range(steps):
            progress = i / steps
            # easeInOutQuad 이징 함수 사용
            if progress < 0.5:
                scroll_step = 2 * progress * progress
            else:
                progress = 2 * progress - 1
                scroll_step = -0.5 * (progress * (progress - 2) - 1)
            
            current_scroll = scroll_distance * scroll_step
            time.sleep(scroll_duration / steps)
        
        return scroll_duration
    
    def wait_between_requests(self):
        """요청 간 자연스러운 대기 시간 적용"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            min_interval = self.settings.SCRAPING.MIN_REQUEST_INTERVAL
            
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        
        delay = self.get_delay()
        time.sleep(delay)
        self.last_request_time = datetime.now()
        return delay 