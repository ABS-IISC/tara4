# AI-Prism - Complete AWS Regional Support

## Overview

Your AI-Prism application now supports **ALL 34 AWS regions globally**, with **18 regions having full Bedrock support** and **16 regions with cross-region Bedrock access**.

---

## Complete Regional Coverage

### 📊 Summary Statistics

- **Total AWS Regions**: 34
- **Bedrock-Enabled Regions**: 18 (direct access)
- **Cross-Region Support**: 16 (automatic fallback to nearest Bedrock region)
- **Geographic Coverage**: All 6 continents

---

## ✅ Bedrock-Enabled Regions (18 Regions)

These regions have **direct Amazon Bedrock access** with Claude models:

### United States (4 Regions)
| Region Code | Region Name | Bedrock Status | Model ID Prefix |
|------------|-------------|----------------|-----------------|
| `us-east-1` | United States (N. Virginia) | ✅ Enabled by default | `us.anthropic...` |
| `us-east-2` | United States (Ohio) | ✅ Enabled by default | `us.anthropic...` |
| `us-west-1` | United States (N. California) | ✅ Enabled by default | `us.anthropic...` |
| `us-west-2` | United States (Oregon) | ✅ Enabled by default | `us.anthropic...` |

### Canada (1 Region)
| Region Code | Region Name | Bedrock Status | Model ID Prefix |
|------------|-------------|----------------|-----------------|
| `ca-central-1` | Canada (Central) | ✅ Enabled by default | `anthropic...` |

### South America (1 Region)
| Region Code | Region Name | Bedrock Status | Model ID Prefix |
|------------|-------------|----------------|-----------------|
| `sa-east-1` | South America (São Paulo) | ✅ Enabled by default | `anthropic...` |

### Europe (6 Regions)
| Region Code | Region Name | Bedrock Status | Model ID Prefix |
|------------|-------------|----------------|-----------------|
| `eu-north-1` | Europe (Stockholm) | ✅ Enabled by default | `eu.anthropic...` |
| `eu-west-1` | Europe (Ireland) | ✅ Enabled by default | `eu.anthropic...` |
| `eu-west-2` | Europe (London) | ✅ Enabled by default | `eu.anthropic...` |
| `eu-west-3` | Europe (Paris) | ✅ Enabled by default | `eu.anthropic...` |
| `eu-central-1` | Europe (Frankfurt) | ✅ Enabled by default | `eu.anthropic...` |
| `eu-south-2` | Europe (Spain) | ✅ Enabled | `eu.anthropic...` |

### Asia Pacific (6 Regions)
| Region Code | Region Name | Bedrock Status | Model ID Prefix |
|------------|-------------|----------------|-----------------|
| `ap-south-1` | Asia Pacific (Mumbai) | ✅ Enabled by default | `apac.anthropic...` |
| `ap-northeast-1` | Asia Pacific (Tokyo) | ✅ Enabled by default | `apac.anthropic...` |
| `ap-northeast-2` | Asia Pacific (Seoul) | ✅ Enabled by default | `apac.anthropic...` |
| `ap-northeast-3` | Asia Pacific (Osaka) | ✅ Enabled by default | `apac.anthropic...` |
| `ap-southeast-1` | Asia Pacific (Singapore) | ✅ Enabled by default | `apac.anthropic...` |
| `ap-southeast-2` | Asia Pacific (Sydney) | ✅ Enabled by default | `apac.anthropic...` |

---

## ⚠️ Cross-Region Supported Regions (16 Regions)

These regions **DO NOT have direct Bedrock access** but the application **automatically routes Bedrock calls** to the nearest supported region:

### Canada (1 Region)
| Region Code | Region Name | Status | Fallback Region |
|------------|-------------|--------|----------------|
| `ca-west-1` | Canada (Calgary) | ❌ Disabled | → `ca-central-1` |

### Mexico (1 Region)
| Region Code | Region Name | Status | Fallback Region |
|------------|-------------|--------|----------------|
| `mx-central-1` | Mexico (Central) | ❌ Disabled | → `us-east-1` |

### Europe (2 Regions)
| Region Code | Region Name | Status | Fallback Region |
|------------|-------------|--------|----------------|
| `eu-central-2` | Europe (Zurich) | ❌ Disabled | → `eu-central-1` |
| `eu-south-1` | Europe (Milan) | ❌ Disabled | → `eu-central-1` |

### Asia Pacific (8 Regions)
| Region Code | Region Name | Status | Fallback Region |
|------------|-------------|--------|----------------|
| `ap-south-2` | Asia Pacific (Hyderabad) | ❌ Disabled | → `ap-south-1` |
| `ap-east-1` | Asia Pacific (Hong Kong) | ❌ Disabled | → `ap-southeast-1` |
| `ap-southeast-3` | Asia Pacific (Jakarta) | ❌ Disabled | → `ap-southeast-1` |
| `ap-southeast-4` | Asia Pacific (Melbourne) | ❌ Disabled | → `ap-southeast-2` |
| `ap-southeast-5` | Asia Pacific (Malaysia) | ❌ Disabled | → `ap-southeast-1` |
| `ap-southeast-6` | Asia Pacific (New Zealand) | ❌ Disabled | → `ap-southeast-2` |
| `ap-southeast-7` | Asia Pacific (Thailand) | ❌ Disabled | → `ap-southeast-1` |
| `ap-southeast-8` | Asia Pacific (Taipei) | ❌ Disabled | → `ap-northeast-1` |

### Middle East (2 Regions)
| Region Code | Region Name | Status | Fallback Region |
|------------|-------------|--------|----------------|
| `me-south-1` | Middle East (Bahrain) | ❌ Disabled | → `eu-central-1` |
| `me-central-1` | Middle East (UAE) | ❌ Disabled | → `eu-central-1` |

### Africa (1 Region)
| Region Code | Region Name | Status | Fallback Region |
|------------|-------------|--------|----------------|
| `af-south-1` | Africa (Cape Town) | ❌ Disabled | → `eu-west-1` |

### Israel (1 Region)
| Region Code | Region Name | Status | Fallback Region |
|------------|-------------|--------|----------------|
| `il-central-1` | Israel (Tel Aviv) | ❌ Disabled | → `eu-central-1` |

---

## How It Works

### Automatic Region Detection

The application automatically detects your deployment region through:

1. **AWS_REGION environment variable** (highest priority)
2. **EC2 Instance Metadata** (when on AWS)
3. **AWS CLI Configuration**
4. **boto3 Session**
5. **Fallback to us-east-1**

### Automatic Bedrock Routing

When you deploy to a region:

**Bedrock-Enabled Region** (18 regions):
```
Deploy to eu-west-1 (Ireland)
    ↓
Application detects: eu-west-1
    ↓
Uses Bedrock in: eu-west-1 (same region)
    ↓
Model ID: eu.anthropic.claude-sonnet-4-5-20250929-v1:0
```

**Non-Bedrock Region** (16 regions):
```
Deploy to ap-southeast-3 (Jakarta)
    ↓
Application detects: ap-southeast-3
    ↓
Bedrock not available, uses cross-region to: ap-southeast-1
    ↓
Model ID: apac.anthropic.claude-sonnet-4-5-20250929-v1:0
    ↓
⚠️ Logs warning: "Using cross-region Bedrock"
```

### S3 Integration

S3 buckets are **region-independent**:
- Application auto-detects S3 bucket's region
- Creates region-specific S3 client
- Works even if S3 bucket is in different region from compute

**Example**:
```
Compute in: ap-northeast-1 (Tokyo)
S3 bucket in: ap-southeast-1 (Singapore)
    ↓
Application detects both regions
    ↓
✅ Works perfectly with optimal routing
```

---

## Deployment Guide

### Quick Start for Any Region

#### Step 1: Choose Your Region

Pick **any** of the 34 supported regions based on:
- **User location** (lowest latency)
- **Data residency** (compliance requirements)
- **Cost** (regional pricing varies)
- **Bedrock availability** (direct vs cross-region)

#### Step 2: Update Configuration

Edit `.ebextensions/01_environment.config`:

```yaml
aws:elasticbeanstalk:application:environment:
  # Update these for your target region:
  AWS_REGION: ap-southeast-1              # Your region
  AWS_DEFAULT_REGION: ap-southeast-1      # Same as above
  S3_REGION: ap-southeast-1               # S3 bucket region
  S3_BUCKET_NAME: ai-prism-logs-xxx-region  # Your bucket
```

#### Step 3: Deploy

```bash
# Option A: AWS Console
1. Go to Elastic Beanstalk Console in your target region
2. Create Application
3. Upload: ai-prism-ALL-REGIONS.zip (470 KB)
4. Wait 10-15 minutes

# Option B: EB CLI
eb init -r YOUR_REGION
eb create
eb deploy
```

#### Step 4: Verify

```bash
# Check region detection
curl http://YOUR-URL/test_s3_connection | jq .

# Expected output:
{
  "primary_region": "ap-southeast-1",
  "bedrock_region": "ap-southeast-1",
  "s3_region": "ap-southeast-1",
  "detection_method": "auto-detected",
  "multi_region_support": true
}
```

---

## Regional Recommendations

### By Use Case

#### Global E-Commerce / SaaS
**Deploy to 3-5 regions for optimal latency**:
- Americas: `us-east-1` (N. Virginia)
- Europe: `eu-west-1` (Ireland)
- Asia: `ap-northeast-1` (Tokyo)
- Australia: `ap-southeast-2` (Sydney)
- South America: `sa-east-1` (São Paulo)

#### Data Residency / Compliance

**Europe (GDPR)**:
- Primary: `eu-central-1` (Frankfurt) or `eu-west-1` (Ireland)
- Backup: `eu-west-2` (London)

**Asia Pacific**:
- India: `ap-south-1` (Mumbai)
- Japan: `ap-northeast-1` (Tokyo)
- Singapore: `ap-southeast-1` (Singapore)
- Australia: `ap-southeast-2` (Sydney)

**Americas**:
- USA: `us-east-1` (N. Virginia) - Best overall
- Canada: `ca-central-1` (Central)
- Brazil: `sa-east-1` (São Paulo)

#### Cost Optimization

**Lowest cost regions** (generally):
1. `us-east-1` (N. Virginia) - Usually cheapest
2. `us-west-2` (Oregon)
3. `eu-west-1` (Ireland)

**Higher cost regions**:
- `ap-southeast-2` (Sydney)
- `sa-east-1` (São Paulo)
- `af-south-1` (Cape Town)

---

## Performance Considerations

### Latency Matrix (Approximate)

**Bedrock API Response Times**:

| Deployment Region | Bedrock Access | Typical Latency |
|------------------|----------------|-----------------|
| **Direct Access** | Same region | 50-100ms |
| **Cross-Region** | Nearby region | 150-300ms |
| **Cross-Continent** | Distant region | 300-500ms |

**Examples**:
- Deploy `us-east-1` → Bedrock `us-east-1`: ~70ms ✅
- Deploy `eu-north-1` → Bedrock `eu-north-1`: ~80ms ✅
- Deploy `ap-southeast-3` → Bedrock `ap-southeast-1`: ~180ms ⚠️
- Deploy `af-south-1` → Bedrock `eu-west-1`: ~350ms ⚠️

### Best Practices

1. **Always deploy to Bedrock-enabled regions when possible** (18 regions available)
2. **If must use non-Bedrock region**, choose one close to a Bedrock region
3. **Consider S3 bucket co-location** for better overall performance
4. **Use CloudFront** for static assets regardless of region

---

## Cost Analysis by Region

### EC2 Pricing (t3.large per hour)

| Region Type | Example Regions | Approx. Cost/Hour |
|------------|----------------|-------------------|
| **Low Cost** | us-east-1, us-west-2, eu-west-1 | $0.0832 |
| **Medium Cost** | ap-southeast-1, eu-central-1 | $0.0930 |
| **High Cost** | ap-southeast-2, sa-east-1 | $0.1045 |

### Monthly Cost Estimate (3x t3.large + ALB + S3)

| Region Category | Monthly Base Cost | Notes |
|----------------|------------------|-------|
| **US East** | ~$200-220 | Lowest cost |
| **Europe** | ~$220-250 | Medium cost |
| **Asia Pacific** | ~$240-280 | Higher cost |
| **South America** | ~$260-300 | Highest cost |

**Plus Bedrock API costs** (pay-per-use, same in all regions)

---

## Monitoring and Observability

### CloudWatch Metrics

For multi-region deployments, track:

1. **Bedrock API Latency** by region
2. **Cross-region call counts**
3. **S3 operation latency**
4. **Error rates** by region

### Example Dashboard

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Bedrock", "Latency", {"stat": "Average", "region": "us-east-1"}],
          ["AWS/Bedrock", "Latency", {"stat": "Average", "region": "eu-west-1"}],
          ["AWS/Bedrock", "Latency", {"stat": "Average", "region": "ap-northeast-1"}]
        ],
        "title": "Bedrock Latency by Region"
      }
    }
  ]
}
```

---

## Migration Between Regions

### Zero-Downtime Migration

```bash
# 1. Deploy to new region
export NEW_REGION="eu-west-1"
eb create ai-prism-${NEW_REGION} --region ${NEW_REGION}

# 2. Test new deployment
curl http://NEW-URL/health

# 3. Copy S3 data (if needed)
aws s3 sync s3://old-bucket s3://new-bucket \
    --source-region OLD_REGION \
    --region NEW_REGION

# 4. Update Route 53 / CloudFront to point to new region
aws route53 change-resource-record-sets ...

# 5. Monitor new region for 24-48 hours

# 6. Terminate old region
eb terminate old-environment --region OLD_REGION
```

---

## Troubleshooting

### Issue: Application Not Working in Non-Bedrock Region

**Symptoms**: Bedrock API calls failing

**Solution**: This is expected. Check logs for:
```
⚠️  Bedrock not available in ap-southeast-3, using cross-region to ap-southeast-1
```

The application automatically handles this. If failures persist:
1. Check IAM permissions for cross-region Bedrock access
2. Verify network connectivity to fallback region
3. Consider deploying to a Bedrock-enabled region

### Issue: High Latency in Non-Bedrock Region

**Symptoms**: Slow response times

**Solution**:
1. Deploy to nearest Bedrock-enabled region instead
2. Or use CloudFront for caching
3. Or accept higher latency for cross-region calls

### Issue: S3 Bucket Region Mismatch

**Symptoms**: S3 operations slow or failing

**Solution**: Application handles this automatically! But to optimize:
1. Create S3 bucket in same region as compute
2. Or use S3 Transfer Acceleration
3. Or replicate bucket to multiple regions

---

## Feature Support Matrix

| Feature | All Regions | Bedrock Regions | Non-Bedrock Regions |
|---------|------------|-----------------|---------------------|
| **Region Detection** | ✅ Yes | ✅ Yes | ✅ Yes |
| **S3 Operations** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Bedrock API** | ✅ Yes (cross-region) | ✅ Yes (direct) | ✅ Yes (cross-region) |
| **Auto-Scaling** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Load Balancing** | ✅ Yes | ✅ Yes | ✅ Yes |
| **CloudWatch Logs** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Optimal Latency** | ⚠️ Varies | ✅ Yes | ⚠️ Higher latency |
| **Cost** | ⚠️ Varies | ✅ Standard | ⚠️ Cross-region charges may apply |

---

## Summary

### What You Have Now

✅ **34 AWS regions** supported globally
✅ **18 regions** with direct Bedrock access
✅ **16 regions** with automatic cross-region fallback
✅ **Automatic region detection** from 5 sources
✅ **Automatic model ID selection** per region
✅ **Cross-region S3 support**
✅ **470 KB deployment package** ready to deploy anywhere
✅ **Complete documentation** for all regions

### Deployment Package

**File**: `ai-prism-ALL-REGIONS.zip` (470 KB)

**Ready to deploy to**:
- ✅ United States (4 regions)
- ✅ Canada (2 regions)
- ✅ Mexico (1 region)
- ✅ South America (1 region)
- ✅ Europe (6 regions)
- ✅ Asia Pacific (14 regions)
- ✅ Middle East (2 regions)
- ✅ Africa (1 region)
- ✅ Israel (1 region)

**Total**: 34 regions across 6 continents!

---

## Next Steps

1. **Choose your target region(s)** from the list above
2. **Review the deployment guide** in this document
3. **Update `.ebextensions/01_environment.config`** with your region
4. **Deploy** using the `ai-prism-ALL-REGIONS.zip` package
5. **Test** using the connection test endpoints
6. **Monitor** using CloudWatch and application logs

---

## Additional Resources

- **Complete Multi-Region Guide**: [MULTI_REGION_DEPLOYMENT_GUIDE.md](MULTI_REGION_DEPLOYMENT_GUIDE.md)
- **Quick Summary**: [REGION_AGNOSTIC_SUMMARY.md](REGION_AGNOSTIC_SUMMARY.md)
- **Region Config Module**: [config/aws_regions.py](config/aws_regions.py)
- **AWS Bedrock Regions**: https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html#bedrock-regions

---

**Your application is now truly global! Deploy anywhere, anytime!** 🌍🚀
