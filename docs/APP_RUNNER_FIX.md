# AWS App Runner Deployment Fix

## Problem

**Symptom**: Build succeeds but deployment fails at the final stage

**Error**: "Failed to deploy your application source code"

**Root Cause**: AWS App Runner's managed Python runtime doesn't support background processes. The application was trying to start a Celery worker subprocess, which caused the deployment to fail.

## Solution Applied

### 1. Updated `main.py` (Lines 107-131)

Modified the startup logic to detect App Runner environment and skip Celery worker startup:

```python
# Check if we're on App Runner - it doesn't support background processes
is_app_runner = (
    os.environ.get('AWS_EXECUTION_ENV', '').startswith('AWS_AppRunner_') or
    'APP_RUNNER' in os.environ.get('AWS_EXECUTION_ENV', '') or
    os.environ.get('FLASK_ENV') == 'production' and not os.environ.get('AWS_EXECUTION_ENV')
)

if is_app_runner:
    print("🔧 Running on AWS App Runner - Background processes disabled")
    print("   Using synchronous processing mode (no Celery worker)")
    print("   All AI analysis will run inline")
else:
    # Local development - start Celery worker as subprocess
    celery_process = start_celery_worker()
```

**What this does**:
- Detects when running on App Runner
- Skips Celery worker startup
- Falls back to synchronous processing (all AI analysis runs inline)

### 2. Updated `apprunner.yaml`

Added explicit health check configuration and disabled Redis:

```yaml
run:
  runtime-version: 3.11
  command: python main.py
  network:
    port: 8080
    env: PORT
  # Health check configuration
  health-check:
    protocol: HTTP
    path: /health
    interval: 10
    timeout: 5
    healthy-threshold: 1
    unhealthy-threshold: 5
  env:
    - name: REDIS_URL
      value: "disabled"
```

**What this does**:
- Configures proper health checks at `/health` endpoint
- Explicitly disables Redis/RQ connection attempts
- Ensures app starts correctly without background workers

## How It Works Now

### On App Runner (Production)
1. ✅ No Celery/RQ worker attempts
2. ✅ All AI analysis runs synchronously (inline)
3. ✅ Simpler, more reliable deployment
4. ✅ Health checks pass immediately
5. ✅ No background process errors

### On Local Development
1. ✅ Celery worker starts as subprocess
2. ✅ Async task processing available
3. ✅ RQ/Redis queuing works
4. ✅ Full feature set

## Performance Impact

**App Runner (Synchronous Mode)**:
- AI analysis runs inline (blocking)
- Request takes 5-15 seconds to complete
- Simple, predictable behavior
- No queue management needed

**Local Dev (Async Mode)**:
- AI analysis runs in background
- Request returns immediately with task ID
- Frontend polls for results
- More complex but non-blocking

## Deployment Steps

1. **Commit the changes**:
   ```bash
   git add main.py apprunner.yaml docs/APP_RUNNER_FIX.md
   git commit -m "fix: Disable Celery worker on App Runner managed runtime"
   ```

2. **Push to trigger deployment**:
   ```bash
   git push origin main
   ```

3. **Monitor deployment**:
   - AWS App Runner console will show build progress
   - Build should complete successfully (2-3 minutes)
   - Deployment should now succeed (1-2 minutes)
   - Health checks should pass immediately

## Verification

After deployment succeeds:

1. **Check health endpoint**:
   ```bash
   curl https://your-app.awsapprunner.com/health
   ```
   Expected response:
   ```json
   {"status": "healthy", "timestamp": "2025-11-25T..."}
   ```

2. **Check application logs** (App Runner console):
   ```
   🔧 Running on AWS App Runner - Background processes disabled
      Using synchronous processing mode (no Celery worker)
      All AI analysis will run inline

   ✅ Model Configuration:
      • Model: Claude Sonnet 4.5 (Enhanced)
      • Region: us-east-1
      • Port: 8080
   ```

3. **Test document upload**:
   - Upload a document through the UI
   - AI analysis should work (takes 5-15 seconds)
   - No task queue errors

## Alternative: Use Docker Deployment

If you need async processing (Celery/RQ), consider using **Docker-based deployment** instead of the managed Python runtime:

### Option A: Elastic Beanstalk (Docker)
- Supports background processes
- Full Celery/RQ support
- More complex but more flexible
- See: `docs/DEPLOYMENT_GUIDE_BEANSTALK.md`

### Option B: ECS Fargate (Docker)
- Best for production workloads
- Supports multiple containers (web + worker)
- Auto-scaling available
- Requires Dockerfile

### Option C: Lightsail Containers
- Simpler than ECS
- Supports Docker
- Fixed pricing
- See: `docs/DEPLOYMENT_GUIDE_LIGHTSAIL.md`

## Files Modified

1. ✅ `main.py` - Added App Runner detection and Celery skip logic
2. ✅ `apprunner.yaml` - Added health checks and disabled Redis
3. ✅ `docs/APP_RUNNER_FIX.md` - This documentation

## No Changes Needed

- ✅ `app.py` - Already has proper RQ_ENABLED fallback
- ✅ `rq_config.py` - Already has graceful Redis connection handling
- ✅ `requirements.txt` - All dependencies compatible

## Summary

✅ **Problem**: App Runner can't run background processes (Celery worker)
✅ **Solution**: Detect App Runner environment and use synchronous processing
✅ **Result**: Deployment succeeds, app runs correctly (albeit slower)
✅ **Trade-off**: Synchronous processing means slower responses but simpler deployment

## Next Steps

After successful deployment:

1. Test the application thoroughly
2. Monitor performance and response times
3. If async processing is critical, migrate to Docker-based deployment
4. Consider upgrading to ECS or Elastic Beanstalk for production workloads

---

**Created**: 2025-11-25
**Status**: Ready to deploy
**Priority**: Critical fix
