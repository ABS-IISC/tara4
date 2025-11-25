# AWS App Runner - Environment Variables Configuration

Complete guide for configuring environment variables in AWS App Runner.

## How to Configure

### Method 1: AWS Console (Recommended)

1. Go to **AWS App Runner Console**
2. Select your service (tara2 or tara4)
3. Click **"Configuration"** tab
4. Click **"Configure"** button
5. Scroll to **"Environment variables"** section
6. Add each variable below

### Method 2: apprunner.yaml

Environment variables are already configured in `apprunner.yaml` but you can override them in the AWS Console.

## Required Environment Variables

### Core Application Settings

```bash
# Flask Environment
FLASK_ENV=production
# CRITICAL: Must be "production" to enable /tmp filesystem usage

# Server Port
PORT=8080
# App Runner expects port 8080

# Redis/Queue Disabled (App Runner has no Redis)
REDIS_URL=disabled
# Disables RQ/Redis gracefully, enables synchronous mode
```

### AWS Credentials & Region

**IMPORTANT**: App Runner uses IAM role for AWS credentials, NOT environment variables.

```bash
# AWS Region for Bedrock API
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1

# DO NOT SET THESE (Use IAM role instead):
# AWS_ACCESS_KEY_ID=<auto from IAM role>
# AWS_SECRET_ACCESS_KEY=<auto from IAM role>
```

**IAM Role Configuration**:
1. Go to App Runner service → **Configuration** → **Security**
2. Set **Instance role**: `AppRunnerBedrockAccess`
3. This role should have:
   - `AmazonBedrockFullAccess` (for Claude API)
   - `AmazonS3FullAccess` (for document uploads)

### Claude Model Configuration

```bash
# Primary Model
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
# Options:
#   - anthropic.claude-3-5-sonnet-20240620-v1:0 (Recommended)
#   - anthropic.claude-sonnet-4-5-20250929-v1:0 (Latest)
#   - us.anthropic.claude-sonnet-4-5-20250929-v1:0 (Cross-region)

# Model Parameters
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
BEDROCK_TIMEOUT=30
BEDROCK_RETRY_ATTEMPTS=2
BEDROCK_RETRY_DELAY=1.0

# Reasoning (Claude 3.7+ only)
REASONING_ENABLED=false
REASONING_BUDGET_TOKENS=2000
```

### S3 Storage Configuration

```bash
# S3 Bucket for document storage
S3_BUCKET_NAME=felix-s3-bucket
S3_BASE_PATH=tara/
S3_REGION=us-east-1

# IAM role must have S3 permissions
```

### Multi-Model Fallback (Optional)

```bash
# Enable automatic model fallback
ENABLE_MODEL_FALLBACK=true

# Fallback models (comma-separated)
BEDROCK_FALLBACK_MODELS=anthropic.claude-sonnet-4-5-20250929-v1:0,anthropic.claude-haiku-4-5-20251001-v1:0,anthropic.claude-3-5-sonnet-20241022-v2:0

# Chat multi-model
CHAT_ENABLE_MULTI_MODEL=true
CHAT_MODEL_PRIORITY=claude-sonnet-4-5,claude-3-5-sonnet,claude-3-5-haiku
```

## Complete Environment Variable List (Copy-Paste Ready)

### For AWS Console Configuration

```
Name: FLASK_ENV
Value: production

Name: PORT
Value: 8080

Name: REDIS_URL
Value: disabled

Name: AWS_REGION
Value: us-east-1

Name: AWS_DEFAULT_REGION
Value: us-east-1

Name: BEDROCK_MODEL_ID
Value: anthropic.claude-3-5-sonnet-20240620-v1:0

Name: BEDROCK_MAX_TOKENS
Value: 8192

Name: BEDROCK_TEMPERATURE
Value: 0.7

Name: BEDROCK_TIMEOUT
Value: 30

Name: BEDROCK_RETRY_ATTEMPTS
Value: 2

Name: BEDROCK_RETRY_DELAY
Value: 1.0

Name: S3_BUCKET_NAME
Value: felix-s3-bucket

Name: S3_BASE_PATH
Value: tara/

Name: S3_REGION
Value: us-east-1

Name: ENABLE_MODEL_FALLBACK
Value: true

Name: CHAT_ENABLE_MULTI_MODEL
Value: true
```

## Critical Settings for App Runner

### 1. FLASK_ENV=production (REQUIRED)

**Why**: The application detects production environment and uses `/tmp` for filesystem writes.

```python
# app.py:113
is_app_runner = os.environ.get('FLASK_ENV') == 'production'
if is_app_runner:
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'  # Writable
    DATA_DIR = '/tmp/data'
```

**Without this**: App crashes trying to write to read-only filesystem.

### 2. REDIS_URL=disabled (REQUIRED)

**Why**: App Runner has no Redis server. Setting this to "disabled" triggers graceful degradation.

```python
# rq_config.py:43
if REDIS_URL in ('disabled', 'none', None, ''):
    return None  # Gracefully disable Redis
```

**Without this**: App tries to connect to Redis and may hang or error.

### 3. PORT=8080 (REQUIRED)

**Why**: App Runner expects the application to listen on port 8080.

```yaml
# apprunner.yaml:13
network:
  port: 8080
  env: PORT
```

**Without this**: Health checks fail, deployment fails.

## Environment Variables App Runner Sets Automatically

App Runner automatically sets these (you don't need to):

```bash
AWS_EXECUTION_ENV=AWS_AppRunner_*
# Used to detect App Runner environment

PORT=8080
# Set automatically if not specified

AWS_REGION=<service-region>
# Inherits from App Runner service region
```

## IAM Role vs Environment Variables

### Use IAM Role For (Recommended):
- ✅ AWS credentials (access key, secret key)
- ✅ Bedrock API access
- ✅ S3 bucket access
- ✅ Any AWS service permissions

### Use Environment Variables For:
- ✅ Application configuration (Flask mode, port)
- ✅ Model selection (which Claude model to use)
- ✅ Feature flags (enable/disable features)
- ✅ Non-sensitive configuration

### Never Use Environment Variables For:
- ❌ AWS_ACCESS_KEY_ID (use IAM role)
- ❌ AWS_SECRET_ACCESS_KEY (use IAM role)
- ❌ Passwords or API keys (use AWS Secrets Manager)

## Verifying Environment Variables

After deployment, check application logs:

```bash
# Expected output in App Runner logs:
✅ Model Configuration:
   • Model: Claude Sonnet 4.5 (Enhanced)
   • Region: us-east-1
   • Port: 8080
   • Environment: production
   • AWS Credentials: ✅ Configured
```

## Troubleshooting

### Issue: "Missing bucket name"
**Cause**: S3_BUCKET_NAME not set
**Fix**: Add `S3_BUCKET_NAME=felix-s3-bucket`

### Issue: "Redis connection failed"
**Cause**: REDIS_URL not set to "disabled"
**Fix**: Set `REDIS_URL=disabled`

### Issue: "Permission denied" writing files
**Cause**: FLASK_ENV not set to "production"
**Fix**: Set `FLASK_ENV=production` (enables /tmp usage)

### Issue: Health check failing
**Cause**: PORT not set to 8080
**Fix**: Set `PORT=8080`

### Issue: "AWS credentials not found"
**Cause**: IAM role not attached
**Fix**:
1. Go to App Runner service → Configuration → Security
2. Set Instance role to `AppRunnerBedrockAccess`
3. Ensure role has Bedrock and S3 permissions

## Testing Environment Variables Locally

Test your App Runner configuration locally:

```bash
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2

# Set App Runner environment
export FLASK_ENV=production
export PORT=8080
export REDIS_URL=disabled
export AWS_REGION=us-east-1
export S3_BUCKET_NAME=felix-s3-bucket
export S3_BASE_PATH=tara/
export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0

# Test with Gunicorn (App Runner uses this)
gunicorn --config gunicorn_apprunner.conf.py app:app

# Access: http://localhost:8080
# Health: http://localhost:8080/health
```

## Environment Variable Precedence

1. **AWS Console** (highest priority)
2. **apprunner.yaml** (if not set in console)
3. **Application defaults** (if not set anywhere)

**Recommendation**: Set critical variables in **both** console and apprunner.yaml for redundancy.

## Complete AWS Console Setup Steps

1. **Create IAM Role** (if not exists):
   ```
   Role name: AppRunnerBedrockAccess
   Policies:
   - AmazonBedrockFullAccess
   - AmazonS3FullAccess
   Trust relationship: apprunner.amazonaws.com
   ```

2. **Configure App Runner Service**:
   - Go to Configuration → Edit
   - **Runtime environment variables**: Add all variables above
   - **Security → Instance role**: AppRunnerBedrockAccess
   - **Health check**: Protocol=HTTP, Path=/health
   - Save and deploy

3. **Verify Deployment**:
   ```bash
   # Test health endpoint
   curl https://your-service.us-east-1.awsapprunner.com/health

   # Should return:
   {"status": "healthy", "timestamp": "..."}
   ```

## Summary

**Minimum Required Variables**:
```bash
FLASK_ENV=production      # Enables /tmp filesystem
REDIS_URL=disabled        # Disables Redis gracefully
PORT=8080                 # App Runner expects this port
AWS_REGION=us-east-1      # Bedrock API region
S3_BUCKET_NAME=felix-s3-bucket  # Document storage
```

**IAM Role**: AppRunnerBedrockAccess with Bedrock + S3 permissions

**Result**: Application runs successfully on App Runner with all features working.

---

**Created**: 2025-11-26
**Status**: Production-ready configuration
**Tested**: ✅ Local simulation passed
