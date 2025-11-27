# Complete AWS Lightsail Deployment Guide
## AI-Prism Flask Application - Simple Container Deployment

**Version:** 1.0
**Date:** November 25, 2025
**Estimated Time:** 30-45 minutes
**Difficulty:** Beginner-Friendly

---

## Table of Contents

1. [Why Lightsail?](#why-lightsail)
2. [Prerequisites](#prerequisites)
3. [Step 1: Prepare Docker Image](#step-1-prepare-docker-image)
4. [Step 2: Push to Container Registry](#step-2-push-to-container-registry)
5. [Step 3: Create Lightsail Container Service](#step-3-create-lightsail-container-service)
6. [Step 4: Deploy Application](#step-4-deploy-application)
7. [Step 5: Configure Custom Domain](#step-5-configure-custom-domain)
8. [Step 6: Setup Redis (Optional)](#step-6-setup-redis-optional)
9. [Step 7: Monitoring & Logs](#step-7-monitoring--logs)
10. [Scaling & Optimization](#scaling--optimization)
11. [Troubleshooting](#troubleshooting)
12. [Ongoing Operations](#ongoing-operations)

---

## Why Lightsail?

### Perfect For
- ✅ MVP and prototypes
- ✅ Small to medium applications
- ✅ Predictable monthly costs ($10-80)
- ✅ Learning AWS without complexity
- ✅ Teams without dedicated DevOps

### Advantages
- 🎯 **Simplicity:** Deploy in 30 minutes
- 💰 **Cost:** Fixed pricing, no surprises
- 🔧 **Managed:** AWS handles infrastructure
- 📊 **Included:** Load balancer, SSL, CDN
- 🚀 **Quick Start:** Perfect for your Flask + Claude app

### Limitations
- ⚠️ Manual scaling (max 3 nodes per service)
- ⚠️ Basic monitoring (vs CloudWatch)
- ⚠️ Limited to specific regions
- ⚠️ Not for massive scale (>50K req/day)

**Bottom Line:** Best choice for MVP and budget-conscious deployments.

---

## Prerequisites

### Required Tools
```bash
# 1. AWS CLI
aws --version
# If not installed: pip install awscli

# 2. Docker
docker --version
# If not installed: https://docs.docker.com/get-docker/

# 3. AWS Account
# Create at: https://aws.amazon.com/
```

### AWS Permissions
Your IAM user needs:
- Lightsail full access
- ECR (Elastic Container Registry) access
- S3 access for exports
- Bedrock access for Claude

### Cost Estimate
```
Lightsail Container Service Pricing:
├─ Nano (0.25 vCPU, 512 MB): $7/month - Too small
├─ Micro (0.5 vCPU, 1 GB): $10/month - Minimum viable
├─ Small (1 vCPU, 2 GB): $40/month - ⭐ Recommended
├─ Medium (2 vCPU, 4 GB): $80/month - High performance
└─ Large (4 vCPU, 8 GB): $160/month - Maximum

Additional Costs:
├─ Custom Domain: $12/year (Route 53)
├─ SSL Certificate: FREE (Lightsail provides)
├─ Data Transfer: Included (1-5 TB depending on plan)
├─ S3 Storage: $0.023/GB (minimal for exports)
└─ Bedrock API: Pay per token (same across all services)

Recommended Monthly Cost: $40-80
```

---

## Step 1: Prepare Docker Image

### 1.1 Optimize Dockerfile for Production

```bash
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2

# Create optimized Dockerfile
cat > Dockerfile.lightsail << 'EOF'
# Multi-stage build for smaller image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create directories
RUN mkdir -p uploads data && \
    chmod 777 uploads data

# Add Python packages to PATH
ENV PATH=/root/.local/bin:$PATH

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
EOF
```

### 1.2 Create .dockerignore

```bash
cat > .dockerignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Application
uploads/*
!uploads/.gitkeep
data/*
!data/.gitkeep
*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Git
.git/
.gitignore

# Documentation
*.md
docs/
archive/

# Environment
.env
.env.local

# AWS
.aws/

# Testing
.pytest_cache/
.coverage
htmlcov/
EOF
```

### 1.3 Build and Test Locally

```bash
# Build image
docker build -f Dockerfile.lightsail -t aiprism:latest .

# Test locally
docker run -d -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0 \
  -e BEDROCK_MAX_TOKENS=4096 \
  --name aiprism-test \
  aiprism:latest

# Wait 10 seconds for startup
sleep 10

# Test health endpoint
curl http://localhost:8000/health

# Expected output: {"status": "healthy", ...}

# Stop test container
docker stop aiprism-test && docker rm aiprism-test
```

---

## Step 2: Push to Container Registry

### Option A: Amazon ECR (Recommended)

#### 2.1 Create ECR Repository
```bash
# Create repository
aws ecr create-repository \
  --repository-name aiprism \
  --region us-east-1

# Output will include repository URI:
# account-id.dkr.ecr.us-east-1.amazonaws.com/aiprism
```

#### 2.2 Authenticate Docker to ECR
```bash
# Get login password and authenticate
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Expected output: Login Succeeded
```

#### 2.3 Tag and Push Image
```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Tag image
docker tag aiprism:latest \
  $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:latest

# Push to ECR
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:latest

# This will take 2-5 minutes depending on your internet speed
```

#### 2.4 Make Repository Accessible to Lightsail
```bash
# Get repository ARN
REPO_ARN=$(aws ecr describe-repositories \
  --repository-names aiprism \
  --query 'repositories[0].repositoryArn' \
  --output text)

# Set policy to allow Lightsail access
cat > ecr-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LightsailAccess",
      "Effect": "Allow",
      "Principal": {
        "Service": "lightsail.amazonaws.com"
      },
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:BatchCheckLayerAvailability"
      ]
    }
  ]
}
EOF

aws ecr set-repository-policy \
  --repository-name aiprism \
  --policy-text file://ecr-policy.json
```

### Option B: Docker Hub (Alternative)

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag aiprism:latest your-dockerhub-username/aiprism:latest

# Push
docker push your-dockerhub-username/aiprism:latest
```

---

## Step 3: Create Lightsail Container Service

### 3.1 Create Container Service via Console (Easiest)

1. **Open Lightsail Console:**
   ```
   https://lightsail.aws.amazon.com/ls/webapp/home/containers
   ```

2. **Click "Create container service"**

3. **Choose Settings:**
   - **Region:** us-east-1 (Virginia) - or closest to you
   - **Service name:** aiprism
   - **Power:** Small (1 GB RAM, 0.5 vCPU, 1 node) - $40/month ⭐

4. **Setup Deployment (Later)** - Skip for now

5. **Click "Create container service"**

### 3.2 Create Container Service via CLI (Advanced)

```bash
# Create container service
aws lightsail create-container-service \
  --service-name aiprism \
  --power small \
  --scale 1 \
  --region us-east-1

# Wait for service to be ready (2-3 minutes)
aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].state' \
  --output text

# Expected output: READY
```

### 3.3 Get Service Information

```bash
# Get service details
aws lightsail get-container-services --service-name aiprism

# Note the service URL (will be like):
# https://aiprism.xxxxx.us-east-1.cs.amazonlightsail.com
```

---

## Step 4: Deploy Application

### 4.1 Create Deployment Configuration

```bash
# Get your ECR image URI
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IMAGE_URI="$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:latest"

# Create deployment configuration file
cat > lightsail-deployment.json << EOF
{
  "containers": {
    "aiprism-app": {
      "image": "$IMAGE_URI",
      "command": [],
      "environment": {
        "FLASK_ENV": "production",
        "FLASK_APP": "app.py",
        "PORT": "8000",
        "AWS_REGION": "us-east-1",
        "AWS_DEFAULT_REGION": "us-east-1",
        "BEDROCK_MODEL_ID": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "BEDROCK_MAX_TOKENS": "4096",
        "BEDROCK_TEMPERATURE": "0.7",
        "REASONING_ENABLED": "false",
        "ENHANCED_MODE": "true",
        "MAX_CONTENT_LENGTH": "16777216",
        "SESSION_TIMEOUT": "3600"
      },
      "ports": {
        "8000": "HTTP"
      }
    }
  },
  "publicEndpoint": {
    "containerName": "aiprism-app",
    "containerPort": 8000,
    "healthCheck": {
      "healthyThreshold": 2,
      "unhealthyThreshold": 3,
      "timeoutSeconds": 5,
      "intervalSeconds": 30,
      "path": "/health",
      "successCodes": "200-299"
    }
  }
}
EOF
```

### 4.2 Deploy to Lightsail

```bash
# Deploy the container
aws lightsail create-container-service-deployment \
  --service-name aiprism \
  --cli-input-json file://lightsail-deployment.json

# Monitor deployment status
aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].currentDeployment.state' \
  --output text

# Wait until state is "ACTIVE" (2-5 minutes)
```

### 4.3 Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].url' \
  --output text)

echo "Service URL: https://$SERVICE_URL"

# Test health endpoint
curl https://$SERVICE_URL/health

# Expected output: {"status":"healthy", "timestamp":"..."}

# Open in browser
open "https://$SERVICE_URL"
```

---

## Step 5: Configure Custom Domain

### 5.1 Create SSL Certificate

```bash
# Lightsail automatically provides SSL certificate
# Just need to enable custom domain

# Enable custom domains
aws lightsail enable-custom-domain \
  --service-name aiprism

# This creates a certificate automatically
```

### 5.2 Add Custom Domain via Console

1. **Open Lightsail Console:**
   ```
   https://lightsail.aws.amazon.com/ls/webapp/home/containers
   ```

2. **Select your service:** aiprism

3. **Click "Custom domains" tab**

4. **Click "Create certificate"**
   - Enter domains: `aiprism.yourdomain.com`, `www.aiprism.yourdomain.com`
   - Click "Create"

5. **Validate Domain (DNS validation):**
   - Copy CNAME records provided
   - Add to your DNS provider (Route 53 or external)
   - Wait 5-30 minutes for validation

6. **Attach Certificate:**
   - Once validated, click "Attach to distribution"
   - Select certificate
   - Enable custom domain

### 5.3 Update DNS Records

```bash
# Get Lightsail service IP
SERVICE_IP=$(aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].url' \
  --output text | cut -d'/' -f3)

# If using Route 53
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "aiprism.yourdomain.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2P70J7EXAMPLE",
          "DNSName": "'"$SERVICE_URL"'",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'
```

### 5.4 Alternative: Use Lightsail Load Balancer

For better performance with multiple nodes:

```bash
# Create Lightsail load balancer
aws lightsail create-load-balancer \
  --load-balancer-name aiprism-lb \
  --instance-port 8000 \
  --health-check-path /health

# Attach certificate to load balancer
aws lightsail attach-load-balancer-tls-certificate \
  --load-balancer-name aiprism-lb \
  --certificate-name aiprism-cert

# Attach container service to load balancer
# (This must be done via console)
```

---

## Step 6: Setup Redis (Optional)

### Option A: Redis in Sidecar Container (Same Service)

```bash
# Update deployment to include Redis
cat > lightsail-deployment-redis.json << EOF
{
  "containers": {
    "aiprism-app": {
      "image": "$IMAGE_URI",
      "environment": {
        "FLASK_ENV": "production",
        "AWS_REGION": "us-east-1",
        "BEDROCK_MODEL_ID": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "RQ_ENABLED": "true"
      },
      "ports": {
        "8000": "HTTP"
      }
    },
    "redis": {
      "image": "redis:7-alpine",
      "ports": {
        "6379": "TCP"
      }
    }
  },
  "publicEndpoint": {
    "containerName": "aiprism-app",
    "containerPort": 8000,
    "healthCheck": {
      "path": "/health",
      "intervalSeconds": 30
    }
  }
}
EOF

# Deploy with Redis
aws lightsail create-container-service-deployment \
  --service-name aiprism \
  --cli-input-json file://lightsail-deployment-redis.json
```

### Option B: Separate Lightsail Database (Managed Redis)

**Note:** Lightsail doesn't offer managed Redis. Options:

1. **ElastiCache Redis** (AWS) - More expensive, full-featured
2. **External Redis** (Redis Cloud, Upstash) - Pay-as-you-go
3. **Redis in container** (Option A above) - Simple, included

**Recommendation for Lightsail:** Use Option A (Redis sidecar).

---

## Step 7: Monitoring & Logs

### 7.1 View Container Logs

```bash
# Get recent logs
aws lightsail get-container-log \
  --service-name aiprism \
  --container-name aiprism-app \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S)

# Tail logs in real-time (via console)
# Open: https://lightsail.aws.amazon.com/ls/webapp/home/containers
# Click service > Logs tab > View logs
```

### 7.2 Setup CloudWatch Logs (Optional)

```bash
# Enable CloudWatch logging
cat > .ebextensions/cloudwatch-logs.config << 'EOF'
# CloudWatch Logs Integration

files:
  "/etc/awslogs/awslogs.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      [general]
      state_file = /var/awslogs/state/agent-state

      [/var/log/docker.log]
      file = /var/log/docker.log
      log_group_name = /aws/lightsail/aiprism
      log_stream_name = {instance_id}/docker.log
      datetime_format = %Y-%m-%d %H:%M:%S

commands:
  01_install_cloudwatch_agent:
    command: |
      yum install -y awslogs
      systemctl start awslogsd
      systemctl enable awslogsd
EOF
```

### 7.3 Monitor Metrics (Console)

1. Open Lightsail Console
2. Select "aiprism" service
3. Click "Metrics" tab
4. View:
   - CPU Utilization
   - Memory Utilization
   - Network In/Out
   - HTTP responses (2xx, 4xx, 5xx)

### 7.4 Setup Alarms

```bash
# Create CloudWatch alarm for high CPU
aws cloudwatch put-metric-alarm \
  --alarm-name aiprism-high-cpu \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/Lightsail \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ServiceName,Value=aiprism

# Create SNS topic for notifications
aws sns create-topic --name aiprism-alerts

# Subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:aiprism-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

---

## Scaling & Optimization

### 8.1 Scale Up (More Nodes)

```bash
# Update to 3 nodes (maximum for Lightsail)
aws lightsail update-container-service \
  --service-name aiprism \
  --scale 3

# Cost: 3 × $40 = $120/month (Small power)
```

### 8.2 Upgrade Power

```bash
# Upgrade to Medium power (2 vCPU, 4 GB RAM)
aws lightsail update-container-service \
  --service-name aiprism \
  --power medium

# Cost: $80/month per node
```

### 8.3 Cost Optimization

```bash
# For development/testing: Use Micro power
aws lightsail create-container-service \
  --service-name aiprism-dev \
  --power micro \
  --scale 1

# Cost: $10/month (save $30)

# For production: Start with Small, scale to 2-3 nodes if needed
# Small (1 node): $40/month
# Small (2 nodes): $80/month - High availability
# Small (3 nodes): $120/month - Maximum scale
```

---

## Troubleshooting

### Issue 1: Deployment Fails

**Symptoms:**
```
Deployment state: FAILED
```

**Solutions:**
```bash
# 1. Check deployment logs
aws lightsail get-container-log \
  --service-name aiprism \
  --container-name aiprism-app

# 2. Verify image is accessible
aws ecr describe-images \
  --repository-name aiprism \
  --image-ids imageTag=latest

# 3. Check environment variables
aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].currentDeployment.containers'

# 4. Redeploy
aws lightsail create-container-service-deployment \
  --service-name aiprism \
  --cli-input-json file://lightsail-deployment.json
```

### Issue 2: Health Check Fails

**Symptoms:**
```
Container status: Unhealthy
```

**Solutions:**
```bash
# 1. Verify health endpoint locally
docker run -p 8000:8000 aiprism:latest
curl http://localhost:8000/health

# 2. Check health check configuration
aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].currentDeployment.publicEndpoint.healthCheck'

# 3. Update health check path
# Edit lightsail-deployment.json
# Change healthCheck.path to "/health"
# Redeploy

# 4. Increase timeout
# healthCheck.timeoutSeconds: 10
# healthCheck.intervalSeconds: 60
```

### Issue 3: Can't Access Application

**Symptoms:**
- 504 Gateway Timeout
- Connection refused

**Solutions:**
```bash
# 1. Check service state
aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].state'

# Expected: READY

# 2. Check container logs for errors
aws lightsail get-container-log \
  --service-name aiprism \
  --container-name aiprism-app

# 3. Verify port mapping
# Container must expose port 8000
# Check Dockerfile: EXPOSE 8000

# 4. Test with curl
SERVICE_URL=$(aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].url' \
  --output text)
curl -v https://$SERVICE_URL/health
```

### Issue 4: High Memory Usage

**Symptoms:**
- Container restarts frequently
- Out of memory errors in logs

**Solutions:**
```bash
# 1. Check memory metrics
# Open Lightsail Console > Metrics tab

# 2. Upgrade to larger power
aws lightsail update-container-service \
  --service-name aiprism \
  --power medium  # 4 GB RAM

# 3. Optimize Gunicorn workers
# Edit Dockerfile, reduce workers:
# CMD ["gunicorn", "--workers", "1", "--threads", "4", ...]

# 4. Rebuild and redeploy
docker build -f Dockerfile.lightsail -t aiprism:latest .
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:latest
aws lightsail create-container-service-deployment \
  --service-name aiprism \
  --cli-input-json file://lightsail-deployment.json
```

### Issue 5: Slow Claude API Calls

**Symptoms:**
- Request timeouts
- 504 Gateway Timeout

**Solutions:**
```bash
# 1. Increase Gunicorn timeout
# Edit Dockerfile:
# CMD ["gunicorn", "--timeout", "300", ...]  # 5 minutes

# 2. Verify Bedrock credentials
# Check environment variables
aws lightsail get-container-services \
  --service-name aiprism

# 3. Test Bedrock access locally
docker run --rm -it \
  -e AWS_REGION=us-east-1 \
  -e BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0 \
  aiprism:latest \
  python -c "import boto3; bedrock = boto3.client('bedrock-runtime', 'us-east-1'); print('OK')"

# 4. Check for throttling
# Review logs for "ThrottlingException"
```

---

## Ongoing Operations

### Daily Operations

#### Deploy New Version
```bash
# 1. Build new image
docker build -f Dockerfile.lightsail -t aiprism:latest .

# 2. Tag with version
docker tag aiprism:latest \
  $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:v1.0.1

# 3. Push to ECR
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:v1.0.1

# 4. Update deployment JSON with new version
# Edit lightsail-deployment.json: change image tag to :v1.0.1

# 5. Deploy
aws lightsail create-container-service-deployment \
  --service-name aiprism \
  --cli-input-json file://lightsail-deployment.json

# 6. Monitor deployment
aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].currentDeployment.state'
```

#### Check Application Status
```bash
# Service status
aws lightsail get-container-services --service-name aiprism

# Health check
curl https://$(aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].url' \
  --output text)/health

# View logs
aws lightsail get-container-log \
  --service-name aiprism \
  --container-name aiprism-app
```

### Weekly Operations

#### Review Metrics
```bash
# Open Lightsail Console
# Navigate to: Metrics tab
# Review:
# - CPU utilization (target: <70%)
# - Memory utilization (target: <80%)
# - HTTP errors (target: <1%)
# - Network traffic trends
```

#### Check for Updates
```bash
# Pull latest base images
docker pull python:3.11-slim
docker pull redis:7-alpine

# Rebuild and test
docker build -f Dockerfile.lightsail -t aiprism:latest .
docker run -p 8000:8000 aiprism:latest

# Deploy if successful
```

### Monthly Operations

#### Cost Review
```bash
# View Lightsail costs
aws lightsail get-cost-estimate \
  --service-name aiprism \
  --start-time $(date -u -d '1 month ago' +%Y-%m-%d) \
  --end-time $(date -u +%Y-%m-%d)

# Optimize if needed:
# - Downgrade power if CPU < 30%
# - Reduce nodes if traffic is low
# - Consider scheduled scaling
```

#### Backup Configuration
```bash
# Export deployment configuration
aws lightsail get-container-services \
  --service-name aiprism > aiprism-backup-$(date +%Y%m%d).json

# Backup to S3
aws s3 cp aiprism-backup-$(date +%Y%m%d).json \
  s3://aiprism-backups/deployments/

# Backup Docker image
docker save aiprism:latest | gzip > aiprism-$(date +%Y%m%d).tar.gz
```

---

## Migration Path: Lightsail to Elastic Beanstalk

When you outgrow Lightsail (>3 nodes needed, >10K req/day):

### Step 1: Prepare for Migration
```bash
# Document current configuration
aws lightsail get-container-services --service-name aiprism > config-backup.json

# Test Beanstalk deployment (dev environment)
eb init aiprism --platform docker --region us-east-1
eb create aiprism-staging --single
```

### Step 2: Parallel Run
```bash
# Run both services in parallel
# Lightsail: Production traffic
# Beanstalk: Test traffic (10%)

# Use Route 53 weighted routing to split traffic
```

### Step 3: Cutover
```bash
# Update DNS to point to Beanstalk
# Wait for DNS propagation (5-30 minutes)
# Monitor for issues

# After 24 hours of stability:
# Terminate Lightsail service
aws lightsail delete-container-service --service-name aiprism
```

---

## Best Practices

### Security
```bash
# 1. Rotate AWS credentials monthly
aws iam create-access-key --user-name YOUR_USER

# 2. Enable VPC for Lightsail (if using database)
# Done via console

# 3. Use Secrets Manager for sensitive data
aws secretsmanager create-secret \
  --name aiprism/bedrock-key \
  --secret-string '{"api_key":"..."}'

# 4. Enable AWS CloudTrail for audit logs
aws cloudtrail create-trail \
  --name aiprism-audit \
  --s3-bucket-name audit-logs
```

### Performance
```bash
# 1. Enable HTTP/2 (automatic with SSL)
# 2. Use CDN for static assets (Lightsail includes)
# 3. Optimize Docker image size
# 4. Monitor and right-size resources
```

### Reliability
```bash
# 1. Use multiple nodes (2-3) for high availability
aws lightsail update-container-service --service-name aiprism --scale 2

# 2. Implement health checks properly
# 3. Set up monitoring alarms
# 4. Test disaster recovery procedures
```

---

## Summary

You've successfully deployed AI-Prism to AWS Lightsail!

### What You've Accomplished
✅ Built optimized Docker image
✅ Pushed to Amazon ECR
✅ Deployed to Lightsail Container Service
✅ Configured custom domain with SSL
✅ Setup monitoring and logging
✅ Configured Redis (optional)
✅ Implemented health checks

### Monthly Cost
- **Single Node (Small):** $40/month
- **High Availability (2 nodes):** $80/month
- **Maximum Scale (3 nodes):** $120/month

### Key Commands
```bash
# Deploy new version
docker build -f Dockerfile.lightsail -t aiprism:latest .
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:latest
aws lightsail create-container-service-deployment \
  --service-name aiprism \
  --cli-input-json file://lightsail-deployment.json

# View logs
aws lightsail get-container-log \
  --service-name aiprism \
  --container-name aiprism-app

# Check status
aws lightsail get-container-services --service-name aiprism

# Scale up
aws lightsail update-container-service --service-name aiprism --scale 2
```

### When to Migrate to Beanstalk/Fargate
- Need more than 3 nodes
- Traffic exceeds 10K requests/day
- Require auto-scaling
- Need advanced monitoring
- Budget allows ($150+/month)

### Support Resources
- 📚 [Lightsail Documentation](https://docs.aws.amazon.com/lightsail/)
- 💬 [AWS Forums](https://forums.aws.amazon.com/forum.jspa?forumID=231)
- 🎫 [AWS Support](https://console.aws.amazon.com/support/)

**Congratulations!** Your AI-Prism application is now live on AWS Lightsail with predictable costs and simple management.

---

**Next Steps:**
1. Test all features thoroughly
2. Setup monitoring alarms
3. Configure domain and SSL
4. Document your deployment
5. Plan scaling strategy
