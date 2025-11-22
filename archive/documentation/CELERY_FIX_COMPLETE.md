# Celery "Missing bucket name" Error - Complete Fix

**Status**: ✅ **RESOLVED**
**Date**: November 19, 2025
**Impact**: Critical - Application startup and task processing

---

## 🎯 Problems Fixed

### 1. ❌ Missing Bucket Name Error
```
celery.exceptions.ImproperlyConfigured: Missing bucket name
```

**Root Cause**: Celery S3 backend was being initialized at module import time, before environment variables were set.

**Solution**: Implemented lazy initialization with proxy pattern.

---

### 2. ❌ Missing submit_chat_task Function
```
NameError: name 'submit_chat_task' is not defined
```

**Root Cause**: Function was referenced in code but never defined.

**Solution**: Updated to use `process_chat_task.delay()` directly (matches pattern used for analysis tasks).

---

### 3. ❌ Multi-Region Support
**Issue**: Application didn't respect AWS CLI profile region (always used us-east-2).

**Solution**: Implemented multi-source region detection:
1. `AWS_REGION` environment variable
2. `AWS_DEFAULT_REGION` environment variable
3. boto3 session default region (from AWS CLI config)
4. Fallback to us-east-2

---

## 🔧 Files Modified

### 1. [celery_config.py](celery_config.py) - Complete Rewrite

**Before**: Eager initialization at module import
```python
# Create Celery app immediately (PROBLEM!)
celery_app = Celery(
    'aiprism_tasks',
    broker=broker_url,
    backend=result_backend,  # Fails if env vars not set
    include=['celery_tasks_enhanced']
)
```

**After**: Lazy initialization with proxy pattern
```python
class _CeleryAppProxy:
    """Proxy object that lazily initializes Celery app"""
    def __getattr__(self, name):
        app = init_celery_app()  # Only initialize when first accessed
        return getattr(app, name)

celery_app = _CeleryAppProxy()  # Safe to import
```

**Key Changes**:
- ✅ Lazy initialization - only creates Celery app when first accessed
- ✅ Multi-source region detection (env vars → boto3 → fallback)
- ✅ Clear error messages with fix instructions
- ✅ Helper function `is_celery_available()` for checking availability
- ✅ Validates S3 backend URL format before initialization

---

### 2. [app.py](app.py:835) - Fixed Chat Task Submission

**Before**:
```python
task_id, is_async = submit_chat_task(  # Function doesn't exist!
    query=message,
    context=context
)
```

**After**:
```python
task = process_chat_task.delay(  # Direct Celery task call
    query=message,
    context=context
)
```

**Location**: Line 835

---

### 3. [run_local.sh](run_local.sh:24-41) - Enhanced Region Detection

**Added**:
```bash
# Detect AWS region from AWS CLI config if not set
if [ -z "$AWS_REGION" ] && [ -z "$AWS_DEFAULT_REGION" ]; then
    AWS_CLI_REGION=$(aws configure get region 2>/dev/null)
    if [ -n "$AWS_CLI_REGION" ]; then
        echo "✅ Detected AWS region from CLI profile: $AWS_CLI_REGION"
        export AWS_REGION=$AWS_CLI_REGION
        export AWS_DEFAULT_REGION=$AWS_CLI_REGION
    else
        echo "⚠️  No AWS region detected, using default: us-east-2"
        export AWS_REGION=us-east-2
        export AWS_DEFAULT_REGION=us-east-2
    fi
fi
```

---

## ✅ How to Use (3 Options)

### Option 1: Use Startup Script (Recommended) ⭐

```bash
./run_local.sh
```

**Benefits**:
- Automatically detects AWS region from CLI profile
- Sets all required environment variables
- Provides colored output for easy debugging
- Validates AWS credentials

---

### Option 2: Set Environment Variables Manually

```bash
export S3_BUCKET_NAME=felix-s3-bucket
export S3_BASE_PATH=tara/
export CELERY_RESULT_BACKEND=s3://felix-s3-bucket/tara/celery-results/

python3 app.py
```

**Note**: Region will be auto-detected from boto3 session if not set.

---

### Option 3: Use .env File

```bash
# Copy example file
cp .env.example .env

# Edit .env with your values
nano .env

# Load and run
export $(cat .env | grep -v '^#' | xargs)
python3 app.py
```

---

## 🧪 Testing & Verification

### Test 1: Celery Configuration Loading

```bash
python3 -c "from celery_config import is_celery_available; print('✅ Celery available' if is_celery_available() else '❌ Not available')"
```

**Expected Output**:
```
✅ Detected AWS region from boto3 session: us-east-1
✅ Celery configured with Amazon SQS + S3 (No Redis required)
   Broker: Amazon SQS (region: us-east-1)
   Backend: Amazon S3 (bucket: felix-s3-bucket)
   Queue prefix: aiprism-
   Enhanced mode: Enabled
✅ Celery available
```

---

### Test 2: Region Auto-Detection

```bash
python3 -c "from celery_config import get_celery_config; print(f'Region: {get_celery_config()[\"aws_region\"]}')"
```

**Expected**: Detects your AWS CLI default region (e.g., us-east-1)

---

### Test 3: App Initialization

```bash
export S3_BUCKET_NAME=felix-s3-bucket
export CELERY_RESULT_BACKEND=s3://felix-s3-bucket/tara/celery-results/

python3 -c "import app; print(f'✅ ENHANCED_MODE: {app.ENHANCED_MODE}'); print(f'✅ CELERY_ENABLED: {app.CELERY_ENABLED}')"
```

**Expected**:
```
✅ ✨ ENHANCED MODE ACTIVATED ✨
   Features enabled:
   • Multi-model fallback (5 models)
   • Extended thinking (Sonnet 4.5)
   ...
✅ ENHANCED_MODE: True
✅ CELERY_ENABLED: True
```

---

## 📊 Technical Details

### Lazy Initialization Pattern

**Why It's Better**:
1. **No import-time errors**: Modules can be imported safely without env vars set
2. **Better error messages**: Failures happen at runtime with context
3. **Testing friendly**: Easy to mock or skip Celery in tests
4. **Flexible**: Can retry initialization if it fails first time

**How It Works**:
```python
# When you access celery_app:
celery_app.delay(...)

# The proxy intercepts and:
1. Checks if _celery_app exists
2. If not, calls init_celery_app()
3. init_celery_app() reads env vars and creates real Celery app
4. Proxy forwards the method call to real app
```

---

### Region Detection Priority

1. **`AWS_REGION` env var** - Highest priority, explicit setting
2. **`AWS_DEFAULT_REGION` env var** - AWS SDK standard
3. **boto3 session** - Reads from `~/.aws/config` or instance metadata
4. **Fallback to us-east-2** - Last resort default

**Why us-east-2?**
- Bedrock models are available
- Lower rate limiting issues than us-east-1
- Good default for new deployments

---

## 🚀 Production Deployment

### App Runner

Environment variables are already set in your deployment. No changes needed!

The lazy initialization ensures Celery only initializes when actually used.

---

### ECS Fargate / EC2

Update your task definition or environment file with:

```bash
CELERY_RESULT_BACKEND=s3://felix-s3-bucket/tara/celery-results/
AWS_REGION=us-east-2  # Or your preferred region
S3_BUCKET_NAME=felix-s3-bucket
S3_BASE_PATH=tara/
```

---

## 📝 Summary of Benefits

### Before This Fix:
- ❌ App crashed on startup without env vars
- ❌ Required manual region configuration
- ❌ Chat functionality broken (missing function)
- ❌ Confusing error messages
- ❌ Testing difficult

### After This Fix:
- ✅ Graceful degradation if Celery unavailable
- ✅ Auto-detects region from AWS CLI profile
- ✅ Chat functionality works properly
- ✅ Clear error messages with fix instructions
- ✅ Easy to test and develop locally
- ✅ Startup script handles all configuration
- ✅ Production deployments unaffected

---

## 🔗 Related Documentation

- **[LOCAL_DEVELOPMENT_GUIDE.md](LOCAL_DEVELOPMENT_GUIDE.md)** - Complete local setup guide
- **[QUICK_FIX_CELERY_ERROR.md](QUICK_FIX_CELERY_ERROR.md)** - Quick reference for this error
- **[DEPLOYMENT_MASTER_GUIDE.md](DEPLOYMENT_MASTER_GUIDE.md)** - Production deployment guide
- **[.env.example](.env.example)** - Environment variable template

---

## ✅ Checklist for Users

- [x] Celery lazy initialization implemented
- [x] Multi-region support added
- [x] Chat task function fixed
- [x] Startup script created
- [x] Environment template created
- [x] All tests passing
- [x] Documentation complete
- [ ] User tests local development
- [ ] User deploys to production

---

**Version**: 2.0
**Last Updated**: November 19, 2025
**Status**: ✅ Production Ready
**Backwards Compatible**: Yes (existing deployments work without changes)
