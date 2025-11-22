"""
Celery Configuration for AI-Prism Task Queue
Handles document analysis and chat requests asynchronously
Uses Amazon SQS + S3 (No Redis required!)

IMPORTANT: This module uses lazy initialization to avoid errors when
environment variables aren't set (e.g., during imports or testing).
"""
import os
from celery import Celery

# Global celery app instance (lazy initialized)
_celery_app = None
_initialization_attempted = False
_initialization_error = None


def get_celery_config():
    """
    Get Celery configuration from environment variables

    Returns:
        dict: Configuration dictionary with all Celery settings
    """
    # AWS Configuration with multi-region support
    # Try multiple sources for region detection:
    # 1. AWS_REGION environment variable
    # 2. AWS_DEFAULT_REGION environment variable
    # 3. boto3 session default region
    # 4. Fallback to us-east-2
    aws_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')

    if not aws_region:
        # Try to detect from boto3
        try:
            import boto3
            session = boto3.Session()
            aws_region = session.region_name
            if aws_region:
                print(f"✅ Detected AWS region from boto3 session: {aws_region}")
        except Exception:
            pass

    if not aws_region:
        aws_region = 'us-east-2'
        print(f"⚠️  No AWS region detected, using default: {aws_region}")

    s3_bucket = os.environ.get('S3_BUCKET_NAME', 'felix-s3-bucket')
    s3_base_path = os.environ.get('S3_BASE_PATH', 'tara/')

    # Celery Broker: Amazon SQS (message queue)
    broker_url = os.environ.get('CELERY_BROKER_URL', 'sqs://')
    broker_transport_options = {
        'region': aws_region,
        'queue_name_prefix': os.environ.get('SQS_QUEUE_PREFIX', 'aiprism-'),
        'visibility_timeout': int(os.environ.get('SQS_VISIBILITY_TIMEOUT', '3600')),
        'polling_interval': int(os.environ.get('SQS_POLLING_INTERVAL', '1')),
        'wait_time_seconds': int(os.environ.get('SQS_WAIT_TIME_SECONDS', '1')),
    }

    # Celery Result Backend: Amazon S3 (task results storage)
    # Format: s3://bucket-name/path/to/results/
    result_backend_url = f's3://{s3_bucket}/{s3_base_path}celery-results/'
    result_backend = os.environ.get('CELERY_RESULT_BACKEND', result_backend_url)

    return {
        'broker_url': broker_url,
        'result_backend': result_backend,
        'aws_region': aws_region,
        's3_bucket': s3_bucket,
        'broker_transport_options': broker_transport_options,
        'task_serializer': 'json',
        'accept_content': ['json'],
        'result_serializer': 'json',
        'timezone': 'UTC',
        'enable_utc': True,
        'result_expires': 3600,
        'worker_prefetch_multiplier': 1,
        'worker_max_tasks_per_child': 50,
        'task_acks_late': True,
        'task_reject_on_worker_lost': True,
        'task_annotations': {
            'celery_tasks_enhanced.analyze_section_task': {
                'rate_limit': os.environ.get('ANALYSIS_TASK_RATE_LIMIT', '20/m'),
                'time_limit': int(os.environ.get('TASK_HARD_TIME_LIMIT', 360)),
                'soft_time_limit': int(os.environ.get('TASK_SOFT_TIME_LIMIT', 300))
            },
            'celery_tasks_enhanced.process_chat_task': {
                'rate_limit': os.environ.get('CHAT_TASK_RATE_LIMIT', '30/m'),
                'time_limit': 120,
                'soft_time_limit': 90
            },
            'celery_tasks_enhanced.monitor_health': {
                'rate_limit': os.environ.get('HEALTH_TASK_RATE_LIMIT', '1/m'),
                'time_limit': 60,
                'soft_time_limit': 45
            }
        },
        'task_routes': {
            'celery_tasks_enhanced.analyze_section_task': {'queue': 'analysis'},
            'celery_tasks_enhanced.process_chat_task': {'queue': 'chat'},
            'celery_tasks_enhanced.monitor_health': {'queue': 'monitoring'}
        },
        'task_default_retry_delay': 60,
        'task_max_retries': 3,
    }


def init_celery_app():
    """
    Initialize Celery app with lazy loading

    This function creates the Celery app only when first accessed,
    avoiding initialization errors when environment variables aren't set.

    Returns:
        Celery: Configured Celery application instance

    Raises:
        RuntimeError: If Celery configuration is invalid
    """
    global _celery_app, _initialization_attempted, _initialization_error

    if _celery_app is not None:
        return _celery_app

    if _initialization_attempted and _initialization_error:
        # Don't keep trying if we already failed
        raise _initialization_error

    _initialization_attempted = True

    try:
        # Get configuration
        config = get_celery_config()

        # Validate result backend URL format
        if not config['result_backend'].startswith('s3://'):
            raise ValueError(
                f"Invalid CELERY_RESULT_BACKEND format: {config['result_backend']}\n"
                f"Expected format: s3://bucket-name/path/to/results/\n"
                f"Example: s3://felix-s3-bucket/tara/celery-results/"
            )

        # Check if bucket name is present
        backend_parts = config['result_backend'].replace('s3://', '').split('/')
        if not backend_parts[0]:
            raise ValueError(
                f"Missing bucket name in CELERY_RESULT_BACKEND: {config['result_backend']}\n"
                f"Expected format: s3://bucket-name/path/to/results/\n"
                f"Example: s3://felix-s3-bucket/tara/celery-results/\n\n"
                f"To fix this, set environment variables:\n"
                f"  export S3_BUCKET_NAME=felix-s3-bucket\n"
                f"  export CELERY_RESULT_BACKEND=s3://felix-s3-bucket/tara/celery-results/\n\n"
                f"Or use the startup script: ./run_local.sh"
            )

        # Create Celery app
        _celery_app = Celery(
            'aiprism_tasks',
            broker=config['broker_url'],
            backend=config['result_backend'],
            include=['celery_tasks_enhanced']
        )

        # Update configuration
        _celery_app.conf.update(config)

        print("✅ Celery configured with Amazon SQS + S3 (No Redis required)")
        print(f"   Broker: Amazon SQS (region: {config['aws_region']})")
        print(f"   Backend: Amazon S3 (bucket: {config['s3_bucket']})")
        print(f"   Queue prefix: {config['broker_transport_options']['queue_name_prefix']}")
        print(f"   Enhanced mode: Enabled")

        return _celery_app

    except Exception as e:
        _initialization_error = RuntimeError(
            f"Failed to initialize Celery: {e}\n\n"
            f"Make sure environment variables are set:\n"
            f"  export S3_BUCKET_NAME=felix-s3-bucket\n"
            f"  export S3_BASE_PATH=tara/\n"
            f"  export AWS_REGION=us-east-2\n"
            f"  export CELERY_RESULT_BACKEND=s3://felix-s3-bucket/tara/celery-results/\n\n"
            f"Or use the startup script: ./run_local.sh"
        )
        raise _initialization_error


# Provide celery_app as a property that initializes on first access
class _CeleryAppProxy:
    """Proxy object that lazily initializes Celery app"""

    def __getattr__(self, name):
        app = init_celery_app()
        return getattr(app, name)

    def __call__(self, *args, **kwargs):
        app = init_celery_app()
        return app(*args, **kwargs)


# Export celery_app as lazy-loading proxy
celery_app = _CeleryAppProxy()


def is_celery_available():
    """
    Check if Celery is available and properly configured

    Returns:
        bool: True if Celery can be used, False otherwise
    """
    global _initialization_attempted, _initialization_error

    if _celery_app is not None:
        return True

    if _initialization_attempted and _initialization_error:
        return False

    try:
        init_celery_app()
        return True
    except Exception as e:
        print(f"⚠️  Celery not available: {e}")
        return False
