# ✅ AWS App Runner Deployment Checklist

**Use this checklist to ensure successful deployment**

---

## 📋 Pre-Deployment (Do This First)

### **1. Code Preparation**

- [ ] All code committed to Git
- [ ] Latest V2 changes included (commit f4672d5+)
- [ ] `core/model_manager_v2.py` exists
- [ ] `requirements.txt` up to date
- [ ] Code tested locally

**Verify:**
```bash
# Check V2 file exists
ls -la core/model_manager_v2.py

# Check git status
git status

# Test locally
python app.py
# Open http://localhost:8080
```

---

### **2. AWS Account Setup**

- [ ] AWS account active
- [ ] Bedrock access enabled in your region
- [ ] Claude models available (us-east-1 recommended)
- [ ] IAM permissions to create App Runner services

**Verify:**
```bash
# Check Bedrock model access
aws bedrock list-foundation-models --region us-east-1 | grep claude

# Should see:
# - anthropic.claude-3-5-sonnet-20240620-v1:0
# - anthropic.claude-3-sonnet-20240229-v1:0
# - anthropic.claude-3-haiku-20240307-v1:0
```

---

### **3. IAM Role Creation**

- [ ] Create IAM role for App Runner
- [ ] Add Bedrock invoke permissions
- [ ] Add S3 permissions (optional)
- [ ] Trust relationship configured

**IAM Role Name:** `AppRunnerTARA2Role`

**Required Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
      ]
    }
  ]
}
```

**Verify:**
```bash
# Check role exists
aws iam get-role --role-name AppRunnerTARA2Role

# Check policy attached
aws iam list-attached-role-policies --role-name AppRunnerTARA2Role
```

---

## 🚀 Deployment Steps

### **Step 1: Create App Runner Service**

- [ ] Navigate to AWS App Runner console
- [ ] Click "Create service"
- [ ] Choose "Source code repository"
- [ ] Connect to GitHub
- [ ] Select your repository
- [ ] Select branch: `main`

---

### **Step 2: Configure Build**

- [ ] Runtime: **Python 3**
- [ ] Build command:
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt
  ```
- [ ] Start command:
  ```bash
  python app.py
  ```

---

### **Step 3: Configure Service**

- [ ] Service name: `tara2-app`
- [ ] Port: `8080`
- [ ] CPU: `1 vCPU` (or `2 vCPU` for > 10 users)
- [ ] Memory: `2 GB` (or `4 GB` for > 10 users)

---

### **Step 4: Set Environment Variables**

**Required (6 variables):**

- [ ] `BEDROCK_MODEL_ID` = `anthropic.claude-3-5-sonnet-20240620-v1:0`
- [ ] `AWS_REGION` = `us-east-1`
- [ ] `BEDROCK_MAX_TOKENS` = `8192`
- [ ] `BEDROCK_TEMPERATURE` = `0.7`
- [ ] `PORT` = `8080`
- [ ] `FLASK_ENV` = `production`

**Optional (recommended):**

- [ ] `BEDROCK_FALLBACK_MODELS` = `anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-sonnet-20240229-v1:0,anthropic.claude-3-haiku-20240307-v1:0`
- [ ] `CHAT_ENABLE_MULTI_MODEL` = `true`

**Copy-paste config:**
```
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
AWS_REGION=us-east-1
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
PORT=8080
FLASK_ENV=production
BEDROCK_FALLBACK_MODELS=anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-sonnet-20240229-v1:0,anthropic.claude-3-haiku-20240307-v1:0
CHAT_ENABLE_MULTI_MODEL=true
```

---

### **Step 5: Configure Security**

- [ ] Instance role: Select `AppRunnerTARA2Role`
- [ ] Encryption: Default (AWS managed)

---

### **Step 6: Configure Auto-Scaling**

- [ ] Min instances: `1`
- [ ] Max instances: `3` (or `5` for > 20 users)
- [ ] Max concurrency: `100`

---

### **Step 7: Configure Health Check**

- [ ] Protocol: `HTTP`
- [ ] Path: `/health`
- [ ] Interval: `10` seconds
- [ ] Timeout: `5` seconds
- [ ] Healthy threshold: `2`
- [ ] Unhealthy threshold: `3`

---

### **Step 8: Deploy**

- [ ] Review all settings
- [ ] Click "Create & Deploy"
- [ ] Wait 5-10 minutes for deployment
- [ ] Status changes to "Running"

---

## ✅ Post-Deployment Verification

### **1. Service Health Check**

- [ ] App Runner status: **Running** (green)
- [ ] Health check: **Passing**
- [ ] No errors in CloudWatch logs

**Verify:**
```bash
# Get service URL from App Runner console
SERVICE_URL="https://your-app.us-east-1.awsapprunner.com"

# Test health endpoint
curl $SERVICE_URL/health

# Expected response:
{
  "status": "healthy",
  "version": "2.0",
  "features": {
    "ai_engine": true,
    "multi_model_v2": true
  }
}
```

---

### **2. V2 Multi-Model Verification**

- [ ] V2 is active
- [ ] Primary model available
- [ ] Fallback models loaded

**Verify:**
```bash
# Check model stats
curl $SERVICE_URL/model_stats

# Expected response:
{
  "version": "V2 (Per-Request Isolation)",  ← Confirms V2!
  "multi_model_enabled": true,
  "stats": {
    "total_models": 4,
    "models": [
      {
        "name": "Claude 3.5 Sonnet (Primary)",
        "status": "available",
        "priority": 1
      }
    ]
  }
}
```

---

### **3. Functional Testing**

**Test 1: Document Upload**

- [ ] Navigate to App Runner URL
- [ ] Upload a test document (.docx)
- [ ] Document processes successfully
- [ ] Sections appear

**Test 2: Section Analysis**

- [ ] Click "Analyze" on a section
- [ ] Analysis completes (< 5 seconds)
- [ ] Feedback items appear
- [ ] No errors in browser console

**Test 3: Full Document Analysis**

- [ ] Click "Analyze All Sections"
- [ ] All sections analyze successfully
- [ ] Stats update correctly
- [ ] Download document works

**Test 4: Chat Feature**

- [ ] Open chat panel
- [ ] Send a test message
- [ ] Response appears (< 5 seconds)
- [ ] Response is relevant

**Test 5: Statistics**

- [ ] View Statistics tab
- [ ] Stats are accurate
- [ ] Charts load correctly

---

### **4. Performance Verification**

- [ ] Response time < 3 seconds (average)
- [ ] No timeout errors
- [ ] No memory errors
- [ ] Auto-scaling works (if load tested)

**Monitor:**
```bash
# CloudWatch Logs
# Check for errors:
/aws/apprunner/tara2-app/*/application

# Look for:
✅ "Multi-model fallback enabled (V2 - Per-Request Isolation)"
✅ "Request abc123 succeeded with Claude 3.5 Sonnet"
❌ No "ERROR" or "Exception" messages
```

---

### **5. Multi-User Testing (Optional)**

**Simulate concurrent users:**

```bash
# Run 10 concurrent requests
for i in {1..10}; do
  curl -X POST $SERVICE_URL/analyze_section \
    -H "Content-Type: application/json" \
    -d "{\"section_name\": \"Test $i\", \"content\": \"Test content\"}" &
done
wait

# Check stats
curl $SERVICE_URL/model_stats
```

**Expected:**
- [ ] All 10 requests complete
- [ ] Most use primary model (> 70%)
- [ ] Success rate > 95%
- [ ] No global blocking observed

---

## 🐛 Troubleshooting

### **Issue: Deployment Failed**

**Check:**
- [ ] Build logs for errors
- [ ] Python version compatibility
- [ ] All dependencies in requirements.txt

**Fix:**
```bash
# Check build logs in App Runner console
# Common issues:
# - Missing dependency → Add to requirements.txt
# - Port mismatch → Ensure PORT=8080
# - Python version → Specify in runtime
```

---

### **Issue: Health Check Failing**

**Check:**
- [ ] `/health` endpoint accessible
- [ ] Port 8080 configured
- [ ] App starts successfully

**Fix:**
```bash
# Check application logs
# Look for startup errors
```

---

### **Issue: Bedrock Access Denied**

**Check:**
- [ ] IAM role attached
- [ ] Bedrock permissions in policy
- [ ] Model access granted

**Fix:**
```bash
# Verify IAM role
aws iam get-role --role-name AppRunnerTARA2Role

# Check policy
aws iam get-role-policy --role-name AppRunnerTARA2Role --policy-name BedrockAccess

# Request model access in Bedrock console if needed
```

---

### **Issue: V1 Instead of V2**

**Check:**
- [ ] `core/model_manager_v2.py` in repository
- [ ] Latest code deployed
- [ ] Import successful

**Fix:**
```bash
# Check logs for:
✅ "Multi-model fallback enabled (V2 - Per-Request Isolation)"

# If seeing V1:
# 1. Verify file exists in repo
# 2. Redeploy from latest code
# 3. Check import errors in logs
```

---

## 📊 Monitoring Setup

### **CloudWatch Alarms (Recommended)**

Create alarms for:

- [ ] HTTP 5xx errors > 5%
- [ ] Response time > 5 seconds (p95)
- [ ] Memory utilization > 85%
- [ ] CPU utilization > 80%
- [ ] Active instances = max instances (scaling issue)

**Setup:**
```bash
# In CloudWatch Console → Alarms
# Create alarm for each metric above
# SNS notification to your email
```

---

### **Log Insights Queries**

Save these queries in CloudWatch:

**Query 1: Error Detection**
```
fields @timestamp, @message
| filter @message like /ERROR|Exception/
| sort @timestamp desc
| limit 100
```

**Query 2: V2 Request Tracking**
```
fields @timestamp, @message
| filter @message like /Request.*starting/
| stats count() by bin(5m)
```

**Query 3: Throttle Analysis**
```
fields @timestamp, @message
| filter @message like /throttl/
| stats count() by bin(5m)
```

---

## 🎯 Success Criteria

**Deployment is successful when:**

- [x] App Runner status: **Running**
- [x] Health check: **Passing**
- [x] V2 confirmed: `"version": "V2"`
- [x] Document upload works
- [x] Section analysis works
- [x] Full document analysis works
- [x] Chat works
- [x] Statistics display correctly
- [x] No errors in logs
- [x] Response time < 5 seconds
- [x] Multi-user independence verified

---

## 📞 Next Steps After Deployment

### **1. Share URL**
```
Your app is live at:
https://your-app-id.us-east-1.awsapprunner.com
```

### **2. Set Up Monitoring**
- CloudWatch alarms configured
- SNS notifications set up
- Log queries saved

### **3. Documentation**
- Save service URL
- Document environment variables
- Note IAM role ARN

### **4. Backup Strategy**
- Code in Git (already done)
- Export configurations
- Save CloudWatch dashboards

---

## 📚 Reference Documents

- **[AWS_APP_RUNNER_DEPLOYMENT_GUIDE.md](AWS_APP_RUNNER_DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[ENV_VARIABLES_REFERENCE.md](ENV_VARIABLES_REFERENCE.md)** - Environment variables quick reference
- **[README_V2.md](README_V2.md)** - V2 features and verification
- **[MULTI_USER_FIX_COMPLETE.md](MULTI_USER_FIX_COMPLETE.md)** - Multi-user independence details

---

**Checklist Version:** 1.0
**Last Updated:** November 17, 2025
**Estimated Time:** 30-45 minutes for first deployment
