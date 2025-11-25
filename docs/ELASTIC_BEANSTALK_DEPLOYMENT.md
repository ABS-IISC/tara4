# AWS Elastic Beanstalk Deployment Guide

Complete guide for deploying AI-Prism to AWS Elastic Beanstalk.

## Why Elastic Beanstalk?

✅ **Better than App Runner for**:
- Persistent storage (not just /tmp)
- Background workers (Celery/RQ with Redis)
- Custom EC2 instance configurations
- VPC and network control
- SSH access for debugging

## Prerequisites

1. **AWS CLI** installed and configured
2. **EB CLI** installed: `pip install awsebcli`
3. **Git** repository initialized
4. **IAM Role** with permissions:
   - AmazonBedrockFullAccess
   - AmazonS3FullAccess
   - ElasticBeanstalk service roles

## Quick Start (5 Minutes)

### Step 1: Initialize Elastic Beanstalk

```bash
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2

# Initialize EB application
eb init -p python-3.11 ai-prism --region us-east-1

# Create environment
eb create ai-prism-prod \
  --instance-type t3.medium \
  --min-instances 2 \
  --max-instances 10 \
  --envvars FLASK_ENV=production,REDIS_URL=disabled \
  --service-role aws-elasticbeanstalk-service-role \
  --instance-profile aws-elasticbeanstalk-ec2-role
```

### Step 2: Deploy

```bash
# Deploy current code
eb deploy

# Check status
eb status

# Open in browser
eb open

# View logs
eb logs
```

## Detailed Configuration

### 1. Environment Variables

Already configured in `.ebextensions/01_environment.config`:

```yaml
FLASK_ENV: production
PORT: "8000"
REDIS_URL: "disabled"  # Or redis://your-elasticache:6379/0
AWS_REGION: us-east-1
BEDROCK_MODEL_ID: us.anthropic.claude-sonnet-4-5-20250929-v1:0
S3_BUCKET_NAME: felix-s3-bucket
S3_BASE_PATH: tara/
ENABLE_MODEL_FALLBACK: "true"
```

**To modify**: Edit `.ebextensions/01_environment.config` or use:
```bash
eb setenv BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

### 2. Instance Configuration

**Current Settings** (in `.ebextensions/01_environment.config`):
- **Instance Type**: t3.medium (2 vCPU, 4 GB RAM)
- **Auto Scaling**: 2-10 instances
- **Load Balancer**: Application Load Balancer
- **Health Check**: HTTP /health endpoint
- **Deployment**: Rolling with additional batch

**Recommended Configurations**:

| Environment | Instance Type | Min/Max | Monthly Cost |
|-------------|--------------|---------|--------------|
| Development | t3.small | 1/2 | ~$30 |
| Production | t3.medium | 2/10 | ~$120-600 |
| High Traffic | t3.large | 4/20 | ~$480-2400 |

### 3. IAM Roles

#### EC2 Instance Profile

Create role `aws-elasticbeanstalk-ec2-role` with policies:

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

Also attach:
- `AWSElasticBeanstalkWebTier`
- `AWSElasticBeanstalkWorkerTier`
- `AWSElasticBeanstalkMulticontainerDocker`

### 4. Files Included in Deployment

```
.ebextensions/
├── 01_environment.config   # Environment variables & scaling
└── 02_packages.config       # System packages & directories

Procfile                     # Gunicorn start command
gunicorn.conf.py            # Gunicorn configuration
requirements.txt            # Python dependencies
app.py                      # Flask application
```

## Redis/ElastiCache Integration (Optional)

### Without Redis (Current - Synchronous Mode)

```yaml
# .ebextensions/01_environment.config
REDIS_URL: "disabled"
```

Application runs in synchronous mode:
- ✅ Simple setup
- ✅ No additional costs
- ❌ Slower for large documents
- ❌ No background tasks

### With Redis (ElastiCache)

1. **Create ElastiCache Redis Cluster**:
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id ai-prism-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxx
```

2. **Update Environment Variable**:
```bash
# Get Redis endpoint
REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
  --cache-cluster-id ai-prism-redis \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
  --output text)

# Set in EB
eb setenv REDIS_URL="redis://${REDIS_ENDPOINT}:6379/0"
```

3. **Security Group**: Allow port 6379 from EB instances

Application automatically uses Redis when available:
- ✅ Async task processing
- ✅ Faster response times
- ✅ Background workers
- 💰 Additional cost (~$15/month)

## Deployment Commands

### Initial Deployment

```bash
# From project directory
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2

# Initialize (first time only)
eb init

# Create environment
eb create ai-prism-prod

# Deploy
eb deploy
```

### Update Deployment

```bash
# Make changes to code
git add .
git commit -m "Update feature"

# Deploy to EB
eb deploy

# Or deploy specific environment
eb deploy ai-prism-prod
```

### Multiple Environments

```bash
# Create staging environment
eb create ai-prism-staging --instance-type t3.small

# Deploy to staging
eb use ai-prism-staging
eb deploy

# Deploy to production
eb use ai-prism-prod
eb deploy
```

## Monitoring & Debugging

### View Logs

```bash
# Recent logs
eb logs

# Tail logs in real-time
eb logs --stream

# Download full logs
eb logs --all
```

### SSH Access

```bash
# SSH into instance
eb ssh

# Check application
sudo su
cd /var/app/current
tail -f /var/log/gunicorn/error.log
```

### Health Monitoring

```bash
# Check environment health
eb health

# Detailed health
eb health --refresh
```

### CloudWatch Metrics

- Go to **AWS Console → CloudWatch**
- Select **Elastic Beanstalk** namespace
- Available metrics:
  - Request Count
  - Response Time
  - HTTP 4xx/5xx Errors
  - CPU/Memory Usage

## Scaling Configuration

### Auto Scaling Triggers

Configured in `.ebextensions/01_environment.config`:

```yaml
aws:autoscaling:trigger:
  MeasureName: CPUUtilization
  UpperThreshold: 75  # Scale up at 75% CPU
  LowerThreshold: 25  # Scale down at 25% CPU
```

### Manual Scaling

```bash
# Scale to 5 instances
eb scale 5

# Or update in configuration
eb config
# Edit MinSize and MaxSize
```

## Cost Estimation

### Without Redis

| Component | Type | Cost/Month |
|-----------|------|------------|
| EC2 Instances (2x t3.medium) | Compute | ~$120 |
| Load Balancer | Network | ~$25 |
| EBS Storage (40 GB) | Storage | ~$5 |
| Data Transfer (100 GB out) | Network | ~$9 |
| **Total** | | **~$160/month** |

### With Redis

Add ElastiCache: +$15-50/month depending on size

## Troubleshooting

### Issue: Deployment Fails

```bash
# Check deployment logs
eb logs --all

# Common causes:
# 1. Missing dependencies
pip install -r requirements.txt

# 2. Syntax errors
python3 -m py_compile app.py

# 3. Permission issues
# Check IAM role has Bedrock + S3 access
```

### Issue: Health Check Failing

```bash
# Test health endpoint locally
curl http://your-env.elasticbeanstalk.com/health

# Check gunicorn logs
eb ssh
sudo tail -f /var/log/gunicorn/error.log

# Verify port 8000
sudo netstat -tlnp | grep 8000
```

### Issue: 502 Bad Gateway

**Causes**:
1. Gunicorn not starting
2. Wrong port configuration
3. Application crash during startup

**Fix**:
```bash
eb ssh
cd /var/app/current

# Test manually
sudo -u webapp gunicorn --config gunicorn.conf.py app:app

# Check logs
tail -f /var/log/gunicorn/error.log
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy-eb.yml`:

```yaml
name: Deploy to Elastic Beanstalk

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install EB CLI
        run: pip install awsebcli

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy to EB
        run: |
          eb init -p python-3.11 ai-prism --region us-east-1
          eb use ai-prism-prod
          eb deploy --staged
```

## Comparison: Elastic Beanstalk vs App Runner

| Feature | Elastic Beanstalk | App Runner |
|---------|-------------------|------------|
| **Filesystem** | Persistent (EC2) | /tmp only (ephemeral) |
| **Background Workers** | ✅ Yes (with Redis) | ❌ No |
| **SSH Access** | ✅ Yes | ❌ No |
| **Auto Scaling** | ✅ Full control | ✅ Automatic |
| **Load Balancer** | ✅ ALB/NLB | ✅ Automatic |
| **VPC Control** | ✅ Full control | ⚠️ Limited |
| **Cost** | ~$160/month | ~$50/month |
| **Setup Complexity** | Medium | Low |
| **Best For** | Production apps | Simple APIs |

## Summary

**Elastic Beanstalk is better for**:
- ✅ Production applications with complex requirements
- ✅ Need for background task processing
- ✅ Persistent storage requirements
- ✅ Custom network configurations
- ✅ Team needing SSH access for debugging

**Current Status**:
- ✅ All configuration files ready
- ✅ Gunicorn configured for production
- ✅ Health checks configured
- ✅ Auto-scaling configured
- ✅ Compatible with Redis (optional)
- ✅ Works without Redis (synchronous mode)

**Ready to Deploy**: Just run `eb init` and `eb create`!

---

**Created**: 2025-11-26
**Status**: Production-ready
**Tested**: Configuration validated
