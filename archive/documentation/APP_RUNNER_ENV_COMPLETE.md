# Complete App Runner Environment Variables Configuration

## 🎯 Overview
This document provides the complete environment variable configuration for AWS App Runner deployment of the AI-Prism tool (tara4).

---

## 📋 REQUIRED Environment Variables

### 1. AWS Region Configuration
```
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1
```
**Purpose**: Specifies the AWS region for Bedrock and other AWS services.
**Note**: Both variables ensure compatibility across different AWS SDK versions.

---

### 2. Claude Model Configuration

#### Primary Model (RECOMMENDED - Works with On-Demand)
```
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```
**Purpose**: Primary Claude model for document analysis and chat.
**Why this model**: Works with on-demand throughput (no provisioning required).

#### Alternative Models (Choose ONE based on your AWS account access):

**Option A: Claude 3.5 Sonnet (Latest - October 2024)**
```
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

**Option B: Claude 3.7 Sonnet (Requires Inference Profile)**
```
BEDROCK_MODEL_ID=anthropic.claude-3-7-sonnet-20250219-v1:0
```
⚠️ **Note**: Claude 3.7 requires either:
- Cross-region inference profile: `us.anthropic.claude-3-7-sonnet-20250219-v1:0`
- Provisioned throughput
- Inference profile ARN

**Option C: Claude 4.5 Sonnet (Latest - Requires Access)**
```
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
```

---

### 3. Model Parameters
```
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
```
**Purpose**: 
- `BEDROCK_MAX_TOKENS`: Maximum response length (8192 recommended for detailed analysis)
- `BEDROCK_TEMPERATURE`: Creativity level (0.7 balanced, 0.0-1.0 range)

---

### 4. Reasoning Configuration (For Claude 3.7+ Models)
```
REASONING_ENABLED=true
REASONING_BUDGET_TOKENS=2000
```
**Purpose**: Enable extended thinking for complex analysis (Claude 3.7+ only).
**Note**: Set to `false` if using Claude 3.5 or earlier.

---

### 5. Flask Configuration
```
FLASK_ENV=production
PORT=8080
```
**Purpose**: 
- `FLASK_ENV`: Sets production mode (disables debug, enables optimizations)
- `PORT`: App Runner default port (8080 standard)

---

### 6. S3 Configuration (For Document Storage & Export)
```
S3_BUCKET_NAME=felix-s3-bucket
S3_BASE_PATH=tara/
```
**Purpose**: 
- `S3_BUCKET_NAME`: Your S3 bucket for storing documents and exports
- `S3_BASE_PATH`: Folder prefix within bucket (e.g., `tara/` creates `s3://felix-s3-bucket/tara/`)

**S3 Bucket Structure**:
```
felix-s3-bucket/
└── tara/
    ├── uploads/              # Uploaded documents
    ├── reviewed/             # Reviewed documents with comments
    ├── exports/              # Exported analysis reports
    └── logs/                 # Activity logs
```

---

## 🔧 OPTIONAL Environment Variables (Advanced)

### Multi-Model Fallback Configuration
```
CHAT_ENABLE_MULTI_MODEL=true
BEDROCK_FALLBACK_MODELS=anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-sonnet-20240229-v1:0
```
**Purpose**: Enable automatic fallback to alternative models if primary fails.
**Format**: Comma-separated list of model IDs.

---

### Cross-Region Inference (For Better Availability)
```
USE_CROSS_REGION_INFERENCE=true
```
**Purpose**: Use cross-region inference profiles for higher availability.
**Note**: Requires models with `us.anthropic.` prefix.

---

### Performance Tuning
```
BEDROCK_TIMEOUT=30
BEDROCK_RETRY_ATTEMPTS=2
BEDROCK_RETRY_DELAY=1.0
```
**Purpose**: Configure timeout and retry behavior for Bedrock API calls.

---

## 📝 Complete Configuration Examples

### Example 1: Production with Claude 3.5 Sonnet (RECOMMENDED)
```
# AWS Configuration
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1

# Model Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7

# Reasoning (Disabled for 3.5)
REASONING_ENABLED=false

# Flask Configuration
FLASK_ENV=production
PORT=8080

# S3 Configuration
S3_BUCKET_NAME=felix-s3-bucket
S3_BASE_PATH=tara/

# Multi-Model Fallback
CHAT_ENABLE_MULTI_MODEL=true
BEDROCK_FALLBACK_MODELS=anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-sonnet-20240229-v1:0
```

---

### Example 2: Production with Claude 3.7 Sonnet (Advanced)
```
# AWS Configuration
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1

# Model Configuration (Cross-Region Inference Profile)
BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7

# Reasoning (Enabled for 3.7)
REASONING_ENABLED=true
REASONING_BUDGET_TOKENS=2000

# Flask Configuration
FLASK_ENV=production
PORT=8080

# S3 Configuration
S3_BUCKET_NAME=felix-s3-bucket
S3_BASE_PATH=tara/

# Cross-Region Inference
USE_CROSS_REGION_INFERENCE=true

# Multi-Model Fallback
CHAT_ENABLE_MULTI_MODEL=true
BEDROCK_FALLBACK_MODELS=us.anthropic.claude-3-5-sonnet-20241022-v2:0,anthropic.claude-3-5-sonnet-20240620-v1:0
```

---

### Example 3: Production with Claude 4.5 Sonnet (Latest)
```
# AWS Configuration
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1

# Model Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7

# Reasoning (Enabled for 4.5)
REASONING_ENABLED=true
REASONING_BUDGET_TOKENS=2000

# Flask Configuration
FLASK_ENV=production
PORT=8080

# S3 Configuration
S3_BUCKET_NAME=felix-s3-bucket
S3_BASE_PATH=tara/

# Cross-Region Inference
USE_CROSS_REGION_INFERENCE=true

# Multi-Model Fallback
CHAT_ENABLE_MULTI_MODEL=true
BEDROCK_FALLBACK_MODELS=us.anthropic.claude-3-7-sonnet-20250219-v1:0,us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

---

## 🔐 IAM Permissions Required

Your App Runner service role needs these permissions:

### Bedrock Permissions
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
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-*",
                "arn:aws:bedrock:*::foundation-model/us.anthropic.claude-*"
            ]
        }
    ]
}
```

### S3 Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
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

---

## 🧪 Testing Your Configuration

### 1. Test Model Access
```bash
python3 test_config.py
```

### 2. Test All Available Models
```python
from config.model_config import model_config
results = model_config.test_model_combinations()
```

### 3. Verify S3 Access
```bash
aws s3 ls s3://felix-s3-bucket/tara/
```

---

## 📊 Model Comparison

| Model | Version | Max Tokens | Reasoning | Availability | Recommended For |
|-------|---------|------------|-----------|--------------|-----------------|
| Claude 3.5 Sonnet | 20240620 | 8192 | ❌ | On-Demand | **Production (Stable)** |
| Claude 3.5 Sonnet | 20241022 | 8192 | ❌ | On-Demand | Production (Latest 3.5) |
| Claude 3.7 Sonnet | 20250219 | 8192 | ✅ | Inference Profile | Advanced Analysis |
| Claude 4.5 Sonnet | 20250929 | 8192 | ✅ | Cross-Region | Latest Features |

---

## 🚨 Common Issues & Solutions

### Issue 1: Model Not Found
**Error**: `ValidationException: The provided model identifier is invalid`

**Solution**: 
1. Check model availability in your region:
   ```bash
   aws bedrock list-foundation-models --region us-east-1
   ```
2. Use cross-region inference profile for newer models:
   ```
   BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0
   USE_CROSS_REGION_INFERENCE=true
   ```

---

### Issue 2: Access Denied
**Error**: `AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel`

**Solution**: 
1. Add Bedrock permissions to App Runner service role
2. Request model access in AWS Bedrock console
3. Verify IAM policy includes correct model ARNs

---

### Issue 3: S3 Upload Fails
**Error**: `S3 upload failed: Access Denied`

**Solution**:
1. Verify S3 bucket exists: `aws s3 ls s3://felix-s3-bucket/`
2. Add S3 permissions to App Runner service role
3. Check bucket policy allows App Runner service role

---

### Issue 4: Reasoning Not Working
**Error**: Reasoning responses not appearing

**Solution**:
1. Verify model supports reasoning (3.7+)
2. Enable reasoning:
   ```
   REASONING_ENABLED=true
   REASONING_BUDGET_TOKENS=2000
   ```
3. Check model ID uses correct version

---

## 📖 Additional Resources

- **AWS Bedrock Models**: https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html
- **App Runner Configuration**: https://docs.aws.amazon.com/apprunner/latest/dg/manage-configure.html
- **Claude Model Guide**: See `config/model_config.py` for all supported models
- **Deployment Guide**: See `DEPLOYMENT.md` for complete deployment instructions

---

## 🎯 Quick Start Checklist

- [ ] Set AWS region variables (`AWS_REGION`, `AWS_DEFAULT_REGION`)
- [ ] Choose and set Claude model (`BEDROCK_MODEL_ID`)
- [ ] Configure model parameters (`BEDROCK_MAX_TOKENS`, `BEDROCK_TEMPERATURE`)
- [ ] Set Flask environment (`FLASK_ENV=production`, `PORT=8080`)
- [ ] Configure S3 bucket (`S3_BUCKET_NAME`, `S3_BASE_PATH`)
- [ ] Enable reasoning if using Claude 3.7+ (`REASONING_ENABLED=true`)
- [ ] Optional: Enable multi-model fallback (`CHAT_ENABLE_MULTI_MODEL=true`)
- [ ] Verify IAM permissions for Bedrock and S3
- [ ] Test configuration before deployment

---

**Last Updated**: November 2024  
**Version**: 1.0  
**Maintained By**: AI-Prism Development Team
