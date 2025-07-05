"""
Enhanced Section Detector for Shopee
Uses advanced techniques to detect dynamic content
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json

def setup_enhanced_driver():
    """Setup Chrome WebDriver with enhanced options for dynamic content"""
    options = Options()
    # Use non-headless mode for better JavaScript execution
    # options.add_argument('--headless=new')  # Comment out for testing
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Enhanced options for JavaScript-heavy sites
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')  # Faster loading
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    
    # Fix chromedriver path
    driver_path = '/Users/DoohanIT/.wdm/drivers/chromedriver/mac64/138.0.7204.49/chromedriver-mac-arm64/THIRD_PARTY_NOTICES.chromedriver'
    service = Service(driver_path)
    
    driver = webdriver.Chrome(service=service, options=options)
    
    # Set longer timeouts
    driver.set_page_load_timeout(120)
    driver.implicitly_wait(10)
    
    # Execute script to hide webdriver detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def wait_for_dynamic_content(driver, max_wait=60):
    """Wait for dynamic content to load with multiple strategies"""
    print(f"⏳ Waiting for dynamic content (max {max_wait}s)...")
    
    start_time = time.time()
    
    # Strategy 1: Wait for document ready state
    try:
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("✅ Document ready state: complete")
    except TimeoutException:
        print("⚠️ Document ready state timeout")
    
    # Strategy 2: Wait for network idle (no network requests for 2 seconds)
    print("🌐 Waiting for network idle...")
    time.sleep(15)  # Wait for initial load
    
    # Strategy 3: Look for React/Vue mounting indicators
    try:
        # Check if React is loaded
        react_loaded = driver.execute_script("return typeof React !== 'undefined'")
        if react_loaded:
            print("⚛️ React detected, waiting for component mounting...")
            time.sleep(10)
    except:
        pass
    
    # Strategy 4: Progressive element discovery
    previous_element_count = 0
    stable_count = 0
    
    for i in range(6):  # Check 6 times, 5 seconds apart
        current_elements = len(driver.find_elements(By.CSS_SELECTOR, "*"))
        print(f"📊 Elements found: {current_elements}")
        
        if current_elements == previous_element_count:
            stable_count += 1
        else:
            stable_count = 0
            
        if stable_count >= 2:
            print("✅ DOM appears stable")
            break
            
        previous_element_count = current_elements
        time.sleep(5)
    
    elapsed = time.time() - start_time
    print(f"⏱️ Total wait time: {elapsed:.1f}s")

def enhanced_section_detection(driver):
    """Enhanced section detection with multiple strategies"""
    print("\n🔍 Enhanced Section Detection Starting...")
    
    # Strategy 1: Look for any elements containing flash/deal text
    print("\n🔥 Strategy 1: Text-based search for Flash/Deal content...")
    text_patterns = ['flash', 'deal', 'sale', 'trending', 'popular', 'hot']
    
    found_elements = {}
    
    for pattern in text_patterns:
        try:
            # XPath to find any element containing the text (case insensitive)
            xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{pattern}')]"
            elements = driver.find_elements(By.XPATH, xpath)
            
            if elements:
                print(f"   ✅ Found {len(elements)} elements containing '{pattern}'")
                found_elements[pattern] = elements[:3]  # Keep first 3
                
                # Sample the first element
                try:
                    sample_text = elements[0].text[:100]
                    print(f"      Sample text: {sample_text}...")
                except:
                    print(f"      Sample text: [Unable to extract]")
            else:
                print(f"   ❌ No elements found for '{pattern}'")
                
        except Exception as e:
            print(f"   ⚠️ Error searching for '{pattern}': {e}")
    
    # Strategy 2: Look for common e-commerce section patterns
    print("\n🛍️ Strategy 2: E-commerce pattern search...")
    section_selectors = [
        'div[class*="section"]',
        'div[class*="container"]',
        'div[class*="row"]',
        'div[class*="grid"]',
        'div[class*="carousel"]',
        'div[class*="slider"]',
        'div[class*="product"]',
        'div[class*="item"]',
        'main',
        'article',
        '[role="main"]',
        '[role="region"]'
    ]
    
    for selector in section_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"   ✅ Found {len(elements)} elements with selector: {selector}")
        except Exception as e:
            print(f"   ⚠️ Error with selector {selector}: {e}")
    
    # Strategy 3: JavaScript execution to find dynamic sections
    print("\n⚡ Strategy 3: JavaScript-based detection...")
    try:
        # Execute JavaScript to find sections
        js_script = """
        var sections = [];
        
        // Find all divs
        var allDivs = document.querySelectorAll('div');
        
        for (var i = 0; i < allDivs.length; i++) {
            var div = allDivs[i];
            var text = div.textContent.toLowerCase();
            var className = div.className.toLowerCase();
            
            // Check for flash/deal/trending keywords
            if (text.includes('flash') || text.includes('deal') || 
                text.includes('trending') || text.includes('popular') ||
                className.includes('flash') || className.includes('deal') ||
                className.includes('trending') || className.includes('popular')) {
                
                sections.push({
                    tag: div.tagName,
                    className: div.className,
                    text: text.substring(0, 100),
                    id: div.id
                });
            }
        }
        
        return sections;
        """
        
        js_results = driver.execute_script(js_script)
        
        if js_results:
            print(f"   ✅ JavaScript found {len(js_results)} potential sections")
            for i, section in enumerate(js_results[:3]):
                print(f"      {i+1}. Tag: {section['tag']}, Class: {section['className'][:50]}")
        else:
            print("   ❌ JavaScript found no matching sections")
            
    except Exception as e:
        print(f"   ⚠️ JavaScript detection error: {e}")
    
    return found_elements

def comprehensive_page_analysis(driver):
    """Comprehensive analysis of page structure"""
    print("\n📊 Comprehensive Page Analysis...")
    
    try:
        # Get page info
        url = driver.current_url
        title = driver.title
        print(f"📄 Page: {title}")
        print(f"🔗 URL: {url}")
        
        # Count all elements
        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        print(f"🔢 Total elements: {len(all_elements)}")
        
        # Count by tag type
        common_tags = ['div', 'span', 'a', 'img', 'button', 'section', 'article', 'main']
        
        for tag in common_tags:
            elements = driver.find_elements(By.TAG_NAME, tag)
            if elements:
                print(f"   - {tag}: {len(elements)}")
        
        # Look for data attributes
        data_attrs = ['data-testid', 'data-test', 'data-id', 'data-section', 'data-component']
        
        for attr in data_attrs:
            elements = driver.find_elements(By.CSS_SELECTOR, f"[{attr}]")
            if elements:
                print(f"   - Elements with {attr}: {len(elements)}")
        
        # Look for specific content
        print("\n🔍 Content Analysis:")
        page_source = driver.page_source.lower()
        
        keywords = ['flash sale', 'trending', 'popular', 'hot deals', 'recommendations']
        for keyword in keywords:
            count = page_source.count(keyword)
            if count > 0:
                print(f"   - '{keyword}' appears {count} times")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def main():
    """Main enhanced detection function"""
    driver = setup_enhanced_driver()
    
    try:
        print("🏠 Navigating to Shopee Philippines...")
        driver.get('https://shopee.ph/')
        
        # Enhanced waiting
        wait_for_dynamic_content(driver, 60)
        
        # Comprehensive analysis
        comprehensive_page_analysis(driver)
        
        # Enhanced section detection
        found_sections = enhanced_section_detection(driver)
        
        # Save results
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'found_sections': {k: len(v) for k, v in found_sections.items()},
            'url': driver.current_url,
            'title': driver.title
        }
        
        with open('enhanced_detection_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to enhanced_detection_results.json")
        
    except Exception as e:
        print(f"❌ Main error: {e}")
    finally:
        input("\n⏸️ Press Enter to close browser (you can inspect manually)...")
        driver.quit()
        print("🔒 Browser closed")

if __name__ == "__main__":
    main() 