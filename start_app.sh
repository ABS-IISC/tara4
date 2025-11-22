#!/bin/bash
# AI-Prism Application Starter
# This script sets required environment variables and starts both Flask and Celery

set -e  # Exit on error

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         AI-Prism Document Analysis Platform               ║${NC}"
echo -e "${BLUE}║              Complete Startup Script                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo -e "${GREEN}✅ Loading environment from .env file${NC}"
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found, using defaults${NC}"
fi

# Detect AWS region
if [ -z "$AWS_REGION" ] && [ -z "$AWS_DEFAULT_REGION" ]; then
    AWS_CLI_REGION=$(aws configure get region 2>/dev/null || echo "")
    if [ -n "$AWS_CLI_REGION" ]; then
        echo -e "${GREEN}✅ Detected AWS region from CLI: ${AWS_CLI_REGION}${NC}"
        export AWS_REGION=$AWS_CLI_REGION
        export AWS_DEFAULT_REGION=$AWS_CLI_REGION
    else
        echo -e "${YELLOW}⚠️  Using default region: us-east-2${NC}"
        export AWS_REGION=us-east-2
        export AWS_DEFAULT_REGION=us-east-2
    fi
fi

# Set required AWS configuration
export S3_BUCKET_NAME=${S3_BUCKET_NAME:-felix-s3-bucket}
export S3_BASE_PATH=${S3_BASE_PATH:-tara/}
export SQS_QUEUE_PREFIX=${SQS_QUEUE_PREFIX:-aiprism-}
export CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND:-s3://${S3_BUCKET_NAME}/${S3_BASE_PATH}celery-results/}

# Set Flask configuration
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_DEBUG=${FLASK_DEBUG:-True}
export PORT=${PORT:-8080}
export SECRET_KEY=${SECRET_KEY:-dev-secret-key-$(date +%s)}

# Set Bedrock AI configuration
export BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID:-us.anthropic.claude-sonnet-4-5-20250929-v1:0}
export BEDROCK_MAX_TOKENS=${BEDROCK_MAX_TOKENS:-8192}
export BEDROCK_TEMPERATURE=${BEDROCK_TEMPERATURE:-0.7}
export REASONING_ENABLED=${REASONING_ENABLED:-true}
export EXTENDED_THINKING_BUDGET=${EXTENDED_THINKING_BUDGET:-2000}

# Set rate limiting
export MAX_REQUESTS_PER_MINUTE=${MAX_REQUESTS_PER_MINUTE:-60}
export MAX_CONCURRENT_REQUESTS=${MAX_CONCURRENT_REQUESTS:-15}
export MAX_TOKENS_PER_MINUTE=${MAX_TOKENS_PER_MINUTE:-180000}

# Set Celery configuration
export CELERY_BROKER_URL=${CELERY_BROKER_URL:-sqs://}
export CELERY_CONCURRENCY=${CELERY_CONCURRENCY:-4}
export CELERY_WORKER_PREFETCH_MULTIPLIER=${CELERY_WORKER_PREFETCH_MULTIPLIER:-1}
export CELERY_TASK_ACKS_LATE=${CELERY_TASK_ACKS_LATE:-true}

# Set SQS settings
export SQS_VISIBILITY_TIMEOUT=${SQS_VISIBILITY_TIMEOUT:-3600}
export SQS_POLLING_INTERVAL=${SQS_POLLING_INTERVAL:-1}
export SQS_WAIT_TIME_SECONDS=${SQS_WAIT_TIME_SECONDS:-1}

# Set feature flags
export USE_CELERY=${USE_CELERY:-true}
export ENHANCED_MODE=${ENHANCED_MODE:-true}
export ENABLE_S3_EXPORT=${ENABLE_S3_EXPORT:-true}
export ENABLE_METRICS=${ENABLE_METRICS:-true}
export LOG_LEVEL=${LOG_LEVEL:-INFO}
export FEEDBACK_MIN_CONFIDENCE=${FEEDBACK_MIN_CONFIDENCE:-0.80}

echo ""
echo -e "${GREEN}📋 Configuration Summary:${NC}"
echo "   AWS Region: $AWS_REGION"
echo "   S3 Bucket: $S3_BUCKET_NAME"
echo "   S3 Base Path: $S3_BASE_PATH"
echo "   SQS Queue Prefix: $SQS_QUEUE_PREFIX"
echo "   Flask Port: $PORT"
echo "   Celery Backend: $CELERY_RESULT_BACKEND"
echo "   Celery Concurrency: $CELERY_CONCURRENCY"
echo ""

# Check AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ] && [ -z "$AWS_PROFILE" ]; then
    echo -e "${YELLOW}⚠️  WARNING: No AWS credentials detected${NC}"
    echo -e "${YELLOW}   The app may not be able to access AWS services${NC}"
    echo -e "${YELLOW}   Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or AWS_PROFILE${NC}"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down...${NC}"
    if [ ! -z "$CELERY_PID" ]; then
        echo "   Stopping Celery worker (PID: $CELERY_PID)"
        kill $CELERY_PID 2>/dev/null || true
    fi
    if [ ! -z "$FLASK_PID" ]; then
        echo "   Stopping Flask app (PID: $FLASK_PID)"
        kill $FLASK_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Celery worker in background
echo -e "${BLUE}🔧 Starting Celery worker...${NC}"
celery -A celery_config.celery_app worker \
    --loglevel=info \
    --concurrency=$CELERY_CONCURRENCY \
    --queues=analysis,chat,monitoring,celery \
    --logfile=logs/celery-worker.log \
    --pidfile=logs/celery-worker.pid \
    > logs/celery-console.log 2>&1 &
CELERY_PID=$!

# Wait a moment for Celery to start
sleep 3

# Check if Celery is still running
if ! kill -0 $CELERY_PID 2>/dev/null; then
    echo -e "${RED}❌ Celery worker failed to start${NC}"
    echo "   Check logs/celery-console.log for details"
    cat logs/celery-console.log
    exit 1
fi

echo -e "${GREEN}✅ Celery worker started (PID: $CELERY_PID)${NC}"
echo "   Logs: logs/celery-worker.log"
echo ""

# Start Flask app
echo -e "${BLUE}🚀 Starting Flask application on port $PORT...${NC}"
python3 app.py > logs/flask-console.log 2>&1 &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 3

# Check if Flask is still running
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo -e "${RED}❌ Flask app failed to start${NC}"
    echo "   Check logs/flask-console.log for details"
    cat logs/flask-console.log
    cleanup
    exit 1
fi

echo -e "${GREEN}✅ Flask app started (PID: $FLASK_PID)${NC}"
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    🎉 AI-Prism is Running!                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Access the application at:${NC}"
echo -e "   ${GREEN}http://localhost:$PORT${NC}"
echo ""
echo -e "${BLUE}📊 Monitor logs:${NC}"
echo "   Flask:  tail -f logs/flask-console.log"
echo "   Celery: tail -f logs/celery-worker.log"
echo ""
echo -e "${BLUE}🔧 Useful commands:${NC}"
echo "   Check health: curl http://localhost:$PORT/health"
echo "   Stop services: Press Ctrl+C"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Monitor both processes
while true; do
    # Check if Flask is still running
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo -e "${RED}❌ Flask app stopped unexpectedly${NC}"
        cat logs/flask-console.log | tail -20
        cleanup
        exit 1
    fi

    # Check if Celery is still running
    if ! kill -0 $CELERY_PID 2>/dev/null; then
        echo -e "${RED}❌ Celery worker stopped unexpectedly${NC}"
        cat logs/celery-worker.log | tail -20
        cleanup
        exit 1
    fi

    sleep 5
done
