"""
Scrapers module for different data sources
"""

# Import only working scrapers for now
# from .shopee import ShopeeScraper  # Temporarily disabled due to import issues

# Working scrapers
try:
    from .lazada_scraper import LazadaScraper
    LAZADA_AVAILABLE = True
except ImportError:
    LAZADA_AVAILABLE = False

# Temporarily disable problematic imports
# from .google_trends import GoogleTrendsScraper
# from .tiktok import TikTokScraper

__all__ = []
if LAZADA_AVAILABLE:
    __all__.append('LazadaScraper') 