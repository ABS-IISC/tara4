# App Runner Environment Variables - Final List

## 🎯 Complete List (43 Variables)

Copy-paste these into AWS App Runner → tara4 → Configuration → Environment Variables

---

## Core AWS Configuration

```
AWS_DEFAULT_REGION=us-east-1
AWS_REGION=us-east-1
```

---

## AWS Bedrock Configuration (Claude AI)

```
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_REGION=us-east-2
BEDROCK_FALLBACK_MODELS=us.anthropic.claude-sonnet-4-20250514-v1:0,us.anthropic.claude-3-7-sonnet-20250219-v1:0,anthropic.claude-3-5-sonnet-20240620-v1:0,anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
BEDROCK_READ_TIMEOUT=300
BEDROCK_CONNECT_TIMEOUT=30
```

---

## Flask Configuration

```
FLASK_ENV=production
PORT=8080
LOG_LEVEL=INFO
```

---

## Redis & Celery Configuration

**Option A: If using Upstash Redis** (Recommended):
```
USE_CELERY=true
REDIS_URL=redis://default:YOUR_PASSWORD@us1-xxx-xxx.upstash.io:6379
CELERY_BROKER_URL=redis://default:YOUR_PASSWORD@us1-xxx-xxx.upstash.io:6379
CELERY_RESULT_BACKEND=redis://default:YOUR_PASSWORD@us1-xxx-xxx.upstash.io:6379
CELERY_CONCURRENCY=8
```

**Option B: If NOT using Redis** (In-Memory Mode):
```
USE_CELERY=false
CELERY_CONCURRENCY=4
```

---

## AWS S3 Configuration

```
S3_BUCKET_NAME=felix-s3-bucket
S3_BASE_PATH=tara/
S3_REGION=us-east-1
```

---

## Rate Limiting (Optimized for 10+ Users)

```
MAX_REQUESTS_PER_MINUTE=60
MAX_CONCURRENT_REQUESTS=15
MAX_TOKENS_PER_MINUTE=180000
ANALYSIS_TASK_RATE_LIMIT=20/m
CHAT_TASK_RATE_LIMIT=30/m
HEALTH_TASK_RATE_LIMIT=1/m
```

---

## Enhanced Mode Features

```
ENABLE_ENHANCED_MODE=true
ENABLE_EXTENDED_THINKING=true
ENABLE_TOON_OPTIMIZATION=true
ENABLE_MULTI_MODEL_FALLBACK=true
ENABLE_HEALTH_MONITORING=true
ENABLE_AUTOMATIC_RETRIES=true
ENABLE_CIRCUIT_BREAKER=true
```

---

## Performance Tuning

```
TASK_SOFT_TIME_LIMIT=300
TASK_HARD_TIME_LIMIT=360
CIRCUIT_BREAKER_FAILURE_THRESHOLD=10
CIRCUIT_BREAKER_TIMEOUT=60
```

---

## Monitoring & Logging

```
ENABLE_CLOUDWATCH_LOGS=true
ENABLE_METRICS=true
METRICS_NAMESPACE=AIRprism/Production
```

---

## Security Settings

```
SECRET_KEY=GENERATE_32_CHAR_RANDOM_STRING_HERE
ENABLE_CORS=true
CORS_ALLOWED_ORIGINS=https://yymivpdgyd.us-east-1.awsapprunner.com
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

---

## ⚠️ Action Items

1. **Generate SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Replace `GENERATE_32_CHAR_RANDOM_STRING_HERE` with output

2. **Get Redis URL** (if using Option A):
   - Sign up at https://upstash.com/
   - Create database in `us-east-1` region
   - Copy Redis URL
   - Replace `YOUR_PASSWORD@us1-xxx-xxx.upstash.io` in above variables

3. **Remove these old variables** (if present):
   - `CHAT_ENABLE_MULTI_MODEL` ❌ (deprecated)

---

## 📊 Total Count: 43 Variables

- AWS: 2
- Bedrock: 7
- Flask: 3
- Redis/Celery: 5
- S3: 3
- Rate Limiting: 6
- Enhanced Mode: 7
- Performance: 4
- Monitoring: 3
- Security: 6

**Status**: ✅ Production Ready
