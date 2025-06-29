import logging
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

from ..utils.anti_bot import AntiBotSystem, AntiBotConfig
from ..config.settings import settings

class ShopeeScraper:
    """Shopee data scraper with anti-bot measures"""
    
    BASE_URL = "https://shopee.ph"
    SEARCH_API = "/api/v4/search/search_items"
    PRODUCT_API = "/api/v4/item/get"
    
    def __init__(self, anti_bot_config: Optional[AntiBotConfig] = None):
        """Initialize the scraper with anti-bot configuration"""
        self.anti_bot = AntiBotSystem(anti_bot_config or AntiBotConfig())
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
    
    def search_products(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for products with the given keyword"""
        products = []
        page = 0
        
        while len(products) < limit:
            try:
                # Prepare request with anti-bot measures
                url = urljoin(self.BASE_URL, self.SEARCH_API)
                request_config = self.anti_bot.prepare_request(url)
                
                # Apply delay before request
                self.anti_bot.apply_delay()
                
                # Make request
                params = {
                    'keyword': keyword,
                    'page': page,
                    'limit': min(50, limit - len(products))
                }
                
                response = self.session.get(
                    url,
                    params=params,
                    headers=request_config['headers'],
                    proxies={'http': request_config['proxy'], 'https': request_config['proxy']} if request_config['proxy'] else None,
                    timeout=30
                )
                
                # Check for bot detection
                if not self.anti_bot.handle_response(response):
                    continue
            
                # Process response
                data = response.json()
                if not data.get('items'):
                    break
                    
                products.extend(data['items'])
                page += 1
                    
            except Exception as e:
                self.logger.error(f"Error searching products: {e}")
                break
                
        return products[:limit]
    
    def get_product_details(self, product_id: str, shop_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific product"""
        try:
            # Prepare request with anti-bot measures
            url = urljoin(self.BASE_URL, self.PRODUCT_API)
            request_config = self.anti_bot.prepare_request(url)
            
            # Apply delay before request
            self.anti_bot.apply_delay()
            
            # Make request
            params = {
                'itemid': product_id,
                'shopid': shop_id
            }
            
            response = self.session.get(
                url,
                params=params,
                headers=request_config['headers'],
                proxies={'http': request_config['proxy'], 'https': request_config['proxy']} if request_config['proxy'] else None,
                timeout=30
            )
            
            # Check for bot detection
            if not self.anti_bot.handle_response(response):
                return None
            
            # Process response
            data = response.json()
            return data.get('item')
            
        except Exception as e:
            self.logger.error(f"Error getting product details: {e}")
            return None
    
    def close(self):
        """Close the session"""
        self.session.close() 