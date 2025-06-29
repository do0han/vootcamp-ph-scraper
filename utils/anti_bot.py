"""
Anti-bot detection evasion utility module for Vootcamp PH Data Scraper.
Provides centralized anti-bot functionality for all scrapers.
"""
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import time
import logging
import json
from .behavior_simulator import HumanBehaviorSimulator

@dataclass
class AntiBotConfig:
    """Configuration for anti-bot measures"""
    min_delay: float = 1.0
    max_delay: float = 5.0
    user_agents: List[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ])
    proxy_list: List[str] = field(default_factory=list)
    max_retries: int = 3
    retry_delay: float = 2.0
    timeout: int = 30

class AntiBotSystem:
    """Centralized anti-bot system"""
    
    def __init__(self, config: AntiBotConfig = None):
        """Initialize the anti-bot system with configuration"""
        self.config = config or AntiBotConfig()
        self.logger = logging.getLogger(__name__)
        self.session_start_time = time.time()
        self.request_count = 0
        self.current_proxy = None
        self.current_user_agent = None
        self.behavior_simulator = HumanBehaviorSimulator()
        
    def get_delay(self) -> float:
        """Calculate delay between requests based on behavior patterns"""
        return self.behavior_simulator.get_natural_delay()
        
    def apply_delay(self) -> None:
        """Apply calculated delay between requests"""
        delay = self.get_delay()
        time.sleep(delay)
        
    def get_user_agent(self) -> str:
        """Get a random user agent from the configured list"""
        self.current_user_agent = random.choice(self.config.user_agents)
        return self.current_user_agent
        
    def get_proxy(self) -> Optional[str]:
        """Get a proxy from the configured list"""
        if not self.config.proxy_list:
            return None
        self.current_proxy = random.choice(self.config.proxy_list)
        return self.current_proxy
        
    def prepare_request(self, url: str) -> Dict[str, Any]:
        """Prepare request with anti-bot measures"""
        # Validate session
        self._validate_session()
        
        # Get proxy and user agent
        proxy = self.get_proxy()
        user_agent = self.get_user_agent()
        
        # Calculate delay
        delay = self.get_delay()
        
        # Prepare headers
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        return {
            'proxy': proxy,
            'headers': headers,
            'delay': delay
        }
        
    def _validate_session(self) -> None:
        """Validate and manage session state"""
        current_time = time.time()
        session_duration = current_time - self.session_start_time
        
        # Reset session if it's too old or has too many requests
        if session_duration > 3600 or self.request_count > 1000:  # 1 hour or 1000 requests
            self.session_start_time = current_time
            self.request_count = 0
            self.current_proxy = None
            self.current_user_agent = None
        
        self.request_count += 1
        
    def handle_response(self, response: Any) -> bool:
        """Handle response and check for bot detection"""
        try:
            response_text = str(response.text).lower()
            
            # Check for common bot detection patterns
            bot_patterns = [
                'captcha',
                'robot',
                'automated',
                'blocked',
                'security check',
                'verify human'
            ]
            
            for pattern in bot_patterns:
                if pattern in response_text:
                    self.logger.warning(f"Bot detection pattern found: {pattern}")
                    self._handle_bot_detection()
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling response: {e}")
            return False
            
    def _handle_bot_detection(self) -> None:
        """Handle bot detection event"""
        self.logger.info("Handling bot detection...")
        
        # Reset session
        self.session_start_time = time.time()
        self.request_count = 0
        
        # Change proxy and user agent
        self.current_proxy = None
        self.current_user_agent = None
        
        # Apply longer delay
        time.sleep(random.uniform(30, 60))  # Wait 30-60 seconds after detection

def simulate_human_delay(min_delay: float = 1.0, max_delay: float = 5.0) -> None:
    """Simulate human-like delay between actions"""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay) 