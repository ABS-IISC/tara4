# 🧪 AI-Prism Testing Guide - Complete Test Suite

**Date:** November 17, 2025
**Purpose:** Comprehensive testing procedures for all features
**Status:** ✅ READY FOR TESTING

---

## 📋 Table of Contents

1. [Testing Overview](#testing-overview)
2. [Local Testing](#local-testing)
3. [App Runner Testing](#app-runner-testing)
4. [Feature-Specific Tests](#feature-specific-tests)
5. [Load Testing](#load-testing)
6. [Acceptance Criteria](#acceptance-criteria)

---

## 🎯 Testing Overview

### Testing Levels:

1. **Unit Tests** - Individual component testing
2. **Integration Tests** - Component interaction testing
3. **System Tests** - End-to-end workflow testing
4. **Load Tests** - Performance and scalability testing
5. **Acceptance Tests** - User-facing functionality verification

### Features to Test:

- ✅ **Baseline:** Original synchronous behavior
- ✅ **Celery Queue:** Async task processing
- ✅ **Multi-Model Fallback:** Automatic model switching
- ✅ **Combined:** Both features enabled
- ✅ **Error Handling:** Graceful degradation
- ✅ **Security:** IAM role authentication

---

## 🏠 Local Testing

### Setup Local Environment

**Prerequisites:**
```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (for Celery testing)
redis-server
```

---

### Test Suite 1: Baseline (No New Features)

**Purpose:** Verify original functionality still works

**Setup:**
```bash
# No environment variables set
python app.py
```

**Test 1.1: Health Check**
```bash
curl http://localhost:8080/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T12:00:00"
}
```
✅ **Pass Criteria:** Status 200, JSON response with "healthy" status

---

**Test 1.2: Model Stats (Without Model Manager)**
```bash
curl http://localhost:8080/model_stats
```

**Expected Response:**
```json
{
  "success": false,
  "multi_model_enabled": false,
  "message": "Multi-model fallback not configured"
}
```
✅ **Pass Criteria:** Returns graceful message, doesn't crash

---

**Test 1.3: Queue Stats (Without Celery)**
```bash
curl http://localhost:8080/queue_stats
```

**Expected Response:**
```json
{
  "available": false,
  "error": "Celery not configured"
}
```
✅ **Pass Criteria:** Returns graceful message, doesn't crash

---

**Test 1.4: Document Upload and Analysis**

**Steps:**
1. Open http://localhost:8080 in browser
2. Upload a .docx file
3. Wait for sections to load
4. Click "Analyze" on a section
5. Wait for feedback (5-10 seconds)

**Expected Behavior:**
- ✅ File uploads successfully
- ✅ Sections extracted and displayed
- ✅ Analysis completes synchronously
- ✅ Feedback items appear
- ✅ Accept/Reject buttons work
- ✅ Download document works

✅ **Pass Criteria:** All steps complete successfully, no errors in console

---

**Test 1.5: Chat Functionality**

**Steps:**
1. Upload document
2. Analyze a section
3. Open chat panel
4. Send message: "What are the main issues?"
5. Wait for response

**Expected Behavior:**
- ✅ Chat opens successfully
- ✅ Message sends immediately
- ✅ Response appears within 3-5 seconds
- ✅ Response is relevant and formatted

✅ **Pass Criteria:** Chat works synchronously with immediate response

---

### Test Suite 2: With Celery Queue

**Purpose:** Verify async task processing with queue

**Setup:**
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
celery -A celery_config worker --loglevel=info

# Terminal 3: Start Flask with Celery enabled
USE_CELERY=true REDIS_URL=redis://localhost:6379/0 python app.py
```

---

**Test 2.1: Verify Celery Availability**
```bash
curl http://localhost:8080/queue_stats
```

**Expected Response:**
```json
{
  "available": true,
  "workers": 1,
  "active_tasks": 0,
  "reserved_tasks": 0,
  "total_pending": 0
}
```
✅ **Pass Criteria:** Shows available=true with worker count

---

**Test 2.2: Async Document Analysis**

**Steps:**
1. Open http://localhost:8080 in browser
2. Upload document
3. Click "Analyze" on a section
4. Check network tab (F12)

**Expected Behavior:**
- ✅ POST to `/analyze_section` returns immediately (< 1 second)
- ✅ Response contains `task_id` and `async: true`
- ✅ Frontend polls `/task_status/{task_id}` every 2 seconds
- ✅ Task state changes: PENDING → PROGRESS → SUCCESS
- ✅ Feedback appears when task completes

**Check Logs (Terminal 2 - Celery Worker):**
```
[2025-11-17 12:00:00,000] Task celery_tasks.analyze_section_task[abc-123] received
[2025-11-17 12:00:00,100] Task celery_tasks.analyze_section_task[abc-123] succeeded in 5.2s
```

✅ **Pass Criteria:** Analysis completes asynchronously with task polling

---

**Test 2.3: Rate Limiting**

**Steps:**
1. Upload document with 10 sections
2. Click "Analyze" on all 10 sections rapidly (within 10 seconds)
3. Monitor queue stats and logs

**Expected Behavior:**
- ✅ All 10 tasks accepted immediately
- ✅ Tasks queue up in Redis
- ✅ Only 5 tasks process per minute (rate limit)
- ✅ Remaining tasks wait in queue
- ✅ All tasks complete within 2 minutes

**Check Queue Stats:**
```bash
curl http://localhost:8080/queue_stats
```

**Expected Response:**
```json
{
  "available": true,
  "workers": 1,
  "active_tasks": 1,
  "reserved_tasks": 4,
  "total_pending": 5
}
```

✅ **Pass Criteria:** Rate limiting enforced, no throttling errors

---

**Test 2.4: Task Cancellation**

**Steps:**
1. Start a long analysis task
2. Get task_id from response
3. Cancel task:
   ```bash
   curl -X POST http://localhost:8080/cancel_task/{task_id}
   ```

**Expected Response:**
```json
{
  "success": true,
  "task_id": "abc-123",
  "cancelled": true
}
```

**Check Task Status:**
```bash
curl http://localhost:8080/task_status/{task_id}
```

**Expected Response:**
```json
{
  "task_id": "abc-123",
  "state": "REVOKED"
}
```

✅ **Pass Criteria:** Task cancelled successfully, no errors

---

### Test Suite 3: With Multi-Model Fallback

**Purpose:** Verify automatic model switching on throttling

**Setup:**
```bash
# Start Flask with model manager available
python app.py
```

---

**Test 3.1: Verify Model Manager Availability**
```bash
curl http://localhost:8080/model_stats
```

**Expected Response:**
```json
{
  "success": true,
  "multi_model_enabled": true,
  "stats": {
    "total_models": 4,
    "available_models": 4,
    "throttled_models": 0,
    "models": [
      {
        "id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "name": "Claude 3.5 Sonnet (Primary)",
        "priority": 1,
        "status": "available",
        "throttle_count": 0
      },
      {
        "id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "name": "Claude Fallback 1",
        "priority": 2,
        "status": "available",
        "throttle_count": 0
      },
      {
        "id": "anthropic.claude-3-sonnet-20240229-v1:0",
        "name": "Claude Fallback 2",
        "priority": 3,
        "status": "available",
        "throttle_count": 0
      },
      {
        "id": "anthropic.claude-3-haiku-20240307-v1:0",
        "name": "Claude Fallback 3",
        "priority": 4,
        "status": "available",
        "throttle_count": 0
      }
    ]
  }
}
```

✅ **Pass Criteria:** 4 models shown, all available

---

**Test 3.2: Simulate Throttling (Burst Load)**

**Steps:**
1. Upload document with 20 sections
2. Click "Analyze" on 10 sections rapidly
3. Monitor logs and model stats

**Expected Behavior:**
- ✅ First few requests use primary model
- ✅ Primary model gets throttled (too many requests)
- ✅ System automatically switches to Fallback 1
- ✅ Fallback 1 processes remaining requests
- ✅ All requests complete successfully

**Check Logs:**
```
🎯 Selected: Claude 3.5 Sonnet (Primary) (Priority 1)
✅ Success with Claude 3.5 Sonnet (Primary)
🎯 Selected: Claude 3.5 Sonnet (Primary) (Priority 1)
🚫 Claude 3.5 Sonnet (Primary) throttled, trying next model...
🎯 Selected: Claude Fallback 1 (Priority 2)
✅ Success with Claude Fallback 1
```

**Check Model Stats After Test:**
```bash
curl http://localhost:8080/model_stats
```

**Expected Response:**
```json
{
  "stats": {
    "models": [
      {
        "name": "Claude 3.5 Sonnet (Primary)",
        "status": "throttled",
        "throttle_count": 1,
        "cooldown_remaining": 45
      },
      {
        "name": "Claude Fallback 1",
        "status": "available",
        "throttle_count": 0
      }
    ]
  }
}
```

✅ **Pass Criteria:** Automatic model switching, all requests succeed

---

**Test 3.3: Reset Model Cooldowns**

**Steps:**
1. After Test 3.2 (primary model throttled)
2. Reset cooldowns:
   ```bash
   curl -X POST http://localhost:8080/reset_model_cooldowns
   ```

**Expected Response:**
```json
{
  "success": true,
  "message": "All model cooldowns have been reset"
}
```

**Verify:**
```bash
curl http://localhost:8080/model_stats
```

**Expected Response:**
```json
{
  "stats": {
    "available_models": 4,
    "throttled_models": 0
  }
}
```

✅ **Pass Criteria:** All models available again

---

### Test Suite 4: Combined (Celery + Multi-Model)

**Purpose:** Verify both features work together

**Setup:**
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
celery -A celery_config worker --loglevel=info --concurrency=2

# Terminal 3: Start Flask with both features
USE_CELERY=true REDIS_URL=redis://localhost:6379/0 python app.py
```

---

**Test 4.1: Verify Both Features Available**

```bash
# Check Celery
curl http://localhost:8080/queue_stats

# Check Models
curl http://localhost:8080/model_stats
```

**Expected:**
- ✅ Celery available with workers
- ✅ 4 models available

---

**Test 4.2: Maximum Throttling Protection**

**Steps:**
1. Upload document with 30 sections
2. Click "Analyze All" (if available) or analyze 20 sections rapidly
3. Monitor queue stats, model stats, and logs

**Expected Behavior:**
- ✅ All 20 tasks submitted to queue immediately
- ✅ Queue processes 5 tasks/minute (rate limit)
- ✅ Within each task, multi-model fallback works
- ✅ Primary model may throttle, falls back to other models
- ✅ All 20 tasks complete successfully within 5 minutes
- ✅ No ThrottlingException errors

**Monitor Progress:**
```bash
# Every 30 seconds, check:
curl http://localhost:8080/queue_stats
curl http://localhost:8080/model_stats
```

✅ **Pass Criteria:** All tasks complete, multiple models used, no errors

---

### Test Suite 5: Error Handling

**Purpose:** Verify graceful error handling

---

**Test 5.1: Redis Down (Celery Enabled)**

**Steps:**
1. Stop Redis (`Ctrl+C` in Terminal 1)
2. Verify Flask still running
3. Try document analysis

**Expected Behavior:**
- ✅ Flask doesn't crash
- ✅ `/queue_stats` returns `"available": false`
- ✅ Analysis falls back to synchronous mode
- ✅ Analysis completes successfully

✅ **Pass Criteria:** Graceful fallback, no crash

---

**Test 5.2: Invalid Model ID**

**Steps:**
1. Set invalid model ID:
   ```bash
   BEDROCK_MODEL_ID=invalid-model-id python app.py
   ```
2. Try document analysis

**Expected Behavior:**
- ✅ Error message in logs
- ✅ Falls back to mock response or error message
- ✅ App doesn't crash

✅ **Pass Criteria:** Graceful error handling, clear error message

---

**Test 5.3: No AWS Credentials**

**Steps:**
1. Unset AWS credentials:
   ```bash
   unset AWS_ACCESS_KEY_ID
   unset AWS_SECRET_ACCESS_KEY
   python app.py
   ```
2. Try Claude connection test

**Expected Behavior:**
- ✅ Connection test fails gracefully
- ✅ Error message: "No AWS credentials found"
- ✅ Mock responses used for analysis
- ✅ App still functional (with mock data)

✅ **Pass Criteria:** Graceful degradation, clear error messages

---

## ☁️ App Runner Testing

### Prerequisites:
- App Runner service deployed
- IAM role configured
- Redis cluster created (for Celery testing)

---

### Test Suite 6: Basic App Runner

**Purpose:** Verify deployment works

---

**Test 6.1: Service Health**
```bash
APP_URL="https://your-app-url.region.awsapprunner.com"
curl $APP_URL/health
```

**Expected:**
```json
{
  "status": "healthy"
}
```
✅ **Pass Criteria:** Status 200

---

**Test 6.2: Claude Connection**
```bash
curl $APP_URL/test_claude_connection
```

**Expected:**
```json
{
  "success": true,
  "claude_status": {
    "connected": true,
    "model": "Claude 3.5 Sonnet",
    "response_time": 1.23
  }
}
```

✅ **Pass Criteria:** Connected=true, reasonable response time

---

**Test 6.3: Model Configuration**
```bash
curl $APP_URL/model_stats
```

**Expected:**
```json
{
  "success": true,
  "multi_model_enabled": true,
  "stats": {
    "total_models": 4,
    "available_models": 4
  }
}
```

✅ **Pass Criteria:** 4 models available

---

**Test 6.4: Queue Configuration (if Celery enabled)**
```bash
curl $APP_URL/queue_stats
```

**Expected:**
```json
{
  "available": true,
  "workers": 2
}
```

✅ **Pass Criteria:** Available=true with workers

---

### Test Suite 7: App Runner End-to-End

**Purpose:** Full workflow test in production

---

**Test 7.1: Document Upload and Analysis**

**Steps:**
1. Open $APP_URL in browser
2. Upload real document (.docx)
3. Wait for sections to load (5-10 seconds)
4. Analyze 5 sections
5. Accept some feedback, reject some
6. Add custom feedback
7. Use chat feature
8. Complete review and download

**Expected Behavior:**
- ✅ Upload succeeds
- ✅ Sections extracted correctly
- ✅ Analysis completes (async or sync)
- ✅ Feedback items appear
- ✅ Accept/reject works
- ✅ Custom feedback saves
- ✅ Chat responds
- ✅ Download includes comments

✅ **Pass Criteria:** Complete workflow succeeds, document has comments

---

**Test 7.2: Concurrent Users**

**Steps:**
1. Open $APP_URL in 3 different browsers/tabs
2. Upload documents in all 3
3. Analyze sections simultaneously
4. Monitor model stats and queue stats

**Expected Behavior:**
- ✅ All 3 users can upload simultaneously
- ✅ All analyses complete successfully
- ✅ No ThrottlingException errors
- ✅ Queue handles load (if Celery enabled)
- ✅ Model fallback activates if needed

✅ **Pass Criteria:** All users complete successfully

---

## 🔥 Load Testing

### Test Suite 8: Performance Testing

**Purpose:** Measure system performance under load

---

**Test 8.1: Baseline Performance (No Load)**

**Tool:** Apache Bench
```bash
ab -n 10 -c 1 $APP_URL/health
```

**Expected:**
- Requests per second: > 50
- Time per request: < 20ms
- Failed requests: 0

✅ **Pass Criteria:** All requests succeed quickly

---

**Test 8.2: Concurrent Request Handling**

**Without Celery:**
```bash
ab -n 100 -c 10 $APP_URL/health
```

**Expected:**
- Requests per second: > 20
- Failed requests: 0
- 50th percentile: < 500ms
- 95th percentile: < 1000ms

**With Celery:**
```bash
ab -n 100 -c 10 $APP_URL/health
```

**Expected:**
- Requests per second: > 30
- Failed requests: 0
- Better consistency in response times

✅ **Pass Criteria:** All requests succeed, reasonable latency

---

**Test 8.3: Analysis Load Test**

**Manual Test:**
1. Upload document with 20 sections
2. Start timer
3. Analyze all 20 sections
4. Stop timer when all complete

**Without Celery (Baseline):**
- Expected time: 3-5 minutes
- Possible throttling errors

**With Celery:**
- Expected time: 4-5 minutes (rate limited)
- No throttling errors

**With Celery + Multi-Model:**
- Expected time: 3-4 minutes
- No throttling errors
- Multiple models used

✅ **Pass Criteria:** All complete, time within range, no errors

---

## ✅ Acceptance Criteria

### Core Functionality:
- [ ] Document upload works
- [ ] Section extraction works
- [ ] Analysis generates feedback
- [ ] Feedback has all fields (description, suggestion, questions, etc.)
- [ ] Accept/reject functionality works
- [ ] Custom feedback works
- [ ] Chat functionality works
- [ ] Document download works
- [ ] Downloaded document has comments

### Celery (if enabled):
- [ ] Queue stats shows workers
- [ ] Analysis returns task_id
- [ ] Task status polling works
- [ ] Rate limiting enforced (5/min)
- [ ] All tasks complete successfully
- [ ] Graceful fallback if Redis down

### Multi-Model Fallback (if enabled):
- [ ] Model stats shows 4 models
- [ ] Primary model used first
- [ ] Automatic switching on throttle
- [ ] Cooldowns tracked correctly
- [ ] Reset cooldowns works
- [ ] All models can succeed

### Error Handling:
- [ ] Invalid file upload handled
- [ ] Network errors handled
- [ ] AWS credential errors handled
- [ ] Throttling errors handled
- [ ] Redis connection errors handled
- [ ] Invalid model ID handled

### Performance:
- [ ] Health endpoint < 100ms
- [ ] Analysis completes < 15 seconds
- [ ] Chat responds < 5 seconds
- [ ] No memory leaks
- [ ] No crashes under load

### Security:
- [ ] IAM role authentication works
- [ ] No credentials in logs
- [ ] Redis encrypted (production)
- [ ] HTTPS enabled (App Runner)

---

## 📊 Test Report Template

**Date:** [Date]
**Tester:** [Name]
**Environment:** [Local/App Runner]
**Configuration:** [Celery: Yes/No, Multi-Model: Yes/No]

### Test Results:

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 1.1 | Health Check | ✅ Pass | |
| 1.2 | Model Stats | ✅ Pass | |
| ... | ... | ... | ... |

### Issues Found:

| Issue ID | Description | Severity | Status |
|----------|-------------|----------|--------|
| 1 | [Description] | High/Medium/Low | Open/Fixed |

### Overall Assessment:
- [ ] Ready for production
- [ ] Needs fixes
- [ ] Needs more testing

### Recommendations:
1. [Recommendation 1]
2. [Recommendation 2]

---

**Testing Guide Version:** 1.0
**Last Updated:** November 17, 2025
**Status:** ✅ READY FOR USE
