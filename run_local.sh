#!/bin/bash
# Local Development Startup Script for AI-Prism
# This script sets up environment variables and starts the Flask app

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting AI-Prism (Local Development Mode)${NC}"
echo ""

# Check if .env file exists
if [ -f .env ]; then
    echo -e "${GREEN}✅ Loading environment variables from .env file${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found, using defaults${NC}"
    echo -e "${YELLOW}   Copy .env.example to .env and update with your values${NC}"
    echo ""
fi

# Detect AWS region from AWS CLI config if not set
if [ -z "$AWS_REGION" ] && [ -z "$AWS_DEFAULT_REGION" ]; then
    # Try to get region from AWS CLI config
    AWS_CLI_REGION=$(aws configure get region 2>/dev/null)
    if [ -n "$AWS_CLI_REGION" ]; then
        echo -e "${GREEN}✅ Detected AWS region from CLI profile: $AWS_CLI_REGION${NC}"
        export AWS_REGION=$AWS_CLI_REGION
        export AWS_DEFAULT_REGION=$AWS_CLI_REGION
    else
        echo -e "${YELLOW}⚠️  No AWS region detected, using default: us-east-2${NC}"
        export AWS_REGION=us-east-2
        export AWS_DEFAULT_REGION=us-east-2
    fi
else
    # Use existing region
    export AWS_REGION=${AWS_REGION:-us-east-2}
    export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-${AWS_REGION}}
fi
export S3_BUCKET_NAME=${S3_BUCKET_NAME:-felix-s3-bucket}
export S3_BASE_PATH=${S3_BASE_PATH:-tara/}
export SQS_QUEUE_PREFIX=${SQS_QUEUE_PREFIX:-aiprism-}

export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_DEBUG=${FLASK_DEBUG:-True}
export PORT=${PORT:-8080}
export SECRET_KEY=${SECRET_KEY:-dev-secret-key-change-in-production}

export BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID:-us.anthropic.claude-sonnet-4-5-20250929-v1:0}
export BEDROCK_MAX_TOKENS=${BEDROCK_MAX_TOKENS:-8192}
export BEDROCK_TEMPERATURE=${BEDROCK_TEMPERATURE:-0.7}
export REASONING_ENABLED=${REASONING_ENABLED:-true}
export EXTENDED_THINKING_BUDGET=${EXTENDED_THINKING_BUDGET:-2000}

export MAX_REQUESTS_PER_MINUTE=${MAX_REQUESTS_PER_MINUTE:-60}
export MAX_CONCURRENT_REQUESTS=${MAX_CONCURRENT_REQUESTS:-15}
export MAX_TOKENS_PER_MINUTE=${MAX_TOKENS_PER_MINUTE:-180000}

export CELERY_BROKER_URL=${CELERY_BROKER_URL:-sqs://}
export CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND:-s3://felix-s3-bucket/tara/celery-results/}
export CELERY_CONCURRENCY=${CELERY_CONCURRENCY:-8}
export CELERY_WORKER_PREFETCH_MULTIPLIER=${CELERY_WORKER_PREFETCH_MULTIPLIER:-1}
export CELERY_TASK_ACKS_LATE=${CELERY_TASK_ACKS_LATE:-true}
export CELERY_WORKER_MAX_TASKS_PER_CHILD=${CELERY_WORKER_MAX_TASKS_PER_CHILD:-1000}

export SQS_VISIBILITY_TIMEOUT=${SQS_VISIBILITY_TIMEOUT:-3600}
export SQS_POLLING_INTERVAL=${SQS_POLLING_INTERVAL:-1}
export SQS_WAIT_TIME_SECONDS=${SQS_WAIT_TIME_SECONDS:-1}

export S3_CELERY_RESULT_EXPIRES=${S3_CELERY_RESULT_EXPIRES:-604800}

export ENABLE_METRICS=${ENABLE_METRICS:-true}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

export FEEDBACK_MIN_CONFIDENCE=${FEEDBACK_MIN_CONFIDENCE:-0.80}

export USE_CELERY=${USE_CELERY:-true}
export ENHANCED_MODE=${ENHANCED_MODE:-true}
export ENABLE_S3_EXPORT=${ENABLE_S3_EXPORT:-true}

echo -e "${GREEN}📋 Configuration:${NC}"
echo "   AWS Region: $AWS_REGION"
echo "   S3 Bucket: $S3_BUCKET_NAME"
echo "   S3 Path: $S3_BASE_PATH"
echo "   SQS Prefix: $SQS_QUEUE_PREFIX"
echo "   Flask Port: $PORT"
echo "   Celery Backend: $CELERY_RESULT_BACKEND"
echo ""

# Check AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ] && [ -z "$AWS_PROFILE" ]; then
    echo -e "${YELLOW}⚠️  WARNING: No AWS credentials found${NC}"
    echo -e "${YELLOW}   Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or AWS_PROFILE${NC}"
    echo ""
fi

# Start the Flask app
echo -e "${GREEN}🎯 Starting Flask application on port $PORT${NC}"
echo ""

python3 app.py
