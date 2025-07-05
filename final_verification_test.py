#!/usr/bin/env python3
"""
Final Verification Test: 3-Way Report Generation Test

This script generates all three specialist reports for the same Business Creator persona
and saves them to separate markdown files for comparison and verification.
"""

from report_dispatcher import generate_specialized_report

def run_final_verification_test():
    """
    Run comprehensive test generating all three report types for Business Creator persona
    """
    
    # Define the test persona: Business Creator
    business_creator_persona = {
        "persona": {
            "id": "business", 
            "name": "비즈니스 크리에이터",
            "emoji": "💼"
        },
        "interests": ["entrepreneurship", "business strategy", "productivity", "leadership"],
        "budget": "₱10,000-25,000"
    }
    
    print("🚀 Starting Final Verification Test")
    print("=" * 60)
    print(f"📊 Test Persona: {business_creator_persona['persona']['name']}")
    print(f"🎯 Interests: {', '.join(business_creator_persona['interests'])}")
    print(f"💰 Budget: {business_creator_persona['budget']}")
    print("-" * 60)
    
    # Test configurations
    test_cases = [
        {
            "report_type": "content_strategy",
            "filename": "report_content_strategy.md",
            "name": "Content Strategy",
            "icon": "🎨"
        },
        {
            "report_type": "monetization_plan", 
            "filename": "report_monetization_plan.md",
            "name": "Monetization Plan",
            "icon": "💰"
        },
        {
            "report_type": "performance_optimization",
            "filename": "report_performance_optimization.md", 
            "name": "Performance Optimization",
            "icon": "📈"
        }
    ]
    
    results = []
    
    # Generate each report
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{test_case['icon']} Test {i}/3: Generating {test_case['name']} Report")
        print(f"📂 Output file: {test_case['filename']}")
        
        try:
            # Generate the report using the dispatcher
            report_content = generate_specialized_report(
                business_creator_persona, 
                test_case['report_type']
            )
            
            # Save to markdown file
            with open(test_case['filename'], 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Basic validation
            report_length = len(report_content)
            has_sections = report_content.count("##") >= 3
            
            print(f"✅ Generated successfully")
            print(f"📏 Length: {report_length:,} characters")
            print(f"📋 Sections: {'✅' if has_sections else '❌'} (3+ sections found)")
            
            results.append({
                "name": test_case['name'],
                "filename": test_case['filename'],
                "length": report_length,
                "success": True,
                "has_sections": has_sections
            })
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append({
                "name": test_case['name'],
                "filename": test_case['filename'],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print(f"\n🎯 FINAL VERIFICATION TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(results)
    
    for result in results:
        status = "✅ SUCCESS" if result.get('success', False) else "❌ FAILED"
        if result.get('success', False):
            print(f"{status} | {result['name']}: {result['length']:,} chars | {result['filename']}")
        else:
            print(f"{status} | {result['name']}: {result.get('error', 'Unknown error')}")
    
    print(f"\n📊 Results: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🔥 ALL TESTS PASSED - Ready for review!")
        print("\n📂 Generated files:")
        for result in results:
            if result.get('success', False):
                print(f"   - {result['filename']}")
    else:
        print("⚠️  Some tests failed - check errors above")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    success = run_final_verification_test()
    
    if success:
        print(f"\n🎉 Final verification test completed successfully!")
        print("📋 All three specialist reports have been generated and saved.")
        print("🔍 Each report should contain ONLY information relevant to its specialist domain.")
    else:
        print(f"\n💥 Final verification test encountered errors!")
        print("🔧 Please check the error messages above and fix any issues.")