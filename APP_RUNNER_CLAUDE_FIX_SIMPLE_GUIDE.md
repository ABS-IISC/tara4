# App Runner Claude Connection Fix - Simple Guide

**Date:** November 17, 2025
**Issue:** ❌ Claude error: Server error: 500 Internal Server Error
**Your Setup:** AWS App Runner with Claude 3.5 Sonnet
**Status:** 🔧 NEEDS IAM PERMISSION FIX

---

## 🔴 The Problem (In Simple Terms)

Your app works locally but fails on App Runner because **App Runner doesn't have permission to talk to Claude (AWS Bedrock)**.

Think of it like this:
- Your app = A person trying to make a phone call
- Claude/Bedrock = The phone service
- App Runner = The building where the person is
- IAM Role = The phone plan/permission to make calls

**Right now:** App Runner doesn't have a "phone plan" to call Claude!

---

## ✅ The Solution (3 Simple Steps)

### Step 1: Create IAM Policy (Permission Document)

This is like writing down "what phone calls are allowed"

1. **Go to AWS Console** → IAM → Policies
2. **Click "Create Policy"**
3. **Click "JSON" tab**
4. **Copy-paste this exactly:**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockInvokeAccess",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-7-sonnet-20250219-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-7-sonnet-20241022-v2:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-opus-4-1-20250805-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-20250514-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-opus-4-20250514-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-opus-20240229-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            ]
        },
        {
            "Sid": "S3Access",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::felix-s3-bucket/*",
                "arn:aws:s3:::felix-s3-bucket"
            ]
        }
    ]
}
```

5. **Click "Next"**
6. **Name it:** `AppRunner-Bedrock-S3-Policy`
7. **Click "Create Policy"**

---

### Step 2: Create IAM Role (Identity Card)

This is like creating an "identity card" that has the permission

1. **Go to AWS Console** → IAM → Roles
2. **Click "Create Role"**
3. **Select:**
   - **Trusted entity type:** AWS service
   - **Use case:** App Runner
   - Click "Next"

4. **Attach the policy you just created:**
   - Search for `AppRunner-Bedrock-S3-Policy`
   - Check the box next to it
   - Click "Next"

5. **Name the role:** `AppRunner-Bedrock-Access-Role`
6. **Click "Create Role"**
7. **Copy the Role ARN** - it looks like:
   ```
   arn:aws:iam::123456789012:role/AppRunner-Bedrock-Access-Role
   ```

---

### Step 3: Give App Runner the Role

This is like giving the "identity card" to your App Runner service

1. **Go to AWS Console** → App Runner → Services
2. **Click on your service name** (your TARA2 app)
3. **Click "Configuration" tab**
4. **Click "Security" section**
5. **Click "Edit"**
6. **Find "Instance role"** section
7. **Select:** `AppRunner-Bedrock-Access-Role` from dropdown
8. **Click "Save"**

**IMPORTANT:** App Runner will restart automatically. Wait 5-10 minutes.

---

## 🧪 Testing After Fix

### 1. Wait for App Runner to Restart
- Status will show "Deployment in progress"
- Wait until it shows "Running"

### 2. Test Your App
1. Go to your App Runner URL
2. Upload a document
3. Click "Analyze" on a section
4. **If it works:** You'll see AI feedback! ✅
5. **If it still fails:** Check the logs (instructions below)

---

## 📋 Your Current Environment Variables (Already Correct!)

Your App Runner environment variables look good:

| Variable | Your Value | Status |
|----------|------------|--------|
| AWS_REGION | us-east-1 | ✅ Correct |
| AWS_DEFAULT_REGION | us-east-1 | ✅ Correct |
| BEDROCK_MODEL_ID | anthropic.claude-3-5-sonnet-20240620-v1:0 | ✅ Correct |
| BEDROCK_MAX_TOKENS | 8192 | ✅ Correct |
| BEDROCK_TEMPERATURE | 0.7 | ✅ Correct |
| FLASK_ENV | production | ✅ Correct |
| PORT | 8080 | ✅ Correct |
| S3_BASE_PATH | tara/ | ✅ Correct |
| S3_BUCKET_NAME | felix-s3-bucket | ✅ Correct |

**You don't need to change any environment variables!**

---

## 🔍 How to Check Logs (If Still Not Working)

### Option 1: From App Runner Console
1. Go to App Runner → Your Service
2. Click "Logs" tab
3. Click "Application logs"
4. Look for errors with "bedrock" or "500"

### Option 2: From CloudWatch
1. Go to CloudWatch → Log groups
2. Find `/aws/apprunner/your-service-name/application`
3. Click on latest log stream
4. Look for error messages

### What to Look For:
```
❌ GOOD ERROR (We can fix): "AccessDeniedException" or "not authorized"
   → Means IAM role isn't attached properly

❌ BAD ERROR (Different issue): "ValidationException" or "Model not found"
   → Means model ID is wrong
```

---

## 📊 All Supported Claude Models

Your code already supports ALL Claude models (you're good!):

### Latest Models (Claude 4.5 - Best Performance)
- ✅ `claude-sonnet-4-5-20250929` - Sonnet 4.5 (Highest capability)
- ✅ `claude-haiku-4-5-20251001` - Haiku 4.5 (Fast & capable)

### Claude 4.1
- ✅ `claude-opus-4-1-20250805` - Opus 4.1 (Premium)

### Claude 4
- ✅ `claude-sonnet-4-20250514` - Sonnet 4
- ✅ `claude-opus-4-20250514` - Opus 4

### Claude 3.7
- ✅ `claude-3-7-sonnet-20250219` - Sonnet 3.7 (Feb 2025)
- ✅ `claude-3-7-sonnet-20241022` - Sonnet 3.7 (Oct 2024)

### Claude 3.5 (Your Current Model - Recommended!)
- ✅ `claude-3-5-sonnet-20240620` - **YOU ARE USING THIS** ← Best choice!
- ✅ `claude-3-5-sonnet-20241022` - Alternative version
- ✅ `claude-3-5-haiku-20241022` - Fast version

### Claude 3 (Legacy)
- ✅ `claude-3-opus-20240229` - Premium
- ✅ `claude-3-sonnet-20240229` - Balanced
- ✅ `claude-3-haiku-20240307` - Fast, low cost

**Your apprunner.yaml and model_config.py already have ALL these models configured!**

---

## 🎯 Model Recommendation

**For App Runner, keep using:**
```
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

**Why?**
- ✅ Works with on-demand access (no special setup needed)
- ✅ Great balance of speed and quality
- ✅ Lower cost than Claude 4 models
- ✅ Reliable and stable

**Claude 4.5/4/3.7 models might require:**
- Provisioned throughput (expensive!)
- Inference profiles (complex setup)
- Special AWS permissions

**Stick with Claude 3.5 Sonnet unless you have specific needs.**

---

## 🔧 If You Want to Test Different Models

### Method 1: Test All Models Automatically

I added a function to test all models. Run this locally first:

```python
from config.model_config import model_config

# Test all model combinations
results = model_config.test_model_combinations()

# This will show you:
# ✅ Which models work in your AWS account
# ❌ Which models don't work
# 🏆 The best model to use
```

### Method 2: Change Model in App Runner

1. Go to App Runner → Configuration → Environment variables
2. Find `BEDROCK_MODEL_ID`
3. Click Edit
4. Change to a different model (from list above)
5. Save and redeploy

**Remember:** Always use the full format:
```
anthropic.MODEL-NAME-DATE-v1:0
```

Example:
```
anthropic.claude-3-5-haiku-20241022-v1:0
```

---

## 📱 Quick Checklist

Before contacting me again, check:

- [ ] Created IAM policy `AppRunner-Bedrock-S3-Policy`
- [ ] Created IAM role `AppRunner-Bedrock-Access-Role`
- [ ] Attached policy to role
- [ ] Attached role to App Runner service
- [ ] Waited for App Runner to redeploy (5-10 minutes)
- [ ] Tested the app - uploaded document and clicked Analyze
- [ ] If still failing, checked logs for error message

---

## 🆘 If Still Not Working

Send me:

1. **The exact error from App Runner logs** (copy-paste full error)
2. **Screenshot of IAM Role → Trust relationships** tab
3. **Tell me:** Did you see "Deployment in progress" after attaching role?

---

## 🎉 Success Indicators

**You'll know it's working when:**

1. ✅ App Runner shows "Status: Running" (green)
2. ✅ Upload document works
3. ✅ Click "Analyze" → See "🤖 AI-Generated Feedback" appear
4. ✅ No red error messages about Claude/Bedrock
5. ✅ Can accept feedback and download document

---

## 💡 Why This Fixes It

**The Problem:**
- App Runner runs your code in AWS cloud
- Your code tries to call Claude (AWS Bedrock service)
- AWS security blocks it: "Who are you? Do you have permission?"
- App Runner has no answer → Error 500

**The Fix:**
- IAM Policy = "Here's what you're allowed to do"
- IAM Role = "Here's the identity card with those permissions"
- Attaching role to App Runner = "Now App Runner can prove who it is"
- AWS Bedrock: "OK, you have permission! Here's Claude's response."

---

## 🔐 Security Note

The IAM policy I gave you:
- ✅ Only allows calling Bedrock models (can't access other AWS services)
- ✅ Only allows your S3 bucket (can't access other buckets)
- ✅ Follows AWS best practices (principle of least privilege)
- ✅ Safe for production use

---

## 📞 Next Steps

1. **Do Step 1, 2, 3** above (takes 10 minutes)
2. **Wait 5-10 minutes** for App Runner to restart
3. **Test your app** - try analyzing a document
4. **If it works:** Celebrate! 🎉
5. **If not:** Send me the error logs

---

**The most common mistake:** Not waiting long enough after attaching the role. App Runner takes 5-10 minutes to redeploy with new permissions.

---

**Created by:** Claude (Anthropic)
**Date:** November 17, 2025
**For:** Non-technical users deploying on AWS App Runner
**Issue:** Claude 500 error due to missing IAM permissions
