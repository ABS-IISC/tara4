# Celery + Redis Architecture for AI-Prism

## Current Architecture (Synchronous - Blocking)

```
┌─────────────┐
│   User      │
│  Browser    │
└──────┬──────┘
       │ 1. Upload document
       ▼
┌─────────────────────┐
│   Flask Server      │
│                     │
│  ┌──────────────┐   │
│  │ AI Analysis  │   │ ⏳ User waits 30-60 seconds
│  │ (Blocking)   │   │
│  └──────────────┘   │
│                     │
└──────┬──────────────┘
       │ 2. Return results
       ▼
┌─────────────┐
│   User      │
│  Browser    │
└─────────────┘
```

**Problem:** User must wait for entire analysis to complete


## New Architecture (Asynchronous - Non-Blocking)

```
┌─────────────┐
│   User      │
│  Browser    │
└──────┬──────┘
       │ 1. Upload document
       ▼
┌─────────────────────────────────────────────────┐
│              Flask Server (Web App)             │
│                                                 │
│  • Receives upload                              │
│  • Creates task ID                              │
│  • Returns immediately: "Processing..."         │
│                                                 │
└──────┬──────────────────────────────────────────┘
       │ 2. Queue task
       ▼
┌─────────────────────────────────────────────────┐
│              Redis (Message Broker)             │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Task 1   │  │ Task 2   │  │ Task 3   │      │
│  │ Pending  │  │ Pending  │  │ Pending  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│                                                 │
└──────┬──────────────────────────────────────────┘
       │ 3. Workers fetch tasks
       ▼
┌─────────────────────────────────────────────────┐
│           Celery Workers (Background)           │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  Worker 1    │  │  Worker 2    │            │
│  │              │  │              │            │
│  │ AI Analysis  │  │ AI Analysis  │            │
│  │ Document 1   │  │ Document 2   │            │
│  │              │  │              │            │
│  └──────────────┘  └──────────────┘            │
│                                                 │
└──────┬──────────────────────────────────────────┘
       │ 4. Store results
       ▼
┌─────────────────────────────────────────────────┐
│         Redis (Results Storage)                 │
│                                                 │
│  Task ID: abc123 → Results: {...}              │
│  Task ID: def456 → Results: {...}              │
│                                                 │
└──────┬──────────────────────────────────────────┘
       │ 5. Poll for results
       ▼
┌─────────────┐
│   User      │
│  Browser    │ ✅ Gets results when ready
└─────────────┘
```


## Detailed Flow Diagram

```
USER                FLASK               REDIS              CELERY WORKER
 │                   │                   │                      │
 │  Upload Doc       │                   │                      │
 ├──────────────────>│                   │                      │
 │                   │                   │                      │
 │                   │ Queue Task        │                      │
 │                   ├──────────────────>│                      │
 │                   │                   │                      │
 │  Task ID: 123     │                   │                      │
 │<──────────────────┤                   │                      │
 │  "Processing..."  │                   │                      │
 │                   │                   │                      │
 │                   │                   │  Fetch Task          │
 │                   │                   │<─────────────────────┤
 │                   │                   │                      │
 │                   │                   │  Task Details        │
 │                   │                   ├─────────────────────>│
 │                   │                   │                      │
 │                   │                   │              ┌───────┴────────┐
 │                   │                   │              │ AI Analysis    │
 │                   │                   │              │ • Section Det. │
 │                   │                   │              │ • Feedback Gen.│
 │                   │                   │              │ • Risk Assess. │
 │                   │                   │              └───────┬────────┘
 │                   │                   │                      │
 │                   │                   │  Store Results       │
 │                   │                   │<─────────────────────┤
 │                   │                   │                      │
 │  Check Status     │                   │                      │
 │  (Task ID: 123)   │                   │                      │
 ├──────────────────>│                   │                      │
 │                   │                   │                      │
 │                   │ Get Results       │                      │
 │                   ├──────────────────>│                      │
 │                   │                   │                      │
 │                   │ Results Data      │                      │
 │                   │<──────────────────┤                      │
 │                   │                   │                      │
 │  Results Ready ✅ │                   │                      │
 │<──────────────────┤                   │                      │
 │                   │                   │                      │
```


## Component Breakdown

### 1. Flask Server (Web Application)
```
Role: Handle HTTP requests
Tasks:
  • Receive document uploads
  • Create Celery tasks
  • Return task IDs immediately
  • Provide status endpoints
  • Serve results when ready
```

### 2. Redis (Message Broker + Result Backend)
```
Role: Queue management & storage
Tasks:
  • Store pending tasks
  • Deliver tasks to workers
  • Store task results
  • Track task status
```

### 3. Celery Workers (Background Processors)
```
Role: Execute long-running tasks
Tasks:
  • Fetch tasks from Redis
  • Run AI analysis
  • Process documents
  • Store results back to Redis
```

### 4. User Browser (Frontend)
```
Role: User interface
Tasks:
  • Upload documents
  • Poll for task status
  • Display progress
  • Show results when ready
```


## Benefits Comparison

| Feature | Without Celery | With Celery |
|---------|---------------|-------------|
| Response Time | 30-60 seconds | < 1 second |
| User Experience | Blocked/Waiting | Immediate feedback |
| Concurrent Users | Limited | Unlimited |
| Scalability | Single server | Multiple workers |
| Reliability | Fails if server restarts | Tasks persist in queue |
| Progress Tracking | Not possible | Real-time updates |


## Real-World Example for AI-Prism

### Scenario: 3 Users Upload Documents Simultaneously

**Without Celery:**
```
User A uploads → Waits 60s → Gets results
User B uploads → Waits 60s → Gets results  
User C uploads → Waits 60s → Gets results
Total time: 180 seconds (sequential)
```

**With Celery (3 workers):**
```
User A uploads → Task queued → Worker 1 processes
User B uploads → Task queued → Worker 2 processes
User C uploads → Task queued → Worker 3 processes
All get results in ~60 seconds (parallel)
Total time: 60 seconds (parallel)
```


## Implementation for AI-Prism

### File Structure
```
tara2/
├── app.py                 # Flask routes
├── celery_app.py          # Celery configuration
├── tasks.py               # Background tasks
├── requirements.txt       # Add celery, redis
└── docker-compose.yml     # Redis + Workers
```

### Key Code Changes

**1. Define Tasks (tasks.py)**
```python
from celery_app import celery
from core.document_analyzer import DocumentAnalyzer

@celery.task(bind=True)
def analyze_document_task(self, doc_path, session_id):
    # Update progress
    self.update_state(state='PROGRESS', meta={'status': 'Analyzing...'})
    
    # Run analysis
    analyzer = DocumentAnalyzer()
    results = analyzer.analyze(doc_path)
    
    return results
```

**2. Flask Route (app.py)**
```python
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['document']
    doc_path = save_file(file)
    
    # Queue task instead of running directly
    task = analyze_document_task.delay(doc_path, session['id'])
    
    return jsonify({'task_id': task.id, 'status': 'queued'})

@app.route('/status/<task_id>')
def check_status(task_id):
    task = analyze_document_task.AsyncResult(task_id)
    return jsonify({'state': task.state, 'result': task.result})
```

**3. Frontend Polling (JavaScript)**
```javascript
// Upload document
fetch('/upload', {method: 'POST', body: formData})
  .then(r => r.json())
  .then(data => {
    // Start polling for results
    checkStatus(data.task_id);
  });

// Poll for status
function checkStatus(taskId) {
  fetch(`/status/${taskId}`)
    .then(r => r.json())
    .then(data => {
      if (data.state === 'SUCCESS') {
        displayResults(data.result);
      } else {
        setTimeout(() => checkStatus(taskId), 2000); // Check every 2s
      }
    });
}
```

---

**Summary:** Celery + Redis transforms AI-Prism from a blocking, single-user tool into a responsive, scalable multi-user application with real-time progress tracking.
