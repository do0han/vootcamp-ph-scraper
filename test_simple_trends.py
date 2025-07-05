"""
Simple Google Trends test to diagnose issues
"""

from pytrends.request import TrendReq
import pandas as pd

def test_basic_trends():
    """Test basic pytrends functionality"""
    print("🔍 Testing basic pytrends functionality...")
    
    try:
        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=360)
        print("✅ pytrends initialized")
        
        # Test with a simple keyword search
        print("📊 Testing interest by region...")
        pytrends.build_payload(['python'], cat=0, timeframe='today 5-y', geo='', gprop='')
        
        # Get interest by region
        interest_by_region = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
        print(f"✅ Got {len(interest_by_region)} countries data")
        
        # Check if Philippines is in the data
        if 'Philippines' in interest_by_region.index:
            ph_value = interest_by_region.loc['Philippines']['python']
            print(f"✅ Philippines data found: {ph_value}")
        else:
            print("⚠️ Philippines not found in region data")
            print("Available regions:", list(interest_by_region.index)[:10])
        
        # Test with Philippines-specific query
        print("\n📊 Testing Philippines-specific query...")
        pytrends.build_payload(['jollibee'], cat=0, timeframe='now 7-d', geo='PH', gprop='')
        
        interest_over_time = pytrends.interest_over_time()
        if not interest_over_time.empty:
            print(f"✅ Philippines-specific query successful: {len(interest_over_time)} data points")
        else:
            print("⚠️ No data returned for Philippines-specific query")
        
        # Test related queries instead of trending searches
        print("\n🔗 Testing related queries...")
        related_queries = pytrends.related_queries()
        if 'jollibee' in related_queries and related_queries['jollibee']['top'] is not None:
            top_queries = related_queries['jollibee']['top']
            print(f"✅ Related queries successful: {len(top_queries)} queries found")
            print("Sample queries:", list(top_queries['query'][:3]))
        else:
            print("⚠️ No related queries found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_alternative_methods():
    """Test alternative methods for getting Philippines data"""
    print("\n🔍 Testing alternative methods...")
    
    try:
        pytrends = TrendReq(hl='en-PH', tz=480)
        
        # Try some Philippines-popular keywords
        ph_keywords = ['shopee', 'lazada', 'gcash', 'jollibee', 'sm mall']
        
        for keyword in ph_keywords:
            try:
                print(f"Testing keyword: {keyword}")
                pytrends.build_payload([keyword], cat=0, timeframe='now 1-d', geo='PH', gprop='')
                
                # Get interest over time
                interest = pytrends.interest_over_time()
                if not interest.empty:
                    print(f"  ✅ {keyword}: {len(interest)} data points")
                    
                    # Get related queries
                    related = pytrends.related_queries()
                    if keyword in related and related[keyword]['top'] is not None:
                        print(f"  ✅ {keyword}: {len(related[keyword]['top'])} related queries")
                    
                    # Success with this keyword, we can work with it
                    return keyword
                else:
                    print(f"  ⚠️ {keyword}: No data")
                    
            except Exception as e:
                print(f"  ❌ {keyword}: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ Alternative methods failed: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Simple Google Trends Diagnostic Test")
    print("=" * 50)
    
    # Test basic functionality
    basic_ok = test_basic_trends()
    
    if basic_ok:
        # Test alternative methods
        working_keyword = test_alternative_methods()
        
        if working_keyword:
            print(f"\n✅ Found working approach with keyword: {working_keyword}")
            print("💡 The issue is with trending_searches(), but we can use related_queries() instead")
        else:
            print("\n⚠️ Alternative methods also had issues")
    
    print("\n💡 Diagnosis complete!") 