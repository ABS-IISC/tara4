# AWS App Runner - Claude Model Configuration Guide

## Overview
This guide shows how to configure different Claude models in AWS App Runner for the AI-Prism tool. The system now supports flexible model configuration with automatic fallback support.

## Supported Claude Models

### Claude 3.7 Sonnet (Reasoning) - RECOMMENDED
```
BEDROCK_MODEL_ID = anthropic.claude-3-7-sonnet-20250219-v1:0
REASONING_ENABLED = true
REASONING_BUDGET_TOKENS = 2000
BEDROCK_MAX_TOKENS = 8192
BEDROCK_TEMPERATURE = 0.7
```

### Claude 3.5 Sonnet (Latest)
```
BEDROCK_MODEL_ID = anthropic.claude-3-5-sonnet-20241022-v1:0
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 8192
BEDROCK_TEMPERATURE = 0.7
```

### Claude 3 Sonnet (Standard)
```
BEDROCK_MODEL_ID = anthropic.claude-3-sonnet-20240229-v1:0
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 4096
BEDROCK_TEMPERATURE = 0.7
```

### Claude 3 Haiku (Fast & Cost-Effective)
```
BEDROCK_MODEL_ID = anthropic.claude-3-haiku-20240307-v1:0
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 4096
BEDROCK_TEMPERATURE = 0.7
```

### Claude 3 Opus (Most Capable)
```
BEDROCK_MODEL_ID = anthropic.claude-3-opus-20240229-v1:0
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 4096
BEDROCK_TEMPERATURE = 0.7
```

### Claude v2.1 (Legacy)
```
BEDROCK_MODEL_ID = claude-v2.1
REASONING_ENABLED = false
BEDROCK_MAX_TOKENS = 8192
BEDROCK_TEMPERATURE = 0.7
```

## Complete App Runner Environment Variables

### For Claude 3.7 Sonnet (Your Current Setup)
```bash
# AWS Configuration
AWS_REGION = us-east-1
AWS_DEFAULT_REGION = us-east-1

# Model Configuration
BEDROCK_MODEL_ID = anthropic.claude-3-7-sonnet-20250219-v1:0
BEDROCK_MAX_TOKENS = 8192
BEDROCK_TEMPERATURE = 0.7

# Reasoning Configuration (Claude 3.7 Sonnet specific)
REASONING_ENABLED = true
REASONING_BUDGET_TOKENS = 2000

# Flask Configuration
FLASK_ENV = production
PORT = 8080

# Performance Tuning (Optional)
BEDROCK_TIMEOUT = 30
BEDROCK_RETRY_ATTEMPTS = 3
BEDROCK_RETRY_DELAY = 1.0
```

### For Claude 3.5 Sonnet (Alternative)
```bash
# AWS Configuration
AWS_REGION = us-east-1
AWS_DEFAULT_REGION = us-east-1

# Model Configuration
BEDROCK_MODEL_ID = anthropic.claude-3-5-sonnet-20241022-v1:0
BEDROCK_MAX_TOKENS = 8192
BEDROCK_TEMPERATURE = 0.7

# Reasoning Configuration (Not supported)
REASONING_ENABLED = false

# Flask Configuration
FLASK_ENV = production
PORT = 8080
```

### For Claude 3 Haiku (Cost-Effective)
```bash
# AWS Configuration
AWS_REGION = us-east-1
AWS_DEFAULT_REGION = us-east-1

# Model Configuration
BEDROCK_MODEL_ID = anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_MAX_TOKENS = 4096
BEDROCK_TEMPERATURE = 0.7

# Reasoning Configuration (Not supported)
REASONING_ENABLED = false

# Flask Configuration
FLASK_ENV = production
PORT = 8080
```

## Model Comparison

| Model | Speed | Cost | Capability | Reasoning | Max Tokens | Best For |
|-------|-------|------|------------|-----------|------------|----------|
| Claude 3.7 Sonnet | Medium | Medium | High | ✅ Yes | 8192 | Complex analysis with reasoning |
| Claude 3.5 Sonnet | Fast | Medium | High | ❌ No | 8192 | General document analysis |
| Claude 3 Sonnet | Medium | Medium | High | ❌ No | 4096 | Standard analysis tasks |
| Claude 3 Haiku | Very Fast | Low | Medium | ❌ No | 4096 | Quick reviews, cost-sensitive |
| Claude 3 Opus | Slow | High | Very High | ❌ No | 4096 | Most complex analysis |
| Claude v2.1 | Medium | Low | Medium | ❌ No | 8192 | Legacy compatibility |

## Automatic Fallback System

The system automatically tries fallback models if the primary model fails:

1. **Primary Model**: Your configured model
2. **Fallback 1**: Claude 3.7 Sonnet (if not primary)
3. **Fallback 2**: Claude 3.5 Sonnet (if not primary)
4. **Fallback 3**: Claude 3 Sonnet (if not primary)
5. **Fallback 4**: Claude 3 Haiku (if not primary)
6. **Final Fallback**: Mock responses for development

## Configuration Steps in App Runner

### 1. Access App Runner Service
```bash
aws apprunner list-services --region us-east-1
```

### 2. Update Environment Variables
Go to AWS Console → App Runner → Your Service → Configuration → Environment Variables

### 3. Add/Update Variables
Set the environment variables based on your chosen model configuration above.

### 4. Deploy Changes
App Runner will automatically redeploy with new configuration.

### 5. Verify Configuration
Check the application logs to see the configuration summary:
```
AI-PRISM MODEL CONFIGURATION
============================================================
Environment: production
Region: us-east-1
Model ID: anthropic.claude-3-7-sonnet-20250219-v1:0
Model Name: Claude 3.7 Sonnet (Reasoning)
Reasoning Enabled: true
Reasoning Budget: 2000
============================================================
```

## Testing Different Models

### Test Configuration Script
```python
# test_model_config.py
from config.model_config import model_config

# Print current configuration
model_config.print_config_summary()

# Test model availability
config = model_config.get_model_config()
print(f"Has credentials: {model_config.has_credentials()}")
print(f"Is production: {model_config.is_production()}")
```

### Run Test
```bash
python test_model_config.py
```

## Troubleshooting

### Model Access Issues
1. **Check IAM Permissions**: Ensure App Runner role has Bedrock access
2. **Verify Region**: Model must be available in your AWS region
3. **Check Model ID**: Ensure exact model ID format

### Performance Issues
1. **Increase Timeout**: Set `BEDROCK_TIMEOUT = 60`
2. **Reduce Token Limit**: Lower `BEDROCK_MAX_TOKENS`
3. **Use Faster Model**: Switch to Claude 3 Haiku

### Cost Optimization
1. **Use Claude 3 Haiku**: Fastest and cheapest
2. **Reduce Max Tokens**: Lower token limits
3. **Disable Reasoning**: Set `REASONING_ENABLED = false`

## Monitoring and Logs

### View App Runner Logs
```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/apprunner"
aws logs get-log-events --log-group-name "/aws/apprunner/your-service/application"
```

### Key Log Messages
- `AI-PRISM MODEL CONFIGURATION`: Configuration summary
- `Using Bedrock model`: Current model being used
- `Trying fallback model`: Fallback model attempts
- `Reasoning enabled`: Reasoning configuration status

## Best Practices

### Production Recommendations
1. **Use Claude 3.7 Sonnet**: Best balance of capability and reasoning
2. **Enable Reasoning**: For complex document analysis
3. **Set Appropriate Timeouts**: 30-60 seconds
4. **Monitor Costs**: Track Bedrock usage

### Development Recommendations
1. **Use Claude 3 Haiku**: Fast and cost-effective
2. **Lower Token Limits**: Reduce costs during testing
3. **Enable Fallbacks**: Ensure system reliability

### Security Recommendations
1. **Use IAM Roles**: Don't hardcode credentials
2. **Limit Model Access**: Only grant necessary permissions
3. **Monitor Usage**: Track API calls and costs

## Migration Guide

### From Current Setup to New System
Your current configuration will work without changes:
```bash
# Your existing variables (still supported)
BEDROCK_MODEL_ID = anthropic.claude-3-7-sonnet-20250219-v1:0
REASONING_ENABLED = true
REASONING_BUDGET_TOKENS = 2000
```

The new system adds:
- Automatic model detection
- Fallback support
- Better error handling
- Configuration validation

### No Action Required
The system is backward compatible with your existing App Runner configuration.

## Support

### Configuration Issues
1. Check App Runner logs for configuration summary
2. Verify environment variables are set correctly
3. Test with different models if primary fails

### Model Access Issues
1. Verify IAM permissions for Bedrock
2. Check model availability in your region
3. Try fallback models

### Performance Issues
1. Monitor response times in logs
2. Adjust timeout and retry settings
3. Consider switching to faster models

---

**The system now supports any Claude model available in AWS Bedrock with automatic configuration and fallback support!**