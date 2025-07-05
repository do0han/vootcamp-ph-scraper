"""
Test script for Shopee scraper
Run this to test the Shopee Philippines scraper functionality
"""

import logging
from scrapers import ShopeeScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_shopee_scraper():
    """Test the Shopee scraper functionality"""
    print("🛍️ Testing Shopee Scraper...")
    
    # Test keywords
    test_keywords = [
        "linen wide pants",
        "korean skincare", 
        "portable fan"
    ]
    
    scraper = ShopeeScraper(headless=True)  # Use headless mode for automation
    
    try:
        for keyword in test_keywords:
            print(f"\n📱 Testing search for: '{keyword}'")
            
            try:
                products = scraper.search_products(keyword, limit=3)
                
                if products:
                    print(f"✅ Found {len(products)} products")
                    for i, product in enumerate(products, 1):
                        name = product['product_name'][:50]
                        price = product['price']
                        print(f"  {i}. {name}... - {price}")
                else:
                    print(f"⚠️ No products found for '{keyword}'")
                    
            except Exception as e:
                print(f"❌ Error testing '{keyword}': {e}")
                
        print("\n✅ Shopee scraper test completed!")
        
    except Exception as e:
        print(f"❌ Scraper setup failed: {e}")
        
    finally:
        scraper.close()
        print("🔒 WebDriver closed")


if __name__ == "__main__":
    test_shopee_scraper() 