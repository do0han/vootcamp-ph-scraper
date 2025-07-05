#!/usr/bin/env python3
"""
Test script to verify the report dispatcher integration
"""

import requests
import json

def test_api_endpoint():
    """Test the /api/generate endpoint with the new dispatcher"""
    
    # API endpoint
    url = "http://localhost:3003/api/generate"
    
    # Test data matching the frontend interface
    test_payload = {
        "persona": {
            "id": "tech",
            "name": "테크 크리에이터", 
            "emoji": "💻"
        },
        "reportType": {
            "id": "content-strategy",
            "name": "콘텐츠 전략"
        }
    }
    
    print("🚀 Testing Report Dispatcher API Integration")
    print(f"📡 Endpoint: {url}")
    print(f"📊 Payload: {json.dumps(test_payload, indent=2, ensure_ascii=False)}")
    print("-" * 50)
    
    try:
        # Make the API call
        response = requests.post(url, json=test_payload, timeout=30)
        
        print(f"📈 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Report Generated:")
            print("-" * 30)
            print(data.get('report', 'No report in response'))
            print("-" * 30)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Next.js server is running on port 3003")
        print("   Run: npm run dev -- --port 3003")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_all_report_types():
    """Test all available report types"""
    
    url = "http://localhost:3003/api/generate"
    
    # Test all report types
    report_types = [
        {"id": "content-strategy", "name": "콘텐츠 전략"},
        {"id": "monetization", "name": "수익화 전략"},
        {"id": "content-ideas", "name": "콘텐츠 아이디어"},
        {"id": "trend-analysis", "name": "트렌드 분석"},
        {"id": "competitor-analysis", "name": "경쟁자 분석"}
    ]
    
    persona = {
        "id": "tech",
        "name": "테크 크리에이터",
        "emoji": "💻"
    }
    
    print("\n🧪 Testing All Report Types")
    print("=" * 50)
    
    for report_type in report_types:
        payload = {
            "persona": persona,
            "reportType": report_type
        }
        
        print(f"\n📊 Testing: {report_type['name']} ({report_type['id']})")
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                report = data.get('report', 'No report')
                print(f"✅ Success: {report}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Server not running")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test single report type
    test_api_endpoint()
    
    # Test all report types
    test_all_report_types()
    
    print("\n🎯 Test Summary:")
    print("- If you see 'Placeholder for X Report', the dispatcher is working!")
    print("- If you see connection errors, start the Next.js server: npm run dev -- --port 3003")
    print("- The placeholder functions can now be replaced with actual report generation logic")