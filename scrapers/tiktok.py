#!/usr/bin/env python3
"""TikTok scraper module for trending hashtag videos from TikTok Philippines."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import json
import random
import logging
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager

from vootcamp_ph_scraper.utils.anti_bot_system import AntiBotSystem
from vootcamp_ph_scraper.utils.ethical_scraping import ScrapingPolicy
from vootcamp_ph_scraper.config.settings import settings
from .base_scraper import BaseScraper

# Import DataAccess
try:
    from database.data_access import DataAccess
    from database.models import TikTokVideo
except ImportError:
    DataAccess = None
    print("⚠️ DataAccess not available - data will not be saved to database")

class TikTokScraper:
    """TikTok data scraper with anti-bot protection for Philippines market."""
    
    def __init__(
        self,
        anti_bot_system: AntiBotSystem,
        scraping_policy: ScrapingPolicy,
        base_url: str = "https://www.tiktok.com",
        request_delay_min: float = 2.0,
        request_delay_max: float = 5.0,
        scroll_delay_min: float = 1.0,
        scroll_delay_max: float = 3.0
    ):
        """Initialize TikTok scraper.
        
        Args:
            anti_bot_system: Anti-bot system instance
            scraping_policy: Ethical scraping policy instance
            base_url: TikTok base URL
            request_delay_min: Minimum delay between requests
            request_delay_max: Maximum delay between requests
            scroll_delay_min: Minimum delay between scrolls
            scroll_delay_max: Maximum delay between scrolls
        """
        self.anti_bot_system = anti_bot_system
        self.scraping_policy = scraping_policy
        self.base_url = base_url
        self.driver = None
        self.user_agent = UserAgent()
        self.logger = logging.getLogger(__name__)
        self.request_delay_min = request_delay_min
        self.request_delay_max = request_delay_max
        self.scroll_delay_min = scroll_delay_min
        self.scroll_delay_max = scroll_delay_max
        
        # Philippines-specific hashtags for trending content
        self.philippines_hashtags = [
            "philippines", "manila", "cebu", "davao", "pinoy", "pinay",
            "filipino", "filipina", "ofw", "pinas", "pilipinas",
            "fyp", "foryou", "viral", "trending"
        ]
    
    def _init_driver(self) -> None:
        """Initialize Selenium WebDriver with enhanced anti-detection."""
        if not self.driver:
            try:
                self.driver = self.anti_bot_system.get_driver()
                self.logger.info("✅ TikTok WebDriver initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize WebDriver: {e}")
                raise
    
    def _close_driver(self) -> None:
        """Close Selenium WebDriver safely."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.logger.info("✅ TikTok WebDriver closed successfully")
            except Exception as e:
                self.logger.warning(f"⚠️ Error closing WebDriver: {e}")
    
    def _human_like_delay(self, min_delay: float = None, max_delay: float = None) -> None:
        """Implement human-like delays between actions."""
        min_delay = min_delay or self.request_delay_min
        max_delay = max_delay or self.request_delay_max
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _human_like_scroll(self, target_scrolls: int = 3) -> None:
        """Perform human-like scrolling to trigger content loading."""
        try:
            for i in range(target_scrolls):
                # Random scroll distance
                scroll_distance = random.randint(300, 800)
                
                # Smooth scroll with random behavior
                self.driver.execute_script(
                    f"window.scrollBy({{top: {scroll_distance}, left: 0, behavior: 'smooth'}});"
                )
                
                # Random pause between scrolls
                time.sleep(random.uniform(self.scroll_delay_min, self.scroll_delay_max))
                
                self.logger.debug(f"Performed scroll {i+1}/{target_scrolls}")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error during scrolling: {e}")
    
    def _extract_video_data(self, video_element) -> Optional[Dict[str, Any]]:
        """Extract data from a single video element with robust error handling."""
        try:
            video_data = {
                "video_id": None,
                "author_username": None,
                "author_name": None,
                "description": None,
                "hashtags": [],
                "video_url": None,
                "music_title": None,
                "view_count": None,
                "like_count": None,
                "comment_count": None,
                "share_count": None,
                "collected_at": datetime.now().isoformat(),
                "source": "tiktok_philippines"
            }
            
            # Try to extract video URL/ID
            try:
                video_link = video_element.find("a")
                if video_link and video_link.get("href"):
                    video_data["video_url"] = video_link["href"]
                    # Extract video ID from URL
                    video_id_match = re.search(r'/video/(\d+)', video_link["href"])
                    if video_id_match:
                        video_data["video_id"] = video_id_match.group(1)
            except:
                pass
            
            # Try to extract author information
            try:
                author_link = video_element.select_one('a[href*="/@"]')
                if author_link:
                    href = author_link.get("href", "")
                    username_match = re.search(r'/@([^/?]+)', href)
                    if username_match:
                        video_data["author_username"] = username_match.group(1)
                
                # Try to get display name
                author_span = video_element.select_one('span[data-e2e="video-author-uniqueid"]')
                if not author_span:
                    author_span = video_element.select_one('p[data-e2e="video-author-uniqueid"]')
                if author_span:
                    video_data["author_name"] = author_span.get_text(strip=True)
            except:
                pass
            
            # Try to extract description/caption
            try:
                desc_element = video_element.select_one('div[data-e2e="video-desc"]')
                if not desc_element:
                    desc_element = video_element.select_one('h1[data-e2e="browse-video-desc"]')
                if desc_element:
                    description = desc_element.get_text(strip=True)
                    video_data["description"] = description
                    
                    # Extract hashtags from description
                    hashtags = re.findall(r'#(\w+)', description)
                    video_data["hashtags"] = hashtags
            except:
                pass
            
            # Try to extract engagement metrics (these are often hidden/dynamic)
            try:
                # Like count
                like_element = video_element.select_one('[data-e2e="like-count"]')
                if like_element:
                    like_text = like_element.get_text(strip=True)
                    video_data["like_count"] = self._parse_count(like_text)
                
                # Comment count
                comment_element = video_element.select_one('[data-e2e="comment-count"]')
                if comment_element:
                    comment_text = comment_element.get_text(strip=True)
                    video_data["comment_count"] = self._parse_count(comment_text)
                
                # Share count
                share_element = video_element.select_one('[data-e2e="share-count"]')
                if share_element:
                    share_text = share_element.get_text(strip=True)
                    video_data["share_count"] = self._parse_count(share_text)
            except:
                pass
            
            # Only return if we got some meaningful data
            if video_data["video_id"] or video_data["author_username"] or video_data["description"]:
                return video_data
            else:
                return None
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error extracting video data: {e}")
            return None
    
    def _parse_count(self, count_text: str) -> Optional[int]:
        """Parse count text (e.g., '1.2K', '5.5M') to integer."""
        try:
            if not count_text:
                return None
            
            count_text = count_text.strip().upper()
            
            # Remove any non-numeric characters except K, M, B, and decimal point
            clean_text = re.sub(r'[^\d.KMB]', '', count_text)
            
            if 'K' in clean_text:
                return int(float(clean_text.replace('K', '')) * 1000)
            elif 'M' in clean_text:
                return int(float(clean_text.replace('M', '')) * 1000000)
            elif 'B' in clean_text:
                return int(float(clean_text.replace('B', '')) * 1000000000)
            else:
                return int(float(clean_text)) if clean_text else None
                
        except:
            return None
    
    def _save_to_database(self, video_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save video data to Supabase database."""
        if not DataAccess:
            self.logger.warning("⚠️ DataAccess not available - skipping database save")
            return None
            
        try:
            # Convert dict to TikTokVideo model
            video = TikTokVideo(
                video_id=video_data["video_id"],
                author_username=video_data["author_username"],
                author_name=video_data["author_name"],
                description=video_data["description"],
                hashtags=video_data["hashtags"],
                video_url=video_data["video_url"],
                music_title=video_data["music_title"],
                view_count=video_data["view_count"],
                like_count=video_data["like_count"],
                comment_count=video_data["comment_count"],
                share_count=video_data["share_count"],
                collected_at=datetime.fromisoformat(video_data["collected_at"]),
                source=video_data["source"]
            )
            
            # Save to database
            result = DataAccess.insert_tiktok_video(video)
            self.logger.info(f"✅ Saved video {video.video_id} to database")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save video to database: {e}")
            return None
    
    def scrape_hashtag_videos(self, hashtag: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape videos for a specific hashtag with database integration."""
        videos = []
        try:
            self._init_driver()
            url = f"{self.base_url}/tag/{hashtag}"
            
            self.driver.get(url)
            self._human_like_delay()
            
            while len(videos) < limit:
                self._human_like_scroll()
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                video_elements = soup.select('div[data-e2e="recommend-list-item-container"]')
                
                for video_element in video_elements:
                    if len(videos) >= limit:
                        break
                        
                    video_data = self._extract_video_data(video_element)
                    if video_data:
                        # Save to database
                        saved_data = self._save_to_database(video_data)
                        if saved_data:
                            videos.append(saved_data)
                        else:
                            videos.append(video_data)
                
                if not video_elements:
                    break
                    
            return videos[:limit]
            
        except Exception as e:
            self.logger.error(f"❌ Error scraping hashtag {hashtag}: {e}")
            return videos
        finally:
            self.cleanup()
    
    def get_philippines_trending_videos(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trending videos from Philippines with database integration."""
        all_videos = []
        videos_per_hashtag = max(5, limit // len(self.philippines_hashtags))
        
        for hashtag in self.philippines_hashtags:
            try:
                videos = self.scrape_hashtag_videos(hashtag, limit=videos_per_hashtag)
                all_videos.extend(videos)
                
                if len(all_videos) >= limit:
                    break
                    
            except Exception as e:
                self.logger.error(f"❌ Error getting trending videos for #{hashtag}: {e}")
                continue
                
        return all_videos[:limit]
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self._close_driver()
    
    # === SIMPLE FALLBACK METHODS FOR MAIN.PY INTEGRATION ===
    
    def search_hashtag_videos(self, hashtag: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Simple fallback method for main.py integration.
        
        This provides a simpler interface that matches the expected signature
        from main.py while utilizing the more advanced scrape_hashtag_videos method.
        
        Args:
            hashtag: Target hashtag (without # symbol)
            limit: Maximum number of videos to collect
            
        Returns:
            List of video data dictionaries
        """
        try:
            return self.scrape_hashtag_videos(hashtag, limit)
        except Exception as e:
            self.logger.error(f"❌ Error in search_hashtag_videos: {e}")
            return []
    
    def get_trending_videos(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending videos from popular hashtags.
        
        Args:
            limit: Maximum number of videos to collect
            
        Returns:
            List of video data dictionaries
        """
        try:
            # Use a subset of popular hashtags for faster execution
            trending_hashtags = ["fyp", "viral", "trending", "philippines", "pinoy"]
            videos_per_hashtag = max(1, limit // len(trending_hashtags))
            
            all_videos = []
            for hashtag in trending_hashtags:
                if len(all_videos) >= limit:
                    break
                    
                self.logger.info(f"🔥 Getting trending videos from #{hashtag}")
                videos = self.scrape_hashtag_videos(hashtag, videos_per_hashtag)
                
                if videos:
                    all_videos.extend(videos)
                    self.logger.info(f"✅ Added {len(videos)} videos from #{hashtag}")
                
                # Small delay between hashtags
                if hashtag != trending_hashtags[-1]:
                    self._human_like_delay(3, 6)
            
            # Remove duplicates
            unique_videos = []
            seen_ids = set()
            
            for video in all_videos:
                video_id = video.get('video_id')
                if video_id and video_id not in seen_ids:
                    unique_videos.append(video)
                    seen_ids.add(video_id)
                elif not video_id:
                    unique_videos.append(video)
            
            self.logger.info(f"🎉 Total trending videos collected: {len(unique_videos)}")
            return unique_videos[:limit]
            
        except Exception as e:
            self.logger.error(f"❌ Error getting trending videos: {e}")
            return []
