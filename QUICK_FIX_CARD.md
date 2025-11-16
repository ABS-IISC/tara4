# 🚨 Quick Fix Card - Claude 500 Error on App Runner

**Problem:** ❌ Claude error: Server error: 500 Internal Server Error
**Cause:** App Runner has no permission to call Bedrock (Claude)
**Fix Time:** 10 minutes

---

## 🎯 3-Step Fix

### 1️⃣ Create IAM Policy (2 min)

```
AWS Console → IAM → Policies → Create Policy → JSON tab
```

**Paste this:**
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
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
        },
        {
            "Effect": "Allow",
            "Action": ["s3:PutObject", "s3:GetObject", "s3:ListBucket"],
            "Resource": [
                "arn:aws:s3:::felix-s3-bucket/*",
                "arn:aws:s3:::felix-s3-bucket"
            ]
        }
    ]
}
```

**Name:** `AppRunner-Bedrock-S3-FullAccess`

---

### 2️⃣ Create IAM Role (3 min)

```
AWS Console → IAM → Roles → Create Role
```

- **Trusted entity:** AWS service → App Runner
- **Attach policy:** `AppRunner-Bedrock-S3-FullAccess`
- **Name:** `AppRunner-Bedrock-Access-Role`

---

### 3️⃣ Attach Role to App Runner (2 min)

```
AWS Console → App Runner → Your Service → Configuration → Security → Edit
```

- **Instance role:** `AppRunner-Bedrock-Access-Role`
- **Save changes**

⏳ **Wait 5-10 minutes** for redeployment

---

## ✅ Test

1. Open your App Runner URL
2. Upload document
3. Click "Analyze"
4. **Should work!** 🎉

---

## 📋 Your Configuration (Already Perfect!)

```
✅ BEDROCK_MODEL_ID: anthropic.claude-3-5-sonnet-20240620-v1:0
✅ AWS_REGION: us-east-1
✅ All 13 Claude models configured
✅ Automatic fallback enabled
```

**Don't change any environment variables!**

---

## 🆘 Still Not Working?

**Check:**
1. Waited 5-10 minutes?
2. App Runner status = "Running" (green)?
3. Role attached? (Configuration → Security → Instance role)

**Logs:**
```
App Runner → Logs → Application logs
```

Look for: `AccessDeniedException` or `500` errors

---

## 📚 Full Guides

- **Simple Guide:** `APP_RUNNER_CLAUDE_FIX_SIMPLE_GUIDE.md`
- **Complete Guide:** `APP_RUNNER_COMPLETE_SETUP_GUIDE.md`
- **Verify Models:** Run `python3 verify_models.py`

---

## 🎯 Success = No More Errors!

When it works:
- ✅ Upload works
- ✅ Analyze shows feedback
- ✅ No 500 errors
- ✅ Claude responds

---

**Created:** November 17, 2025
**Fix:** IAM permissions for App Runner
