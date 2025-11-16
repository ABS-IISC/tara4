#!/bin/bash

# TARA Application Deployment Script for AWS App Runner via ECR
# Usage: ./deploy.sh [region] [repository-name]

set -e

# Configuration
AWS_REGION=${1:-us-east-1}
ECR_REPOSITORY=${2:-tara-app}
IMAGE_TAG=${3:-latest}
APP_NAME="tara-document-analyzer"

echo "🚀 Starting TARA deployment to AWS App Runner..."
echo "Region: $AWS_REGION"
echo "ECR Repository: $ECR_REPOSITORY"
echo "Image Tag: $IMAGE_TAG"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"

echo "📦 Building Docker image..."
docker build -t $ECR_REPOSITORY:$IMAGE_TAG .

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

echo "🏷️ Tagging image..."
docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_URI:$IMAGE_TAG

echo "⬆️ Pushing to ECR..."
docker push $ECR_URI:$IMAGE_TAG

echo "✅ Deployment complete!"
echo "ECR Image URI: $ECR_URI:$IMAGE_TAG"
echo ""
echo "Next steps:"
echo "1. Go to AWS App Runner console"
echo "2. Create new service using ECR image: $ECR_URI:$IMAGE_TAG"
echo "3. Configure environment variables for AWS Bedrock access"