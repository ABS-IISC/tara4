# Quick Start Deployment Guide
## AI-Prism Flask Application - Choose Your Path

**Version:** 1.0
**Date:** November 25, 2025

---

## Which Service Should You Choose?

### 🎯 Quick Decision Tree

```
Do you need auto-scaling?
├─ NO → AWS Lightsail ($40/month) ✅
│
├─ YES → What's your budget?
   ├─ <$100/month → Start with Lightsail, migrate later
   ├─ $150-200/month → AWS Elastic Beanstalk ⭐
   └─ $150+/month → AWS Fargate
```

---

## Path 1: AWS Lightsail (Simplest - 30 Minutes)

### Perfect For
- MVP and prototypes
- Budget: $40-80/month
- Traffic: <10K requests/day
- Team: 1-2 developers

### Quick Start
```bash
# 1. Build Docker image
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2
docker build -f Dockerfile.lightsail -t aiprism:latest .

# 2. Push to ECR
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr create-repository --repository-name aiprism --region us-east-1
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag aiprism:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:latest

# 3. Create Lightsail service
aws lightsail create-container-service \
  --service-name aiprism \
  --power small \
  --scale 1 \
  --region us-east-1

# 4. Deploy (use deployment JSON from guide)
aws lightsail create-container-service-deployment \
  --service-name aiprism \
  --cli-input-json file://lightsail-deployment.json

# 5. Get URL
aws lightsail get-container-services \
  --service-name aiprism \
  --query 'containerServices[0].url' \
  --output text
```

**Full Guide:** [DEPLOYMENT_GUIDE_LIGHTSAIL.md](DEPLOYMENT_GUIDE_LIGHTSAIL.md)

---

## Path 2: AWS Elastic Beanstalk (Recommended - 45 Minutes)

### Perfect For
- Production deployments
- Budget: $150-200/month
- Traffic: 10K-100K requests/day
- Team: 2-5 developers
- Need: Auto-scaling, zero-downtime deployments

### Quick Start
```bash
# 1. Install EB CLI
pip install awsebcli --upgrade

# 2. Initialize Beanstalk
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2
eb init aiprism --platform docker --region us-east-1

# 3. Create environment
eb create aiprism-production \
  --instance-type t3.medium \
  --scale 2 \
  --envvars \
    AWS_REGION=us-east-1,\
    BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0,\
    BEDROCK_MAX_TOKENS=4096,\
    FLASK_ENV=production

# 4. Monitor deployment (10-15 minutes)
eb status
eb health

# 5. Get URL
eb open
```

**Full Guide:** [DEPLOYMENT_GUIDE_BEANSTALK.md](DEPLOYMENT_GUIDE_BEANSTALK.md)

---

## Path 3: AWS Fargate (Advanced - 4-6 Hours)

### Perfect For
- Production with variable traffic
- Budget: $155+/month
- Need: Serverless containers, 99.99% SLA
- Team: 3+ developers with AWS experience

### Quick Start
See [AWS_DEPLOYMENT_COMPREHENSIVE_EVALUATION.md](AWS_DEPLOYMENT_COMPREHENSIVE_EVALUATION.md) for complete Fargate setup.

---

## Files Created for You

### Elastic Beanstalk Configuration
```
.ebextensions/
├── 01_environment.config    # Environment & scaling config
└── 02_packages.config        # System packages & cron jobs

gunicorn.conf.py              # Gunicorn production config
Procfile                      # EB process definition
.ebignore                     # Files to exclude from deployment
```

### Lightsail Configuration
```
Dockerfile.lightsail          # Optimized Dockerfile for Lightsail
.dockerignore                 # Files to exclude from image
lightsail-deployment.json     # Container deployment config (create from guide)
```

---

## Pre-Deployment Checklist

### ✅ Before You Start

1. **AWS Account Setup**
   ```bash
   # Configure AWS CLI
   aws configure

   # Verify credentials
   aws sts get-caller-identity
   ```

2. **IAM Permissions**
   - ElasticBeanstalk (for Beanstalk)
   - Lightsail (for Lightsail)
   - ECR (both)
   - Bedrock (both)
   - S3 (both)

3. **Test Locally**
   ```bash
   # Test Flask app
   cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2
   python app.py
   # Visit: http://localhost:8000/health

   # Test Docker image (Lightsail)
   docker build -f Dockerfile.lightsail -t aiprism:latest .
   docker run -p 8000:8000 aiprism:latest
   # Visit: http://localhost:8000/health
   ```

4. **Environment Variables**
   Ensure these are set in your deployment:
   - `AWS_REGION=us-east-1`
   - `BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0`
   - `BEDROCK_MAX_TOKENS=4096`
   - `FLASK_ENV=production`

---

## Post-Deployment Checklist

### ✅ After Deployment

1. **Test Application**
   ```bash
   # Test health endpoint
   curl https://your-url/health

   # Test main page
   curl https://your-url/
   ```

2. **Setup Monitoring**
   - Configure CloudWatch alarms
   - Setup SNS notifications
   - Review logs regularly

3. **Configure Domain (Optional)**
   - Purchase domain (Route 53 or external)
   - Setup SSL certificate
   - Update DNS records

4. **Enable Cost Alerts**
   ```bash
   # Create budget alert
   aws budgets create-budget \
     --account-id ACCOUNT_ID \
     --budget file://budget-config.json
   ```

---

## Cost Comparison

### Monthly Costs (24/7 Operation)

| Service | Minimal | Recommended | High Availability |
|---------|---------|-------------|-------------------|
| **Lightsail** | $40 (1 node) | $40 (1 node) | $80 (2 nodes) |
| **Beanstalk** | $80 (1 instance) | $150 (2 instances) | $180 (3+ instances) |
| **Fargate** | $77 (1 task) | $155 (2 tasks) | $230 (3+ tasks) |

### Cost Optimization Tips

**Lightsail:**
- Start with Small ($40/month)
- Scale to 2-3 nodes only if needed
- No auto-scaling = predictable costs

**Beanstalk:**
- Use scheduled scaling (save 50% off-hours)
- Purchase Reserved Instances after 3 months
- Enable managed updates

**Both:**
- Enable S3 lifecycle policies
- Monitor CloudWatch metrics
- Right-size resources monthly

---

## Common Issues & Solutions

### Issue: Deployment Fails

**Lightsail:**
```bash
# Check logs
aws lightsail get-container-log \
  --service-name aiprism \
  --container-name aiprism-app

# Verify image is accessible
aws ecr describe-images \
  --repository-name aiprism \
  --image-ids imageTag=latest
```

**Beanstalk:**
```bash
# Check events
eb events

# View logs
eb logs --all

# Check health
eb health
```

### Issue: Health Check Fails

**Solution:**
1. Verify `/health` endpoint works locally
2. Check container logs for startup errors
3. Increase health check timeout
4. Verify environment variables are set

### Issue: Can't Access Application

**Solution:**
1. Check security group rules
2. Verify load balancer health
3. Check service status
4. Review application logs

---

## Daily Operations

### Deploy New Version

**Lightsail:**
```bash
# Build and push
docker build -f Dockerfile.lightsail -t aiprism:latest .
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aiprism:latest

# Deploy
aws lightsail create-container-service-deployment \
  --service-name aiprism \
  --cli-input-json file://lightsail-deployment.json
```

**Beanstalk:**
```bash
# Commit changes
git add .
git commit -m "New feature"

# Deploy
eb deploy

# Monitor
eb events --follow
```

### View Logs

**Lightsail:**
```bash
aws lightsail get-container-log \
  --service-name aiprism \
  --container-name aiprism-app
```

**Beanstalk:**
```bash
eb logs --stream
# Or download all
eb logs --all
```

### Check Status

**Lightsail:**
```bash
aws lightsail get-container-services --service-name aiprism
```

**Beanstalk:**
```bash
eb status
eb health
```

---

## Migration Paths

### From Lightsail to Beanstalk

**When:** Traffic exceeds 10K req/day or need auto-scaling

**Steps:**
1. Setup Beanstalk environment (Path 2 above)
2. Deploy to Beanstalk
3. Test thoroughly
4. Update DNS to point to Beanstalk
5. Monitor for 24 hours
6. Decommission Lightsail

### From Beanstalk to Fargate

**When:** Need full container orchestration or microservices

**Steps:**
1. Create ECS cluster
2. Define task definitions
3. Setup ALB
4. Deploy to Fargate
5. Update DNS
6. Terminate Beanstalk

---

## Support & Resources

### Documentation
- 📚 [Lightsail Full Guide](DEPLOYMENT_GUIDE_LIGHTSAIL.md)
- 📚 [Beanstalk Full Guide](DEPLOYMENT_GUIDE_BEANSTALK.md)
- 📚 [Complete Service Evaluation](AWS_DEPLOYMENT_COMPREHENSIVE_EVALUATION.md)
- 📚 [Extended Options](AWS_DEPLOYMENT_EXTENDED_OPTIONS.md)

### AWS Resources
- [Lightsail Documentation](https://docs.aws.amazon.com/lightsail/)
- [Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [AWS Forums](https://forums.aws.amazon.com/)
- [AWS Support](https://console.aws.amazon.com/support/)

### Pricing Calculators
- [AWS Pricing Calculator](https://calculator.aws/)
- [Lightsail Pricing](https://aws.amazon.com/lightsail/pricing/)
- [Beanstalk Pricing](https://aws.amazon.com/elasticbeanstalk/pricing/)

---

## Summary

### Your Application is Ready to Deploy!

**Files Added:**
- ✅ `.ebextensions/` - Beanstalk configuration
- ✅ `gunicorn.conf.py` - Production WSGI config
- ✅ `Procfile` - Process definition
- ✅ `Dockerfile.lightsail` - Optimized Docker image
- ✅ `.ebignore` / `.dockerignore` - Deployment filters

**Documentation Created:**
- ✅ Complete deployment guides (2)
- ✅ Service evaluation documents (2)
- ✅ This quick start guide

**Recommended Path:**
1. **Start:** AWS Lightsail ($40/month) - Deploy MVP in 30 minutes
2. **Grow:** AWS Elastic Beanstalk ($150/month) - Scale with auto-scaling
3. **Enterprise:** AWS Fargate ($155+/month) - Full container orchestration

**Next Steps:**
1. Choose deployment path (Lightsail or Beanstalk recommended)
2. Follow the corresponding guide
3. Test thoroughly
4. Setup monitoring
5. Go live!

Good luck with your deployment! 🚀
