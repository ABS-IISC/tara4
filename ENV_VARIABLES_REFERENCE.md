# 🔧 Environment Variables Reference Card

**Quick reference for AWS App Runner deployment**

---

## ✅ Required Variables

```bash
# AWS Bedrock - Claude AI Model
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
AWS_REGION=us-east-1
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7

# Flask Application
PORT=8080
FLASK_ENV=production
```

---

## 🔄 Optional - Multi-Model Fallback

```bash
# Add backup models (comma-separated)
BEDROCK_FALLBACK_MODELS=anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-sonnet-20240229-v1:0,anthropic.claude-3-haiku-20240307-v1:0
```

**Note:** V2 multi-model is automatically enabled if `core/model_manager_v2.py` exists

---

## 🚀 Optional - Celery Task Queue

```bash
# Enable async processing (requires Redis/ElastiCache)
USE_CELERY=true
REDIS_URL=redis://your-elasticache-endpoint.amazonaws.com:6379/0
```

**When to use:**
- Document analysis > 30 seconds
- High concurrent users
- Frequent Bedrock throttling

**Start command changes to:**
```bash
python app.py & celery -A celery_config worker --loglevel=info --concurrency=2
```

---

## 💾 Optional - S3 Exports

```bash
# S3 region (uses IAM role for auth)
S3_REGION=us-east-1
```

**Note:** Bucket name hardcoded in `utils/s3_export_manager.py`

**Fallback:** Local storage if S3 unavailable

---

## 🧪 Optional - Advanced Features

```bash
# Extended reasoning (Claude Sonnet 4.0+ only)
REASONING_ENABLED=false
REASONING_BUDGET_TOKENS=2000

# Cross-region inference
USE_CROSS_REGION_INFERENCE=false

# Multi-model chat (recommended: true)
CHAT_ENABLE_MULTI_MODEL=true

# Bedrock timeout/retry
BEDROCK_TIMEOUT=30
BEDROCK_RETRY_ATTEMPTS=2
BEDROCK_RETRY_DELAY=1.0
```

---

## ❌ Do NOT Set These

```bash
# App Runner uses IAM role instead
# AWS_ACCESS_KEY_ID=...        ❌ Don't set
# AWS_SECRET_ACCESS_KEY=...    ❌ Don't set
# AWS_PROFILE=...              ❌ Don't set
```

---

## 📋 Copy-Paste Template

### **Minimum Configuration (Most Users)**

```bash
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
AWS_REGION=us-east-1
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
PORT=8080
FLASK_ENV=production
```

---

### **Recommended Configuration (With Fallback)**

```bash
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

### **Advanced Configuration (With Celery)**

```bash
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
AWS_REGION=us-east-1
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
PORT=8080
FLASK_ENV=production
BEDROCK_FALLBACK_MODELS=anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-sonnet-20240229-v1:0
CHAT_ENABLE_MULTI_MODEL=true
USE_CELERY=true
REDIS_URL=redis://your-elasticache-endpoint.amazonaws.com:6379/0
S3_REGION=us-east-1
```

---

## 🔍 Verification

### **Check V2 is Active**

```bash
# Call model stats endpoint
curl https://your-app.us-east-1.awsapprunner.com/model_stats

# Expected response
{
  "version": "V2 (Per-Request Isolation)",  ← Confirms V2!
  "multi_model_enabled": true
}
```

### **Check Celery is Active**

```bash
# Call queue stats endpoint
curl https://your-app.us-east-1.awsapprunner.com/queue_stats

# Expected response (if Celery enabled)
{
  "available": true,
  "active_tasks": 2,
  "pending_tasks": 0
}
```

### **Check S3 is Active**

```bash
# Call S3 test endpoint
curl https://your-app.us-east-1.awsapprunner.com/test_s3_connection

# Expected response (if S3 enabled)
{
  "connected": true,
  "bucket_accessible": true,
  "bucket_name": "felix-s3-bucket"
}
```

---

## 🎯 Feature Matrix

| Feature | Required Env Vars | IAM Permissions | Additional Setup |
|---------|------------------|-----------------|------------------|
| **Basic App** | 6 required vars | Bedrock | None |
| **Multi-Model V2** | Auto-detected | Bedrock (all models) | None |
| **Celery Queue** | USE_CELERY, REDIS_URL | Bedrock | Redis/ElastiCache |
| **S3 Exports** | S3_REGION (optional) | Bedrock + S3 | S3 bucket |

---

## 📞 Quick Help

### **App won't start?**
- Check PORT=8080
- Check FLASK_ENV=production
- Verify all 6 required vars set

### **Bedrock errors?**
- Verify IAM role attached
- Check model access in AWS Console
- Confirm AWS_REGION is correct

### **Throttling issues?**
- V2 handles automatically (no action needed)
- Add more fallback models
- Consider enabling Celery

### **S3 exports failing?**
- Check IAM role has S3 permissions
- Verify bucket exists
- App falls back to local storage (still works)

---

**Version:** 1.0
**Last Updated:** November 17, 2025
**Full Guide:** [AWS_APP_RUNNER_DEPLOYMENT_GUIDE.md](AWS_APP_RUNNER_DEPLOYMENT_GUIDE.md)
