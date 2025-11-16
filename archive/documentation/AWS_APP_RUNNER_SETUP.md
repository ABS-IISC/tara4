# AWS App Runner Deployment Guide

## ✅ Code Successfully Pushed to GitHub
Repository: https://github.com/ABS-IISC/Document_Review_tool.git

## 🚀 Deploy to AWS App Runner

### Step 1: Create App Runner Service
1. Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner/)
2. Click "Create service"
3. Select "Source code repository"

### Step 2: Connect to GitHub
1. Choose "GitHub" as source
2. Connect to repository: `ABS-IISC/Document_Review_tool`
3. Branch: `main`
4. Deployment trigger: "Automatic"

### Step 3: Configure Build
1. Configuration file: `Use configuration file` 
2. File: `apprunner.yaml` (already included in repo)

### Step 4: Service Settings
- **Service name**: `tara-document-analyzer`
- **Port**: `8000`
- **CPU**: `1 vCPU`
- **Memory**: `2 GB`

### Step 5: Environment Variables
Add these environment variables:
```
PORT=8000
AWS_DEFAULT_REGION=us-east-1
```

### Step 6: IAM Role (CRITICAL)
Create IAM role with these permissions:
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
            "Resource": "*"
        }
    ]
}
```

### Step 7: Deploy
1. Click "Create & deploy"
2. Wait 5-10 minutes for deployment
3. Access your app at the provided URL

## 🔧 Post-Deployment
- Test document upload functionality
- Verify AI analysis is working
- Check all features are operational

## 📋 Deployment Status
- ✅ Code pushed to GitHub
- ✅ apprunner.yaml configured
- ✅ Dockerfile ready
- ✅ Requirements specified
- ⏳ Awaiting App Runner deployment

## 🆘 Troubleshooting
If deployment fails:
1. Check IAM role has Bedrock permissions
2. Verify environment variables are set
3. Check App Runner logs for errors
4. Ensure port 8000 is configured correctly