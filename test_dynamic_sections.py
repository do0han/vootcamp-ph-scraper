"""
Test script for dynamic section locators
Tests the new Flash Deals and Trending Products section locator methods
"""

import logging
from scrapers import ShopeeScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_dynamic_section_locators():
    """Test the dynamic section locator methods"""
    print("🔍 Testing Dynamic Section Locators...")
    
    # Initialize scraper with selenium
    scraper = ShopeeScraper(headless=True, use_selenium=True)
    
    try:
        print("\n🏠 Navigating to Shopee main page...")
        
        # Test individual section locators
        print("\n🔥 Testing Flash Deals section locator...")
        flash_section = scraper.locate_flash_deals_section()
        
        if flash_section:
            print("✅ Flash Deals section found!")
            print(f"   Element tag: {flash_section.tag_name}")
            try:
                print(f"   Element text preview: {flash_section.text[:100]}...")
            except:
                print("   Element text: [Unable to extract]")
        else:
            print("❌ Flash Deals section not found")
        
        print("\n📈 Testing Trending Products section locator...")
        trending_section = scraper.locate_trending_section()
        
        if trending_section:
            print("✅ Trending Products section found!")
            print(f"   Element tag: {trending_section.tag_name}")
            try:
                print(f"   Element text preview: {trending_section.text[:100]}...")
            except:
                print("   Element text: [Unable to extract]")
        else:
            print("❌ Trending Products section not found")
        
        # Test combined method
        print("\n🔧 Testing combined dynamic sections locator...")
        sections = scraper.locate_dynamic_sections()
        
        print("\n📊 Results Summary:")
        for section_name, section_element in sections.items():
            status = "✅ Found" if section_element else "❌ Not found"
            print(f"  - {section_name}: {status}")
        
        return sections
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return None
    finally:
        scraper.close()
        print("\n🔒 Test completed and driver closed!")

def test_section_analysis():
    """Analyze what sections we can actually find"""
    print("\n🔬 Additional Section Analysis...")
    
    scraper = ShopeeScraper(headless=True, use_selenium=True)
    
    try:
        # Navigate to main page
        scraper._setup_driver()
        scraper.driver.get('https://shopee.ph/')
        scraper._wait_for_page_load(10)
        
        # Look for any sections
        print("\n📋 Looking for all sections on page...")
        sections = scraper.driver.find_elements("css selector", "section")
        print(f"   Found {len(sections)} section elements")
        
        # Look for divs with data attributes
        print("\n🏷️ Looking for elements with data-testid attributes...")
        data_elements = scraper.driver.find_elements("css selector", "[data-testid]")
        print(f"   Found {len(data_elements)} elements with data-testid")
        
        # Sample some data-testid values
        if data_elements:
            print("   Sample data-testid values:")
            for i, element in enumerate(data_elements[:5]):
                try:
                    testid = element.get_attribute('data-testid')
                    print(f"     {i+1}. {testid}")
                except:
                    print(f"     {i+1}. [Unable to extract]")
        
        # Look for carousels (common for flash deals/trending)
        print("\n🎠 Looking for carousel elements...")
        carousel_selectors = [
            "[class*='carousel']",
            "[class*='slider']",
            "[class*='swiper']"
        ]
        
        for selector in carousel_selectors:
            elements = scraper.driver.find_elements("css selector", selector)
            if elements:
                print(f"   Found {len(elements)} elements with selector: {selector}")
        
    except Exception as e:
        print(f"❌ Error in section analysis: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    # Test the dynamic section locators
    sections = test_dynamic_section_locators()
    
    # Additional analysis
    test_section_analysis() 