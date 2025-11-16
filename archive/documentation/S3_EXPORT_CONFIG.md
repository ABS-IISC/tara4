# S3 Export Configuration for AI-Prism

## Overview
The S3 export functionality automatically saves complete review sessions to AWS S3 storage when users complete their document review.

## S3 Bucket Structure
```
s3://felix-s3-bucket/tara/
├── 20241114_143022_document_name/
│   ├── documents/
│   │   ├── before_document_name.docx
│   │   ├── after_document_name.docx
│   │   └── guidelines_document_name.docx
│   ├── feedback/
│   │   ├── accepted_feedback.json
│   │   ├── rejected_feedback.json
│   │   ├── user_custom_feedback.json
│   │   └── all_ai_suggestions.json
│   ├── logs/
│   │   ├── activity_log.json
│   │   ├── chat_history.json
│   │   └── audit_logs.json
│   ├── comprehensive_report.json
│   └── readable_report.txt
```

## App Runner Configuration

### Environment Variables
Add these to your App Runner service configuration:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=felix-s3-bucket
S3_BASE_PATH=tara/

# Application Configuration
FLASK_ENV=production
PORT=8080
BEDROCK_MODEL_ID=anthropic.claude-3-7-sonnet-20250219-v1:0
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
REASONING_ENABLED=true
REASONING_BUDGET_TOKENS=2000
```

### IAM Role Permissions
Your App Runner service needs an IAM role with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::felix-s3-bucket",
                "arn:aws:s3:::felix-s3-bucket/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-7-sonnet-20250219-v1:0"
            ]
        }
    ]
}
```

## User Experience Flow

### 1. Complete Review Button
When user clicks "Complete Review":
- Shows confirmation popup with S3 export option
- User can choose:
  - ☁️ Complete with S3 Export (Recommended)
  - 💾 Local Download Only
  - ❌ Cancel

### 2. S3 Export Process
If user chooses S3 export:
1. Generates final document with comments
2. Creates timestamped folder in S3
3. Uploads all documents (before/after/guidelines)
4. Exports all feedback data (accepted/rejected/custom)
5. Saves complete activity logs and chat history
6. Creates comprehensive analysis report
7. Provides download link for final document

### 3. Fallback Behavior
If S3 is unavailable:
- Automatically falls back to local storage
- Creates export folder in `/exports/` directory
- Generates ZIP file with all content
- User still gets complete audit trail

## Export Contents

### Documents Folder
- **before_[document_name].docx**: Original uploaded document
- **after_[document_name].docx**: Final document with AI and user comments
- **guidelines_[document_name].docx**: Custom guidelines (if uploaded)

### Feedback Folder
- **accepted_feedback.json**: All AI feedback accepted by user
- **rejected_feedback.json**: All AI feedback rejected by user  
- **user_custom_feedback.json**: All custom feedback added by user
- **all_ai_suggestions.json**: Complete original AI analysis

### Logs Folder
- **activity_log.json**: Complete user activity timeline
- **chat_history.json**: All AI chat conversations
- **audit_logs.json**: Detailed audit trail with performance metrics

### Reports
- **comprehensive_report.json**: Complete analysis with statistics
- **readable_report.txt**: Human-readable summary report

## Testing S3 Export

### Local Testing
```bash
# Test S3 connection and export functionality
python test_s3_export.py
```

### Production Verification
1. Deploy to App Runner with proper IAM role
2. Upload a test document
3. Complete review with S3 export option
4. Verify files appear in S3 bucket
5. Check CloudWatch logs for any errors

## Troubleshooting

### Common Issues

**S3 Access Denied**
- Verify IAM role has correct S3 permissions
- Check bucket policy allows App Runner service
- Ensure bucket exists and is in correct region

**Export Fails Silently**
- Check CloudWatch logs for detailed error messages
- Verify AWS_REGION environment variable is set
- Test with smaller documents first

**Local Fallback Always Used**
- Check AWS credentials configuration
- Verify S3 bucket name and region
- Test S3 connection with AWS CLI

### Monitoring
Monitor these CloudWatch metrics:
- S3 PUT/GET operations
- Export success/failure rates
- Average export time
- Storage usage in S3 bucket

## Security Considerations

### Data Protection
- All exports are encrypted in transit (HTTPS/TLS)
- S3 bucket should have encryption at rest enabled
- Consider bucket versioning for audit compliance
- Implement lifecycle policies for data retention

### Access Control
- Use least-privilege IAM policies
- Consider S3 bucket policies for additional security
- Monitor access logs for unusual activity
- Implement MFA for S3 bucket access if required

## Cost Optimization

### S3 Storage Classes
- Use Standard for frequently accessed exports
- Consider Standard-IA for older exports
- Implement lifecycle policies to move to cheaper storage

### Monitoring Costs
- Set up billing alerts for S3 usage
- Monitor export frequency and size
- Consider data compression for large exports

## Compliance & Audit

### Audit Trail
Each export creates a complete audit trail including:
- User actions and timestamps
- AI analysis decisions
- Document modification history
- Chat conversation logs
- Performance metrics

### Retention Policy
Implement appropriate retention policies based on:
- Regulatory requirements
- Business needs
- Storage costs
- Compliance mandates

## Future Enhancements

### Planned Features
- Batch export for multiple documents
- Export scheduling and automation
- Integration with other AWS services
- Advanced analytics on export data
- Custom export templates
- Email notifications on export completion

### Integration Opportunities
- CloudTrail for enhanced auditing
- Lambda for post-processing
- SNS for notifications
- CloudWatch for monitoring
- Athena for analytics on export data