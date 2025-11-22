# Redis Setup Guide - Get Your Redis URL

## 🎯 Quick Answer: You Have 3 Options

### Option 1: ⚡ Use MemoryStore (No Redis - Fastest Setup)
**Best for**: Testing, <10 users, quick deployment
**Cost**: $0 (included in App Runner)
**Setup Time**: 2 minutes

### Option 2: 🐳 Use Upstash Redis (Managed, Easy)
**Best for**: Production, 10-100 users, no AWS setup needed
**Cost**: Free tier (10K commands/day) or $10-20/month
**Setup Time**: 5 minutes

### Option 3: ☁️ Use AWS ElastiCache (Full Control)
**Best for**: Production, 100+ users, full AWS integration
**Cost**: $15-50/month
**Setup Time**: 15-20 minutes

---

## Option 1: ⚡ Use MemoryStore (No Redis Required)

### What is MemoryStore?
A built-in fallback that stores task results in memory. **No Redis setup needed!**

### Pros:
- ✅ Zero setup
- ✅ Works immediately
- ✅ No additional cost
- ✅ Good for testing and development

### Cons:
- ⚠️ Results lost if app restarts
- ⚠️ Limited to single App Runner instance
- ⚠️ Not recommended for production with >10 users

### How to Use:

**Environment Variables**:
```bash
# Comment out or don't set Redis variables
# REDIS_URL=...          # Don't set
# CELERY_BROKER_URL=...  # Don't set
# CELERY_RESULT_BACKEND=... # Don't set

# Enable in-memory mode
USE_CELERY=false         # Set to false
ENABLE_ENHANCED_MODE=true  # Keep true
```

**Your app will automatically use in-memory storage.**

### Verification:
```bash
curl https://yymivpdgyd.us-east-1.awsapprunner.com/health

# Expected output:
# {
#   "status": "healthy",
#   "celery": "in-memory mode",
#   "redis": "not configured",
#   "enhanced_mode": true
# }
```

---

## Option 2: 🐳 Use Upstash Redis (Recommended for Easy Setup)

### What is Upstash?
Serverless Redis with a generous free tier and no infrastructure management.

### Pros:
- ✅ Free tier (10K commands/day = ~500 requests/day)
- ✅ 5-minute setup
- ✅ No AWS configuration needed
- ✅ Works perfectly with App Runner
- ✅ Pay-as-you-go pricing

### Step-by-Step Setup:

#### Step 1: Create Upstash Account

1. Go to: https://upstash.com/
2. Click "Sign Up" (use GitHub/Google login)
3. Verify email

#### Step 2: Create Redis Database

1. Click "Create Database"
2. Choose:
   - **Name**: `aiprism-redis`
   - **Type**: Regional
   - **Region**: `us-east-1` (same as App Runner)
   - **TLS**: Enabled
   - **Eviction**: No eviction
3. Click "Create"

#### Step 3: Get Redis URL

1. After creation, you'll see database details
2. Look for **"UPSTASH_REDIS_REST_URL"** or **"Redis URL"**
3. Copy the URL that looks like:
   ```
   redis://default:AbCd1234EfGh5678IjKl@us1-moving-fox-12345.upstash.io:6379
   ```

#### Step 4: Add to App Runner

Go to App Runner → tara4 → Configuration → Environment Variables:

```bash
REDIS_URL=redis://default:AbCd1234EfGh5678IjKl@us1-moving-fox-12345.upstash.io:6379
CELERY_BROKER_URL=redis://default:AbCd1234EfGh5678IjKl@us1-moving-fox-12345.upstash.io:6379
CELERY_RESULT_BACKEND=redis://default:AbCd1234EfGh5678IjKl@us1-moving-fox-12345.upstash.io:6379
USE_CELERY=true
```

#### Step 5: Verify Connection

```bash
# Test Redis connection
curl https://yymivpdgyd.us-east-1.awsapprunner.com/health

# Expected output:
# {
#   "status": "healthy",
#   "celery": "connected",
#   "redis": "connected",
#   "redis_provider": "upstash",
#   "enhanced_mode": true
# }
```

### Pricing (Upstash):
- **Free Tier**: 10K commands/day (enough for ~500 requests)
- **Pay-as-you-go**: $0.20 per 100K commands
- **Pro Plan**: $10/month (1M commands/day)

**Recommended**: Start with free tier, upgrade if needed.

---

## Option 3: ☁️ Use AWS ElastiCache (Full Production Setup)

### What is ElastiCache?
AWS's managed Redis service with high availability and automatic backups.

### Pros:
- ✅ Fully integrated with AWS
- ✅ High availability (Multi-AZ)
- ✅ Automatic backups
- ✅ Best for 100+ users

### Cons:
- ⚠️ More complex setup
- ⚠️ Costs $15-50/month
- ⚠️ Requires VPC configuration

### Step-by-Step Setup:

#### Step 1: Get Your AWS Account ID and VPC

```bash
# Get AWS Account ID
aws sts get-caller-identity --query Account --output text
# Output: 758897368787

# Get Default VPC ID
aws ec2 describe-vpcs \
  --filters "Name=isDefault,Values=true" \
  --query 'Vpcs[0].VpcId' \
  --output text
# Output: vpc-abc123def456

# Get Subnet IDs in your VPC
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=vpc-abc123def456" \
  --query 'Subnets[*].[SubnetId,AvailabilityZone]' \
  --output table
# Pick 2 subnets in different availability zones
```

#### Step 2: Create Cache Subnet Group

```bash
# Create subnet group (use your subnet IDs)
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name aiprism-redis-subnet \
  --cache-subnet-group-description "Subnet group for AI-Prism Redis" \
  --subnet-ids subnet-abc123 subnet-def456
```

#### Step 3: Create Security Group

```bash
# Get your VPC ID
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)

# Create security group
aws ec2 create-security-group \
  --group-name aiprism-redis-sg \
  --description "Security group for AI-Prism Redis" \
  --vpc-id $VPC_ID

# Get security group ID (save this)
SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=aiprism-redis-sg" \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

echo "Security Group ID: $SG_ID"

# Allow Redis traffic from anywhere in VPC (port 6379)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 6379 \
  --cidr 0.0.0.0/0
```

#### Step 4: Create Redis Cluster

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id aiprism-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.1 \
  --num-cache-nodes 1 \
  --cache-subnet-group-name aiprism-redis-subnet \
  --security-group-ids $SG_ID \
  --tags "Key=Name,Value=aiprism-redis" "Key=Environment,Value=production"

echo "⏳ Creating Redis cluster... (takes 5-10 minutes)"
```

#### Step 5: Wait for Cluster to be Available

```bash
# Check cluster status
aws elasticache describe-cache-clusters \
  --cache-cluster-id aiprism-redis \
  --query 'CacheClusters[0].CacheClusterStatus' \
  --output text

# Keep running until output shows: available
```

#### Step 6: Get Redis Endpoint

```bash
# Get Redis endpoint URL
aws elasticache describe-cache-clusters \
  --cache-cluster-id aiprism-redis \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
  --output text

# Output example: aiprism-redis.abc123.0001.use1.cache.amazonaws.com
```

#### Step 7: Construct Redis URL

Format: `redis://[endpoint]:6379/0`

Example:
```
redis://aiprism-redis.abc123.0001.use1.cache.amazonaws.com:6379/0
```

#### Step 8: Add to App Runner

```bash
REDIS_URL=redis://aiprism-redis.abc123.0001.use1.cache.amazonaws.com:6379/0
CELERY_BROKER_URL=redis://aiprism-redis.abc123.0001.use1.cache.amazonaws.com:6379/0
CELERY_RESULT_BACKEND=redis://aiprism-redis.abc123.0001.use1.cache.amazonaws.com:6379/0
USE_CELERY=true
```

#### Step 9: Configure App Runner VPC Access

⚠️ **IMPORTANT**: App Runner needs VPC access to reach ElastiCache.

1. Go to AWS Console → App Runner → tara4
2. Click "Configuration" → "Networking"
3. Click "Edit"
4. Enable "Custom VPC"
5. Select:
   - **VPC**: Your VPC ID (vpc-abc123def456)
   - **Subnets**: Same subnets used for Redis
   - **Security Groups**: Same security group ($SG_ID)
6. Save changes

#### Step 10: Verify Connection

```bash
curl https://yymivpdgyd.us-east-1.awsapprunner.com/health

# Expected output:
# {
#   "status": "healthy",
#   "celery": "connected",
#   "redis": "connected",
#   "redis_provider": "elasticache",
#   "enhanced_mode": true
# }
```

### Pricing (ElastiCache):
- **cache.t3.micro**: $15/month (0.5GB memory)
- **cache.t3.small**: $30/month (1.5GB memory)
- **cache.t3.medium**: $60/month (3GB memory)

**Recommended**: Start with t3.micro, upgrade if needed.

---

## 📊 Comparison: Which Option Should You Choose?

| Feature | MemoryStore | Upstash Redis | AWS ElastiCache |
|---------|-------------|---------------|-----------------|
| **Setup Time** | 2 min | 5 min | 20 min |
| **Cost** | Free | Free-$10/mo | $15-50/mo |
| **Reliability** | Low | High | Very High |
| **Best For** | Testing | Production (<100 users) | Production (100+ users) |
| **Data Persistence** | ❌ No | ✅ Yes | ✅ Yes |
| **Multi-Instance** | ❌ No | ✅ Yes | ✅ Yes |
| **Auto-Scaling** | ❌ No | ✅ Yes | ⚠️ Manual |
| **Backups** | ❌ No | ✅ Yes | ✅ Yes |
| **AWS Integration** | N/A | ⚠️ External | ✅ Native |

### My Recommendation:

**For Your Use Case (10+ simultaneous users)**:

✅ **Use Upstash Redis** (Option 2)

**Why?**
- ✅ Perfect for 10-50 users
- ✅ 5-minute setup (no AWS complexity)
- ✅ Free tier covers testing
- ✅ $10/month for production
- ✅ Reliable and persistent
- ✅ No VPC configuration needed

**When to Switch to ElastiCache:**
- When you have 100+ simultaneous users
- When you need strict AWS compliance
- When you need multi-AZ redundancy

---

## 🚀 Quick Start: Setup Upstash in 5 Minutes

### Step 1: Create Account
Go to: https://upstash.com/ → Sign Up

### Step 2: Create Database
Dashboard → Create Database → Name: `aiprism-redis` → Region: `us-east-1` → Create

### Step 3: Copy Redis URL
Click on database → Copy the URL that starts with `redis://`

Example:
```
redis://default:AYZxMjAy...Njg3ODc@us1-fast-crow-31234.upstash.io:6379
```

### Step 4: Add to App Runner
Go to: AWS Console → App Runner → tara4 → Configuration → Edit

Add these 3 variables:
```
REDIS_URL=redis://default:AYZxMjAy...Njg3ODc@us1-fast-crow-31234.upstash.io:6379
CELERY_BROKER_URL=redis://default:AYZxMjAy...Njg3ODc@us1-fast-crow-31234.upstash.io:6379
CELERY_RESULT_BACKEND=redis://default:AYZxMjAy...Njg3ODc@us1-fast-crow-31234.upstash.io:6379
```

### Step 5: Save & Deploy
Click "Save changes" → Wait 5-10 minutes → Done! 🎉

### Step 6: Verify
```bash
curl https://yymivpdgyd.us-east-1.awsapprunner.com/health
```

Look for: `"redis": "connected"` ✅

---

## 🆘 Troubleshooting

### Issue 1: "Can't connect to Redis"

**Solution**:
1. Check Redis URL is correct (no extra spaces)
2. Verify Redis is running (check Upstash dashboard)
3. Check App Runner logs: `aws logs tail /aws/apprunner/tara4 --follow`

### Issue 2: "Connection timeout"

**For Upstash**: Check if TLS is enabled, use `rediss://` instead of `redis://`

**For ElastiCache**: Verify VPC configuration and security groups

### Issue 3: "Authentication failed"

**For Upstash**: Copy the full URL including password
**For ElastiCache**: ElastiCache doesn't require password by default

---

## ✅ Final Recommendation

**For 10+ simultaneous users, use Upstash Redis:**

1. Sign up at https://upstash.com/
2. Create Redis database in `us-east-1`
3. Copy Redis URL
4. Add to App Runner as `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
5. Set `USE_CELERY=true`
6. Deploy and test

**Total time**: 5 minutes
**Total cost**: Free (or $10/month for production)
**Result**: Reliable async processing for 10-50+ users 🚀

---

**Guide Version**: 1.0
**Last Updated**: November 19, 2025
**Status**: Production Ready ✅
