"""
Celery Integration Helper for Flask
Provides utilities for checking if Celery is available and handling fallback
"""
import os

# Check if Celery/Redis should be used
USE_CELERY = os.environ.get('USE_CELERY', 'false').lower() == 'true'

def is_celery_available():
    """Check if Celery with Redis is available and configured"""
    if not USE_CELERY:
        return False

    try:
        from celery_config import celery_app
        # Try to ping Redis
        celery_app.control.inspect().ping(timeout=1.0)
        return True
    except:
        return False


def submit_analysis_task(section_name, content, doc_type="Full Write-up", session_id=None):
    """
    Submit analysis task to Celery queue or execute directly

    Args:
        section_name: Section name
        content: Section content
        doc_type: Document type
        session_id: Optional session ID

    Returns:
        tuple: (task_id, is_async)
            - If Celery available: (task_id, True)
            - If Celery not available: (result, False)
    """
    if is_celery_available():
        from celery_tasks import analyze_section_task

        # Submit to Celery queue
        task = analyze_section_task.delay(section_name, content, doc_type, session_id)
        print(f"📤 Submitted analysis task {task.id} to queue", flush=True)
        return task.id, True
    else:
        # Execute directly (synchronous fallback)
        from core.ai_feedback_engine import AIFeedbackEngine
        ai_engine = AIFeedbackEngine()
        result = ai_engine.analyze_section(section_name, content, doc_type)
        return result, False


def submit_chat_task(query, context):
    """
    Submit chat task to Celery queue or execute directly

    Args:
        query: Chat query
        context: Chat context

    Returns:
        tuple: (task_id, is_async) or (result, False)
    """
    if is_celery_available():
        from celery_tasks import process_chat_task

        # Submit to Celery queue
        task = process_chat_task.delay(query, context)
        print(f"📤 Submitted chat task {task.id} to queue", flush=True)
        return task.id, True
    else:
        # Execute directly (synchronous fallback)
        from core.ai_feedback_engine import AIFeedbackEngine
        ai_engine = AIFeedbackEngine()
        result = ai_engine.process_chat_query(query, context)
        return result, False


def submit_test_task():
    """
    Submit connection test task to Celery queue or execute directly

    Returns:
        tuple: (task_id, is_async) or (result, False)
    """
    if is_celery_available():
        from celery_tasks import test_connection_task

        # Submit to Celery queue
        task = test_connection_task.delay()
        print(f"📤 Submitted test task {task.id} to queue", flush=True)
        return task.id, True
    else:
        # Execute directly (synchronous fallback)
        from core.ai_feedback_engine import AIFeedbackEngine
        ai_engine = AIFeedbackEngine()
        result = ai_engine.test_connection()
        return result, False


def get_task_status(task_id):
    """
    Get status of a Celery task

    Args:
        task_id: Task ID

    Returns:
        dict: Task status information
    """
    if not is_celery_available():
        return {
            'state': 'UNKNOWN',
            'error': 'Celery not available'
        }

    try:
        from celery_config import celery_app
        from celery.result import AsyncResult

        task = AsyncResult(task_id, app=celery_app)

        # Get task state
        state = task.state

        # Build status response
        status = {
            'task_id': task_id,
            'state': state,
            'ready': task.ready(),
            'successful': task.successful() if task.ready() else None,
            'failed': task.failed() if task.ready() else None
        }

        # Add task-specific info
        if state == 'PENDING':
            status['status'] = 'Task is waiting to be processed'
        elif state == 'PROGRESS':
            status['status'] = task.info.get('status', 'Processing...')
            status['progress'] = task.info.get('progress', 0)
            status.update(task.info)
        elif state == 'SUCCESS':
            status['status'] = 'Task completed successfully'
            status['result'] = task.result
        elif state == 'FAILURE':
            status['status'] = 'Task failed'
            status['error'] = str(task.info)
        elif state == 'RETRY':
            status['status'] = 'Task is being retried'
            status['error'] = str(task.info)

        return status

    except Exception as e:
        return {
            'task_id': task_id,
            'state': 'ERROR',
            'error': str(e)
        }


def get_queue_stats():
    """
    Get statistics about Celery queues

    Returns:
        dict: Queue statistics
    """
    if not is_celery_available():
        return {
            'available': False,
            'error': 'Celery not configured'
        }

    try:
        from celery_config import celery_app

        # Get worker stats
        inspect = celery_app.control.inspect()

        active = inspect.active()
        reserved = inspect.reserved()
        stats = inspect.stats()

        # Count tasks
        active_count = sum(len(tasks) for tasks in (active or {}).values())
        reserved_count = sum(len(tasks) for tasks in (reserved or {}).values())
        worker_count = len(stats or {})

        return {
            'available': True,
            'workers': worker_count,
            'active_tasks': active_count,
            'reserved_tasks': reserved_count,
            'total_pending': active_count + reserved_count,
            'worker_details': stats
        }

    except Exception as e:
        return {
            'available': False,
            'error': str(e)
        }
