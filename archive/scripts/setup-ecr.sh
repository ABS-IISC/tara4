#!/bin/bash

# ECR Repository Setup Script
# Usage: ./setup-ecr.sh [region] [repository-name]

set -e

AWS_REGION=${1:-us-east-1}
ECR_REPOSITORY=${2:-tara-app}

echo "🏗️ Setting up ECR repository..."

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null || {
    echo "Creating ECR repository: $ECR_REPOSITORY"
    aws ecr create-repository \
        --repository-name $ECR_REPOSITORY \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true
}

# Set lifecycle policy to manage image retention
aws ecr put-lifecycle-policy \
    --repository-name $ECR_REPOSITORY \
    --region $AWS_REGION \
    --lifecycle-policy-text '{
        "rules": [
            {
                "rulePriority": 1,
                "description": "Keep last 10 images",
                "selection": {
                    "tagStatus": "any",
                    "countType": "imageCountMoreThan",
                    "countNumber": 10
                },
                "action": {
                    "type": "expire"
                }
            }
        ]
    }'

echo "✅ ECR repository setup complete!"
echo "Repository URI: $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"