#!/usr/bin/env python3
"""
AI-Prism Main Entry Point
Single file to start everything - Flask + Celery Worker
Works on both local development and App Runner
"""

import os
import sys
import subprocess
import signal

# Set default environment variables BEFORE any imports
os.environ.setdefault('S3_BUCKET_NAME', 'felix-s3-bucket')
os.environ.setdefault('S3_BASE_PATH', 'tara/')
os.environ.setdefault('AWS_REGION', 'us-east-1')
os.environ.setdefault('CELERY_RESULT_BACKEND', 's3://felix-s3-bucket/tara/celery-results/')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('PORT', '8080')
os.environ.setdefault('CELERY_BROKER_URL', 'sqs://')
os.environ.setdefault('SQS_QUEUE_PREFIX', 'aiprism-')

def start_celery_worker():
    """Start Celery worker as subprocess"""
    print("🔧 Starting Celery worker in background...")
    sys.stdout.flush()

    try:
        import subprocess

        # Build celery command
        celery_cmd = [
            'celery',
            '-A', 'celery_config.celery_app',
            'worker',
            '--loglevel=INFO',
            '--concurrency=4',
            '--queues=analysis,chat,monitoring,celery',
            '--pool=solo',
            '--without-gossip',
            '--without-mingle',
            '--without-heartbeat',
        ]

        # Start Celery worker as subprocess
        # Pass current environment to subprocess
        env = os.environ.copy()

        celery_process = subprocess.Popen(
            celery_cmd,
            env=env,
            # Don't capture output - let it print to console for debugging
            stdout=None,
            stderr=None
        )

        print(f"✅ Celery worker started (PID: {celery_process.pid})")
        sys.stdout.flush()

        return celery_process

    except Exception as e:
        print(f"⚠️  Celery worker error: {e}")
        import traceback
        traceback.print_exc()
        return None

def start_flask_app():
    """Start Flask app"""
    print("🚀 Starting Flask application...")
    sys.stdout.flush()

    # Import Flask app
    from app import app as flask_app

    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV', 'development') != 'production'

    print(f"   Listening on http://0.0.0.0:{port}")
    print()
    sys.stdout.flush()

    # Start Flask (this blocks)
    flask_app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=False,  # Important: disable reloader
        threaded=True
    )

def main():
    """Main entry point"""
    print("=" * 60)
    print("AI-Prism Document Analysis Platform")
    print("=" * 60)
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Port: {os.environ.get('PORT', 8080)}")
    print(f"AWS Region: {os.environ.get('AWS_REGION', 'us-east-1')}")
    print(f"S3 Bucket: {os.environ.get('S3_BUCKET_NAME', 'felix-s3-bucket')}")
    print(f"Celery Backend: {os.environ.get('CELERY_RESULT_BACKEND', 's3://...')}")
    print("=" * 60)
    print()

    celery_process = None

    try:
        # Check if we're on App Runner or similar managed environment
        is_managed_env = os.environ.get('AWS_EXECUTION_ENV', '').startswith('AWS_ECS_')

        if not is_managed_env:
            # Local development - start Celery worker as subprocess
            celery_process = start_celery_worker()

            # Give Celery a moment to start
            import time
            time.sleep(3)
        else:
            print("ℹ️  Running in managed environment (App Runner)")
            print("   Celery worker should be running separately")
            print()

        # Start Flask app (blocks until shutdown)
        start_flask_app()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if celery_process:
            print(f"   Stopping Celery worker (PID: {celery_process.pid})")
            celery_process.terminate()
            celery_process.wait(timeout=5)
        print("✅ Cleanup complete")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        if celery_process:
            celery_process.terminate()
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
