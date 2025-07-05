"""
Google Trends scraper implementation
"""
from typing import Dict, List, Any, Optional
import logging
import json
import asyncio
import time
import pandas as pd
from datetime import datetime, timedelta
from retry import retry
from pytrends.request import TrendReq

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from utils.anti_bot_system import AntiBotSystem
from utils.ethical_scraping import ScrapingPolicy

logger = logging.getLogger(__name__)


class GoogleTrendsScraper:
    """Google Trends 데이터 스크래퍼"""
    
    def __init__(
        self,
        anti_bot_system: AntiBotSystem,
        scraping_policy: ScrapingPolicy,
        hl: str = "en-PH",
        tz: int = 480  # Manila timezone
    ):
        self.anti_bot_system = anti_bot_system
        self.scraping_policy = scraping_policy
        self.pytrends = TrendReq(hl=hl, tz=tz)
        self.last_request_time = None
        
        # Popular keywords in Philippines to track instead of trending searches
        self.popular_keywords = [
            # E-commerce & Shopping
            "shopee", "lazada", "amazon", "alibaba",
            
            # Local brands & services
            "jollibee", "mcdonalds", "sm mall", "ayala", "gcash", "paymaya",
            
            # Categories of interest for Philippines market
            "skincare", "beauty", "makeup", "cosmetics",
            "fashion", "clothing", "shoes", "bags",
            "electronics", "gadgets", "iphone", "samsung",
            "food", "restaurants", "delivery", "grab food",
            "travel", "hotels", "vacation", "boracay", "palawan",
            "fitness", "health", "wellness", "gym",
            "education", "online learning", "university",
            "business", "investment", "cryptocurrency", "bitcoin",
            
            # Entertainment & Social
            "netflix", "youtube", "tiktok", "facebook",
            "kpop", "kdrama", "anime", "movies"
        ]
        
        logger.info(f"Google Trends scraper initialized for region: {hl}")
    
    def get_trends(self, keywords: List[str], timeframe: str = "today 3-m") -> Dict[str, Any]:
        """키워드에 대한 트렌드 데이터 수집"""
        # 윤리적 스크래핑 정책 확인
        self.scraping_policy.wait_for_rate_limit()
        
        try:
            # Anti-bot 시스템 적용
            self.anti_bot_system.simulate_human_behavior()
            
            # 트렌드 데이터 요청
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo="PH")
            interest_over_time = self.pytrends.interest_over_time()
            
            # related_queries를 안전하게 처리
            related_queries = {}
            try:
                related_queries = self.pytrends.related_queries()
            except (IndexError, KeyError, Exception) as e:
                logger.warning(f"Related queries not available for keywords {keywords}: {e}")
                related_queries = {}
            
            # 데이터 정리 (JSON 직렬화 가능하도록 변환)
            def safe_to_dict(df):
                """DataFrame을 JSON 직렬화 가능한 dict로 변환"""
                if df is None or df.empty:
                    return {}
                # 인덱스를 문자열로 변환하고 값들을 기본 Python 타입으로 변환
                result = {}
                for col in df.columns:
                    result[col] = {str(idx): val for idx, val in df[col].items()}
                return result
            
            trends_data = {
                "keywords": keywords,
                "interest_over_time": safe_to_dict(interest_over_time),
                "related_queries": {
                    kw: {
                        "top": safe_to_dict(queries["top"]) if queries and queries.get("top") is not None else {},
                        "rising": safe_to_dict(queries["rising"]) if queries and queries.get("rising") is not None else {}
                    } for kw, queries in related_queries.items()
                } if related_queries else {},
                "collected_at": datetime.now().isoformat()
            }
            
            return trends_data
            
        except Exception as e:
            # 에러 처리
            logger.error(f"Google Trends scraping error: {e}")
            
            # Try to handle error with anti-bot system if it has error handler
            try:
                if hasattr(self.anti_bot_system, 'error_handler'):
                    self.anti_bot_system.error_handler.handle_error(e, "google_trends_scraping")
            except:
                pass
                
            return {}
    
    def cleanup(self) -> None:
        """리소스 정리"""
        pass  # pytrends는 특별한 정리가 필요 없음
    
    @retry(tries=3, delay=2, backoff=2)
    def get_popular_keywords_data(self) -> List[Dict[str, Any]]:
        """
        Get interest data for popular Philippines keywords
        This replaces trending_searches which doesn't work reliably
        
        Returns:
            List of keyword interest data
        """
        try:
            logger.info("Fetching interest data for popular Philippines keywords...")
            
            result = []
            current_time = datetime.utcnow()
            
            # Process keywords in small batches to avoid rate limits
            batch_size = 5  # Google Trends limit
            
            for i in range(0, len(self.popular_keywords), batch_size):
                batch_keywords = self.popular_keywords[i:i + batch_size]
                
                try:
                    # Build payload for this batch
                    self.pytrends.build_payload(
                        batch_keywords, 
                        cat=0, 
                        timeframe='now 1-d', 
                        geo='PH',
                        gprop=''
                    )
                    
                    # Get interest over time
                    interest_df = self.pytrends.interest_over_time()
                    
                    if not interest_df.empty:
                        # Process each keyword's latest interest score
                        latest_data = interest_df.iloc[-1]  # Get most recent data point
                        
                        for keyword in batch_keywords:
                            if keyword in latest_data and pd.notna(latest_data[keyword]):
                                interest_score = int(latest_data[keyword])
                                
                                if interest_score > 0:  # Only include keywords with interest
                                    result.append({
                                        'collection_date': current_time.isoformat(),
                                        'trend_type': 'popular_keyword',
                                        'keyword': keyword,
                                        'search_volume': interest_score,
                                        'related_topics': None,
                                        'region': 'PH',
                                        'category': self._classify_keyword(keyword),
                                        'timeframe': '24h'
                                    })
                    
                    # Add delay between batches
                    time.sleep(Settings.DELAY_BETWEEN_REQUESTS)
                    
                except Exception as e:
                    logger.warning(f"Failed to get data for batch {batch_keywords}: {e}")
                    continue
            
            logger.info(f"Successfully fetched interest data for {len(result)} popular keywords")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching popular keywords data: {e}")
            raise
    
    @retry(tries=3, delay=2, backoff=2)
    def get_related_queries(self, keyword: str, timeframe: str = 'now 1-d') -> List[Dict[str, Any]]:
        """
        Get related queries for a specific keyword
        
        Args:
            keyword: The main keyword to search for
            timeframe: Time range for the search
            
        Returns:
            List of related query data
        """
        try:
            logger.info(f"Fetching related queries for keyword: {keyword}")
            
            # Build payload for the keyword
            self.pytrends.build_payload(
                [keyword], 
                cat=0, 
                timeframe=timeframe, 
                geo='PH',
                gprop=''
            )
            
            # Get related queries
            related_queries = self.pytrends.related_queries()
            
            result = []
            current_time = datetime.utcnow()
            
            if keyword in related_queries:
                # Process rising queries
                if ('rising' in related_queries[keyword] and 
                    related_queries[keyword]['rising'] is not None and
                    not related_queries[keyword]['rising'].empty):
                    
                    rising_df = related_queries[keyword]['rising']
                    
                    for index, row in rising_df.iterrows():
                        query = row['query'] if pd.notna(row['query']) else ""
                        value = row['value'] if pd.notna(row['value']) else None
                        
                        if query:
                            result.append({
                                'collection_date': current_time.isoformat(),
                                'trend_type': 'related_rising',
                                'keyword': query,
                                'search_volume': str(value) if value is not None else None,
                                'related_topics': json.dumps({'parent_keyword': keyword}),
                                'region': 'PH',
                                'category': self._classify_keyword(query),
                                'timeframe': timeframe
                            })
                
                # Process top queries
                if ('top' in related_queries[keyword] and 
                    related_queries[keyword]['top'] is not None and
                    not related_queries[keyword]['top'].empty):
                    
                    top_df = related_queries[keyword]['top']
                    
                    for index, row in top_df.iterrows():
                        query = row['query'] if pd.notna(row['query']) else ""
                        value = row['value'] if pd.notna(row['value']) else None
                        
                        if query:
                            result.append({
                                'collection_date': current_time.isoformat(),
                                'trend_type': 'related_top',
                                'keyword': query,
                                'search_volume': str(value) if value is not None else None,
                                'related_topics': json.dumps({'parent_keyword': keyword}),
                                'region': 'PH',
                                'category': self._classify_keyword(query),
                                'timeframe': timeframe
                            })
            
            logger.info(f"Successfully fetched {len(result)} related queries for '{keyword}'")
            
            # Add delay to prevent rate limiting
            time.sleep(Settings.DELAY_BETWEEN_REQUESTS)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching related queries for {keyword}: {e}")
            # Don't raise exception for individual keyword failures
            return []
    
    def get_interest_over_time(self, keywords: List[str], timeframe: str = 'now 7-d') -> List[Dict[str, Any]]:
        """
        Get interest over time for keywords
        
        Args:
            keywords: List of keywords to track
            timeframe: Time range for the search
            
        Returns:
            List of interest over time data
        """
        try:
            logger.info(f"Fetching interest over time for keywords: {keywords}")
            
            # Limit to 5 keywords at a time (Google Trends limitation)
            keywords = keywords[:5]
            
            self.pytrends.build_payload(
                keywords, 
                cat=0, 
                timeframe=timeframe, 
                geo='PH',
                gprop=''
            )
            
            interest_df = self.pytrends.interest_over_time()
            
            result = []
            current_time = datetime.utcnow()
            
            if not interest_df.empty:
                # Get the latest data point for each keyword
                latest_data = interest_df.iloc[-1]
                
                for keyword in keywords:
                    if keyword in latest_data and pd.notna(latest_data[keyword]):
                        result.append({
                            'collection_date': current_time.isoformat(),
                            'trend_type': 'interest_over_time',
                            'keyword': keyword,
                            'search_volume': int(latest_data[keyword]),
                            'related_topics': json.dumps({'timeframe': timeframe}),
                            'region': 'PH',
                            'category': self._classify_keyword(keyword),
                            'timeframe': timeframe
                        })
            
            logger.info(f"Successfully fetched interest over time data: {len(result)} records")
            
            # Add delay to prevent rate limiting
            time.sleep(Settings.DELAY_BETWEEN_REQUESTS)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching interest over time: {e}")
            return []
    
    def _classify_keyword(self, keyword: str) -> str:
        """
        Classify a keyword into a category based on predefined categories
        
        Args:
            keyword: The keyword to classify
            
        Returns:
            Category name or 'general'
        """
        keyword_lower = keyword.lower()
        
        # E-commerce
        if any(term in keyword_lower for term in ['shopee', 'lazada', 'amazon', 'alibaba', 'store', 'shop']):
            return 'ecommerce'
        
        # Beauty & skincare
        elif any(term in keyword_lower for term in ['skincare', 'beauty', 'makeup', 'cosmetic', 'serum', 'moisturizer']):
            return 'beauty_skincare'
        
        # Fashion
        elif any(term in keyword_lower for term in ['fashion', 'clothing', 'dress', 'shirt', 'shoes', 'bag']):
            return 'fashion'
        
        # Electronics & gadgets
        elif any(term in keyword_lower for term in ['iphone', 'samsung', 'laptop', 'phone', 'gadget', 'electronic']):
            return 'electronics'
        
        # Food & restaurants
        elif any(term in keyword_lower for term in ['food', 'restaurant', 'recipe', 'cooking', 'delivery', 'jollibee', 'mcdo']):
            return 'food_dining'
        
        # Travel
        elif any(term in keyword_lower for term in ['travel', 'hotel', 'vacation', 'flight', 'beach', 'resort', 'boracay', 'palawan']):
            return 'travel'
        
        # Health & fitness
        elif any(term in keyword_lower for term in ['health', 'fitness', 'gym', 'workout', 'medicine', 'doctor']):
            return 'health_fitness'
        
        # Education
        elif any(term in keyword_lower for term in ['education', 'school', 'university', 'learning', 'course']):
            return 'education'
        
        # Business & finance
        elif any(term in keyword_lower for term in ['business', 'investment', 'crypto', 'stock', 'money', 'bank', 'gcash', 'paymaya']):
            return 'business_finance'
        
        # Entertainment
        elif any(term in keyword_lower for term in ['netflix', 'youtube', 'tiktok', 'facebook', 'kpop', 'kdrama', 'anime', 'movie']):
            return 'entertainment'
        
        else:
            return 'general'
    
    def collect_all_data(self) -> List[Dict[str, Any]]:
        """
        Collect all Google Trends data: popular keywords + related queries for top categories
        
        Returns:
            Combined list of all collected data
        """
        all_data = []
        
        try:
            logger.info("Starting comprehensive Google Trends data collection...")
            
            # 1. Get popular keywords data (replaces trending searches)
            popular_data = self.get_popular_keywords_data()
            all_data.extend(popular_data)
            
            # 2. Get related queries for top performing keywords
            if popular_data:
                # Sort by search volume and get top 5
                top_keywords = sorted(popular_data, key=lambda x: x['search_volume'], reverse=True)[:5]
                
                for item in top_keywords:
                    keyword = item['keyword']
                    try:
                        related_data = self.get_related_queries(keyword)
                        all_data.extend(related_data)
                        
                        # Extra delay between keyword requests
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.warning(f"Failed to get related queries for keyword '{keyword}': {e}")
                        continue
            
            # 3. Get interest over time for sample of categories
            sample_keywords = ['shopee', 'jollibee', 'skincare', 'bitcoin', 'netflix']
            interest_data = self.get_interest_over_time(sample_keywords)
            all_data.extend(interest_data)
            
            logger.info(f"Google Trends data collection completed. Total records: {len(all_data)}")
            
        except Exception as e:
            logger.error(f"Error in collect_all_data: {e}")
        
        return all_data


def main():
    """Main function for testing the Google Trends scraper"""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize scraper
    scraper = GoogleTrendsScraper()
    
    # Collect data
    print("🔍 Starting Google Trends data collection for Philippines...")
    data = scraper.collect_all_data()
    
    print(f"✅ Collected {len(data)} records from Google Trends")
    
    # Display sample data
    if data:
        print("\n📊 Sample data:")
        for i, item in enumerate(data[:5]):
            print(f"{i+1}. {item['trend_type']}: {item['keyword']} ({item['category']}) - Volume: {item['search_volume']}")
    
    return data


if __name__ == "__main__":
    main() 