"""
Browser fingerprint randomization utility for anti-bot system.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import random
import json
import os
from pathlib import Path

@dataclass
class BrowserProfile:
    """브라우저 프로필 설정"""
    user_agent: str
    platform: str
    browser_version: str
    screen_resolution: str
    color_depth: int
    timezone: str
    language: str
    plugins: List[str]

class BrowserFingerprintRandomizer:
    """브라우저 지문 무작위화 시스템"""
    
    def __init__(self):
        self.profiles_data = self._load_profiles_data()
        
    def _load_profiles_data(self) -> Dict[str, Any]:
        """프로필 데이터 로드"""
        profile_path = Path(__file__).parent.parent / 'data' / 'browser_profiles.json'
        
        try:
            with open(profile_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load browser profiles: {str(e)}")
            
    def _get_random_os(self) -> str:
        """운영체제 무작위 선택"""
        return random.choice(list(self.profiles_data.keys()))
        
    def _get_random_platform(self, os_type: str) -> str:
        """플랫폼 무작위 선택"""
        return random.choice(self.profiles_data[os_type]['platforms'])
        
    def _get_random_user_agent(self, os_type: str) -> str:
        """User-Agent 무작위 선택"""
        return random.choice(self.profiles_data[os_type]['browsers']['chrome']['user_agents'])
        
    def _get_random_browser_version(self, os_type: str) -> str:
        """브라우저 버전 무작위 선택"""
        return random.choice(self.profiles_data[os_type]['browsers']['chrome']['versions'])
        
    def _get_random_screen_resolution(self, os_type: str) -> str:
        """화면 해상도 무작위 선택"""
        return random.choice(self.profiles_data[os_type]['screen_resolutions'])
        
    def _get_random_color_depth(self, os_type: str) -> int:
        """색상 심도 무작위 선택"""
        return random.choice(self.profiles_data[os_type]['color_depths'])
        
    def _get_random_timezone(self, os_type: str) -> str:
        """시간대 무작위 선택"""
        return random.choice(self.profiles_data[os_type]['timezones'])
        
    def _get_random_language(self, os_type: str) -> str:
        """언어 무작위 선택"""
        return random.choice(self.profiles_data[os_type]['languages'])
        
    def _get_random_plugins(self, os_type: str) -> List[str]:
        """플러그인 무작위 선택"""
        plugins = self.profiles_data[os_type]['plugins']
        num_plugins = random.randint(1, len(plugins))
        return random.sample(plugins, num_plugins)
        
    def generate_profile(self) -> BrowserProfile:
        """새로운 브라우저 프로필 생성"""
        os_type = self._get_random_os()
        
        return BrowserProfile(
            platform=self._get_random_platform(os_type),
            user_agent=self._get_random_user_agent(os_type),
            browser_version=self._get_random_browser_version(os_type),
            screen_resolution=self._get_random_screen_resolution(os_type),
            color_depth=self._get_random_color_depth(os_type),
            timezone=self._get_random_timezone(os_type),
            language=self._get_random_language(os_type),
            plugins=self._get_random_plugins(os_type)
        )
        
    def apply_profile_to_driver(self, driver, profile: Optional[BrowserProfile] = None) -> None:
        """브라우저 프로필을 드라이버에 적용"""
        if profile is None:
            profile = self.generate_profile()
            
        # JavaScript를 통한 브라우저 지문 설정
        js_script = f"""
        Object.defineProperty(navigator, 'platform', {{
            get: function() {{ return '{profile.platform}'; }}
        }});
        Object.defineProperty(navigator, 'userAgent', {{
            get: function() {{ return '{profile.user_agent}'; }}
        }});
        Object.defineProperty(screen, 'colorDepth', {{
            get: function() {{ return {profile.color_depth}; }}
        }});
        Object.defineProperty(Intl, 'DateTimeFormat', {{
            get: function() {{ return function() {{ return {{ resolvedOptions: function() {{ return {{ timeZone: '{profile.timezone}' }}; }} }}; }}; }}
        }});
        Object.defineProperty(navigator, 'languages', {{
            get: function() {{ return ['{profile.language}']; }}
        }});
        """
        
        driver.execute_script(js_script)
        
        # 화면 해상도 설정
        width, height = map(int, profile.screen_resolution.split('x'))
        driver.set_window_size(width, height) 