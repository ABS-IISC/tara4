"""
Enhanced Celery Tasks with Multi-Model Async Fallback
Comprehensive throttling protection and rate limiting

Features:
1. Automatic multi-model fallback on throttling
2. Distributed rate limiting via Redis
3. Token-aware request scheduling
4. Circuit breaker pattern for error recovery
5. Exponential backoff with jitter
6. Comprehensive error handling
"""

import os
import sys
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from celery import Task
from celery.exceptions import Reject, Retry
from celery_config import celery_app

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.async_request_manager import get_async_request_manager, RateLimitConfig
from core.toon_serializer import to_toon, from_toon, toon_savings
from config.bedrock_prompt_templates import BedrockPromptTemplate
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


class EnhancedAnalysisTask(Task):
    """
    Base task with enhanced error handling and monitoring

    Features:
    - Automatic throttling detection
    - Multi-model fallback
    - Rate limit coordination
    - Detailed progress tracking
    """

    def __init__(self):
        super().__init__()
        self._async_manager = None
        self._boto_client = None
        self._models = []

    @property
    def async_manager(self):
        """Lazy-load async request manager"""
        if self._async_manager is None:
            self._async_manager = get_async_request_manager()
        return self._async_manager

    def get_bedrock_client(self):
        """Get or create Bedrock runtime client with optimized configuration"""
        if self._boto_client is None:
            boto_config = Config(
                connect_timeout=15,          # Connection timeout
                read_timeout=240,            # Read timeout (4 minutes)
                retries={
                    'max_attempts': 0,       # Disable boto3 retries (we handle it)
                    'mode': 'standard'
                },
                max_pool_connections=50      # Connection pooling
            )

            # Use us-east-2 for Bedrock API calls to prevent rate limiting
            # Note: S3 operations will continue to use their configured region
            bedrock_region = os.environ.get('BEDROCK_REGION', 'us-east-2')
            self._boto_client = boto3.client(
                'bedrock-runtime',
                region_name=bedrock_region,
                config=boto_config
            )

            print(f"✅ Bedrock client created (region: {bedrock_region})")
            print(f"   Using us-east-2 for Bedrock API calls (rate limit optimization)")

        return self._boto_client

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models in priority order
        Updated with Claude Sonnet 4.5 with extended thinking

        Returns:
            List of model configurations
        """
        if not self._models:
            # Import enhanced model config
            try:
                from config.model_config_enhanced import ClaudeModelRegistry, get_default_models
                model_configs = get_default_models()

                # Convert ModelConfig objects to dicts
                self._models = []
                for config in model_configs:
                    self._models.append({
                        'id': config.id,
                        'name': config.name,
                        'priority': config.priority,
                        'max_tokens': config.max_tokens,
                        'temperature': config.temperature,
                        'supports_extended_thinking': config.supports_extended_thinking
                    })

                print(f"✅ Loaded {len(self._models)} Claude models:")
                for m in self._models:
                    thinking_str = " [Extended Thinking]" if m.get('supports_extended_thinking') else ""
                    print(f"   {m['priority']}. {m['name']}{thinking_str}")

            except ImportError:
                print("⚠️  Enhanced model config not found, using fallback")
                # Fallback to hardcoded models with complete priority order
                self._models = [
                    {
                        'id': 'us.anthropic.claude-sonnet-4-5-20250929-v1:0',
                        'name': 'Claude Sonnet 4.5 (Extended Thinking)',
                        'priority': 1,
                        'max_tokens': 8192,
                        'temperature': 0.7,
                        'supports_extended_thinking': True
                    },
                    {
                        'id': 'us.anthropic.claude-sonnet-4-0-20250514-v1:0',
                        'name': 'Claude Sonnet 4.0',
                        'priority': 2,
                        'max_tokens': 8192,
                        'temperature': 0.7,
                        'supports_extended_thinking': False
                    },
                    {
                        'id': 'anthropic.claude-3-7-sonnet-20250219-v1:0',
                        'name': 'Claude Sonnet 3.7',
                        'priority': 3,
                        'max_tokens': 8192,
                        'temperature': 0.7,
                        'supports_extended_thinking': False
                    },
                    {
                        'id': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
                        'name': 'Claude Sonnet 3.5',
                        'priority': 4,
                        'max_tokens': 8192,
                        'temperature': 0.7,
                        'supports_extended_thinking': False
                    },
                    {
                        'id': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                        'name': 'Claude Sonnet 3.5 v2',
                        'priority': 5,
                        'max_tokens': 8192,
                        'temperature': 0.7,
                        'supports_extended_thinking': False
                    }
                ]

        return self._models

    def invoke_with_fallback(self, system_prompt: str, user_prompt: str,
                           estimated_tokens: int = 0) -> Dict[str, Any]:
        """
        Invoke Bedrock with automatic multi-model fallback

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            estimated_tokens: Estimated token count (for rate limiting)

        Returns:
            Response dict with result or error

        Raises:
            Exception: If all models fail
        """
        async_manager = self.async_manager
        models = self.get_available_models()

        # Wait for rate limit clearance
        wait_time = async_manager.wait_for_rate_limit(estimated_tokens)

        # Record request start
        async_manager.record_request_start()

        last_error = None
        attempted_models = []

        try:
            for model in models:
                model_id = model['id']

                # Check if model is available
                is_available, reason = async_manager.is_model_available(model_id)
                if not is_available:
                    print(f"⏭️ Skipping {model['name']}: {reason}")
                    continue

                attempted_models.append(model['name'])

                try:
                    print(f"🎯 Attempting: {model['name']}")

                    # Build request with extended thinking support
                    request_body = {
                        'anthropic_version': 'bedrock-2023-05-31',
                        'max_tokens': model['max_tokens'],
                        'temperature': model['temperature'],
                        'system': system_prompt,
                        'messages': [{'role': 'user', 'content': user_prompt}]
                    }

                    # Enable extended thinking for Sonnet 4.5
                    if model.get('supports_extended_thinking', False):
                        request_body['thinking'] = {
                            'type': 'enabled',
                            'budget_tokens': 2000  # Reserve tokens for reasoning
                        }
                        # Adjust max_tokens to account for thinking budget
                        request_body['max_tokens'] = model['max_tokens'] - 2000
                        print(f"   🧠 Extended thinking enabled (budget: 2000 tokens)")

                    # Invoke model
                    start_time = time.time()
                    client = self.get_bedrock_client()

                    response = client.invoke_model(
                        body=json.dumps(request_body),
                        modelId=model_id,
                        accept='application/json',
                        contentType='application/json'
                    )

                    duration = time.time() - start_time
                    response_body = json.loads(response.get('body').read())

                    # Extract content
                    content = response_body.get('content', [])
                    if content and len(content) > 0:
                        result_text = content[0].get('text', '')
                    else:
                        result_text = response_body.get('completion', '')

                    # Extract token usage
                    usage = response_body.get('usage', {})
                    input_tokens = usage.get('input_tokens', estimated_tokens or 0)
                    output_tokens = usage.get('output_tokens', len(result_text) // 4)
                    total_tokens = input_tokens + output_tokens

                    # Record success
                    async_manager.record_request_end(
                        success=True,
                        model_id=model_id,
                        duration=duration,
                        tokens_used=total_tokens
                    )

                    print(f"✅ Success: {model['name']} ({duration:.2f}s, {total_tokens} tokens)")

                    return {
                        'success': True,
                        'result': result_text,
                        'model_used': model['name'],
                        'model_id': model_id,
                        'duration': round(duration, 2),
                        'tokens': {
                            'input': input_tokens,
                            'output': output_tokens,
                            'total': total_tokens
                        }
                    }

                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    error_msg = e.response['Error']['Message']
                    last_error = f"{error_code}: {error_msg}"

                    # Check if throttling/503 error
                    is_throttle = any(keyword in error_code.lower() for keyword in
                                    ['throttl', 'ratelimit', 'toomanyrequests', '503', 'serviceunavailable'])

                    if is_throttle:
                        print(f"🚫 {model['name']} throttled: {error_code}")

                        # Record throttling
                        async_manager.record_request_end(
                            success=False,
                            model_id=model_id,
                            duration=time.time() - start_time,
                            error=last_error
                        )

                        # Wait before trying next model
                        time.sleep(RateLimitConfig.MODEL_SWITCH_DELAY_SECONDS)
                        continue  # Try next model
                    else:
                        # Non-throttling error - don't try other models
                        print(f"❌ {model['name']} error: {error_code}")
                        raise e

                except Exception as e:
                    last_error = str(e)
                    print(f"❌ {model['name']} exception: {last_error}")

                    # Record failure
                    async_manager.record_request_end(
                        success=False,
                        model_id=model_id,
                        duration=time.time() - start_time if 'start_time' in locals() else 0,
                        error=last_error
                    )

                    # Check if recoverable
                    if 'throttl' in last_error.lower() or '503' in last_error:
                        time.sleep(RateLimitConfig.MODEL_SWITCH_DELAY_SECONDS)
                        continue  # Try next model

                    raise e  # Non-recoverable error

            # All models exhausted
            error_msg = f"All {len(attempted_models)} models failed/throttled. Tried: {', '.join(attempted_models)}"
            print(f"❌ {error_msg}")

            raise Exception(error_msg)

        finally:
            # Always decrement active requests (already done in record_request_end)
            pass

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        print(f"✅ Task {task_id[:8]} completed successfully")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        print(f"❌ Task {task_id[:8]} failed: {exc}")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        print(f"🔄 Task {task_id[:8]} retrying: {exc}")


@celery_app.task(
    bind=True,
    base=EnhancedAnalysisTask,
    name='celery_tasks_enhanced.analyze_section_task',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3,
    acks_late=True,
    reject_on_worker_lost=True
)
def analyze_section_task(self, section_name: str, content: str,
                        doc_type: str = "Investigation Report",
                        session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Enhanced asynchronous section analysis with multi-model fallback

    Args:
        section_name: Section name
        content: Section content
        doc_type: Document type
        session_id: Session ID (for tracking)

    Returns:
        Analysis result with feedback items
    """
    try:
        print(f"📝 [Task {self.request.id[:8]}] Analyzing: {section_name}")

        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Building prompts...',
                'section': section_name,
                'progress': 10
            }
        )

        # Build prompts using AWS Bedrock templates
        from core.ai_feedback_engine import AIFeedbackEngine
        ai_engine = AIFeedbackEngine()

        hawkeye_checkpoints = ai_engine.hawkeye_sections

        # Build system prompt
        system_prompt = BedrockPromptTemplate.build_system_prompt(
            role="Senior Investigation Analyst",
            expertise=[
                "Hawkeye investigation framework",
                "Document quality assessment",
                "Risk analysis and compliance",
                "Investigation best practices"
            ],
            guidelines=ai_engine._load_hawkeye_checklist()
        )

        # Build analysis prompt
        user_prompt = BedrockPromptTemplate.build_analysis_prompt(
            section_name=section_name,
            content=content,
            framework_checkpoints=hawkeye_checkpoints,
            doc_type=doc_type,
            max_feedback_items=10
        )

        # Estimate tokens
        estimated_tokens = (len(system_prompt) + len(user_prompt)) // 4

        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Invoking AI model...',
                'section': section_name,
                'progress': 30,
                'estimated_tokens': estimated_tokens
            }
        )

        # Invoke with fallback
        start_time = time.time()
        result = self.invoke_with_fallback(system_prompt, user_prompt, estimated_tokens)

        if not result['success']:
            raise Exception(result.get('error', 'Analysis failed'))

        # Parse response
        response_text = result['result']

        # Clean up response (remove markdown if present)
        import re
        cleaned = response_text.strip()
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

        # Parse JSON
        try:
            analysis_result = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            print(f"Response preview: {response_text[:500]}")

            # Try to extract JSON
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group(0))
            else:
                raise Exception(f"Failed to parse AI response: {e}")

        # Validate and filter feedback
        feedback_items = analysis_result.get('feedback_items', [])

        # Filter by confidence >= 0.80
        high_quality_items = [
            item for item in feedback_items
            if isinstance(item, dict) and item.get('confidence', 0) >= 0.80
        ]

        duration = time.time() - start_time

        print(f"✅ [Task {self.request.id[:8]}] Complete: {len(high_quality_items)} items ({duration:.2f}s)")

        self.update_state(
            state='SUCCESS',
            meta={
                'status': 'Analysis complete',
                'section': section_name,
                'feedback_count': len(high_quality_items),
                'duration': round(duration, 2),
                'model_used': result['model_used'],
                'tokens_used': result['tokens']['total']
            }
        )

        return {
            'success': True,
            'feedback_items': high_quality_items,
            'section': section_name,
            'duration': round(duration, 2),
            'model_used': result['model_used'],
            'tokens': result['tokens']
        }

    except Exception as e:
        error_msg = str(e)
        print(f"❌ [Task {self.request.id[:8]}] Error: {error_msg}")

        # Check if should retry
        if 'throttl' in error_msg.lower() or '503' in error_msg or 'all models' in error_msg.lower():
            # Throttling - retry with exponential backoff
            print(f"⏳ [Task {self.request.id[:8]}] Will retry after cooldown...")
            raise self.retry(exc=e, countdown=60)

        # Non-recoverable error
        return {
            'success': False,
            'error': error_msg,
            'section': section_name
        }


@celery_app.task(
    bind=True,
    base=EnhancedAnalysisTask,
    name='celery_tasks_enhanced.process_chat_task',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=3
)
def process_chat_task(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced chat processing with multi-model fallback

    Args:
        query: User query
        context: Chat context

    Returns:
        Chat response
    """
    try:
        print(f"💬 [Task {self.request.id[:8]}] Processing chat: {query[:50]}...")

        # Build prompts
        from core.ai_feedback_engine import AIFeedbackEngine
        ai_engine = AIFeedbackEngine()

        framework_overview = """Hawkeye 20-Point Investigation Checklist covering:
Initial Assessment, Investigation Process, Seller Classification, Enforcement,
Verification, Appeals, Security, Funds, Outreach, Sentiment, Root Cause,
Prevention, Documentation, Collaboration, QC, Improvement, Communication,
Metrics, Legal, Launch."""

        # Build chat prompt
        user_prompt = BedrockPromptTemplate.build_chat_prompt(
            user_query=query,
            context=context,
            framework_overview=framework_overview
        )

        system_prompt = BedrockPromptTemplate.build_system_prompt(
            role="Hawkeye Framework Expert",
            expertise=[
                "Investigation framework guidance",
                "Document review assistance",
                "Best practices consulting"
            ]
        )

        # Estimate tokens
        estimated_tokens = (len(system_prompt) + len(user_prompt)) // 4

        # Invoke with fallback
        start_time = time.time()
        result = self.invoke_with_fallback(system_prompt, user_prompt, estimated_tokens)

        if not result['success']:
            raise Exception(result.get('error', 'Chat failed'))

        duration = time.time() - start_time

        print(f"✅ [Task {self.request.id[:8]}] Chat complete ({duration:.2f}s)")

        return {
            'success': True,
            'response': result['result'],
            'duration': round(duration, 2),
            'model_used': result['model_used'],
            'tokens': result['tokens']
        }

    except Exception as e:
        error_msg = str(e)
        print(f"❌ [Task {self.request.id[:8]}] Chat error: {error_msg}")

        # Retry on throttling
        if 'throttl' in error_msg.lower() or '503' in error_msg:
            raise self.retry(exc=e, countdown=30)

        return {
            'success': False,
            'error': error_msg
        }


# Task for monitoring and cleanup
@celery_app.task(name='celery_tasks_enhanced.monitor_health')
def monitor_health():
    """
    Periodic task to monitor system health

    Runs every 5 minutes via Celery Beat
    """
    try:
        async_manager = get_async_request_manager()
        stats = async_manager.get_stats()

        print("=" * 60)
        print("📊 SYSTEM HEALTH CHECK")
        print("=" * 60)
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Successful: {stats['successful_requests']}")
        print(f"Failed: {stats['failed_requests']}")
        print(f"Throttled: {stats['throttled_requests']}")
        print(f"Active: {stats['active_requests']}")
        print(f"Requests/min: {stats['requests_last_minute']}")
        print(f"Tokens/min: {stats['tokens_last_minute']}")
        print(f"Avg Response: {stats['avg_response_time']:.2f}s")
        print("=" * 60)

        return {'status': 'healthy', 'stats': stats}

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return {'status': 'error', 'error': str(e)}


# Celery Beat schedule
celery_app.conf.beat_schedule = {
    'monitor-health-every-5-minutes': {
        'task': 'celery_tasks_enhanced.monitor_health',
        'schedule': 300.0,  # Every 5 minutes
    },
}
