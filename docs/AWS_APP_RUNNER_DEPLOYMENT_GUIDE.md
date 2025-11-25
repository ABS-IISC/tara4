# AWS App Runner Deployment Guide
## AI-Prism Document Analysis Tool with 7-Model Fallback System

Last Updated: November 22, 2025
Repository: https://github.com/ABS-IISC/tara2

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [App Runner Configuration](#app-runner-configuration)
3. [Environment Variables](#environment-variables)
4. [IAM Permissions](#iam-permissions)
5. [Deployment Steps](#deployment-steps)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. AWS Account Requirements
- Active AWS Account with billing enabled
- IAM user with App Runner and Bedrock permissions
- GitHub repository access (public or connected via GitHub connection)

### 2. Required AWS Services
- **AWS App Runner** - Container orchestration
- **AWS Bedrock** - Claude AI models (us-east-1 or us-east-2 region)
- **Amazon S3** - Document and export storage
- **IAM** - Role and permissions management

### 3. GitHub Repository
- Repository: `https://github.com/ABS-IISC/tara2`
- Branch: `main`
- Latest commit includes 7-model fallback system

---

## App Runner Configuration

### Service Settings

```yaml
Service name: ai-prism-doc-analyzer
Region: us-east-1  # Must match Bedrock region
```

### Source Configuration

**Source Type:** GitHub Repository
```
Repository: ABS-IISC/tara2
Branch: main
Deployment trigger: Automatic (on git push)
```

### Build Settings

**Runtime:** Python 3
```yaml
Build command: |
  pip install --upgrade pip
  pip install -r requirements.txt

Start command: |
  python3 app.py
```

### Instance Configuration

```yaml
CPU: 1 vCPU
Memory: 2 GB
Port: 8080  # App Runner default

Auto scaling:
  Min instances: 1
  Max instances: 3
  Concurrency: 100 requests per instance
```

### Health Check

```yaml
Protocol: HTTP
Path: /health
Interval: 10 seconds
Timeout: 5 seconds
Healthy threshold: 1
Unhealthy threshold: 5
```

---

## Environment Variables

### Critical AWS Configuration

```bash
# AWS Bedrock Configuration
AWS_REGION=us-east-1
# Alternative: AWS_REGION=us-east-2
# Must match your Bedrock model access region

BEDROCK_REGION=us-east-1
# Same as AWS_REGION for consistency

# AWS Credentials (IAM Role Recommended)
# DO NOT set these if using IAM role (recommended)
# AWS_ACCESS_KEY_ID=<your-access-key>
# AWS_SECRET_ACCESS_KEY=<your-secret-key>
```

### S3 Storage Configuration

```bash
# S3 Bucket for document storage
S3_BUCKET_NAME=felix-s3-bucket
# Or your custom bucket name

# S3 Export folder structure
S3_EXPORT_PREFIX=ai-prism-exports/

# File upload limits
MAX_CONTENT_LENGTH=104857600
# 100 MB in bytes (100 * 1024 * 1024)
```

### Model Configuration

```bash
# Primary Model Settings
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
# Claude Sonnet 4.5 (Primary)

BEDROCK_MAX_TOKENS=4096
# Maximum tokens per request

BEDROCK_TEMPERATURE=0.7
# Creativity level (0.0-1.0)

# Feedback Confidence Threshold
FEEDBACK_MIN_CONFIDENCE=0.80
# 80% minimum confidence (0.80 = 80%)
```

### Flask Application Settings

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Port Configuration
PORT=8080
# App Runner uses port 8080 by default

# Session and Security
SECRET_KEY=<generate-secure-random-key>
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"

SESSION_TYPE=filesystem
PERMANENT_SESSION_LIFETIME=86400
# 24 hours in seconds
```

### Environment Detection

```bash
# Environment Type
ENVIRONMENT=production
# Options: production, development

# Deployment Platform
DEPLOYMENT_PLATFORM=apprunner
# Helps code detect AWS App Runner environment
```

### Task Queue Configuration (RQ)

```bash
# Redis Configuration (Optional - uses in-memory if not set)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# RQ Queue Names
RQ_QUEUE_DEFAULT=default
RQ_QUEUE_ANALYSIS=analysis
RQ_QUEUE_CHAT=chat
RQ_QUEUE_MONITORING=monitoring
```

### Optional Performance Settings

```bash
# Request Timeouts
REQUEST_TIMEOUT=300
# 5 minutes in seconds

# Worker Configuration
WORKERS=2
# Number of concurrent workers

# Log Level
LOG_LEVEL=INFO
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## Complete Environment Variables List (Copy-Paste Ready)

```bash
# AWS Core Configuration
AWS_REGION=us-east-1
BEDROCK_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=felix-s3-bucket
S3_EXPORT_PREFIX=ai-prism-exports/
MAX_CONTENT_LENGTH=104857600

# Model Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_MAX_TOKENS=4096
BEDROCK_TEMPERATURE=0.7
FEEDBACK_MIN_CONFIDENCE=0.80

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
PORT=8080
SECRET_KEY=<GENERATE_SECURE_KEY_HERE>
SESSION_TYPE=filesystem
PERMANENT_SESSION_LIFETIME=86400

# Environment Detection
ENVIRONMENT=production
DEPLOYMENT_PLATFORM=apprunner

# Optional Redis (if using external Redis)
# REDIS_HOST=your-redis-endpoint
# REDIS_PORT=6379
# REDIS_DB=0

# Performance Settings
REQUEST_TIMEOUT=300
WORKERS=2
LOG_LEVEL=INFO
```

---

## IAM Permissions

### Required IAM Role for App Runner

Create an IAM role with the following policies:

#### 1. AWS Bedrock Access

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockModelAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-*",
        "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-*"
      ]
    }
  ]
}
```

#### 2. S3 Access

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::felix-s3-bucket",
        "arn:aws:s3:::felix-s3-bucket/*"
      ]
    }
  ]
}
```

#### 3. CloudWatch Logs (Automatic - App Runner creates this)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### Trust Relationship for IAM Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "tasks.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

---

## Deployment Steps

### Step 1: Prepare Your Repository

1. Ensure latest changes are pushed to GitHub:
```bash
cd "/Users/abhsatsa/Documents/risk stuff/tool/tara2"
git add -A
git commit -m "Deploy: AWS App Runner configuration"
git push origin main
```

2. Verify `requirements.txt` is up to date

3. Ensure `app.py` is the main entry point

### Step 2: Create IAM Role

1. Go to AWS IAM Console → Roles → Create Role
2. Select "Custom trust policy" and paste the trust relationship above
3. Attach the 3 permission policies (Bedrock, S3, CloudWatch)
4. Name: `AppRunnerAIPrismRole`
5. Create role and note the ARN

### Step 3: Create S3 Bucket (if not exists)

```bash
aws s3 mb s3://felix-s3-bucket --region us-east-1
```

Or use AWS Console:
1. S3 → Create bucket
2. Name: `felix-s3-bucket`
3. Region: `us-east-1`
4. Block public access: Enabled
5. Create bucket

### Step 4: Create App Runner Service

1. Go to AWS App Runner Console → Create service

2. **Source:**
   - Repository type: Source code repository
   - Connect to GitHub (if first time)
   - Repository: `ABS-IISC/tara2`
   - Branch: `main`
   - Deployment trigger: Automatic

3. **Build settings:**
   - Runtime: Python 3
   - Build command: `pip install -r requirements.txt`
   - Start command: `python3 app.py`
   - Port: `8080`

4. **Service settings:**
   - Service name: `ai-prism-doc-analyzer`
   - vCPU: 1
   - Memory: 2 GB

5. **Environment variables:**
   - Paste all environment variables from the list above
   - Generate a secure `SECRET_KEY`

6. **Security:**
   - Instance role: Select `AppRunnerAIPrismRole`

7. **Auto scaling:**
   - Min: 1, Max: 3
   - Concurrency: 100

8. **Health check:**
   - Protocol: HTTP
   - Path: `/health`
   - Interval: 10s
   - Timeout: 5s

9. Review and Create

### Step 5: Monitor Deployment

1. Watch deployment logs in App Runner Console
2. Wait for status: "Running"
3. Note the service URL (e.g., `https://abc123.us-east-1.awsapprunner.com`)

---

## Post-Deployment Verification

### 1. Health Check

```bash
curl https://your-app-url.awsapprunner.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-22T18:30:00",
  "environment": "production",
  "models_loaded": 7
}
```

### 2. Access Application

Open in browser:
```
https://your-app-url.awsapprunner.com
```

You should see the AI-Prism dashboard

### 3. Test Model Fallback

Check CloudWatch Logs for model initialization:
```
✅ Loaded 7 Claude models:
1. Claude Sonnet 4.5 (Extended Thinking)
2. Claude Sonnet 4.0
3. Claude 3.7 Sonnet
4. Claude 3.5 Sonnet (June)
5. Claude 3.5 Sonnet v2 (October)
6. Claude 3 Sonnet
7. Claude 4.5 Haiku
```

### 4. Test Document Upload

1. Upload a sample .docx file
2. Click "Analyze All Sections"
3. Verify AI feedback generation
4. Check S3 bucket for exported files

---

## Troubleshooting

### Issue: "No module named 'flask'"

**Solution:** Check build logs - `requirements.txt` may not be installing correctly

```bash
# Verify requirements.txt exists and contains:
Flask==3.0.0
python-docx==1.1.2
boto3==1.35.0
# ... etc
```

### Issue: "Bedrock model not accessible"

**Causes:**
1. IAM role missing Bedrock permissions
2. Wrong AWS region (models only in us-east-1 or us-east-2)
3. Bedrock access not enabled in your AWS account

**Solution:**
1. Verify IAM role has Bedrock permissions
2. Check `AWS_REGION=us-east-1`
3. Request Bedrock access: AWS Console → Bedrock → Model access

### Issue: "S3 bucket access denied"

**Solution:**
1. Verify IAM role has S3 permissions
2. Check bucket name matches `S3_BUCKET_NAME`
3. Ensure bucket exists in same region

### Issue: "Application timeout / crashes"

**Causes:**
1. Insufficient memory (2GB recommended minimum)
2. Model inference taking too long
3. Missing environment variables

**Solution:**
1. Increase instance size to 2GB+ memory
2. Check `BEDROCK_MAX_TOKENS` (lower if needed)
3. Verify all required env vars are set

### Issue: "Port already in use"

**Solution:** App Runner expects port 8080 by default
```bash
# Ensure environment variable:
PORT=8080
```

### Viewing Logs

```bash
# Using AWS CLI
aws logs tail /aws/apprunner/ai-prism-doc-analyzer --follow

# Or use CloudWatch Console:
# CloudWatch → Log groups → /aws/apprunner/ai-prism-doc-analyzer
```

---

## Model Fallback System (Production Ready)

Your application now includes a robust 7-model fallback system:

```python
Priority 1: Claude Sonnet 4.5 (Primary) - 60s cooldown
Priority 2: Claude Sonnet 4.0 - 50s cooldown
Priority 3: Claude 3.7 Sonnet - 45s cooldown
Priority 4: Claude 3.5 Sonnet (June) - 40s cooldown
Priority 5: Claude 3.5 Sonnet v2 (October) - 35s cooldown
Priority 6: Claude 3 Sonnet - 30s cooldown
Priority 7: Claude 4.5 Haiku - 20s cooldown (cost-effective fallback)
```

**How it works:**
1. Application tries Primary model (Sonnet 4.5)
2. If unavailable/throttled, automatically falls back to next model
3. Decreasing cooldown times ensure faster recovery down the chain
4. All 7 models must fail before request fails
5. Haiku provides reliable last-resort at 10x lower cost

---

## Cost Optimization

### Model Costs (per 1K tokens)
- Sonnet models: $0.003 input / $0.015 output
- Haiku model: $0.00025 input / $0.00125 output (10x cheaper)

### App Runner Costs
- 1 vCPU, 2GB: ~$0.064/hour active + $0.003/hour provisioned
- Estimate: ~$50-70/month for low-moderate traffic

### S3 Storage Costs
- First 50TB: $0.023/GB/month
- Estimate: $1-5/month for document storage

### Total Estimated Monthly Cost
- **Low traffic:** $50-75/month
- **Moderate traffic:** $100-150/month
- **High traffic (scaled to 3 instances):** $200-300/month

---

## Security Best Practices

1. **Never commit secrets to GitHub:**
   - Use environment variables for all credentials
   - Add `.env` to `.gitignore`

2. **Use IAM Roles (not access keys):**
   - App Runner instance role provides automatic credential rotation
   - No need to store AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY

3. **Enable HTTPS only:**
   - App Runner provides automatic HTTPS
   - Disable HTTP if possible

4. **Rotate SECRET_KEY regularly:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Monitor CloudWatch Logs:**
   - Set up alarms for errors
   - Monitor request patterns

6. **S3 Bucket Security:**
   - Keep bucket private (block all public access)
   - Use IAM roles for access
   - Enable versioning for data recovery

---

## Additional Resources

- **AWS App Runner Docs:** https://docs.aws.amazon.com/apprunner/
- **AWS Bedrock Docs:** https://docs.aws.amazon.com/bedrock/
- **GitHub Repository:** https://github.com/ABS-IISC/tara2
- **Support:** Open an issue on GitHub

---

## Summary Checklist

Before deploying, verify:
- [ ] All 47 files committed and pushed to GitHub
- [ ] IAM role created with Bedrock + S3 permissions
- [ ] S3 bucket created (felix-s3-bucket)
- [ ] Bedrock model access enabled (us-east-1)
- [ ] Environment variables configured in App Runner
- [ ] SECRET_KEY generated securely
- [ ] Health check endpoint `/health` exists
- [ ] Port set to 8080
- [ ] Auto-scaling configured (min 1, max 3)
- [ ] CloudWatch logging enabled

**Your application is now production-ready with enterprise-grade AI model fallback!**

---

*Generated: November 22, 2025*
*Repository: https://github.com/ABS-IISC/tara2*
*Commit: bace9cd*
