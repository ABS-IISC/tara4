# Quick Start: Enable Multi-User Request Handling

**Goal:** Prevent AWS throttling when multiple users use the system simultaneously

**Time Required:** 5 minutes

---

## 🚀 Quick Setup (Recommended)

### Step 1: Add to `.env` file

Create or edit `.env` file in the project root:

```bash
# Enable Request Manager (prevents AWS throttling)
ENABLE_REQUEST_MANAGER=true

# Rate limit preset (choose one based on your needs)
RATE_LIMIT_PRESET=production-low

# Alternative: Manual configuration
# MAX_CONCURRENT_REQUESTS=3
# REQUESTS_PER_MINUTE=30
# MAX_REQUESTS_PER_USER=2
```

### Step 2: Restart Flask

```bash
# Stop existing Flask process
pkill -f "python.*app.py"

# Start Flask
python3 app.py
```

### Step 3: Verify

You should see this in the console:

```
✅ Request Manager enabled for parallel request handling
📊 Rate limit: 30 requests/minute
```

**That's it!** Your system now handles multiple users safely.

---

## 📋 Configuration Presets

Choose a preset based on your expected usage:

### Development (1-3 users)
```bash
RATE_LIMIT_PRESET=development
```
- Max 2 concurrent AWS requests
- 20 requests per minute
- Best for: Local testing

### Production Low (5-10 users)
```bash
RATE_LIMIT_PRESET=production-low
```
- Max 3 concurrent AWS requests
- 30 requests per minute
- Best for: Small production deployments

### Production High (10-20 users)
```bash
RATE_LIMIT_PRESET=production-high
```
- Max 5 concurrent AWS requests
- 60 requests per minute
- Best for: Large production deployments
- **Requires AWS quota increase**

### Single User (No queuing)
```bash
RATE_LIMIT_PRESET=single-user
```
- Disables request manager
- Direct AWS calls
- Best for: Personal use only

---

## 🧪 Testing

### Test 1: Single User
1. Upload a document
2. Analyze 3-5 sections
3. **Expected:** All sections succeed

### Test 2: Multiple Users (Simulation)
```bash
# Open 3 browser windows
# Window 1: Analyze Section 1
# Window 2: Analyze Section 1 (same or different doc)
# Window 3: Analyze Section 1

# Expected: All succeed, some may wait briefly in queue
```

### Test 3: Check Statistics
```bash
# Add this to a Python shell or Flask route
from core.request_manager import get_request_manager

stats = get_request_manager().get_stats()
print(stats)
```

---

## ⚙️ Advanced: Enable Celery (Optional)

**When to use:** If you want async processing (better UX for 5+ users)

### Prerequisites
```bash
# Install dependencies
pip install celery redis

# Start Redis
redis-server
```

### Configuration
```bash
# Add to .env
USE_CELERY=true
ENABLE_REQUEST_MANAGER=true  # Use both for best results
```

### Start Celery Worker
```bash
# In a separate terminal
celery -A celery_config worker --loglevel=info
```

### Start Flask
```bash
python3 app.py
```

---

## 🔍 Troubleshooting

### Issue: "Request Manager not available"

**Cause:** Python import error

**Fix:**
```bash
# Verify file exists
ls core/request_manager.py

# If missing, the file was created in this session
# It should be there now
```

### Issue: Still getting throttled

**Cause:** Rate limit too high for your AWS quota

**Fix:**
```bash
# Reduce rate limit in .env
REQUESTS_PER_MINUTE=20  # Lower value

# Or use development preset
RATE_LIMIT_PRESET=development
```

### Issue: Long wait times

**Cause:** Queue building up, too many users

**Solutions:**
1. **Increase concurrent requests:**
   ```bash
   MAX_CONCURRENT_REQUESTS=5
   ```

2. **Enable Celery** (async processing)

3. **Request AWS quota increase:**
   - AWS Console → Bedrock → Service Quotas
   - Request increase to 200 requests/minute

---

## 📊 Monitoring

### Check Queue Status
```python
from core.request_manager import get_request_manager

manager = get_request_manager()
stats = manager.get_stats()

print(f"Queue size: {stats['queue_size']}")
print(f"Active requests: {stats['active_requests']}")
print(f"Active users: {stats['active_users']}")
```

### Check Celery Status (if enabled)
```bash
curl http://localhost:8080/queue_stats
```

---

## ✅ Summary

**What you get:**
- ✅ No AWS throttling errors
- ✅ Fair request scheduling
- ✅ Automatic rate limiting
- ✅ All users' requests succeed
- ✅ Transparent to users

**What changes:**
- Requests may wait briefly in queue during high load
- You'll see queue messages in logs
- Better overall reliability

**When to use Celery:**
- 5+ concurrent users
- Want async processing
- Need better UX

---

## 📚 More Information

- **Full Analysis:** [MULTI_USER_PARALLEL_REQUESTS_ANALYSIS.md](MULTI_USER_PARALLEL_REQUESTS_ANALYSIS.md)
- **Timeout Fixes:** [TIMEOUT_FIX_NOV18.md](TIMEOUT_FIX_NOV18.md)
- **Configuration Options:** [config/rate_limit_config.py](config/rate_limit_config.py)

---

**Last Updated:** November 18, 2025
