# 🔧 FIX: S3 Connection and Claude API Not Working

## ❌ Current Problem

Your application is showing:
```
AWS Connection: ❌ Failed
Bucket Access: ❌ Not accessible
Bucket Name: Not specified
Error: S3 client not initialized - check AWS credentials
```

**Root Cause:** Environment variables were added via console but haven't been applied to the running application yet.

---

## ✅ SOLUTION: Apply Environment Variables and Restart

You need to **restart the application** after adding environment variables. Here are 3 ways to do this:

---

## METHOD 1: Restart App Servers (Fastest - 2 minutes)

### **Via AWS Console:**

1. Go to: https://eu-north-1.console.aws.amazon.com/elasticbeanstalk/home?region=eu-north-1
2. Click on your environment (e.g., **AI-Prism-production** or **AI-Prism1-prod**)
3. On the left sidebar, click **"Configuration"**
4. Scroll to **"Rolling updates and deployments"** section
5. Click **"Edit"**
6. Click **"Apply"** at the bottom (even without changing anything)
7. This will trigger a **rolling restart** of all instances

**Time:** 5-8 minutes (restarts instances one by one)
**Downtime:** None (rolling restart)

### **Via AWS CLI:**

```bash
# Find your environment name
aws elasticbeanstalk describe-environments --region eu-north-1 \
  --query 'Environments[*].[EnvironmentName,Status,Health]' --output table

# Restart application servers (replace with your environment name)
aws elasticbeanstalk restart-app-server \
  --environment-name YOUR-ENVIRONMENT-NAME \
  --region eu-north-1
```

**Expected Output:**
```
Environment update initiated successfully
```

---

## METHOD 2: Deploy New Version (Recommended - 10 minutes)

This ensures environment variables are properly loaded:

### **Step 1: Verify Environment Variables in Console**

1. Go to: **Elastic Beanstalk** → Your environment → **Configuration** → **Software**
2. Scroll down to **"Environment properties"**
3. **Verify these 17 variables exist:**

```
AWS_REGION = eu-north-1
AWS_DEFAULT_REGION = eu-north-1
BEDROCK_MODEL_ID = anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_MAX_TOKENS = 4096
BEDROCK_TEMPERATURE = 0.7
REASONING_ENABLED = false

S3_BUCKET_NAME = ai-prism-logs-600222957378-eu
S3_BASE_PATH = Logs and data/
S3_REGION = eu-north-1

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

### **Step 2: Wait for Environment Update**

After clicking "Apply":
- Status will change to **"Warning"** (orange) - this is normal
- Wait 5-8 minutes for instances to restart
- Status will change back to **"Ok"** (green)

### **Step 3: Verify Variables Are Loaded**

After the update completes:
1. Visit your application URL
2. Click **"S3 Connection Test"** button
3. You should now see:
```
AWS Connection: ✅ Connected
Bucket Access: ✅ Accessible
Bucket Name: ai-prism-logs-600222957378-eu
Region: eu-north-1
```

---

## METHOD 3: Redeploy Application (If Methods 1-2 Don't Work)

If environment variables still aren't loading, redeploy the application:

### **Option A: Redeploy Same Version**

1. Go to: **Elastic Beanstalk** → Your environment
2. Click **"Upload and deploy"**
3. Select the existing version (e.g., `production-100users-v1`)
4. Click **"Deploy"**
5. Wait 10-15 minutes

### **Option B: Deploy Fresh Package**

Use the CLI to deploy:

```bash
cd "/Users/abhsatsa/Documents/risk stuff/tool/tara2"

# Create new deployment package
zip -r ai-prism-eb-FIXED-ENVVARS.zip \
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
  -x "*.pyc" -x "__pycache__/*" -x ".git/*" -x "logs/*" -x "data/*"

# Upload and deploy
aws elasticbeanstalk create-application-version \
  --application-name AI-Prism1 \
  --version-label envvars-fixed-$(date +%s) \
  --source-bundle S3Bucket="elasticbeanstalk-eu-north-1-600222957378",S3Key="ai-prism-eb-FIXED-ENVVARS.zip" \
  --region eu-north-1

# Update environment (replace with your environment name)
aws elasticbeanstalk update-environment \
  --environment-name YOUR-ENVIRONMENT-NAME \
  --version-label envvars-fixed-$(date +%s) \
  --region eu-north-1
```

---

## 🔍 HOW TO VERIFY IT'S FIXED

### **Test 1: S3 Connection**

1. Visit your application URL
2. Look for **"S3 Connection Test"** section
3. Click **"Test Connection"** button

**Expected Result:**
```
☁️ S3 Connection Test Results
Connection Status:
AWS Connection: ✅ Connected
Bucket Access: ✅ Accessible
Bucket Name: ai-prism-logs-600222957378-eu
Region: eu-north-1
```

### **Test 2: Document Analysis**

1. Upload a test document (.docx or .txt)
2. Click **"Analyze Document"**
3. Wait 10-30 seconds

**Expected Result:**
- Progress bar appears
- Claude AI feedback is generated
- No errors about "Bedrock not initialized"

### **Test 3: Chat Feature**

1. Go to **Chat** tab
2. Type a message: "Hello, can you help me?"
3. Press Enter

**Expected Result:**
- Claude responds within 5-10 seconds
- No errors about "API not configured"

### **Test 4: Check Application Logs**

**Via AWS Console:**
1. Go to: Environment → **Logs** → **Request Logs** → **Last 100 Lines**
2. Look for these lines:

```
✅ GOOD - Variables loaded:
AWS region: eu-north-1
S3 bucket: ai-prism-logs-600222957378-eu
Bedrock model: anthropic.claude-sonnet-4-5-20250929-v1:0

❌ BAD - Variables missing:
AWS region: None
S3 bucket: None
Bedrock model: None
```

**Via SSH to instance:**
```bash
# SSH to instance
eb ssh YOUR-ENVIRONMENT-NAME --region eu-north-1

# Check environment variables
sudo su webapp
echo $AWS_REGION
echo $S3_BUCKET_NAME
echo $BEDROCK_MODEL_ID

# Should print:
# eu-north-1
# ai-prism-logs-600222957378-eu
# anthropic.claude-sonnet-4-5-20250929-v1:0
```

---

## 🐛 TROUBLESHOOTING

### **Issue: Environment Variables Still Not Loading**

**Possible Causes:**

1. **Variables added to wrong section**
   - Must be in: **Configuration** → **Software** → **Environment properties**
   - NOT in: **.ebextensions** file (those are defaults)

2. **Variables not saved**
   - Make sure you clicked **"Apply"** after adding variables
   - Wait for environment update to complete (green "Ok" status)

3. **Application caching old values**
   - Some Flask apps cache environment variables
   - Solution: Restart app servers (Method 1)

4. **IAM role missing permissions**
   - EC2 instance profile needs: `AmazonBedrockFullAccess`, `AmazonS3FullAccess`
   - Verify at: IAM → Roles → `aws-elasticbeanstalk-ec2-role` → Permissions

### **Issue: S3 Connection Works but Claude API Doesn't**

**Check Bedrock Access:**

```bash
# Via CLI
aws bedrock list-foundation-models --region eu-north-1 \
  --query 'modelSummaries[?contains(modelId, `claude-sonnet-4-5`)].modelId'

# Should return:
# [
#   "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
#   "anthropic.claude-sonnet-4-5-20250929-v1:0"
# ]
```

**Verify IAM Permissions:**
```bash
# Check if EC2 role has Bedrock access
aws iam list-attached-role-policies \
  --role-name aws-elasticbeanstalk-ec2-role \
  --query 'AttachedPolicies[*].PolicyName'

# Should include:
# - AmazonBedrockFullAccess
# - AmazonS3FullAccess
```

### **Issue: Still Getting "S3 client not initialized"**

**This means app.py isn't reading environment variables.**

**Check app.py initialization:**

```python
# In app.py, look for:
AWS_REGION = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID')

# Add debug logging:
import logging
logging.info(f"AWS_REGION loaded: {AWS_REGION}")
logging.info(f"S3_BUCKET_NAME loaded: {S3_BUCKET_NAME}")
logging.info(f"BEDROCK_MODEL_ID loaded: {BEDROCK_MODEL_ID}")
```

**If all show None:**
1. Environment variables aren't being passed to the application
2. Try Method 2 (Deploy New Version) or Method 3 (Redeploy)

---

## 📋 QUICK CHECKLIST

**Before Restarting:**
- [ ] 17 environment variables added in **Software Configuration**
- [ ] Clicked **"Apply"** and waited for update
- [ ] Environment status is **"Ok"** (green)

**After Restarting:**
- [ ] S3 Connection Test shows **✅ Connected**
- [ ] Document analysis works (Claude generates feedback)
- [ ] Chat works (Claude responds to messages)
- [ ] Application logs show environment variables loaded

**If Still Not Working:**
- [ ] Verified IAM role has Bedrock + S3 permissions
- [ ] Checked Bedrock is enabled in eu-north-1
- [ ] Reviewed application logs for errors
- [ ] Tried redeploying the application

---

## 🎯 EXPECTED TIMELINE

| Action | Time | Downtime |
|--------|------|----------|
| Method 1: Restart App Servers | 2-5 min | None |
| Method 2: Apply Config Changes | 5-8 min | None |
| Method 3: Redeploy Application | 10-15 min | None (rolling) |

All methods use **rolling updates** - no downtime!

---

## 📞 NEXT STEPS

1. **Start with Method 1** (Restart App Servers) - fastest
2. **If that doesn't work, try Method 2** (Apply Config Changes)
3. **If still broken, use Method 3** (Redeploy Application)
4. **Verify using Test 1-4** after each attempt

Once environment variables are loaded, your application will:
- ✅ Connect to S3 bucket
- ✅ Use Claude Sonnet 4.5 via Bedrock
- ✅ Process documents and generate AI feedback
- ✅ Enable chat functionality

---

**TIP:** The most common fix is Method 2 - just click "Apply" in Software Configuration even if nothing changed. This triggers a proper environment variable reload.
