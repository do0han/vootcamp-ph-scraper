#!/usr/bin/env python3
"""
Test Scenario 2: Data Coverage Gap Analysis
Testing niche but valid interests: fountain pen, calligraphy, stationery
"""

import json
import sys
import os
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.getcwd())

from vootcamp_ph_scraper.persona_recommendation_engine import PersonaRecommendationEngine

def test_niche_valid_interests():
    """Test with niche but valid interests that should have some products"""
    
    print("🧪 Test Scenario 2: Data Coverage Gap Analysis")
    print("=" * 70)
    print()
    
    # Test data with niche but valid interests
    test_data = {
        "mbti": "ISFJ",  # Detail-oriented, appreciates craftsmanship
        "interests": [
            "fountain pen",
            "calligraphy", 
            "stationery"
        ],
        "channel_category": "Lifestyle",
        "budget_level": "medium"
    }
    
    print("📝 Test Profile:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print()
    print("🎯 Profile Analysis:")
    print("   • Target: Calligraphy enthusiast, appreciates fine writing instruments")
    print("   • Expected Products: Fountain pens, ink, special paper, calligraphy supplies")
    print("   • Expected Content: Writing tutorials, pen reviews, calligraphy guides")
    print()
    
    print("🚀 Running recommendation engine...")
    print("-" * 50)
    
    try:
        # Initialize engine with debug mode
        engine = PersonaRecommendationEngine(debug_mode=True)
        
        # Generate custom recommendation
        result = engine.generate_custom_recommendation(test_data)
        
        print("✅ Recommendation generated successfully!")
        print()
        
        # Generate user-facing report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"calligraphy_enthusiast_report_{timestamp}.md"
        
        generate_user_report(result, test_data, report_file)
        
        # Analysis
        analyze_data_coverage(result, test_data)
        
        # Save raw results
        result_file = f'niche_interest_test_result_{timestamp}.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Raw results saved to: {result_file}")
        print(f"📄 User report generated: {report_file}")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

def generate_user_report(result, test_data, filename):
    """Generate a user-facing markdown report"""
    
    stats = result.get('statistics', {})
    products = result.get('product_recommendations', [])
    content_ideas = result.get('content_ideas', [])
    user_profile = result.get('user_profile', {})
    
    report = f"""# 🖋️ Calligraphy Enthusiast - Personal Recommendation Report

## 👤 Your Profile
- **MBTI**: {user_profile.get('mbti', 'N/A')}
- **Interests**: {', '.join(user_profile.get('interests', []))}
- **Channel Category**: {user_profile.get('channel_category', 'N/A')}
- **Budget Level**: {user_profile.get('budget_level', 'N/A')}
- **Generated Persona**: {user_profile.get('persona_name', 'N/A')}

## 📊 Recommendation Summary
- **Total Products Found**: {stats.get('total_products', 0)}
- **Average Match Score**: {stats.get('average_score', 0)}/100
- **High-Quality Matches (80+)**: {stats.get('high_score_products', 0)}
- **Content Ideas Generated**: {stats.get('content_ideas_count', 0)}

## 🛍️ Product Recommendations

"""
    
    if products:
        for i, product in enumerate(products, 1):
            score = product.get('trending_score', 0)
            score_emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            
            report += f"""### {i}. {product.get('product', 'Unknown Product')} {score_emoji}
- **Score**: {score}/100
- **Category**: {product.get('category', 'N/A')}
- **Price Range**: {product.get('price', 'N/A')}
- **Why This Product**: {product.get('reason', 'N/A')}
- **Where to Buy**: {', '.join(product.get('where_to_buy', []))}
- **Content Angle**: {product.get('content_angle', 'N/A')}

"""
    else:
        report += "❌ No products found matching your interests.\n\n"
    
    report += "## 💡 Content Ideas for Your Channel\n\n"
    
    if content_ideas:
        for i, idea in enumerate(content_ideas, 1):
            report += f"""### {i}. {idea.get('title', 'Untitled')}
- **Type**: {idea.get('type', 'N/A')}
- **Platform**: {idea.get('platform', 'N/A')}
- **Hook**: "{idea.get('hook', 'N/A')}"
- **Key Points**:
"""
            for point in idea.get('key_points', []):
                report += f"  - {point}\n"
            report += f"- **Call to Action**: {idea.get('call_to_action', 'N/A')}\n\n"
    else:
        report += "❌ No content ideas generated.\n\n"
    
    report += f"""## 🎯 Personalization Quality Assessment

This report was generated using AI analysis of your interests in **fountain pens**, **calligraphy**, and **stationery**. 

### Relevance Check:
- Are the recommended products actually related to your interests?
- Do the content ideas make sense for a calligraphy enthusiast?
- Are the price ranges appropriate for quality writing instruments?

### Coverage Analysis:
- Did we find specialized calligraphy supplies or just generic items?
- Are there specific fountain pen brands or just general writing tools?
- Do the content ideas show understanding of the calligraphy community?

---
*Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | AI Recommendation Engine*
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 User-facing report generated: {filename}")

def analyze_data_coverage(result, test_data):
    """Analyze the quality and relevance of recommendations"""
    
    print("🔍 DATA COVERAGE ANALYSIS")
    print("=" * 50)
    
    products = result.get('product_recommendations', [])
    content_ideas = result.get('content_ideas', [])
    stats = result.get('statistics', {})
    
    # Relevance keywords for calligraphy/fountain pen interests
    relevant_keywords = [
        'fountain pen', 'pen', 'ink', 'calligraphy', 'writing', 'paper', 
        'stationery', 'notebook', 'journal', 'brush', 'lettering', 'script'
    ]
    
    print(f"📊 Product Relevance Analysis:")
    print(f"   Total Products: {len(products)}")
    
    if products:
        relevant_count = 0
        for i, product in enumerate(products, 1):
            product_name = product.get('product', '').lower()
            category = product.get('category', '').lower()
            score = product.get('trending_score', 0)
            
            # Check relevance
            is_relevant = any(keyword in product_name or keyword in category for keyword in relevant_keywords)
            
            if is_relevant:
                relevant_count += 1
                relevance_status = "✅ RELEVANT"
            else:
                relevance_status = "❌ IRRELEVANT"
            
            print(f"   {i}. {product.get('product', 'N/A')} ({score}pts) - {relevance_status}")
            print(f"      Category: {product.get('category', 'N/A')}")
        
        relevance_ratio = relevant_count / len(products) * 100
        print(f"\n📈 Relevance Summary:")
        print(f"   • Relevant Products: {relevant_count}/{len(products)} ({relevance_ratio:.1f}%)")
        
        if relevance_ratio >= 80:
            print("   ✅ EXCELLENT: High relevance to calligraphy interests")
        elif relevance_ratio >= 50:
            print("   🟡 MODERATE: Some relevant products found")
        else:
            print("   ❌ POOR: Mostly irrelevant recommendations")
        
        # Score analysis
        avg_score = stats.get('average_score', 0)
        high_score_products = stats.get('high_score_products', 0)
        
        print(f"\n🎯 Score Quality:")
        print(f"   • Average Score: {avg_score}/100")
        print(f"   • High-Quality Products (80+): {high_score_products}")
        
        if avg_score >= 70:
            print("   ✅ HIGH: Strong match with user interests")
        elif avg_score >= 50:
            print("   🟡 MEDIUM: Moderate match quality")
        else:
            print("   ❌ LOW: Weak match with user interests")
    
    else:
        print("   ❌ No products recommended")
    
    print(f"\n💡 Content Ideas Analysis:")
    print(f"   Total Ideas: {len(content_ideas)}")
    
    if content_ideas:
        for i, idea in enumerate(content_ideas, 1):
            title = idea.get('title', '').lower()
            idea_type = idea.get('type', '')
            
            # Check if content ideas are relevant to calligraphy
            is_relevant = any(keyword in title for keyword in relevant_keywords)
            
            relevance_status = "✅ RELEVANT" if is_relevant else "❌ GENERIC"
            print(f"   {i}. {idea.get('title', 'N/A')} ({idea_type}) - {relevance_status}")
    
    print(f"\n📋 Coverage Gap Assessment:")
    
    # Check for specific calligraphy-related gaps
    expected_products = [
        "fountain pen", "ink bottle", "calligraphy paper", "practice pad", 
        "nib", "converter", "pen case", "washi tape", "ruler", "guide sheets"
    ]
    
    found_products = [p.get('product', '').lower() for p in products]
    
    gaps = []
    for expected in expected_products:
        if not any(expected in found for found in found_products):
            gaps.append(expected)
    
    if gaps:
        print(f"   🔴 Missing Expected Items: {', '.join(gaps[:5])}")
        print(f"   💡 Suggestion: Expand product database for calligraphy niche")
    else:
        print(f"   ✅ Good coverage of expected calligraphy products")

if __name__ == "__main__":
    test_niche_valid_interests()