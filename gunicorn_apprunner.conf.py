"""
Gunicorn configuration for AWS App Runner
Simplified config without filesystem logging
"""

import multiprocessing
import os

# Server socket - App Runner expects port 8080
bind = f"0.0.0.0:{os.environ.get('PORT', 8080)}"
backlog = 2048

# Worker processes - App Runner has 4 vCPU
workers = 4
worker_class = "sync"  # Sync workers for Flask
worker_connections = 1000
max_requests = 1000  # Restart workers after 1000 requests
max_requests_jitter = 50
timeout = 300  # 5 minutes for long AI API calls
graceful_timeout = 30
keepalive = 5

# Logging - output to stdout/stderr for App Runner
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "aiprism-apprunner"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

def when_ready(server):
    """Called when server is ready"""
    server.log.info("Gunicorn server ready on App Runner")
    server.log.info(f"Workers: {workers}, Port: {os.environ.get('PORT', 8080)}")
