"""
Browser fingerprint randomization for anti-bot evasion
"""

import random
import json
import logging
from typing import Dict, Any

from vootcamp_ph_scraper.config.settings import settings

logger = logging.getLogger(__name__)

class FingerprintRandomizer:
    def __init__(self):
        """브라우저 지문 무작위화 초기화"""
        self.settings = settings
        self.current_fingerprint: Dict[str, Any] = {}
        self.regenerate_fingerprint()
    
    def regenerate_fingerprint(self):
        """새로운 브라우저 지문 생성"""
        user_agent = random.choice(self.settings.BROWSER.USER_AGENTS)
        
        # 화면 해상도
        resolutions = [
            (1920, 1080),
            (1366, 768),
            (1536, 864),
            (1440, 900),
            (1280, 720)
        ]
        width, height = random.choice(resolutions)
        
        # 브라우저 플러그인
        plugins = [
            "PDF Viewer",
            "Chrome PDF Viewer",
            "Chromium PDF Viewer",
            "Microsoft Edge PDF Viewer",
            "WebKit built-in PDF"
        ]
        enabled_plugins = random.sample(plugins, random.randint(1, len(plugins)))
        
        # 시스템 글꼴
        fonts = [
            "Arial",
            "Helvetica",
            "Times New Roman",
            "Times",
            "Courier New",
            "Courier",
            "Verdana",
            "Georgia",
            "Palatino",
            "Garamond",
            "Bookman",
            "Comic Sans MS",
            "Trebuchet MS",
            "Arial Black",
            "Impact"
        ]
        installed_fonts = random.sample(fonts, random.randint(5, 10))
        
        # WebGL 정보
        webgl_vendors = [
            "Google Inc. (NVIDIA)",
            "Google Inc. (Intel)",
            "Google Inc. (AMD)",
            "Apple Computer, Inc.",
            "Intel Inc."
        ]
        webgl_renderers = [
            "ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)",
            "Apple M1",
            "Intel Iris OpenGL Engine"
        ]
        
        self.current_fingerprint = {
            "userAgent": user_agent,
            "screenResolution": f"{width}x{height}",
            "colorDepth": random.choice([24, 32]),
            "pixelRatio": random.choice([1, 1.25, 1.5, 2]),
            "plugins": enabled_plugins,
            "fonts": installed_fonts,
            "webglVendor": random.choice(webgl_vendors),
            "webglRenderer": random.choice(webgl_renderers),
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            "language": random.choice(["en-US", "en-GB", "ko-KR"]),
            "timezone": random.choice(["Asia/Seoul", "America/Los_Angeles", "Europe/London"]),
            "doNotTrack": random.choice([None, "1", "0"]),
            "hardwareConcurrency": random.choice([2, 4, 6, 8, 12, 16]),
            "deviceMemory": random.choice([2, 4, 8, 16])
        }
    
    def get_headers(self) -> Dict[str, str]:
        """현재 지문에 기반한 HTTP 헤더 생성"""
        headers = self.settings.BROWSER.DEFAULT_HEADERS.copy()
        headers["User-Agent"] = self.current_fingerprint["userAgent"]
        headers["Accept-Language"] = f"{self.current_fingerprint['language']},en;q=0.9"
        
        return headers
    
    def get_fingerprint(self) -> Dict[str, Any]:
        """현재 브라우저 지문 반환"""
        return self.current_fingerprint.copy() 