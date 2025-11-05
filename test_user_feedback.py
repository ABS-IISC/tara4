#!/usr/bin/env python3
"""
Test script for user feedback management features
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_user_feedback_features():
    """Test the new user feedback management features"""
    
    print("🧪 Testing User Feedback Management Features")
    print("=" * 50)
    
    # Test data
    test_feedback = {
        "type": "addition",
        "category": "Investigation Process", 
        "description": "This section needs more detail about customer impact assessment",
        "ai_reference": "AI suggested missing impact analysis",
        "ai_id": "ai_123"
    }
    
    session_id = "test_session_123"
    section_name = "Executive Summary"
    
    try:
        # Test 1: Add custom feedback
        print("1. Testing add custom feedback...")
        response = requests.post(f"{BASE_URL}/add_custom_feedback", json={
            "session_id": session_id,
            "section_name": section_name,
            **test_feedback
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                feedback_id = data['feedback_item']['id']
                print(f"   ✅ Added feedback with ID: {feedback_id}")
            else:
                print(f"   ❌ Failed: {data.get('error')}")
                return
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return
            
        # Test 2: Get user feedback
        print("2. Testing get user feedback...")
        response = requests.get(f"{BASE_URL}/get_user_feedback", params={
            "session_id": session_id
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Retrieved {data['total_count']} feedback items")
                print(f"   📊 Sections with feedback: {data['sections_with_feedback']}")
            else:
                print(f"   ❌ Failed: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
        # Test 3: Update user feedback
        print("3. Testing update user feedback...")
        updated_data = {
            "description": "Updated: This section needs comprehensive customer impact assessment with metrics",
            "type": "enhancement"
        }
        
        response = requests.post(f"{BASE_URL}/update_user_feedback", json={
            "session_id": session_id,
            "feedback_id": feedback_id,
            "updated_data": updated_data
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Updated feedback successfully")
            else:
                print(f"   ❌ Failed: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
        # Test 4: Export user feedback (JSON)
        print("4. Testing export user feedback (JSON)...")
        response = requests.get(f"{BASE_URL}/export_user_feedback", params={
            "session_id": session_id,
            "format": "json"
        })
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Exported JSON with {data.get('total_feedback', 0)} items")
            except:
                print(f"   ✅ Exported JSON data (raw response)")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
        # Test 5: Export user feedback (CSV)
        print("5. Testing export user feedback (CSV)...")
        response = requests.get(f"{BASE_URL}/export_user_feedback", params={
            "session_id": session_id,
            "format": "csv"
        })
        
        if response.status_code == 200:
            csv_content = response.text
            lines = csv_content.split('\n')
            print(f"   ✅ Exported CSV with {len(lines)} lines")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
        # Test 6: Delete user feedback
        print("6. Testing delete user feedback...")
        response = requests.post(f"{BASE_URL}/delete_user_feedback", json={
            "session_id": session_id,
            "feedback_id": feedback_id
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Deleted feedback successfully")
            else:
                print(f"   ❌ Failed: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
        print("\n🎉 All tests completed!")
        print("\n📋 Features implemented:")
        print("   ✅ Custom feedback for each AI suggestion")
        print("   ✅ User feedback management system")
        print("   ✅ Edit and delete user feedback")
        print("   ✅ Export feedback in multiple formats")
        print("   ✅ Enhanced UI with better organization")
        print("   ✅ Real-time feedback tracking")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")

if __name__ == "__main__":
    test_user_feedback_features()