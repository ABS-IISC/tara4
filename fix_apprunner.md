# Fix AWS App Runner Bedrock Configuration

## Issue
Your TARA chat shows "Sorry, all AI models are currently unavailable" because of AWS Bedrock configuration issues.

## Quick Fixes

### 1. Update Environment Variables in App Runner

In your App Runner service settings, update these environment variables:

**Current (Wrong):**
```
BEDROCK_MODEL_ID = anthropic.claude-v2
```

**Fixed (Correct):**
```
BEDROCK_MODEL_ID = anthropic.claude-3-sonnet-20240229-v1:0
```

### 2. Create IAM Role for App Runner

Your App Runner service needs an IAM role with Bedrock permissions:

**IAM Policy JSON:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

### 3. App Runner Service Configuration

**Complete Environment Variables:**
```
AWS_REGION = us-east-1
BEDROCK_MODEL_ID = anthropic.claude-3-sonnet-20240229-v1:0
FLASK_ENV = production
PORT = 8080
```

**IAM Role:**
- Create IAM role named: `AppRunner-TARA-Bedrock-Role`
- Attach the Bedrock policy above
- Assign this role to your App Runner service

### 4. Alternative Model IDs (if Claude 3 Sonnet doesn't work)

Try these in order:
1. `anthropic.claude-3-sonnet-20240229-v1:0` (recommended)
2. `anthropic.claude-3-haiku-20240307-v1:0` (faster, cheaper)
3. `anthropic.claude-v2:1` (legacy, if others fail)

### 5. Test Configuration

Run this command locally to test:
```bash
python test_aws.py
```

## Step-by-Step Fix

1. **Update App Runner Environment Variables:**
   - Go to AWS App Runner Console
   - Select your service: `bedrock-app-runner-service`
   - Go to Configuration → Environment variables
   - Update `BEDROCK_MODEL_ID` to: `anthropic.claude-3-sonnet-20240229-v1:0`

2. **Create IAM Role:**
   - Go to IAM Console
   - Create new role for "AWS Service" → "App Runner"
   - Attach custom policy with Bedrock permissions (JSON above)
   - Name it: `AppRunner-TARA-Bedrock-Role`

3. **Assign IAM Role to App Runner:**
   - Go back to App Runner service
   - Configuration → Security
   - Set Instance role to: `AppRunner-TARA-Bedrock-Role`

4. **Deploy Changes:**
   - Click "Deploy" to restart with new configuration

## Verification

After changes, the chat should work. If still failing:

1. Check CloudWatch logs for specific error messages
2. Verify Bedrock is available in `us-east-1` region
3. Ensure your AWS account has Bedrock access enabled
4. Try the alternative model IDs listed above

## Common Issues

- **"Model not found"**: Wrong model ID format
- **"Access denied"**: Missing IAM permissions  
- **"Service unavailable"**: Bedrock not enabled in region
- **"Credentials not found"**: IAM role not assigned to App Runner

The fix should take 5-10 minutes and immediately resolve the chat functionality.