#!/bin/bash
# RQ Worker Startup Script for AI-Prism
# Replaces Celery worker with simpler RQ worker
# NO AWS signature expiration, NO complex S3 polling!

echo "=" * 70
echo "Starting RQ Worker for AI-Prism"
echo "=" * 70
echo ""

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis is not running!"
    echo "   Starting Redis..."
    brew services start redis
    sleep 2
fi

# Confirm Redis is available
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ ERROR: Redis is not accessible"
    echo "   Please start Redis manually: brew services start redis"
    exit 1
fi

echo ""
echo "Starting RQ workers..."
echo ""
echo "Queues:"
echo "  • analysis (5 min timeout) - Document section analysis"
echo "  • chat (2 min timeout) - Chat processing"
echo "  • monitoring (1 min timeout) - Health monitoring"
echo "  • default - General tasks"
echo ""

# Start RQ worker for all queues
# RQ will process jobs from these queues in order of priority
cd "$(dirname "$0")"

echo "💻 Worker command:"
echo "   rq worker analysis chat monitoring default --url redis://localhost:6379/0"
echo ""

# Start worker with all queues
# The worker will pick jobs from any of these queues
# ✅ OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES fixes macOS fork() issues with Objective-C runtime
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES rq worker analysis chat monitoring default --url redis://localhost:6379/0

# Note: To run multiple workers in parallel, use:
# rq worker analysis &
# rq worker chat &
# rq worker monitoring default &
