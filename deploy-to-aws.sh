#!/bin/bash

# AI-Prism Elastic Beanstalk Deployment Script
# This script deploys the new region-agnostic package to AWS

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "  AI-PRISM DEPLOYMENT TO ELASTIC BEANSTALK"
echo "  Region: eu-north-1 (Europe - Stockholm)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Configuration
APP_NAME="AI_prism"
ENV_NAME="AI_prism-env"
REGION="eu-north-1"
PACKAGE="ai-prism-eb-final.zip"
VERSION_LABEL="v3-final-$(date +%Y%m%d-%H%M%S)"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "YOUR-ACCOUNT-ID")

echo "📦 Package Details:"
echo "   File: $PACKAGE"
echo "   Size: $(ls -lh $PACKAGE | awk '{print $5}')"
echo "   MD5:  $(md5 -q $PACKAGE 2>/dev/null || md5sum $PACKAGE | awk '{print $1}')"
echo ""

# Check if package exists
if [ ! -f "$PACKAGE" ]; then
    echo "❌ ERROR: Package file not found: $PACKAGE"
    exit 1
fi

echo "✅ Package found"
echo ""

# Step 1: Upload to S3
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Uploading package to S3..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

S3_BUCKET="elasticbeanstalk-$REGION-$ACCOUNT_ID"
echo "Uploading to: s3://$S3_BUCKET/$PACKAGE"

if aws s3 cp "$PACKAGE" "s3://$S3_BUCKET/$PACKAGE" --region "$REGION"; then
    echo "✅ Upload successful"
else
    echo "❌ Upload failed"
    exit 1
fi
echo ""

# Step 2: Create Application Version
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Creating application version..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Version: $VERSION_LABEL"

if aws elasticbeanstalk create-application-version \
    --application-name "$APP_NAME" \
    --version-label "$VERSION_LABEL" \
    --source-bundle "S3Bucket=$S3_BUCKET,S3Key=$PACKAGE" \
    --region "$REGION" \
    --description "Region-agnostic deployment with correct S3 configuration" \
    > /dev/null; then
    echo "✅ Application version created"
else
    echo "❌ Failed to create application version"
    exit 1
fi
echo ""

# Step 3: Deploy to Environment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Deploying to environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Environment: $ENV_NAME"

if aws elasticbeanstalk update-environment \
    --application-name "$APP_NAME" \
    --environment-name "$ENV_NAME" \
    --version-label "$VERSION_LABEL" \
    --region "$REGION" \
    > /dev/null; then
    echo "✅ Deployment initiated"
else
    echo "❌ Failed to initiate deployment"
    exit 1
fi
echo ""

# Step 4: Monitor Deployment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Monitoring deployment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏱️  Deployment typically takes 7-12 minutes"
echo "📊 Check progress at: https://console.aws.amazon.com/elasticbeanstalk/"
echo ""

# Poll for deployment status
MAX_WAIT=720  # 12 minutes
ELAPSED=0
INTERVAL=30

while [ $ELAPSED -lt $MAX_WAIT ]; do
    STATUS=$(aws elasticbeanstalk describe-environments \
        --application-name "$APP_NAME" \
        --environment-names "$ENV_NAME" \
        --region "$REGION" \
        --query 'Environments[0].Status' \
        --output text 2>/dev/null || echo "Unknown")
    
    HEALTH=$(aws elasticbeanstalk describe-environments \
        --application-name "$APP_NAME" \
        --environment-names "$ENV_NAME" \
        --region "$REGION" \
        --query 'Environments[0].Health' \
        --output text 2>/dev/null || echo "Unknown")
    
    echo "[$(date +%H:%M:%S)] Status: $STATUS | Health: $HEALTH"
    
    if [ "$STATUS" = "Ready" ] && [ "$HEALTH" = "Green" ]; then
        echo ""
        echo "✅ Deployment completed successfully!"
        break
    fi
    
    if [ "$STATUS" = "Ready" ] && [ "$HEALTH" = "Red" ]; then
        echo ""
        echo "⚠️  Deployment completed but health is RED"
        echo "   Check logs: aws elasticbeanstalk retrieve-environment-info --environment-name $ENV_NAME --region $REGION"
        break
    fi
    
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  DEPLOYMENT SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get environment URL
ENV_URL=$(aws elasticbeanstalk describe-environments \
    --application-name "$APP_NAME" \
    --environment-names "$ENV_NAME" \
    --region "$REGION" \
    --query 'Environments[0].CNAME' \
    --output text 2>/dev/null || echo "Unknown")

echo "Application:  $APP_NAME"
echo "Environment:  $ENV_NAME"
echo "Version:      $VERSION_LABEL"
echo "Region:       $REGION"
echo "URL:          https://$ENV_URL"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  POST-DEPLOYMENT TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test health endpoint
echo "Testing health endpoint..."
if curl -s "https://$ENV_URL/health" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "⚠️  Health check failed or unexpected response"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Test your application:"
echo "   → Open: https://$ENV_URL"
echo "   → Upload a document"
echo "   → Analyze with AI (should work without session errors)"
echo "   → Export to S3 (should work with ai.prism bucket)"
echo ""
echo "2. View deployment logs:"
echo "   → AWS Console: https://console.aws.amazon.com/elasticbeanstalk/"
echo "   → Or run: aws elasticbeanstalk retrieve-environment-info \\"
echo "             --environment-name $ENV_NAME --region $REGION"
echo ""
echo "3. If issues occur:"
echo "   → Check DEPLOY_NOW.txt for troubleshooting"
echo "   → Deployment auto-rollsback on failure"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "  Deployment script completed!"
echo "════════════════════════════════════════════════════════════════"
