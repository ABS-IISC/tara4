"""
Celery Configuration
Minimal stub for compatibility - actual task queue uses RQ
"""

from celery import Celery

# Create minimal Celery app for compatibility
celery_app = Celery('tara2')

# Basic configuration
celery_app.conf.update(
    broker_url='memory://',  # In-memory broker (won't actually work, but prevents errors)
    result_backend='cache+memory://',
    task_always_eager=True,  # Execute tasks synchronously
    task_eager_propagates=True
)
