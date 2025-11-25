# AWS App Runner - Quick Setup (Console)

## 📋 Checklist

Use this checklist when configuring your App Runner service in the AWS Console.

## Step 1: Environment Variables

Go to **Configuration → Edit → Environment variables**

Copy and paste these variables:

| Name | Value |
|------|-------|
| `FLASK_ENV` | `production` |
| `PORT` | `8080` |
| `REDIS_URL` | `disabled` |
| `AWS_REGION` | `us-east-1` |
| `AWS_DEFAULT_REGION` | `us-east-1` |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-5-sonnet-20240620-v1:0` |
| `BEDROCK_MAX_TOKENS` | `8192` |
| `BEDROCK_TEMPERATURE` | `0.7` |
| `BEDROCK_TIMEOUT` | `30` |
| `S3_BUCKET_NAME` | `felix-s3-bucket` |
| `S3_BASE_PATH` | `tara/` |
| `S3_REGION` | `us-east-1` |
| `ENABLE_MODEL_FALLBACK` | `true` |
| `CHAT_ENABLE_MULTI_MODEL` | `true` |

## Step 2: IAM Role (Security)

Go to **Configuration → Edit → Security**

- **Instance role**: `AppRunnerBedrockAccess`
- **Access role**: (default - AWS creates this automatically)

### IAM Role Required Permissions:

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
      "Resource": "arn:aws:bedrock:*:*:model/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
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

## Step 3: Health Check

Go to **Configuration → Edit → Health check**

- **Protocol**: `HTTP`
- **Path**: `/health`
- **Interval**: `10` seconds
- **Timeout**: `5` seconds
- **Healthy threshold**: `1` requests
- **Unhealthy threshold**: `5` requests

## Step 4: Deploy

Click **"Deploy"** and wait for:

1. ✅ Build phase (2-3 minutes)
2. ✅ Deploy phase (1-2 minutes)
3. ✅ Health checks pass
4. ✅ Status: **Running**

## Verification

After deployment completes:

```bash
# Get your App Runner URL from console
curl https://your-service.us-east-1.awsapprunner.com/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-11-26T..."
}
```

## Critical Variables Explained

### FLASK_ENV=production
- **Required**: YES
- **Why**: Enables `/tmp` filesystem usage (App Runner has read-only filesystem)
- **Without it**: App crashes trying to write to `/uploads` or `/data`

### REDIS_URL=disabled
- **Required**: YES
- **Why**: App Runner has no Redis server, this disables it gracefully
- **Without it**: App hangs trying to connect to Redis

### PORT=8080
- **Required**: YES
- **Why**: App Runner expects applications to listen on port 8080
- **Without it**: Health checks fail, deployment fails

## Common Issues

### ❌ Deployment Failed
**Check**:
- [ ] FLASK_ENV set to `production`
- [ ] REDIS_URL set to `disabled`
- [ ] PORT set to `8080`
- [ ] IAM role attached

### ❌ Health Check Failed
**Check**:
- [ ] Health check path is `/health` (not `/healthcheck`)
- [ ] Protocol is `HTTP` (not TCP)
- [ ] Port is `8080`

### ❌ Permission Denied
**Check**:
- [ ] IAM role `AppRunnerBedrockAccess` is attached
- [ ] Role has Bedrock permissions
- [ ] Role has S3 permissions for `felix-s3-bucket`

## Quick Test After Deployment

```bash
# Replace with your actual URL
export APP_URL="https://your-service.us-east-1.awsapprunner.com"

# 1. Health check
curl $APP_URL/health

# 2. Main page (should return HTML)
curl -I $APP_URL/

# 3. Test upload (requires auth in browser)
# Open: https://your-service.us-east-1.awsapprunner.com
```

## Environment Variables Already Set by App Runner

These are automatic (don't set them):

- `AWS_EXECUTION_ENV` - Set by App Runner
- `PORT` - Can be overridden, defaults to 8080

## Summary

**Minimum Configuration**:
1. ✅ Set 14 environment variables (see table above)
2. ✅ Attach IAM role: `AppRunnerBedrockAccess`
3. ✅ Configure health check: HTTP `/health`
4. ✅ Deploy and verify

**Time**: ~5 minutes to configure, ~5 minutes to deploy

**Result**: Fully functional AI document analysis application on AWS App Runner!

---

**Created**: 2025-11-26
**For**: AWS App Runner Console Configuration
