#!/usr/bin/env python3
"""
Test script for Persona Recommendation Engine debug mode
"""

from persona_recommendation_engine import PersonaRecommendationEngine

def test_debug_mode():
    """Test the transparency report feature"""
    print("🔍 Testing PersonaRecommendationEngine in DEBUG MODE")
    print("="*80)
    
    # Initialize engine in debug mode
    engine = PersonaRecommendationEngine(debug_mode=True)
    
    # Generate full report
    report = engine.generate_full_recommendation_report()
    
    print("\n🎉 Debug test completed!")
    return report

if __name__ == "__main__":
    test_debug_mode()