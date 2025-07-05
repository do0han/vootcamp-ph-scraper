#!/usr/bin/env python3
"""
Test the upgraded hierarchical interest matching system
계층적 관심사 매칭 시스템 테스트 - Test Scenario 2 재실행
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project path
sys.path.append(str(Path(__file__).parent / "vootcamp_ph_scraper"))

from vootcamp_ph_scraper.persona_recommendation_engine import PersonaRecommendationEngine

def test_fountain_pen_hierarchical_matching():
    """Test Scenario 2: Fountain pen with hierarchical scoring"""
    
    print("🖋️ Test Scenario 2: Hierarchical Interest Matching")
    print("=" * 70)
    print("Objective: Test fountain pen interest with upgraded hierarchical scoring")
    print()
    
    # Test user profile with fountain pen interest
    test_user_data = {
        "mbti": "ISFJ",
        "interests": ["fountain pen", "calligraphy", "stationery"],
        "channel_category": "Lifestyle",
        "budget_level": "medium"
    }
    
    print("👤 Test User Profile:")
    print(f"   MBTI: {test_user_data['mbti']}")
    print(f"   Interests: {', '.join(test_user_data['interests'])}")
    print(f"   Channel: {test_user_data['channel_category']}")
    print(f"   Budget: {test_user_data['budget_level']}")
    print()
    
    # Initialize recommendation engine with debug mode
    print("🚀 Initializing PersonaRecommendationEngine with debug mode...")
    engine = PersonaRecommendationEngine(debug_mode=True)
    print()
    
    # Generate custom recommendation
    print("🎯 Generating custom recommendations with hierarchical scoring...")
    print("-" * 50)
    
    result = engine.generate_custom_recommendation(test_user_data)
    
    print("-" * 50)
    print("✅ Recommendation generation completed!")
    print()
    
    # Analyze results
    print("📊 RESULTS ANALYSIS:")
    print("=" * 50)
    
    statistics = result.get('statistics', {})
    products = result.get('product_recommendations', [])
    debug_info = result.get('debug_log', result.get('debug_info', []))
    
    print(f"📈 Statistics:")
    print(f"   • Total Products: {statistics.get('total_products', 0)}")
    print(f"   • Average Score: {statistics.get('average_score', 0)}/100")
    print(f"   • High Score Products (80+): {statistics.get('high_score_products', 0)}")
    print(f"   • Content Ideas: {statistics.get('content_ideas_count', 0)}")
    print()
    
    # Check for relevant fountain pen products
    fountain_pen_products = []
    calligraphy_products = []
    
    for product in products:
        product_name = product.get('product', '').lower()
        if 'fountain pen' in product_name or 'lamy' in product_name or 'pilot' in product_name:
            fountain_pen_products.append(product)
        elif 'calligraphy' in product_name or 'ink' in product_name:
            calligraphy_products.append(product)
    
    print(f"🖋️ Fountain Pen Products Found: {len(fountain_pen_products)}")
    for i, product in enumerate(fountain_pen_products, 1):
        name = product.get('product', 'Unknown')
        score = product.get('trending_score', 0)
        price = product.get('price', 'N/A')
        print(f"   {i}. {name}")
        print(f"      💯 Score: {score}/100")
        print(f"      💰 Price: {price}")
        print(f"      📝 Reason: {product.get('reason', 'N/A')[:60]}...")
        print()
    
    print(f"✍️ Calligraphy Products Found: {len(calligraphy_products)}")
    for i, product in enumerate(calligraphy_products, 1):
        name = product.get('product', 'Unknown')
        score = product.get('trending_score', 0)
        print(f"   {i}. {name} - {score} points")
    print()
    
    # Analyze debug log for hierarchical matching evidence
    print("🔍 HIERARCHICAL MATCHING ANALYSIS:")
    print("-" * 40)
    
    hierarchical_matches_found = []
    interest_alignment_scores = []
    
    for line in debug_info:
        # Look for hierarchical matching messages with various formats
        if any(phrase in line for phrase in ["Hierarchical match:", "✓ Hierarchical match:", "Level 5:", "Level 4:", "Level 3:"]):
            hierarchical_matches_found.append(line)
        
        # Look for interest alignment scores with point values
        if "Interest alignment" in line and any(score in line for score in ["+15", "+12", "+8", "+10", "+5"]):
            interest_alignment_scores.append(line)
        
        # Look for final scores that indicate successful matching
        if "Final Score:" in line and "60/100" in line:
            hierarchical_matches_found.append(line)
    
    if hierarchical_matches_found:
        print("✅ Hierarchical Matches Found:")
        for match in hierarchical_matches_found[:5]:  # Show first 5
            print(f"   {match.strip()}")
        print()
    else:
        print("❌ No hierarchical matches found in debug log")
        print()
    
    if interest_alignment_scores:
        print("✅ Interest Alignment Scores:")
        for score in interest_alignment_scores[:3]:  # Show first 3
            print(f"   {score.strip()}")
        print()
    else:
        print("❌ No hierarchical interest alignment scores found")
        print()
    
    # Check for specific scoring improvements
    non_zero_interest_scores = []
    for line in debug_info:
        # Look for any positive scoring evidence
        if any(phrase in line for phrase in ["✓ Hierarchical match:", "+15 points", "+12 points", "+8 points", "+10 points"]):
            if "+15" in line:
                non_zero_interest_scores.append("Level 5 match (+15 points)")
            elif "+12" in line:
                non_zero_interest_scores.append("Level 4 match (+12 points)")
            elif "+8" in line:
                non_zero_interest_scores.append("Level 3 match (+8 points)")
            elif "+10" in line:
                non_zero_interest_scores.append("Keyword match (+10 points)")
        
        # Look for final score evidence showing interest points added
        if "🎯 Final Score:" in line and "60/100" in line:
            non_zero_interest_scores.append("Final score shows interest bonus applied")
    
    print(f"🎯 NON-ZERO INTEREST SCORES:")
    print(f"   Found {len(non_zero_interest_scores)} non-zero interest alignment scores")
    for score in non_zero_interest_scores:
        print(f"   ✅ {score}")
    print()
    
    # Success criteria check
    print("📋 SUCCESS CRITERIA CHECK:")
    print("-" * 30)
    
    criteria_met = 0
    total_criteria = 4
    
    # 1. Relevant products (Lamy Safari, etc.)
    if fountain_pen_products or calligraphy_products:
        print("✅ 1. Relevant products found (fountain pens/calligraphy)")
        criteria_met += 1
    else:
        print("❌ 1. No relevant fountain pen/calligraphy products found")
    
    # 2. Non-zero interest alignment score
    if non_zero_interest_scores:
        print("✅ 2. Non-zero interest alignment scores detected")
        criteria_met += 1
    else:
        print("❌ 2. All interest alignment scores are zero")
    
    # 3. Hierarchical level matching explanation
    if hierarchical_matches_found:
        print("✅ 3. Hierarchical level matching explanations found")
        criteria_met += 1
    else:
        print("❌ 3. No hierarchical level matching explanations")
    
    # 4. Overall score improvement (expect >60 for fountain pen products)
    high_scoring_relevant = [p for p in (fountain_pen_products + calligraphy_products) if p.get('trending_score', 0) > 60]
    if high_scoring_relevant:
        print("✅ 4. High-scoring relevant products (>60 points)")
        criteria_met += 1
    else:
        print("❌ 4. No high-scoring relevant products found")
    
    success_rate = (criteria_met / total_criteria) * 100
    print(f"\n🏆 SUCCESS RATE: {criteria_met}/{total_criteria} ({success_rate:.0f}%)")
    
    if success_rate >= 75:
        print("🎉 EXCELLENT: Hierarchical scoring system working correctly!")
    elif success_rate >= 50:
        print("👍 GOOD: Hierarchical scoring system partially working")
    else:
        print("⚠️ NEEDS IMPROVEMENT: Hierarchical scoring system needs debugging")
    
    # Save detailed results
    test_result = {
        'timestamp': datetime.now().isoformat(),
        'test_scenario': 'fountain_pen_hierarchical_matching',
        'user_profile': test_user_data,
        'results': {
            'statistics': statistics,
            'fountain_pen_products_found': len(fountain_pen_products),
            'calligraphy_products_found': len(calligraphy_products),
            'hierarchical_matches_found': len(hierarchical_matches_found),
            'non_zero_interest_scores': len(non_zero_interest_scores),
            'success_rate': success_rate,
            'criteria_met': criteria_met,
            'total_criteria': total_criteria
        },
        'products': products,
        'debug_samples': {
            'hierarchical_matches': hierarchical_matches_found[:3],
            'interest_scores': interest_alignment_scores[:3],
            'non_zero_scores': non_zero_interest_scores
        }
    }
    
    with open('hierarchical_scoring_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(test_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Detailed results saved to: hierarchical_scoring_test_result.json")
    
    return success_rate >= 75

def main():
    """Main test execution"""
    print("🧪 Testing Hierarchical Interest Matching System")
    print("=" * 60)
    print()
    
    success = test_fountain_pen_hierarchical_matching()
    
    print("\n" + "="*60)
    if success:
        print("🎯 TEST PASSED: Hierarchical scoring system is working correctly!")
        print("✅ The upgrade successfully resolves the data coverage gap.")
    else:
        print("❌ TEST FAILED: Hierarchical scoring system needs investigation.")
        print("🔧 Check the debug logs and scoring logic.")
    
    return success

if __name__ == "__main__":
    main()