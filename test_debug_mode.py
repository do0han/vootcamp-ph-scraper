#!/usr/bin/env python3
"""
Test the debug transparency mode of PersonaRecommendationEngine
"""

from persona_recommendation_engine import PersonaRecommendationEngine

def test_debug_mode():
    """Test the transparency report functionality"""
    
    print("🚀 Testing PersonaRecommendationEngine Debug Mode")
    print("=" * 80)
    
    # Create engine with debug mode enabled
    engine = PersonaRecommendationEngine(debug_mode=True)
    
    # Test specific persona to see detailed debug output
    print("\n📊 Testing product scoring for Young Professional Fashionista...")
    recommendations = engine.generate_product_recommendations("young_professional_fashionista")
    
    print("\n💡 Testing content generation...")
    content_ideas = engine.generate_content_ideas("young_professional_fashionista")
    
    print("\n📋 Generating full transparency report...")
    full_report = engine.generate_full_recommendation_report()
    
    print("\n✅ Debug mode test completed!")
    print(f"📝 Generated {len(engine.debug_log)} debug log entries")

if __name__ == "__main__":
    test_debug_mode()