"""
Celery Tasks for AI-Prism
Asynchronous task processing for document analysis and chat
"""
import os
import sys
import time
from celery import Task
from celery_config import celery_app

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ai_feedback_engine import AIFeedbackEngine

# Create AI engine instance (shared across tasks)
ai_engine = AIFeedbackEngine()


class CallbackTask(Task):
    """Base task with callbacks for progress tracking"""

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        print(f"✅ Task {task_id} completed successfully")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        print(f"❌ Task {task_id} failed: {exc}")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        print(f"🔄 Task {task_id} retrying after error: {exc}")


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name='celery_tasks.analyze_section_task',
    autoretry_for=(Exception,),
    retry_backoff=True,  # Exponential backoff
    retry_backoff_max=600,  # Max 10 minutes
    retry_jitter=True,  # Add jitter to backoff
    max_retries=3
)
def analyze_section_task(self, section_name, content, doc_type="Full Write-up", session_id=None):
    """
    Asynchronous document analysis task

    Args:
        section_name: Name of the section to analyze
        content: Section content
        doc_type: Document type
        session_id: Optional session ID for logging

    Returns:
        dict: Analysis result with feedback_items
    """
    try:
        # Update task state to show progress
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Analyzing section...',
                'section': section_name,
                'progress': 0
            }
        )

        print(f"📝 [Task {self.request.id}] Starting analysis: {section_name}", flush=True)
        start_time = time.time()

        # Perform analysis
        result = ai_engine.analyze_section(section_name, content, doc_type)

        duration = time.time() - start_time
        feedback_count = len(result.get('feedback_items', []))

        print(f"✅ [Task {self.request.id}] Analysis complete: {feedback_count} items in {duration:.2f}s", flush=True)

        # Update state to success
        self.update_state(
            state='SUCCESS',
            meta={
                'status': 'Analysis complete',
                'section': section_name,
                'feedback_count': feedback_count,
                'duration': round(duration, 2),
                'result': result
            }
        )

        return {
            'success': True,
            'section': section_name,
            'feedback_count': feedback_count,
            'duration': round(duration, 2),
            'result': result
        }

    except Exception as e:
        error_msg = str(e)
        print(f"❌ [Task {self.request.id}] Analysis failed: {error_msg}", flush=True)

        # Update state to failure
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Analysis failed',
                'section': section_name,
                'error': error_msg
            }
        )

        # Check if it's a throttling error - if so, retry
        if 'throttling' in error_msg.lower() or 'too many requests' in error_msg.lower():
            print(f"⏳ [Task {self.request.id}] Throttling detected, will retry...", flush=True)
            raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds

        # For other errors, don't retry automatically
        return {
            'success': False,
            'section': section_name,
            'error': error_msg
        }


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name='celery_tasks.process_chat_task',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,  # Max 5 minutes
    retry_jitter=True,
    max_retries=3
)
def process_chat_task(self, query, context):
    """
    Asynchronous chat processing task

    Args:
        query: User's chat query
        context: Chat context (current section, feedback, etc.)

    Returns:
        dict: Chat response
    """
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Processing query...',
                'query': query[:50] + '...' if len(query) > 50 else query,
                'progress': 0
            }
        )

        print(f"💬 [Task {self.request.id}] Processing chat: {query[:50]}...", flush=True)
        start_time = time.time()

        # Process chat query
        response = ai_engine.process_chat_query(query, context)

        duration = time.time() - start_time

        print(f"✅ [Task {self.request.id}] Chat complete in {duration:.2f}s", flush=True)

        # Update state to success
        self.update_state(
            state='SUCCESS',
            meta={
                'status': 'Chat complete',
                'duration': round(duration, 2),
                'response': response
            }
        )

        return {
            'success': True,
            'response': response,
            'duration': round(duration, 2)
        }

    except Exception as e:
        error_msg = str(e)
        print(f"❌ [Task {self.request.id}] Chat failed: {error_msg}", flush=True)

        # Update state to failure
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Chat failed',
                'error': error_msg
            }
        )

        # Check if it's a throttling error
        if 'throttling' in error_msg.lower() or 'too many requests' in error_msg.lower():
            print(f"⏳ [Task {self.request.id}] Throttling detected, will retry...", flush=True)
            raise self.retry(exc=e, countdown=30)  # Retry after 30 seconds

        return {
            'success': False,
            'error': error_msg
        }


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name='celery_tasks.test_connection_task',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,  # Max 1 minute
    retry_jitter=True,
    max_retries=2
)
def test_connection_task(self):
    """
    Asynchronous connection test task

    Returns:
        dict: Connection test result
    """
    try:
        print(f"🔍 [Task {self.request.id}] Testing Claude connection...", flush=True)
        start_time = time.time()

        # Test connection
        result = ai_engine.test_connection()

        duration = time.time() - start_time

        print(f"✅ [Task {self.request.id}] Connection test complete in {duration:.2f}s", flush=True)

        return {
            'success': True,
            'result': result,
            'duration': round(duration, 2)
        }

    except Exception as e:
        error_msg = str(e)
        print(f"❌ [Task {self.request.id}] Connection test failed: {error_msg}", flush=True)

        # Throttling errors retry automatically
        if 'throttling' in error_msg.lower() or 'too many requests' in error_msg.lower():
            print(f"⏳ [Task {self.request.id}] Throttling detected, will retry...", flush=True)
            raise self.retry(exc=e, countdown=15)  # Retry after 15 seconds

        return {
            'success': False,
            'error': error_msg
        }


@celery_app.task(name='celery_tasks.cleanup_old_results')
def cleanup_old_results():
    """
    Periodic task to cleanup old task results
    Runs every hour via Celery Beat
    """
    print("🧹 Cleaning up old task results...")
    # Celery backend automatically expires results after 1 hour (configured in celery_config.py)
    # This is just a placeholder for any additional cleanup logic
    return {'cleaned': True}


# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-every-hour': {
        'task': 'celery_tasks.cleanup_old_results',
        'schedule': 3600.0,  # Every hour
    },
}
