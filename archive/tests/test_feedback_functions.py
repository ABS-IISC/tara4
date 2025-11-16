#!/usr/bin/env python3
"""
Test Accept/Reject Feedback Functions
"""

import requests
import json

def test_feedback_functions():
    """Test the accept and reject feedback endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Accept/Reject Feedback Functions")
    print("=" * 50)
    
    # Test data
    test_data = {
        "session_id": "test_session_123",
        "section_name": "Test Section",
        "feedback_id": "test_feedback_1"
    }
    
    # Test accept feedback
    print("1. Testing Accept Feedback...")
    try:
        response = requests.post(f"{base_url}/accept_feedback", json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Accept test failed: {e}")
    
    # Test reject feedback
    print("\n2. Testing Reject Feedback...")
    try:
        response = requests.post(f"{base_url}/reject_feedback", json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Reject test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Note: These tests will fail with 'Invalid session' which is expected")
    print("The important thing is that the endpoints respond correctly")

if __name__ == "__main__":
    test_feedback_functions()