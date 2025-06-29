"""
Integration tests for the Vootcamp PH Data Scraper system.
Tests the complete integration of all components.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Mock Supabase client
mock_supabase = Mock()
mock_supabase_client = Mock()
mock_supabase_client.client = mock_supabase

with patch('vootcamp_ph_scraper.database.supabase_client.SupabaseClient', return_value=mock_supabase_client), \
     patch.dict('os.environ', {'SUPABASE_URL': 'http://test.com', 'SUPABASE_KEY': 'test_key'}):
    
    from vootcamp_ph_scraper.utils.anti_bot_system import AntiBotSystem
    from vootcamp_ph_scraper.utils.anti_bot import AntiBotConfig
    from vootcamp_ph_scraper.utils.ethical_scraping import ScrapingPolicy
    from vootcamp_ph_scraper.scrapers.google_trends import GoogleTrendsScraper
    from vootcamp_ph_scraper.scrapers.shopee_scraper import ShopeeScraper
    from vootcamp_ph_scraper.scrapers.tiktok import TikTokScraper
    from vootcamp_ph_scraper.database.supabase_client import SupabaseClient

class TestIntegration(unittest.TestCase):
    """통합 테스트 클래스"""

    @classmethod
    def setUpClass(cls):
        """테스트 클래스 설정"""
        cls.anti_bot = AntiBotSystem()
        cls.scraping_policy = ScrapingPolicy()
        cls.google_trends = GoogleTrendsScraper()
        cls.shopee = ShopeeScraper()
        cls.tiktok = TikTokScraper()

    def test_anti_bot_system(self):
        """안티봇 시스템 테스트"""
        self.assertIsNotNone(self.anti_bot)
        self.assertIsInstance(self.anti_bot, AntiBotSystem)

    def test_scraping_policy(self):
        """스크래핑 정책 테스트"""
        self.assertIsNotNone(self.scraping_policy)
        self.assertIsInstance(self.scraping_policy, ScrapingPolicy)

    def test_google_trends_scraper(self):
        """Google Trends 스크래퍼 테스트"""
        self.assertIsNotNone(self.google_trends)
        self.assertIsInstance(self.google_trends, GoogleTrendsScraper)

    def test_shopee_scraper(self):
        """Shopee 스크래퍼 테스트"""
        self.assertIsNotNone(self.shopee)
        self.assertIsInstance(self.shopee, ShopeeScraper)

    def test_tiktok_scraper(self):
        """TikTok 스크래퍼 테스트"""
        self.assertIsNotNone(self.tiktok)
        self.assertIsInstance(self.tiktok, TikTokScraper)

if __name__ == '__main__':
    unittest.main() 