"""
Celery Configuration for AI-Prism Task Queue
Handles document analysis and chat requests asynchronously
"""
import os
from celery import Celery

# Get Redis URL from environment or use default
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app with enhanced tasks
celery_app = Celery(
    'aiprism_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['celery_tasks_enhanced']  # ✅ UPDATED: Using enhanced tasks with multi-model fallback
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
        'celery_tasks_enhanced.analyze_section_task': {  # ✅ UPDATED
            'rate_limit': '10/m',  # Max 10 analysis tasks per minute (increased with multi-model)
            'time_limit': 300,     # 5 minute timeout
            'soft_time_limit': 240  # Soft timeout at 4 minutes
        },
        'celery_tasks_enhanced.process_chat_task': {  # ✅ UPDATED
            'rate_limit': '15/m',  # Max 15 chat tasks per minute (increased)
            'time_limit': 120,      # 2 minute timeout
            'soft_time_limit': 90   # Soft timeout at 90 seconds
        },
        'celery_tasks_enhanced.monitor_health': {  # ✅ NEW: Health monitoring
            'rate_limit': '1/m',   # Once per minute
            'time_limit': 60,
            'soft_time_limit': 45
        }
    },

    # Queue settings
    task_routes={
        'celery_tasks_enhanced.analyze_section_task': {'queue': 'analysis'},  # ✅ UPDATED
        'celery_tasks_enhanced.process_chat_task': {'queue': 'chat'},  # ✅ UPDATED
        'celery_tasks_enhanced.monitor_health': {'queue': 'monitoring'}  # ✅ NEW
    },

    # Retry settings
    task_default_retry_delay=60,  # Wait 60 seconds before retry
    task_max_retries=3,  # Max 3 retries for failed tasks
)

# Optional: Monitoring with Flower
# Run: celery -A celery_config flower --port=5555
