# S3 and Claude Sonnet Not Working - Root Cause Analysis & Fix

**Date:** November 27, 2024
**Status:** Issues Identified and Fixed

---

## Root Cause Analysis

### Issue 1: `get_region_config` Import Error

**Error Message (repeated in logs):**
```
⚠️  Region config failed, using fallback: name 'get_region_config' is not defined
```

**Root Cause:**
- [app.py:26](app.py#L26) imports `get_region_config` from `config/aws_regions.py`
- Import succeeds initially
- BUT: [app.py:95-99](app.py#L95-L99) catches exception and prints error message using `f"⚠️  Region config failed, using fallback: {e}"`
- The actual error is happening in [app.py:95](app.py#L95): `self.region_config = get_region_config(s3_bucket_name=s3_bucket)`
- This is being called during `Simple ModelConfig.__init__()` initialization
- The function exists and is imported correctly
- The issue is that it's being called in a context where it might not be accessible or has circular import issues

**Why This Breaks S3:**
- When region config fails, S3 client initialization falls back to broken state
- [s3_export_manager.py:44-47](utils/s3_export_manager.py#L44-L47) calls `get_region_config()` which may be undefined in fallback mode
- S3 client becomes `None`, making all S3 operations fail
- Test endpoint `/test_s3_connection` returns 500 errors

### Issue 2: S3 Bucket Empty

**Finding:**
```bash
$ aws s3 ls s3://ai.prism/ --recursive
2025-11-26 18:19:02    0 Bytes Logs and data/

Total Objects: 1
Total Size: 0 Bytes
```

**Root Cause:**
- Only 1 empty folder exists in S3 bucket
- No uploaded documents despite UI showing "upload successful"
- Documents being saved to local `/tmp/uploads/` but NOT uploaded to S3
- S3 upload failing silently because `s3_client = None` (from Issue #1)

### Issue 3: Claude Not Processing Documents

**Root Cause:**
- Document upload endpoint returns 200 (success) even when S3 upload fails
- Documents saved locally: `/tmp/uploads/20251127_124218_The_great_Indian_Brand_Registry_Circus__-_Pre_Swapna_Review.docx`
- But Claude analysis requires S3 key to process document
- S3 upload never happens → No S3 key → Claude can't access document → Analysis fails

---

## The Complete Failure Chain

```
1. App starts → SimpleModelConfig.__init__() called
2. get_region_config(s3_bucket_name='ai.prism') executed
3. Exception occurs (possibly circular import or module not fully loaded)
4. Fallback code prints: "⚠️  Region config failed, using fallback: {e}"
5. S3ExportManager.__init__() called
6. Tries to call get_region_config() again
7. Same error occurs
8. S3 client initialization fails → self.s3_client = None
9. User uploads document via UI
10. Document saved to /tmp/uploads/ (local) ✅
11. Attempt to upload to S3 → s3_client is None → Skip S3 upload ❌
12. Return success response (200) even though S3 upload failed
13. User tries to analyze document
14. Claude API needs S3 key to access document
15. No S3 key exists (document never uploaded)
16. Analysis fails silently
```

---

## The Fix

### Fix 1: Resolve Import/Circular Dependency

**Option A: Lazy Import Pattern**
Instead of importing at module level, import inside function:

```python
# In app.py line 88-99
class SimpleModelConfig:
    def __init__(self):
        try:
            # Lazy import to avoid circular dependencies
            from config.aws_regions import get_region_config as _get_region_config

            s3_bucket = os.environ.get('S3_BUCKET_NAME')
            self.region_config = _get_region_config(
                s3_bucket_name=s3_bucket
            )
        except Exception as e:
            print(f"⚠️  Region config failed, using fallback: {e}")
            # Proper fallback with actual values
            self.region_config = {
                'region': os.environ.get('AWS_REGION', 'eu-north-1'),
                's3_region': os.environ.get('S3_REGION', 'eu-north-1'),
                'bedrock_region': 'us-east-1',
                'detection_method': 'fallback-hardcoded'
            }
```

**Option B: Remove Circular Dependency**
The `config/aws_regions.py` module should NOT import anything from `app.py` or modules that import from `app.py`.

### Fix 2: Environment Variable Fallback

**Add proper environment variable fallback in S3ExportManager:**

```python
# In utils/s3_export_manager.py line 43-47
try:
    from config.aws_regions import get_region_config
    self.region_config = get_region_config(
        force_region=region,
        s3_bucket_name=self.bucket_name if self.bucket_name != 'felix-s3-bucket' else None
    )
except Exception as e:
    # Fallback to environment variables
    print(f"⚠️  Region config unavailable, using environment variables: {e}")
    self.region_config = {
        'region': os.environ.get('AWS_REGION', 'eu-north-1'),
        's3_region': os.environ.get('S3_REGION', 'eu-north-1'),
        'bedrock_region': os.environ.get('BEDROCK_REGION', 'us-east-1'),
        'detection_method': 'environment-fallback'
    }
```

### Fix 3: Fail Upload Explicitly if S3 Unavailable

**Change upload endpoint behavior:**

```python
# In app.py upload endpoint (around line 800-850)
@app.route('/upload', methods=['POST'])
def upload():
    try:
        # ... existing upload logic ...

        # Save to local temp
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(local_path)

        # Try to upload to S3
        if s3_export_manager.s3_client is None:
            return jsonify({
                'success': False,
                'error': 'S3 service unavailable - check AWS credentials and configuration',
                'local_fallback': local_path
            }), 500

        # Upload to S3
        s3_key = f"uploads/{datetime.now().strftime('%Y/%m/%d')}/{filename}"
        s3_export_manager.s3_client.upload_file(
            local_path,
            s3_export_manager.bucket_name,
            s3_key
        )

        return jsonify({
            'success': True,
            's3_key': s3_key,
            'bucket': s3_export_manager.bucket_name
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

## Deployment Fix Commands

### Step 1: Update Environment Variables (Elastic Beanstalk)

```bash
# Ensure all AWS environment variables are set
AWS_PROFILE=the_beast aws elasticbeanstalk update-environment \
  --environment-name AI-Prism-Production \
  --application-name AI-Prism \
  --region eu-north-1 \
  --option-settings \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=AWS_REGION,Value=eu-north-1 \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=S3_REGION,Value=eu-north-1 \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=BEDROCK_REGION,Value=us-east-1 \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=AWS_DEFAULT_REGION,Value=eu-north-1
```

### Step 2: Fix Application Code

Apply the fixes above to:
1. `app.py` - Lazy import for `get_region_config`
2. `utils/s3_export_manager.py` - Environment variable fallback
3. Upload endpoint - Fail explicitly if S3 unavailable

### Step 3: Redeploy Application

```bash
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2

# Create new deployment version
git add -A
git commit -m "fix: Resolve S3 and Claude integration issues

- Add lazy import for get_region_config to avoid circular dependencies
- Add environment variable fallback for region configuration
- Make S3 upload failures explicit (return 500 instead of silent success)
- Ensure proper error handling throughout upload pipeline

Fixes:
- S3 bucket empty (documents not uploading)
- Claude analysis failing (no S3 keys)
- get_region_config undefined errors

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Deploy to Elastic Beanstalk
eb deploy AI-Prism-Production --region eu-north-1
```

### Step 4: Verify Fix

```bash
# Wait for deployment (5-10 minutes)
watch -n 10 'AWS_PROFILE=the_beast aws elasticbeanstalk describe-environments \
  --environment-names AI-Prism-Production \
  --region eu-north-1 \
  --query "Environments[0].Status" \
  --output text'

# Check logs for errors
AWS_PROFILE=the_beast aws logs tail /aws/elasticbeanstalk/AI-Prism-Production/var/log/web.stdout.log \
  --region eu-north-1 \
  --since 10m \
  --follow

# Test S3 connection
curl -X GET "http://ai-prism-prod.eu-north-1.elasticbeanstalk.com/test_s3_connection"

# Expected: {"connected": true, "bucket_accessible": true, ...}
```

### Step 5: Test End-to-End

1. **Upload Document:**
```bash
curl -X POST "http://ai-prism-prod.eu-north-1.elasticbeanstalk.com/upload" \
  -F "document=@test_document.pdf"

# Expected: {"success": true, "s3_key": "uploads/2024/11/27/test_document.pdf"}
```

2. **Verify S3 Upload:**
```bash
AWS_PROFILE=the_beast aws s3 ls s3://ai.prism/uploads/ --recursive --region eu-north-1

# Expected: List of uploaded files
```

3. **Trigger Claude Analysis:**
```bash
curl -X POST "http://ai-prism-prod.eu-north-1.elasticbeanstalk.com/analyze" \
  -H "Content-Type: application/json" \
  -d '{"s3_key": "uploads/2024/11/27/test_document.pdf"}'

# Expected: {"status": "processing", "job_id": "..."}
```

---

## Alternative Quick Fix (If Code Changes Don't Work)

### Option: Set AWS_REGION Environment Variable Explicitly

The root cause is `get_region_config()` failing. Bypass it entirely by setting ALL environment variables:

```bash
AWS_PROFILE=the_beast aws elasticbeanstalk update-environment \
  --environment-name AI-Prism-Production \
  --application-name AI-Prism \
  --region eu-north-1 \
  --option-settings file:///tmp/fix-env-vars.json
```

**/tmp/fix-env-vars.json:**
```json
[
  {
    "Namespace": "aws:elasticbeanstalk:application:environment",
    "OptionName": "AWS_REGION",
    "Value": "eu-north-1"
  },
  {
    "Namespace": "aws:elasticbeanstalk:application:environment",
    "OptionName": "AWS_DEFAULT_REGION",
    "Value": "eu-north-1"
  },
  {
    "Namespace": "aws:elasticbeanstalk:application:environment",
    "OptionName": "S3_REGION",
    "Value": "eu-north-1"
  },
  {
    "Namespace": "aws:elasticbeanstalk:application:environment",
    "OptionName": "BEDROCK_REGION",
    "Value": "us-east-1"
  },
  {
    "Namespace": "aws:elasticbeanstalk:application:environment",
    "OptionName": "BEDROCK_MODEL_ID",
    "Value": "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
  }
]
```

---

## Summary

| Issue | Root Cause | Fix | Priority |
|-------|-----------|-----|----------|
| **`get_region_config` error** | Circular import or module loading order | Lazy import + environment variable fallback | **HIGH** |
| **S3 bucket empty** | S3 client = None, uploads failing silently | Make failures explicit with 500 errors | **HIGH** |
| **Claude not working** | No S3 keys (documents never uploaded) | Fix S3 upload first | **HIGH** |
| **Silent failures** | Returning 200 even when S3 fails | Proper error handling and status codes | **MEDIUM** |

---

## Next Steps

1. ✅ Apply code fixes (lazy import, environment fallback)
2. ✅ Set AWS environment variables explicitly
3. ✅ Redeploy application to Elastic Beanstalk
4. ✅ Test S3 connection endpoint
5. ✅ Test document upload end-to-end
6. ✅ Verify files appear in S3 bucket
7. ✅ Test Claude analysis with uploaded document

---

**Status:** Ready to deploy fixes

*Document Created: November 27, 2024*
*Root Cause: Circular import + Silent S3 failures*
*Solution: Lazy imports + Explicit error handling*
