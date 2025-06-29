"""
Base scraper implementation with dependency injection
"""
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import aiohttp
import asyncio
import logging

from ..utils.anti_bot_system import AntiBotSystem
from ..config.settings import settings

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, anti_bot_system: Optional[AntiBotSystem] = None):
        """
        스크래퍼 초기화
        
        Args:
            anti_bot_system: 안티봇 시스템 인스턴스 (선택사항)
        """
        self.anti_bot = anti_bot_system or AntiBotSystem()
        self.settings = settings
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Dict[str, Any]:
        """
        안티봇 시스템을 적용한 HTTP 요청 수행
        
        Args:
            url: 요청 URL
            method: HTTP 메서드
            **kwargs: 추가 요청 매개변수
            
        Returns:
            응답 데이터
        """
        # 안티봇 설정 적용
        anti_bot_config = self.anti_bot.prepare_request(url)
        
        # 요청 설정 병합
        if 'headers' in kwargs:
            kwargs['headers'].update(anti_bot_config['headers'])
        else:
            kwargs['headers'] = anti_bot_config['headers']
            
        if anti_bot_config['proxy']:
            kwargs['proxy'] = anti_bot_config['proxy']
            
        # 인간다운 지연 적용
        await asyncio.sleep(anti_bot_config['delay'])
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                # 봇 감지 확인
                if not self.anti_bot.handle_response(response):
                    raise Exception("Bot detection triggered")
                
                # 응답 처리
                if response.status == 200:
                    if 'json' in response.headers.get('content-type', ''):
                        return await response.json()
                    return {'text': await response.text()}
                else:
                    raise Exception(f"Request failed with status {response.status}")
                    
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    @abstractmethod
    async def scrape(self, *args, **kwargs):
        """스크래핑 로직 구현 (하위 클래스에서 구현)"""
        pass 