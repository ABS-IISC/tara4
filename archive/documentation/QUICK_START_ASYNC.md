# Quick Start: Async AI-Prism Setup

## 🚀 5-Minute Setup Guide

### Prerequisites
- Python 3.8+
- AWS credentials configured
- Redis server (or Docker)

---

## Step 1: Install Dependencies (1 minute)

```bash
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2

# Install required packages
pip install redis celery[redis] boto3 botocore
```

---

## Step 2: Start Redis (1 minute)

### Option A: Docker (Recommended)
```bash
docker run -d --name aiprism-redis \
  -p 6379:6379 \
  redis:latest
```

### Option B: Local Redis
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Verify
redis-cli ping
# Should return: PONG
```

---

## Step 3: Configure Environment (1 minute)

Create `.env` file:
```bash
cat > .env << 'EOF'
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
USE_CELERY=true

# AWS Configuration
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0

# Fallback Models (comma-separated)
BEDROCK_FALLBACK_MODELS=anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-sonnet-20240229-v1:0,anthropic.claude-3-haiku-20240307-v1:0

# AWS Credentials (if not using IAM role)
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key

# Rate Limiting (optional - defaults shown)
# MAX_REQUESTS_PER_MINUTE=30
# MAX_CONCURRENT_REQUESTS=5
# MAX_TOKENS_PER_MINUTE=120000
EOF

# Load environment variables
export $(cat .env | xargs)
```

---

## Step 4: Start Celery Workers (1 minute)

### Terminal 1: Start Worker
```bash
celery -A celery_config worker \
  --loglevel=info \
  --concurrency=4 \
  --pool=threads

# You should see:
# ✅ Redis connected for distributed rate limiting
# ✅ AsyncRequestManager initialized
# [tasks]
#   . celery_tasks_enhanced.analyze_section_task
#   . celery_tasks_enhanced.process_chat_task
#   . celery_tasks_enhanced.monitor_health
```

### Terminal 2: Start Beat Scheduler
```bash
celery -A celery_config beat --loglevel=info

# You should see:
# Scheduler: Running...
# beat: Starting...
```

### Terminal 3: Start Flask App
```bash
python app.py

# You should see:
# ✅ Request Manager initialized
# * Running on http://127.0.0.1:5000
```

---

## Step 5: Verify Setup (1 minute)

### Test 1: Check Redis Connection
```bash
redis-cli ping
# Expected: PONG
```

### Test 2: Check Celery Workers
```bash
celery -A celery_config inspect active
# Expected: JSON with worker info
```

### Test 3: Test API Endpoint
```bash
curl http://localhost:5000/health
# Expected: {"status": "healthy"}
```

### Test 4: Check Rate Limiting
```bash
curl http://localhost:5000/model_stats
# Expected: JSON with rate limit stats
```

---

## 🎯 Usage Examples

### Example 1: Analyze Section (Async)

```python
import requests

# Submit analysis task
response = requests.post('http://localhost:5000/analyze_section', json={
    'session_id': 'test-session-123',
    'section_name': 'Executive Summary',
    'content': 'This investigation examined...',
    'doc_type': 'Investigation Report'
})

task_data = response.json()
task_id = task_data['task_id']
print(f"Task submitted: {task_id}")

# Poll for results
import time
while True:
    status_response = requests.get(f'http://localhost:5000/task_status/{task_id}')
    status = status_response.json()

    print(f"Status: {status['state']}")

    if status['ready']:
        if status['successful']:
            print(f"✅ Analysis complete!")
            print(f"Feedback items: {len(status['result']['feedback_items'])}")
            break
        else:
            print(f"❌ Error: {status['error']}")
            break

    time.sleep(2)
```

### Example 2: Monitor System Health

```python
import requests

response = requests.get('http://localhost:5000/model_stats')
stats = response.json()

print(f"Total Requests: {stats['total_requests']}")
print(f"Success Rate: {stats['successful_requests'] / stats['total_requests'] * 100:.1f}%")
print(f"Active Requests: {stats['active_requests']}")
print(f"Rate Limit: {stats['requests_last_minute']}/30 requests/min")
print(f"Token Usage: {stats['tokens_last_minute']}/120000 tokens/min")

# Check model health
for model_id, health in stats['model_health'].items():
    print(f"\n{model_id}:")
    print(f"  Status: {health['status']}")
    print(f"  Success Rate: {health['successful_requests']}/{health['total_requests']}")
```

### Example 3: Test TOON Serialization

```python
from core.toon_serializer import to_toon, from_toon, toon_savings

data = {
    'feedback': 'Timeline missing timestamps',
    'risk_level': 'High',
    'confidence': 0.92
}

# Serialize
toon_str = to_toon(data)
print(f"TOON: {toon_str}")

# Calculate savings
savings = toon_savings(data)
print(f"Token savings: {savings['savings_percent']}%")
```

---

## 🔍 Monitoring

### Option 1: Flower Dashboard (Recommended)
```bash
# Terminal 4
celery -A celery_config flower --port=5555

# Open browser
open http://localhost:5555

# Features:
# - Real-time task monitoring
# - Worker status
# - Task history
# - Performance graphs
```

### Option 2: Redis CLI
```bash
redis-cli monitor
# Watch all Redis commands in real-time
```

### Option 3: Celery Events
```bash
celery -A celery_config events
# Watch all Celery events in real-time
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused" for Redis
**Solution**:
```bash
# Check if Redis is running
redis-cli ping

# If not running, start it
docker start aiprism-redis
# OR
brew services start redis
```

### Issue: "No tasks registered"
**Solution**:
```bash
# Ensure celery_tasks_enhanced.py is in the include list
# Check celery_config.py:
# include=['celery_tasks_enhanced']

# Restart worker
celery -A celery_config worker --loglevel=info
```

### Issue: Tasks fail with "AWS credentials not found"
**Solution**:
```bash
# Option 1: Configure AWS CLI
aws configure

# Option 2: Set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Option 3: Use IAM role (for EC2/ECS)
# Already configured automatically
```

### Issue: "ThrottlingException" still occurring
**Solution**:
```bash
# Reduce rate limits in async_request_manager.py
# Line 23-26:
MAX_REQUESTS_PER_MINUTE = 20  # Lower from 30
MAX_CONCURRENT_REQUESTS = 3   # Lower from 5

# Restart workers
```

### Issue: High token usage
**Solution**:
```python
# Use TOON serialization more aggressively
# In bedrock_prompt_templates.py, enable TOON for all context
framework_toon = to_toon(framework_checkpoints, use_abbrev=True)

# Truncate content more aggressively
content = content[:5000]  # Lower from 7500
```

---

## 📊 Performance Tuning

### For High Throughput
```python
# celery_config.py
celery_app.conf.update(
    worker_concurrency=8,           # More workers
    worker_prefetch_multiplier=2,   # Fetch 2 tasks per worker
)

# async_request_manager.py
MAX_CONCURRENT_REQUESTS = 10        # More concurrent calls
MAX_REQUESTS_PER_MINUTE = 50        # Higher rate limit
```

### For Cost Optimization
```bash
# Use Haiku by default (cheaper, faster)
export BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Reduce max tokens
export BEDROCK_MAX_TOKENS=4096
```

### For Stability (Recommended)
```python
# Conservative settings (current defaults)
MAX_REQUESTS_PER_MINUTE = 30
MAX_CONCURRENT_REQUESTS = 5
MAX_TOKENS_PER_MINUTE = 120000
THROTTLE_COOLDOWN_SECONDS = 60
```

---

## 🔄 Production Deployment

### Using Systemd (Linux)

Create `/etc/systemd/system/celery-aiprism.service`:
```ini
[Unit]
Description=AI-Prism Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/aiprism
EnvironmentFile=/opt/aiprism/.env
ExecStart=/usr/local/bin/celery -A celery_config worker \
  --loglevel=info \
  --concurrency=4 \
  --pidfile=/var/run/celery-aiprism.pid \
  --logfile=/var/log/celery-aiprism.log
ExecStop=/usr/local/bin/celery -A celery_config control shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable celery-aiprism
sudo systemctl start celery-aiprism
sudo systemctl status celery-aiprism
```

### Using Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  celery-worker:
    build: .
    command: celery -A celery_config worker --loglevel=info --concurrency=4
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
      - USE_CELERY=true
      - AWS_REGION=us-east-1
    volumes:
      - .:/app

  celery-beat:
    build: .
    command: celery -A celery_config beat --loglevel=info
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0

  flower:
    build: .
    command: celery -A celery_config flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0

volumes:
  redis-data:
```

Start services:
```bash
docker-compose up -d
```

---

## ✅ Success Checklist

After setup, verify:

- [ ] Redis is running and accessible
- [ ] Celery worker shows "ready" status
- [ ] Celery beat scheduler is running
- [ ] Flask app is running on port 5000
- [ ] `/health` endpoint returns healthy status
- [ ] `/model_stats` endpoint shows rate limit stats
- [ ] Test analysis task completes successfully
- [ ] Flower dashboard is accessible (optional)
- [ ] Logs show no errors
- [ ] Multi-model fallback is working (test by lowering rate limits)

---

## 🎉 You're Ready!

Your AI-Prism system is now configured with:
- ✅ Asynchronous processing
- ✅ Multi-model fallback
- ✅ Comprehensive throttling protection
- ✅ Token-optimized serialization
- ✅ AWS Bedrock best practices
- ✅ Production-ready monitoring

Next steps:
1. Review [ASYNC_IMPROVEMENTS_README.md](ASYNC_IMPROVEMENTS_README.md) for detailed documentation
2. Monitor system performance using Flower dashboard
3. Tune rate limits based on your AWS quotas
4. Set up alerts for throttling rates
5. Configure production deployment (systemd/Docker)

**Questions?** Check the troubleshooting section or review logs.
