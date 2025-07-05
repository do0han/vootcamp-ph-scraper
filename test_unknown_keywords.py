#!/usr/bin/env python3
"""
Test Scenario 1: Unknown Interest Keyword Test
Testing niche keywords that are unlikely to be in our database
"""

import json
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.getcwd())

from vootcamp_ph_scraper.persona_recommendation_engine import PersonaRecommendationEngine

def test_unknown_keywords():
    """Test with unknown/niche keywords"""
    
    print("🧪 Test Scenario 1: Unknown Interest Keyword Test")
    print("=" * 70)
    print()
    
    # Test data with niche/unknown keywords
    test_data = {
        "mbti": "INFP",
        "interests": [
            "dark academia core",
            "plushie collecting", 
            "asmr mukbang"
        ],
        "channel_category": "Lifestyle",
        "budget_level": "medium"
    }
    
    print("📝 Test Data:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print()
    
    print("🚀 Running recommendation engine in debug mode...")
    print("-" * 50)
    
    try:
        # Initialize engine with debug mode
        engine = PersonaRecommendationEngine(debug_mode=True)
        
        # Generate custom recommendation
        result = engine.generate_custom_recommendation(test_data)
        
        print("✅ Engine executed successfully - no crashes!")
        print()
        
        # Analyze results
        print("📊 ANALYSIS RESULTS:")
        print("=" * 50)
        
        stats = result.get('statistics', {})
        products = result.get('product_recommendations', [])
        
        print(f"📈 Final Statistics:")
        print(f"   • Total Products: {stats.get('total_products', 0)}")
        print(f"   • Average Score: {stats.get('average_score', 0)}/100")
        print(f"   • High Score Products (80+): {stats.get('high_score_products', 0)}")
        print(f"   • Content Ideas: {stats.get('content_ideas_count', 0)}")
        print()
        
        print("🛍️ Product Recommendations Analysis:")
        if products:
            for i, product in enumerate(products, 1):
                score = product.get('trending_score', 0)
                print(f"   {i}. {product.get('product', 'N/A')}")
                print(f"      💯 Score: {score}/100")
                print(f"      📂 Category: {product.get('category', 'N/A')}")
                print(f"      💰 Price: {product.get('price', 'N/A')}")
                print(f"      📝 Reason: {product.get('reason', 'N/A')}")
                print()
        else:
            print("   ❌ No products recommended")
            print()
        
        # Interest alignment analysis
        print("🎯 INTEREST ALIGNMENT ANALYSIS:")
        print("-" * 40)
        
        debug_info = result.get('debug_info', [])
        interest_scores = []
        
        for line in debug_info:
            if "Interest alignment" in line:
                # Extract interest score from debug line
                if "no matches" in line.lower():
                    interest_scores.append(0)
                elif "+0" in line:
                    interest_scores.append(0)
                else:
                    # Try to extract score if any
                    import re
                    match = re.search(r'\+(\d+)', line)
                    if match:
                        interest_scores.append(int(match.group(1)))
        
        if interest_scores:
            avg_interest_score = sum(interest_scores) / len(interest_scores)
            print(f"📊 Interest Alignment Scores: {interest_scores}")
            print(f"📊 Average Interest Score: {avg_interest_score}/20")
            
            if avg_interest_score == 0:
                print("✅ EXPECTED: Zero interest alignment for unknown keywords")
            else:
                print(f"⚠️  UNEXPECTED: Got {avg_interest_score} points for unknown keywords")
        else:
            print("📊 No explicit interest scores found in debug")
        
        print()
        
        # Fallback behavior analysis
        print("🔄 FALLBACK BEHAVIOR ANALYSIS:")
        print("-" * 40)
        
        if products:
            # Check if products match channel category
            channel_cat = test_data['channel_category']
            print(f"🎯 Target Channel: {channel_cat}")
            
            channel_matches = 0
            for product in products:
                reason = product.get('reason', '').lower()
                if channel_cat.lower() in reason:
                    channel_matches += 1
            
            print(f"📊 Products matching channel category: {channel_matches}/{len(products)}")
            
            if channel_matches > 0:
                print("✅ System correctly fell back to channel category matching")
            else:
                print("⚠️  System did not explicitly mention channel category fallback")
        
        print()
        
        # Save detailed results
        result_file = 'unknown_keywords_test_result.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Full debug results saved to: {result_file}")
        print()
        
        # Summary
        print("🎯 TEST SUMMARY:")
        print("=" * 30)
        print("✅ System did not crash")
        print(f"✅ Generated {len(products)} product(s)")
        if interest_scores and all(score == 0 for score in interest_scores):
            print("✅ Interest alignment correctly scored as 0 for unknown keywords")
        print("✅ System gracefully handled unknown keywords")
        
        if products:
            avg_score = stats.get('average_score', 0)
            if avg_score < 50:
                print(f"✅ Low average score ({avg_score}) indicates poor match as expected")
            else:
                print(f"⚠️  Unexpectedly high average score ({avg_score}) for unknown keywords")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        print("❌ System crashed when handling unknown keywords")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unknown_keywords()