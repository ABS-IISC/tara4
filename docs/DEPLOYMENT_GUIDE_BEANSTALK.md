# Complete AWS Elastic Beanstalk Deployment Guide
## AI-Prism Flask Application with Claude Multi-Model Fallback

**Version:** 1.0
**Date:** November 25, 2025
**Estimated Time:** 45-60 minutes
**Difficulty:** Intermediate

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Step 1: Prepare Your Application](#step-1-prepare-your-application)
4. [Step 2: AWS Account Setup](#step-2-aws-account-setup)
5. [Step 3: Install EB CLI](#step-3-install-eb-cli)
6. [Step 4: Configure Application](#step-4-configure-application)
7. [Step 5: Initialize Elastic Beanstalk](#step-5-initialize-elastic-beanstalk)
8. [Step 6: Create Environment](#step-6-create-environment)
9. [Step 7: Configure Domain & SSL](#step-7-configure-domain--ssl)
10. [Step 8: Setup Redis & Database](#step-8-setup-redis--database)
11. [Step 9: Configure Auto-Scaling](#step-9-configure-auto-scaling)
12. [Step 10: Monitoring & Logging](#step-10-monitoring--logging)
13. [Ongoing Operations](#ongoing-operations)
14. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
- ✅ AWS Account with billing enabled
- ✅ AWS CLI installed and configured
- ✅ Docker installed locally
- ✅ Python 3.11+ installed
- ✅ Git for version control
- ✅ Text editor (VS Code recommended)

### AWS Permissions Required
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "elasticbeanstalk:*",
        "ec2:*",
        "ecs:*",
        "ecr:*",
        "elasticloadbalancing:*",
        "autoscaling:*",
        "cloudwatch:*",
        "s3:*",
        "sns:*",
        "cloudformation:*",
        "rds:*",
        "elasticache:*",
        "iam:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Estimated Costs
```
Monthly Costs (Production Environment):
├─ EC2 Instances (2 × t3.medium): $60.74
├─ Application Load Balancer: $26-36
├─ EBS Storage (40 GB): $3.20
├─ Data Transfer: $10-30
├─ CloudWatch Logs: $5-10
├─ ElastiCache Redis: $12
├─ NAT Gateway: $32-60
└─ Total: $149-208/month

First-time setup: Free tier may apply
Development: $40-80/month (single instance)
```

---

## Pre-Deployment Checklist

### ✅ Application Readiness
- [ ] Application runs locally without errors
- [ ] All dependencies in requirements.txt
- [ ] Environment variables documented
- [ ] Dockerfile builds successfully
- [ ] Health check endpoint (`/health`) works
- [ ] AWS Bedrock credentials configured

### ✅ AWS Setup
- [ ] AWS account created
- [ ] Billing alerts configured
- [ ] IAM user with necessary permissions
- [ ] AWS CLI configured (`aws configure`)
- [ ] Default region selected (e.g., us-east-1)

### ✅ Domain & SSL (Optional but Recommended)
- [ ] Domain name purchased
- [ ] DNS access (Route 53 or external)
- [ ] SSL certificate (ACM or external)

---

## Step 1: Prepare Your Application

### 1.1 Create Beanstalk-Specific Files

Navigate to your project directory:
```bash
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2
```

### 1.2 Create `.ebignore` File
```bash
cat > .ebignore << 'EOF'
# Elastic Beanstalk ignore file
.git/
.gitignore
*.md
docs/
archive/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.env
.venv/
venv/
ENV/
.DS_Store
*.log
uploads/*
!uploads/.gitkeep
data/*
!data/.gitkeep
.pytest_cache/
.coverage
htmlcov/
.idea/
.vscode/
*.swp
*.swo
*~
EOF
```

### 1.3 Create Production Requirements File
```bash
cat > requirements-production.txt << 'EOF'
# Production-optimized requirements for Elastic Beanstalk
Flask==2.3.3
python-docx==0.8.11
boto3==1.28.85
lxml==4.9.3
Werkzeug==2.3.7
Jinja2==3.1.2
MarkupSafe==2.1.3
click==8.1.7
itsdangerous==2.1.2
blinker==1.6.3
urllib3==1.26.18
botocore==1.31.85
jmespath==1.0.1
python-dateutil==2.8.2
s3transfer==0.7.0
six==1.16.0

# Production WSGI server
gunicorn==21.2.0

# Redis for session management
redis==5.0.1

# RQ for async tasks (Redis Queue - simpler than Celery)
rq==1.15.1

# Health monitoring
psutil==5.9.6

# Production logging
python-json-logger==2.0.7
EOF
```

### 1.4 Create Gunicorn Configuration
```bash
mkdir -p .platform/hooks/postdeploy
cat > gunicorn.conf.py << 'EOF'
"""
Gunicorn configuration for AI-Prism on Elastic Beanstalk
Optimized for AWS Bedrock Claude API calls
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # 2-4 workers on t3.medium
worker_class = "sync"  # Use 'sync' for Flask (not async)
worker_connections = 1000
max_requests = 1000  # Restart workers after 1000 requests (prevent memory leaks)
max_requests_jitter = 50
timeout = 300  # 5 minutes (for long Claude API calls)
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "aiprism-flask"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (handled by ALB)
# No SSL configuration needed - ALB terminates SSL

def post_fork(server, worker):
    """Called after worker is forked"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Called before worker is forked"""
    pass

def pre_exec(server):
    """Called before exec"""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Called when server is ready"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called when worker receives SIGINT or SIGQUIT"""
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when worker receives SIGABRT"""
    worker.log.info("Worker received SIGABRT signal")
EOF
```

---

## Step 2: AWS Account Setup

### 2.1 Configure AWS CLI

```bash
# Configure AWS credentials
aws configure

# Enter when prompted:
AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
Default region name: us-east-1
Default output format: json
```

### 2.2 Create IAM Roles for Beanstalk

Create IAM roles (if not exist):

```bash
# Create service role for Elastic Beanstalk
aws iam create-role \
  --role-name aws-elasticbeanstalk-service-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "elasticbeanstalk.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach managed policies
aws iam attach-role-policy \
  --role-name aws-elasticbeanstalk-service-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth

aws iam attach-role-policy \
  --role-name aws-elasticbeanstalk-service-role \
  --policy-arn arn:aws:iam::aws:policy/AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy
```

### 2.3 Create EC2 Instance Profile

```bash
# Create role for EC2 instances
aws iam create-role \
  --role-name aws-elasticbeanstalk-ec2-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policies for Bedrock, S3, CloudWatch
aws iam attach-role-policy \
  --role-name aws-elasticbeanstalk-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier

aws iam attach-role-policy \
  --role-name aws-elasticbeanstalk-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker

aws iam attach-role-policy \
  --role-name aws-elasticbeanstalk-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier

# Custom policy for Bedrock access
cat > bedrock-policy.json << 'EOF'
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
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-*",
        "arn:aws:bedrock:*::foundation-model/us.anthropic.claude-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::aiprism-exports/*",
        "arn:aws:s3:::aiprism-exports"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name aws-elasticbeanstalk-ec2-role \
  --policy-name BedrockAndS3Access \
  --policy-document file://bedrock-policy.json

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name aws-elasticbeanstalk-ec2-role

aws iam add-role-to-instance-profile \
  --instance-profile-name aws-elasticbeanstalk-ec2-role \
  --role-name aws-elasticbeanstalk-ec2-role
```

---

## Step 3: Install EB CLI

### 3.1 Install EB CLI via pip

```bash
# Install EB CLI
pip install awsebcli --upgrade

# Verify installation
eb --version
# Expected output: EB CLI 3.20.x (Python 3.x.x)
```

### 3.2 Alternative: Install via Homebrew (macOS)

```bash
brew install awsebcli
```

---

## Step 4: Configure Application

### 4.1 Create Elastic Beanstalk Extensions Directory

```bash
mkdir -p .ebextensions
```

### 4.2 Create Environment Configuration

```bash
cat > .ebextensions/01_environment.config << 'EOF'
# Elastic Beanstalk Environment Configuration
# AI-Prism Flask Application

option_settings:
  # ============================================
  # INSTANCE CONFIGURATION
  # ============================================
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.medium  # 2 vCPU, 4 GB RAM
    IamInstanceProfile: aws-elasticbeanstalk-ec2-role
    EC2KeyName: YOUR_KEY_PAIR  # Replace with your key pair name
    RootVolumeType: gp3
    RootVolumeSize: 20
    RootVolumeIOPS: 3000

  # ============================================
  # AUTO SCALING
  # ============================================
  aws:autoscaling:asg:
    MinSize: 2  # Minimum 2 instances for HA
    MaxSize: 10  # Scale up to 10 instances
    Cooldown: 360  # 6 minutes cooldown

  aws:autoscaling:trigger:
    MeasureName: CPUUtilization
    Statistic: Average
    Unit: Percent
    UpperThreshold: 75  # Scale up at 75% CPU
    UpperBreachScaleIncrement: 1
    LowerThreshold: 25  # Scale down at 25% CPU
    LowerBreachScaleIncrement: -1
    Period: 5
    BreachDuration: 5
    EvaluationPeriods: 1

  # ============================================
  # ENVIRONMENT TYPE
  # ============================================
  aws:elasticbeanstalk:environment:
    EnvironmentType: LoadBalanced
    LoadBalancerType: application
    ServiceRole: aws-elasticbeanstalk-service-role

  # ============================================
  # LOAD BALANCER
  # ============================================
  aws:elbv2:loadbalancer:
    IdleTimeout: 300  # 5 minutes for long Claude API calls
    ManagedSecurityGroup: sg-YOUR_SG  # Will be auto-created
    SecurityGroups: sg-YOUR_SG

  aws:elbv2:listener:default:
    ListenerEnabled: true
    Protocol: HTTP

  # ============================================
  # HEALTH REPORTING
  # ============================================
  aws:elasticbeanstalk:healthreporting:system:
    SystemType: enhanced
    EnhancedHealthAuthEnabled: true
    ConfigDocument:
      Version: 1
      CloudWatchMetrics:
        Instance:
          - CPUUtilization
          - InstanceHealth
          - ApplicationRequests5xx
          - ApplicationRequests4xx
          - ApplicationRequestsTotal
        Environment:
          - EnvironmentHealth
          - InstancesSevere
          - InstancesDegraded
          - InstancesWarning
          - InstancesInfo
          - InstancesOk
          - InstancesPending

  # ============================================
  # APPLICATION HEALTH CHECK
  # ============================================
  aws:elasticbeanstalk:application:
    Application Healthcheck URL: /health

  aws:elasticbeanstalk:environment:process:default:
    HealthCheckPath: /health
    HealthCheckInterval: 30
    HealthCheckTimeout: 5
    UnhealthyThresholdCount: 3
    HealthyThresholdCount: 2
    Port: 80
    Protocol: HTTP
    DeregistrationDelay: 20
    StickinessEnabled: true
    StickinessLBCookieDuration: 86400  # 24 hours

  # ============================================
  # DEPLOYMENT POLICY
  # ============================================
  aws:elasticbeanstalk:command:
    DeploymentPolicy: RollingWithAdditionalBatch
    BatchSizeType: Fixed
    BatchSize: 1  # Deploy to 1 instance at a time
    Timeout: 600  # 10 minutes timeout
    IgnoreHealthCheck: false

  # ============================================
  # ROLLING UPDATES
  # ============================================
  aws:autoscaling:updatepolicy:rollingupdate:
    RollingUpdateEnabled: true
    RollingUpdateType: Health
    MinInstancesInService: 1
    MaxBatchSize: 1
    PauseTime: PT5M  # 5 minutes pause between batches

  # ============================================
  # CLOUDWATCH LOGS
  # ============================================
  aws:elasticbeanstalk:cloudwatch:logs:
    StreamLogs: true
    DeleteOnTerminate: false
    RetentionInDays: 7

  aws:elasticbeanstalk:cloudwatch:logs:health:
    HealthStreamingEnabled: true
    DeleteOnTerminate: false
    RetentionInDays: 7

  # ============================================
  # ENVIRONMENT VARIABLES
  # ============================================
  aws:elasticbeanstalk:application:environment:
    # Flask Configuration
    FLASK_ENV: production
    FLASK_APP: app.py
    PORT: 8000

    # AWS Configuration
    AWS_REGION: us-east-1
    AWS_DEFAULT_REGION: us-east-1

    # Bedrock Configuration
    BEDROCK_MODEL_ID: us.anthropic.claude-sonnet-4-5-20250929-v1:0
    BEDROCK_MAX_TOKENS: "4096"
    BEDROCK_TEMPERATURE: "0.7"
    REASONING_ENABLED: "false"

    # Redis Configuration (will be set after ElastiCache setup)
    REDIS_HOST: ""
    REDIS_PORT: "6379"

    # Application Configuration
    MAX_CONTENT_LENGTH: "16777216"  # 16 MB
    SESSION_TIMEOUT: "3600"  # 1 hour

    # Feature Flags
    ENHANCED_MODE: "true"
    RQ_ENABLED: "true"

  # ============================================
  # MANAGED UPDATES
  # ============================================
  aws:elasticbeanstalk:managedactions:
    ManagedActionsEnabled: true
    PreferredStartTime: "Sun:03:00"  # Sunday 3 AM UTC
    ServiceRoleForManagedUpdates: aws-elasticbeanstalk-service-role

  aws:elasticbeanstalk:managedactions:platformupdate:
    UpdateLevel: minor  # Automatic minor version updates
    InstanceRefreshEnabled: true
EOF
```

### 4.3 Create Package Installation Configuration

```bash
cat > .ebextensions/02_packages.config << 'EOF'
# Package Installation Configuration

packages:
  yum:
    gcc: []
    python3-devel: []
    libxml2-devel: []
    libxslt-devel: []
    git: []

commands:
  01_create_directories:
    command: |
      mkdir -p /var/app/current/uploads
      mkdir -p /var/app/current/data
      mkdir -p /var/log/gunicorn
      chmod 777 /var/app/current/uploads
      chmod 777 /var/app/current/data
      chmod 777 /var/log/gunicorn
    ignoreErrors: true

  02_cleanup_old_uploads:
    command: |
      cat > /etc/cron.daily/cleanup-uploads << 'CLEANUP_SCRIPT'
      #!/bin/bash
      # Clean up files older than 7 days
      find /var/app/current/uploads -type f -mtime +7 -delete
      find /var/app/current/data -type f -mtime +7 -delete
      CLEANUP_SCRIPT
      chmod +x /etc/cron.daily/cleanup-uploads
    ignoreErrors: true

files:
  "/opt/elasticbeanstalk/tasks/taillogs.d/gunicorn.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      /var/log/gunicorn/access.log
      /var/log/gunicorn/error.log

  "/opt/elasticbeanstalk/tasks/bundlelogs.d/gunicorn.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      /var/log/gunicorn/access.log
      /var/log/gunicorn/error.log
EOF
```

### 4.4 Create Procfile

```bash
cat > Procfile << 'EOF'
web: gunicorn --config gunicorn.conf.py app:app
EOF
```

### 4.5 Create Dockerrun Configuration (Alternative to Procfile)

**Option A: Use Python Platform (Recommended)**
Skip this step and use Procfile above.

**Option B: Use Docker Platform**
```bash
cat > Dockerrun.aws.json << 'EOF'
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": 8000,
      "HostPort": 80
    }
  ],
  "Volumes": [
    {
      "HostDirectory": "/var/app/current/uploads",
      "ContainerDirectory": "/app/uploads"
    },
    {
      "HostDirectory": "/var/app/current/data",
      "ContainerDirectory": "/app/data"
    }
  ],
  "Logging": "/var/log/nginx",
  "Environment": []
}
EOF
```

---

## Step 5: Initialize Elastic Beanstalk

### 5.1 Initialize EB Application

```bash
# Navigate to project directory
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2

# Initialize Elastic Beanstalk
eb init

# Follow the prompts:
# 1. Select region: us-east-1 (or your preferred region)
# 2. Select application: Create new Application
# 3. Application name: aiprism
# 4. Platform: Docker (or Python 3.11)
# 5. Platform branch: Docker running on Amazon Linux 2
# 6. CodeCommit: No
# 7. SSH: Yes (select or create key pair)
```

### 5.2 Alternative: Non-Interactive Initialization

```bash
eb init aiprism \
  --platform docker \
  --region us-east-1 \
  --keyname YOUR_KEY_PAIR
```

### 5.3 Verify Initialization

```bash
# Check configuration
cat .elasticbeanstalk/config.yml

# Expected output:
# branch-defaults:
#   default:
#     environment: null
# global:
#   application_name: aiprism
#   default_platform: Docker running on Amazon Linux 2
#   default_region: us-east-1
```

---

## Step 6: Create Environment

### 6.1 Create Production Environment

```bash
# Create production environment
eb create aiprism-production \
  --instance-type t3.medium \
  --scale 2 \
  --envvars \
    AWS_REGION=us-east-1,\
    BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0,\
    BEDROCK_MAX_TOKENS=4096,\
    FLASK_ENV=production,\
    ENHANCED_MODE=true \
  --timeout 20

# This will:
# 1. Create CloudFormation stack
# 2. Launch 2 EC2 instances (t3.medium)
# 3. Create Application Load Balancer
# 4. Configure security groups
# 5. Setup CloudWatch logs
# 6. Deploy your application
#
# Expected time: 10-15 minutes
```

### 6.2 Monitor Environment Creation

```bash
# Watch environment status
eb status

# View events in real-time
eb events --follow

# Check health
eb health
```

### 6.3 Create Development Environment (Optional)

```bash
# Create development environment (single instance, cheaper)
eb create aiprism-development \
  --single \
  --instance-type t3.small \
  --envvars \
    AWS_REGION=us-east-1,\
    BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0,\
    FLASK_ENV=development \
  --timeout 15
```

---

## Step 7: Configure Domain & SSL

### 7.1 Get Environment URL

```bash
# Get automatically generated URL
eb status | grep CNAME

# Example output:
# CNAME: aiprism-production.us-east-1.elasticbeanstalk.com
```

### 7.2 Request SSL Certificate (AWS Certificate Manager)

```bash
# Request certificate
aws acm request-certificate \
  --domain-name aiprism.yourdomain.com \
  --subject-alternative-names www.aiprism.yourdomain.com \
  --validation-method DNS \
  --region us-east-1

# Note the Certificate ARN from output
# ARN: arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID
```

### 7.3 Validate Certificate

```bash
# Get validation records
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID \
  --region us-east-1

# Add the CNAME record to your DNS (Route 53 or external)
# Wait 5-30 minutes for validation
```

### 7.4 Configure HTTPS Listener

```bash
cat > .ebextensions/03_https.config << 'EOF'
# HTTPS Configuration

Resources:
  # HTTPS Listener on port 443
  AWSEBV2LoadBalancerListener443:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn:
        Ref: AWSEBV2LoadBalancer
      Port: 443
      Protocol: HTTPS
      Certificates:
        - CertificateArn: arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID
      DefaultActions:
        - Type: forward
          TargetGroupArn:
            Ref: AWSEBV2LoadBalancerTargetGroup
      SslPolicy: ELBSecurityPolicy-TLS-1-2-2017-01

  # Redirect HTTP to HTTPS
  AWSEBV2LoadBalancerListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn:
        Ref: AWSEBV2LoadBalancer
      Port: 80
      Protocol: HTTP
      DefaultActions:
        - Type: redirect
          RedirectConfig:
            Protocol: HTTPS
            Port: 443
            StatusCode: HTTP_301
EOF

# Deploy configuration
eb deploy
```

### 7.5 Configure Custom Domain (Route 53)

```bash
# Get Load Balancer DNS name
EB_LB_DNS=$(aws elasticbeanstalk describe-environments \
  --environment-names aiprism-production \
  --query 'Environments[0].CNAME' \
  --output text)

# Create Route 53 record
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "aiprism.yourdomain.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "'"$EB_LB_DNS"'"}]
      }
    }]
  }'
```

---

## Step 8: Setup Redis & Database

### 8.1 Create ElastiCache Redis Cluster

```bash
# Create Redis subnet group
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name aiprism-redis-subnet \
  --cache-subnet-group-description "Subnet group for AI-Prism Redis" \
  --subnet-ids subnet-XXXXX subnet-YYYYY

# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id aiprism-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --cache-subnet-group-name aiprism-redis-subnet \
  --security-group-ids sg-XXXXX \
  --port 6379

# Wait for creation (5-10 minutes)
aws elasticache describe-cache-clusters \
  --cache-cluster-id aiprism-redis \
  --show-cache-node-info

# Get Redis endpoint
REDIS_HOST=$(aws elasticache describe-cache-clusters \
  --cache-cluster-id aiprism-redis \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
  --output text)

echo "Redis Host: $REDIS_HOST"
```

### 8.2 Update Environment Variables with Redis

```bash
# Set Redis host in environment
eb setenv REDIS_HOST=$REDIS_HOST REDIS_PORT=6379 RQ_ENABLED=true

# This will restart the environment with new variables
```

### 8.3 Create S3 Bucket for Exports

```bash
# Create S3 bucket
aws s3 mb s3://aiprism-exports-$(date +%s) --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket aiprism-exports-TIMESTAMP \
  --versioning-configuration Status=Enabled

# Set lifecycle policy (delete after 90 days)
cat > lifecycle-policy.json << 'EOF'
{
  "Rules": [{
    "Id": "DeleteOldExports",
    "Status": "Enabled",
    "Prefix": "",
    "Expiration": {
      "Days": 90
    }
  }]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket aiprism-exports-TIMESTAMP \
  --lifecycle-configuration file://lifecycle-policy.json

# Update environment with S3 bucket name
eb setenv S3_EXPORT_BUCKET=aiprism-exports-TIMESTAMP
```

---

## Step 9: Configure Auto-Scaling

### 9.1 Create Scheduled Scaling (Optional - Cost Optimization)

```bash
cat > .ebextensions/04_scheduled_scaling.config << 'EOF'
# Scheduled Scaling Configuration
# Scale down at night, scale up during business hours

Resources:
  # Scale down at 10 PM UTC (2 AM PST / 5 AM EST)
  ScheduledScaleDown:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      AutoScalingGroupName:
        Ref: AWSEBAutoScalingGroup
      MinSize: 1
      MaxSize: 4
      DesiredCapacity: 1
      Recurrence: "0 22 * * *"  # 10 PM UTC daily

  # Scale up at 6 AM UTC (10 PM PST / 1 AM EST)
  ScheduledScaleUp:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      AutoScalingGroupName:
        Ref: AWSEBAutoScalingGroup
      MinSize: 2
      MaxSize: 10
      DesiredCapacity: 2
      Recurrence: "0 6 * * *"  # 6 AM UTC daily

  # Weekend scale down (Saturday midnight)
  WeekendScaleDown:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      AutoScalingGroupName:
        Ref: AWSEBAutoScalingGroup
      MinSize: 1
      MaxSize: 4
      DesiredCapacity: 1
      Recurrence: "0 0 * * 6"  # Saturday midnight

  # Monday scale up
  MondayScaleUp:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      AutoScalingGroupName:
        Ref: AWSEBAutoScalingGroup
      MinSize: 2
      MaxSize: 10
      DesiredCapacity: 2
      Recurrence: "0 6 * * 1"  # Monday 6 AM UTC

option_settings:
  # Custom CloudWatch alarms for advanced scaling
  aws:autoscaling:trigger:
    # Scale based on request count (in addition to CPU)
    MeasureName: RequestCount
    Statistic: Sum
    Unit: Count
    UpperThreshold: 10000  # 10K requests per period
    LowerThreshold: 2000   # 2K requests per period
    Period: 5
    EvaluationPeriods: 1
    BreachDuration: 5
EOF

# Deploy scaling configuration
eb deploy
```

### 9.2 Configure Memory-Based Scaling (Advanced)

```bash
cat > .ebextensions/05_memory_scaling.config << 'EOF'
# Memory-Based Scaling using CloudWatch Alarms

Resources:
  HighMemoryAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmDescription: "Scale up when memory > 80%"
      AlarmActions:
        - Ref: AWSEBAutoScalingScaleUpPolicy
      MetricName: MemoryUtilization
      Namespace: System/Linux
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: AutoScalingGroupName
          Value:
            Ref: AWSEBAutoScalingGroup

  LowMemoryAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmDescription: "Scale down when memory < 30%"
      AlarmActions:
        - Ref: AWSEBAutoScalingScaleDownPolicy
      MetricName: MemoryUtilization
      Namespace: System/Linux
      Statistic: Average
      Period: 300
      EvaluationPeriods: 3
      Threshold: 30
      ComparisonOperator: LessThanThreshold
      Dimensions:
        - Name: AutoScalingGroupName
          Value:
            Ref: AWSEBAutoScalingGroup

commands:
  01_install_cloudwatch_monitoring:
    command: |
      yum install -y perl-Switch perl-DateTime perl-Sys-Syslog perl-LWP-Protocol-https
      cd /tmp
      curl https://aws-cloudwatch.s3.amazonaws.com/downloads/CloudWatchMonitoringScripts-1.2.2.zip -O
      unzip CloudWatchMonitoringScripts-1.2.2.zip
      rm CloudWatchMonitoringScripts-1.2.2.zip

  02_setup_cron:
    command: |
      echo "*/5 * * * * /tmp/aws-scripts-mon/mon-put-instance-data.pl --mem-util --disk-space-util --disk-path=/ --from-cron" | crontab -
EOF

eb deploy
```

---

## Step 10: Monitoring & Logging

### 10.1 Enable Enhanced Health Reporting

```bash
# Already enabled in 01_environment.config
# Verify it's working:
eb health --refresh

# Expected output:
#  aiprism-production                               Ok                2023-11-25 10:30:00
# WebServer                                          PHP 8.1 running on 64bit Amazon Linux 2
# Total: 2      Ok: 2      Warning: 0     Degraded: 0   Severe: 0
# instance-id  status     cause              health
# i-0a1b2c3d  Ok         -                  Ok
# i-4e5f6g7h  Ok         -                  Ok
```

### 10.2 Create CloudWatch Dashboard

```bash
cat > cloudwatch-dashboard.json << 'EOF'
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ElasticBeanstalk", "EnvironmentHealth", {"stat": "Average"}],
          [".", "InstancesOk", {"stat": "Sum"}],
          [".", "InstancesDegraded", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Environment Health",
        "yAxis": {"left": {"min": 0}}
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ElasticBeanstalk", "ApplicationRequests5xx", {"stat": "Sum"}],
          [".", "ApplicationRequests4xx", {"stat": "Sum"}],
          [".", "ApplicationRequests2xx", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Request Status Codes"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ElasticBeanstalk", "ApplicationLatencyP50", {"stat": "Average"}],
          [".", "ApplicationLatencyP90", {"stat": "Average"}],
          [".", "ApplicationLatencyP99", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Application Latency"
      }
    }
  ]
}
EOF

# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name AIPrism-Production \
  --dashboard-body file://cloudwatch-dashboard.json
```

### 10.3 Setup CloudWatch Alarms

```bash
# Create SNS topic for alarms
aws sns create-topic --name aiprism-alerts

# Subscribe email to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:aiprism-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Confirm subscription via email

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name aiprism-high-5xx-errors \
  --alarm-description "Alert when 5xx errors exceed threshold" \
  --metric-name ApplicationRequests5xx \
  --namespace AWS/ElasticBeanstalk \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:aiprism-alerts

aws cloudwatch put-metric-alarm \
  --alarm-name aiprism-environment-degraded \
  --alarm-description "Alert when environment health degrades" \
  --metric-name EnvironmentHealth \
  --namespace AWS/ElasticBeanstalk \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 15 \
  --comparison-operator LessThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:aiprism-alerts
```

### 10.4 View Logs

```bash
# Tail logs in real-time
eb logs --stream

# Download full log bundle
eb logs --all

# View specific log
eb ssh
tail -f /var/log/web.stdout.log
tail -f /var/log/gunicorn/error.log
tail -f /var/log/gunicorn/access.log
```

---

## Ongoing Operations

### Daily Operations

#### Deploy New Version
```bash
# Commit changes
git add .
git commit -m "New feature: improved Claude fallback logic"

# Deploy to production
eb deploy aiprism-production

# Monitor deployment
eb events --follow

# Verify health after deployment
eb health
```

#### Check Application Status
```bash
# Environment status
eb status

# Health check
eb health

# Recent events
eb events

# Open environment in browser
eb open
```

#### View Logs
```bash
# Stream logs
eb logs --stream

# Download logs
eb logs --all --zip

# SSH to instance
eb ssh
```

### Weekly Operations

#### Review CloudWatch Metrics
```bash
# Open CloudWatch console
eb console

# Or view specific metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElasticBeanstalk \
  --metric-name CPUUtilization \
  --dimensions Name=EnvironmentName,Value=aiprism-production \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average
```

#### Check Cost & Billing
```bash
# View cost breakdown
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '1 month ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://filter.json

# filter.json:
# {
#   "Tags": {
#     "Key": "elasticbeanstalk:environment-name",
#     "Values": ["aiprism-production"]
#   }
# }
```

### Monthly Operations

#### Apply Platform Updates
```bash
# Check available updates
eb platform list

# Apply updates (during maintenance window)
eb upgrade

# Or enable automatic updates in console
```

#### Review and Optimize
```bash
# Review instance types and scaling
eb config

# Adjust based on actual usage
# Consider Reserved Instances if stable usage
```

#### Backup Configuration
```bash
# Save configuration
eb config save aiprism-production --cfg production-backup

# Configuration saved to .elasticbeanstalk/saved_configs/
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Deployment Fails

**Symptoms:**
```
ERROR: ServiceError - Failed to deploy application
```

**Solutions:**
```bash
# 1. Check events
eb events

# 2. View detailed logs
eb logs --all

# 3. Check health
eb health

# 4. SSH and investigate
eb ssh
sudo tail -f /var/log/eb-engine.log
sudo tail -f /var/log/web.stdout.log

# 5. Rollback if needed
eb deploy --version <previous-version>
```

#### Issue 2: Application Not Responding

**Symptoms:**
- 502 Bad Gateway errors
- Health check failures

**Solutions:**
```bash
# 1. Check if Gunicorn is running
eb ssh
ps aux | grep gunicorn

# 2. Check Gunicorn logs
sudo tail -100 /var/log/gunicorn/error.log

# 3. Restart application
eb restart

# 4. Check environment variables
eb printenv

# 5. Verify health check endpoint
curl http://localhost:8000/health
```

#### Issue 3: High CPU Usage

**Symptoms:**
- Auto-scaling triggering frequently
- Slow response times

**Solutions:**
```bash
# 1. Check what's consuming CPU
eb ssh
top
htop

# 2. Review application logs for errors
sudo tail -100 /var/log/gunicorn/error.log

# 3. Check Bedrock API latency
# Look for slow Claude API calls

# 4. Optimize Gunicorn workers
# Edit gunicorn.conf.py to adjust worker count

# 5. Consider larger instance type
eb scale --instance-type t3.large
```

#### Issue 4: Redis Connection Errors

**Symptoms:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solutions:**
```bash
# 1. Verify Redis endpoint
eb printenv | grep REDIS

# 2. Check security group rules
# Ensure EB security group can access Redis (port 6379)

# 3. Test connection from instance
eb ssh
redis-cli -h $REDIS_HOST ping
# Expected: PONG

# 4. Verify ElastiCache cluster status
aws elasticache describe-cache-clusters \
  --cache-cluster-id aiprism-redis \
  --show-cache-node-info
```

#### Issue 5: Out of Memory

**Symptoms:**
```
MemoryError: Unable to allocate memory
```

**Solutions:**
```bash
# 1. Check memory usage
eb ssh
free -h

# 2. Identify memory-consuming processes
ps aux --sort=-%mem | head

# 3. Review Gunicorn worker count
# Reduce workers if memory constrained

# 4. Upgrade to larger instance type
eb scale --instance-type t3.large  # 8 GB RAM

# 5. Add swap space (temporary solution)
sudo dd if=/dev/zero of=/swapfile bs=1G count=2
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Getting Help

#### AWS Support
```bash
# Create support case
aws support create-case \
  --subject "Elastic Beanstalk deployment issue" \
  --service-code "elastic-beanstalk" \
  --severity-code "normal" \
  --category-code "deployment-issues" \
  --communication-body "Description of issue..."
```

#### Useful Commands
```bash
# Complete environment info
eb status --verbose

# All recent events
eb events --follow

# Full log bundle
eb logs --all --zip

# Environment configuration
eb config

# Platform information
eb platform list

# SSH access
eb ssh
```

---

## Next Steps

### After Successful Deployment

1. **Test Application**
   ```bash
   # Get URL
   eb open

   # Test endpoints
   curl https://your-domain.com/health
   curl https://your-domain.com/
   ```

2. **Configure Monitoring**
   - Setup CloudWatch dashboards
   - Configure SNS alerts
   - Review logs regularly

3. **Optimize Costs**
   - Enable scheduled scaling
   - Consider Reserved Instances
   - Review unused resources

4. **Security Hardening**
   - Enable AWS WAF
   - Configure VPC security groups
   - Enable CloudTrail logging
   - Regular security audits

5. **Backup & DR**
   - Document environment configuration
   - Setup cross-region backup (optional)
   - Test disaster recovery procedures

---

## Cost Optimization Tips

### Immediate Savings

1. **Use Scheduled Scaling**
   - Scale down during off-hours (saves 50%)
   - Already configured in Step 9.1

2. **Right-Size Instances**
   ```bash
   # Monitor actual usage for 1 week
   eb health --refresh

   # If CPU < 30% consistently, downgrade to t3.small
   eb scale --instance-type t3.small
   ```

3. **Enable Spot Instances (Dev/Test)**
   ```bash
   # Dev environment only
   eb create aiprism-dev \
     --instance-type t3.medium \
     --enable-spot \
     --spot-max-price 0.03
   ```

### Long-Term Savings

1. **Purchase Reserved Instances**
   ```bash
   # If stable usage for 1+ years
   # Save 40-60% on compute costs

   # Purchase via AWS Console:
   # EC2 > Reserved Instances > Purchase Reserved Instances
   # Choose: t3.medium, 1-year, All Upfront
   ```

2. **Use Savings Plans**
   - Flexible commitment across AWS services
   - 3-year plans save up to 72%

---

## Summary

You've successfully deployed AI-Prism to AWS Elastic Beanstalk!

### What You've Accomplished
✅ Configured Elastic Beanstalk environment
✅ Deployed Flask application with Gunicorn
✅ Setup auto-scaling (2-10 instances)
✅ Configured HTTPS with SSL certificate
✅ Integrated with ElastiCache Redis
✅ Enabled CloudWatch monitoring & logging
✅ Implemented zero-downtime deployments
✅ Configured health checks & alarms

### Monthly Cost Estimate
- **Production:** $150-200/month
- **Development:** $40-80/month (if created)

### Key Commands to Remember
```bash
eb deploy                    # Deploy new version
eb status                    # Check environment status
eb health                    # View health status
eb logs --stream            # Tail logs
eb ssh                       # Connect to instance
eb config                    # Edit configuration
eb console                   # Open AWS console
```

### Support Resources
- 📚 [Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- 💬 [AWS Forums](https://forums.aws.amazon.com/forum.jspa?forumID=86)
- 🎫 [AWS Support](https://console.aws.amazon.com/support/)

**Congratulations!** Your application is now running on production-grade AWS infrastructure with auto-scaling, monitoring, and zero-downtime deployments.
