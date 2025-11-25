"""
Gunicorn configuration for AI-Prism on Elastic Beanstalk
Optimized for AWS Bedrock Claude API calls
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # 2-4 workers on t3.medium
worker_class = "sync"  # Use 'sync' for Flask (not async)
worker_connections = 1000
max_requests = 1000  # Restart workers after 1000 requests (prevent memory leaks)
max_requests_jitter = 50
timeout = 300  # 5 minutes (for long Claude API calls)
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
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
