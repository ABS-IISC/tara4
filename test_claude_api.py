#!/usr/bin/env python3
"""
Test Claude API End-to-End through Deployed Application
Tests document analysis and chatbot functionality with AWS Bedrock
"""

import requests
import json
import time
import os
from io import BytesIO

# Configuration
BASE_URL = "http://ai-prism-prod.eu-north-1.elasticbeanstalk.com"
# BASE_URL = "http://localhost:8080"  # For local testing

def test_health():
    """Test health endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check passed")
        print(f"   Region: {data.get('region')}")
        print(f"   Bedrock Region: {data.get('bedrock_region')}")
        print(f"   Model ID: {data.get('model_id')}")
        print(f"   S3 Bucket: {data.get('s3_bucket')}")
        print(f"   Bedrock Supported: {data.get('is_bedrock_supported')}")
        return True
    else:
        print(f"❌ Health check failed")
        return False

def test_document_analysis():
    """Test document analysis with Claude API"""
    print("\n" + "="*80)
    print("TEST 2: Document Analysis - Claude API")
    print("="*80)

    # Create a session to maintain cookies
    session = requests.Session()

    # Upload document (requires DOCX file)
    print("\nStep 1: Uploading test document...")

    docx_path = 'test_risk_assessment.docx'
    if not os.path.exists(docx_path):
        print(f"❌ Test DOCX file not found: {docx_path}")
        print("   Please run: python3 -c 'from docx import Document; doc=Document(); doc.add_heading(\"Test\"); doc.save(\"test_risk_assessment.docx\")'")
        return False

    files = {
        'document': ('test_risk_assessment.docx', open(docx_path, 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    }

    data = {
        'guidelines_preference': 'old_only'
    }

    upload_response = session.post(f"{BASE_URL}/upload", files=files, data=data)

    if upload_response.status_code != 200:
        print(f"❌ Document upload failed: {upload_response.status_code}")
        print(f"   Response: {upload_response.text}")
        return False

    upload_data = upload_response.json()
    if not upload_data.get('success'):
        print(f"❌ Upload unsuccessful: {upload_data.get('error', 'Unknown error')}")
        return False

    session_id = upload_data.get('session_id')
    sections = upload_data.get('sections', [])

    print(f"✅ Document uploaded successfully")
    print(f"   Session ID: {session_id}")
    print(f"   Sections detected: {len(sections)}")
    for section in sections[:3]:  # Show first 3 sections
        print(f"     - {section}")

    # Analyze a section with Claude
    print("\nStep 2: Analyzing section with Claude API...")

    # Pick the first substantial section (skip Executive Summary for better test)
    test_section = "Methodology" if "Methodology" in sections else sections[0] if sections else None

    if not test_section:
        print("❌ No sections available for analysis")
        return False

    print(f"   Analyzing section: {test_section}")

    analyze_payload = {
        'session_id': session_id,
        'section_name': test_section
    }

    analyze_response = session.post(
        f"{BASE_URL}/analyze_section",
        json=analyze_payload,
        headers={'Content-Type': 'application/json'}
    )

    if analyze_response.status_code != 200:
        print(f"❌ Analysis request failed: {analyze_response.status_code}")
        print(f"   Response: {analyze_response.text}")
        return False

    analyze_data = analyze_response.json()

    if not analyze_data.get('success'):
        print(f"❌ Analysis unsuccessful: {analyze_data.get('error', 'Unknown error')}")
        return False

    # Check if it's async (RQ/Celery) or sync
    is_async = analyze_data.get('async', False)

    if is_async:
        task_id = analyze_data.get('task_id')
        print(f"✅ Analysis task queued (async mode)")
        print(f"   Task ID: {task_id}")
        print(f"   Enhanced Mode: {analyze_data.get('enhanced', False)}")

        # Poll for results
        print("\nStep 3: Polling for analysis results...")
        max_retries = 60  # 60 seconds max
        retry_count = 0

        while retry_count < max_retries:
            time.sleep(1)
            retry_count += 1

            status_response = session.get(f"{BASE_URL}/task_status/{task_id}")

            if status_response.status_code != 200:
                print(f"   Retry {retry_count}: Status check failed")
                continue

            status_data = status_response.json()
            task_status = status_data.get('status')

            print(f"   Retry {retry_count}: Task status = {task_status}")

            if task_status == 'completed':
                result = status_data.get('result', {})
                feedback_items = result.get('feedback_items', [])

                print(f"\n✅ Claude API analysis completed successfully!")
                print(f"   Analysis duration: ~{retry_count} seconds")
                print(f"   Feedback items generated: {len(feedback_items)}")

                if feedback_items:
                    print(f"\n   Sample feedback items:")
                    for i, item in enumerate(feedback_items[:3], 1):
                        print(f"     {i}. {item.get('type', 'N/A')}: {item.get('message', 'N/A')[:80]}...")

                return True

            elif task_status in ['failed', 'error']:
                error_msg = status_data.get('error', 'Unknown error')
                print(f"\n❌ Analysis failed: {error_msg}")
                return False

        print(f"\n❌ Analysis timed out after {max_retries} seconds")
        return False

    else:
        # Synchronous result
        feedback_items = analyze_data.get('feedback_items', [])

        print(f"✅ Claude API analysis completed (sync mode)")
        print(f"   Feedback items generated: {len(feedback_items)}")

        if feedback_items:
            print(f"\n   Sample feedback items:")
            for i, item in enumerate(feedback_items[:3], 1):
                print(f"     {i}. {item.get('type', 'N/A')}: {item.get('message', 'N/A')[:80]}...")

        return True

def test_chatbot():
    """Test chatbot with Claude API"""
    print("\n" + "="*80)
    print("TEST 3: Chatbot - Claude API")
    print("="*80)

    # Create a session to maintain cookies
    session = requests.Session()

    # Create a test document first (requires DOCX)
    docx_path = 'test_risk_assessment.docx'
    if not os.path.exists(docx_path):
        print(f"❌ Test DOCX file not found")
        return False

    files = {
        'document': ('test_risk_assessment.docx', open(docx_path, 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    }

    data = {
        'guidelines_preference': 'old_only'
    }

    upload_response = session.post(f"{BASE_URL}/upload", files=files, data=data)

    if upload_response.status_code != 200:
        print(f"❌ Document upload failed")
        return False

    upload_data = upload_response.json()
    session_id = upload_data.get('session_id')

    print(f"✅ Test session created: {session_id}")

    # Send a chat message
    print("\nStep 1: Sending chat message to Claude...")

    chat_payload = {
        'session_id': session_id,
        'message': 'Can you summarize the key points in this document?'
    }

    chat_response = session.post(
        f"{BASE_URL}/chat",
        json=chat_payload,
        headers={'Content-Type': 'application/json'}
    )

    if chat_response.status_code != 200:
        print(f"❌ Chat request failed: {chat_response.status_code}")
        print(f"   Response: {chat_response.text}")
        return False

    chat_data = chat_response.json()

    if not chat_data.get('success'):
        print(f"❌ Chat unsuccessful: {chat_data.get('error', 'Unknown error')}")
        return False

    # Check if it's async
    is_async = chat_data.get('async', False)

    if is_async:
        task_id = chat_data.get('task_id')
        print(f"✅ Chat task queued (async mode)")
        print(f"   Task ID: {task_id}")

        # Poll for results
        print("\nStep 2: Polling for chat response...")
        max_retries = 30
        retry_count = 0

        while retry_count < max_retries:
            time.sleep(1)
            retry_count += 1

            status_response = session.get(f"{BASE_URL}/task_status/{task_id}")

            if status_response.status_code != 200:
                continue

            status_data = status_response.json()
            task_status = status_data.get('status')

            print(f"   Retry {retry_count}: Task status = {task_status}")

            if task_status == 'completed':
                result = status_data.get('result', {})
                response_text = result.get('response', '')

                print(f"\n✅ Claude chatbot response received!")
                print(f"   Response length: {len(response_text)} characters")
                print(f"\n   Claude's response:")
                print(f"   {response_text[:200]}...")

                return True

            elif task_status in ['failed', 'error']:
                error_msg = status_data.get('error', 'Unknown error')
                print(f"\n❌ Chat failed: {error_msg}")
                return False

        print(f"\n❌ Chat timed out")
        return False

    else:
        # Synchronous result
        response_text = chat_data.get('response', '')

        print(f"✅ Claude chatbot response received (sync mode)")
        print(f"   Response length: {len(response_text)} characters")
        print(f"\n   Claude's response:")
        print(f"   {response_text[:200]}...")

        return True

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 CLAUDE API END-TO-END TESTING")
    print("="*80)
    print(f"Target: {BASE_URL}")
    print("Testing: Document Analysis + Chatbot with AWS Bedrock")

    results = {
        'health': False,
        'document_analysis': False,
        'chatbot': False
    }

    # Run tests
    try:
        results['health'] = test_health()

        if results['health']:
            results['document_analysis'] = test_document_analysis()
            results['chatbot'] = test_chatbot()

    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.upper()}: {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())

    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n✅ ALL TESTS PASSED - Claude API is fully operational!")
        return 0
    else:
        print(f"\n❌ {total_tests - passed_tests} test(s) failed")
        return 1

if __name__ == '__main__':
    exit(main())
