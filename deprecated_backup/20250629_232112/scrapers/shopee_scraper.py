"""
Shopee 데이터 스크래퍼
"""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import aiohttp
from ..utils.anti_bot_system import AntiBotSystem

logger = logging.getLogger(__name__)

class ShopeeScraper:
    """Shopee 데이터 스크래퍼"""
    
    BASE_URL = "https://shopee.ph"
    SEARCH_API = f"{BASE_URL}/api/v4/search/search_items"
    PRODUCT_API = f"{BASE_URL}/api/v4/item/get"
    
    def __init__(self, anti_bot_system: AntiBotSystem):
        """
        Args:
            anti_bot_system: 안티봇 시스템 인스턴스
        """
        self.anti_bot = anti_bot_system
        self.session = None
    
    async def init_session(self):
        """세션 초기화"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """세션 종료"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def search_products(self, keyword: str, limit: int = 10) -> List[Dict[Any, Any]]:
        """
        키워드로 상품 검색
        
        Args:
            keyword: 검색 키워드
            limit: 검색 결과 제한 수
            
        Returns:
            검색된 상품 목록
        """
        await self.init_session()
        
        params = {
            "by": "relevancy",
            "keyword": keyword,
            "limit": limit,
            "newest": 0,
            "order": "desc",
            "page_type": "search",
            "scenario": "PAGE_GLOBAL_SEARCH",
            "version": 2
        }
        
        headers = {
            "User-Agent": self.anti_bot.get_user_agent(),
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        try:
            proxy = self.anti_bot.get_proxy()
            await asyncio.sleep(self.anti_bot.get_delay())
            
            async with self.session.get(
                self.SEARCH_API,
                params=params,
                headers=headers,
                proxy=proxy,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    return [self._parse_product(item) for item in items]
                else:
                    logger.error(f"검색 실패: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {str(e)}")
            return []
    
    async def get_product_details(self, shop_id: int, item_id: int) -> Optional[Dict[Any, Any]]:
        """
        상품 상세 정보 조회
        
        Args:
            shop_id: 상점 ID
            item_id: 상품 ID
            
        Returns:
            상품 상세 정보
        """
        await self.init_session()
        
        params = {
            "itemid": item_id,
            "shopid": shop_id
        }
        
        headers = {
            "User-Agent": self.anti_bot.get_user_agent(),
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        try:
            proxy = self.anti_bot.get_proxy()
            await asyncio.sleep(self.anti_bot.get_delay())
            
            async with self.session.get(
                self.PRODUCT_API,
                params=params,
                headers=headers,
                proxy=proxy,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_product_details(data)
                else:
                    logger.error(f"상품 상세 정보 조회 실패: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"상품 상세 정보 조회 중 오류 발생: {str(e)}")
            return None
    
    def _parse_product(self, item: Dict[Any, Any]) -> Dict[Any, Any]:
        """상품 정보 파싱"""
        return {
            "item_id": item.get("itemid"),
            "shop_id": item.get("shopid"),
            "name": item.get("item_basic", {}).get("name"),
            "price": item.get("item_basic", {}).get("price") / 100000,
            "currency": "PHP",
            "stock": item.get("item_basic", {}).get("stock"),
            "sold": item.get("item_basic", {}).get("sold"),
            "rating": item.get("item_basic", {}).get("item_rating", {}).get("rating_star", 0),
            "image_url": f"https://cf.shopee.ph/file/{item.get('item_basic', {}).get('image')}"
        }
    
    def _parse_product_details(self, data: Dict[Any, Any]) -> Dict[Any, Any]:
        """상품 상세 정보 파싱"""
        item = data.get("data", {})
        return {
            "item_id": item.get("itemid"),
            "shop_id": item.get("shopid"),
            "name": item.get("name"),
            "description": item.get("description"),
            "price": item.get("price") / 100000,
            "currency": "PHP",
            "stock": item.get("stock"),
            "sold": item.get("sold"),
            "rating": item.get("item_rating", {}).get("rating_star", 0),
            "categories": [cat.get("display_name") for cat in item.get("categories", [])],
            "images": [f"https://cf.shopee.ph/file/{img}" for img in item.get("images", [])],
            "attributes": [{
                "name": attr.get("name"),
                "value": attr.get("value")
            } for attr in item.get("attributes", [])]
        }

    def _get_description(self, soup: BeautifulSoup) -> str:
        """Extract product description from page"""
        try:
            desc_div = soup.find("div", {"class": "product-detail__description"})
            return desc_div.get_text().strip() if desc_div else "No description available"
        except:
            return "Description extraction failed"
            
    def _get_stock(self, soup: BeautifulSoup) -> int:
        """Extract product stock from page"""
        try:
            stock_div = soup.find("div", {"class": "product-detail__stock"})
            if stock_div:
                stock_text = stock_div.get_text()
                return int(''.join(filter(str.isdigit, stock_text)))
            return 0
        except:
            return 0
            
    def _get_categories(self, soup: BeautifulSoup) -> List[str]:
        """Extract product categories from page"""
        try:
            cat_div = soup.find("div", {"class": "product-detail__category"})
            if cat_div:
                return [a.get_text().strip() for a in cat_div.find_all("a")]
            return []
        except:
            return [] 