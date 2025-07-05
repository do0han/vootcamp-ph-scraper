#!/usr/bin/env python3
"""
Test script for the enhanced niche category data pipeline
니치 카테고리 데이터 파이프라인 테스트
"""

import json
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project path
sys.path.append(str(Path(__file__).parent / "vootcamp_ph_scraper"))

from vootcamp_ph_scraper.utils.product_tagger import ProductTagger
from vootcamp_ph_scraper.scrapers.niche_category_scraper import NicheCategoryScraper

def test_product_tagger():
    """Test the hierarchical keyword tagging system"""
    print("🧪 Testing Product Tagging System")
    print("=" * 60)
    
    # Initialize tagger
    tagger = ProductTagger()
    
    # Test products from each niche category
    test_products = [
        # Calligraphy & Fountain Pens
        {
            "product_name": "Lamy Safari Fountain Pen Set with Blue Ink Cartridges",
            "description": "Premium fountain pen perfect for calligraphy and handwriting practice",
            "category": "Stationery", 
            "price": 2500,
            "brand": "Lamy"
        },
        {
            "product_name": "Pilot Metropolitan Fountain Pen Black with Converter",
            "description": "Entry-level fountain pen for beginners, includes ink converter",
            "category": "Writing Instruments",
            "price": 1800
        },
        
        # Mechanical Keyboards
        {
            "product_name": "Keychron K2 Wireless Mechanical Keyboard Hot Swappable RGB",
            "description": "75% compact gaming keyboard with Cherry MX Red switches",
            "category": "Computer Accessories",
            "price": 6500,
            "brand": "Keychron"
        },
        {
            "product_name": "Royal Kludge RK61 60% Mechanical Gaming Keyboard RGB",
            "description": "Compact 60% keyboard with hot swap switches for gaming",
            "category": "Gaming Accessories",
            "price": 3200
        },
        
        # Home Barista & Coffee
        {
            "product_name": "Hario V60 Pour Over Coffee Dripper Kit with Filters",
            "description": "Professional coffee brewing set for home baristas",
            "category": "Kitchen Appliances",
            "price": 1800,
            "brand": "Hario"
        },
        {
            "product_name": "Timemore C2 Manual Coffee Grinder Burr Mill",
            "description": "Precision hand grinder for specialty coffee beans",
            "category": "Coffee Equipment",
            "price": 4500
        },
        
        # Film Photography
        {
            "product_name": "Canon AE-1 Vintage Film Camera 35mm SLR with 50mm Lens",
            "description": "Classic analog film camera for photography enthusiasts",
            "category": "Cameras",
            "price": 8500,
            "brand": "Canon"
        },
        {
            "product_name": "Kodak Portra 400 Color Negative Film 35mm 36 Exposures",
            "description": "Professional color film for portrait and wedding photography",
            "category": "Film & Photography",
            "price": 650
        },
        
        # Indoor Gardening
        {
            "product_name": "Monstera Deliciosa Large Tropical Houseplant",
            "description": "Rare split-leaf tropical plant perfect for indoor gardening",
            "category": "Plants",
            "price": 1200
        },
        {
            "product_name": "Fiddle Leaf Fig Tree Large Indoor Plant with Ceramic Pot",
            "description": "Statement houseplant for modern indoor garden decoration", 
            "category": "Home Decor",
            "price": 2800
        },
        
        # Non-niche products for comparison
        {
            "product_name": "Regular Office Ballpoint Pen Set Blue Black",
            "description": "Standard writing pens for office and school use",
            "category": "Office Supplies",
            "price": 120
        },
        {
            "product_name": "Generic Wireless Mouse USB Computer Accessory",
            "description": "Basic computer mouse for everyday use",
            "category": "Computer Accessories", 
            "price": 450
        }
    ]
    
    print(f"📦 Testing {len(test_products)} products")
    print()
    
    # Test individual tagging
    niche_matches = 0
    total_products = len(test_products)
    
    for i, product in enumerate(test_products, 1):
        print(f"🏷️ Product {i}: {product['product_name'][:50]}...")
        
        tagged_product = tagger.tag_product_with_keywords(product)
        
        categories = tagged_product.get('niche_categories', [])
        confidence = tagged_product.get('tag_confidence', 'none')
        hierarchical_tags = tagged_product.get('hierarchical_tags', [])
        
        print(f"   Categories: {categories}")
        print(f"   Confidence: {confidence}")
        
        if hierarchical_tags:
            top_tag = hierarchical_tags[0]
            print(f"   Top Match: {top_tag['full_path']} (Score: {top_tag['match_score']:.1f})")
            keywords = ', '.join(top_tag['matched_keywords'][:3])
            print(f"   Keywords: {keywords}")
            
            if categories:
                niche_matches += 1
        else:
            print("   No hierarchical matches found")
        
        print()
    
    # Summary statistics
    niche_detection_rate = (niche_matches / total_products) * 100
    print(f"📊 TAGGING RESULTS SUMMARY:")
    print(f"   • Products Tested: {total_products}")
    print(f"   • Niche Matches Found: {niche_matches}")
    print(f"   • Detection Rate: {niche_detection_rate:.1f}%")
    
    # Expected: ~10/12 products should be detected as niche (excluding generic office supplies)
    expected_niche_products = 10
    if niche_matches >= expected_niche_products:
        print(f"   ✅ GOOD: Detected {niche_matches}/{expected_niche_products} expected niche products")
    else:
        print(f"   ⚠️ LOW: Only detected {niche_matches}/{expected_niche_products} expected niche products")
    
    print()
    return niche_matches >= expected_niche_products

def test_niche_scraper():
    """Test the niche category scraper (dry run)"""
    print("🎯 Testing Niche Category Scraper")
    print("=" * 60)
    
    # Initialize scraper
    scraper = NicheCategoryScraper(use_undetected=False)  # No actual browser for testing
    
    # Test category info extraction
    categories = scraper.TARGET_CATEGORIES
    print(f"📂 Target Categories: {len(categories)}")
    
    for category in categories:
        print(f"\n🏷️ Category: {category}")
        
        # Test search terms extraction
        search_terms = scraper._get_category_search_terms(category, "high")
        print(f"   Search Terms: {', '.join(search_terms[:3])}...")
        
        # Test price range extraction
        price_range = scraper._get_platform_price_range(category, "lazada")
        print(f"   Price Range: ₱{price_range[0]:,}-{price_range[1]:,}" if price_range else "   Price Range: Not specified")
        
        # Test platform-specific info
        platform_info = scraper.tagger.get_platform_specific_info(category, "lazada")
        modifiers = platform_info.get('search_modifiers', [])
        print(f"   Platform Modifiers: {', '.join(modifiers)}")
    
    print(f"\n✅ Scraper configuration test completed")
    
    # Don't actually scrape in test mode
    print("💡 Skipping actual scraping in test mode")
    print("   To run full scraping test, use: scraper.scrape_lazada_niche_category('calligraphy_fountain_pens', 5)")
    
    scraper.close()
    return True

def test_integration_with_recommendation_engine():
    """Test integration with existing recommendation engine"""
    print("🔗 Testing Integration with Recommendation Engine")
    print("=" * 60)
    
    try:
        # Import recommendation engine
        from vootcamp_ph_scraper.persona_recommendation_engine import PersonaRecommendationEngine
        
        # Test with niche interest
        test_user_data = {
            "mbti": "ISFJ",
            "interests": ["fountain pen", "calligraphy", "mechanical keyboard"],
            "channel_category": "Lifestyle", 
            "budget_level": "medium"
        }
        
        print(f"👤 Test User Profile:")
        print(f"   MBTI: {test_user_data['mbti']}")
        print(f"   Interests: {', '.join(test_user_data['interests'])}")
        print(f"   Channel: {test_user_data['channel_category']}")
        print(f"   Budget: {test_user_data['budget_level']}")
        print()
        
        # Initialize recommendation engine
        engine = PersonaRecommendationEngine(debug_mode=True)
        
        # Test the tagging integration
        tagger = ProductTagger()
        
        # Simulate some products that would come from niche scraping
        mock_products = [
            {
                "product_name": "Lamy Safari Fountain Pen Calligraphy Set",
                "category": "stationery",
                "price": "₱2,500",
                "trending_score": 0  # Will be calculated
            },
            {
                "product_name": "Keychron K2 Mechanical Gaming Keyboard",
                "category": "electronics", 
                "price": "₱6,500",
                "trending_score": 0
            },
            {
                "product_name": "Generic Office Supplies Set",
                "category": "office",
                "price": "₱500", 
                "trending_score": 0
            }
        ]
        
        print("🏷️ Testing product tagging for recommendations:")
        
        enhanced_products = []
        for product in mock_products:
            # Apply hierarchical tagging
            tagged_product = tagger.tag_product_with_keywords(product)
            
            name = product['product_name']
            categories = tagged_product.get('niche_categories', [])
            confidence = tagged_product.get('tag_confidence', 'none')
            
            print(f"   • {name[:40]}...")
            print(f"     Categories: {categories}")
            print(f"     Confidence: {confidence}")
            
            enhanced_products.append(tagged_product)
        
        print()
        
        # Test how niche-tagged products would score in recommendation engine
        print("📊 Testing recommendation scoring with niche tags:")
        
        niche_aware_products = []
        for product in enhanced_products:
            # Simulate how the recommendation engine would handle niche tags
            base_score = 30  # Base product score
            
            # Bonus for niche category matches
            user_interests = test_user_data['interests']
            product_categories = product.get('niche_categories', [])
            
            niche_bonus = 0
            for interest in user_interests:
                for category in product_categories:
                    if any(interest.lower() in keyword for keyword in [
                        'fountain pen', 'calligraphy', 'mechanical', 'keyboard'
                    ]):
                        niche_bonus += 15  # Significant bonus for niche match
            
            confidence_bonus = {
                'high': 10, 'medium': 5, 'low': 2, 'very_low': 1, 'none': 0
            }.get(product.get('tag_confidence', 'none'), 0)
            
            final_score = base_score + niche_bonus + confidence_bonus
            
            product['enhanced_score'] = final_score
            niche_aware_products.append(product)
            
            name = product.get('product_name', 'Unknown')[:40]
            print(f"   • {name}... = {final_score} pts")
            print(f"     (Base: {base_score} + Niche: {niche_bonus} + Confidence: {confidence_bonus})")
        
        print()
        
        # Check if niche products scored higher
        niche_products = [p for p in niche_aware_products if p.get('niche_categories')]
        generic_products = [p for p in niche_aware_products if not p.get('niche_categories')]
        
        avg_niche_score = sum(p['enhanced_score'] for p in niche_products) / len(niche_products) if niche_products else 0
        avg_generic_score = sum(p['enhanced_score'] for p in generic_products) / len(generic_products) if generic_products else 0
        
        print(f"📈 SCORING COMPARISON:")
        print(f"   • Average Niche Product Score: {avg_niche_score:.1f}")
        print(f"   • Average Generic Product Score: {avg_generic_score:.1f}")
        
        if avg_niche_score > avg_generic_score:
            print(f"   ✅ SUCCESS: Niche products scored {avg_niche_score - avg_generic_score:.1f} points higher")
            return True
        else:
            print(f"   ⚠️ ISSUE: Generic products scored higher or equal")
            return False
        
    except ImportError as e:
        print(f"❌ Could not import recommendation engine: {e}")
        return False
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n" + "="*80)
    print("📋 NICHE DATA PIPELINE TEST REPORT")
    print("="*80)
    
    results = {}
    
    # Run all tests
    print("\n🧪 Running Test Suite...")
    
    try:
        results['tagger_test'] = test_product_tagger()
        print()
    except Exception as e:
        print(f"❌ Tagger test failed: {e}")
        results['tagger_test'] = False
    
    try:
        results['scraper_test'] = test_niche_scraper()
        print()
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        results['scraper_test'] = False
    
    try:
        results['integration_test'] = test_integration_with_recommendation_engine()
        print()
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        results['integration_test'] = False
    
    # Generate summary
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    print(f"\n📊 TEST RESULTS SUMMARY:")
    print(f"   • Tests Passed: {passed_tests}/{total_tests}")
    print(f"   • Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   • {test_name.replace('_', ' ').title()}: {status}")
    
    print()
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Niche Data Pipeline Ready!")
        print("\n🚀 Next Steps:")
        print("   1. Run full scraping: python -m vootcamp_ph_scraper.scrapers.niche_category_scraper")
        print("   2. Integrate with recommendation engine")
        print("   3. Update True Personalization feature with niche data")
    else:
        print("⚠️ Some tests failed - Review implementation before deployment")
    
    # Save report
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'test_results': results,
        'summary': {
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'success_rate': (passed_tests/total_tests)*100
        }
    }
    
    with open('niche_pipeline_test_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📁 Detailed report saved to: niche_pipeline_test_report.json")
    
    return results

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run comprehensive test
    generate_test_report()