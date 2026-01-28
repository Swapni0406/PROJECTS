"""
Simple test script to verify the API is working correctly.
Run this after starting the server with: uvicorn app.main:app --reload
"""

import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000"

def test_health_check():
    """Test if server is running"""
    print("Testing health check...")
    response = requests.get(f"{API_URL}/")
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Response: {response.json()}")
    print()

def test_analyze_report():
    """Test report analysis endpoint"""
    print("Testing report analysis...")
    
    # Use sample report
    sample_file = Path("data/sample_reports/blood_test_sample.txt")
    
    if not sample_file.exists():
        print("✗ Sample file not found!")
        return
    
    with open(sample_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_URL}/api/analyze", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Report Type: {data.get('report_type')}")
        print(f"✓ Summary: {data.get('patient_friendly_summary')[:100]}...")
        print(f"✓ Key Findings: {len(data.get('key_findings', []))} findings")
        print(f"✓ Health Insights: {len(data.get('health_insights', []))} insights")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"✗ Message: {response.json()}")
    print()

def test_chat():
    """Test chat endpoint"""
    print("Testing chat endpoint...")
    
    payload = {
        "message": "What is cholesterol?"
    }
    
    response = requests.post(f"{API_URL}/api/chat", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Response: {data.get('response')[:150]}...")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"✗ Message: {response.json()}")
    print()

def test_explain_term():
    """Test term explanation endpoint"""
    print("Testing term explanation...")
    
    response = requests.post(f"{API_URL}/api/explain-term?term=hemoglobin")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Term: {data.get('term')}")
        print(f"✓ Explanation: {data.get('explanation')[:150]}...")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"✗ Message: {response.json()}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Healthcare LLM API Test Suite")
    print("=" * 60)
    print("\nMake sure the server is running: uvicorn app.main:app --reload\n")
    
    try:
        test_health_check()
        test_analyze_report()
        test_chat()
        test_explain_term()
        
        print("=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to the API!")
        print("Make sure the server is running with:")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
