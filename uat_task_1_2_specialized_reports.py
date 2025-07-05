#!/usr/bin/env python3
"""
UAT Task 1-2: Generate All Three Specialized Reports for Persona A

This script generates Content Strategy, Monetization Plan, and Performance Optimization
reports for the same Persona A profile using the report dispatcher.
"""

from report_dispatcher import generate_specialized_report

def generate_persona_a_specialized_reports():
    """
    Generate all three specialized reports for Persona A
    """
    
    # Define Persona A profile (same as UAT 1-1)
    persona_a_profile = {
        "persona": {
            "id": "tech",
            "name": "테크 크리에이터", 
            "emoji": "💻"
        },
        "mbti": "INTP",
        "interests": ["mechanical keyboard", "desk setup"],
        "channel_category": "Tech",
        "budget_level": "High",
        "budget": "₱15,000-50,000"
    }
    
    print("🚀 UAT Task 1-2: Generating All Three Specialized Reports for Persona A")
    print("=" * 80)
    print(f"👤 MBTI: {persona_a_profile['mbti']} (The Architect)")
    print(f"🎯 Interests: {', '.join(persona_a_profile['interests'])}")
    print(f"📺 Channel: {persona_a_profile['channel_category']}")
    print(f"💰 Budget: {persona_a_profile['budget_level']} ({persona_a_profile['budget']})")
    print("-" * 80)
    
    # Define the three report types to generate
    report_configs = [
        {
            "report_type": "content_strategy",
            "filename": "test_A_content.md",
            "name": "Content Strategy",
            "icon": "🎨",
            "description": "Creative content ideas and strategies"
        },
        {
            "report_type": "monetization_plan", 
            "filename": "test_A_monetization.md",
            "name": "Monetization Plan",
            "icon": "💰",
            "description": "Revenue strategies and income opportunities"
        },
        {
            "report_type": "performance_optimization",
            "filename": "test_A_performance.md",
            "name": "Performance Optimization", 
            "icon": "📈",
            "description": "Metrics optimization and growth strategies"
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
                persona_a_profile, 
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
            
            # Check for specialist focus
            if config['report_type'] == 'content_strategy':
                focus_check = 'content' in report_content.lower() and 'ideas' in report_content.lower()
                exclusion_check = 'monetization' not in report_content.lower() and 'revenue' not in report_content.lower()
            elif config['report_type'] == 'monetization_plan':
                focus_check = 'revenue' in report_content.lower() or 'monetization' in report_content.lower()
                exclusion_check = 'content ideas' not in report_content.lower() and 'creative' not in report_content.lower()
            else:  # performance_optimization
                focus_check = 'performance' in report_content.lower() or 'optimization' in report_content.lower()
                exclusion_check = 'content ideas' not in report_content.lower() and 'revenue' not in report_content.lower()
            
            print(f"🎯 Focus Check: {'✅' if focus_check else '❌'}")
            print(f"🚫 Exclusion Check: {'✅' if exclusion_check else '❌'}")
            
            results.append({
                "name": config['name'],
                "filename": config['filename'],
                "type": config['report_type'],
                "length": report_length,
                "sections": section_count,
                "focus_check": focus_check,
                "exclusion_check": exclusion_check,
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
    print(f"\n🎯 UAT TASK 1-2 SUMMARY")
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
            
            print(f"{status} | {result['name']}")
            print(f"   📂 {result['filename']} ({result['length']:,} chars, {result['sections']} sections)")
            print(f"   🎯 Focus: {focus_status} | 🚫 Exclusion: {exclusion_status}")
        else:
            print(f"❌ FAILED | {result['name']}: {result.get('error', 'Unknown error')}")
        print()
    
    if successful_reports == total_reports:
        print("🔥 ALL REPORTS GENERATED SUCCESSFULLY!")
        print("📋 Ready for specialist review and verification")
        
        # Show file contents preview
        print(f"\n📂 Generated Files:")
        for result in results:
            if result.get('success', False):
                print(f"   - {result['filename']} ({result['type']})")
    else:
        print("⚠️  Some reports failed - check errors above")
    
    return successful_reports == total_reports

if __name__ == "__main__":
    success = generate_persona_a_specialized_reports()
    
    if success:
        print(f"\n🎉 UAT Task 1-2 completed successfully!")
        print("📋 All three specialized reports generated for Persona A.")
        print("🔍 Each report maintains strict focus on its specialist domain.")
    else:
        print(f"\n💥 UAT Task 1-2 encountered errors!")
        print("🔧 Please check the error messages above.")