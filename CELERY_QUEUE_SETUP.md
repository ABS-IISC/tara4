# 🚀 Celery Task Queue Setup - Professional Async Processing

**Date:** November 17, 2025
**Purpose:** Replace synchronous API calls with async task queue for better throttling management

---

## 🎯 Why Celery?

### Problems with Current Synchronous Approach:
1. **Concurrent requests hit rate limits** - Multiple users → multiple simultaneous API calls
2. **Browser timeouts** - Long-running analysis blocks HTTP request
3. **No request queuing** - All requests try to execute immediately
4. **Poor scalability** - Can't handle multiple concurrent users

### Benefits of Celery Task Queue:
1. ✅ **Automatic rate limiting** - Control max requests per minute
2. ✅ **Request queuing** - Requests wait in line, no thundering herd
3. ✅ **Async processing** - Browser doesn't block, poll for results
4. ✅ **Better scalability** - Handle 100+ concurrent users
5. ✅ **Retry management** - Automatic exponential backoff built-in
6. ✅ **Monitoring** - See queue status, active tasks, workers
7. ✅ **Load balancing** - Distribute tasks across multiple workers

---

## 📋 Architecture

### Current (Synchronous):
```
Browser → Flask → Claude API → Wait... → Response → Browser
         (blocks for 5-10 seconds)
```

**Problem:** If 10 users click "Analyze" at the same time → 10 simultaneous Claude API calls → Throttling!

---

### New (Asynchronous with Celery):
```
Browser → Flask → Redis Queue → Celery Worker → Claude API
    ↓                                ↓
Gets task_id                   Processes 1 at a time
    ↓
Poll /task_status/{task_id}
    ↓
Get results when ready
```

**Benefit:** 10 users → 10 tasks in queue → Celery processes 1-5 at a time → No throttling!

---

## 🔧 Components

### 1. Redis (Message Broker & Result Backend)
- **Purpose:** Stores task queue and results
- **Why Redis:** Fast, reliable, widely used
- **Alternative:** RabbitMQ (more complex, not needed here)

### 2. Celery (Task Queue System)
- **Purpose:** Manages async task execution
- **Features:**
  - Rate limiting (5 analysis tasks/minute)
  - Automatic retries with exponential backoff
  - Task prioritization
  - Monitoring and statistics

### 3. Celery Workers (Background Processors)
- **Purpose:** Execute tasks from queue
- **Scalable:** Run 1-10 workers based on load
- **Isolation:** Each worker has own AI engine instance

---

## 📦 Installation

### Requirements

Add to `requirements.txt`:
```txt
celery[redis]==5.3.4
redis==5.0.1
```

### AWS App Runner Setup

You'll need **Redis** running. Options:

#### Option 1: AWS ElastiCache Redis (Recommended for Production)
```bash
# In AWS Console:
1. Go to ElastiCache
2. Create Redis cluster
3. Choose instance type (cache.t3.micro for testing)
4. Note the endpoint URL
5. Set environment variable in App Runner:
   REDIS_URL=redis://your-redis-endpoint:6379/0
```

**Cost:** ~$15/month for t3.micro

#### Option 2: Redis Container (For Testing)
```yaml
# In apprunner.yaml, add Redis sidecar
# (App Runner doesn't support this - need ECS/EKS instead)
```

#### Option 3: External Redis (Quick Testing)
```bash
# Use Redis Labs free tier or Upstash
REDIS_URL=redis://:password@redis-endpoint:6379/0
```

---

## 🚀 Usage

### Enable Celery

Set environment variable in AWS App Runner:
```bash
USE_CELERY=true
REDIS_URL=redis://your-redis-endpoint:6379/0
```

### Start Celery Worker

**In App Runner, add startup command:**

**Option A: Single process (simple, for testing):**
```dockerfile
# In Dockerfile or start script:
CMD python main.py & celery -A celery_config worker --loglevel=info --concurrency=2
```

**Option B: Separate worker container (production):**
```dockerfile
# Worker Dockerfile:
CMD celery -A celery_config worker --loglevel=info --concurrency=4 --max-tasks-per-child=50
```

**Worker Options:**
- `--concurrency=N` - Number of worker threads (2-4 recommended)
- `--max-tasks-per-child=50` - Restart worker after 50 tasks (memory management)
- `--queues=analysis,chat,test` - Process specific queues

---

## 🔧 Configuration

### Rate Limits (Key Feature!)

In `celery_config.py`:
```python
task_annotations={
    'celery_tasks.analyze_section_task': {
        'rate_limit': '5/m',  # Max 5 analysis per minute
    },
    'celery_tasks.process_chat_task': {
        'rate_limit': '10/m',  # Max 10 chats per minute
    },
}
```

**This prevents throttling!** Even if 100 users submit requests, Celery will only execute 5/minute.

### Queue Priorities

```python
task_routes={
    'celery_tasks.analyze_section_task': {'queue': 'analysis'},
    'celery_tasks.process_chat_task': {'queue': 'chat'},
    'celery_tasks.test_connection_task': {'queue': 'test'}
}
```

**Benefit:** Can prioritize chat over analysis, or vice versa.

### Retry Configuration

```python
@celery_app.task(
    autoretry_for=(Exception,),  # Auto-retry on errors
    retry_backoff=True,          # Exponential backoff
    retry_backoff_max=600,       # Max 10 minutes
    retry_jitter=True,           # Add randomness
    max_retries=3                # Try up to 3 times
)
```

---

## 📡 API Changes

### Analyze Section (Async)

**Old (Synchronous):**
```python
@app.route('/analyze_section', methods=['POST'])
def analyze_section():
    result = ai_engine.analyze_section(section, content)
    return jsonify(result)  # Wait 5-10 seconds
```

**New (Asynchronous):**
```python
@app.route('/analyze_section', methods=['POST'])
def analyze_section():
    task_id, is_async = submit_analysis_task(section, content)

    if is_async:
        # Return task ID immediately
        return jsonify({
            'task_id': task_id,
            'status': 'processing',
            'message': 'Task submitted to queue'
        })
    else:
        # Celery not available, return result directly
        return jsonify(task_id)  # task_id is actually the result
```

**Frontend polls:**
```javascript
// Poll every 2 seconds
const checkStatus = setInterval(async () => {
    const response = await fetch(`/task_status/${task_id}`);
    const data = await response.json();

    if (data.state === 'SUCCESS') {
        clearInterval(checkStatus);
        displayFeedback(data.result);
    }
}, 2000);
```

---

### New Endpoints

#### 1. Check Task Status
```python
@app.route('/task_status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    status = get_task_status(task_id)
    return jsonify(status)
```

**Response:**
```json
{
    "task_id": "abc-123-def",
    "state": "PROGRESS",
    "status": "Analyzing section...",
    "progress": 50
}
```

**States:**
- `PENDING` - Task waiting in queue
- `PROGRESS` - Task is being processed
- `SUCCESS` - Task completed
- `FAILURE` - Task failed
- `RETRY` - Task is being retried

#### 2. Queue Statistics
```python
@app.route('/queue_stats', methods=['GET'])
def queue_stats():
    stats = get_queue_stats()
    return jsonify(stats)
```

**Response:**
```json
{
    "available": true,
    "workers": 2,
    "active_tasks": 3,
    "reserved_tasks": 7,
    "total_pending": 10
}
```

#### 3. Cancel Task
```python
@app.route('/cancel_task/<task_id>', methods=['POST'])
def cancel_task(task_id):
    from celery_config import celery_app
    celery_app.control.revoke(task_id, terminate=True)
    return jsonify({'cancelled': True})
```

---

## 🖥️ Frontend Changes

### Old (Synchronous):
```javascript
async function analyzeSection(section) {
    showLoading();
    const response = await fetch('/analyze_section', {
        method: 'POST',
        body: JSON.stringify({section, content})
    });
    const result = await response.json();  // Waits 5-10 seconds
    displayFeedback(result);
    hideLoading();
}
```

### New (Asynchronous):
```javascript
async function analyzeSection(section) {
    showLoading();

    // Submit task
    const response = await fetch('/analyze_section', {
        method: 'POST',
        body: JSON.stringify({section, content})
    });
    const data = await response.json();  // Returns immediately

    if (data.task_id) {
        // Poll for results
        pollTaskStatus(data.task_id);
    } else {
        // Celery not available, got result directly
        displayFeedback(data);
        hideLoading();
    }
}

async function pollTaskStatus(taskId) {
    const checkStatus = setInterval(async () => {
        const response = await fetch(`/task_status/${taskId}`);
        const data = await response.json();

        // Update progress bar
        if (data.progress) {
            updateProgress(data.progress);
        }

        // Check if complete
        if (data.state === 'SUCCESS') {
            clearInterval(checkStatus);
            displayFeedback(data.result.result);
            hideLoading();
        } else if (data.state === 'FAILURE') {
            clearInterval(checkStatus);
            showError(data.error);
            hideLoading();
        }
    }, 2000);  // Poll every 2 seconds
}
```

---

## 📊 Monitoring

### Celery Flower (Web Dashboard)

**Install:**
```bash
pip install flower
```

**Run:**
```bash
celery -A celery_config flower --port=5555
```

**Access:** http://localhost:5555

**Features:**
- See all tasks (pending, active, completed, failed)
- Monitor worker status
- View task details and results
- Cancel running tasks
- See queue statistics
- Performance graphs

---

## 🧪 Testing

### Test Without Redis (Fallback Mode)

```bash
# Don't set USE_CELERY or REDIS_URL
python main.py
```

**Behavior:** Tasks execute synchronously (same as before), no Redis needed.

### Test With Redis (Async Mode)

```bash
# Terminal 1: Start Redis (if local)
redis-server

# Terminal 2: Start Celery Worker
celery -A celery_config worker --loglevel=info

# Terminal 3: Start Flask App
USE_CELERY=true REDIS_URL=redis://localhost:6379/0 python main.py
```

**Test:**
1. Upload document
2. Click "Analyze"
3. Should return task_id immediately
4. Poll `/task_status/{task_id}` to see progress
5. Results appear when complete

---

## 🚀 Deployment Options

### Option 1: App Runner + ElastiCache (Recommended)

**Architecture:**
```
App Runner (Flask + Celery Worker) ← → ElastiCache Redis
```

**Setup:**
1. Create ElastiCache Redis cluster
2. Set security group to allow App Runner access
3. Set environment variables:
   ```
   USE_CELERY=true
   REDIS_URL=redis://redis-endpoint:6379/0
   ```
4. Update start command:
   ```dockerfile
   CMD python main.py & celery -A celery_config worker --loglevel=info --concurrency=2
   ```

**Pros:** Simple, single service
**Cons:** Worker and Flask in same container (not ideal for high load)

---

### Option 2: App Runner (Flask) + ECS (Workers) + ElastiCache

**Architecture:**
```
App Runner (Flask)  ← → ElastiCache Redis ← → ECS (Celery Workers)
     ↓
  Submits tasks                            ↑
                                     Processes tasks
```

**Setup:**
1. Deploy Flask app to App Runner (no worker)
2. Deploy separate Celery worker to ECS
3. Both connect to same Redis
4. Workers auto-scale based on queue size

**Pros:** Scalable, workers separate from web
**Cons:** More complex, need ECS

---

### Option 3: Full ECS/EKS (Production-Grade)

**Architecture:**
```
Load Balancer
    ↓
ECS Flask Tasks (3 replicas)
    ↓
ElastiCache Redis
    ↑
ECS Celery Worker Tasks (5 replicas, auto-scaling)
```

**Pros:** Highly scalable, production-ready
**Cons:** Most complex, higher cost

---

## 💰 Cost Comparison

### Without Celery (Current):
- App Runner: ~$25/month
- **Total:** $25/month

### With Celery (Option 1):
- App Runner: ~$25/month
- ElastiCache Redis (t3.micro): ~$15/month
- **Total:** $40/month (+$15)

### With Celery (Option 2):
- App Runner: ~$25/month
- ElastiCache Redis (t3.micro): ~$15/month
- ECS Fargate Workers (0.25 vCPU): ~$10/month
- **Total:** $50/month (+$25)

---

## 🎯 Recommendation

### For Testing/Development:
**Use exponential backoff retry (already implemented)**
- No extra cost
- Good enough for light load
- Works with current setup

### For Production (5-50 users):
**Option 1: App Runner + ElastiCache**
- Reasonable cost (+$15/month)
- Easy to set up
- Handles moderate load
- **START HERE**

### For Production (50+ users):
**Option 2: App Runner + ECS Workers + ElastiCache**
- Better scalability
- Workers separate from web
- Auto-scaling based on load

---

## 📋 Implementation Checklist

- [ ] **Create ElastiCache Redis cluster**
  - [ ] Choose cache.t3.micro instance
  - [ ] Note endpoint URL
  - [ ] Configure security group

- [ ] **Set Environment Variables**
  - [ ] `USE_CELERY=true`
  - [ ] `REDIS_URL=redis://endpoint:6379/0`

- [ ] **Update Start Command**
  - [ ] Add Celery worker to startup
  - [ ] Test locally first

- [ ] **Update Flask Endpoints**
  - [ ] Modify `/analyze_section` to use tasks
  - [ ] Modify `/chat` to use tasks
  - [ ] Add `/task_status/<id>` endpoint
  - [ ] Add `/queue_stats` endpoint

- [ ] **Update Frontend**
  - [ ] Add task polling logic
  - [ ] Add progress indicators
  - [ ] Handle async responses

- [ ] **Test Everything**
  - [ ] Test without Celery (fallback mode)
  - [ ] Test with Celery (async mode)
  - [ ] Test concurrent requests
  - [ ] Test retry behavior

- [ ] **Monitor in Production**
  - [ ] Set up Flower dashboard
  - [ ] Monitor queue sizes
  - [ ] Watch for failures

---

## 🔄 Migration Strategy

### Phase 1: Add Celery Infrastructure (No Code Changes)
1. Create Redis cluster
2. Add Celery packages
3. Set `USE_CELERY=false` (disabled)
4. Deploy and test

### Phase 2: Enable Celery (With Fallback)
1. Set `USE_CELERY=true`
2. Code automatically falls back if Redis unavailable
3. Deploy and test
4. Monitor queue behavior

### Phase 3: Update Frontend (Async UI)
1. Add task polling
2. Improve progress indicators
3. Better error handling

---

## 📞 Support

If you run into issues:

1. **Check Redis connectivity:**
   ```bash
   redis-cli -h your-redis-endpoint ping
   ```

2. **Check Celery worker logs:**
   ```bash
   celery -A celery_config worker --loglevel=debug
   ```

3. **Check queue stats:**
   ```bash
   curl http://your-app/queue_stats
   ```

4. **Use Flower dashboard:**
   ```bash
   celery -A celery_config flower
   ```

---

**Created:** November 17, 2025
**Files Created:**
- `celery_config.py` - Celery configuration
- `celery_tasks.py` - Task definitions
- `celery_integration.py` - Flask integration helper

**Status:** ✅ READY FOR TESTING
**Next:** Set up Redis and test async processing
