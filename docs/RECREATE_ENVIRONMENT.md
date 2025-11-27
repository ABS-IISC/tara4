# Recreate Elastic Beanstalk Environment - Complete Guide

## What Happened

Your Elastic Beanstalk environment **AI-Prism1** in **eu-north-1** has been **terminated/deleted**. This likely happened because:
- The deployment encountered critical errors (HTTP 5xx)
- The environment health went to "Severe" and couldn't recover
- Either automatic cleanup or manual termination occurred

## Current Status

```
✅ Fixed Code Package Ready: ai-prism-eb-FIXED-S3-CLAUDE.zip (464 KB)
✅ S3 Bucket Exists: ai-prism-logs-600222957378-eu
✅ IAM Role Exists: aws-elasticbeanstalk-ec2-role
❌ EB Application: DELETED (needs recreation)
❌ EB Environment: DELETED (needs recreation)
```

---

## Option 1: AWS Console (Easiest - Recommended)

### Step 1: Create New Elastic Beanstalk Application

1. **Go to Elastic Beanstalk Console**:
   - URL: https://eu-north-1.console.aws.amazon.com/elasticbeanstalk/home?region=eu-north-1
   - Click **"Create Application"**

2. **Application Settings**:
   ```
   Application name: AI-Prism1
   Platform: Python
   Platform branch: Python 3.11 running on 64bit Amazon Linux 2023
   Platform version: (Latest - let it auto-select)
   ```

3. **Application Code**:
   - Select: **"Upload your code"**
   - Click **"Choose file"**
   - Select: `ai-prism-eb-FIXED-S3-CLAUDE.zip`
   - Version label: `fixed-s3-claude-v1`

4. **Presets**:
   - Select: **"High availability"** (for 100+ users)

5. **Click "Next"** to configure service access

### Step 2: Configure Service Access

1. **Service Role**:
   - Select: **"Use an existing service role"**
   - Service role: `aws-elasticbeanstalk-service-role` (should exist)
   - If not, create it with these permissions:
     - AWSElasticBeanstalkEnhancedHealth
     - AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy

2. **EC2 Instance Profile**:
   - Select: **"Use an existing instance profile"**
   - Instance profile: `aws-elasticbeanstalk-ec2-role`
   - Verify it has these policies:
     - AmazonBedrockFullAccess
     - AmazonS3FullAccess
     - CloudWatchAgentServerPolicy

3. **Click "Next"**

### Step 3: Configure Networking, Database, and Tags (Skip)

- **VPC**: Default VPC is fine
- **Database**: Skip (not needed)
- Click **"Next"**

### Step 4: Configure Instance Traffic and Scaling

#### **Instances**:
```
Root volume type: General Purpose (SSD)
Size: 20 GB
Instance types: t3.large (2 vCPU, 8 GB RAM)
IMDSv1: Deactivated (use IMDSv2)
```

#### **Capacity**:
```
Environment type: Load balanced
Min instances: 3
Max instances: 15
Fleet composition: On-Demand instances
Architecture: x86_64
```

#### **Scaling Triggers**:
```
Metric: CPUUtilization
Statistic: Average
Unit: Percent
Period: 5 minutes
Breach duration: 5 minutes
Upper threshold: 70
Scale up increment: 2
Lower threshold: 20
Scale down increment: -1
```

#### **Load Balancer**:
```
Load balancer type: Application Load Balancer
Visibility: Public
```

#### **Processes**:
```
Name: default
Port: 80
Protocol: HTTP
Health check path: /health
Timeout: 5 seconds
Interval: 30 seconds
Healthy threshold: 2
Unhealthy threshold: 3
Deregistration delay: 20 seconds
Stickiness: Disabled
```

Click **"Next"**

### Step 5: Configure Updates, Monitoring, and Logging

#### **Monitoring**:
```
✅ Enable enhanced health reporting
Health reporting system type: Enhanced
```

#### **Managed Updates**:
```
✅ Enable managed platform updates
Update level: Minor and patch
```

#### **Platform Updates**:
```
✅ Enable rolling updates
Deployment policy: Rolling
Batch size type: Percentage
Batch size: 33%
```

#### **Logging**:
```
✅ Enable log streaming to CloudWatch Logs
Retention: 7 days
✅ Enable instance log streaming
✅ Enable environment health streaming
```

Click **"Next"**

### Step 6: Review and Create

1. **Review all settings**
2. Click **"Submit"**

3. **Wait 10-15 minutes** for environment creation

---

## Step 7: CRITICAL - Add Environment Variables

**IMPORTANT**: After environment is created and shows "Ok" status, you MUST add environment variables:

1. Go to your environment
2. Click **"Configuration"** in left sidebar
3. Scroll to **"Software"** category
4. Click **"Edit"**
5. Scroll down to **"Environment properties"**
6. Add these **17 variables**:

```bash
# Core AWS Configuration
AWS_REGION=eu-north-1
AWS_DEFAULT_REGION=eu-north-1

# S3 Configuration
S3_BUCKET_NAME=ai-prism-logs-600222957378-eu
S3_BASE_PATH=Logs and data/
S3_REGION=eu-north-1

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_REGION=eu-north-1

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
PORT=8000

# Document Processing
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=pdf,txt,docx,doc,xlsx,xls,csv

# Claude Rate Limits
CLAUDE_MAX_RETRIES=3
CLAUDE_RETRY_DELAY=2
CLAUDE_TIMEOUT=300
```

7. Click **"Apply"**
8. Wait 3-5 minutes for environment to update

---

## Step 8: Verify Deployment

### 1. Check Environment Status
```
Status: Ready
Health: Ok (Green)
Running version: fixed-s3-claude-v1
```

### 2. Get Application URL
From Elastic Beanstalk console, copy the environment URL:
```
http://[environment-name].eu-north-1.elasticbeanstalk.com
```

### 3. Test S3 Connection
Visit: `http://[your-url]/test-s3-connection`

**Expected Result**:
```json
{
  "aws_connection": true,
  "bucket_accessible": true,
  "bucket_name": "ai-prism-logs-600222957378-eu",
  "region": "eu-north-1",
  "connection_type": "AWS Bedrock SDK (boto3)",
  "credentials_source": "IAM Role (Elastic Beanstalk)",
  "environment_variables": {
    "S3_BUCKET_NAME": "ai-prism-logs-600222957378-eu",
    "S3_REGION": "eu-north-1",
    "AWS_REGION": "eu-north-1",
    "FLASK_ENV": "production"
  }
}
```

### 4. Check Application Logs
View logs from console or run:
```bash
aws elasticbeanstalk request-environment-info \
    --region eu-north-1 \
    --environment-name [your-env-name] \
    --info-type tail

# Wait 2 minutes, then retrieve:
aws elasticbeanstalk retrieve-environment-info \
    --region eu-north-1 \
    --environment-name [your-env-name] \
    --info-type tail
```

**Expected in logs**:
```
✅ AWS environment detected - using IAM role credentials
   S3 Bucket: ai-prism-logs-600222957378-eu
   S3 Region: eu-north-1
✅ S3 connection established to bucket: ai-prism-logs-600222957378-eu
✅ Model Configuration:
   Region: eu-north-1
   Model: anthropic.claude-sonnet-4-5-20250929-v1:0
```

---

## Option 2: AWS CLI (Advanced)

If you prefer CLI, install EB CLI first:

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 AI-Prism1 --region eu-north-1

# Create environment
eb create ai-prism-env \
    --instance-type t3.large \
    --min-instances 3 \
    --max-instances 15 \
    --elb-type application \
    --scale 3 \
    --envvars AWS_REGION=eu-north-1,S3_BUCKET_NAME=ai-prism-logs-600222957378-eu,S3_REGION=eu-north-1,BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-5-20250929-v1:0,FLASK_ENV=production,PORT=8000

# Deploy
eb deploy
```

---

## Troubleshooting

### If Environment Creation Fails

1. **Check IAM Roles**:
   ```bash
   aws iam get-role --role-name aws-elasticbeanstalk-service-role
   aws iam get-role --role-name aws-elasticbeanstalk-ec2-role
   ```

2. **Check S3 Bucket**:
   ```bash
   aws s3 ls s3://ai-prism-logs-600222957378-eu --region eu-north-1
   ```

3. **Check Bedrock Access**:
   ```bash
   aws bedrock list-foundation-models --region eu-north-1 --query 'modelSummaries[?contains(modelId, `claude-sonnet-4-5`)]'
   ```

### If S3 Connection Still Fails After Deployment

1. Verify environment variables are set correctly
2. Check IAM role has `AmazonS3FullAccess` policy
3. Check application logs for error messages
4. Verify S3 bucket exists and is in correct region

---

## What Was Fixed in This Package

The `ai-prism-eb-FIXED-S3-CLAUDE.zip` contains these critical fixes:

1. **utils/s3_export_manager.py**:
   - Reads `S3_BUCKET_NAME` from environment (was hardcoded to `felix-s3-bucket`)
   - Reads `S3_REGION` from environment (was hardcoded)
   - Reads `S3_BASE_PATH` from environment
   - Properly detects Elastic Beanstalk environment

2. **app.py**:
   - Correct region fallback: `eu-north-1` (was `us-east-2`)
   - Enhanced S3 connection test with environment variable debugging
   - Correct model ID format for Bedrock

3. **.ebextensions/01_environment.config**:
   - Optimized for 100+ concurrent users
   - t3.large instances (8 GB RAM)
   - 3-15 instance auto-scaling
   - Gevent workers for concurrency
   - 10-minute ALB timeout for long Claude API calls

---

## Cost Estimate

With this configuration (100+ users):
- **EC2 (3x t3.large)**: ~$150/month
- **Application Load Balancer**: ~$20/month
- **S3 Storage**: ~$5/month
- **Bedrock API (Claude)**: Pay-per-use (varies by usage)
- **Data Transfer**: ~$10-20/month

**Total**: ~$200-250/month base + Bedrock API costs

---

## Next Steps

1. ✅ Read this guide
2. ⏳ Create new environment via AWS Console (Option 1)
3. ⏳ Add environment variables after creation
4. ⏳ Test S3 connection
5. ⏳ Test document analysis feature
6. ⏳ Monitor for 24 hours

## Need Help?

If you encounter issues:
1. Check CloudWatch logs
2. Verify IAM roles and policies
3. Test S3 and Bedrock access from AWS CLI
4. Review Elastic Beanstalk events in console
