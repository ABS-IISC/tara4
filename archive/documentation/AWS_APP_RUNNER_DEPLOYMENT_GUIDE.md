# AWS App Runner Deployment Guide - AI-Prism Complete Setup

**Date**: November 19, 2025
**System**: AI-Prism Risk Assessment Platform v2.0 (Enhanced Mode)
**Target**: AWS App Runner + ECS Fargate (Celery Workers)

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Variables (Complete List)](#environment-variables-complete-list)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Cost Estimation](#cost-estimation)
8. [Scaling Strategy](#scaling-strategy)

---

## 🏗️ Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    Production Architecture                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────┐     │
│  │         Users (HTTPS)                               │     │
│  └──────────────────────┬──────────────────────────────┘     │
│                         │                                     │
│                         ▼                                     │
│  ┌─────────────────────────────────────────────────────┐     │
│  │     AWS App Runner (Flask Application)             │     │
│  │     • Auto-scaling: 1-10 instances                  │     │
│  │     • CPU: 1 vCPU, Memory: 2 GB                     │     │
│  │     • Health check: /health                         │     │
│  │     • Port: 5000                                    │     │
│  └─────────────────┬───────────────────────────────────┘     │
│                    │                                          │
│                    │ Connects to                              │
│                    ▼                                          │
│  ┌─────────────────────────────────────────────────────┐     │
│  │   AWS ElastiCache for Redis (Managed)              │     │
│  │   • Engine: Redis 7.x                               │     │
│  │   • Node: cache.t3.micro                            │     │
│  │   • Endpoint: xxx.cache.amazonaws.com:6379          │     │
│  └─────────────────┬───────────────────────────────────┘     │
│                    │                                          │
│                    │ Task Queue                               │
│                    ▼                                          │
│  ┌─────────────────────────────────────────────────────┐     │
│  │   AWS ECS Fargate (Celery Workers)                  │     │
│  │   • Cluster: aiprism-celery-cluster                 │     │
│  │   • Service: aiprism-celery-workers                 │     │
│  │   • Task count: 2-8 (auto-scaling)                  │     │
│  │   • CPU: 0.5 vCPU, Memory: 1 GB per task            │     │
│  └─────────────────┬───────────────────────────────────┘     │
│                    │                                          │
│                    │ Invokes                                  │
│                    ▼                                          │
│  ┌─────────────────────────────────────────────────────┐     │
│  │   AWS Bedrock (us-east-2)                           │     │
│  │   • 5 Claude models with fallback                   │     │
│  │   • Extended thinking enabled                       │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌─────────────────────────────────────────────────────┐     │
│  │   AWS S3 (us-east-1)                                │     │
│  │   • Document storage                                │     │
│  │   • Bucket: aiprism-documents                       │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌─────────────────────────────────────────────────────┐     │
│  │   AWS Secrets Manager                               │     │
│  │   • Environment variables                           │     │
│  │   • AWS credentials                                 │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌─────────────────────────────────────────────────────┐     │
│  │   AWS CloudWatch                                    │     │
│  │   • Application logs                                │     │
│  │   • Metrics & alarms                                │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

### 1. AWS Account Setup

```bash
# Install AWS CLI
brew install awscli  # macOS
# or
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region name: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

### 2. Required AWS Services

- ✅ AWS App Runner (Flask application)
- ✅ AWS ElastiCache for Redis (message broker)
- ✅ AWS ECS Fargate (Celery workers)
- ✅ AWS Bedrock (Claude API access)
- ✅ AWS S3 (document storage)
- ✅ AWS Secrets Manager (credentials)
- ✅ AWS CloudWatch (monitoring)
- ✅ AWS VPC (networking)

### 3. IAM Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "apprunner:*",
        "ecs:*",
        "ecr:*",
        "elasticache:*",
        "bedrock:*",
        "s3:*",
        "secretsmanager:*",
        "cloudwatch:*",
        "logs:*",
        "iam:PassRole",
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups"
      ],
      "Resource": "*"
    }
  ]
}
```

### 4. Local Development Tools

```bash
# Docker (for building images)
docker --version  # Should be 20.x or higher

# Python 3.9+
python3 --version

# Git
git --version
```

---

## 🔐 Environment Variables (Complete List)

### Critical Variables (Required)

#### AWS Configuration
```bash
# AWS Credentials (for boto3 clients)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1

# AWS Bedrock Configuration
BEDROCK_REGION=us-east-2
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7

# AWS S3 Configuration
S3_BUCKET_NAME=aiprism-documents-prod
S3_PREFIX=sessions/
AWS_REGION=us-east-1  # S3 region (can be different from Bedrock)
```

#### Celery/Redis Configuration
```bash
# Redis Connection (ElastiCache endpoint)
REDIS_URL=redis://aiprism-redis.cache.amazonaws.com:6379/0

# Celery Settings
USE_CELERY=true
CELERY_BROKER_URL=redis://aiprism-redis.cache.amazonaws.com:6379/0
CELERY_RESULT_BACKEND=redis://aiprism-redis.cache.amazonaws.com:6379/0
CELERY_CONCURRENCY=4
```

#### Rate Limiting Configuration
```bash
# Request Rate Limits (AsyncRequestManager)
MAX_REQUESTS_PER_MINUTE=30
MAX_CONCURRENT_REQUESTS=5
MAX_TOKENS_PER_MINUTE=120000

# Celery Task Rate Limits (per worker)
ANALYSIS_TASK_RATE_LIMIT=10/m
CHAT_TASK_RATE_LIMIT=15/m
HEALTH_TASK_RATE_LIMIT=1/m
```

### Optional Variables (Recommended)

#### Application Configuration
```bash
# Flask Settings
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_PORT=5000
SECRET_KEY=your-secret-key-here-change-me

# Application Behavior
ENVIRONMENT=production
LOG_LEVEL=INFO
ENABLE_CORS=true
```

#### Performance Tuning
```bash
# Timeout Settings
BEDROCK_READ_TIMEOUT=240
BEDROCK_CONNECT_TIMEOUT=30
TASK_SOFT_TIME_LIMIT=240
TASK_HARD_TIME_LIMIT=300

# Circuit Breaker Settings
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60
CIRCUIT_BREAKER_EXPECTED_EXCEPTION=ThrottlingException
```

#### Monitoring & Observability
```bash
# CloudWatch Settings
ENABLE_CLOUDWATCH_LOGS=true
CLOUDWATCH_LOG_GROUP=/aws/apprunner/aiprism
CLOUDWATCH_LOG_STREAM=flask-app

# Metrics
ENABLE_METRICS=true
METRICS_NAMESPACE=AIRprism/Production
```

#### Security Settings
```bash
# CORS Configuration
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# Session Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

#### Feature Flags
```bash
# Enhanced Mode Features
ENABLE_ENHANCED_MODE=true
ENABLE_EXTENDED_THINKING=true
ENABLE_TOON_OPTIMIZATION=true
ENABLE_MULTI_MODEL_FALLBACK=true

# Optional Features
ENABLE_HEALTH_MONITORING=true
ENABLE_AUTOMATIC_RETRIES=true
ENABLE_CIRCUIT_BREAKER=true
```

### Complete .env Template

Save this as `.env.production`:

```bash
# ============================================================================
# AI-Prism Production Environment Variables
# ============================================================================

# ----------------------------------------------------------------------------
# AWS Credentials & Configuration
# ----------------------------------------------------------------------------
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1

# ----------------------------------------------------------------------------
# AWS Bedrock (Claude API)
# ----------------------------------------------------------------------------
BEDROCK_REGION=us-east-2
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
BEDROCK_READ_TIMEOUT=240
BEDROCK_CONNECT_TIMEOUT=30

# ----------------------------------------------------------------------------
# AWS S3 (Document Storage)
# ----------------------------------------------------------------------------
S3_BUCKET_NAME=aiprism-documents-prod
S3_PREFIX=sessions/
AWS_REGION=us-east-1

# ----------------------------------------------------------------------------
# Redis/Celery Configuration
# ----------------------------------------------------------------------------
REDIS_URL=redis://aiprism-redis.abc123.cache.amazonaws.com:6379/0
USE_CELERY=true
CELERY_BROKER_URL=redis://aiprism-redis.abc123.cache.amazonaws.com:6379/0
CELERY_RESULT_BACKEND=redis://aiprism-redis.abc123.cache.amazonaws.com:6379/0
CELERY_CONCURRENCY=4

# ----------------------------------------------------------------------------
# Rate Limiting
# ----------------------------------------------------------------------------
MAX_REQUESTS_PER_MINUTE=30
MAX_CONCURRENT_REQUESTS=5
MAX_TOKENS_PER_MINUTE=120000
ANALYSIS_TASK_RATE_LIMIT=10/m
CHAT_TASK_RATE_LIMIT=15/m
HEALTH_TASK_RATE_LIMIT=1/m

# ----------------------------------------------------------------------------
# Flask Application
# ----------------------------------------------------------------------------
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_PORT=5000
SECRET_KEY=change-this-to-a-random-secret-key-min-32-chars
ENVIRONMENT=production
LOG_LEVEL=INFO

# ----------------------------------------------------------------------------
# Performance Tuning
# ----------------------------------------------------------------------------
TASK_SOFT_TIME_LIMIT=240
TASK_HARD_TIME_LIMIT=300
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60

# ----------------------------------------------------------------------------
# Security
# ----------------------------------------------------------------------------
ENABLE_CORS=true
CORS_ALLOWED_ORIGINS=https://yourdomain.com
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# ----------------------------------------------------------------------------
# Monitoring
# ----------------------------------------------------------------------------
ENABLE_CLOUDWATCH_LOGS=true
CLOUDWATCH_LOG_GROUP=/aws/apprunner/aiprism
ENABLE_METRICS=true
METRICS_NAMESPACE=AIRprism/Production

# ----------------------------------------------------------------------------
# Feature Flags
# ----------------------------------------------------------------------------
ENABLE_ENHANCED_MODE=true
ENABLE_EXTENDED_THINKING=true
ENABLE_TOON_OPTIMIZATION=true
ENABLE_MULTI_MODEL_FALLBACK=true
ENABLE_HEALTH_MONITORING=true
ENABLE_AUTOMATIC_RETRIES=true
ENABLE_CIRCUIT_BREAKER=true
```

---

## 🚀 Step-by-Step Deployment

### Phase 1: Create S3 Bucket

```bash
# Create S3 bucket for documents
aws s3 mb s3://aiprism-documents-prod --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket aiprism-documents-prod \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket aiprism-documents-prod \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Set CORS policy (if accessing from browser)
aws s3api put-bucket-cors \
  --bucket aiprism-documents-prod \
  --cors-configuration file://s3-cors.json

# s3-cors.json content:
# {
#   "CORSRules": [
#     {
#       "AllowedOrigins": ["https://yourdomain.com"],
#       "AllowedMethods": ["GET", "PUT", "POST"],
#       "AllowedHeaders": ["*"],
#       "MaxAgeSeconds": 3000
#     }
#   ]
# }

# Verify bucket created
aws s3 ls s3://aiprism-documents-prod/
```

### Phase 2: Create ElastiCache Redis

```bash
# Create subnet group (if not exists)
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name aiprism-redis-subnet \
  --cache-subnet-group-description "Subnet group for AI-Prism Redis" \
  --subnet-ids subnet-abc123 subnet-def456

# Create security group for Redis
aws ec2 create-security-group \
  --group-name aiprism-redis-sg \
  --description "Security group for AI-Prism Redis" \
  --vpc-id vpc-abc123

# Allow inbound Redis traffic (port 6379) from App Runner
aws ec2 authorize-security-group-ingress \
  --group-id sg-abc123 \
  --protocol tcp \
  --port 6379 \
  --source-group sg-apprunner-abc123

# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id aiprism-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --cache-subnet-group-name aiprism-redis-subnet \
  --security-group-ids sg-abc123 \
  --tags "Key=Name,Value=aiprism-redis" "Key=Environment,Value=production"

# Wait for cluster to be available (5-10 minutes)
aws elasticache describe-cache-clusters \
  --cache-cluster-id aiprism-redis \
  --show-cache-node-info

# Get Redis endpoint
aws elasticache describe-cache-clusters \
  --cache-cluster-id aiprism-redis \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
  --output text

# Output: aiprism-redis.abc123.cache.amazonaws.com
# Use this as REDIS_URL: redis://aiprism-redis.abc123.cache.amazonaws.com:6379/0
```

### Phase 3: Store Secrets in AWS Secrets Manager

```bash
# Create secret for environment variables
aws secretsmanager create-secret \
  --name aiprism/production/env \
  --description "AI-Prism production environment variables" \
  --secret-string file://env-secrets.json

# env-secrets.json content:
# {
#   "AWS_ACCESS_KEY_ID": "AKIA...",
#   "AWS_SECRET_ACCESS_KEY": "...",
#   "REDIS_URL": "redis://aiprism-redis.abc123.cache.amazonaws.com:6379/0",
#   "SECRET_KEY": "your-secret-key-min-32-chars",
#   "BEDROCK_REGION": "us-east-2"
# }

# Verify secret created
aws secretsmanager describe-secret --secret-id aiprism/production/env

# Retrieve secret (for testing)
aws secretsmanager get-secret-value --secret-id aiprism/production/env
```

### Phase 4: Build and Push Docker Images

#### 4.1: Create ECR Repositories

```bash
# Create repository for Flask app
aws ecr create-repository \
  --repository-name aiprism/flask-app \
  --region us-east-1

# Create repository for Celery worker
aws ecr create-repository \
  --repository-name aiprism/celery-worker \
  --region us-east-1

# Get ECR login credentials
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com
```

#### 4.2: Create Dockerfile for Flask App

Create `Dockerfile.flask`:

```dockerfile
# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)"

# Start Flask app
CMD ["python", "app.py"]
```

#### 4.3: Create Dockerfile for Celery Worker

Create `Dockerfile.celery`:

```dockerfile
# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Health check (check if worker is responsive)
HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
  CMD celery -A celery_config inspect ping -d celery@$HOSTNAME || exit 1

# Start Celery worker
CMD ["celery", "-A", "celery_config", "worker", "--loglevel=info", "--concurrency=4"]
```

#### 4.4: Create requirements.txt

```txt
# Core dependencies
Flask==2.3.3
celery[redis]==5.3.4
redis==5.0.1
boto3==1.28.85
botocore==1.31.85

# Additional dependencies
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0

# Optional: Performance monitoring
prometheus-client==0.18.0
```

#### 4.5: Build and Push Images

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1

# Build Flask app image
docker build -f Dockerfile.flask -t aiprism-flask:latest .

# Tag and push Flask app
docker tag aiprism-flask:latest \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/aiprism/flask-app:latest

docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/aiprism/flask-app:latest

# Build Celery worker image
docker build -f Dockerfile.celery -t aiprism-celery:latest .

# Tag and push Celery worker
docker tag aiprism-celery:latest \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/aiprism/celery-worker:latest

docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/aiprism/celery-worker:latest

# Verify images pushed
aws ecr describe-images --repository-name aiprism/flask-app
aws ecr describe-images --repository-name aiprism/celery-worker
```

### Phase 5: Deploy Flask App to App Runner

#### 5.1: Create IAM Role for App Runner

Create `apprunner-role-trust-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "tasks.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Create `apprunner-role-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "secretsmanager:GetSecretValue",
        "cloudwatch:PutMetricData",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

Create IAM role:

```bash
# Create role
aws iam create-role \
  --role-name aiprism-apprunner-role \
  --assume-role-policy-document file://apprunner-role-trust-policy.json

# Attach policy
aws iam put-role-policy \
  --role-name aiprism-apprunner-role \
  --policy-name aiprism-apprunner-policy \
  --policy-document file://apprunner-role-policy.json

# Get role ARN
aws iam get-role --role-name aiprism-apprunner-role --query 'Role.Arn' --output text
```

#### 5.2: Create App Runner Service

Create `apprunner-service-config.json`:

```json
{
  "ServiceName": "aiprism-flask-app",
  "SourceConfiguration": {
    "ImageRepository": {
      "ImageIdentifier": "123456789012.dkr.ecr.us-east-1.amazonaws.com/aiprism/flask-app:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "5000",
        "RuntimeEnvironmentVariables": {
          "FLASK_ENV": "production",
          "FLASK_PORT": "5000",
          "USE_CELERY": "true",
          "ENABLE_ENHANCED_MODE": "true",
          "LOG_LEVEL": "INFO"
        },
        "RuntimeEnvironmentSecrets": {
          "AWS_ACCESS_KEY_ID": "arn:aws:secretsmanager:us-east-1:123456789012:secret:aiprism/production/env:AWS_ACCESS_KEY_ID::",
          "AWS_SECRET_ACCESS_KEY": "arn:aws:secretsmanager:us-east-1:123456789012:secret:aiprism/production/env:AWS_SECRET_ACCESS_KEY::",
          "REDIS_URL": "arn:aws:secretsmanager:us-east-1:123456789012:secret:aiprism/production/env:REDIS_URL::",
          "SECRET_KEY": "arn:aws:secretsmanager:us-east-1:123456789012:secret:aiprism/production/env:SECRET_KEY::"
        }
      }
    },
    "AutoDeploymentsEnabled": true,
    "AuthenticationConfiguration": {
      "AccessRoleArn": "arn:aws:iam::123456789012:role/aiprism-apprunner-ecr-access"
    }
  },
  "InstanceConfiguration": {
    "Cpu": "1 vCPU",
    "Memory": "2 GB",
    "InstanceRoleArn": "arn:aws:iam::123456789012:role/aiprism-apprunner-role"
  },
  "HealthCheckConfiguration": {
    "Protocol": "HTTP",
    "Path": "/health",
    "Interval": 10,
    "Timeout": 5,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 5
  },
  "AutoScalingConfigurationArn": "arn:aws:apprunner:us-east-1:123456789012:autoscalingconfiguration/aiprism-autoscaling/1/abc123"
}
```

Create auto-scaling configuration first:

```bash
# Create auto-scaling configuration
aws apprunner create-auto-scaling-configuration \
  --auto-scaling-configuration-name aiprism-autoscaling \
  --max-concurrency 50 \
  --min-size 1 \
  --max-size 10
```

Create App Runner service:

```bash
# Create service (simpler command without JSON file)
aws apprunner create-service \
  --service-name aiprism-flask-app \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ACCOUNT_ID'.dkr.ecr.us-east-1.amazonaws.com/aiprism/flask-app:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "5000",
        "RuntimeEnvironmentVariables": {
          "FLASK_ENV": "production",
          "USE_CELERY": "true",
          "REDIS_URL": "redis://aiprism-redis.abc123.cache.amazonaws.com:6379/0",
          "BEDROCK_REGION": "us-east-2",
          "S3_BUCKET_NAME": "aiprism-documents-prod",
          "MAX_REQUESTS_PER_MINUTE": "30",
          "MAX_CONCURRENT_REQUESTS": "5",
          "MAX_TOKENS_PER_MINUTE": "120000",
          "ENABLE_ENHANCED_MODE": "true"
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB",
    "InstanceRoleArn": "arn:aws:iam::'$ACCOUNT_ID':role/aiprism-apprunner-role"
  }' \
  --health-check-configuration '{
    "Protocol": "HTTP",
    "Path": "/health",
    "Interval": 10,
    "Timeout": 5,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 5
  }'

# Wait for service to be running (5-10 minutes)
aws apprunner describe-service \
  --service-arn arn:aws:apprunner:us-east-1:$ACCOUNT_ID:service/aiprism-flask-app/abc123 \
  --query 'Service.Status' \
  --output text

# Get service URL
aws apprunner describe-service \
  --service-arn arn:aws:apprunner:us-east-1:$ACCOUNT_ID:service/aiprism-flask-app/abc123 \
  --query 'Service.ServiceUrl' \
  --output text

# Output: abc123.us-east-1.awsapprunner.com
```

### Phase 6: Deploy Celery Workers to ECS Fargate

#### 6.1: Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster \
  --cluster-name aiprism-celery-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=2 \
    capacityProvider=FARGATE_SPOT,weight=4

# Verify cluster created
aws ecs describe-clusters --clusters aiprism-celery-cluster
```

#### 6.2: Create IAM Role for ECS Task

Create `ecs-task-role-trust-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Create role:

```bash
# Create task execution role
aws iam create-role \
  --role-name aiprism-ecs-task-execution-role \
  --assume-role-policy-document file://ecs-task-role-trust-policy.json

# Attach AWS managed policy for ECR/CloudWatch
aws iam attach-role-policy \
  --role-name aiprism-ecs-task-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create task role (for Bedrock/S3 access)
aws iam create-role \
  --role-name aiprism-ecs-task-role \
  --assume-role-policy-document file://ecs-task-role-trust-policy.json

# Attach custom policy
aws iam put-role-policy \
  --role-name aiprism-ecs-task-role \
  --policy-name aiprism-celery-policy \
  --policy-document file://apprunner-role-policy.json
```

#### 6.3: Create ECS Task Definition

Create `celery-task-definition.json`:

```json
{
  "family": "aiprism-celery-worker",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/aiprism-ecs-task-execution-role",
  "taskRoleArn": "arn:aws:iam::123456789012:role/aiprism-ecs-task-role",
  "containerDefinitions": [
    {
      "name": "celery-worker",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/aiprism/celery-worker:latest",
      "essential": true,
      "environment": [
        {"name": "REDIS_URL", "value": "redis://aiprism-redis.abc123.cache.amazonaws.com:6379/0"},
        {"name": "BEDROCK_REGION", "value": "us-east-2"},
        {"name": "S3_BUCKET_NAME", "value": "aiprism-documents-prod"},
        {"name": "AWS_REGION", "value": "us-east-1"},
        {"name": "CELERY_CONCURRENCY", "value": "4"},
        {"name": "MAX_REQUESTS_PER_MINUTE", "value": "30"},
        {"name": "MAX_CONCURRENT_REQUESTS", "value": "5"},
        {"name": "MAX_TOKENS_PER_MINUTE", "value": "120000"},
        {"name": "ENABLE_ENHANCED_MODE", "value": "true"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {
          "name": "AWS_ACCESS_KEY_ID",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:aiprism/production/env:AWS_ACCESS_KEY_ID::"
        },
        {
          "name": "AWS_SECRET_ACCESS_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:aiprism/production/env:AWS_SECRET_ACCESS_KEY::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/aiprism-celery-worker",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "celery"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "celery -A celery_config inspect ping || exit 1"],
        "interval": 60,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

Register task definition:

```bash
# Create CloudWatch log group first
aws logs create-log-group --log-group-name /ecs/aiprism-celery-worker

# Register task definition
aws ecs register-task-definition --cli-input-json file://celery-task-definition.json

# Verify task definition registered
aws ecs describe-task-definition --task-definition aiprism-celery-worker
```

#### 6.4: Create ECS Service

```bash
# Get VPC and subnet IDs
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text)

# Create security group for Celery workers
SG_ID=$(aws ec2 create-security-group \
  --group-name aiprism-celery-workers-sg \
  --description "Security group for AI-Prism Celery workers" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# Allow outbound traffic (for Redis, Bedrock, S3)
aws ec2 authorize-security-group-egress \
  --group-id $SG_ID \
  --protocol all \
  --cidr 0.0.0.0/0

# Create ECS service
aws ecs create-service \
  --cluster aiprism-celery-cluster \
  --service-name aiprism-celery-workers \
  --task-definition aiprism-celery-worker \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[$SUBNET_IDS],
    securityGroups=[$SG_ID],
    assignPublicIp=ENABLED
  }" \
  --scheduling-strategy REPLICA

# Wait for service to stabilize (5-10 minutes)
aws ecs wait services-stable \
  --cluster aiprism-celery-cluster \
  --services aiprism-celery-workers

# Verify service running
aws ecs describe-services \
  --cluster aiprism-celery-cluster \
  --services aiprism-celery-workers \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'
```

#### 6.5: Set Up Auto-Scaling for Celery Workers

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/aiprism-celery-cluster/aiprism-celery-workers \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 8

# Create scaling policy (CPU-based)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/aiprism-celery-cluster/aiprism-celery-workers \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name aiprism-celery-cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'

# Create scaling policy (Memory-based)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/aiprism-celery-cluster/aiprism-celery-workers \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name aiprism-celery-memory-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 80.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageMemoryUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

### Phase 7: Set Up CloudWatch Monitoring

```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name AIRprism-Production \
  --dashboard-body file://cloudwatch-dashboard.json

# cloudwatch-dashboard.json content (see below)

# Create alarms
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name aiprism-high-error-rate \
  --alarm-description "Alert when error rate exceeds 5%" \
  --metric-name ErrorRate \
  --namespace AIRprism/Production \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 5.0 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:aiprism-alerts

# High latency alarm
aws cloudwatch put-metric-alarm \
  --alarm-name aiprism-high-latency \
  --alarm-description "Alert when P95 latency exceeds 10 seconds" \
  --metric-name ResponseTime \
  --namespace AIRprism/Production \
  --statistic p95 \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 10000 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:aiprism-alerts

# Celery queue length alarm
aws cloudwatch put-metric-alarm \
  --alarm-name aiprism-high-queue-length \
  --alarm-description "Alert when queue length exceeds 50" \
  --metric-name QueueLength \
  --namespace AIRprism/Production \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:aiprism-alerts
```

---

## ✅ Post-Deployment Verification

### Step 1: Verify All Services Running

```bash
# Check App Runner service
aws apprunner describe-service \
  --service-arn arn:aws:apprunner:us-east-1:$ACCOUNT_ID:service/aiprism-flask-app/abc123 \
  --query 'Service.{Status:Status,URL:ServiceUrl}'

# Check ECS service
aws ecs describe-services \
  --cluster aiprism-celery-cluster \
  --services aiprism-celery-workers \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'

# Check Redis cluster
aws elasticache describe-cache-clusters \
  --cache-cluster-id aiprism-redis \
  --query 'CacheClusters[0].{Status:CacheClusterStatus,Endpoint:CacheNodes[0].Endpoint.Address}'
```

### Step 2: Test Health Endpoints

```bash
# Get App Runner URL
APP_URL=$(aws apprunner describe-service \
  --service-arn arn:aws:apprunner:us-east-1:$ACCOUNT_ID:service/aiprism-flask-app/abc123 \
  --query 'Service.ServiceUrl' \
  --output text)

# Test Flask health
curl https://$APP_URL/health

# Expected output:
# {
#   "status": "healthy",
#   "celery": "connected",
#   "redis": "connected",
#   "enhanced_mode": true,
#   "models_available": 5,
#   "timestamp": "2025-11-19T10:30:00Z"
# }

# Test Celery task submission
curl -X POST https://$APP_URL/analyze_section \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "section_name": "Test Section",
    "content": "This is a test document."
  }'

# Expected output:
# {
#   "success": true,
#   "task_id": "abc-123-def-456",
#   "status": "processing",
#   "async": true,
#   "enhanced": true,
#   "features": {
#     "multi_model_fallback": true,
#     "extended_thinking": true,
#     "throttle_protection": true,
#     "token_optimization": true
#   }
# }

# Poll task status
curl https://$APP_URL/task_status/abc-123-def-456

# Expected output (when complete):
# {
#   "status": "completed",
#   "result": {
#     "feedback": [...],
#     "confidence": 0.95,
#     "model_used": "Claude Sonnet 4.5 (Extended Thinking)",
#     "thinking": "...",
#     "enhanced": true
#   }
# }
```

### Step 3: Verify Enhanced Mode

```bash
# Check logs for enhanced mode activation
aws logs tail /aws/apprunner/aiprism --follow

# Look for:
# ✅ ✨ ENHANCED MODE ACTIVATED ✨
#    Features enabled:
#    • Multi-model fallback (5 models)
#    • Extended thinking (Sonnet 4.5)
#    • 5-layer throttling protection
#    • Token optimization (TOON)
#    • us-east-2 region for Bedrock
#    • Loaded 5 Claude models:
#      1. Claude Sonnet 4.5 (Extended Thinking) [Extended Thinking]
#      2. Claude Sonnet 4.0
#      3. Claude Sonnet 3.7
#      4. Claude Sonnet 3.5
#      5. Claude Sonnet 3.5 v2

# Check Celery worker logs
aws logs tail /ecs/aiprism-celery-worker --follow

# Look for:
# ✅ Loaded 5 Claude models:
#    1. Claude Sonnet 4.5 (Extended Thinking) [Extended Thinking]
#    2. Claude Sonnet 4.0
#    3. Claude Sonnet 3.7
#    4. Claude Sonnet 3.5
#    5. Claude Sonnet 3.5 v2
```

### Step 4: Load Testing

```bash
# Install load testing tool
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class AIRprismUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def analyze_section(self):
        self.client.post("/analyze_section", json={
            "session_id": "load-test",
            "section_name": "Test",
            "content": "This is a load test document."
        })

    @task(2)
    def check_health(self):
        self.client.get("/health")
EOF

# Run load test (50 users, ramp up over 10 seconds)
locust -f locustfile.py --host https://$APP_URL --users 50 --spawn-rate 5 --run-time 5m --headless

# Expected results:
# - 99%+ success rate
# - P95 latency < 6 seconds
# - Throughput: 20-30 req/second
```

---

## 📊 Monitoring & Troubleshooting

### Key Metrics to Monitor

| Metric | Location | Healthy Range | Alert Threshold |
|--------|----------|---------------|-----------------|
| **App Runner CPU** | CloudWatch | 30-60% | >80% |
| **App Runner Memory** | CloudWatch | 40-70% | >85% |
| **ECS CPU** | CloudWatch | 40-70% | >80% |
| **ECS Memory** | CloudWatch | 50-75% | >85% |
| **Redis CPU** | CloudWatch | 20-50% | >70% |
| **Redis Memory** | CloudWatch | 30-60% | >75% |
| **Request Success Rate** | Custom | >99% | <95% |
| **Task Queue Length** | Redis | <10 | >50 |
| **P95 Latency** | CloudWatch | <6s | >10s |
| **Error Rate** | CloudWatch | <1% | >5% |
| **Bedrock Throttles** | CloudWatch | <5/hour | >20/hour |

### Common Issues & Solutions

#### Issue 1: "Enhanced mode not available"

**Symptom**:
```
ℹ️ Enhanced mode not available: No module named 'celery_tasks_enhanced'
```

**Solution**:
```bash
# Verify files are in Docker image
docker run --rm $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism/flask-app:latest ls -la

# If missing, rebuild image ensuring all files are copied
docker build -f Dockerfile.flask -t aiprism-flask:latest .
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism/flask-app:latest

# Force App Runner to redeploy
aws apprunner start-deployment \
  --service-arn arn:aws:apprunner:us-east-1:$ACCOUNT_ID:service/aiprism-flask-app/abc123
```

#### Issue 2: "Can't connect to Redis"

**Symptom**:
```
ERROR: Can't connect to Redis at aiprism-redis.abc123.cache.amazonaws.com:6379
```

**Solution**:
```bash
# Check Redis cluster status
aws elasticache describe-cache-clusters \
  --cache-cluster-id aiprism-redis \
  --query 'CacheClusters[0].CacheClusterStatus'

# Check security group rules
aws ec2 describe-security-groups \
  --group-ids sg-redis-abc123 \
  --query 'SecurityGroups[0].IpPermissions'

# Ensure App Runner and ECS tasks are in same VPC/security groups
# Allow inbound 6379 from App Runner and ECS security groups
```

#### Issue 3: "AWS Bedrock Access Denied"

**Symptom**:
```
ERROR: An error occurred (AccessDeniedException) when calling the InvokeModel operation
```

**Solution**:
```bash
# Check IAM role has Bedrock permissions
aws iam get-role-policy \
  --role-name aiprism-apprunner-role \
  --policy-name aiprism-apprunner-policy

# If missing, add Bedrock permissions
aws iam put-role-policy \
  --role-name aiprism-apprunner-role \
  --policy-name aiprism-bedrock-access \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }]
  }'

# Check if Bedrock is enabled in us-east-2 region
aws bedrock list-foundation-models --region us-east-2
```

#### Issue 4: "High task queue length"

**Symptom**:
```
WARNING: Celery queue length: 85 (threshold: 50)
```

**Solution**:
```bash
# Scale up Celery workers manually
aws ecs update-service \
  --cluster aiprism-celery-cluster \
  --service aiprism-celery-workers \
  --desired-count 6

# Or adjust auto-scaling settings
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/aiprism-celery-cluster/aiprism-celery-workers \
  --scalable-dimension ecs:service:DesiredCount \
  --max-capacity 12  # Increase from 8
```

### Useful Commands

```bash
# View App Runner logs (real-time)
aws logs tail /aws/apprunner/aiprism --follow --filter-pattern "ERROR"

# View Celery worker logs (real-time)
aws logs tail /ecs/aiprism-celery-worker --follow --filter-pattern "ERROR"

# Check current resource usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/AppRunner \
  --metric-name CpuUtilized \
  --dimensions Name=ServiceName,Value=aiprism-flask-app \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# Check Redis memory usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name DatabaseMemoryUsagePercentage \
  --dimensions Name=CacheClusterId,Value=aiprism-redis \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# Check Celery task statistics
aws ecs describe-services \
  --cluster aiprism-celery-cluster \
  --services aiprism-celery-workers \
  --query 'services[0].deployments[0].{Status:status,Running:runningCount,Pending:pendingCount}'

# Force redeploy (for updates)
aws apprunner start-deployment \
  --service-arn arn:aws:apprunner:us-east-1:$ACCOUNT_ID:service/aiprism-flask-app/abc123

aws ecs update-service \
  --cluster aiprism-celery-cluster \
  --service aiprism-celery-workers \
  --force-new-deployment
```

---

## 💰 Cost Estimation

### Monthly Cost Breakdown (Baseline: 1000 requests/day)

#### Compute Costs

| Service | Configuration | Cost |
|---------|---------------|------|
| **App Runner** | 1 vCPU, 2 GB, 730 hours | $51.10/month |
| **ECS Fargate (2 tasks)** | 0.5 vCPU, 1 GB, 730 hours × 2 | $59.86/month |
| **ElastiCache Redis** | cache.t3.micro | $15.33/month |
| **Sub-total (Compute)** | | **$126.29/month** |

#### API & Storage Costs

| Service | Usage | Cost |
|---------|-------|------|
| **AWS Bedrock (Sonnet 4.5)** | 1000 req/day × 4000 tokens avg | ~$360/month |
| **AWS Bedrock (Fallback models)** | ~50 req/day × 4000 tokens | ~$6/month |
| **S3 Storage** | 100 GB documents | $2.30/month |
| **S3 Requests** | 1000 uploads/day | $0.50/month |
| **Data Transfer** | 50 GB out | $4.50/month |
| **Sub-total (API/Storage)** | | **$373.30/month** |

#### Monitoring & Security

| Service | Usage | Cost |
|---------|-------|------|
| **CloudWatch Logs** | 10 GB ingestion, 10 GB storage | $5.50/month |
| **CloudWatch Metrics** | Custom metrics | $3.00/month |
| **Secrets Manager** | 1 secret | $0.40/month |
| **Sub-total (Monitoring)** | | **$8.90/month** |

#### Total Monthly Cost

| Scenario | Requests/Day | Total Cost |
|----------|--------------|------------|
| **Development** | 100 | $180/month |
| **Production (Small)** | 1,000 | $508/month |
| **Production (Medium)** | 5,000 | $1,850/month |
| **Production (Large)** | 10,000 | $3,450/month |

### Cost Optimization Tips

1. **Use FARGATE_SPOT** for Celery workers (70% savings)
2. **Enable S3 Intelligent-Tiering** (30% savings on storage)
3. **Use Reserved Capacity** for ElastiCache (40% savings)
4. **Implement request caching** (reduce Bedrock calls by 20%)
5. **Monitor and right-size** instances (10-20% savings)

**Estimated savings with optimizations**: 30-40% ($150-200/month at 1000 req/day)

---

## 📈 Scaling Strategy

### Scaling Dimensions

#### 1. Horizontal Scaling (Add more instances)

**App Runner Auto-Scaling**:
```bash
# Configure aggressive scaling
aws apprunner update-service \
  --service-arn arn:aws:apprunner:us-east-1:$ACCOUNT_ID:service/aiprism-flask-app/abc123 \
  --auto-scaling-configuration-arn arn:aws:apprunner:us-east-1:$ACCOUNT_ID:autoscalingconfiguration/aiprism-autoscaling-aggressive/1/abc123

# Aggressive config:
# - max-concurrency: 30 (down from 50)
# - min-size: 2 (up from 1)
# - max-size: 20 (up from 10)
```

**ECS Auto-Scaling**:
```bash
# Update scalable target for more workers
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/aiprism-celery-cluster/aiprism-celery-workers \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 4 \
  --max-capacity 16  # Doubled from 8
```

#### 2. Vertical Scaling (Bigger instances)

**App Runner**:
```bash
# Upgrade to larger instance
aws apprunner update-service \
  --service-arn arn:aws:apprunner:us-east-1:$ACCOUNT_ID:service/aiprism-flask-app/abc123 \
  --instance-configuration '{
    "Cpu": "2 vCPU",
    "Memory": "4 GB"
  }'
```

**ECS Fargate**:
```bash
# Update task definition with more resources
aws ecs register-task-definition \
  --family aiprism-celery-worker \
  --cpu "1024" \
  --memory "2048" \
  # ... rest of task definition
```

**ElastiCache Redis**:
```bash
# Upgrade Redis instance
aws elasticache modify-cache-cluster \
  --cache-cluster-id aiprism-redis \
  --cache-node-type cache.t3.small \
  --apply-immediately
```

#### 3. Multi-Region Deployment (Global scale)

Deploy to multiple regions for:
- Lower latency for global users
- 99.99% availability
- Geographic redundancy

```bash
# Deploy to us-west-2
aws apprunner create-service \
  --service-name aiprism-flask-app-west \
  --region us-west-2 \
  # ... same config as us-east-1

# Use Route 53 for geographic routing
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://route53-geo-routing.json
```

### Scaling Triggers & Thresholds

| Metric | Scale Out | Scale In | Cooldown |
|--------|-----------|----------|----------|
| CPU Usage | >70% for 3 min | <30% for 10 min | 5 min |
| Memory Usage | >80% for 3 min | <40% for 10 min | 5 min |
| Request Rate | >80% of limit | <40% of limit | 3 min |
| Queue Length | >30 tasks | <5 tasks | 5 min |
| P95 Latency | >8 seconds | <3 seconds | 10 min |

---

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ App Runner service status: `RUNNING`
- ✅ ECS service desired count = running count
- ✅ Redis status: `available`
- ✅ Health endpoint returns 200 OK
- ✅ Enhanced mode activated (check logs)
- ✅ Test analysis completes successfully
- ✅ All 5 models loadedsuccessfully
- ✅ CloudWatch logs show no errors
- ✅ Load test achieves 99%+ success rate
- ✅ P95 latency < 6 seconds

---

## 📚 Additional Resources

- **AWS App Runner Documentation**: https://docs.aws.amazon.com/apprunner/
- **AWS ECS Fargate Documentation**: https://docs.aws.amazon.com/ecs/
- **AWS Bedrock Documentation**: https://docs.aws.amazon.com/bedrock/
- **Celery Documentation**: https://docs.celeryproject.org/
- **Flask Deployment Best Practices**: https://flask.palletsprojects.com/en/2.3.x/deploying/

---

**Deployment Guide Version**: 1.0
**Last Updated**: November 19, 2025
**Status**: Production Ready ✅
**Support**: See [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md) for troubleshooting
