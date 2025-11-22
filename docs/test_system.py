#!/usr/bin/env python3
"""
Comprehensive System Test
Tests all components end-to-end
"""
import os
import sys

# Set environment variables FIRST
os.environ['S3_BUCKET_NAME'] = 'felix-s3-bucket'
os.environ['S3_BASE_PATH'] = 'tara/'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['CELERY_RESULT_BACKEND'] = 's3://felix-s3-bucket/tara/celery-results/'
os.environ['CELERY_BROKER_URL'] = 'sqs://'
os.environ['SQS_QUEUE_PREFIX'] = 'aiprism-'
os.environ['FLASK_ENV'] = 'development'
os.environ['PORT'] = '8080'

print("=" * 60)
print("AI-Prism System Test")
print("=" * 60)
print()

# Test 1: Celery Config
print("1. Testing Celery Configuration...")
try:
    from celery_config import get_celery_config
    config = get_celery_config()
    print(f"   ✅ Broker: {config['broker_url']}")
    print(f"   ✅ Backend: {config['result_backend']}")
    print(f"   ✅ Region: {config['aws_region']}")
    print(f"   ✅ Queue Prefix: {config['broker_transport_options']['queue_name_prefix']}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

print()

# Test 2: Celery App
print("2. Testing Celery App...")
try:
    from celery_config import celery_app
    print(f"   ✅ Type: {type(celery_app)}")
    # Force initialization by accessing conf
    conf = celery_app.conf
    print(f"   ✅ Celery app initialized")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Tasks Import
print("3. Testing Tasks Import...")
try:
    from celery_tasks_enhanced import analyze_section_task, process_chat_task, monitor_health
    print(f"   ✅ analyze_section_task: {analyze_section_task}")
    print(f"   ✅ process_chat_task: {process_chat_task}")
    print(f"   ✅ monitor_health: {monitor_health}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Registered Tasks
print("4. Testing Registered Tasks...")
try:
    tasks = [t for t in celery_app.tasks.keys() if not t.startswith('celery.')]
    print(f"   ✅ Found {len(tasks)} registered tasks:")
    for task_name in sorted(tasks):
        print(f"      - {task_name}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 5: AWS Bedrock Connection
print("5. Testing AWS Bedrock Connection...")
try:
    import boto3
    from botocore.config import Config

    # Use us-east-2 for Bedrock (where Claude models are available)
    bedrock_config = Config(
        region_name='us-east-2',
        retries={'max_attempts': 3, 'mode': 'adaptive'}
    )

    bedrock = boto3.client('bedrock-runtime', config=bedrock_config)

    # Try a simple request
    response = bedrock.invoke_model(
        modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
        body='{"anthropic_version":"bedrock-2023-05-31","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}',
        contentType='application/json',
        accept='application/json'
    )

    print(f"   ✅ Bedrock connection successful")
    print(f"   ✅ Model: Claude Sonnet 4.5")
    print(f"   ✅ Region: us-east-2")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 6: SQS Connection
print("6. Testing SQS Connection...")
try:
    import boto3
    sqs = boto3.client('sqs', region_name='us-east-1')

    queues = sqs.list_queues(QueueNamePrefix='aiprism-')
    if 'QueueUrls' in queues:
        print(f"   ✅ Found {len(queues['QueueUrls'])} queues:")
        for queue_url in queues['QueueUrls']:
            queue_name = queue_url.split('/')[-1]
            attrs = sqs.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['ApproximateNumberOfMessages']
            )
            msg_count = attrs['Attributes']['ApproximateNumberOfMessages']
            print(f"      - {queue_name}: {msg_count} messages")
    else:
        print(f"   ❌ No queues found")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 7: S3 Connection
print("7. Testing S3 Connection...")
try:
    import boto3
    s3 = boto3.client('s3', region_name='us-east-1')

    # Check if bucket exists
    s3.head_bucket(Bucket='felix-s3-bucket')
    print(f"   ✅ Bucket 'felix-s3-bucket' accessible")

    # List objects in celery results path
    response = s3.list_objects_v2(
        Bucket='felix-s3-bucket',
        Prefix='tara/celery-results/',
        MaxKeys=5
    )

    if 'Contents' in response:
        print(f"   ✅ Found {response['KeyCount']} objects in celery-results/")
    else:
        print(f"   ℹ️  No objects in celery-results/ (empty)")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("System Test Complete")
print("=" * 60)
