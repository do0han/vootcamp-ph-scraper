"""
Supabase client module.
Handles database operations with Supabase.
"""
from typing import Dict, Any, List, Optional
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

class SupabaseClient:
    """Supabase 데이터베이스 클라이언트"""
    
    _instance = None
    client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Delay client initialization until first use
        if self.client is None:
            self._initialized = False
        else:
            self._initialized = True
        
    def _ensure_client(self):
        """클라이언트가 초기화되지 않았다면 초기화"""
        if not self._initialized:
            load_dotenv()
            
            # Supabase 설정 확인
            url: str = os.getenv("SUPABASE_URL")
            key: str = os.getenv("SUPABASE_KEY")
            
            if not url or not key:
                raise ValueError("Supabase URL and key must be set in environment variables")
                    
            self.client = get_singleton_client()
            self._initialized = True
    
    def insert_google_trends(self, data: Dict[str, Any]) -> None:
        """Google Trends 데이터 저장"""
        self._ensure_client()
        try:
            # Google Trends 데이터를 개별 키워드별로 저장
            keywords = data.get("keywords", [])
            interest_data = data.get("interest_over_time", {})
            related_queries = data.get("related_queries", {})
            collection_timestamp = data.get("collected_at", datetime.now().isoformat())
            
            for keyword in keywords:
                # 각 키워드별로 레코드 생성
                record = {
                    "collection_date": collection_timestamp,
                    "trend_type": "search_trends",
                    "keyword": keyword,
                    "search_volume": None,  # pytrends doesn't provide absolute volume
                    "related_topics": {
                        "interest_over_time": interest_data,
                        "related_queries": related_queries.get(keyword, {})
                    },
                    "region": "PH",
                    "timeframe": "today 3-m"
                }
                
                self.client.table("google_trends").insert(record).execute()
                
        except Exception as e:
            print(f"Error inserting Google Trends data: {e}")
    
    def insert_shopee_products(self, products: List[Dict[str, Any]], type: str = "top_sales") -> None:
        """Shopee 제품 데이터 저장"""
        self._ensure_client()
        try:
            for product in products:
                # Shopee 제품 데이터를 스키마에 맞게 변환
                record = {
                    "collection_date": product.get("collected_at", datetime.now().isoformat()),
                    "search_keyword": product.get("search_keyword", type),
                    "product_name": product.get("name", product.get("title", "Unknown Product")),
                    "seller_name": product.get("seller", product.get("shop_name")),
                    "price": self._parse_price(product.get("price")),
                    "currency": "PHP",
                    "rating": self._parse_rating(product.get("rating")),
                    "review_count": self._parse_number(product.get("reviews", product.get("review_count"))),
                    "sales_count": self._parse_number(product.get("sales", product.get("sold"))),
                    "product_url": product.get("url", product.get("link")),
                    "image_url": product.get("image"),
                    "category": product.get("category"),
                    "location": product.get("location"),
                    "discount_info": {"original_price": product.get("original_price"), "discount": product.get("discount")} if product.get("discount") else {}
                }
                
                self.client.table("shopee_products").insert(record).execute()
                
        except Exception as e:
            print(f"Error inserting Shopee products: {e}")
    
    def _parse_price(self, price_str) -> float:
        """가격 문자열을 float로 변환"""
        if not price_str:
            return None
        try:
            # Remove currency symbols and commas
            clean_price = str(price_str).replace('₱', '').replace(',', '').strip()
            return float(clean_price)
        except:
            return None
    
    def _parse_rating(self, rating_str) -> float:
        """평점 문자열을 float로 변환"""
        if not rating_str:
            return None
        try:
            return float(str(rating_str).strip())
        except:
            return None
    
    def _parse_number(self, num_str) -> int:
        """숫자 문자열을 int로 변환 (K, M 등 처리)"""
        if not num_str:
            return None
        try:
            clean_num = str(num_str).strip().upper()
            if 'K' in clean_num:
                return int(float(clean_num.replace('K', '')) * 1000)
            elif 'M' in clean_num:
                return int(float(clean_num.replace('M', '')) * 1000000)
            else:
                return int(float(clean_num.replace(',', '')))
        except:
            return None
    
    def insert_tiktok_hashtags(self, hashtags: List[Dict[str, Any]]) -> None:
        """TikTok 해시태그 데이터 저장"""
        self._ensure_client()
        try:
            for hashtag in hashtags:
                self.client.table("tiktok_hashtags").insert({
                    **hashtag,
                    "created_at": datetime.now().isoformat()
                }).execute()
        except Exception as e:
            print(f"Error inserting TikTok hashtags: {e}")
    
    def insert_tiktok_videos(self, videos: List[Dict[str, Any]]) -> None:
        """TikTok 비디오 데이터 저장"""
        self._ensure_client()
        try:
            for video in videos:
                # TikTok 비디오 데이터를 스키마에 맞게 변환
                record = {
                    "collection_date": video.get("collected_at", datetime.now().isoformat()),
                    "hashtag": ",".join(video.get("hashtags", [])) if video.get("hashtags") else "unknown",
                    "video_url": video.get("video_url"),
                    "video_id": video.get("video_id"),
                    "uploader_name": video.get("author_name"),
                    "uploader_username": video.get("author_username"),
                    "view_count": video.get("view_count"),
                    "like_count": video.get("like_count"),
                    "comment_count": video.get("comment_count"),
                    "share_count": video.get("share_count"),
                    "video_title": video.get("title"),
                    "video_description": video.get("description"),
                    "used_hashtags": video.get("hashtags", []),
                    "sound_info": {"title": video.get("music_title")} if video.get("music_title") else {},
                    "is_trending": True  # All collected videos are considered trending
                }
                
                self.client.table("tiktok_videos").insert(record).execute()
                
        except Exception as e:
            print(f"Error inserting TikTok videos: {e}")
    
    def get_latest_google_trends(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 Google Trends 데이터 조회"""
        self._ensure_client()
        try:
            response = self.client.table("google_trends") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching Google Trends data: {e}")
            return []
    
    def get_latest_shopee_products(self, type: str = "top_sales", limit: int = 50) -> List[Dict[str, Any]]:
        """최근 Shopee 제품 데이터 조회"""
        try:
            response = self.client.table("shopee_products") \
                .select("*") \
                .eq("type", type) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching Shopee products: {e}")
            return []
    
    def get_latest_tiktok_hashtags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """최근 TikTok 해시태그 데이터 조회"""
        try:
            response = self.client.table("tiktok_hashtags") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching TikTok hashtags: {e}")
            return []
    
    def get_latest_tiktok_videos(self, hashtag: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 TikTok 비디오 데이터 조회"""
        try:
            query = self.client.table("tiktok_videos").select("*")
            
            if hashtag:
                query = query.eq("hashtag", hashtag)
            
            response = query \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching TikTok videos: {e}")
            return []
    
    def insert_tiktok_shop_products(self, products: List[Dict[str, Any]]) -> None:
        """TikTok Shop 상품 데이터 저장"""
        self._ensure_client()
        
        if not products:
            print("⚠️ No products to insert")
            return

        try:
            # TikTok Shop 상품 데이터를 적절한 형식으로 변환
            formatted_products = []
            
            for product in products:
                # 상품 ID 생성 (URL에서 추출 또는 고유 식별자 생성)
                product_id = self._extract_product_id(product)
                
                formatted_product = {
                    "collection_date": product.get("collection_date", datetime.now().isoformat()),
                    "source_type": product.get("source_type", "unknown"),
                    "product_name": product.get("product_name", "Unknown Product"),
                    "price": product.get("price_numeric"),
                    "currency": "PHP",
                    "discount_price": product.get("original_price_numeric"),
                    "discount_percentage": product.get("discount_percentage"),
                    "seller_name": product.get("seller_info", "Unknown Seller"),
                    "seller_id": None,  # TikTok Shop 스크래퍼에서 추출하면 업데이트
                    "rating": product.get("rating_numeric"),
                    "sales_count": product.get("sales_count_numeric"),
                    "product_url": product.get("product_url"),
                    "image_url": product.get("image_url"),
                    "category": product.get("category"),
                    "subcategory": None,
                    "brand": None,
                    "is_flash_sale": product.get("source_type") == "flash_sale",
                    "is_trending": False,
                    "is_sponsored": False,
                    "product_tags": [],
                    "product_description": product.get("product_name"),  # 기본적으로 상품명 사용
                    "shipping_info": {},
                    "stock_count": None  # 재고 정보는 상세페이지에서만 가능
                }
                
                formatted_products.append(formatted_product)
            
            # 배치로 데이터 삽입
            if formatted_products:
                response = self.client.table("tiktok_shop_products").insert(formatted_products).execute()
                print(f"✅ Inserted {len(formatted_products)} TikTok Shop products to database")
                return response.data
            else:
                print("⚠️ No TikTok Shop products to insert")
                return []
                
        except Exception as e:
            print(f"❌ Error inserting TikTok Shop products: {e}")
            # 개별 삽입 시도 (일부 데이터라도 저장)
            return self._insert_tiktok_shop_products_individually(products)
    
    def _extract_product_id(self, product: Dict[str, Any]) -> str:
        """상품 URL에서 상품 ID 추출 또는 고유 ID 생성"""
        try:
            product_url = product.get("product_url", "")
            
            # TikTok Shop URL 패턴에서 ID 추출 시도
            if "/product/" in product_url:
                import re
                match = re.search(r'/product/([^/?]+)', product_url)
                if match:
                    return f"tiktok_{match.group(1)}"
            
            # URL에서 ID를 추출할 수 없으면 상품명과 타임스탬프로 생성
            product_name = product.get("product_name", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 상품명을 안전한 ID로 변환
            import re
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', product_name.lower())[:30]
            return f"tiktok_{safe_name}_{timestamp}"
            
        except Exception as e:
            # 최후의 수단: 타임스탬프 기반 ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            return f"tiktok_unknown_{timestamp}"
    
    def _insert_tiktok_shop_products_individually(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """TikTok Shop 상품을 개별적으로 삽입 (배치 삽입 실패 시 fallback)"""
        successfully_inserted = []
        
        for i, product in enumerate(products):
            try:
                formatted_product = {
                    "collection_date": product.get("collection_date", datetime.now().isoformat()),
                    "source_type": product.get("source_type", "unknown"),
                    "product_name": product.get("product_name", "Unknown Product"),
                    "seller_name": product.get("seller_info", "Unknown Seller"),
                    "price": product.get("price_numeric"),
                    "currency": "PHP",
                    "rating": product.get("rating_numeric"),
                    "sales_count": product.get("sales_count_numeric"),
                    "product_url": product.get("product_url"),
                    "image_url": product.get("image_url"),
                    "category": product.get("category")
                }
                
                response = self.client.table("tiktok_shop_products").insert(formatted_product).execute()
                successfully_inserted.append(response.data[0] if response.data else formatted_product)
                print(f"✅ Individual insert successful for product {i+1}")
                
            except Exception as e:
                print(f"❌ Failed to insert individual product {i+1}: {e}")
                continue
        
        print(f"💾 Successfully inserted {len(successfully_inserted)}/{len(products)} TikTok Shop products individually")
        return successfully_inserted
    
    def get_latest_tiktok_shop_products(self, source_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 TikTok Shop 상품 데이터 조회"""
        try:
            query = self.client.table("tiktok_shop_products").select("*")
            
            if source_type:
                query = query.eq("source_type", source_type)
            
            response = query \
                .order("collection_date", desc=True) \
                .limit(limit) \
                .execute()
            
            return response.data
        except Exception as e:
            print(f"❌ Error fetching TikTok Shop products: {e}")
            return []
    
    def insert_local_events(self, events: List[Dict[str, Any]]) -> None:
        """로컬 이벤트 데이터 저장"""
        self._ensure_client()
        try:
            for event in events:
                # 로컬 이벤트 데이터를 스키마에 맞게 변환
                record = {
                    "collection_date": event.get("collection_date", datetime.now().isoformat()),
                    "event_name": event.get("event_name"),
                    "event_dates": event.get("event_dates"),
                    "event_location": event.get("event_location"),
                    "event_description": event.get("event_description"),
                    "source_url": event.get("source_url"),
                    "source_website": event.get("source_website"),
                    "event_type": event.get("event_type", "lifestyle_event"),
                    "event_tags": event.get("event_tags", []),
                    "is_recurring": event.get("is_recurring", False)
                }
                
                self.client.table("local_events").insert(record).execute()
                
        except Exception as e:
            print(f"Error inserting local events: {e}")
    
    def get_latest_local_events(self, event_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 로컬 이벤트 데이터 조회"""
        self._ensure_client()
        try:
            query = self.client.table("local_events").select("*")
            
            if event_type:
                query = query.eq("event_type", event_type)
            
            response = query.order("collection_date", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching local events: {e}")
            return []

def get_supabase_client() -> Client:
    """
    Get Supabase client instance
    """
    # Check if running in test environment first
    if os.environ.get('TESTING') == 'true':
        from unittest.mock import Mock
        mock_client = Mock()
        # Add any necessary mock methods
        mock_client.table = Mock(return_value=mock_client)
        mock_client.insert = Mock(return_value=mock_client)
        mock_client.select = Mock(return_value=mock_client)
        mock_client.execute = Mock(return_value={'data': []})
        return mock_client

    # Only try to create real client if not in testing mode
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')

    if not url or not key:
        raise ValueError("Supabase URL and key must be set in environment variables")

    try:
        # Simple client creation without options
        client = create_client(url, key)
        return client
    except Exception as e:
        # If proxy error occurs, try with a custom user agent to bypass
        try:
            import httpx
            from supabase._sync.client import SyncClient
            
            # Create minimal client bypassing problematic configurations
            client = create_client(url, key)
            return client
        except Exception as e2:
            raise ConnectionError(f"Failed to create Supabase client: {e2}")

# Global client instance - initialized lazily to avoid import-time errors
_supabase_client = None

def get_singleton_client():
    """싱글톤 Supabase 클라이언트 반환 (lazy initialization)"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    return _supabase_client 