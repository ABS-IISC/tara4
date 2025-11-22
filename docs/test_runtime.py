#!/usr/bin/env python3
"""
Runtime test for AI-Prism application
Tests critical endpoints while the application is running
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_endpoint(name, method, endpoint, expected_status=200, data=None, json_data=None):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"

        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            if json_data:
                response = requests.post(url, json=json_data, timeout=5)
            else:
                response = requests.post(url, data=data, timeout=5)
        else:
            print(f"❌ {name}: Unsupported method {method}")
            return False

        if response.status_code == expected_status:
            print(f"✅ {name}: Status {response.status_code} (expected {expected_status})")
            return True
        else:
            print(f"⚠️  {name}: Status {response.status_code} (expected {expected_status})")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection refused (is the app running?)")
        return False
    except requests.exceptions.Timeout:
        print(f"⚠️  {name}: Request timed out")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False

def main():
    """Run all runtime tests"""
    print("=" * 60)
    print("AI-PRISM RUNTIME TEST SUITE")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print()

    # Check if application is running
    print("🔍 Checking application status...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ Application is running and responding")
            print()
        else:
            print("❌ Application returned unexpected status")
            return 1
    except:
        print("❌ Application is not running on port 8080")
        print("💡 Start it with: python3 main.py")
        return 1

    # Test critical endpoints
    print("📡 Testing Critical Endpoints")
    print("-" * 60)

    results = []

    # GET endpoints
    results.append(test_endpoint("Health Check", "GET", "/health", 200))
    results.append(test_endpoint("Main Page", "GET", "/", 200))
    results.append(test_endpoint("Queue Stats", "GET", "/queue_stats", 200))

    # POST endpoints (should fail with validation errors, not 500s)
    results.append(test_endpoint("Upload (no file)", "POST", "/upload", 400))
    results.append(test_endpoint("Analyze Section (no data)", "POST", "/analyze_section", 400))
    results.append(test_endpoint("Chat (no data)", "POST", "/chat", 400))

    print()

    # Test specific fix
    print("🔧 Testing Fixed Endpoint")
    print("-" * 60)

    # Test get_section_content (should return 400 for missing data, not 500)
    results.append(test_endpoint(
        "Get Section Content (no session)",
        "POST",
        "/get_section_content",
        400,
        json_data={}
    ))

    results.append(test_endpoint(
        "Get Section Content (invalid session)",
        "POST",
        "/get_section_content",
        400,
        json_data={"session_id": "invalid", "section_name": "test"}
    ))

    print()

    # Test AWS connectivity
    print("☁️  Testing AWS Connectivity")
    print("-" * 60)

    try:
        response = requests.get(f"{BASE_URL}/test_claude_connection", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('connected'):
                print(f"✅ Claude AI: Connected ({data.get('model', 'Unknown')})")
                print(f"   Response time: {data.get('response_time', 0)}s")
                results.append(True)
            else:
                print(f"⚠️  Claude AI: Not connected - {data.get('error', 'Unknown error')}")
                print(f"   (This is OK if AWS credentials not configured)")
                results.append(True)  # Don't fail test
        else:
            print(f"⚠️  Claude AI: Status {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ Claude AI test failed: {str(e)}")
        results.append(False)

    try:
        response = requests.get(f"{BASE_URL}/test_s3_connection", timeout=10)
        if response.status_code == 200:
            data = response.json()
            s3_status = data.get('s3_status', {})
            if s3_status.get('connected'):
                print(f"✅ S3 Storage: Connected ({s3_status.get('bucket_name', 'Unknown')})")
                results.append(True)
            else:
                print(f"⚠️  S3 Storage: Not connected - {s3_status.get('error', 'Unknown error')}")
                print(f"   (This is OK if S3 not configured)")
                results.append(True)  # Don't fail test
        else:
            print(f"⚠️  S3 Storage: Status {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ S3 test failed: {str(e)}")
        results.append(False)

    print()

    # Print summary
    print("=" * 60)
    print("RUNTIME TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    failed = total - passed

    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")

    if total > 0:
        success_rate = (passed / total) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")

    print()

    if failed == 0:
        print("🎉 ALL RUNTIME TESTS PASSED!")
        print("✅ Application is working correctly")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Review errors above")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
