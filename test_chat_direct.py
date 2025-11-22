#!/usr/bin/env python3
"""
Direct test of chat task submission and processing
"""
import os
import sys
import time
import json

# Set environment variables
os.environ['S3_BUCKET_NAME'] = 'felix-s3-bucket'
os.environ['S3_BASE_PATH'] = 'tara/'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['CELERY_RESULT_BACKEND'] = 's3://felix-s3-bucket/tara/celery-results/'
os.environ['CELERY_BROKER_URL'] = 'sqs://'
os.environ['SQS_QUEUE_PREFIX'] = 'aiprism-'

print("=" * 60)
print("Testing Chat Task Direct Submission")
print("=" * 60)
print()

# Import task
print("1. Importing task...")
from celery_tasks_enhanced import process_chat_task
print(f"   ✅ Task imported: {process_chat_task}")
print()

# Submit task
print("2. Submitting task to queue...")
try:
    query = "What is risk assessment?"
    context = {"session_id": "test-123", "history": []}

    # Use delay() to submit to queue
    result = process_chat_task.delay(query=query, context=context)

    print(f"   ✅ Task submitted!")
    print(f"   Task ID: {result.id}")
    print(f"   Task state: {result.state}")
    print()

    # Wait for result
    print("3. Waiting for task to complete...")
    print("   (Checking every 2 seconds, max 30 seconds)")

    max_wait = 30
    wait_time = 0
    while wait_time < max_wait:
        time.sleep(2)
        wait_time += 2

        state = result.state
        print(f"   [{wait_time}s] State: {state}")

        if state == 'SUCCESS':
            print()
            print("4. Task completed successfully!")
            task_result = result.get()
            print(f"   Response: {json.dumps(task_result, indent=2)}")
            break
        elif state == 'FAILURE':
            print()
            print("❌ Task failed!")
            print(f"   Error: {result.info}")
            break
        elif state in ['PENDING', 'STARTED']:
            continue
        else:
            print(f"   Unknown state: {state}")
            break
    else:
        print()
        print("⚠️  Task did not complete within 30 seconds")
        print(f"   Final state: {result.state}")

except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Test Complete")
print("=" * 60)
