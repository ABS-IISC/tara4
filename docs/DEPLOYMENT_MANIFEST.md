# AI-Prism Elastic Beanstalk Deployment Package
## Final Region-Agnostic Version

**Package Name:** `ai-prism-eb-final.zip`
**Package Size:** 480 KB
**MD5 Checksum:** `99ab20e9ac573126fa83f8d6037ecda5`
**Created:** November 27, 2025
**Target Platform:** AWS Elastic Beanstalk (Python 3.11)

---

## Package Contents (69 files)

### Critical Files for Multi-Region Support

#### 1. **Region Configuration Module** ✅
- `config/aws_regions.py` (22,664 bytes) - **NEW**
  - Supports ALL 34 AWS regions
  - 18 Bedrock-enabled regions with native support
  - 16 non-Bedrock regions with automatic cross-region fallback
  - Auto-detects region from 5 sources (AWS_REGION, EC2 metadata, AWS CLI, boto3, fallback)
  - Regional model ID mappings (us./eu./apac. prefixes)
  - S3 bucket region auto-detection
  - Thread-safe with LRU caching

#### 2. **Updated S3 Export Manager** ✅
- `utils/s3_export_manager.py` (24,690 bytes) - **UPDATED**
  - Imports centralized region config
  - Auto-detects S3 bucket region
  - Uses region-specific S3 client initialization
  - Enhanced logging with region information

#### 3. **Updated Flask Application** ✅
- `app.py` (131,866 bytes) - **UPDATED**
  - Imports region configuration functions
  - Completely rewritten `SimpleModelConfig` class
  - Dynamic model ID selection based on detected region
  - Connection test endpoints show region info
  - Graceful fallback if region detection fails

#### 4. **Elastic Beanstalk Configuration** ✅
- `.ebextensions/01_environment.config` (6,650 bytes) - **UPDATED**
  - Pre-configured for eu-north-1 deployment
  - Comprehensive region configuration documentation
  - Instructions for deploying to any of 34 AWS regions
  - Auto-scaling configuration (3-15 instances)
  - Load balancer optimized for long Claude API calls (600s timeout)
  - Health check configuration
  - Environment variables with region guidance

#### 5. **Application Entry Point** ✅
- `main.py` (4,731 bytes)
  - Flask application initialization
  - Gunicorn WSGI server configuration

#### 6. **Python Dependencies** ✅
- `requirements.txt` (618 bytes)
  - Flask 2.3.3
  - boto3 1.28.85 (AWS SDK)
  - python-docx 0.8.11
  - gunicorn 21.2.0
  - gevent 24.2.1 (async workers)
  - redis 5.0.1, rq 1.15.1 (optional async processing)
  - All dependencies pinned for reproducibility

---

## Application Modules

### Core Modules (7 files)
- `core/ai_feedback_engine.py` - AI-powered feedback analysis
- `core/document_analyzer.py` - Document processing and analysis
- `core/database_manager.py` - Data persistence layer
- `core/async_request_manager.py` - Async request handling
- `core/toon_serializer.py` - Data serialization
- `core/__init__.py`
- `core/ai_feedback_engine.py.bak` - Backup

### Utilities (9 files)
- `utils/s3_export_manager.py` - **REGION-AGNOSTIC** S3 operations
- `utils/document_processor.py` - Document text extraction
- `utils/activity_logger.py` - Activity logging
- `utils/thread_pool_manager.py` - Thread pool management
- `utils/statistics_manager.py` - Statistics tracking
- `utils/audit_logger.py` - Audit trail logging
- `utils/learning_system.py` - ML-based learning
- `utils/pattern_analyzer.py` - Pattern recognition
- `utils/task_functions.py` - Background tasks
- `utils/__init__.py`

### Configuration (5 files)
- `config/aws_regions.py` - **NEW** Multi-region configuration
- `config/model_config_enhanced.py` - Enhanced model fallback configuration
- `config/bedrock_prompt_templates.py` - Claude prompt templates
- `config/ai_prompts.py` - AI prompts library
- `config/__init__.py`

### UI/Templates (6 files)
- `ui/responsive_interface.py` - Responsive UI components
- `ui/__init__.py`
- `templates/enhanced_index.html` - Main UI template
- `templates/abc.html` - Alternative template
- `templates/enhanced_index_backup.html` - Backup
- `templates/enhanced_index_OLD.html` - Legacy

### Static Assets (19 JavaScript files)
- `static/js/unified_button_fixes.js` - Unified button handlers
- `static/js/button_fixes.js` - Button fix logic
- `static/js/global_function_fixes.js` - Global function patches
- `static/js/text_highlighting.js` - Text selection/highlighting
- `static/js/network_error_handler.js` - Network error handling
- `static/js/activity_logs.js` - Activity log viewer
- `static/js/enhanced_help_system.js` - Help system
- Plus 12 additional JavaScript modules

### Elastic Beanstalk Configuration (2 files)
- `.ebextensions/01_environment.config` - **UPDATED** Environment settings
- `.ebextensions/02_packages.config` - System packages

### Additional Files
- `Dockerfile` - Container configuration (for local testing)
- `.claude/settings.local.json` - Claude Code IDE settings

---

## Region Support Matrix

### ✅ Bedrock-Enabled Regions (18 regions)
These regions have native Claude Sonnet 4.5 support:

**United States (4 regions)**
- `us-east-1` - United States (N. Virginia) - **PRIMARY**
- `us-east-2` - United States (Ohio)
- `us-west-1` - United States (N. California)
- `us-west-2` - United States (Oregon)

**Europe (6 regions)**
- `eu-north-1` - Europe (Stockholm) - **CURRENT DEPLOYMENT**
- `eu-west-1` - Europe (Ireland)
- `eu-west-2` - Europe (London)
- `eu-west-3` - Europe (Paris)
- `eu-central-1` - Europe (Frankfurt)
- `eu-south-2` - Europe (Spain)

**Asia Pacific (6 regions)**
- `ap-south-1` - Asia Pacific (Mumbai)
- `ap-northeast-1` - Asia Pacific (Tokyo)
- `ap-northeast-2` - Asia Pacific (Seoul)
- `ap-northeast-3` - Asia Pacific (Osaka)
- `ap-southeast-1` - Asia Pacific (Singapore)
- `ap-southeast-2` - Asia Pacific (Sydney)

**Other (2 regions)**
- `ca-central-1` - Canada (Central)
- `sa-east-1` - South America (São Paulo)

### ⚠️ Cross-Region Fallback Regions (16 regions)
These regions automatically route Bedrock calls to the nearest supported region:

**Canada:** ca-west-1
**South America:** mx-central-1
**Europe:** eu-central-2, eu-south-1
**Asia Pacific:** ap-south-2, ap-southeast-3, ap-southeast-4, ap-southeast-5, ap-southeast-6, ap-southeast-7, ap-southeast-8, ap-east-1
**Middle East:** me-south-1, me-central-1
**Africa:** af-south-1
**Israel:** il-central-1

---

## Regional Model IDs

The package automatically selects the correct model ID based on deployment region:

### US Regions
```
Model ID: us.anthropic.claude-sonnet-4-5-20250929-v1:0
Regions: us-east-1, us-east-2, us-west-1, us-west-2
```

### EU Regions
```
Model ID: eu.anthropic.claude-sonnet-4-5-20250929-v1:0
Regions: eu-north-1, eu-west-1, eu-west-2, eu-west-3, eu-central-1, eu-south-2
```

### APAC Regions
```
Model ID: apac.anthropic.claude-sonnet-4-5-20250929-v1:0
Regions: ap-south-1, ap-northeast-1, ap-northeast-2, ap-northeast-3, ap-southeast-1, ap-southeast-2
```

### Other Regions
```
Model ID: anthropic.claude-sonnet-4-5-20250929-v1:0
Regions: ca-central-1, sa-east-1
```

---

## Pre-Deployment Checklist

Before deploying to Elastic Beanstalk, ensure you have:

### AWS Resources
- [ ] IAM Role: `aws-elasticbeanstalk-ec2-role` with policies:
  - AmazonBedrockFullAccess
  - AmazonS3FullAccess
  - CloudWatchLogsFullAccess
- [ ] IAM Role: `aws-elasticbeanstalk-service-role`
- [ ] S3 Bucket: Created in target region
- [ ] Bedrock Access: Model access enabled in target region

### Configuration Updates
- [ ] Update `AWS_REGION` in `.ebextensions/01_environment.config`
- [ ] Update `S3_BUCKET_NAME` to your bucket name
- [ ] Update `S3_REGION` to match your S3 bucket's region
- [ ] Verify `BEDROCK_MODEL_ID` is set (or leave unset for auto-detection)

### Elastic Beanstalk Environment
- [ ] Application created: `AI_prism` (or your preferred name)
- [ ] Platform: Python 3.11 running on 64bit Amazon Linux 2023
- [ ] Instance type: t3.large or larger (for 100+ concurrent users)
- [ ] Load balancer type: Application Load Balancer

---

## Deployment Instructions for eu-north-1

### Current Configuration
The package is **pre-configured** for deployment to **eu-north-1** (Europe - Stockholm):

```yaml
AWS_REGION: eu-north-1
AWS_DEFAULT_REGION: eu-north-1
S3_BUCKET_NAME: ai-prism-logs-600222957378-eu
S3_REGION: eu-north-1
BEDROCK_MODEL_ID: anthropic.claude-sonnet-4-5-20250929-v1:0
```

### Deployment Steps

#### Option 1: AWS Console Deployment
1. Log in to AWS Console → Elastic Beanstalk
2. Select your application (`AI_prism`)
3. Click "Upload and deploy"
4. Upload: `ai-prism-eb-final.zip`
5. Version label: `v2-region-agnostic-{timestamp}`
6. Click "Deploy"
7. Monitor deployment in Events tab
8. Wait for health status to turn Green (5-10 minutes)

#### Option 2: AWS CLI Deployment
```bash
# Set your application and environment names
APP_NAME="AI_prism"
ENV_NAME="AI_prism-env"
REGION="eu-north-1"

# Create application version
aws elasticbeanstalk create-application-version \
  --application-name $APP_NAME \
  --version-label v2-region-agnostic-$(date +%Y%m%d-%H%M%S) \
  --source-bundle S3Bucket="your-deployment-bucket",S3Key="ai-prism-eb-final.zip" \
  --region $REGION

# Deploy to environment
aws elasticbeanstalk update-environment \
  --application-name $APP_NAME \
  --environment-name $ENV_NAME \
  --version-label v2-region-agnostic-$(date +%Y%m%d-%H%M%S) \
  --region $REGION
```

#### Option 3: EB CLI Deployment
```bash
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2

# Initialize EB (if not already done)
eb init -p python-3.11 AI_prism --region eu-north-1

# Deploy the new version
eb deploy AI_prism-env

# Monitor deployment
eb status
eb logs
```

---

## Post-Deployment Verification

### 1. Health Check
```bash
curl https://your-eb-environment.eu-north-1.elasticbeanstalk.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "region": "eu-north-1",
  "bedrock_region": "eu-north-1",
  "s3_region": "eu-north-1",
  "model_id": "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"
}
```

### 2. Connection Test
```bash
curl https://your-eb-environment.eu-north-1.elasticbeanstalk.com/test_bedrock_connection
```

### 3. Region Configuration Test
```bash
curl https://your-eb-environment.eu-north-1.elasticbeanstalk.com/test_region_config
```

### 4. Check Logs
```bash
# Via EB CLI
eb logs

# Via AWS Console
Elastic Beanstalk → Environments → Logs → Request Logs → Full Logs
```

Look for log messages like:
```
✅ Region from EC2 metadata: eu-north-1
📍 Region Configuration:
   Primary Region: eu-north-1 (Europe (Stockholm))
   Bedrock Region: eu-north-1
   S3 Region: eu-north-1
   Model ID: eu.anthropic.claude-sonnet-4-5-20250929-v1:0
   Detection: auto-detected
```

---

## Deploying to Other Regions

### Quick Region Switch

To deploy to a different region, update `.ebextensions/01_environment.config`:

#### Example: Deploy to us-east-1
```yaml
AWS_REGION: us-east-1
AWS_DEFAULT_REGION: us-east-1
S3_BUCKET_NAME: ai-prism-logs-{your-account-id}-us
S3_REGION: us-east-1
BEDROCK_MODEL_ID: us.anthropic.claude-sonnet-4-5-20250929-v1:0
```

#### Example: Deploy to ap-southeast-1 (Singapore)
```yaml
AWS_REGION: ap-southeast-1
AWS_DEFAULT_REGION: ap-southeast-1
S3_BUCKET_NAME: ai-prism-logs-{your-account-id}-apac
S3_REGION: ap-southeast-1
BEDROCK_MODEL_ID: apac.anthropic.claude-sonnet-4-5-20250929-v1:0
```

#### Example: Deploy to non-Bedrock region (cross-region fallback)
```yaml
AWS_REGION: ap-southeast-3  # Jakarta (no Bedrock)
AWS_DEFAULT_REGION: ap-southeast-3
S3_BUCKET_NAME: ai-prism-logs-{your-account-id}-jakarta
S3_REGION: ap-southeast-3
# Model ID auto-detected, Bedrock calls routed to ap-southeast-1
```

After updating the config:
1. Re-create the deployment package: `zip -r ai-prism-eb-final.zip ...`
2. Deploy using one of the methods above
3. Application will automatically detect and use the new region

---

## Troubleshooting

### Health Check Failures
**Symptom:** Deployment fails with "Instance id(s) did not pass health check"

**Possible Causes:**
1. Missing IAM permissions
2. S3 bucket not accessible
3. Bedrock not enabled in region
4. Import errors in Python code
5. Health check timeout

**Solutions:**
```bash
# 1. Check IAM role has correct policies
aws iam list-attached-role-policies --role-name aws-elasticbeanstalk-ec-role

# 2. Test S3 access
aws s3 ls s3://ai-prism-logs-600222957378-eu --region eu-north-1

# 3. Test Bedrock access
aws bedrock list-foundation-models --region eu-north-1 --by-provider Anthropic

# 4. Check application logs
eb logs --all

# 5. Increase health check timeout in .ebextensions/01_environment.config
HealthCheckTimeout: 10  # Increase from 5 to 10 seconds
```

### Region Detection Issues
**Symptom:** Application uses wrong region or falls back to us-east-1

**Solution:**
Explicitly set environment variables in `.ebextensions/01_environment.config`:
```yaml
AWS_REGION: eu-north-1
AWS_DEFAULT_REGION: eu-north-1
```

### Bedrock Permission Errors
**Symptom:** 403 Forbidden errors when calling Claude API

**Solution:**
```bash
# Add Bedrock permissions to EC2 role
aws iam attach-role-policy \
  --role-name aws-elasticbeanstalk-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

### S3 Access Errors
**Symptom:** Cannot export to S3, "Access Denied" errors

**Solution:**
1. Verify bucket exists in correct region:
```bash
aws s3api get-bucket-location --bucket ai-prism-logs-600222957378-eu
```

2. Update S3 bucket policy to allow EC2 role access

3. Ensure S3_REGION matches bucket's actual region

---

## Performance Optimization

### For 100+ Concurrent Users

Current configuration supports 100+ concurrent users with:
- **Auto-scaling:** 3-15 instances (t3.large)
- **CPU Threshold:** 70% (scale up aggressively)
- **Load Balancer Timeout:** 600s (for long Claude API calls)
- **Gunicorn Workers:** gevent async workers
- **Session Stickiness:** 24 hours

### To Increase Capacity:
Edit `.ebextensions/01_environment.config`:
```yaml
aws:autoscaling:asg:
  MinSize: 5          # Increase minimum instances
  MaxSize: 30         # Increase maximum instances

aws:autoscaling:launchconfiguration:
  InstanceType: t3.xlarge  # Upgrade to 4 vCPU, 16 GB RAM
```

---

## Package Integrity Verification

Before deployment, verify package integrity:

```bash
# Verify MD5 checksum
md5 ai-prism-eb-final.zip
# Should output: MD5 (ai-prism-eb-final.zip) = 99ab20e9ac573126fa83f8d6037ecda5

# Verify file count
unzip -l ai-prism-eb-final.zip | wc -l
# Should output: 69

# Verify critical files exist
unzip -l ai-prism-eb-final.zip | grep -E "(aws_regions|s3_export_manager|app.py|requirements.txt)"
```

---

## Migration from Previous Version

If migrating from the old deployment (AI_prism-1) to this new version:

### Zero-Downtime Migration
1. Deploy new version to a NEW environment (e.g., `AI_prism-v2-env`)
2. Test thoroughly in new environment
3. Use Route 53 or load balancer to gradually shift traffic
4. Monitor both environments during transition
5. Terminate old environment after full migration

### In-Place Update (Small Downtime)
1. Create backup of current environment configuration
2. Deploy `ai-prism-eb-final.zip` to existing environment
3. Elastic Beanstalk will perform rolling update (1 instance at a time)
4. Total downtime: ~5-15 minutes depending on instance count

---

## Support and Debugging

### Enable Debug Logging
Set environment variable:
```yaml
FLASK_DEBUG: "true"
```

### Access Instance via SSH
```bash
eb ssh AI_prism-env
```

### View Real-Time Logs
```bash
eb logs --stream
```

### Test Region Configuration Locally
```bash
cd /Users/abhsatsa/Documents/risk\ stuff/tool/tara2
python3 -c "from config.aws_regions import get_region_config; print(get_region_config())"
```

---

## Package Changelog

### Version 2.0 - Region-Agnostic (November 27, 2025)
✅ **NEW:** Complete multi-region support for all 34 AWS regions
✅ **NEW:** Automatic region detection from 5 sources
✅ **NEW:** Regional model ID selection (us./eu./apac. prefixes)
✅ **NEW:** Cross-region Bedrock fallback for non-supported regions
✅ **NEW:** S3 bucket region auto-detection
✅ **UPDATED:** S3ExportManager for region-agnostic initialization
✅ **UPDATED:** Flask app with dynamic model configuration
✅ **UPDATED:** Elastic Beanstalk config with comprehensive region documentation
✅ **IMPROVED:** Error handling and fallback mechanisms
✅ **IMPROVED:** Logging with region context

### Version 1.0 - Initial Deployment
- Hardcoded to us-east-2 and eu-north-1
- Manual region configuration required
- No automatic fallback

---

## License and Credits

**Application:** AI-Prism Risk Assessment Tool
**Cloud Platform:** AWS Elastic Beanstalk
**AI Provider:** Anthropic Claude (via AWS Bedrock)
**Deployment Package Created:** November 27, 2025
**Region-Agnostic Enhancement:** Claude Code

---

## Quick Reference

| Property | Value |
|----------|-------|
| Package Name | ai-prism-eb-final.zip |
| Package Size | 480 KB |
| File Count | 69 files |
| MD5 Checksum | 99ab20e9ac573126fa83f8d6037ecda5 |
| Target Region | eu-north-1 (pre-configured) |
| Python Version | 3.11 |
| Platform | Amazon Linux 2023 |
| Min Instances | 3 |
| Max Instances | 15 |
| Instance Type | t3.large |
| LB Timeout | 600 seconds |
| Health Check | /health |
| Deployment Time | ~5-10 minutes |

---

**Ready for deployment to any of the 34 AWS regions! 🚀**
