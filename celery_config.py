"""
Celery Configuration for AI-Prism Task Queue
Handles document analysis and chat requests asynchronously
"""
import os
from celery import Celery

# Get Redis URL from environment or use default
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'aiprism_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['celery_tasks']
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={'master_name': 'mymaster'},

    # Worker settings
    worker_prefetch_multiplier=1,  # Only fetch 1 task at a time (prevents overload)
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (memory management)

    # Task execution settings
    task_acks_late=True,  # Acknowledge task after completion (not before)
    task_reject_on_worker_lost=True,  # Reject if worker dies

    # Rate limiting (KEY FEATURE for throttling!)
    task_annotations={
        'celery_tasks.analyze_section_task': {
            'rate_limit': '5/m',  # Max 5 analysis tasks per minute
            'time_limit': 300,     # 5 minute timeout
            'soft_time_limit': 240  # Soft timeout at 4 minutes
        },
        'celery_tasks.process_chat_task': {
            'rate_limit': '10/m',  # Max 10 chat tasks per minute
            'time_limit': 120,      # 2 minute timeout
            'soft_time_limit': 90   # Soft timeout at 90 seconds
        },
        'celery_tasks.test_connection_task': {
            'rate_limit': '3/m',  # Max 3 test tasks per minute
            'time_limit': 30,      # 30 second timeout
            'soft_time_limit': 20  # Soft timeout at 20 seconds
        }
    },

    # Queue settings
    task_routes={
        'celery_tasks.analyze_section_task': {'queue': 'analysis'},
        'celery_tasks.process_chat_task': {'queue': 'chat'},
        'celery_tasks.test_connection_task': {'queue': 'test'}
    },

    # Retry settings
    task_default_retry_delay=60,  # Wait 60 seconds before retry
    task_max_retries=3,  # Max 3 retries for failed tasks
)

# Optional: Monitoring with Flower
# Run: celery -A celery_config flower --port=5555
