# 🔧 DEPLOY FIXES - S3 & Claude API Not Working

## ❌ Current Problem

Your logs show the **OLD code is still deployed**:

```
⚠️ S3 bucket 'felix-s3-bucket' not accessible: An error occurred (403) when calling the HeadBucket operation: Forbidden
📝 S3 export will use local fallback.
• AWS Credentials: ❌ Not configured
```

**The code is still using the hardcoded old bucket name `felix-s3-bucket` instead of reading from environment variables!**

---

## ✅ Fixes Ready

I've fixed the code in these files:
- **utils/s3_export_manager.py** - Now reads `S3_BUCKET_NAME`, `S3_BASE_PATH`, `S3_REGION` from environment
- **app.py** - Fixed region fallback (`us-east-2` → `eu-north-1`)
- **app.py** - Added environment variable debugging

**Deployment package created:** `ai-prism-eb-FIXED-S3-CLAUDE.zip` (464 KB)

---

## 🚀 DEPLOY NOW (2 Options)

### **Option 1: Automated Deployment Script (Recommended)**

```bash
cd "/Users/abhsatsa/Documents/risk stuff/tool/tara2"

./DEPLOY_FIX_NOW.sh
```

This will:
1. Upload the zip to S3
2. Create new application version
3. Deploy to your environment
4. Take 5-10 minutes

### **Option 2: Manual via AWS Console**

1. Go to: https://eu-north-1.console.aws.amazon.com/elasticbeanstalk
2. Click your environment (the one with URL `ai-prisms.eu-north-1.elasticbeanstalk.com`)
3. Click: **"Upload and deploy"**
4. Upload: `ai-prism-eb-FIXED-S3-CLAUDE.zip`
5. Version label: `fixed-s3-claude-v1`
6. Click: **"Deploy"**
7. Wait 10-15 minutes

---

## 🔍 After Deployment - Verify

### **Test 1: Check Logs**

Wait 5 minutes after deployment, then check logs. You should see:

**BEFORE (Current - Wrong):**
```
✅ Local environment - using AWS CLI credentials
⚠️ S3 bucket 'felix-s3-bucket' not accessible
📝 S3 export will use local fallback
```

**AFTER (Fixed - Correct):**
```
✅ AWS environment detected - using IAM role credentials
   S3 Bucket: ai-prism-logs-600222957378-eu
   S3 Region: eu-north-1
   Base Path: Logs and data/
✅ S3 connection established to bucket: ai-prism-logs-600222957378-eu
```

### **Test 2: S3 Connection Test**

Visit: http://ai-prisms.eu-north-1.elasticbeanstalk.com

Click "S3 Connection Test" button

**Should show:**
```json
{
  "s3_status": {
    "connected": true,
    "bucket_accessible": true,
    "bucket_name": "ai-prism-logs-600222957378-eu",
    "region": "eu-north-1",
    "base_path": "Logs and data/",
    "credentials_source": "IAM Role (Elastic Beanstalk)",
    "environment_variables": {
      "S3_BUCKET_NAME": "ai-prism-logs-600222957378-eu",
      "S3_REGION": "eu-north-1",
      "AWS_REGION": "eu-north-1",
      "FLASK_ENV": "production"
    }
  }
}
```

### **Test 3: Document Analysis**

1. Upload a test document
2. Click "Analyze Document"
3. Should work without errors

### **Test 4: Chat**

1. Go to Chat tab
2. Send a message
3. Claude should respond

---

## 📊 What Changed

| File | Change | Why |
|------|--------|-----|
| utils/s3_export_manager.py | Read S3_BUCKET_NAME from env | Was hardcoded to 'felix-s3-bucket' |
| utils/s3_export_manager.py | Read S3_BASE_PATH from env | Was hardcoded to 'tara/' |
| utils/s3_export_manager.py | Read S3_REGION from env | Wasn't reading from environment |
| utils/s3_export_manager.py | Detect Elastic Beanstalk | Was only detecting App Runner |
| app.py | Fix region fallback | us-east-2 → eu-north-1 |
| app.py | Add env var debugging | Show all environment variables |

---

## ⏱️ Timeline

| Step | Time | What Happens |
|------|------|--------------|
| 1. Run deployment script | 0:00 | Upload to S3 |
| 2. Create version | 0:30 | Register new version |
| 3. Start deployment | 1:00 | Begin rolling update |
| 4. Update instances | 5:00 | Install new code on instances |
| 5. Restart workers | 8:00 | Restart Gunicorn with new code |
| 6. **Deployment complete** | **10:00** | ✅ **Ready to test** |

---

## 🆘 If Deployment Fails

**Check deployment events:**
```bash
aws elasticbeanstalk describe-events \
    --environment-name ai-prisms \
    --region eu-north-1 \
    --max-items 20 \
    --query 'Events[].[EventDate,Severity,Message]' \
    --output table
```

**Check environment status:**
```bash
aws elasticbeanstalk describe-environments \
    --environment-names ai-prisms \
    --region eu-north-1 \
    --query 'Environments[0].[Status,Health,HealthStatus]' \
    --output table
```

**Common issues:**
- **Status: Updating** → Wait, deployment in progress
- **Health: Warning** → Normal during deployment
- **Health: Degraded** → Check Events tab for errors

---

## 📚 Documentation

- **[URGENT_FIX_S3_AND_CLAUDE.md](URGENT_FIX_S3_AND_CLAUDE.md)** - Complete fix details
- **[FIX_ENVIRONMENT_VARIABLES.md](FIX_ENVIRONMENT_VARIABLES.md)** - How to apply env vars
- **[DEPLOY_FIX_NOW.sh](DEPLOY_FIX_NOW.sh)** - Automated deployment script

---

## 🎯 Quick Start

**Just run this command:**

```bash
cd "/Users/abhsatsa/Documents/risk stuff/tool/tara2" && ./DEPLOY_FIX_NOW.sh
```

Then wait 10 minutes and test! 🚀
