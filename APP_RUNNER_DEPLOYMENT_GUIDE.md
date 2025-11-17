# 🚀 AWS App Runner Deployment Guide - Complete Setup

**Date:** November 17, 2025
**Purpose:** Step-by-step guide for deploying AI-Prism with Celery + Multi-Model Fallback
**Status:** ✅ PRODUCTION READY

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Option 1: Basic Deployment (No Celery)](#option-1-basic-deployment)
4. [Option 2: With Celery + Multi-Model](#option-2-with-celery--multi-model)
5. [Environment Variables Reference](#environment-variables-reference)
6. [Testing Procedures](#testing-procedures)
7. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
8. [Rollback Procedures](#rollback-procedures)

---

## 🎯 Prerequisites

### Required AWS Services:
- ✅ AWS App Runner (for Flask application)
- ✅ AWS Bedrock (for Claude AI models)
- ✅ IAM Role with Bedrock permissions
- ⚠️ ElastiCache Redis (optional, for Celery)

### Required Permissions:
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
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-*",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-*",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-*"
      ]
    }
  ]
}
```

### Model Access:
Ensure you have access to these models in AWS Bedrock:
1. `anthropic.claude-3-5-sonnet-20240620-v1:0` (Primary)
2. `anthropic.claude-3-5-sonnet-20241022-v2:0` (Fallback 1)
3. `anthropic.claude-3-sonnet-20240229-v1:0` (Fallback 2)
4. `anthropic.claude-3-haiku-20240307-v1:0` (Fallback 3)

**To request access:**
1. Go to AWS Bedrock console
2. Select "Model access"
3. Request access for Claude models
4. Wait for approval (usually immediate)

---

## 🔧 Deployment Options

### Decision Matrix:

| Scenario | Users | Requests/Day | Cost/Month | Recommendation |
|----------|-------|--------------|------------|----------------|
| Testing/Development | 1-5 | <100 | $25 | Option 1 (Basic) |
| Small Team | 5-20 | 100-1000 | $40 | Option 2 (Celery) |
| Medium Team | 20-50 | 1000-5000 | $50-75 | Option 2 + Monitoring |
| Large Team | 50+ | 5000+ | $100+ | Option 2 + Scaling |

---

## 🚀 Option 1: Basic Deployment (No Celery)

**Best for:** Testing, development, small teams (1-5 users)

**Features:**
- ✅ Synchronous processing
- ✅ Single model with exponential backoff retry
- ✅ Simplest setup
- ✅ No Redis required
- ✅ $25/month (App Runner only)

### Step 1: Create App Runner Service

**Using AWS Console:**

1. **Go to AWS App Runner Console**
   - Navigate to: https://console.aws.amazon.com/apprunner

2. **Create Service**
   - Click "Create service"
   - Source: "Source code repository" (GitHub) or "Container registry" (ECR)

3. **Configure Repository** (if using GitHub)
   - Connect your GitHub account
   - Select repository: `your-org/tara2`
   - Branch: `main`
   - Deployment trigger: "Automatic"

4. **Configure Build**
   - Runtime: Python 3
   - Build command:
     ```bash
     pip install -r requirements.txt
     ```
   - Start command:
     ```bash
     python app.py
     ```

5. **Configure Service**
   - Service name: `aiprism-document-analysis`
   - Port: `8080`
   - Instance configuration:
     - CPU: 1 vCPU
     - Memory: 2 GB

6. **Configure IAM Role**
   - Create new IAM role
   - Add inline policy (see Prerequisites)
   - Role name: `AppRunnerBedrockAccessRole`

7. **Set Environment Variables**
   ```bash
   # AWS Configuration
   AWS_REGION=us-east-1

   # Claude Model Configuration
   BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
   BEDROCK_MAX_TOKENS=8192
   BEDROCK_TEMPERATURE=0.7

   # Flask Configuration
   FLASK_ENV=production
   PORT=8080

   # Celery Configuration (DISABLED)
   USE_CELERY=false
   ```

8. **Review and Create**
   - Review all settings
   - Click "Create & deploy"
   - Wait 5-10 minutes for deployment

### Step 2: Verify Deployment

**Test Health Endpoint:**
```bash
curl https://your-app-url.region.awsapprunner.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T12:00:00"
}
```

**Test Claude Connection:**
```bash
curl https://your-app-url.region.awsapprunner.com/test_claude_connection
```

**Expected Response:**
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

### Step 3: Test Document Upload

1. Open app URL in browser
2. Upload test document (DOCX)
3. Click "Analyze" on a section
4. Should see feedback within 5-10 seconds

**✅ Option 1 Complete!**

---

## 🔄 Option 2: With Celery + Multi-Model (Recommended)

**Best for:** Production, teams with 5+ users, high availability needs

**Features:**
- ✅ Asynchronous processing with task queue
- ✅ Rate limiting (5 analysis/min, 10 chat/min)
- ✅ Multi-model automatic fallback (4 models)
- ✅ Handles 20-50+ concurrent users
- ✅ $40-50/month (App Runner + Redis)

### Step 1: Create ElastiCache Redis

**Using AWS Console:**

1. **Go to ElastiCache Console**
   - Navigate to: https://console.aws.amazon.com/elasticache

2. **Create Redis Cluster**
   - Click "Create"
   - Choose "Redis OSS"
   - Cluster mode: Disabled

3. **Configure Cluster**
   - Name: `aiprism-task-queue`
   - Node type: `cache.t3.micro` (for testing) or `cache.t3.small` (for production)
   - Number of replicas: 0 (for testing) or 1+ (for production)
   - Multi-AZ: Disabled (for testing) or Enabled (for production)

4. **Configure Subnet**
   - VPC: Default VPC
   - Subnet group: Create new or use existing
   - Availability zones: Select 1 or more

5. **Security Settings**
   - Encryption at rest: Enabled (recommended)
   - Encryption in transit: Enabled (recommended)
   - Security groups:
     - Create security group `aiprism-redis-sg`
     - Inbound rule: Port 6379 from App Runner (see next step)

6. **Review and Create**
   - Review settings
   - Click "Create"
   - Wait 10-15 minutes for cluster creation
   - **Note the Primary Endpoint URL** (e.g., `aiprism-redis.abc123.0001.use1.cache.amazonaws.com:6379`)

### Step 2: Configure Security Group

**Allow App Runner to Access Redis:**

1. **Get App Runner VPC Connector** (if using VPC)
   - Go to App Runner console
   - View service details
   - Note VPC connector ID

2. **Update Redis Security Group**
   - Go to EC2 → Security Groups
   - Select `aiprism-redis-sg`
   - Add inbound rule:
     - Type: Custom TCP
     - Port: 6379
     - Source: VPC CIDR or App Runner security group
     - Description: "App Runner access"

**Alternative: Public Access (Not Recommended for Production)**
- In Redis configuration, enable public access
- Use AUTH token for security
- Update security group to allow your IP ranges

### Step 3: Update App Runner Service

**Update Environment Variables:**

```bash
# AWS Configuration
AWS_REGION=us-east-1

# Claude Model Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
BEDROCK_FALLBACK_MODELS=anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-sonnet-20240229-v1:0,anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7

# Flask Configuration
FLASK_ENV=production
PORT=8080

# ✅ Celery Configuration (ENABLED)
USE_CELERY=true
REDIS_URL=redis://aiprism-redis.abc123.0001.use1.cache.amazonaws.com:6379/0
```

**Update Start Command:**

**Option A: Single Container (Simple)**
```bash
python app.py & celery -A celery_config worker --loglevel=info --concurrency=2
```

**Option B: Separate Worker Container (Advanced)**
- Create second App Runner service for Celery worker
- Use same code, different start command
- Start command: `celery -A celery_config worker --loglevel=info --concurrency=4`

### Step 4: Deploy Updated Configuration

**Using AWS Console:**

1. **Go to App Runner Service**
   - Select your service
   - Click "Configuration"

2. **Update Environment Variables**
   - Add/update variables from Step 3
   - Click "Save changes"

3. **Redeploy Service**
   - Click "Deploy"
   - Wait 5-10 minutes for redeployment

### Step 5: Verify Celery + Multi-Model

**Test Queue Stats:**
```bash
curl https://your-app-url.region.awsapprunner.com/queue_stats
```

**Expected Response:**
```json
{
  "available": true,
  "workers": 2,
  "active_tasks": 0,
  "reserved_tasks": 0,
  "total_pending": 0
}
```

**Test Model Stats:**
```bash
curl https://your-app-url.region.awsapprunner.com/model_stats
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

**Test Async Analysis:**

1. Open app URL in browser
2. Upload test document
3. Click "Analyze" on a section
4. Should see "Processing..." indicator
5. Results appear after 5-10 seconds

**Check Logs:**
```bash
# In App Runner console, view logs
# Look for:
✅ Celery task queue is available and configured
✅ Multi-model fallback enabled
📤 Submitting analysis task to Celery queue
🎯 Selected: Claude 3.5 Sonnet (Primary) (Priority 1)
✅ Success with Claude 3.5 Sonnet (Primary)
```

**✅ Option 2 Complete!**

---

## 📝 Environment Variables Reference

### Core Configuration (Required):

```bash
# AWS Region
AWS_REGION=us-east-1

# Claude Model Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7

# Flask Configuration
FLASK_ENV=production
PORT=8080
```

### Multi-Model Fallback (Optional):

```bash
# Comma-separated list of fallback model IDs
BEDROCK_FALLBACK_MODELS=anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-sonnet-20240229-v1:0,anthropic.claude-3-haiku-20240307-v1:0
```

**If not set:** Uses default fallback models

### Celery Task Queue (Optional):

```bash
# Enable Celery
USE_CELERY=true

# Redis connection URL
REDIS_URL=redis://your-redis-endpoint:6379/0

# Optional: Redis AUTH password
REDIS_URL=redis://:password@your-redis-endpoint:6379/0
```

**If not set:** Falls back to synchronous processing

### S3 Export (Optional):

```bash
# S3 Bucket for exports
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
```

### Chat Configuration (Optional):

```bash
# Enable multi-model chat (default: true)
CHAT_ENABLE_MULTI_MODEL=true
```

---

## 🧪 Testing Procedures

### Pre-Deployment Testing (Local):

**Test 1: Without Celery**
```bash
# Terminal 1
python app.py

# Terminal 2
curl http://localhost:8080/health
curl http://localhost:8080/test_claude_connection
```

**Test 2: With Celery**
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
celery -A celery_config worker --loglevel=info

# Terminal 3: Start Flask
USE_CELERY=true REDIS_URL=redis://localhost:6379/0 python app.py

# Terminal 4: Test
curl http://localhost:8080/queue_stats
curl http://localhost:8080/model_stats
```

### Post-Deployment Testing (App Runner):

**Test Suite:**
```bash
APP_URL="https://your-app-url.region.awsapprunner.com"

# Test 1: Health Check
curl $APP_URL/health

# Test 2: Claude Connection
curl $APP_URL/test_claude_connection

# Test 3: Queue Stats (if Celery enabled)
curl $APP_URL/queue_stats

# Test 4: Model Stats
curl $APP_URL/model_stats

# Test 5: Upload and Analyze (manual)
# Open $APP_URL in browser
# Upload document
# Click "Analyze"
```

### Load Testing (Optional):

**Using Apache Bench:**
```bash
# Test concurrent requests
ab -n 100 -c 10 $APP_URL/health

# Expected: All requests succeed
# With Celery: Queue handles load gracefully
```

---

## 📊 Monitoring and Troubleshooting

### CloudWatch Logs:

**View Logs in AWS Console:**
1. Go to App Runner console
2. Select your service
3. Click "Logs" tab
4. View "Application logs"

**Key Log Messages:**

**Startup:**
```
✅ Celery task queue is available and configured
✅ Multi-model fallback enabled
🔑 Using AWS credentials from IAM role (App Runner)
```

**Analysis Request:**
```
📤 Submitted analysis task abc-123 to queue
🎯 Selected: Claude 3.5 Sonnet (Primary) (Priority 1)
✅ Success with Claude 3.5 Sonnet (Primary) (1523 chars)
```

**Throttling (Multi-Model Fallback):**
```
🎯 Selected: Claude 3.5 Sonnet (Primary) (Priority 1)
🎯 Attempting with Claude 3.5 Sonnet (Primary)
   ⏳ Retry 1/3 after 1.2s...
   ⏳ Retry 2/3 after 2.3s...
   ⏳ Retry 3/3 after 4.5s...
🚫 Claude 3.5 Sonnet (Primary) throttled, trying next model...
🎯 Selected: Claude Fallback 1 (Priority 2)
✅ Success with Claude Fallback 1 (1467 chars)
```

### Common Issues:

**Issue 1: Celery Not Available**

**Symptoms:**
```
ℹ️  Celery not available - using synchronous processing
```

**Solutions:**
1. Check `USE_CELERY` environment variable (should be `true`)
2. Check `REDIS_URL` is set correctly
3. Verify Redis is accessible (security groups)
4. Check Redis endpoint URL is correct

**Issue 2: All Models Throttled**

**Symptoms:**
```
❌ All 4 models are currently throttled
🎭 Falling back to mock analysis response
```

**Solutions:**
1. Wait 60 seconds for cooldowns to expire
2. Check `/model_stats` endpoint
3. Use `/reset_model_cooldowns` (emergency)
4. Enable Celery to rate limit requests

**Issue 3: Claude Connection Failed**

**Symptoms:**
```json
{
  "connected": false,
  "error": "Access denied"
}
```

**Solutions:**
1. Check IAM role has Bedrock permissions
2. Verify model IDs are correct for your region
3. Request model access in Bedrock console
4. Check AWS region matches model availability

**Issue 4: Redis Connection Failed**

**Symptoms:**
```
Celery not available - using synchronous processing
```

**Solutions:**
1. Check Redis security group allows App Runner
2. Verify Redis endpoint URL
3. Check VPC configuration (if using private Redis)
4. Test Redis connection manually

---

## 🔄 Rollback Procedures

### Scenario 1: Celery Issues

**Quick Rollback to Synchronous:**

1. **Update Environment Variables**
   ```bash
   USE_CELERY=false
   # Keep all other variables
   ```

2. **Redeploy Service**
   - App Runner will redeploy with new config
   - Falls back to original synchronous behavior
   - No data loss

**Result:** ✅ Original behavior restored

---

### Scenario 2: Model Fallback Issues

**Disable Multi-Model Fallback:**

1. **Option A: Remove model_manager.py** (not recommended)
   - Remove file from repository
   - Redeploy

2. **Option B: Use single fallback model**
   ```bash
   # Set only one fallback
   BEDROCK_FALLBACK_MODELS=anthropic.claude-3-5-sonnet-20241022-v2:0
   ```

**Result:** ✅ Reduced to 2 models (primary + 1 fallback)

---

### Scenario 3: Complete Rollback

**Revert to Previous Deployment:**

1. **Using AWS Console:**
   - Go to App Runner service
   - Click "Deployments" tab
   - Find previous successful deployment
   - Click "Redeploy"

2. **Using Git:**
   ```bash
   # Find last working commit
   git log --oneline

   # Revert to that commit
   git revert HEAD
   git push

   # App Runner auto-deploys
   ```

**Result:** ✅ Previous version restored

---

## 📋 Deployment Checklist

### Pre-Deployment:
- [ ] IAM role created with Bedrock permissions
- [ ] Model access requested and approved
- [ ] Redis cluster created (if using Celery)
- [ ] Security groups configured
- [ ] Environment variables prepared

### Deployment:
- [ ] App Runner service created
- [ ] Environment variables set
- [ ] IAM role attached
- [ ] Service deployed successfully
- [ ] Health check passes

### Post-Deployment:
- [ ] `/health` endpoint responds
- [ ] `/test_claude_connection` succeeds
- [ ] `/queue_stats` shows workers (if Celery enabled)
- [ ] `/model_stats` shows 4 models
- [ ] Document upload works
- [ ] Analysis generates feedback
- [ ] Chat functionality works

### Monitoring:
- [ ] CloudWatch logs configured
- [ ] Alerts set up (optional)
- [ ] Performance dashboard created (optional)
- [ ] Queue monitoring enabled (if Celery)

---

## 💰 Cost Estimate

### Option 1: Basic (No Celery)
- **App Runner:** $25/month (1 vCPU, 2GB)
- **Total:** $25/month

### Option 2: With Celery
- **App Runner:** $25/month (1 vCPU, 2GB)
- **ElastiCache Redis (t3.micro):** $15/month
- **Total:** $40/month

### Option 3: Production Scale
- **App Runner:** $50/month (2 vCPU, 4GB)
- **ElastiCache Redis (t3.small):** $30/month
- **Separate Worker Service:** $25/month
- **Total:** $105/month

**Bedrock Costs (Pay Per Use):**
- Claude 3.5 Sonnet: $3/MTok input, $15/MTok output
- Claude 3 Haiku: $0.25/MTok input, $1.25/MTok output

**Example Usage:**
- 1000 analyses/month × 10K tokens avg = $30-50/month

---

## 🎓 Best Practices

### 1. Start Simple
✅ Deploy Option 1 first (no Celery)
✅ Test basic functionality
✅ Upgrade to Option 2 when needed

### 2. Monitor Early
✅ Check `/model_stats` regularly
✅ Watch CloudWatch logs for throttling
✅ Set up alerts for errors

### 3. Use Celery for >5 Users
✅ Rate limiting prevents throttling
✅ Queue handles burst load
✅ Better user experience

### 4. Test Rollback
✅ Practice rollback procedure
✅ Keep previous deployment ready
✅ Document configuration changes

### 5. Security
✅ Use IAM roles (not access keys)
✅ Enable Redis encryption
✅ Use VPC for Redis (production)
✅ Rotate secrets regularly

---

**Deployment Guide Version:** 1.0
**Last Updated:** November 17, 2025
**Status:** ✅ PRODUCTION READY
**Contact:** Check logs or App Runner console for issues
