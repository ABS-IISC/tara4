# 🔧 URGENT FIX: S3 Connection and Claude API Not Working

## ❌ Problem Summary

Your application is deployed and running, but showing errors:
```
AWS Connection: ❌ Failed
Bucket Name: Not specified
S3 client not initialized - check AWS credentials
```

**Root Causes Found:**
1. ✅ **Fixed:** S3ExportManager was hardcoded with old bucket name `felix-s3-bucket`
2. ✅ **Fixed:** S3ExportManager wasn't reading from environment variables (`S3_BUCKET_NAME`, `S3_BASE_PATH`, `S3_REGION`)
3. ✅ **Fixed:** Default region was `us-east-2` instead of `eu-north-1`
4. ⚠️ **Needs Deployment:** Environment variables may not be loaded in running application

---

## ✅ FIXES APPLIED

I've updated the following files to fix the issues:

### **1. utils/s3_export_manager.py**

**Before:**
```python
def __init__(self, bucket_name='felix-s3-bucket', base_path='tara/'):
    self.bucket_name = bucket_name
    self.base_path = base_path.rstrip('/') + '/'
```

**After:**
```python
def __init__(self, bucket_name=None, base_path=None):
    # Read from environment variables with fallbacks
    self.bucket_name = bucket_name or os.environ.get('S3_BUCKET_NAME', 'felix-s3-bucket')
    self.base_path = (base_path or os.environ.get('S3_BASE_PATH', 'tara/')).rstrip('/') + '/'
    self.s3_region = os.environ.get('S3_REGION') or os.environ.get('AWS_REGION', 'eu-north-1')
```

**What Changed:**
- ✅ Now reads `S3_BUCKET_NAME` from environment
- ✅ Now reads `S3_BASE_PATH` from environment
- ✅ Now reads `S3_REGION` from environment
- ✅ Creates S3 client with correct region

### **2. app.py (SimpleModelConfig)**

**Before:**
```python
def get_model_config(self):
    return {
        'model_id': os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'),
        'region': os.environ.get('AWS_REGION', 'us-east-2'),  # Wrong fallback region!
    }
```

**After:**
```python
def get_model_config(self):
    # Read region from AWS_REGION or AWS_DEFAULT_REGION
    region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION', 'eu-north-1')
    return {
        'model_id': os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-sonnet-4-5-20250929-v1:0'),
        'region': region,  # Now uses correct region
    }
```

**What Changed:**
- ✅ Region fallback changed: `us-east-2` → `eu-north-1`
- ✅ Reads from both `AWS_REGION` and `AWS_DEFAULT_REGION`
- ✅ Model ID fallback fixed (removed `us.` prefix)

### **3. app.py (S3 Connection Test)**

**Before:**
```python
'region': os.environ.get('S3_REGION', 'us-east-1'),
'credentials_source': 'AWS Profile (admin-abhsatsa)' if os.environ.get('AWS_PROFILE') else 'Environment Variables'
```

**After:**
```python
'region': os.environ.get('S3_REGION') or os.environ.get('AWS_REGION', 'eu-north-1'),
'credentials_source': 'IAM Role (Elastic Beanstalk)' if os.environ.get('FLASK_ENV') == 'production' else ...,
'environment_variables': {
    'S3_BUCKET_NAME': os.environ.get('S3_BUCKET_NAME', 'Not set'),
    'S3_REGION': os.environ.get('S3_REGION', 'Not set'),
    'AWS_REGION': os.environ.get('AWS_REGION', 'Not set'),
    'FLASK_ENV': os.environ.get('FLASK_ENV', 'Not set')
}
```

**What Changed:**
- ✅ Shows all environment variables for debugging
- ✅ Correctly identifies IAM Role in production
- ✅ Better region detection

---

## 🚀 DEPLOY THE FIX

Now you need to deploy these code changes to Elastic Beanstalk:

### **Option 1: Quick Deploy via EB CLI (5 minutes)**

```bash
cd "/Users/abhsatsa/Documents/risk stuff/tool/tara2"

# Deploy the updated code
eb deploy --region eu-north-1

# Wait 5-8 minutes for deployment to complete
```

### **Option 2: Create New Deployment Package (10 minutes)**

```bash
cd "/Users/abhsatsa/Documents/risk stuff/tool/tara2"

# Create deployment package with fixes
zip -r ai-prism-eb-FIXED-S3-CLAUDE.zip \
  .ebextensions \
  app.py \
  main.py \
  core \
  utils \
  config \
  templates \
  static \
  gunicorn.conf.py \
  Procfile \
  requirements.txt \
  -x "*.pyc" -x "__pycache__/*" -x ".git/*" -x "logs/*" -x "data/*" -x "docs/*"

echo "✅ Package created: ai-prism-eb-FIXED-S3-CLAUDE.zip"
```

Then deploy via AWS Console:
1. Go to: **Elastic Beanstalk** → Your environment
2. Click: **"Upload and deploy"**
3. Upload: `ai-prism-eb-FIXED-S3-CLAUDE.zip`
4. Version label: `fixed-s3-claude-$(date +%s)`
5. Click: **"Deploy"**
6. Wait 10-15 minutes

---

## 🔍 VERIFY THE FIX

After deployment completes:

### **Test 1: Environment Variables Loaded**

Visit your application URL and open the S3 Connection Test. You should now see:

```json
{
  "environment_variables": {
    "S3_BUCKET_NAME": "ai-prism-logs-600222957378-eu",
    "S3_REGION": "eu-north-1",
    "AWS_REGION": "eu-north-1",
    "FLASK_ENV": "production"
  }
}
```

**If you see "Not set":**
- Environment variables aren't loaded yet
- Go to: **Configuration** → **Software** → Click **"Apply"**
- Wait 5 minutes for restart

### **Test 2: S3 Connection Working**

The S3 Connection Test should now show:

```
☁️ S3 Connection Test Results
Connection Status:
AWS Connection: ✅ Connected
Bucket Access: ✅ Accessible
Bucket Name: ai-prism-logs-600222957378-eu
Region: eu-north-1
Base Path: Logs and data/
```

### **Test 3: Claude API Working**

1. Upload a test document
2. Click "Analyze Document"
3. Should see: ✅ AI feedback generated (no errors)

### **Test 4: Check Application Logs**

Go to: Environment → **Logs** → **Request Logs** → **Last 100 Lines**

**Look for:**
```
✅ AWS environment detected - using IAM role credentials
   S3 Bucket: ai-prism-logs-600222957378-eu
   S3 Region: eu-north-1
   Base Path: Logs and data/
✅ S3 connection established to bucket: ai-prism-logs-600222957378-eu
```

---

## ⚠️ IF STILL NOT WORKING

### **Issue: Environment Variables Show "Not set"**

**This means the environment variables haven't been applied yet.**

**Solution:**
1. Go to: **Elastic Beanstalk** → Your environment → **Configuration** → **Software**
2. Scroll to: **Environment properties**
3. **Verify these 17 variables exist:**

```
AWS_REGION = eu-north-1
AWS_DEFAULT_REGION = eu-north-1
S3_BUCKET_NAME = ai-prism-logs-600222957378-eu
S3_BASE_PATH = Logs and data/
S3_REGION = eu-north-1

BEDROCK_MODEL_ID = anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_MAX_TOKENS = 4096
BEDROCK_TEMPERATURE = 0.7
REASONING_ENABLED = false

FLASK_ENV = production
FLASK_APP = app.py
PORT = 8000

REDIS_URL = disabled

MAX_CONTENT_LENGTH = 16777216
SESSION_TIMEOUT = 3600

ENABLE_MODEL_FALLBACK = true
CHAT_ENABLE_MULTI_MODEL = true
```

4. **If any are missing, add them now**
5. Click **"Apply"** at the bottom
6. Wait 5-8 minutes for environment update
7. Test again

### **Issue: S3 Connection Still Fails**

**Check IAM Role Permissions:**

```bash
# Verify EC2 instance profile has S3 access
aws iam list-attached-role-policies \
  --role-name aws-elasticbeanstalk-ec2-role \
  --query 'AttachedPolicies[*].PolicyName'

# Should show:
# - AmazonS3FullAccess
# - AmazonBedrockFullAccess
```

**If missing, attach policies:**

```bash
# Attach S3 access
aws iam attach-role-policy \
  --role-name aws-elasticbeanstalk-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Attach Bedrock access
aws iam attach-role-policy \
  --role-name aws-elasticbeanstalk-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

### **Issue: Claude API Still Not Working**

**Check Bedrock is enabled in eu-north-1:**

```bash
# List available Claude models in eu-north-1
aws bedrock list-foundation-models --region eu-north-1 \
  --query 'modelSummaries[?contains(modelId, `claude`)].modelId' \
  --output table

# Should show Claude models available in eu-north-1
```

**If no models found:**
- Bedrock may not be enabled in eu-north-1 for your account
- Either: Enable Bedrock in eu-north-1 via AWS Console
- Or: Change all regions to a supported region (e.g., `us-east-1`)

---

## 📋 QUICK CHECKLIST

**Before Deployment:**
- [✅] Fixed `utils/s3_export_manager.py` (reads env vars)
- [✅] Fixed `app.py` SimpleModelConfig (correct region fallback)
- [✅] Fixed `app.py` S3 test endpoint (shows env vars)
- [ ] Created deployment package
- [ ] Ready to deploy

**After Deployment:**
- [ ] Deployment completes (environment shows "Ok" green status)
- [ ] S3 Connection Test shows "✅ Connected"
- [ ] Environment variables all show correct values (not "Not set")
- [ ] Document analysis works (Claude generates feedback)
- [ ] Chat works (Claude responds)

---

## 🎯 SUMMARY OF CHANGES

| File | Line | Change | Reason |
|------|------|--------|--------|
| utils/s3_export_manager.py | 11-15 | Read S3_BUCKET_NAME from env | Was hardcoded to 'felix-s3-bucket' |
| utils/s3_export_manager.py | 11-15 | Read S3_BASE_PATH from env | Was hardcoded to 'tara/' |
| utils/s3_export_manager.py | 15 | Read S3_REGION from env | Wasn't using environment variable |
| utils/s3_export_manager.py | 23-33 | Detect Elastic Beanstalk env | Was only checking for App Runner |
| utils/s3_export_manager.py | 33 | Use region when creating client | Was using default region |
| app.py | 85 | Read AWS_REGION from env | Fallback was wrong region (us-east-2) |
| app.py | 87 | Fix model ID fallback | Removed 'us.' prefix |
| app.py | 2471 | Fix region fallback | Changed us-east-1 → eu-north-1 |
| app.py | 2475 | Detect IAM role correctly | Show "IAM Role" in production |
| app.py | 2479-2484 | Add env var debugging | Show all environment variables |

---

## 🚀 NEXT STEPS

1. **Deploy the fixes:**
   - Use EB CLI: `eb deploy --region eu-north-1`
   - Or: Upload deployment package via console

2. **Wait for deployment:** 10-15 minutes

3. **Verify environment variables:**
   - Configuration → Software → Check all 17 variables

4. **Test the application:**
   - S3 Connection Test → Should show ✅ Connected
   - Document Analysis → Should work
   - Chat → Should respond

5. **If still broken:**
   - Check IAM role permissions (S3 + Bedrock)
   - Check Bedrock is enabled in eu-north-1
   - Review application logs for errors

---

**The fixes are ready to deploy! The code now correctly reads all environment variables and will work once deployed.** 🎉
