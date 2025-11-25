"""
RQ (Redis Queue) Configuration for AI-Prism
100% Free & Open Source Task Queue

This replaces Celery + SQS + S3 with a much simpler Redis-based solution.
- No AWS costs
- No signature expiration issues
- No complex broker/backend configuration
- Results stored directly in Redis (no S3 polling needed)

Setup:
  Development: brew install redis && brew services start redis
  Production: docker run -d -p 6379:6379 redis:latest
"""

import os
from redis import Redis
from rq import Queue

# Redis Configuration
# Default: localhost:6379 (free, runs locally)
# Production: Set REDIS_URL environment variable
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Lazy initialization - connection created only when needed
_redis_conn = None
_queues_initialized = False
analysis_queue = None
chat_queue = None
monitoring_queue = None
default_queue = None

def get_redis_conn():
    """
    Get Redis connection (lazy initialization)
    Returns None if Redis is disabled or unavailable
    """
    global _redis_conn

    if _redis_conn is None:
        try:
            # Check if explicitly disabled
            if REDIS_URL in ('disabled', 'none', None, ''):
                return None

            # Try to create connection
            _redis_conn = Redis.from_url(REDIS_URL, decode_responses=False)
        except Exception as e:
            print(f"⚠️  Could not create Redis connection: {e}")
            return None

    return _redis_conn

def _initialize_queues():
    """Initialize RQ queues (called only once)"""
    global _queues_initialized, analysis_queue, chat_queue, monitoring_queue, default_queue

    if _queues_initialized:
        return

    conn = get_redis_conn()
    if conn is None:
        # Create dummy None queues
        analysis_queue = None
        chat_queue = None
        monitoring_queue = None
        default_queue = None
    else:
        # Create real queues
        analysis_queue = Queue('analysis', connection=conn, default_timeout=300)
        chat_queue = Queue('chat', connection=conn, default_timeout=120)
        monitoring_queue = Queue('monitoring', connection=conn, default_timeout=60)
        default_queue = Queue('default', connection=conn)

    _queues_initialized = True

def get_queue(queue_name='default'):
    """
    Get a queue by name

    Args:
        queue_name: One of 'analysis', 'chat', 'monitoring', 'default'

    Returns:
        RQ Queue instance or None if Redis unavailable
    """
    # Initialize queues on first access
    _initialize_queues()

    queues = {
        'analysis': analysis_queue,
        'chat': chat_queue,
        'monitoring': monitoring_queue,
        'default': default_queue
    }
    return queues.get(queue_name, default_queue)


def is_rq_available():
    """
    Check if Redis/RQ is available

    Returns:
        bool: True if Redis is running and accessible
    """
    try:
        conn = get_redis_conn()
        if conn is None:
            return False
        conn.ping()
        return True
    except Exception as e:
        print(f"⚠️  RQ not available: {e}")
        print(f"   Make sure Redis is running: brew services start redis")
        return False


# Print configuration on import
if __name__ != "__main__":
    try:
        if is_rq_available():
            print("✅ RQ configured with local Redis (No AWS costs!)")
            print(f"   Redis URL: {REDIS_URL}")
            print(f"   Queues: analysis, chat, monitoring, default")
            print(f"   Free & Open Source: 100%")
        else:
            print(f"⚠️  Redis not available (REDIS_URL={REDIS_URL})")
            print(f"   Running in synchronous mode")
    except Exception as e:
        print(f"⚠️  Could not connect to Redis: {e}")
        print(f"   Running in synchronous mode")
