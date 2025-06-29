"""
프록시 설정을 위한 데이터 클래스
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ProxyConfig:
    """프록시 설정"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None 