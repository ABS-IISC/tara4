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

# Create Redis connection
redis_conn = Redis.from_url(REDIS_URL, decode_responses=False)

# Create task queues
# Separate queues for different task types (optional, but organized)
analysis_queue = Queue('analysis', connection=redis_conn, default_timeout=300)  # 5 min timeout
chat_queue = Queue('chat', connection=redis_conn, default_timeout=120)  # 2 min timeout
monitoring_queue = Queue('monitoring', connection=redis_conn, default_timeout=60)  # 1 min timeout

# Default queue for generic tasks
default_queue = Queue('default', connection=redis_conn)

def get_queue(queue_name='default'):
    """
    Get a queue by name

    Args:
        queue_name: One of 'analysis', 'chat', 'monitoring', 'default'

    Returns:
        RQ Queue instance
    """
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
        redis_conn.ping()
        return True
    except Exception as e:
        print(f"⚠️  RQ not available: {e}")
        print(f"   Make sure Redis is running: brew services start redis")
        return False


# Print configuration on import
if __name__ != "__main__":
    try:
        redis_conn.ping()
        print("✅ RQ configured with local Redis (No AWS costs!)")
        print(f"   Redis URL: {REDIS_URL}")
        print(f"   Queues: analysis, chat, monitoring, default")
        print(f"   Free & Open Source: 100%")
    except Exception as e:
        print(f"⚠️  Could not connect to Redis: {e}")
        print(f"   Start Redis: brew services start redis")
