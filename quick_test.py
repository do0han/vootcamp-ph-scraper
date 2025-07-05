"""
Quick test for Shopee scraper with fallback to requests
"""

import logging
from scrapers import ShopeeScraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def quick_test():
    """Quick test of Shopee scraper with fallback"""
    print("🛍️ Quick Shopee Test (with fallback)...")
    
    # Initialize scraper with requests fallback
    scraper = ShopeeScraper(headless=True, use_selenium=False)  # Skip selenium for now
    
    try:
        # Test with one keyword
        keyword = "laptop"
        print(f"\n📱 Testing search for: '{keyword}'")
        
        products = scraper.search_products(keyword, limit=3)
        
        if products:
            print(f"✅ Found {len(products)} products:")
            for i, product in enumerate(products):
                print(f"  {i+1}. {product['product_name']}")
                print(f"     Price: {product['price']}")
                print(f"     URL: {product['product_url']}")
        else:
            print("⚠️ No products found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()
        print("🔒 Test completed!")

if __name__ == "__main__":
    quick_test() 