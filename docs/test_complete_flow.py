#!/usr/bin/env python3
"""
Complete UI Flow Test
Tests the full async workflow: /chat → /task_status → result
"""
import time
import json
import requests

PORT = 8080
BASE_URL = f"http://localhost:{PORT}"

print("=" * 70)
print("COMPLETE UI FLOW TEST")
print("=" * 70)
print(f"Testing: {BASE_URL}")
print()

# Step 1: Test connection
print("1. Testing Claude connection...")
try:
    response = requests.get(f"{BASE_URL}/test_claude_connection", timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Connected: {data['claude_status']['connected']}")
        print(f"   Model: {data['claude_status']['model']}")
    else:
        print(f"   ❌ Connection test failed")
        exit(1)
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    exit(1)

print()

# Step 2: Create a session (needed for chat)
print("2. Creating review session...")
try:
    response = requests.post(f"{BASE_URL}/upload_document",
                            files={'document': ('test.txt', b'Test document content', 'text/plain')},
                            timeout=30)
    if response.status_code == 200:
        data = response.json()
        session_id = data.get('session_id')
        print(f"   ✅ Session created: {session_id}")
    else:
        print(f"   ❌ Session creation failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    exit(1)

print()

# Step 3: Submit chat message (async)
print("3. Submitting chat message (async)...")
try:
    payload = {
        'session_id': session_id,
        'message': 'What is risk assessment?',
        'current_section': 'test_section',
        'ai_model': 'claude-sonnet-4-5'
    }

    response = requests.post(f"{BASE_URL}/chat",
                            json=payload,
                            timeout=30)

    if response.status_code == 200:
        data = response.json()
        if data.get('async'):
            task_id = data.get('task_id')
            print(f"   ✅ Task submitted: {task_id}")
            print(f"   Status: {data.get('status')}")
        else:
            print(f"   ⚠️  Got synchronous response (not async)")
            print(f"   Response: {data.get('response', '')[:100]}")
            exit(0)
    else:
        print(f"   ❌ Chat submission failed: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# Step 4: Poll for result
print("4. Polling for task result...")
print("   (Checking every 2 seconds, max 30 seconds)")
print()

max_wait = 30
wait_time = 0

while wait_time < max_wait:
    time.sleep(2)
    wait_time += 2

    try:
        response = requests.get(f"{BASE_URL}/task_status/{task_id}", timeout=10)

        if response.status_code == 200:
            status_data = response.json()
            state = status_data.get('state')
            progress = status_data.get('progress', 0)

            print(f"   [{wait_time}s] State: {state}, Progress: {progress}%")

            if state == 'SUCCESS':
                print()
                print("5. ✅ TASK COMPLETED SUCCESSFULLY!")
                result = status_data.get('result', {})

                print(f"   Success: {result.get('success')}")
                response_text = result.get('response', '')
                print(f"   Response length: {len(response_text)} chars")
                print(f"   Model used: {result.get('model_used')}")
                print(f"   Duration: {result.get('duration')}s")
                print(f"   Tokens: {result.get('tokens')}")
                print()
                print("   Response preview:")
                print("   " + "-" * 66)
                print(f"   {response_text[:500]}")
                if len(response_text) > 500:
                    print("   ...")
                print("   " + "-" * 66)

                if response_text:
                    print()
                    print("🎉 SUCCESS! Claude responses are now working in the UI!")
                else:
                    print()
                    print("❌ FAILURE! Response is empty!")

                break

            elif state == 'FAILURE':
                print()
                print("❌ Task failed!")
                print(f"   Error: {status_data.get('error')}")
                break

            elif state in ['PENDING', 'STARTED']:
                continue
            else:
                print(f"   Unknown state: {state}")
                break
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            break

    except Exception as e:
        print(f"   ❌ ERROR polling status: {e}")
        break
else:
    print()
    print("⚠️  Task did not complete within 30 seconds")

print()
print("=" * 70)
print("Test Complete")
print("=" * 70)
