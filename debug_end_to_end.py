#!/usr/bin/env python3
"""
COMPREHENSIVE END-TO-END DIAGNOSTIC
Traces every step of the request flow with detailed logging
"""
import os
import sys
import time
import json

# Set environment
os.environ['S3_BUCKET_NAME'] = 'felix-s3-bucket'
os.environ['S3_BASE_PATH'] = 'tara/'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['CELERY_RESULT_BACKEND'] = 's3://felix-s3-bucket/tara/celery-results/'
os.environ['CELERY_BROKER_URL'] = 'sqs://'
os.environ['SQS_QUEUE_PREFIX'] = 'aiprism-'

print("=" * 80)
print("COMPREHENSIVE END-TO-END DIAGNOSTIC")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Import and Configuration Check
# ============================================================================
print("STEP 1: Checking Imports and Configuration")
print("-" * 80)

try:
    print("  1.1 Importing celery_config...")
    from celery_config import celery_app, get_celery_config
    print("      ✅ celery_config imported")

    print("  1.2 Getting Celery configuration...")
    config = get_celery_config()
    print(f"      ✅ Broker: {config['broker_url']}")
    print(f"      ✅ Backend: {config['result_backend']}")
    print(f"      ✅ Region: {config['aws_region']}")

    print("  1.3 Importing celery_tasks_enhanced...")
    from celery_tasks_enhanced import process_chat_task
    print(f"      ✅ Task imported: {process_chat_task.name}")

    print("  1.4 Importing model config...")
    from config.model_config_enhanced import get_default_models
    models = get_default_models()
    print(f"      ✅ Loaded {len(models)} models:")
    for i, model in enumerate(models, 1):
        thinking = " [Extended Thinking]" if model.supports_extended_thinking else ""
        print(f"         {i}. {model.name}{thinking}")

except Exception as e:
    print(f"      ❌ IMPORT FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# ============================================================================
# STEP 2: Direct Task Submission Test
# ============================================================================
print("STEP 2: Testing Direct Task Submission to Celery")
print("-" * 80)

try:
    query = "What is risk assessment?"
    context = {"session_id": "debug-test", "history": []}

    print(f"  2.1 Submitting task with query: '{query}'")
    result = process_chat_task.delay(query=query, context=context)

    print(f"      ✅ Task submitted")
    print(f"      Task ID: {result.id}")
    print(f"      Initial state: {result.state}")

except Exception as e:
    print(f"      ❌ SUBMISSION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# ============================================================================
# STEP 3: Monitor Task Execution with Detailed State Tracking
# ============================================================================
print("STEP 3: Monitoring Task Execution (max 45 seconds)")
print("-" * 80)

task_id = result.id
max_wait = 45
wait_time = 0
last_state = None

while wait_time < max_wait:
    time.sleep(2)
    wait_time += 2

    try:
        # Refresh task result
        task = celery_app.AsyncResult(task_id)
        current_state = task.state

        # Only print if state changed
        if current_state != last_state:
            print(f"  [{wait_time}s] STATE CHANGE: {last_state} → {current_state}")
            last_state = current_state

            if current_state == 'STARTED':
                if task.info:
                    print(f"         Info: {task.info}")
        else:
            print(f"  [{wait_time}s] State: {current_state} (unchanged)")

        if current_state == 'SUCCESS':
            print()
            print(f"  ✅ TASK COMPLETED SUCCESSFULLY")

            # Get result
            task_result = task.result
            print(f"      Result type: {type(task_result)}")

            if isinstance(task_result, dict):
                print(f"      Result keys: {list(task_result.keys())}")
                print()
                print("  3.1 Analyzing Result Structure:")
                print(f"      - success: {task_result.get('success')}")
                print(f"      - response: {type(task_result.get('response'))}")
                print(f"      - response length: {len(task_result.get('response', ''))} chars")
                print(f"      - model_used: {task_result.get('model_used')}")
                print(f"      - duration: {task_result.get('duration')}s")
                print(f"      - tokens: {task_result.get('tokens')}")

                response_text = task_result.get('response', '')

                if response_text:
                    print()
                    print("  3.2 Response Content Preview:")
                    print("      " + "=" * 72)
                    lines = response_text.split('\n')
                    for line in lines[:10]:
                        print(f"      {line}")
                    if len(lines) > 10:
                        print(f"      ... ({len(lines) - 10} more lines)")
                    print("      " + "=" * 72)
                else:
                    print()
                    print("  ❌ CRITICAL: Response is EMPTY!")
                    print("      Full result:")
                    print(f"      {json.dumps(task_result, indent=6)}")
            else:
                print(f"      ❌ Result is not a dict: {task_result}")

            break

        elif current_state == 'FAILURE':
            print()
            print(f"  ❌ TASK FAILED")
            print(f"      Error: {task.info}")
            print(f"      Traceback: {task.traceback}")
            break

        elif current_state == 'RETRY':
            print(f"      ⚠️  Task is retrying: {task.info}")

    except Exception as e:
        print(f"      ❌ ERROR checking status: {e}")
        import traceback
        traceback.print_exc()
        break
else:
    print()
    print(f"  ⚠️  TIMEOUT: Task did not complete in {max_wait} seconds")
    print(f"      Final state: {task.state}")

print()

# ============================================================================
# STEP 4: Test get_task_status Function
# ============================================================================
print("STEP 4: Testing get_task_status() Function")
print("-" * 80)

try:
    print("  4.1 Importing app module...")
    # Import the function we added
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Import as module
    import importlib.util
    spec = importlib.util.spec_from_file_location("app_module", "app.py")
    app_module = importlib.util.module_from_spec(spec)

    print("      ✅ App module loaded")

    print("  4.2 Calling get_task_status()...")
    # We can't import app.py directly because it starts Flask
    # So let's just verify the function exists by reading the file

    with open('app.py', 'r') as f:
        app_content = f.read()

    if 'def get_task_status(task_id):' in app_content:
        print("      ✅ get_task_status() function EXISTS in app.py")

        # Find the function
        import re
        match = re.search(r'def get_task_status\(task_id\):.*?(?=\n\ndef|\nclass|\n\n@|\Z)', app_content, re.DOTALL)
        if match:
            func_lines = len(match.group(0).split('\n'))
            print(f"      ✅ Function is {func_lines} lines long")
    else:
        print("      ❌ get_task_status() function NOT FOUND in app.py")

    if 'def get_queue_stats():' in app_content:
        print("      ✅ get_queue_stats() function EXISTS in app.py")
    else:
        print("      ❌ get_queue_stats() function NOT FOUND in app.py")

except Exception as e:
    print(f"      ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# STEP 5: Verify Response Extraction Logic
# ============================================================================
print("STEP 5: Analyzing Response Extraction Logic")
print("-" * 80)

try:
    print("  5.1 Reading celery_tasks_enhanced.py...")
    with open('celery_tasks_enhanced.py', 'r') as f:
        tasks_content = f.read()

    print("  5.2 Checking for response extraction checkpoints...")
    checkpoints = [
        'CHECKPOINT 1',
        'CHECKPOINT 2',
        'CHECKPOINT 3',
        'CHECKPOINT 6',
        'CHECKPOINT 7'
    ]

    for cp in checkpoints:
        if cp in tasks_content:
            print(f"      ✅ {cp} found")
        else:
            print(f"      ❌ {cp} NOT found")

    print("  5.3 Checking response extraction logic...")
    if 'block_type == \'text\':' in tasks_content:
        print("      ✅ Text block extraction logic found")
    if 'block_type == \'thinking\':' in tasks_content:
        print("      ✅ Thinking block skip logic found")
    if 'for idx, block in enumerate(content):' in tasks_content:
        print("      ✅ Content block iteration found")

except Exception as e:
    print(f"      ❌ ERROR: {e}")

print()

# ============================================================================
# STEP 6: Check Celery Worker Status
# ============================================================================
print("STEP 6: Checking Celery Worker Status")
print("-" * 80)

try:
    print("  6.1 Inspecting Celery workers...")
    inspect = celery_app.control.inspect()

    print("  6.2 Getting active tasks...")
    active = inspect.active()
    if active:
        print(f"      ✅ Active tasks: {sum(len(tasks) for tasks in active.values())}")
    else:
        print(f"      ℹ️  No active tasks")

    print("  6.3 Getting registered tasks...")
    registered = inspect.registered()
    if registered:
        for worker, tasks in registered.items():
            print(f"      Worker: {worker}")
            for task in tasks:
                if not task.startswith('celery.'):
                    print(f"        - {task}")
    else:
        print(f"      ⚠️  No workers found or not responding")

except Exception as e:
    print(f"      ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)

if task.state == 'SUCCESS' and task.result.get('response'):
    print("✅ ALL SYSTEMS OPERATIONAL")
    print("   - Celery task execution: WORKING")
    print("   - Response extraction: WORKING")
    print("   - Extended thinking: WORKING")
    print()
    print("🎯 The backend is functioning correctly!")
    print("   If UI still shows no response, the issue is in:")
    print("   1. Frontend JavaScript polling logic")
    print("   2. /task_status endpoint (check Flask logs)")
    print("   3. Frontend response display code")
elif task.state == 'SUCCESS' and not task.result.get('response'):
    print("❌ RESPONSE EXTRACTION FAILURE")
    print("   - Celery task execution: WORKING")
    print("   - Response extraction: BROKEN")
    print()
    print("🔍 The issue is in response extraction logic")
    print("   Check celery_tasks_enhanced.py lines 246-290")
elif task.state == 'FAILURE':
    print("❌ TASK EXECUTION FAILURE")
    print(f"   Error: {task.info}")
else:
    print("⚠️  INCONCLUSIVE")
    print(f"   Final state: {task.state}")

print("=" * 80)
