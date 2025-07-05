"""
Shopee Structure Analyzer
Analyze the HTML structure of Flash Deals and Trending Products sections
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re

def setup_driver():
    """Setup Chrome WebDriver with stealth options"""
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Fix chromedriver path
    driver_path = '/Users/DoohanIT/.wdm/drivers/chromedriver/mac64/138.0.7204.49/chromedriver-mac-arm64/THIRD_PARTY_NOTICES.chromedriver'
    service = Service(driver_path)
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def analyze_main_page_structure(driver):
    """Analyze Shopee main page structure for Flash Deals and Trending Products"""
    print("🔍 Analyzing Shopee main page structure...")
    
    try:
        # Navigate to Shopee Philippines
        driver.get('https://shopee.ph/')
        print("✅ Loaded Shopee main page")
        
        # Wait for page to load
        time.sleep(5)
        
        # Get page source
        page_source = driver.page_source
        print(f"📄 Page source length: {len(page_source)} characters")
        
        # Look for Flash Deals related content
        print("\n🔥 Looking for Flash Deals patterns...")
        flash_deals_patterns = [
            'flash',
            'Flash',
            'FLASH',
            'flashsale',
            'flash-sale',
            'flash_sale',
            'deal',
            'Deal',
            'DEAL'
        ]
        
        flash_found = []
        for pattern in flash_deals_patterns:
            if pattern in page_source:
                # Find surrounding context
                matches = re.finditer(re.escape(pattern), page_source, re.IGNORECASE)
                for match in list(matches)[:3]:  # Limit to first 3 matches
                    start = max(0, match.start() - 100)
                    end = min(len(page_source), match.end() + 100)
                    context = page_source[start:end]
                    flash_found.append({
                        'pattern': pattern,
                        'context': context
                    })
        
        if flash_found:
            print(f"✅ Found {len(flash_found)} Flash Deals patterns")
            for i, finding in enumerate(flash_found[:3]):
                print(f"  {i+1}. Pattern '{finding['pattern']}':")
                print(f"     Context: {finding['context'][:100]}...")
        else:
            print("❌ No Flash Deals patterns found")
        
        # Look for Trending Products related content
        print("\n📈 Looking for Trending Products patterns...")
        trending_patterns = [
            'trending',
            'Trending',
            'TRENDING',
            'popular',
            'Popular',
            'POPULAR',
            'trend',
            'Trend',
            'TREND'
        ]
        
        trending_found = []
        for pattern in trending_patterns:
            if pattern in page_source:
                matches = re.finditer(re.escape(pattern), page_source, re.IGNORECASE)
                for match in list(matches)[:3]:
                    start = max(0, match.start() - 100)
                    end = min(len(page_source), match.end() + 100)
                    context = page_source[start:end]
                    trending_found.append({
                        'pattern': pattern,
                        'context': context
                    })
        
        if trending_found:
            print(f"✅ Found {len(trending_found)} Trending Products patterns")
            for i, finding in enumerate(trending_found[:3]):
                print(f"  {i+1}. Pattern '{finding['pattern']}':")
                print(f"     Context: {finding['context'][:100]}...")
        else:
            print("❌ No Trending Products patterns found")
        
        # Look for common e-commerce section patterns
        print("\n🛍️ Looking for general section patterns...")
        section_patterns = [
            'data-testid',
            'section',
            'div class=',
            'carousel',
            'grid',
            'list',
            'product',
            'item'
        ]
        
        for pattern in section_patterns:
            count = page_source.count(pattern)
            if count > 0:
                print(f"  - Found '{pattern}': {count} occurrences")
        
        return {
            'flash_deals': flash_found,
            'trending_products': trending_found,
            'page_length': len(page_source)
        }
        
    except Exception as e:
        print(f"❌ Error analyzing page structure: {e}")
        return None

def analyze_dom_elements(driver):
    """Analyze DOM elements for potential Flash Deals and Trending sections"""
    print("\n🔧 Analyzing DOM elements...")
    
    try:
        # Look for common container elements
        containers = []
        
        # Check for sections with specific attributes
        test_selectors = [
            "[data-testid*='flash']",
            "[data-testid*='deal']", 
            "[data-testid*='trending']",
            "[data-testid*='popular']",
            "[class*='flash']",
            "[class*='deal']",
            "[class*='trending']",
            "[class*='popular']",
            "section",
            "[role='region']",
            ".shopee-carousel",
            ".shopee-section"
        ]
        
        for selector in test_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    containers.append({
                        'selector': selector,
                        'count': len(elements),
                        'sample_html': elements[0].get_attribute('outerHTML')[:200] if elements else None
                    })
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")
        
        return containers
        
    except Exception as e:
        print(f"❌ Error analyzing DOM elements: {e}")
        return []

def main():
    """Main analysis function"""
    driver = setup_driver()
    
    try:
        # Analyze page structure
        structure_analysis = analyze_main_page_structure(driver)
        
        # Analyze DOM elements
        dom_analysis = analyze_dom_elements(driver)
        
        # Save results
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'structure_analysis': structure_analysis,
            'dom_analysis': dom_analysis
        }
        
        with open('shopee_structure_analysis.json', 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Analysis complete! Results saved to shopee_structure_analysis.json")
        
        # Summary
        print("\n📋 Summary:")
        if structure_analysis:
            print(f"  - Flash Deals patterns found: {len(structure_analysis.get('flash_deals', []))}")
            print(f"  - Trending Products patterns found: {len(structure_analysis.get('trending_products', []))}")
        print(f"  - DOM containers analyzed: {len(dom_analysis)}")
        
    except Exception as e:
        print(f"❌ Error in main analysis: {e}")
    finally:
        driver.quit()
        print("🔒 Driver closed")

if __name__ == "__main__":
    main() 