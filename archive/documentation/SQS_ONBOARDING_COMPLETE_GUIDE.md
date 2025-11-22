# Complete SQS Onboarding Guide for Non-Technical Users

**For**: AI-Prism Project
**Date**: November 19, 2025
**Audience**: Non-technical person
**Time**: 15 minutes total

---

## 🎯 What is Amazon SQS? (Simple Explanation)

Think of Amazon SQS like a **post office mailbox** for your application:

```
Your App → Puts "letters" (tasks) in mailbox (SQS Queue)
                           ↓
Workers → Check mailbox → Pick up letters → Do the work
```

**Why we use it**:
- ✅ Tasks don't get lost (like mail is safe in a mailbox)
- ✅ Free up your app to handle more users (don't wait for tasks to finish)
- ✅ 100% free for your usage (AWS gives 1 million requests/month free)
- ✅ No Redis needed (no external services, no permissions needed)

---

## 📚 Part 1: Understanding the Basics

### What is a Queue?

A **queue** is like a line at a coffee shop:
1. Customers (tasks) join the line
2. Wait their turn
3. Barista (worker) serves them one by one
4. Customer leaves after being served

```
Task 1 → Task 2 → Task 3 → Worker picks Task 1 → Processes → Done
         Task 2 → Task 3 → Worker picks Task 2 → Processes → Done
                  Task 3 → Worker picks Task 3 → Processes → Done
```

### Why 3 Different Queues?

Your system has 3 types of work:

1. **aiprism-analysis** - Document analysis (slow, important)
2. **aiprism-chat** - Chat responses (fast, frequent)
3. **aiprism-monitoring** - Health checks (low priority)

**Analogy**: Like having 3 lines at airport:
- Line 1: Check-in (slow but important)
- Line 2: Security (fast but frequent)
- Line 3: Customer service (occasional)

---

## 🚀 Part 2: Setting Up SQS (Step-by-Step)

### Prerequisites

You need:
- ✅ AWS Account (you already have this)
- ✅ AWS CLI installed (check by running `aws --version` in terminal)
- ✅ Terminal/Command Prompt access

---

### Step 1: Open Terminal

**Mac**: Press `Cmd + Space`, type "Terminal", press Enter
**Windows**: Press `Win + R`, type "cmd", press Enter

---

### Step 2: Verify AWS CLI is Working

```bash
aws sts get-caller-identity
```

**Expected output**:
```json
{
    "UserId": "AIDAI...",
    "Account": "758897368787",
    "Arn": "arn:aws:iam::758897368787:user/yourname"
}
```

**If you see error "aws: command not found"**:
```bash
# Install AWS CLI
# Mac:
brew install awscli

# Windows: Download from
https://awscli.amazonaws.com/AWSCLIV2.msi
```

---

### Step 3: Create Your First SQS Queue

Copy and paste this command (press Enter after each):

```bash
aws sqs create-queue \
    --queue-name aiprism-analysis \
    --region us-east-1
```

**What this does**:
- Creates a mailbox named "aiprism-analysis"
- In AWS region us-east-1 (Virginia)

**Expected output**:
```json
{
    "QueueUrl": "https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-analysis"
}
```

**✅ Success!** You created your first queue!

---

### Step 4: Create the Other 2 Queues

```bash
aws sqs create-queue \
    --queue-name aiprism-chat \
    --region us-east-1
```

```bash
aws sqs create-queue \
    --queue-name aiprism-monitoring \
    --region us-east-1
```

**Expected**: You'll get URLs for each queue.

---

### Step 5: Verify All 3 Queues Exist

```bash
aws sqs list-queues --region us-east-1
```

**Expected output**:
```json
{
    "QueueUrls": [
        "https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-analysis",
        "https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-chat",
        "https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-monitoring"
    ]
}
```

**✅ All 3 queues created!**

---

### Step 6: Configure Queue Settings (Optional but Recommended)

This makes your queues work better:

```bash
# For analysis queue (longer timeout for big tasks)
aws sqs set-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-analysis \
    --attributes '{
        "VisibilityTimeout": "3600",
        "MessageRetentionPeriod": "86400",
        "ReceiveMessageWaitTimeSeconds": "1"
    }' \
    --region us-east-1
```

**What these settings mean**:
- **VisibilityTimeout: 3600** = Task is hidden for 1 hour while being processed (prevents duplicates)
- **MessageRetentionPeriod: 86400** = Keep task in queue for 24 hours if not processed
- **ReceiveMessageWaitTimeSeconds: 1** = Check for new tasks every 1 second

Repeat for other queues:

```bash
# For chat queue (shorter timeout, faster responses)
aws sqs set-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-chat \
    --attributes '{
        "VisibilityTimeout": "300",
        "MessageRetentionPeriod": "86400",
        "ReceiveMessageWaitTimeSeconds": "1"
    }' \
    --region us-east-1

# For monitoring queue
aws sqs set-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-monitoring \
    --attributes '{
        "VisibilityTimeout": "300",
        "MessageRetentionPeriod": "86400",
        "ReceiveMessageWaitTimeSeconds": "1"
    }' \
    --region us-east-1
```

---

## 🔗 Part 3: Connecting SQS to Your Application

### What Your App Needs to Know

Your app needs to know 3 things:
1. Where are the queues? (AWS region: us-east-1)
2. What are they called? (aiprism-analysis, aiprism-chat, aiprism-monitoring)
3. Who can access them? (Your AWS credentials)

**Good news**: Your app already has AWS credentials! (You're using S3 already)

---

### How the Connection Works

```
Your Code (celery_config.py)
         ↓
  Reads environment variables:
  - AWS_REGION=us-east-1
  - S3_BUCKET_NAME=felix-s3-bucket
  - SQS_QUEUE_PREFIX=aiprism-
         ↓
  Uses boto3 (AWS Python library)
         ↓
  Connects to SQS
         ↓
  Creates/finds queues automatically!
```

**You don't need to manually connect anything!**

The code in `celery_config.py` (which I already updated) handles everything automatically.

---

### How Tasks Flow Through SQS

```
Step 1: User uploads document
         ↓
Step 2: Flask app receives request
         ↓
Step 3: Flask creates a task:
        {
          "section": "Executive Summary",
          "content": "...",
          "task_id": "abc-123"
        }
         ↓
Step 4: Celery sends task to SQS queue
         ↓
Step 5: SQS stores task (like putting letter in mailbox)
         ↓
Step 6: Flask returns to user immediately:
        "Task submitted! ID: abc-123"
         ↓
Step 7: In background, Celery worker checks SQS
         ↓
Step 8: Worker finds task in queue
         ↓
Step 9: Worker processes task (calls AI)
         ↓
Step 10: Worker stores result in S3
         ↓
Step 11: Worker deletes task from SQS (job done!)
         ↓
Step 12: User polls /task_status/abc-123
         ↓
Step 13: Flask reads result from S3
         ↓
Step 14: User gets result!
```

**Total time**: 2-5 seconds, but user doesn't wait!

---

## 🧪 Part 4: Testing Your SQS Setup

### Test 1: Check if Queues Exist

```bash
aws sqs list-queues --region us-east-1 | grep aiprism
```

**Expected**: You should see your 3 queue URLs

---

### Test 2: Send a Test Message

```bash
aws sqs send-message \
    --queue-url https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-analysis \
    --message-body "Test message from terminal" \
    --region us-east-1
```

**Expected output**:
```json
{
    "MessageId": "12345-abcde-67890",
    "MD5OfMessageBody": "..."
}
```

**✅ Message sent to queue!**

---

### Test 3: Read the Message Back

```bash
aws sqs receive-message \
    --queue-url https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-analysis \
    --region us-east-1
```

**Expected output**:
```json
{
    "Messages": [
        {
            "MessageId": "12345-abcde-67890",
            "Body": "Test message from terminal",
            "ReceiptHandle": "..."
        }
    ]
}
```

**✅ Message received!**

---

### Test 4: Delete the Test Message

```bash
aws sqs delete-message \
    --queue-url https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-analysis \
    --receipt-handle "PASTE_RECEIPT_HANDLE_HERE" \
    --region us-east-1
```

(Replace `PASTE_RECEIPT_HANDLE_HERE` with the ReceiptHandle from previous step)

**✅ Message deleted!**

---

## 📊 Part 5: Monitoring Your Queues

### Check Queue Status

```bash
aws sqs get-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-analysis \
    --attribute-names All \
    --region us-east-1
```

**Important metrics to watch**:
- **ApproximateNumberOfMessages**: How many tasks are waiting
- **ApproximateNumberOfMessagesNotVisible**: How many tasks are being processed
- **ApproximateNumberOfMessagesDelayed**: How many tasks are scheduled for later

**Healthy system**:
- ApproximateNumberOfMessages: 0-5 (low queue backlog)
- ApproximateNumberOfMessagesNotVisible: 1-3 (workers are active)

**Unhealthy system**:
- ApproximateNumberOfMessages: 50+ (queue is backing up!)
- ApproximateNumberOfMessagesNotVisible: 0 (no workers running!)

---

### View Queue in AWS Console (Visual Way)

1. Go to: https://console.aws.amazon.com/sqs/
2. Make sure region is "US East (N. Virginia)" (top right)
3. You'll see your 3 queues listed
4. Click on a queue name to see details:
   - **Messages Available**: Waiting to be processed
   - **Messages in Flight**: Currently being processed
   - **Age of Oldest Message**: How long oldest task has been waiting

**Screenshot Guide**:
```
┌─────────────────────────────────────────┐
│ SQS > Queues                            │
├─────────────────────────────────────────┤
│                                         │
│ Queue Name             Messages  Status │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ aiprism-analysis           3      ✓     │
│ aiprism-chat               0      ✓     │
│ aiprism-monitoring         0      ✓     │
│                                         │
└─────────────────────────────────────────┘
```

---

## 💰 Part 6: Understanding Costs

### SQS Pricing (Very Simple)

**Free Tier** (First 12 months):
- 1 million requests per month = **$0**

**After Free Tier**:
- First 1 million requests = **$0.40** ($0.40 per million)
- Your usage: ~60,000 requests/month = **$0.024/month** (2.4 cents!)

### Your Actual Cost Breakdown

**Monthly with 10 users, 20 requests/day each**:

```
Tasks per month:
- 10 users × 20 requests/day × 30 days = 6,000 tasks

SQS requests:
- Send message: 6,000 requests
- Receive message: 6,000 requests (workers polling)
- Delete message: 6,000 requests
- Total: 18,000 requests/month

Cost:
- Within FREE tier (1 million >> 18,000) = $0/month ✅
```

**Even with 100 users**:
- 180,000 requests/month
- Still FREE ✅

**You'd need 5,500 users to exceed free tier!**

---

### Cost Comparison

| Service | Your Usage | Cost |
|---------|------------|------|
| **Redis (ElastiCache)** | N/A | $15-50/month ❌ |
| **Upstash Redis** | 60K requests/month | $0-10/month ⚠️ |
| **Amazon SQS** | 18K requests/month | $0/month ✅ |
| **Amazon S3** | 100MB storage, 60K requests | $0/month ✅ |

**Total savings**: $15-50/month by using SQS!

---

## 🔧 Part 7: Troubleshooting Common Issues

### Issue 1: "Queue does not exist"

**Error**:
```
An error occurred (AWS.SimpleQueueService.NonExistentQueue)
```

**Solution**:
```bash
# List all queues to verify name
aws sqs list-queues --region us-east-1

# Check if region is correct (must be us-east-1)
# Check if queue name is spelled correctly
```

---

### Issue 2: "Access Denied"

**Error**:
```
An error occurred (AccessDeniedException)
```

**Solution**:
```bash
# Verify AWS credentials are configured
aws sts get-caller-identity

# Check IAM permissions (you need sqs:* permissions)
# Ask your AWS admin to add SQS permissions to your IAM user
```

**IAM Policy needed**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sqs:*",
            "Resource": "*"
        }
    ]
}
```

---

### Issue 3: "Messages not being processed"

**Symptoms**: Queue depth keeps growing, no results

**Diagnosis**:
```bash
# Check if workers are running
aws sqs get-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-analysis \
    --attribute-names ApproximateNumberOfMessages,ApproximateNumberOfMessagesNotVisible \
    --region us-east-1
```

**Solution**:
- If `ApproximateNumberOfMessages` is high AND `ApproximateNumberOfMessagesNotVisible` is 0:
  - **Workers are not running!**
  - Check App Runner logs
  - Verify Celery is configured correctly

---

### Issue 4: "Duplicate processing"

**Symptoms**: Same task processed multiple times

**Cause**: Visibility timeout too short

**Solution**:
```bash
# Increase visibility timeout
aws sqs set-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-analysis \
    --attributes '{"VisibilityTimeout": "3600"}' \
    --region us-east-1
```

---

### Issue 5: "Messages disappearing"

**Symptoms**: Tasks submitted but never appear in queue

**Diagnosis**:
```bash
# Check dead letter queue (if configured)
aws sqs receive-message \
    --queue-url https://sqs.us-east-1.amazonaws.com/758897368787/aiprism-analysis-dlq \
    --region us-east-1
```

**Solution**:
- Check App Runner logs for errors
- Verify message is JSON-serializable
- Check queue permissions

---

## 📱 Part 8: Viewing Queues in AWS Console (Step-by-Step with Pictures)

### Step 1: Go to SQS Console

1. Open browser
2. Go to: https://console.aws.amazon.com/sqs/
3. Log in with your AWS credentials

---

### Step 2: Select Correct Region

**Top right corner**, verify region says:
```
📍 US East (N. Virginia)
```

If not, click dropdown and select **US East (N. Virginia)**

---

### Step 3: View Your Queues

You'll see a table:

```
┌──────────────────────────────────────────────────────────┐
│ Queues (3)                                    [ Create ] │
├──────────────────────────────────────────────────────────┤
│ Name ▼                    Type    Messages  In Flight    │
│ ────────────────────────────────────────────────────     │
│ □ aiprism-analysis        Standard    3         1        │
│ □ aiprism-chat            Standard    0         0        │
│ □ aiprism-monitoring      Standard    0         0        │
└──────────────────────────────────────────────────────────┘
```

**What the columns mean**:
- **Messages**: Tasks waiting to be processed
- **In Flight**: Tasks currently being processed
- **Type**: Standard (normal queue) vs FIFO (ordered queue)

---

### Step 4: View Queue Details

Click on **aiprism-analysis** (the queue name)

You'll see:

```
┌─────────────────────────────────────────────┐
│ aiprism-analysis                    Actions │
├─────────────────────────────────────────────┤
│                                             │
│ Details                                     │
│ ───────                                     │
│ URL: https://sqs.us-east-1.amazonaws.com... │
│ ARN: arn:aws:sqs:us-east-1:758897368787... │
│                                             │
│ Configuration                               │
│ ─────────────                               │
│ Visibility timeout: 1 hour                  │
│ Message retention: 1 day                    │
│ Maximum message size: 256 KB                │
│ Receive message wait time: 1 second         │
│                                             │
│ Monitoring                                  │
│ ──────────                                  │
│ Messages Available: 3                       │
│ Messages in Flight: 1                       │
│ Oldest Message: 2 minutes                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

### Step 5: View Messages (Optional)

**IMPORTANT**: Only do this for debugging, not in production!

1. Click **Send and receive messages** button (top right)
2. Click **Poll for messages**
3. You'll see list of messages in the queue
4. Click on a message to view its content

**Don't delete messages manually** - let your workers do it!

---

### Step 6: View Queue Metrics (Graphs)

Scroll down to see graphs:

```
Messages Available ─────────────────────
     5 │             ╱╲
       │            ╱  ╲
     3 │           ╱    ╲___
       │     ╱────╱
     1 │  ╱──╱
     0 └──────────────────────────
       10:00  11:00  12:00  13:00

Messages In Flight ─────────────────────
     3 │           ╱──╲
       │          ╱    ╲
     2 │         ╱      ╲___
       │    ╱───╱           ╲
     1 │  ╱─────             ╲___
     0 └──────────────────────────
       10:00  11:00  12:00  13:00
```

**Healthy pattern**:
- Messages Available: Low and stable (0-5)
- Messages In Flight: Active but not stuck (1-3)

**Unhealthy pattern**:
- Messages Available: Growing rapidly (queue backup!)
- Messages In Flight: Stuck at same number (workers frozen!)

---

## ✅ Part 9: Integration Checklist

Use this checklist to verify your SQS is fully integrated:

### Pre-Deployment Checklist

- [ ] 3 SQS queues created (analysis, chat, monitoring)
- [ ] Queue attributes configured (visibility timeout, retention)
- [ ] IAM permissions verified (sqs:* access)
- [ ] AWS CLI configured and working
- [ ] Test message sent and received successfully

### Code Integration Checklist

- [ ] `celery_config.py` updated to use SQS
- [ ] `requirements.txt` includes `celery[sqs]==5.3.4`
- [ ] `pycurl` added to requirements (SQS dependency)
- [ ] No Redis URLs in environment variables
- [ ] `SQS_QUEUE_PREFIX=aiprism-` set in environment
- [ ] Code pushed to GitHub repository

### Deployment Checklist

- [ ] App Runner environment variables updated
- [ ] App Runner successfully redeployed
- [ ] Health endpoint returns `"broker": "sqs"`
- [ ] Health endpoint returns `"backend": "s3"`
- [ ] Test analysis task completes successfully
- [ ] Task results stored in S3
- [ ] No errors in App Runner logs

### Monitoring Checklist

- [ ] CloudWatch logs showing SQS activity
- [ ] Queue depth stays low (< 10 messages)
- [ ] Tasks being processed within 5-10 seconds
- [ ] No "Queue does not exist" errors
- [ ] No "Access Denied" errors

---

## 📖 Part 10: Glossary (Terms Explained)

### Technical Terms

**SQS (Simple Queue Service)**: Amazon's message queue service. Think of it as a reliable mailbox for tasks.

**Queue**: A line where tasks wait to be processed, like customers waiting at a store.

**Message**: A single task in the queue, containing information about what needs to be done.

**Broker**: The system that manages the queue (SQS in our case).

**Backend**: Where results are stored after tasks are completed (S3 in our case).

**Worker**: A program that checks the queue, picks up tasks, and processes them.

**Visibility Timeout**: How long a message is hidden from other workers after one worker picks it up.

**Dead Letter Queue (DLQ)**: A special queue for messages that failed processing multiple times.

**Polling**: Checking the queue for new messages (like checking your mailbox).

**Receipt Handle**: A unique ID given when you receive a message, used to delete it later.

**Message Retention**: How long a message stays in the queue before being automatically deleted.

### Common Acronyms

- **AWS**: Amazon Web Services
- **IAM**: Identity and Access Management (permissions)
- **ARN**: Amazon Resource Name (unique ID for AWS resources)
- **TTL**: Time To Live (how long something exists)
- **API**: Application Programming Interface (how programs talk to each other)

---

## 🎓 Part 11: Learning Resources

### AWS Official Documentation

- **SQS Getting Started**: https://docs.aws.amazon.com/sqs/
- **SQS Developer Guide**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/
- **AWS Free Tier**: https://aws.amazon.com/free/

### Video Tutorials

- AWS SQS in 5 minutes: https://www.youtube.com/results?search_query=aws+sqs+tutorial
- Understanding Message Queues: https://www.youtube.com/results?search_query=message+queue+explained

### Interactive Learning

- AWS SQS Workshop: https://aws.amazon.com/getting-started/hands-on/
- AWS Skill Builder (Free courses): https://skillbuilder.aws/

---

## 📞 Part 12: Getting Help

### If Something Goes Wrong

1. **Check this guide first** - Most issues are covered in Troubleshooting (Part 7)
2. **Check AWS console** - View queue details and messages
3. **Check App Runner logs** - See errors in real-time
4. **Ask in team chat** - Share error messages and queue URLs

### Useful Commands for Support

When asking for help, provide these:

```bash
# 1. Check queue status
aws sqs get-queue-attributes \
    --queue-url YOUR_QUEUE_URL \
    --attribute-names All \
    --region us-east-1

# 2. Check recent messages (first 5)
aws sqs receive-message \
    --queue-url YOUR_QUEUE_URL \
    --max-number-of-messages 5 \
    --region us-east-1

# 3. Check App Runner logs
aws logs tail /aws/apprunner/tara4 --follow
```

---

## 🎉 Congratulations!

You've successfully:
- ✅ Learned what SQS is and why we use it
- ✅ Created 3 SQS queues
- ✅ Configured queue settings
- ✅ Tested your setup
- ✅ Learned how to monitor queues
- ✅ Saved $15-50/month by not using Redis!

**Your system is now running on 100% AWS-native services with zero external dependencies!**

---

**Guide Version**: 1.0
**Last Updated**: November 19, 2025
**Status**: Complete ✅
**Difficulty**: Beginner-Friendly
**Time to Complete**: 15 minutes
