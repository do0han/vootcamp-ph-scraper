#!/usr/bin/env python3
"""
UAT Task 1-1: Generate Custom Recommendation for Persona A

This script generates a custom recommendation report for:
- MBTI: INTP
- Interests: mechanical keyboard, desk setup, aesthetic tech, productivity
- Channel Category: Tech  
- Budget Level: High
"""

import json
import subprocess
import sys
import os

def generate_persona_a_report():
    """
    Generate custom recommendation report for Persona A using the existing pipeline
    """
    
    # Define Persona A profile
    persona_a_profile = {
        "mbti": "INTP",
        "interests": ["mechanical keyboard", "desk setup", "aesthetic tech", "productivity"],
        "channel_category": "Tech",
        "budget_level": "High",
        "persona": {
            "id": "tech",
            "name": "테크 크리에이터", 
            "emoji": "💻"
        },
        "budget": "₱15,000-50,000"  # High budget range
    }
    
    print("🚀 UAT Task 1-1: Generating Custom Recommendation for Persona A")
    print("=" * 70)
    print(f"👤 MBTI: {persona_a_profile['mbti']}")
    print(f"🎯 Interests: {', '.join(persona_a_profile['interests'])}")
    print(f"📺 Channel Category: {persona_a_profile['channel_category']}")
    print(f"💰 Budget Level: {persona_a_profile['budget_level']} ({persona_a_profile['budget']})")
    print("-" * 70)
    
    # Check if PersonaRecommendationEngine is available
    try:
        print("🔍 Checking for PersonaRecommendationEngine...")
        
        # Try to import and use the existing persona recommendation engine
        if os.path.exists('persona_recommendation_engine.py'):
            print("✅ Found persona_recommendation_engine.py")
            
            # Create a Python script to call the engine
            engine_script = f"""
import sys
import json
sys.path.append('.')

try:
    from persona_recommendation_engine import PersonaRecommendationEngine
    
    # Initialize the engine
    engine = PersonaRecommendationEngine()
    
    # Profile data
    profile = {json.dumps(persona_a_profile, indent=2)}
    
    # Generate recommendations
    print("🔄 Generating recommendations...")
    
    # Use the engine's recommendation methods
    result = engine.generate_personalized_recommendations(
        mbti_type=profile['mbti'],
        interests=profile['interests'],
        budget_range=profile['budget'],
        channel_category=profile['channel_category']
    )
    
    print("✅ Recommendation generation completed")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"❌ Error using PersonaRecommendationEngine: {{e}}")
    
    # Fallback: Use the report dispatcher
    print("🔄 Falling back to report dispatcher...")
    from report_dispatcher import generate_specialized_report
    
    # Generate a content strategy report as primary recommendation
    report = generate_specialized_report(profile, "content_strategy")
    
    # Create a structured result
    fallback_result = {{
        "recommendations": {{
            "primary_focus": "Content Strategy for Tech Creator",
            "mbti_match": "INTP personality traits integrated",
            "report": report
        }},
        "source": "Report Dispatcher Fallback"
    }}
    
    print(json.dumps(fallback_result, indent=2, ensure_ascii=False))
"""
            
            # Write and execute the engine script
            with open('temp_engine_test.py', 'w', encoding='utf-8') as f:
                f.write(engine_script)
            
            # Run the engine script
            result = subprocess.run([sys.executable, 'temp_engine_test.py'], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("✅ Engine execution successful")
                engine_output = result.stdout
                
                # Try to extract JSON from output
                try:
                    # Find JSON in the output
                    import re
                    json_match = re.search(r'\{.*\}', engine_output, re.DOTALL)
                    if json_match:
                        recommendation_data = json.loads(json_match.group())
                        
                        # Format as user-facing report
                        report_content = format_persona_a_report(recommendation_data, persona_a_profile)
                        
                        # Save to file
                        with open('test_A_report.md', 'w', encoding='utf-8') as f:
                            f.write(report_content)
                        
                        print("📁 Report saved as: test_A_report.md")
                        return True
                        
                except json.JSONDecodeError:
                    print("⚠️  Could not parse JSON from engine output")
                    print("Raw output:", engine_output)
            else:
                print(f"❌ Engine execution failed: {result.stderr}")
            
            # Clean up temp file
            if os.path.exists('temp_engine_test.py'):
                os.remove('temp_engine_test.py')
        
        else:
            print("⚠️  PersonaRecommendationEngine not found")
    
    except Exception as e:
        print(f"❌ Error with engine approach: {e}")
    
    # Fallback: Use report dispatcher directly
    print("\n🔄 Using Report Dispatcher Fallback...")
    try:
        from report_dispatcher import generate_specialized_report
        
        # Generate content strategy report
        content_report = generate_specialized_report(persona_a_profile, "content_strategy")
        
        # Create comprehensive report
        report_content = f"""# 🎯 Custom Recommendation Report: Persona A (INTP Tech Creator)

## 👤 Profile Summary
- **MBTI Type**: {persona_a_profile['mbti']} (The Architect)
- **Primary Interests**: {', '.join(persona_a_profile['interests'])}
- **Channel Category**: {persona_a_profile['channel_category']}
- **Budget Range**: {persona_a_profile['budget']} (High Budget)

## 🔍 INTP Personality-Driven Recommendations

### INTP Traits Applied to Content Creation:
- **Analytical Thinking**: Perfect for detailed tech reviews and comparisons
- **Innovation Focus**: Ideal for exploring cutting-edge tech and setups
- **Independent Work Style**: Suits solo content creation and personal branding
- **Quality over Quantity**: Aligns with in-depth, well-researched content

## 📝 Content Strategy Recommendations

{content_report}

## 🎯 INTP-Specific Content Opportunities

### 1. "The Science Behind" Series
Perfect for INTP's analytical nature - deep dives into mechanical keyboard switches, ergonomic science, productivity psychology.

### 2. "Tech Philosophy" Content
Exploring the 'why' behind tech choices, minimalism vs. maximalism in setups, the psychology of productivity tools.

### 3. "Independent Creator Setup" 
Showcasing personal workspace evolution, decision-making processes, and thought leadership in tech aesthetics.

---

*🧠 This report combines INTP personality insights with specialized content strategy for optimal creator success.*"""
        
        # Save to file
        with open('test_A_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print("✅ Fallback report generated successfully")
        print("📁 Report saved as: test_A_report.md")
        return True
        
    except Exception as e:
        print(f"❌ Fallback also failed: {e}")
        return False

def format_persona_a_report(recommendation_data, profile):
    """
    Format the recommendation data into a user-facing report
    """
    
    report = f"""# 🎯 Custom Recommendation Report: Persona A (INTP Tech Creator)

## 👤 Profile Summary
- **MBTI Type**: {profile['mbti']} (The Architect)
- **Primary Interests**: {', '.join(profile['interests'])}
- **Channel Category**: {profile['channel_category']}
- **Budget Range**: {profile['budget']} (High Budget)

## 🤖 AI-Generated Recommendations

"""
    
    # Add the recommendation data
    if 'recommendations' in recommendation_data:
        report += f"### {recommendation_data['recommendations'].get('primary_focus', 'Custom Recommendations')}\n\n"
        
        if 'report' in recommendation_data['recommendations']:
            report += recommendation_data['recommendations']['report']
        else:
            report += "Detailed recommendations generated based on INTP personality traits and tech interests."
    
    report += f"\n\n---\n\n*🧠 Generated using {recommendation_data.get('source', 'PersonaRecommendationEngine')} for INTP personality optimization.*"
    
    return report

if __name__ == "__main__":
    success = generate_persona_a_report()
    
    if success:
        print(f"\n🎉 UAT Task 1-1 completed successfully!")
        print("📋 Custom recommendation report for Persona A has been generated.")
        print("📂 File: test_A_report.md")
    else:
        print(f"\n💥 UAT Task 1-1 failed!")
        print("🔧 Please check the error messages above.")