# AI-Prism Multi-Region Deployment Guide

## Overview

AI-Prism is now **fully region-agnostic** and can be deployed to **ANY AWS region** with Amazon Bedrock support. The application automatically detects the deployment region and configures itself accordingly.

---

## Supported AWS Regions

### Bedrock-Enabled Regions

The application supports **12 AWS regions** where Amazon Bedrock with Claude models is available:

#### United States
- **us-east-1** (N. Virginia) - **RECOMMENDED** (Best Bedrock support)
- **us-west-2** (Oregon)

#### Europe
- **eu-central-1** (Frankfurt) - **RECOMMENDED for EU**
- **eu-west-1** (Ireland)
- **eu-west-2** (London)
- **eu-west-3** (Paris)

#### Asia Pacific
- **ap-south-1** (Mumbai)
- **ap-northeast-1** (Tokyo) - **RECOMMENDED for APAC**
- **ap-southeast-1** (Singapore)
- **ap-southeast-2** (Sydney)

#### Other Regions
- **ca-central-1** (Canada Central)
- **sa-east-1** (São Paulo)

### Region Selection Guide

**Choose your region based on:**

1. **User Location** - Deploy closest to your users for lowest latency
2. **Data Residency** - Meet regulatory requirements (GDPR, data sovereignty)
3. **Cost** - Pricing varies slightly by region
4. **Bedrock Availability** - Must be one of the 12 supported regions above

**Regional Model IDs:**
- US regions: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- EU regions: `eu.anthropic.claude-sonnet-4-5-20250929-v1:0`
- APAC regions: `apac.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Other regions: `anthropic.claude-sonnet-4-5-20250929-v1:0`

The application **automatically selects** the correct model ID based on your deployment region.

---

## Architecture Features

### Automatic Region Detection

The application detects region from multiple sources (in priority order):

1. **AWS_REGION** environment variable (explicit override)
2. **EC2 Instance Metadata** (when running on EC2/Elastic Beanstalk)
3. **AWS CLI Configuration** (~/.aws/config)
4. **boto3 Session Default**
5. **Fallback to us-east-1** if detection fails

### Cross-Region Support

- **S3 Buckets**: Automatically detects S3 bucket region and uses it
- **Bedrock API**: Routes to correct regional endpoint
- **Multi-Region Buckets**: Supports S3 buckets in different regions from compute

### Region Configuration Module

Located at `config/aws_regions.py`, this module provides:

- Complete list of all 28+ AWS regions
- Bedrock-supported region identification
- Automatic region detection
- Model ID mapping per region
- Region validation and health checks
- Cross-region inference support

---

## Deployment Steps

### Method 1: AWS Elastic Beanstalk Console (Recommended)

#### 1. Create S3 Bucket (if needed)

```bash
# Replace REGION with your target region (e.g., us-east-1)
export TARGET_REGION="us-east-1"
export BUCKET_NAME="ai-prism-logs-${AWS_ACCOUNT_ID}-${TARGET_REGION}"

# Create bucket
aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $TARGET_REGION \
    --create-bucket-configuration LocationConstraint=$TARGET_REGION

# Note: For us-east-1, omit the LocationConstraint
# aws s3api create-bucket --bucket $BUCKET_NAME --region us-east-1
```

#### 2. Update .ebextensions Configuration

Edit `.ebextensions/01_environment.config`:

```yaml
aws:elasticbeanstalk:application:environment:
  # Update these 3 variables for your region:
  AWS_REGION: us-east-1                  # Your target region
  AWS_DEFAULT_REGION: us-east-1          # Same as AWS_REGION
  S3_REGION: us-east-1                   # Region where S3 bucket is located
  S3_BUCKET_NAME: ai-prism-logs-123456789-us-east-1  # Your bucket name

  # Optional: Override model ID (auto-selected if not set)
  # BEDROCK_MODEL_ID: us.anthropic.claude-sonnet-4-5-20250929-v1:0
```

#### 3. Create Deployment Package

```bash
# Ensure you're in the project directory
cd /path/to/ai-prism

# Create deployment package
zip -r ai-prism-${TARGET_REGION}.zip \
  app.py \
  main.py \
  Procfile \
  gunicorn.conf.py \
  requirements.txt \
  config/ \
  core/ \
  utils/ \
  static/ \
  templates/ \
  .ebextensions/ \
  -x "*.pyc" "__pycache__/*" "*.git*" "venv/*" "*.log"

echo "Package created: ai-prism-${TARGET_REGION}.zip"
```

#### 4. Deploy via AWS Console

1. **Go to Elastic Beanstalk Console**:
   ```
   https://console.aws.amazon.com/elasticbeanstalk/home?region=YOUR_REGION
   ```

2. **Create Application**:
   - Click "Create Application"
   - Application name: `AI-Prism`
   - Platform: Python 3.11
   - Upload code: `ai-prism-${TARGET_REGION}.zip`

3. **Configure Environment**:
   - Preset: High availability
   - Instance type: t3.large (for 100+ users)
   - Min instances: 3
   - Max instances: 15

4. **Set IAM Roles**:
   - Service role: `aws-elasticbeanstalk-service-role`
   - Instance profile: `aws-elasticbeanstalk-ec2-role`
   - Ensure role has:
     - AmazonBedrockFullAccess
     - AmazonS3FullAccess
     - CloudWatchAgentServerPolicy

5. **Create Environment** (takes 10-15 minutes)

#### 5. Verify Deployment

```bash
# Get environment URL
export EB_URL=$(aws elasticbeanstalk describe-environments \
    --region $TARGET_REGION \
    --query 'Environments[0].CNAME' \
    --output text)

# Test S3 connection
curl -s "http://${EB_URL}/test_s3_connection" | jq .

# Expected output:
# {
#   "s3_status": {
#     "connected": true,
#     "bucket_accessible": true,
#     "bucket_name": "ai-prism-logs-123456789-us-east-1",
#     "primary_region": "us-east-1",
#     "primary_region_name": "US East (N. Virginia)",
#     "s3_region": "us-east-1",
#     "bedrock_region": "us-east-1",
#     "detection_method": "auto-detected",
#     "multi_region_support": true
#   }
# }
```

---

### Method 2: AWS CLI / EB CLI

#### Prerequisites

```bash
# Install EB CLI
pip install awsebcli

# Configure AWS credentials
aws configure --profile ai-prism
```

#### Deployment Script

```bash
#!/bin/bash
# deploy_to_region.sh

# Configuration
TARGET_REGION="us-east-1"  # Change this to your target region
APP_NAME="AI-Prism"
ENV_NAME="ai-prism-${TARGET_REGION}"
INSTANCE_TYPE="t3.large"
MIN_INSTANCES=3
MAX_INSTANCES=15

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="ai-prism-logs-${AWS_ACCOUNT_ID}-${TARGET_REGION}"

echo "Deploying AI-Prism to ${TARGET_REGION}..."

# 1. Create S3 bucket if it doesn't exist
echo "Step 1: Creating S3 bucket..."
if [ "$TARGET_REGION" = "us-east-1" ]; then
    aws s3api create-bucket --bucket $BUCKET_NAME --region $TARGET_REGION 2>/dev/null || echo "Bucket already exists"
else
    aws s3api create-bucket \
        --bucket $BUCKET_NAME \
        --region $TARGET_REGION \
        --create-bucket-configuration LocationConstraint=$TARGET_REGION 2>/dev/null || echo "Bucket already exists"
fi

# 2. Update .ebextensions with region
echo "Step 2: Updating configuration for ${TARGET_REGION}..."
sed -i.bak "s/AWS_REGION: .*/AWS_REGION: ${TARGET_REGION}/" .ebextensions/01_environment.config
sed -i.bak "s/S3_REGION: .*/S3_REGION: ${TARGET_REGION}/" .ebextensions/01_environment.config
sed -i.bak "s/S3_BUCKET_NAME: .*/S3_BUCKET_NAME: ${BUCKET_NAME}/" .ebextensions/01_environment.config

# 3. Initialize EB application
echo "Step 3: Initializing Elastic Beanstalk..."
eb init -p python-3.11 $APP_NAME --region $TARGET_REGION

# 4. Create environment
echo "Step 4: Creating environment (this takes 10-15 minutes)..."
eb create $ENV_NAME \
    --instance-type $INSTANCE_TYPE \
    --min-instances $MIN_INSTANCES \
    --max-instances $MAX_INSTANCES \
    --elb-type application \
    --scale $MIN_INSTANCES \
    --region $TARGET_REGION

# 5. Open application
echo "Step 5: Opening application..."
eb open --region $TARGET_REGION

echo "Deployment complete!"
echo "Environment URL: $(eb status --region $TARGET_REGION | grep CNAME | awk '{print $2}')"
```

---

### Method 3: Infrastructure as Code (CloudFormation)

For production deployments, use CloudFormation or Terraform. Example CloudFormation template:

```yaml
# cloudformation-ai-prism.yaml
Parameters:
  TargetRegion:
    Type: String
    Default: us-east-1
    AllowedValues:
      - us-east-1
      - us-west-2
      - eu-central-1
      - eu-west-1
      - eu-west-2
      - eu-west-3
      - ap-south-1
      - ap-northeast-1
      - ap-southeast-1
      - ap-southeast-2
      - ca-central-1
      - sa-east-1
    Description: AWS region for deployment

Resources:
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'ai-prism-logs-${AWS::AccountId}-${TargetRegion}'
      VersioningConfiguration:
        Status: Enabled

  ElasticBeanstalkApplication:
    Type: AWS::ElasticBeanstalk::Application
    Properties:
      ApplicationName: AI-Prism

  ElasticBeanstalkEnvironment:
    Type: AWS::ElasticBeanstalk::Environment
    Properties:
      ApplicationName: !Ref ElasticBeanstalkApplication
      EnvironmentName: !Sub 'ai-prism-${TargetRegion}'
      SolutionStackName: '64bit Amazon Linux 2023 v4.0.0 running Python 3.11'
      OptionSettings:
        - Namespace: aws:elasticbeanstalk:application:environment
          OptionName: AWS_REGION
          Value: !Ref TargetRegion
        - Namespace: aws:elasticbeanstalk:application:environment
          OptionName: S3_BUCKET_NAME
          Value: !Ref S3Bucket
        # ... additional settings
```

---

## Region-Specific Configuration

### Environment Variables

The application requires these environment variables (auto-configured in .ebextensions):

#### Required Variables
```bash
AWS_REGION=us-east-1                    # Deployment region
AWS_DEFAULT_REGION=us-east-1            # Same as AWS_REGION
S3_BUCKET_NAME=ai-prism-logs-xxx-region # S3 bucket name
S3_REGION=us-east-1                     # S3 bucket region
FLASK_ENV=production                     # Production mode
PORT=8000                                # Application port
```

#### Optional Variables (with Auto-Detection)
```bash
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0  # Auto-selected
BEDROCK_MAX_TOKENS=4096                 # Claude token limit
BEDROCK_TEMPERATURE=0.7                  # Response randomness
```

### IAM Permissions

The instance profile role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:HeadBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::ai-prism-logs-*",
        "arn:aws:s3:::ai-prism-logs-*/*"
      ]
    },
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

---

## Multi-Region Deployment Strategies

### Strategy 1: Single Region (Simplest)

**Best for:** Single geographic market, small to medium scale

```
User → CloudFront → ELB → EC2 (us-east-1) → Bedrock (us-east-1)
                                           → S3 (us-east-1)
```

**Pros:**
- Simple architecture
- Lowest cost
- Easy to manage

**Cons:**
- Higher latency for distant users
- Single point of failure

### Strategy 2: Multi-Region Active-Passive

**Best for:** Disaster recovery, high availability

```
Primary:   Users → CloudFront → ELB → EC2 (us-east-1) → Bedrock (us-east-1)
                                                        → S3 (us-east-1 primary)
                                                        → S3 (eu-west-1 replica)

Secondary: Users → CloudFront → ELB → EC2 (eu-west-1) → Bedrock (eu-west-1)
(Standby)                                              → S3 (eu-west-1)
```

**Setup:**
1. Deploy to primary region (e.g., us-east-1)
2. Set up S3 cross-region replication
3. Deploy to secondary region (e.g., eu-west-1)
4. Configure Route 53 failover routing

**Pros:**
- Disaster recovery
- Regional data compliance
- Low RTO/RPO

**Cons:**
- Higher cost (2x resources)
- Complex failover management

### Strategy 3: Multi-Region Active-Active

**Best for:** Global user base, lowest latency worldwide

```
US Users   → CloudFront → ELB → EC2 (us-east-1) → Bedrock (us-east-1)
                                                  → S3 (us-east-1)

EU Users   → CloudFront → ELB → EC2 (eu-west-1) → Bedrock (eu-west-1)
                                                  → S3 (eu-west-1)

APAC Users → CloudFront → ELB → EC2 (ap-northeast-1) → Bedrock (ap-northeast-1)
                                                       → S3 (ap-northeast-1)
```

**Setup:**
1. Deploy to multiple regions (3-5 regions)
2. Set up S3 in each region (or use cross-region replication)
3. Configure Route 53 geolocation routing
4. Use DynamoDB Global Tables for session data (optional)

**Pros:**
- Lowest latency worldwide
- Regional data residency
- True high availability

**Cons:**
- Highest cost (3-5x resources)
- Complex session management
- Requires global database

---

## Region Migration

### Migrating Between Regions

If you need to move from one region to another:

#### 1. Create Resources in New Region

```bash
export NEW_REGION="eu-west-1"
export NEW_BUCKET="ai-prism-logs-${AWS_ACCOUNT_ID}-${NEW_REGION}"

# Create S3 bucket
aws s3api create-bucket \
    --bucket $NEW_BUCKET \
    --region $NEW_REGION \
    --create-bucket-configuration LocationConstraint=$NEW_REGION
```

#### 2. Copy Data from Old Region

```bash
export OLD_REGION="us-east-1"
export OLD_BUCKET="ai-prism-logs-${AWS_ACCOUNT_ID}-${OLD_REGION}"

# Copy all data
aws s3 sync s3://${OLD_BUCKET} s3://${NEW_BUCKET} \
    --source-region $OLD_REGION \
    --region $NEW_REGION
```

#### 3. Update Configuration

```bash
# Update .ebextensions/01_environment.config
sed -i "s/AWS_REGION: ${OLD_REGION}/AWS_REGION: ${NEW_REGION}/" .ebextensions/01_environment.config
sed -i "s/S3_REGION: ${OLD_REGION}/S3_REGION: ${NEW_REGION}/" .ebextensions/01_environment.config
sed -i "s/S3_BUCKET_NAME: ${OLD_BUCKET}/S3_BUCKET_NAME: ${NEW_BUCKET}/" .ebextensions/01_environment.config
```

#### 4. Deploy to New Region

```bash
# Create new environment
eb create ai-prism-${NEW_REGION} --region $NEW_REGION

# Test new environment
curl "http://$(eb status --region $NEW_REGION | grep CNAME | awk '{print $2}')/health"
```

#### 5. Cutover Traffic

Update Route 53 or CloudFront to point to new region.

#### 6. Decommission Old Region

```bash
# Terminate old environment
eb terminate ai-prism-${OLD_REGION} --region $OLD_REGION

# Keep S3 bucket for archival (or delete after backup)
```

---

## Troubleshooting

### Region Detection Issues

**Problem**: Application not detecting correct region

**Solution**:
```bash
# Check EC2 metadata
curl http://169.254.169.254/latest/meta-data/placement/region

# Force region via environment variable
export AWS_REGION=us-east-1

# Check application logs
eb logs --region YOUR_REGION
```

### Bedrock Not Available

**Problem**: "Bedrock not available in region"

**Solution**:
1. Verify region supports Bedrock:
   ```bash
   aws bedrock list-foundation-models --region YOUR_REGION
   ```

2. Check IAM permissions for Bedrock

3. Use cross-region inference (automatic fallback)

### S3 Bucket Region Mismatch

**Problem**: S3 bucket in different region from compute

**Solution**: The application automatically handles this! It detects the S3 bucket's region and uses it for S3 operations.

To verify:
```bash
# Check bucket location
aws s3api get-bucket-location --bucket YOUR_BUCKET
```

### Model ID Issues

**Problem**: Wrong model ID for region

**Solution**: The application auto-selects model ID. To override:
```bash
# In .ebextensions/01_environment.config
BEDROCK_MODEL_ID: us.anthropic.claude-sonnet-4-5-20250929-v1:0  # For US regions
BEDROCK_MODEL_ID: eu.anthropic.claude-sonnet-4-5-20250929-v1:0  # For EU regions
BEDROCK_MODEL_ID: apac.anthropic.claude-sonnet-4-5-20250929-v1:0  # For APAC regions
```

---

## Cost Optimization

### Cost by Region

Monthly costs for 3x t3.large instances (100+ users):

| Region | EC2 | ALB | S3 | Bedrock* | Data Transfer | Total/Month |
|--------|-----|-----|----|---------|--------------| ------------|
| us-east-1 | $130 | $18 | $5 | Variable | $10 | ~$165 + Bedrock |
| us-west-2 | $135 | $18 | $5 | Variable | $10 | ~$170 + Bedrock |
| eu-central-1 | $145 | $20 | $6 | Variable | $12 | ~$185 + Bedrock |
| ap-southeast-1 | $140 | $19 | $5 | Variable | $11 | ~$175 + Bedrock |

*Bedrock costs vary by usage (input/output tokens)

### Cost Reduction Tips

1. **Use Spot Instances** (50-70% savings):
   ```yaml
   aws:ec2:instances:
     SpotFleetOnDemandBase: 1
     SpotFleetOnDemandAboveBasePercentage: 0
     EnableSpot: true
   ```

2. **Right-Size Instances**:
   - 10-50 users: t3.medium (2 GB RAM)
   - 50-100 users: t3.large (8 GB RAM)
   - 100-200 users: t3.xlarge (16 GB RAM)

3. **S3 Lifecycle Policies**:
   ```bash
   aws s3api put-bucket-lifecycle-configuration \
       --bucket YOUR_BUCKET \
       --lifecycle-configuration file://lifecycle.json
   ```

4. **Bedrock Token Optimization**:
   - Use BEDROCK_MAX_TOKENS wisely
   - Enable result caching where possible

---

## Monitoring and Observability

### CloudWatch Metrics

Enable these metrics for each region:

```yaml
aws:elasticbeanstalk:cloudwatch:logs:
  StreamLogs: true
  RetentionInDays: 7

aws:elasticbeanstalk:cloudwatch:logs:health:
  HealthStreamingEnabled: true
```

### Multi-Region Dashboard

Create CloudWatch dashboard showing metrics across all regions:

```bash
aws cloudwatch put-dashboard \
    --dashboard-name AI-Prism-Global \
    --dashboard-body file://dashboard.json
```

### Alarms

Set up CloudWatch alarms:

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
    --alarm-name ai-prism-${REGION}-errors \
    --metric-name 4XXError \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 300 \
    --threshold 100 \
    --comparison-operator GreaterThanThreshold
```

---

## Best Practices

### 1. Region Selection
- Choose regions closest to users
- Consider data residency requirements
- Verify Bedrock availability first

### 2. Deployment
- Always test in dev/staging environment first
- Use blue-green deployments for production
- Keep deployment packages under 500 MB

### 3. Configuration Management
- Use AWS Systems Manager Parameter Store for secrets
- Version control your .ebextensions
- Document region-specific customizations

### 4. Monitoring
- Set up CloudWatch alarms for each region
- Monitor Bedrock quotas and limits
- Track cross-region latency

### 5. Security
- Use IAM roles, never hard-code credentials
- Enable S3 bucket encryption
- Use VPC endpoints for Bedrock (optional)

---

## Support and Resources

### Official Documentation
- [AWS Bedrock Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html#bedrock-regions)
- [Elastic Beanstalk Multi-Region](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.managing.vpc.html)
- [Claude Model IDs](https://docs.anthropic.com/claude/docs/models-overview)

### Application Files
- Region config: `config/aws_regions.py`
- Deployment config: `.ebextensions/01_environment.config`
- S3 manager: `utils/s3_export_manager.py`
- App config: `app.py` (SimpleModelConfig class)

### Testing Region Configuration

```python
# Test region detection locally
python3 -c "
from config.aws_regions import get_region_config, validate_region_setup

config = get_region_config()
print(f'Region: {config[\"region\"]}')
print(f'Region Name: {config[\"region_name\"]}')
print(f'Bedrock Region: {config[\"bedrock_region\"]}')
print(f'Model ID: {config[\"model_id\"]}')

is_valid, errors = validate_region_setup()
print(f'Valid: {is_valid}')
if errors:
    print(f'Errors: {errors}')
"
```

---

## Quick Reference

### Deployment Package Contents
```
ai-prism-REGION-AGNOSTIC.zip (470 KB)
├── app.py                      # Main Flask application
├── main.py                     # Entry point
├── Procfile                    # Gunicorn config
├── gunicorn.conf.py            # Gunicorn settings
├── requirements.txt            # Python dependencies
├── config/
│   └── aws_regions.py         # ✨ NEW: Region configuration
├── utils/
│   └── s3_export_manager.py   # ✨ UPDATED: Region-agnostic S3
├── .ebextensions/
│   └── 01_environment.config  # ✨ UPDATED: Region variables
└── [other files...]
```

### Key Commands

```bash
# Deploy to specific region
eb create ai-prism-REGION --region REGION

# Update existing environment
eb deploy --region REGION

# Check environment status
eb status --region REGION

# View logs
eb logs --region REGION

# Terminate environment
eb terminate ENV_NAME --region REGION

# List all environments across regions
for region in us-east-1 us-west-2 eu-west-1; do
    echo "Region: $region"
    eb list --region $region
done
```

---

## Changelog

### Version 2.0.0 - Multi-Region Support
- ✅ Added centralized region configuration (`config/aws_regions.py`)
- ✅ Updated S3 export manager for region-agnostic operations
- ✅ Updated Flask app for automatic region detection
- ✅ Enhanced connection test endpoints with region info
- ✅ Updated .ebextensions for region flexibility
- ✅ Added support for all 12 Bedrock regions
- ✅ Automatic model ID selection per region
- ✅ Cross-region S3 bucket support
- ✅ Region validation and health checks

### Migration from v1.x
If upgrading from a region-specific deployment:
1. No code changes needed in your application
2. Update .ebextensions with new region variables
3. Redeploy using new package
4. Application automatically detects and uses correct region

---

**Ready to deploy?** Choose your target region and follow the deployment steps above!

For issues or questions, check the troubleshooting section or review application logs.
