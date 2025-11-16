# S3 Export Setup Guide for AI-Prism

## Quick Fix for S3 Document Export

The AI-Prism tool can export your complete document reviews to AWS S3 for backup and audit purposes. If documents are not saving to S3, follow this guide.

## 🚀 Quick Setup

### Option 1: Run the Setup Script
```bash
python setup_aws_s3.py
```

### Option 2: Manual Setup

1. **Install AWS CLI** (if not already installed):
   ```bash
   pip install awscli
   ```

2. **Configure AWS Credentials**:
   ```bash
   aws configure
   ```
   Enter your:
   - AWS Access Key ID
   - AWS Secret Access Key  
   - Default region: `us-east-1`
   - Output format: `json`

3. **Test S3 Access**:
   ```bash
   aws s3 ls s3://felix-s3-bucket/tara/
   ```

## 🔧 Troubleshooting S3 Export Issues

### Issue: "No AWS credentials found"
**Solution**: Configure AWS credentials using one of these methods:

1. **AWS CLI** (Recommended):
   ```bash
   aws configure
   ```

2. **Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **Credentials File**: Create `~/.aws/credentials`:
   ```ini
   [default]
   aws_access_key_id = your_access_key
   aws_secret_access_key = your_secret_key
   ```

### Issue: "Bucket not accessible"
**Solution**: Check bucket permissions and name:

1. **Verify Bucket Name**: Default is `felix-s3-bucket`
2. **Check Permissions**: Your AWS user needs:
   - `s3:GetObject`
   - `s3:PutObject`
   - `s3:DeleteObject`
   - `s3:ListBucket`

3. **Test Bucket Access**:
   ```bash
   aws s3 ls s3://felix-s3-bucket/
   ```

### Issue: "S3 export failed"
**Solution**: The app will automatically fallback to local storage:

1. Check the `exports/` folder in your project directory
2. Look for timestamped folders with your document name
3. Files are also saved as ZIP archives for easy sharing

## 🧪 Testing S3 Connection

### In the AI-Prism App:
1. Click the "☁️ Test S3" button in the controls
2. Check the connection status
3. Review any error messages

### From Command Line:
```bash
python setup_aws_s3.py
```

## 📁 S3 Export Structure

When S3 export works, your files are organized like this:

```
s3://felix-s3-bucket/tara/
└── 20241201_143022_your_document_name/
    ├── documents/
    │   ├── before_your_document.docx
    │   ├── after_your_document.docx
    │   └── guidelines_document.docx
    ├── feedback/
    │   ├── accepted_feedback.json
    │   ├── rejected_feedback.json
    │   ├── user_custom_feedback.json
    │   └── all_ai_suggestions.json
    ├── logs/
    │   ├── activity_log.json
    │   ├── chat_history.json
    │   └── audit_logs.json
    ├── comprehensive_report.json
    └── readable_report.txt
```

## 🔄 Local Fallback

If S3 export fails, files are automatically saved locally:

- **Location**: `exports/` folder in your project directory
- **Format**: Same structure as S3, plus ZIP file
- **Access**: Check the app logs for exact file paths

## 🆘 Still Having Issues?

1. **Check AWS Credentials**:
   ```bash
   aws sts get-caller-identity
   ```

2. **Verify S3 Permissions**:
   ```bash
   aws s3api head-bucket --bucket felix-s3-bucket
   ```

3. **Test with Different Bucket**: Edit `utils/s3_export_manager.py`:
   ```python
   def __init__(self, bucket_name='your-bucket-name', base_path='your-path/'):
   ```

4. **Check App Logs**: Look for S3-related error messages in the console

## 💡 Pro Tips

- **Use IAM Roles**: For production, use IAM roles instead of access keys
- **Bucket Policies**: Ensure your S3 bucket allows your AWS user/role
- **Region Matching**: Use the same region for your bucket and credentials
- **Test Regularly**: Use the "Test S3" button to verify connectivity

## 🔐 Security Best Practices

1. **Least Privilege**: Only grant necessary S3 permissions
2. **Rotate Keys**: Regularly rotate your AWS access keys
3. **Use IAM Roles**: When running on EC2 or other AWS services
4. **Bucket Encryption**: Enable S3 bucket encryption for sensitive documents
5. **Access Logging**: Enable S3 access logging for audit trails

---

**Need Help?** The AI-Prism app includes built-in S3 testing and will automatically fallback to local storage if S3 is unavailable.