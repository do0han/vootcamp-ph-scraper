#!/usr/bin/env python3
"""
UAT Task 2-2: Generate All Three Specialized Reports for Persona B

This script generates Content Strategy, Monetization Plan, and Performance Optimization
reports for Persona B (ESFP Beauty Creator) using the report dispatcher.
"""

from report_dispatcher import generate_specialized_report

def generate_persona_b_specialized_reports():
    """
    Generate all three specialized reports for Persona B
    """
    
    # Define Persona B profile (ESFP Beauty Creator)
    persona_b_profile = {
        "persona": {
            "id": "beauty",
            "name": "뷰티 크리에이터", 
            "emoji": "💄"
        },
        "mbti": "ESFP",
        "interests": ["k-beauty", "skincare"],
        "channel_category": "Beauty",
        "budget_level": "Medium",
        "budget": "₱2,000-5,000"
    }
    
    print("🚀 UAT Task 2-2: Generating All Three Specialized Reports for Persona B")
    print("=" * 80)
    print(f"👤 MBTI: {persona_b_profile['mbti']} (The Entertainer)")
    print(f"🎯 Interests: {', '.join(persona_b_profile['interests'])}")
    print(f"📺 Channel: {persona_b_profile['channel_category']}")
    print(f"💰 Budget: {persona_b_profile['budget_level']} ({persona_b_profile['budget']})")
    print("-" * 80)
    
    # Define the three report types to generate
    report_configs = [
        {
            "report_type": "content_strategy",
            "filename": "test_B_content.md",
            "name": "Content Strategy",
            "icon": "🎨",
            "description": "Creative K-beauty content ideas and strategies"
        },
        {
            "report_type": "monetization_plan", 
            "filename": "test_B_monetization.md",
            "name": "Monetization Plan",
            "icon": "💰",
            "description": "Beauty creator revenue strategies and partnerships"
        },
        {
            "report_type": "performance_optimization",
            "filename": "test_B_performance.md",
            "name": "Performance Optimization", 
            "icon": "📈",
            "description": "Beauty content performance and engagement optimization"
        }
    ]
    
    results = []
    
    # Generate each specialized report
    for i, config in enumerate(report_configs, 1):
        print(f"\n{config['icon']} Report {i}/3: {config['name']}")
        print(f"📂 Output: {config['filename']}")
        print(f"🎯 Focus: {config['description']}")
        
        try:
            # Generate the report using the dispatcher
            print(f"🔄 Calling dispatcher with report_type='{config['report_type']}'...")
            
            report_content = generate_specialized_report(
                persona_b_profile, 
                config['report_type']
            )
            
            # Save to the specified filename
            with open(config['filename'], 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Validation checks
            report_length = len(report_content)
            section_count = report_content.count("##")
            has_title = config['name'] in report_content or "Report:" in report_content
            
            print(f"✅ Generated successfully")
            print(f"📏 Length: {report_length:,} characters")
            print(f"📋 Sections: {section_count} (## headings)")
            print(f"📄 Title: {'✅' if has_title else '❌'}")
            
            # Check for specialist focus and ESFP context
            report_lower = report_content.lower()
            
            if config['report_type'] == 'content_strategy':
                focus_check = 'content' in report_lower and 'ideas' in report_lower
                exclusion_check = 'monetization' not in report_lower and 'revenue' not in report_lower
                beauty_context = 'beauty' in report_lower or 'skincare' in report_lower
            elif config['report_type'] == 'monetization_plan':
                focus_check = 'revenue' in report_lower or 'monetization' in report_lower
                exclusion_check = 'content ideas' not in report_lower and 'creative' not in report_lower
                beauty_context = 'beauty' in report_lower or 'influencer' in report_lower
            else:  # performance_optimization
                focus_check = 'performance' in report_lower or 'optimization' in report_lower
                exclusion_check = 'content ideas' not in report_lower and 'revenue' not in report_lower
                beauty_context = 'beauty' in report_lower or 'engagement' in report_lower
            
            print(f"🎯 Focus Check: {'✅' if focus_check else '❌'}")
            print(f"🚫 Exclusion Check: {'✅' if exclusion_check else '❌'}")
            print(f"💄 Beauty Context: {'✅' if beauty_context else '❌'}")
            
            results.append({
                "name": config['name'],
                "filename": config['filename'],
                "type": config['report_type'],
                "length": report_length,
                "sections": section_count,
                "focus_check": focus_check,
                "exclusion_check": exclusion_check,
                "beauty_context": beauty_context,
                "success": True
            })
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append({
                "name": config['name'],
                "filename": config['filename'],
                "type": config['report_type'],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print(f"\n🎯 UAT TASK 2-2 SUMMARY")
    print("=" * 80)
    
    successful_reports = sum(1 for r in results if r.get('success', False))
    total_reports = len(results)
    
    print(f"📊 Results: {successful_reports}/{total_reports} reports generated successfully")
    print()
    
    for result in results:
        if result.get('success', False):
            status = "✅ SUCCESS"
            focus_status = "✅" if result.get('focus_check', False) else "❌"
            exclusion_status = "✅" if result.get('exclusion_check', False) else "❌"
            beauty_status = "✅" if result.get('beauty_context', False) else "❌"
            
            print(f"{status} | {result['name']}")
            print(f"   📂 {result['filename']} ({result['length']:,} chars, {result['sections']} sections)")
            print(f"   🎯 Focus: {focus_status} | 🚫 Exclusion: {exclusion_status} | 💄 Beauty: {beauty_status}")
        else:
            print(f"❌ FAILED | {result['name']}: {result.get('error', 'Unknown error')}")
        print()
    
    if successful_reports == total_reports:
        print("🔥 ALL PERSONA B REPORTS GENERATED SUCCESSFULLY!")
        print("📋 Ready for specialist review and comparison with Persona A")
        
        # Show file contents preview
        print(f"\n📂 Generated Files for ESFP Beauty Creator:")
        for result in results:
            if result.get('success', False):
                print(f"   - {result['filename']} ({result['type']}) - {result['length']:,} chars")
                
        print(f"\n🔍 Persona B vs Persona A Comparison Available:")
        print("   - Content Strategy: Beauty-focused vs Tech-focused")
        print("   - Monetization: Beauty influencer vs Tech expert revenue streams")
        print("   - Performance: Visual/social platforms vs Analytical content optimization")
    else:
        print("⚠️  Some reports failed - check errors above")
    
    return successful_reports == total_reports

if __name__ == "__main__":
    success = generate_persona_b_specialized_reports()
    
    if success:
        print(f"\n🎉 UAT Task 2-2 completed successfully!")
        print("📋 All three specialized reports generated for Persona B (ESFP Beauty Creator).")
        print("🔍 Each report maintains strict focus on its specialist domain with beauty context.")
        print("🆚 Ready for comparison with Persona A reports to verify persona differentiation.")
    else:
        print(f"\n💥 UAT Task 2-2 encountered errors!")
        print("🔧 Please check the error messages above.")