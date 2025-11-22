"""
Task Functions for ThreadPoolExecutor

These functions replace Celery tasks with simple synchronous functions
that can be executed in thread pools.
"""

from typing import Dict, Any
from core.ai_feedback_engine import AIFeedbackEngine
import time


def analyze_section_sync(section_name: str, content: str, doc_type: str = "Full Write-up", session_id: str = None) -> Dict[str, Any]:
    """
    Synchronous section analysis (replaces Celery task)

    Args:
        section_name: Section name
        content: Section content
        doc_type: Document type
        session_id: Session ID for tracking

    Returns:
        Analysis result with feedback items
    """
    start_time = time.time()

    try:
        print(f"📝 [Thread] Analyzing: {section_name}")

        # Create AI engine
        ai_engine = AIFeedbackEngine(session_id=session_id)

        # Run analysis (synchronous)
        result = ai_engine.analyze_section(
            section_name=section_name,
            content=content,
            doc_type=doc_type
        )

        duration = time.time() - start_time

        # Extract feedback items
        feedback_items = result.get('feedback_items', [])

        print(f"✅ [Thread] Analysis complete: {len(feedback_items)} items ({duration:.2f}s)")

        return {
            'success': True,
            'feedback_items': feedback_items,
            'section': section_name,
            'duration': round(duration, 2),
            'feedback_count': len(feedback_items)
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ [Thread] Analysis error: {str(e)}")

        return {
            'success': False,
            'error': str(e),
            'section': section_name,
            'duration': round(duration, 2)
        }


def process_chat_sync(query: str, context: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
    """
    Synchronous chat processing (replaces Celery task)

    Args:
        query: User query
        context: Chat context
        session_id: Session ID for tracking

    Returns:
        Chat response
    """
    start_time = time.time()

    try:
        print(f"💬 [Thread] Processing chat: {query[:50]}...")

        # Create AI engine
        ai_engine = AIFeedbackEngine(session_id=session_id)

        # Process chat (synchronous)
        response = ai_engine.process_chat_query(query, context)

        duration = time.time() - start_time

        print(f"✅ [Thread] Chat complete ({duration:.2f}s)")

        return {
            'success': True,
            'response': response,
            'duration': round(duration, 2)
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ [Thread] Chat error: {str(e)}")

        return {
            'success': False,
            'error': str(e),
            'duration': round(duration, 2)
        }


def health_check_sync() -> Dict[str, Any]:
    """
    System health check (replaces Celery monitor task)

    Returns:
        Health status
    """
    from utils.thread_pool_manager import get_task_manager

    try:
        task_manager = get_task_manager()
        stats = task_manager.get_stats()

        return {
            'status': 'healthy',
            'task_stats': stats,
            'timestamp': time.time()
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }
