# AI-Prism Production Credentials & Endpoints

**IMPORTANT:** Keep this file secure and do not commit to version control!

---

## 🌐 Application URLs

### Primary Endpoints
- **Elastic Beanstalk:** http://ai-prism-prod.eu-north-1.elasticbeanstalk.com
- **CloudFront CDN:** https://d3fna3nvr6h3a0.cloudfront.net
- **Load Balancer:** awseb--AWSEB-sZaC9E02O2CL-1884918780.eu-north-1.elb.amazonaws.com

---

## 🗄️ Database Credentials

### PostgreSQL RDS
```
Host: ai-prism-postgres.cxisww4oqn9v.eu-north-1.rds.amazonaws.com
Port: 5432
Database: aiprism
Username: aiprismadmin
Password: AiPrism2024SecurePass

Connection String:
postgresql://aiprismadmin:AiPrism2024SecurePass@ai-prism-postgres.cxisww4oqn9v.eu-north-1.rds.amazonaws.com:5432/aiprism
```

**psql command:**
```bash
psql -h ai-prism-postgres.cxisww4oqn9v.eu-north-1.rds.amazonaws.com \
     -U aiprismadmin \
     -d aiprism \
     -p 5432
```

---

## 💾 Redis Cache

### ElastiCache Redis
```
Host: ai-prism-redis.5ubcga.0001.eun1.cache.amazonaws.com
Port: 6379
Database: 0

Connection String:
redis://ai-prism-redis.5ubcga.0001.eun1.cache.amazonaws.com:6379/0
```

**redis-cli command:**
```bash
redis-cli -h ai-prism-redis.5ubcga.0001.eun1.cache.amazonaws.com -p 6379
```

---

## 📦 S3 Buckets

### Primary Storage
- **Bucket Name:** `ai.prism`
- **Region:** eu-north-1
- **URL:** s3://ai.prism/
- **Console:** https://s3.console.aws.amazon.com/s3/buckets/ai.prism

### Backup Storage
- **Bucket Name:** `ai-prism-backups`
- **Region:** eu-north-1
- **URL:** s3://ai-prism-backups/
- **Console:** https://s3.console.aws.amazon.com/s3/buckets/ai-prism-backups

---

## 🌍 CloudFront CDN

- **Distribution ID:** E92ME8ZL3PLL0
- **Domain Name:** d3fna3nvr6h3a0.cloudfront.net
- **Status:** Deployed
- **Console:** https://console.aws.amazon.com/cloudfront/v3/home#/distributions/E92ME8ZL3PLL0

**Static Assets URLs:**
- Old: `http://ai-prism-prod.eu-north-1.elasticbeanstalk.com/static/...`
- New: `https://d3fna3nvr6h3a0.cloudfront.net/static/...`

---

## 📊 Monitoring & Logs

### CloudWatch Dashboards
1. **Bedrock Metrics:** https://console.aws.amazon.com/cloudwatch/home?region=eu-north-1#dashboards:name=AI-Prism-Bedrock-Metrics
2. **Application Performance:** https://console.aws.amazon.com/cloudwatch/home?region=eu-north-1#dashboards:name=AI-Prism-Application-Performance
3. **Infrastructure Health:** https://console.aws.amazon.com/cloudwatch/home?region=eu-north-1#dashboards:name=AI-Prism-Infrastructure-Health

### CloudWatch Alarms
- **High CPU:** AI-Prism-High-CPU
- **High Memory:** AI-Prism-High-Memory
- **Bedrock Throttling:** AI-Prism-Bedrock-Throttling
- **5xx Errors:** AI-Prism-High-5xx-Errors
- **Redis Memory:** AI-Prism-Redis-High-Memory

### Log Streams
```bash
# View application logs
aws logs tail /aws/elasticbeanstalk/AI-Prism-Production/var/log/eb-engine.log --follow

# View web server logs
aws logs tail /aws/elasticbeanstalk/AI-Prism-Production/var/log/web.stdout.log --follow
```

---

## 🔐 Security Groups

### EB Instance Security Group
- **ID:** sg-017f605744bb4ca1e
- **Purpose:** EC2 instances running the application
- **Ingress:** HTTP/HTTPS from ALB

### Redis Security Group
- **ID:** sg-08f44365739f6ece7
- **Purpose:** ElastiCache Redis cluster
- **Ingress:** Port 6379 from EB instances

### RDS Security Group
- **ID:** sg-07098fd80ec3cb52d
- **Purpose:** PostgreSQL RDS instance
- **Ingress:** Port 5432 from EB instances

---

## 🖥️ EC2 Instances

### Current Running Instances
```
Instance ID            Type       Private IP
i-0867503c8556d03d2    t3.large   172.31.x.x
i-0dd1841f13e8d975e    t3.large   172.31.x.x
i-03c26b21dbaf2d6c2    t3.large   172.31.x.x
```

**Auto-Scaling Configuration:**
- Min Size: 3
- Max Size: 15
- Desired: 3

---

## 🔑 IAM Roles

### EB Instance Role
- **Name:** aws-elasticbeanstalk-ec2-role
- **ARN:** arn:aws:iam::600222957378:role/aws-elasticbeanstalk-ec2-role
- **Permissions:** S3, Bedrock, CloudWatch, EC2

### S3 Replication Role
- **Name:** ai-prism-s3-replication-role
- **ARN:** arn:aws:iam::600222957378:role/ai-prism-s3-replication-role
- **Purpose:** S3 cross-bucket replication

---

## 🌐 Network Configuration

### VPC
- **ID:** vpc-0ea15ff1bbb2d473e
- **CIDR:** 172.31.0.0/16
- **Region:** eu-north-1

### Subnets
```
Subnet ID                    AZ            CIDR
subnet-05c8bf51b23aae0cd     eu-north-1c   172.31.0.0/20
subnet-0c006a13357037927     eu-north-1b   172.31.32.0/20
subnet-00858970d57520a73     eu-north-1a   172.31.16.0/20
```

---

## 🤖 Bedrock Configuration

### Claude Models (Fallback Chain)
1. **Primary:** us.anthropic.claude-sonnet-4-5-20250929-v1:0
2. **Fallback 1:** us.anthropic.claude-sonnet-4-0-20241129-v1:0
3. **Fallback 2:** us.anthropic.claude-3-7-sonnet-20250219-v1:0
4. **Fallback 3:** us.anthropic.claude-3-5-sonnet-20240620-v1:0
5. **Fallback 4:** us.anthropic.claude-3-5-sonnet-20241022-v2:0
6. **Fallback 5:** anthropic.claude-3-sonnet-20240229-v1:0
7. **Fallback 6:** us.anthropic.claude-haiku-4-5-20250815-v1:0

**Region:** us-east-1 (Bedrock models)
**Quota per Model:** 200 RPM
**Total Available:** 650+ RPM

---

## ⚙️ Environment Variables

```bash
# Application
FLASK_ENV=production
PORT=8080

# Database
DATABASE_URL=postgresql://aiprismadmin:AiPrism2024SecurePass@ai-prism-postgres.cxisww4oqn9v.eu-north-1.rds.amazonaws.com:5432/aiprism

# Redis
REDIS_URL=redis://ai-prism-redis.5ubcga.0001.eun1.cache.amazonaws.com:6379/0

# AWS
AWS_REGION=eu-north-1
AWS_DEFAULT_REGION=eu-north-1

# S3
S3_BUCKET=ai.prism
S3_BACKUP_BUCKET=ai-prism-backups

# CDN
CLOUDFRONT_DOMAIN=d3fna3nvr6h3a0.cloudfront.net
```

---

## 🚀 Deployment Commands

### Update Environment Variables
```bash
aws elasticbeanstalk update-environment \
  --environment-name AI-Prism-Production \
  --region eu-north-1 \
  --option-settings \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=DATABASE_URL,Value=postgresql://aiprismadmin:AiPrism2024SecurePass@ai-prism-postgres.cxisww4oqn9v.eu-north-1.rds.amazonaws.com:5432/aiprism
```

### Deploy New Application Version
```bash
# Create application version
eb deploy

# Or manually:
aws elasticbeanstalk create-application-version \
  --application-name AI-Prism \
  --version-label v4-$(date +%Y%m%d-%H%M%S) \
  --source-bundle S3Bucket=elasticbeanstalk-eu-north-1-600222957378,S3Key=app.zip

# Update environment
aws elasticbeanstalk update-environment \
  --environment-name AI-Prism-Production \
  --version-label v4-20241127-XXXXXX
```

### Restart Application
```bash
aws elasticbeanstalk restart-app-server \
  --environment-name AI-Prism-Production \
  --region eu-north-1
```

---

## 📝 Quick Commands

### Check Environment Status
```bash
aws elasticbeanstalk describe-environments \
  --environment-names AI-Prism-Production \
  --region eu-north-1
```

### View Recent Logs
```bash
eb logs
```

### SSH into Instance
```bash
eb ssh AI-Prism-Production
```

### Check RDS Status
```bash
aws rds describe-db-instances \
  --db-instance-identifier ai-prism-postgres \
  --region eu-north-1
```

### Check Redis Status
```bash
aws elasticache describe-cache-clusters \
  --cache-cluster-id ai-prism-redis \
  --region eu-north-1
```

### Invalidate CloudFront Cache
```bash
aws cloudfront create-invalidation \
  --distribution-id E92ME8ZL3PLL0 \
  --paths "/*"
```

---

## 🔒 Security Best Practices

1. **Rotate Database Password:**
   ```bash
   aws rds modify-db-instance \
     --db-instance-identifier ai-prism-postgres \
     --master-user-password NewSecurePassword123 \
     --apply-immediately
   ```

2. **Store Secrets in Secrets Manager:**
   ```bash
   aws secretsmanager create-secret \
     --name ai-prism/db/password \
     --secret-string "AiPrism2024SecurePass"
   ```

3. **Enable MFA for AWS Account**

4. **Review CloudTrail Logs Regularly**

---

*Last Updated: November 27, 2024*
*Region: eu-north-1 (Stockholm)*
*Account: 600222957378*
