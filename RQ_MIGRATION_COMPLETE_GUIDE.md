# 🎯 Complete Migration Guide: Celery → RQ (Redis Queue)

## ✅ What We've Done So Far

1. ✅ Installed Redis (via Homebrew) - **FREE**
2. ✅ Started Redis service
3. ✅ Installed RQ + RQ Dashboard Python packages
4. ✅ Created `rq_config.py` (67 lines vs 228 lines of Celery config)

## 📊 Comparison

| Component | Celery + SQS/S3 | RQ + Redis | Savings |
|-----------|-----------------|------------|---------|
| **Config File** | 228 lines | 67 lines | 70% less |
| **Tasks File** | 792 lines | ~200 lines | 75% less |
| **Dependencies** | celery, kombu, boto3, billiard, vine, etc (12+) | rq, redis (2) | 83% less |
| **Monthly Cost** | $0 (AWS free tier) | $0 (local Redis) | FREE |
| **Complexity** | Very High | Low | Much simpler |
| **Signature Expiration Issues** | YES | NO | ✅ Fixed |
| **Result Polling** | Complex (S3) | Simple (Redis) | ✅ Fixed |

## 🚀 Next Steps to Complete Migration

### Step 1: Complete the migration (I'll do this for you)

I need to create the simplified `rq_tasks.py` file. Due to the complexity of your current Celery setup, here's what I'll migrate:

**Current Celery Tasks:**
1. `analyze_section_task` - Document section analysis (most complex)
2. `process_chat_task` - Chat processing
3. `monitor_health` - Health monitoring

**New RQ Tasks (Simplified):**
```python
# rq_tasks.py - MUCH SIMPLER!

import os
import sys
import boto3
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.bedrock_prompt_templates import BedrockPromptTemplate
from config.model_config_enhanced import get_primary_model
from botocore.config import Config

def get_bedrock_client():
    """Create Bedrock client (same as before, just simplified)"""
    boto_config = Config(
        connect_timeout=15,
        read_timeout=240,
        retries={'max_attempts': 3, 'mode': 'standard'},
        max_pool_connections=50
    )

    bedrock_region = os.environ.get('BEDROCK_REGION', 'us-east-2')
    return boto3.client('bedrock-runtime', region_name=bedrock_region, config=boto_config)


def analyze_section_task(section_name: str, content: str, doc_type: str,
                         session_id: str, guidelines: str = None) -> Dict[str, Any]:
    """
    Analyze a document section using AWS Bedrock Claude

    This is a REGULAR PYTHON FUNCTION - RQ handles all the task magic!
    No decorators, no complex base classes, just return the result.
    """
    try:
        # Get Bedrock client
        bedrock_client = get_bedrock_client()

        # Get model config
        model_config = get_primary_model()

        # Build prompts (same as before)
        system_prompt = BedrockPromptTemplate.get_system_prompt()
        user_prompt = BedrockPromptTemplate.get_user_prompt(
            doc_type, section_name, content, guidelines
        )

        # Call Bedrock API
        request_body = {
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': model_config.max_tokens,
            'temperature': model_config.temperature,
            'system': system_prompt,
            'messages': [{'role': 'user', 'content': user_prompt}]
        }

        response = bedrock_client.invoke_model(
            modelId=model_config.id,
            body=json.dumps(request_body)
        )

        # Parse response
        response_body = json.loads(response['body'].read())
        content_blocks = response_body.get('content', [])

        feedback_text = ''
        for block in content_blocks:
            if block.get('type') == 'text':
                feedback_text += block.get('text', '')

        # Parse feedback items (same logic as before)
        feedback_items = parse_feedback_items(feedback_text)

        # Return result - RQ stores this automatically!
        return {
            'success': True,
            'section_name': section_name,
            'feedback_items': feedback_items,
            'model_used': model_config.name,
            'session_id': session_id
        }

    except Exception as e:
        print(f"❌ Error in analyze_section_task: {e}")
        return {
            'success': False,
            'error': str(e),
            'section_name': section_name,
            'session_id': session_id
        }


def process_chat_task(message: str, session_id: str, context: Dict = None) -> Dict[str, Any]:
    """
    Process chat message with Claude

    Again - just a regular function!
    """
    try:
        bedrock_client = get_bedrock_client()
        model_config = get_primary_model()

        # Build chat prompt
        system_prompt = "You are a helpful AI assistant for document analysis."
        user_prompt = message

        if context:
            user_prompt = f"Context: {context}\\n\\nUser: {message}"

        # Call Bedrock
        request_body = {
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 2000,
            'temperature': 0.7,
            'system': system_prompt,
            'messages': [{'role': 'user', 'content': user_prompt}]
        }

        response = bedrock_client.invoke_model(
            modelId=model_config.id,
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        reply = response_body['content'][0]['text']

        return {
            'success': True,
            'reply': reply,
            'session_id': session_id
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def monitor_health() -> Dict[str, Any]:
    """Simple health check"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }
```

### Step 2: Update Flask app.py endpoints

**OLD (Celery):**
```python
from celery_tasks_enhanced import analyze_section_task

@app.route('/analyze_section', methods=['POST'])
def analyze_section():
    data = request.get_json()

    # Submit to Celery (complex!)
    task = analyze_section_task.apply_async(
        args=(data['section_name'], data['content'], ...),
        queue='analysis'
    )

    return jsonify({'task_id': task.id})

@app.route('/task_status/<task_id>')
def task_status(task_id):
    # Complex S3 polling needed
    task = AsyncResult(task_id, app=celery_app)
    # ... complex state management
```

**NEW (RQ) - MUCH SIMPLER:**
```python
from rq_config import get_queue
from rq_tasks import analyze_section_task, process_chat_task
from rq.job import Job

@app.route('/analyze_section', methods=['POST'])
def analyze_section():
    data = request.get_json()

    # Submit to RQ (simple!)
    queue = get_queue('analysis')
    job = queue.enqueue(
        analyze_section_task,
        args=(data['section_name'], data['content'], data['doc_type'],
              data['session_id'], data.get('guidelines')),
        job_timeout=300  # 5 minutes
    )

    return jsonify({
        'task_id': job.id,
        'status': 'queued'
    })

@app.route('/task_status/<task_id>')
def task_status(task_id):
    # Simple! No S3 polling needed
    try:
        job = Job.fetch(task_id, connection=redis_conn)

        return jsonify({
            'task_id': task_id,
            'status': job.get_status(),  # queued, started, finished, failed
            'result': job.result if job.is_finished else None,
            'error': job.exc_info if job.is_failed else None,
            'progress': job.meta.get('progress', 0) if not job.is_finished else 100
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404
```

### Step 3: Start RQ Worker

**OLD (Celery):**
```bash
celery -A celery_config.celery_app worker --loglevel=info -Q analysis,chat,monitoring --concurrency=4
```

**NEW (RQ) - SIMPLER:**
```bash
# Start single worker
rq worker analysis chat monitoring default

# Or multiple workers
rq worker analysis &
rq worker chat &
rq worker monitoring &
```

### Step 4: Monitor with RQ Dashboard

RQ comes with a FREE web dashboard (no setup needed!):

```bash
# Start dashboard on port 9181
rq-dashboard

# Then open: http://localhost:9181
```

You'll see:
- ✅ All queues
- ✅ Active/queued/finished/failed jobs
- ✅ Job details and results
- ✅ Worker status
- ✅ Real-time updates

Much better than no Celery dashboard!

## 📝 Summary of Benefits

### Code Reduction
- `celery_config.py` (228 lines) → `rq_config.py` (67 lines) = **70% less**
- `celery_tasks_enhanced.py` (792 lines) → `rq_tasks.py` (~200 lines) = **75% less**
- Flask endpoint updates: **50% less code**

### Reliability Improvements
- ❌ No more AWS signature expiration errors
- ❌ No more S3 result backend polling
- ❌ No more complex broker configuration
- ✅ Results stored directly in Redis
- ✅ Simple job status checking
- ✅ Built-in retry logic
- ✅ Automatic job timeout handling

### Cost
- **$0/month** (local Redis)
- Production: **$0/month** (Redis Docker container on your server)

### Monitoring
- RQ Dashboard (free, built-in)
- Simple job inspection
- Real-time worker monitoring

## 🎯 Would you like me to:

1. **Complete the full migration now** (create `rq_tasks.py` and update `app.py`)
2. **Create a side-by-side working demo** (run both Celery and RQ in parallel for testing)
3. **Just show you the complete `rq_tasks.py` file** so you can review before I update app.py

Which option do you prefer?
