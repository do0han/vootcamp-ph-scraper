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
        if self.client is None:
            self.client = get_supabase_client()
        
        load_dotenv()
        
        # Supabase 설정
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("Supabase URL and key must be set in environment variables")
    
    def insert_google_trends(self, data: Dict[str, Any]) -> None:
        """Google Trends 데이터 저장"""
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
        client = create_client(url, key)
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to create Supabase client: {e}")

# Create a singleton instance
supabase = get_supabase_client() 