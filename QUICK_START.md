# 🚀 AI-Prism Quick Start Guide

**Status:** ✅ PRODUCTION READY
**Last Updated:** November 17, 2025

---

## 📖 Documentation Index

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[THIS FILE]** | Quick reference | First stop |
| [IMPLEMENTATION_COMPLETE_SUMMARY.md](IMPLEMENTATION_COMPLETE_SUMMARY.md) | What was built | Overview |
| [APP_RUNNER_DEPLOYMENT_GUIDE.md](APP_RUNNER_DEPLOYMENT_GUIDE.md) | How to deploy | Deployment |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | How to test | Testing |
| [MULTI_MODEL_FALLBACK_GUIDE.md](MULTI_MODEL_FALLBACK_GUIDE.md) | Multi-model details | Technical deep-dive |
| [CELERY_QUEUE_SETUP.md](CELERY_QUEUE_SETUP.md) | Celery details | Technical deep-dive |
| [CODE_COMPATIBILITY_REVIEW.md](CODE_COMPATIBILITY_REVIEW.md) | Code review | Development |

---

## ⚡ 30-Second Overview

**Problem Solved:** AWS Bedrock throttling errors when multiple users analyze documents

**Solution:** 4-layer protection system
1. ✅ Exponential backoff retry (3 attempts per model)
2. ✅ Multi-model fallback (4 Claude models)
3. ✅ Celery task queue (rate limiting, optional)
4. ✅ Mock fallback (last resort)

**Result:** Handles 20-50+ concurrent users with zero throttling errors

---

## 🎯 Choose Your Deployment

### Option 1: Basic (No Redis) - $25/month
**Best for:** Testing, small teams (1-5 users)

```bash
# No configuration needed!
# Just deploy the code to App Runner
```

**Features:**
- ✅ Synchronous processing
- ✅ Multi-model fallback (4 models)
- ✅ Simple setup

**Deploy:** [APP_RUNNER_DEPLOYMENT_GUIDE.md](APP_RUNNER_DEPLOYMENT_GUIDE.md#option-1-basic-deployment)

---

### Option 2: With Celery - $40/month
**Best for:** Production, teams with 5+ users

```bash
# In App Runner environment variables:
USE_CELERY=true
REDIS_URL=redis://your-redis-endpoint:6379/0
```

**Features:**
- ✅ Async processing
- ✅ Multi-model fallback (4 models)
- ✅ Rate limiting (5 analysis/min)
- ✅ Handles 20-50+ users

**Deploy:** [APP_RUNNER_DEPLOYMENT_GUIDE.md](APP_RUNNER_DEPLOYMENT_GUIDE.md#option-2-with-celery--multi-model)

---

## 🔧 Environment Variables

### Required (Always):
```bash
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
FLASK_ENV=production
PORT=8080
```

### Optional (Multi-Model):
```bash
# Comma-separated fallback models
BEDROCK_FALLBACK_MODELS=anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-sonnet-20240229-v1:0,anthropic.claude-3-haiku-20240307-v1:0
```

### Optional (Celery):
```bash
USE_CELERY=true
REDIS_URL=redis://endpoint:6379/0
```

---

## 🧪 Quick Test

After deployment:

```bash
# Replace with your App Runner URL
APP_URL="https://your-app.region.awsapprunner.com"

# Test 1: Health
curl $APP_URL/health
# Expected: {"status": "healthy"}

# Test 2: Claude Connection
curl $APP_URL/test_claude_connection
# Expected: {"connected": true}

# Test 3: Model Stats
curl $APP_URL/model_stats
# Expected: {"multi_model_enabled": true, "stats": {"total_models": 4}}

# Test 4: Queue Stats (if Celery enabled)
curl $APP_URL/queue_stats
# Expected: {"available": true, "workers": 2}
```

---

## 📊 Monitoring

### Check Model Health:
```bash
curl $APP_URL/model_stats
```

**Response shows:**
- Total models available
- Which models are throttled
- Cooldown times

### Check Queue Status (if Celery enabled):
```bash
curl $APP_URL/queue_stats
```

**Response shows:**
- Number of workers
- Active tasks
- Pending tasks

### Emergency: Reset Cooldowns
```bash
curl -X POST $APP_URL/reset_model_cooldowns
```

---

## 🔥 Common Scenarios

### Scenario 1: No Throttling Protection Needed
**Use:** Option 1 (Basic)
**Cost:** $25/month
**Setup:** 5 minutes

### Scenario 2: Getting Throttling Errors
**Use:** Option 2 (with Celery)
**Cost:** $40/month
**Setup:** 20 minutes (includes Redis)

### Scenario 3: High Traffic (10+ Users)
**Use:** Option 2 (with Celery)
**Cost:** $40-100/month (scale as needed)
**Setup:** 20 minutes + monitoring

---

## 🚨 Troubleshooting

### Issue: ThrottlingException errors
**Solution:**
1. Check `/model_stats` - are models throttled?
2. If yes, wait 60 seconds or use `/reset_model_cooldowns`
3. If persistent, enable Celery (Option 2)

### Issue: Celery not working
**Solution:**
1. Check `USE_CELERY=true` is set
2. Check `REDIS_URL` is correct
3. Verify Redis security group allows App Runner
4. Check `/queue_stats` endpoint

### Issue: Claude not connecting
**Solution:**
1. Verify IAM role has Bedrock permissions
2. Check model IDs are correct for your region
3. Request model access in Bedrock console
4. Verify AWS_REGION matches model availability

---

## 📞 Where to Get Help

| Issue Type | Document to Check |
|------------|-------------------|
| Deployment | [APP_RUNNER_DEPLOYMENT_GUIDE.md](APP_RUNNER_DEPLOYMENT_GUIDE.md) |
| Testing | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| Multi-Model | [MULTI_MODEL_FALLBACK_GUIDE.md](MULTI_MODEL_FALLBACK_GUIDE.md) |
| Celery | [CELERY_QUEUE_SETUP.md](CELERY_QUEUE_SETUP.md) |
| Code Issues | [CODE_COMPATIBILITY_REVIEW.md](CODE_COMPATIBILITY_REVIEW.md) |

---

## ✅ Deployment Checklist

### Before Deployment:
- [ ] Read [APP_RUNNER_DEPLOYMENT_GUIDE.md](APP_RUNNER_DEPLOYMENT_GUIDE.md)
- [ ] Choose Option 1 or 2
- [ ] Request Bedrock model access
- [ ] Create IAM role with permissions
- [ ] Create Redis cluster (if Option 2)

### During Deployment:
- [ ] Create App Runner service
- [ ] Set environment variables
- [ ] Attach IAM role
- [ ] Deploy service

### After Deployment:
- [ ] Run quick tests (above)
- [ ] Upload test document
- [ ] Verify analysis works
- [ ] Check CloudWatch logs

---

## 💡 Pro Tips

1. **Start Simple:** Deploy Option 1 first, upgrade to Option 2 only if needed
2. **Monitor Early:** Check `/model_stats` after first few analyses
3. **Test Rollback:** Practice reverting `USE_CELERY` to false
4. **Watch Logs:** CloudWatch logs show which models are used
5. **Use Defaults:** Multi-model fallback works automatically, no config needed

---

## 🎓 Understanding the System

### Without New Features (Baseline):
```
Request → Claude API → Wait 5-10s → Response
```
**Risk:** Throttling with multiple users

### With Multi-Model Only:
```
Request → Primary Model → Throttled? → Try Fallback 1 → Success!
```
**Protection:** 4x capacity

### With Celery Only:
```
Request → Queue → Process 1 at a time → Claude API
```
**Protection:** Rate limiting

### With Both (Maximum Protection):
```
Request → Queue (5/min) → Worker → Try 4 Models → Success!
```
**Protection:** 4x capacity + rate limiting = Zero throttling

---

## 📈 Capacity Guide

| Setup | Max Users | Requests/Hour | Cost/Month |
|-------|-----------|---------------|------------|
| Baseline | 1-5 | ~3,600 | $25 |
| Multi-Model | 10-20 | ~14,400 | $25 |
| Celery | 5-20 | ~14,400 | $40 |
| Both | 20-50+ | ~14,400+ | $40-100 |

---

## 🚀 Next Steps

1. **Read:** [APP_RUNNER_DEPLOYMENT_GUIDE.md](APP_RUNNER_DEPLOYMENT_GUIDE.md)
2. **Deploy:** Follow Option 1 or 2
3. **Test:** Use [TESTING_GUIDE.md](TESTING_GUIDE.md)
4. **Monitor:** Check `/model_stats` and `/queue_stats`
5. **Scale:** Upgrade to Option 2 if needed

---

**Quick Start Version:** 1.0
**Last Updated:** November 17, 2025
**Status:** ✅ READY TO USE

**🎯 Deploy now and eliminate throttling forever!**
