"""
Debug Shopee page structure to understand selectors
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def debug_shopee():
    """Debug Shopee page structure"""
    # Setup Chrome
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Fix chromedriver path
    driver_path = '/Users/DoohanIT/.wdm/drivers/chromedriver/mac64/138.0.7204.49/chromedriver-mac-arm64/THIRD_PARTY_NOTICES.chromedriver'
    service = Service(driver_path)
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # Navigate to Shopee search
        url = 'https://shopee.ph/search?keyword=laptop'
        print(f"🔍 Navigating to: {url}")
        driver.get(url)
        
        print("⏳ Waiting for page to load...")
        time.sleep(10)  # Wait longer for JavaScript
        
        # Get page title
        title = driver.title
        print(f"📄 Page title: {title}")
        
        # Try more generic selectors
        selectors = [
            'div[data-sqe="item"]',
            'a[href*="/product/"]',
            'div[role="button"]',
            'div.item-card-wrapper',
            'div[class*="item"]',
            'div[class*="product"]',
            'a[class*="link"]',
            'img[src*="product"]',
            'div[class*="col"]'
        ]
        
        print("\n🔍 Testing selectors...")
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"✅ '{selector}': {len(elements)} elements")
                
                if elements and len(elements) > 2:  # Found multiple elements
                    print(f"   First element text: {elements[0].text[:50]}...")
                    print(f"   First element HTML: {elements[0].get_attribute('outerHTML')[:100]}...")
                    
            except Exception as e:
                print(f"❌ '{selector}': {e}")
        
        # Look for any images that might be products
        print("\n🖼️ Looking for images...")
        images = driver.find_elements(By.TAG_NAME, 'img')
        print(f"Found {len(images)} images")
        
        # Check page source for clues
        source = driver.page_source
        print(f"\n📝 Page source length: {len(source)} characters")
        
        # Search for common patterns
        patterns = ['item-card', 'product-item', 'search-item', 'grid-item', 'data-sqe']
        for pattern in patterns:
            if pattern in source:
                print(f"✅ Found '{pattern}' in source")
                # Extract a snippet around the pattern
                index = source.find(pattern)
                snippet = source[max(0, index-50):index+100]
                print(f"   Context: ...{snippet}...")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_shopee() 