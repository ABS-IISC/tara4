# 🚀 TARA AWS App Runner Deployment Guide

Complete guide for deploying TARA Document Analysis Tool to AWS App Runner via ECR.

## 📋 Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed and running
- AWS account with ECR and App Runner access
- IAM role with Bedrock permissions for AI features

## 🔧 Required AWS Permissions

Your AWS user/role needs these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:*",
                "apprunner:*",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole",
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🏗️ Step 1: Setup ECR Repository

```bash
# Make script executable
chmod +x setup-ecr.sh

# Create ECR repository
./setup-ecr.sh us-east-1 tara-app
```

## 📦 Step 2: Build and Deploy

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy to ECR
./deploy.sh us-east-1 tara-app latest
```

## ☁️ Step 3: Create App Runner Service

### Via AWS Console:
1. Go to AWS App Runner console
2. Click "Create service"
3. Choose "Container registry"
4. Select "Amazon ECR"
5. Enter ECR URI: `{account-id}.dkr.ecr.us-east-1.amazonaws.com/tara-app:latest`
6. Configure service settings:
   - **Service name**: `tara-document-analyzer`
   - **Port**: `8000`
   - **Environment variables**:
     ```
     PORT=8000
     FLASK_ENV=production
     AWS_DEFAULT_REGION=us-east-1
     ```

### Via AWS CLI:
```bash
# Create apprunner.yaml configuration
aws apprunner create-service \
    --service-name tara-document-analyzer \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "{account-id}.dkr.ecr.us-east-1.amazonaws.com/tara-app:latest",
            "ImageConfiguration": {
                "Port": "8000",
                "RuntimeEnvironmentVariables": {
                    "PORT": "8000",
                    "FLASK_ENV": "production",
                    "AWS_DEFAULT_REGION": "us-east-1"
                }
            },
            "ImageRepositoryType": "ECR"
        },
        "AutoDeploymentsEnabled": true
    }' \
    --instance-configuration '{
        "Cpu": "1 vCPU",
        "Memory": "2 GB"
    }'
```

## 🔐 Step 4: Configure IAM Role for Bedrock

Create IAM role for App Runner to access Bedrock:

```bash
# Create trust policy
cat > trust-policy.json << EOF
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
EOF

# Create IAM role
aws iam create-role \
    --role-name TaraAppRunnerRole \
    --assume-role-policy-document file://trust-policy.json

# Attach Bedrock policy
aws iam attach-role-policy \
    --role-name TaraAppRunnerRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

## 🔄 Step 5: Update App Runner Service

Associate IAM role with App Runner service:

```bash
aws apprunner update-service \
    --service-arn {service-arn} \
    --instance-configuration '{
        "Cpu": "1 vCPU",
        "Memory": "2 GB",
        "InstanceRoleArn": "arn:aws:iam::{account-id}:role/TaraAppRunnerRole"
    }'
```

## 📊 Monitoring & Logs

- **Service URL**: Available in App Runner console
- **Logs**: CloudWatch Logs group `/aws/apprunner/{service-name}`
- **Metrics**: CloudWatch metrics for App Runner

## 🔧 Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | `8000` | Application port |
| `FLASK_ENV` | `production` | Flask environment |
| `AWS_DEFAULT_REGION` | `us-east-1` | AWS region for Bedrock |

## 🚀 Quick Deploy Commands

```bash
# Complete deployment in one go
chmod +x setup-ecr.sh deploy.sh
./setup-ecr.sh us-east-1 tara-app
./deploy.sh us-east-1 tara-app latest
```

## 🔍 Troubleshooting

### Common Issues:

1. **ECR Login Failed**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin {ecr-uri}
   ```

2. **App Runner Service Failed**
   - Check CloudWatch logs
   - Verify IAM role permissions
   - Ensure port 8000 is configured

3. **AI Features Not Working**
   - Verify Bedrock permissions
   - Check AWS region configuration
   - Ensure IAM role is attached

## 💰 Cost Optimization

- **Instance Size**: Start with 1 vCPU, 2 GB RAM
- **Auto Scaling**: Configure based on usage
- **ECR Lifecycle**: Automatic cleanup of old images

## 🔒 Security Best Practices

- Use least privilege IAM policies
- Enable ECR image scanning
- Configure VPC connector if needed
- Use AWS Secrets Manager for sensitive data

## 📈 Scaling Configuration

```yaml
# Auto scaling settings
MinSize: 1
MaxSize: 10
MaxConcurrency: 100
```

Your TARA application will be available at the App Runner service URL once deployment completes!