#!/bin/bash

# Deploy S3 and Claude API Fixes to Elastic Beanstalk
# This script uploads and deploys the fixed code

set -e  # Exit on error

echo "🚀 Deploying Fixed Code to Elastic Beanstalk..."
echo ""

# Configuration
REGION="eu-north-1"
APP_NAME="AI-Prism1"
ZIP_FILE="ai-prism-eb-FIXED-S3-CLAUDE.zip"
VERSION_LABEL="fixed-s3-claude-$(date +%s)"

# Check if zip file exists
if [ ! -f "$ZIP_FILE" ]; then
    echo "❌ Error: $ZIP_FILE not found!"
    echo "   Run this script from the project directory."
    exit 1
fi

echo "📦 Package: $ZIP_FILE ($(du -h "$ZIP_FILE" | cut -f1))"
echo "🏷️  Version: $VERSION_LABEL"
echo ""

# Step 1: Upload to S3
echo "Step 1: Uploading to S3..."
S3_BUCKET="elasticbeanstalk-$REGION-600222957378"
S3_KEY="$VERSION_LABEL/$ZIP_FILE"

aws s3 cp "$ZIP_FILE" "s3://$S3_BUCKET/$S3_KEY" --region "$REGION"
echo "✅ Uploaded to s3://$S3_BUCKET/$S3_KEY"
echo ""

# Step 2: Create application version
echo "Step 2: Creating application version..."
aws elasticbeanstalk create-application-version \
    --application-name "$APP_NAME" \
    --version-label "$VERSION_LABEL" \
    --source-bundle S3Bucket="$S3_BUCKET",S3Key="$S3_KEY" \
    --region "$REGION" \
    --no-cli-pager

echo "✅ Application version created: $VERSION_LABEL"
echo ""

# Step 3: Get environment name
echo "Step 3: Finding environment..."
ENV_NAME=$(aws elasticbeanstalk describe-environments \
    --region "$REGION" \
    --query 'Environments[?contains(CNAME, `ai-prisms`)].[EnvironmentName]' \
    --output text)

if [ -z "$ENV_NAME" ]; then
    echo "❌ Error: Could not find environment with CNAME containing 'ai-prisms'"
    echo "   Available environments:"
    aws elasticbeanstalk describe-environments --region "$REGION" \
        --query 'Environments[].[EnvironmentName,CNAME]' --output table
    exit 1
fi

echo "✅ Found environment: $ENV_NAME"
echo ""

# Step 4: Deploy to environment
echo "Step 4: Deploying to $ENV_NAME..."
echo "⏱️  This will take 5-10 minutes..."
echo ""

aws elasticbeanstalk update-environment \
    --environment-name "$ENV_NAME" \
    --version-label "$VERSION_LABEL" \
    --region "$REGION" \
    --no-cli-pager

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📊 Monitor deployment:"
echo "   aws elasticbeanstalk describe-environments \\"
echo "       --environment-names \"$ENV_NAME\" \\"
echo "       --region \"$REGION\" \\"
echo "       --query 'Environments[0].[Status,Health,HealthStatus]' \\"
echo "       --output table"
echo ""
echo "🌐 Your application URL:"
echo "   http://ai-prisms.$REGION.elasticbeanstalk.com"
echo ""
echo "⏳ Wait 5-10 minutes for deployment to complete, then test:"
echo "   1. Visit the application URL"
echo "   2. Click 'S3 Connection Test'"
echo "   3. Should show: ✅ Connected to ai-prism-logs-600222957378-eu"
echo ""
