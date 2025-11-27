"""
Gunicorn configuration for AI-Prism on Elastic Beanstalk
Optimized for 100+ concurrent users with AWS Bedrock Claude API calls
"""

import multiprocessing
import os

# Server socket - Use PORT environment variable from Elastic Beanstalk
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 4096  # Increased from 2048 for high concurrency

# Worker processes - OPTIMIZED FOR 100+ USERS
# t3.large has 2 vCPUs, 8 GB RAM
# Formula: (2 * CPU cores) + 1 = 5 workers per instance
# With 3 instances minimum = 15 workers handling 100+ users
workers = (multiprocessing.cpu_count() * 2) + 1  # 5 workers on t3.large
worker_class = "gevent"  # Changed to gevent for better concurrency
worker_connections = 2000  # Increased from 1000 for more concurrent connections
max_requests = 2000  # Restart workers after 2000 requests
max_requests_jitter = 100
timeout = 600  # 10 minutes (for long Claude API calls - doubled from 5min)
graceful_timeout = 60  # Increased for clean shutdowns
keepalive = 10  # Increased keepalive

# Logging - Use stdout/stderr for Elastic Beanstalk log capture
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "aiprism-flask"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (handled by ALB)
# No SSL configuration needed - ALB terminates SSL

def post_fork(server, worker):
    """Called after worker is forked"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Called before worker is forked"""
    pass

def pre_exec(server):
    """Called before exec"""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Called when server is ready"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called when worker receives SIGINT or SIGQUIT"""
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when worker receives SIGABRT"""
    worker.log.info("Worker received SIGABRT signal")
