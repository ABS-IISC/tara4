#!/bin/bash

# TARA ECR Deployment Script
# Builds and pushes TARA application to ECR

set -e

ECR_URI="758897368787.dkr.ecr.us-east-1.amazonaws.com/tara"
AWS_REGION="us-east-1"
IMAGE_TAG="latest"

echo "========================================"
echo "TARA ECR Deployment Script"
echo "========================================"

echo "Step 1: Building Docker image..."
docker build -t tara-app:$IMAGE_TAG .

echo "Step 2: Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

echo "Step 3: Tagging image for ECR..."
docker tag tara-app:$IMAGE_TAG $ECR_URI:$IMAGE_TAG

echo "Step 4: Pushing image to ECR..."
docker push $ECR_URI:$IMAGE_TAG

echo "========================================"
echo "SUCCESS: TARA deployed to ECR!"
echo "ECR URI: $ECR_URI:$IMAGE_TAG"
echo "========================================"
echo ""
echo "Next steps for AWS App Runner:"
echo "1. Go to AWS App Runner console"
echo "2. Create service with ECR image: $ECR_URI:$IMAGE_TAG"
echo "3. Set port to 8000"
echo "4. Add environment variables:"
echo "   - AWS_DEFAULT_REGION=us-east-1"
echo "   - PORT=8000"
echo "========================================"