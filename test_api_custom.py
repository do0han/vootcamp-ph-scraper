#!/usr/bin/env python3
"""
Test the custom recommendation API directly
"""

import json
import subprocess
import sys
import os

def test_api_directly():
    """Test the custom recommendation API by running the Python script directly"""
    
    print("🧪 Testing Custom Recommendation API Logic")
    print("=" * 60)
    
    # Test data similar to what would come from the frontend
    test_data = {
        "mbti": "INFJ",
        "interests": ["vintage camera", "specialty coffee", "book reviews"],
        "channel_category": "Lifestyle", 
        "budget_level": "medium"
    }
    
    print("📝 Test Data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    # Create a test script that mimics the API route behavior
    test_script = f"""
import sys
import json
import os
sys.path.append('{os.getcwd()}')

from persona_recommendation_engine import PersonaRecommendationEngine

# Test data
user_data = {json.dumps(test_data)}

try:
    # Initialize engine with debug mode
    engine = PersonaRecommendationEngine(debug_mode=True)
    
    # Generate custom recommendation
    result = engine.generate_custom_recommendation(user_data)
    
    # Output result in the same format as the API
    print("RESULT_START")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("RESULT_END")
    
except Exception as e:
    print("ERROR_START")
    print(f"Error: {{str(e)}}")
    print("ERROR_END")
    sys.exit(1)
"""
    
    print("🚀 Running API logic test...")
    
    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            print(f"❌ Test failed with return code {result.returncode}")
            print("STDERR:", result.stderr)
            return
        
        # Parse the result
        output = result.stdout
        print("📤 Raw output (first 500 chars):")
        print(output[:500] + ("..." if len(output) > 500 else ""))
        print()
        
        # Extract JSON result
        import re
        match = re.search(r'RESULT_START\s*(.*?)\s*RESULT_END', output, re.DOTALL)
        if match:
            json_result = json.loads(match.group(1))
            
            print("✅ API Logic Test Successful!")
            print(f"📊 Statistics:")
            print(f"   • Products: {json_result['statistics']['total_products']}")
            print(f"   • Average Score: {json_result['statistics']['average_score']}/100")
            print(f"   • Content Ideas: {json_result['statistics']['content_ideas_count']}")
            
            print(f"\n🛍️ Product Examples:")
            for i, product in enumerate(json_result['product_recommendations'][:2], 1):
                print(f"   {i}. {product['product']} - {product['trending_score']}점")
                print(f"      💰 {product['price']}")
            
            print(f"\n💡 Content Ideas:")
            for i, idea in enumerate(json_result['content_ideas'][:2], 1):
                print(f"   {i}. {idea['title']}")
                print(f"      📱 {idea['platform']} | {idea['type']}")
            
            # Save result
            with open('api_test_result.json', 'w', encoding='utf-8') as f:
                json.dump(json_result, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 Result saved to: api_test_result.json")
            
        else:
            print("❌ Could not parse result from output")
            print("Raw output:", output)
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")

if __name__ == "__main__":
    test_api_directly()