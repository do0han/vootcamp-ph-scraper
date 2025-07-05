#!/usr/bin/env python3
"""
Standalone test for the Content Strategy report function
"""

from report_dispatcher import generate_content_strategy_report

def test_content_strategy():
    """Test the Content Strategy report function directly"""
    
    # Test user profiles
    test_profiles = [
        {
            "persona": {"id": "tech", "name": "테크 크리에이터", "emoji": "💻"},
            "interests": ["mechanical keyboards", "gadgets", "coding"],
            "budget": "₱5,000-15,000"
        },
        {
            "persona": {"id": "lifestyle", "name": "라이프스타일 크리에이터", "emoji": "✨"},
            "interests": ["fashion", "beauty", "home decor"],
            "budget": "₱3,000-10,000"
        },
        {
            "persona": {"id": "food-travel", "name": "푸드/여행 크리에이터", "emoji": "🍜"},
            "interests": ["cooking", "travel", "local food"],
            "budget": "₱2,000-8,000"
        }
    ]
    
    print("🎨 Testing Content Strategy Report Generation")
    print("=" * 60)
    
    for i, profile in enumerate(test_profiles, 1):
        persona_name = profile['persona']['name']
        print(f"\n📊 Test {i}: {persona_name}")
        print("-" * 40)
        
        try:
            report = generate_content_strategy_report(profile)
            
            # Check if report follows the required structure
            required_sections = [
                "# 🎨 Content Strategy Report:",
                "## 📊 Section 1: Current Hot Topics",
                "## 🌺 Section 2: Seasonal Keyword Recommendations", 
                "## 💡 Section 3: Top 5 Concrete Content Ideas"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in report:
                    missing_sections.append(section)
            
            if not missing_sections:
                print("✅ Report structure: COMPLETE")
                print(f"📝 Report length: {len(report)} characters")
                
                # Check for exclusion rule compliance
                excluded_terms = ["monetization", "analytics", "performance optimization", "business strategy"]
                found_excluded = [term for term in excluded_terms if term.lower() in report.lower()]
                
                if not found_excluded:
                    print("✅ Exclusion rule: COMPLIANT (no monetization/performance advice)")
                else:
                    print(f"⚠️  Exclusion rule: Found excluded terms: {found_excluded}")
                
                # Preview first 200 characters
                preview = report[:200].replace('\n', ' ')
                print(f"👀 Preview: {preview}...")
                
            else:
                print("❌ Report structure: INCOMPLETE")
                print(f"Missing sections: {missing_sections}")
                
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    print("\n🎯 Content Strategy Test Summary:")
    print("- Reports should include all 3 required sections")
    print("- No monetization or performance advice should be included")
    print("- Content should be tailored to Filipino audience")
    print("- Each content idea should have all required fields")

if __name__ == "__main__":
    test_content_strategy()