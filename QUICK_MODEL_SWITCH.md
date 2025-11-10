# Quick Model Switch Guide for AWS App Runner

## Current Configuration (Your Setup)
```bash
BEDROCK_MODEL_ID = anthropic.claude-3-7-sonnet-20250219-v1:0
REASONING_ENABLED = true
REASONING_BUDGET_TOKENS = 2000
```

## Switch to Different Models

### 1. Claude 3.5 Sonnet (Latest, No Reasoning)
**In App Runner Environment Variables:**
```bash
BEDROCK_MODEL_ID = anthropic.claude-3-5-sonnet-20241022-v1:0
REASONING_ENABLED = false
```
**Benefits:** Latest model, fast, high quality
**Use Case:** General document analysis without reasoning

### 2. Claude 3 Haiku (Fastest, Cheapest)
**In App Runner Environment Variables:**
```bash
BEDROCK_MODEL_ID = anthropic.claude-3-haiku-20240307-v1:0
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 4096
```
**Benefits:** Very fast, cost-effective
**Use Case:** Quick reviews, high-volume processing

### 3. Claude 3 Opus (Most Capable)
**In App Runner Environment Variables:**
```bash
BEDROCK_MODEL_ID = anthropic.claude-3-opus-20240229-v1:0
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 4096
```
**Benefits:** Highest quality analysis
**Use Case:** Complex, critical document analysis

### 4. Claude v2.1 (Legacy, Reliable)
**In App Runner Environment Variables:**
```bash
BEDROCK_MODEL_ID = claude-v2.1
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 8192
```
**Benefits:** Proven, stable, lower cost
**Use Case:** Fallback option, budget-conscious

## How to Switch Models

### Method 1: AWS Console
1. Go to AWS Console → App Runner
2. Select your service
3. Go to Configuration → Environment variables
4. Update `BEDROCK_MODEL_ID`
5. Update `REASONING_ENABLED` if needed
6. Save changes (auto-deploys)

### Method 2: AWS CLI
```bash
# Update environment variables
aws apprunner update-service \
  --service-arn "your-service-arn" \
  --source-configuration '{
    "ImageRepository": {
      "ImageConfiguration": {
        "RuntimeEnvironmentVariables": {
          "BEDROCK_MODEL_ID": "anthropic.claude-3-5-sonnet-20241022-v1:0",
          "REASONING_ENABLED": "false"
        }
      }
    }
  }' \
  --region us-east-1
```

## Test Your Configuration

### Run Test Script
```bash
python test_model_config.py
```

### Check Logs
```bash
# View App Runner logs to see configuration
aws logs get-log-events \
  --log-group-name "/aws/apprunner/your-service/application" \
  --log-stream-name "latest" \
  --region us-east-1
```

### Look for Configuration Summary
```
AI-PRISM MODEL CONFIGURATION
============================================================
Model ID: anthropic.claude-3-5-sonnet-20241022-v1:0
Model Name: Claude 3.5 Sonnet (Latest)
Reasoning Enabled: false
============================================================
```

## Model Comparison Quick Reference

| Model | Speed | Cost | Quality | Reasoning | Best For |
|-------|-------|------|---------|-----------|----------|
| **Claude 3.7 Sonnet** | Medium | Medium | High | ✅ | Complex analysis |
| **Claude 3.5 Sonnet** | Fast | Medium | High | ❌ | General use |
| **Claude 3 Haiku** | Very Fast | Low | Good | ❌ | Quick reviews |
| **Claude 3 Opus** | Slow | High | Excellent | ❌ | Critical analysis |
| **Claude v2.1** | Medium | Low | Good | ❌ | Budget option |

## Automatic Fallback

The system automatically tries these models in order if your primary model fails:
1. Your configured model
2. Claude 3.7 Sonnet (reasoning)
3. Claude 3.5 Sonnet (latest)
4. Claude 3 Sonnet (standard)
5. Claude 3 Haiku (fast)

## Troubleshooting

### Model Not Available
- Check if model is available in your region (us-east-1)
- Verify IAM permissions for the specific model
- Try a different model from the list above

### Performance Issues
- Switch to Claude 3 Haiku for speed
- Reduce `BEDROCK_MAX_TOKENS` to 4096 or lower
- Increase `BEDROCK_TIMEOUT` to 60

### Cost Concerns
- Use Claude 3 Haiku (cheapest)
- Disable reasoning: `REASONING_ENABLED = false`
- Lower token limits: `BEDROCK_MAX_TOKENS = 2048`

## Recommended Configurations

### For Production (Balanced)
```bash
BEDROCK_MODEL_ID = anthropic.claude-3-7-sonnet-20250219-v1:0
REASONING_ENABLED = true
REASONING_BUDGET_TOKENS = 2000
BEDROCK_MAX_TOKENS = 8192
```

### For High Volume (Fast)
```bash
BEDROCK_MODEL_ID = anthropic.claude-3-haiku-20240307-v1:0
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 4096
```

### For Critical Analysis (Quality)
```bash
BEDROCK_MODEL_ID = anthropic.claude-3-opus-20240229-v1:0
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 4096
BEDROCK_TIMEOUT = 60
```

### For Budget-Conscious (Cost)
```bash
BEDROCK_MODEL_ID = claude-v2.1
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 4096
```

---

**Your current Claude 3.7 Sonnet with reasoning is excellent for complex document analysis. Switch models based on your specific needs for speed, cost, or quality.**