# Fix tara4 App Runner - Claude 500 Error

**Your Service:** tara4
**URL:** https://yymivpdgyd.us-east-1.awsapprunner.com
**Status:** Running but Claude failing
**Problem:** No IAM Instance Role attached

---

## 🔴 The Issue

Your App Runner service is missing the **Instance role** that gives permission to call Bedrock (Claude).

**I can see from your configuration:**
- ✅ Environment variables are correct
- ✅ Service is running
- ❌ **No Instance role shown** (this is the problem!)

---

## ✅ Step-by-Step Fix

### Step 1: Create IAM Policy

1. **Open new tab:** https://console.aws.amazon.com/iam/home#/policies

2. **Click:** "Create policy"

3. **Click:** "JSON" tab

4. **Delete everything** and paste:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockAccess",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
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
                "arn:aws:s3:::felix-s3-bucket",
                "arn:aws:s3:::felix-s3-bucket/*"
            ]
        }
    ]
}
```

5. **Click:** "Next"

6. **Policy name:** `tara4-bedrock-s3-policy`

7. **Click:** "Create policy"

---

### Step 2: Create IAM Role

1. **Open new tab:** https://console.aws.amazon.com/iam/home#/roles

2. **Click:** "Create role"

3. **Select:**
   - **Trusted entity type:** AWS service
   - **Use case:** App Runner
   - **Click:** "Next"

4. **Attach policy:**
   - In search box, type: `tara4-bedrock-s3-policy`
   - **Check the box** next to it
   - **Click:** "Next"

5. **Role name:** `tara4-apprunner-role`

6. **Click:** "Create role"

7. **Find your role:**
   - Click on `tara4-apprunner-role`
   - **Copy the ARN** (looks like):
     ```
     arn:aws:iam::758897368787:role/tara4-apprunner-role
     ```

---

### Step 3: Attach Role to tara4 Service

**Option A: Using AWS Console (Easier)**

1. **Go to:** https://console.aws.amazon.com/apprunner/home?region=us-east-1#/services

2. **Click on:** `tara4`

3. **Click:** "Configuration" tab at the top

4. **Scroll down to:** "Security" section

5. **Click:** "Edit" button (next to Security)

6. **Find:** "Instance role" dropdown

7. **Select:** `tara4-apprunner-role`

8. **Click:** "Save changes" at bottom

**Option B: Using AWS CLI (If you prefer)**

```bash
aws apprunner update-service \
  --service-arn arn:aws:apprunner:us-east-1:758897368787:service/tara4/ae6df5459ea8441b9e7c58f155b3a5ae \
  --instance-configuration InstanceRoleArn=arn:aws:iam::758897368787:role/tara4-apprunner-role \
  --region us-east-1
```

---

### Step 4: Wait for Redeployment

**⏳ CRITICAL: You MUST wait!**

1. After saving, App Runner will show: **"Update in progress"**
2. Status will change to: **"Operation in progress"**
3. **Wait 5-10 minutes** for automatic redeployment
4. Status will return to: **"Running"** (green)

**DO NOT test until status is "Running"!**

---

## 🧪 Test After Redeployment

### 1. Check Status First

Go to: https://console.aws.amazon.com/apprunner/home?region=us-east-1#/services/tara4

Wait until you see:
- ✅ Status: **Running** (green circle)
- ✅ No "Update in progress" message

### 2. Test Your App

1. **Open:** https://yymivpdgyd.us-east-1.awsapprunner.com

2. **Upload a Word document**

3. **Click "Analyze"** on any section

4. **Expected result:**
   - ✅ Loading spinner appears
   - ✅ Feedback items show up
   - ✅ No 500 error
   - ✅ Can accept/reject feedback

---

## 🔍 Verify Role is Attached

After redeployment, check if role is attached:

1. Go to: https://console.aws.amazon.com/apprunner/home?region=us-east-1#/services/tara4

2. Click: **"Configuration"** tab

3. Scroll to: **"Security"** section

4. **You should see:**
   ```
   Instance role: tara4-apprunner-role
   ```

**If you DON'T see the role there, it didn't attach properly - repeat Step 3.**

---

## 📊 What Should Happen

### Before Fix:
```
User uploads doc → Clicks Analyze
→ App tries to call Claude
→ AWS Bedrock says "Who are you?"
→ App has no answer (no role)
→ ❌ 500 Internal Server Error
```

### After Fix:
```
User uploads doc → Clicks Analyze
→ App tries to call Claude
→ AWS Bedrock says "Who are you?"
→ App shows Instance Role: tara4-apprunner-role
→ AWS checks role → Has bedrock:InvokeModel permission
→ ✅ Claude responds with feedback
```

---

## 🆘 Troubleshooting

### Issue 1: Role Not Showing After Attach

**Problem:** Clicked "Save" but role doesn't appear in Configuration

**Solution:**
1. Go back to Security → Edit
2. Make sure dropdown shows `tara4-apprunner-role`
3. Click Save again
4. Refresh the page after 1 minute

### Issue 2: Still Getting 500 Error

**Check these:**

1. **Did you wait 5-10 minutes?**
   - App Runner needs time to redeploy with new role
   - Check status is "Running" not "Update in progress"

2. **Is role attached?**
   - Configuration → Security → Instance role should show role name
   - If empty, repeat Step 3

3. **Check logs:**
   - Go to: tara4 → Logs → Application logs
   - Look for error message
   - If you see `AccessDeniedException` → Role not working
   - If you see `ValidationException` → Different issue

### Issue 3: AccessDeniedException in Logs

**Error:** `User: arn:aws:sts::758897368787:assumed-role/tara4-apprunner-role/... is not authorized to perform: bedrock:InvokeModel`

**Solution:** Policy wasn't attached correctly

1. Go to: IAM → Roles → tara4-apprunner-role
2. Click "Permissions" tab
3. Check if `tara4-bedrock-s3-policy` is listed
4. If not, click "Add permissions" → "Attach policies"
5. Search for `tara4-bedrock-s3-policy` and attach

---

## 📋 Checklist

Before saying "it's still not working":

- [ ] Created policy: `tara4-bedrock-s3-policy`
- [ ] Created role: `tara4-apprunner-role`
- [ ] Attached policy to role
- [ ] Attached role to tara4 service
- [ ] Saw "Update in progress" message
- [ ] Waited 5-10 minutes
- [ ] Status returned to "Running" (green)
- [ ] Verified role appears in Configuration → Security
- [ ] Tested uploading and analyzing document

---

## 🎯 Expected Success

**When it works, you'll see:**

1. ✅ Open https://yymivpdgyd.us-east-1.awsapprunner.com
2. ✅ Upload document - no errors
3. ✅ Click Analyze - loading spinner
4. ✅ **Feedback cards appear** with AI suggestions
5. ✅ Accept/Reject buttons work
6. ✅ Submit All Feedbacks creates document
7. ✅ Download works
8. ✅ S3 export works

**No more 500 errors!**

---

## 📞 If Still Failing

Send me:

1. **Screenshot of:** Configuration → Security section showing Instance role
2. **Logs:** From Logs → Application logs (copy error message)
3. **Tell me:**
   - Did status change to "Update in progress"?
   - How long did you wait?
   - Does Configuration show the role?
   - What error appears when you click Analyze?

---

## 💡 Why This Specifically Failed

Your configuration showed:
- ✅ Correct model ID: `anthropic.claude-3-5-sonnet-20240620-v1:0`
- ✅ Correct region: `us-east-1`
- ✅ All environment variables correct
- ❌ **No Instance role** = No permission to call Bedrock

**That's literally the only thing missing!**

---

## 🔐 What the Role Does

**The IAM role gives App Runner permission to:**

1. **Call Bedrock:** `bedrock:InvokeModel`
   - This is what allows Claude to analyze documents
   - Without this = 500 error

2. **Access S3:** `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`
   - This allows exporting documents to felix-s3-bucket
   - Without this = S3 export fails

**Nothing else is allowed** (secure by default)

---

## 🚀 After This Works

**Your app will:**
- ✅ Analyze documents with Claude 3.5 Sonnet
- ✅ Automatically fall back to other models if needed
- ✅ Export to S3 bucket
- ✅ Generate reviewed documents with comments
- ✅ Cost ~$0.02 per document

**And you can:**
- Access it from anywhere: https://yymivpdgyd.us-east-1.awsapprunner.com
- Scale automatically (App Runner handles it)
- Pay only for usage

---

**Next Action:** Follow Steps 1, 2, 3 above. It will take exactly 10 minutes to fix. Then wait 5-10 minutes for redeployment. Total: ~20 minutes to working app.

---

**Created:** November 17, 2025
**For:** tara4 App Runner service
**Issue:** Missing IAM Instance Role
**Service ARN:** arn:aws:apprunner:us-east-1:758897368787:service/tara4/ae6df5459ea8441b9e7c58f155b3a5ae
