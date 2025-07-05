#!/usr/bin/env python3
"""
Complete test for all three specialist report functions
"""

from report_dispatcher import (
    generate_content_strategy_report,
    generate_monetization_plan_report,
    generate_performance_optimization_report
)

def test_all_specialists():
    """Test all three specialist functions with exclusion rule compliance"""
    
    # Test user profile
    test_profile = {
        "persona": {"id": "tech", "name": "테크 크리에이터", "emoji": "💻"},
        "interests": ["mechanical keyboards", "gadgets", "coding"],
        "budget": "₱5,000-15,000"
    }
    
    # Define the specialists and their exclusion rules
    specialists = [
        {
            "name": "Content Strategy",
            "function": generate_content_strategy_report,
            "icon": "🎨",
            "should_exclude": ["monetization", "performance optimization", "analytics", "business"],
            "should_include": ["content ideas", "creative", "strategy", "topics"]
        },
        {
            "name": "Monetization Plan", 
            "function": generate_monetization_plan_report,
            "icon": "💰",
            "should_exclude": ["content ideas", "performance tips", "creative"],
            "should_include": ["revenue", "monetization", "income", "business"]
        },
        {
            "name": "Performance Optimization",
            "function": generate_performance_optimization_report,
            "icon": "📈",
            "should_exclude": ["content ideas", "monetization", "creative"],
            "should_include": ["performance", "metrics", "optimization", "analytics"]
        }
    ]
    
    print("🚀 Testing All Specialist Report Functions")
    print("=" * 60)
    
    all_passed = True
    
    for specialist in specialists:
        print(f"\n{specialist['icon']} Testing {specialist['name']} Specialist")
        print("-" * 50)
        
        try:
            # Generate the report
            report = specialist['function'](test_profile)
            
            # Basic structure check
            report_lower = report.lower()
            
            # Check exclusion rule compliance
            violations = []
            for excluded_term in specialist['should_exclude']:
                if excluded_term.lower() in report_lower:
                    violations.append(excluded_term)
            
            # Check inclusion compliance (specialist focus)
            includes = []
            for included_term in specialist['should_include']:
                if included_term.lower() in report_lower:
                    includes.append(included_term)
            
            # Report results
            print(f"📝 Report Length: {len(report)} characters")
            
            if violations:
                print(f"❌ EXCLUSION VIOLATIONS: Found {violations}")
                all_passed = False
            else:
                print("✅ Exclusion Rule: COMPLIANT")
            
            if includes:
                print(f"✅ Focus Area: Contains {len(includes)} relevant terms")
            else:
                print("⚠️  Focus Area: May lack specialist focus")
            
            # Check for required sections based on specialist type
            if specialist['name'] == "Content Strategy":
                required = ["Section 1:", "Section 2:", "Section 3:", "Content Ideas"]
            elif specialist['name'] == "Monetization Plan":
                required = ["Section 1:", "Section 2:", "Section 3:", "Revenue"]
            else:  # Performance Optimization
                required = ["Section 1:", "Section 2:", "Section 3:", "Optimization"]
            
            missing_sections = [section for section in required if section not in report]
            
            if missing_sections:
                print(f"❌ Structure: Missing {missing_sections}")
                all_passed = False
            else:
                print("✅ Structure: All required sections present")
            
            # Preview
            preview = report[:150].replace('\n', ' ')
            print(f"👀 Preview: {preview}...")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            all_passed = False
    
    print(f"\n🎯 FINAL TEST RESULT")
    print("=" * 60)
    if all_passed:
        print("✅ ALL SPECIALISTS PASSED")
        print("🔥 Ready for production use!")
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Review exclusion rule compliance and structure")
    
    print(f"\n📋 Summary:")
    print("- Content Strategy: Creative ideas only, no monetization/performance")
    print("- Monetization Plan: Revenue strategies only, no content/performance")  
    print("- Performance Optimization: Metrics only, no content/monetization")

if __name__ == "__main__":
    test_all_specialists()