# 🚀 AWS Bedrock Setup Guide for AI-Prism

This guide will help you configure AWS Bedrock to enable real AI analysis in AI-Prism.

## 📋 Prerequisites

1. **AWS Account** with Bedrock access
2. **Claude 3.7 Sonnet model access** in AWS Bedrock
3. **Appropriate IAM permissions** for Bedrock

## 🔧 Quick Setup Methods

### Method 1: Environment Variables (Recommended for Development)

Set these environment variables in your system:

```bash
# Windows (Command Prompt)
set AWS_ACCESS_KEY_ID=your_access_key_here
set AWS_SECRET_ACCESS_KEY=your_secret_key_here
set AWS_DEFAULT_REGION=us-east-1

# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key_here"
$env:AWS_DEFAULT_REGION="us-east-1"

# Linux/macOS
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=us-east-1
```

### Method 2: AWS CLI Configuration

1. **Install AWS CLI** (if not already installed):
   ```bash
   # Windows
   winget install Amazon.AWSCLI
   
   # macOS
   brew install awscli
   
   # Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **Configure AWS CLI**:
   ```bash
   aws configure
   ```
   
   Enter when prompted:
   - **AWS Access Key ID**: Your access key
   - **AWS Secret Access Key**: Your secret key
   - **Default region name**: `us-east-1` (or your preferred region)
   - **Default output format**: `json`

### Method 3: IAM Roles (For EC2/Lambda deployment)

If running on AWS infrastructure, attach an IAM role with Bedrock permissions.

## 🔑 Required IAM Permissions

Your AWS user/role needs these permissions:

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
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-7-sonnet-20250219-v1:0",
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
            ]
        }
    ]
}
```

## 🌍 Supported AWS Regions

Claude 3.7 Sonnet is available in these regions:
- **us-east-1** (N. Virginia) - Recommended
- **us-west-2** (Oregon)
- **eu-west-1** (Ireland)
- **ap-southeast-1** (Singapore)

## 🧪 Test Your Configuration

Run the test script to verify everything is working:

```bash
python test_bedrock_connection.py
```

Expected output for successful setup:
```
🧪 AI-PRISM AWS BEDROCK CONNECTION TEST
====================================
🔐 Testing AWS Credentials...
   AWS_ACCESS_KEY_ID: ✅ Set
   AWS_SECRET_ACCESS_KEY: ✅ Set
   AWS_DEFAULT_REGION: us-east-1

🚀 Testing AWS Bedrock Access...
   ✅ Bedrock client created successfully
   📍 Region: us-east-1
   🤖 Model ID: anthropic.claude-3-7-sonnet-20250219-v1:0

🧠 Testing Claude Sonnet Model...
   📤 Sending test request...
   ✅ Model responded successfully!
   💬 Response: Hello from AI-Prism! I am working correctly...

📊 TEST SUMMARY
===============
🔐 AWS Credentials: ✅ OK
🚀 Bedrock Access: ✅ OK
🧠 Claude Model: ✅ OK

🎉 ALL TESTS PASSED! AI-Prism is ready to use AWS Bedrock.
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### ❌ "Credentials not found"
**Solution**: Set up AWS credentials using Method 1 or 2 above.

#### ❌ "Access Denied" or "UnauthorizedOperation"
**Solution**: 
1. Check IAM permissions (see Required IAM Permissions section)
2. Ensure your AWS account has Bedrock access enabled
3. Verify the model is available in your region

#### ❌ "Model not found" or "ValidationException"
**Solution**:
1. Check if Claude 3.7 Sonnet is available in your region
2. Try a different region (us-east-1 recommended)
3. Verify model ID in the configuration

#### ❌ "ThrottlingException" or "Rate exceeded"
**Solution**:
1. Wait a few minutes and try again
2. Implement exponential backoff (already built into AI-Prism)
3. Check your Bedrock usage limits

#### ❌ "Region not supported"
**Solution**:
1. Switch to a supported region (us-east-1 recommended)
2. Update AWS_DEFAULT_REGION environment variable

## 🔄 Fallback Behavior

If AWS Bedrock is not available, AI-Prism will:
1. ✅ **Try primary model** (Claude 3.7 Sonnet)
2. ✅ **Try fallback models** (Claude 3.5 Sonnet, Claude 3 Sonnet)
3. ✅ **Use mock responses** if all models fail
4. ✅ **Continue functioning** with simulated AI analysis

This ensures AI-Prism always works, even without AWS access.

## 💰 Cost Considerations

**Claude 3.7 Sonnet Pricing** (as of 2024):
- Input tokens: ~$3.00 per 1M tokens
- Output tokens: ~$15.00 per 1M tokens

**Typical AI-Prism Usage**:
- Document analysis: ~2,000-5,000 tokens per section
- Chat responses: ~500-1,500 tokens per query
- **Estimated cost**: $0.10-0.50 per document analysis

## 🔒 Security Best Practices

1. **Never commit credentials** to version control
2. **Use IAM roles** when possible (for AWS deployments)
3. **Rotate access keys** regularly
4. **Use least privilege** IAM permissions
5. **Monitor usage** in AWS CloudTrail
6. **Set up billing alerts** to avoid unexpected charges

## 📞 Getting Help

If you need help with AWS setup:
1. **AWS Documentation**: https://docs.aws.amazon.com/bedrock/
2. **AWS Support**: Create a support case in AWS Console
3. **AI-Prism Test Script**: Run `python test_bedrock_connection.py`

---

**✅ Once configured, AI-Prism will provide real AI analysis with the Hawkeye framework!**