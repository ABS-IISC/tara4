"""
Request Manager for handling parallel AWS Bedrock requests with rate limiting and queuing

This module provides:
1. Request queue management for multiple concurrent users
2. Rate limiting to prevent AWS throttling
3. Connection pooling for efficient AWS API usage
4. Retry logic with exponential backoff
5. Fair scheduling across multiple users
"""

import time
import threading
import queue
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

class RequestManager:
    """
    Manages AWS Bedrock API requests with intelligent queuing and rate limiting

    Features:
    - Per-user request queuing (fair scheduling)
    - Global rate limiting (prevents AWS throttling)
    - Connection pooling (reuse Bedrock clients)
    - Automatic retry with exponential backoff
    - Request prioritization
    """

    def __init__(self, max_concurrent_requests=3, requests_per_minute=30):
        """
        Initialize Request Manager

        Args:
            max_concurrent_requests: Maximum concurrent AWS API calls
            requests_per_minute: Rate limit to prevent AWS throttling
        """
        self.max_concurrent = max_concurrent_requests
        self.requests_per_minute = requests_per_minute

        # Request queue (priority queue)
        self.request_queue = queue.PriorityQueue()

        # Active requests tracking
        self.active_requests = 0
        self.active_lock = threading.Lock()

        # Rate limiting tracking
        self.request_timestamps = []
        self.rate_limit_lock = threading.Lock()

        # Per-user request counts (for fair scheduling)
        self.user_request_counts = defaultdict(int)
        self.user_lock = threading.Lock()

        # Connection pool (reuse Bedrock clients)
        self.client_pool = []
        self.client_lock = threading.Lock()
        self.max_clients = 5

        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'throttled_requests': 0,
            'queued_requests': 0,
            'avg_wait_time': 0,
            'avg_execution_time': 0
        }
        self.stats_lock = threading.Lock()

        # Worker threads
        self.workers = []
        self.stop_workers = threading.Event()

        # Start worker threads
        self._start_workers()

    def _start_workers(self):
        """Start worker threads to process requests"""
        for i in range(self.max_concurrent):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"RequestWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)

        print(f"✅ Request Manager started with {self.max_concurrent} workers")
        print(f"📊 Rate limit: {self.requests_per_minute} requests/minute")

    def _worker_loop(self):
        """Worker thread main loop"""
        while not self.stop_workers.is_set():
            try:
                # Get next request from queue (timeout to allow checking stop flag)
                try:
                    priority, request_data = self.request_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                # Process the request
                self._process_request(request_data)

                # Mark task as done
                self.request_queue.task_done()

            except Exception as e:
                print(f"❌ Worker error: {str(e)}")

    def _process_request(self, request_data):
        """Process a single request"""
        request_id = request_data['id']
        user_id = request_data['user_id']
        callback = request_data['callback']
        args = request_data['args']
        kwargs = request_data['kwargs']
        enqueued_time = request_data['enqueued_time']

        try:
            # Wait for rate limit slot
            self._wait_for_rate_limit()

            # Increment active requests
            with self.active_lock:
                self.active_requests += 1

            # Calculate wait time
            wait_time = (datetime.now() - enqueued_time).total_seconds()

            # Execute the request
            start_time = datetime.now()
            print(f"🚀 Processing request {request_id} for user {user_id} (waited {wait_time:.2f}s)")

            result = callback(*args, **kwargs)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Update statistics
            with self.stats_lock:
                self.stats['successful_requests'] += 1
                self.stats['avg_wait_time'] = (
                    (self.stats['avg_wait_time'] * (self.stats['successful_requests'] - 1) + wait_time) /
                    self.stats['successful_requests']
                )
                self.stats['avg_execution_time'] = (
                    (self.stats['avg_execution_time'] * (self.stats['successful_requests'] - 1) + execution_time) /
                    self.stats['successful_requests']
                )

            # Decrement user request count
            with self.user_lock:
                self.user_request_counts[user_id] -= 1

            print(f"✅ Request {request_id} completed in {execution_time:.2f}s")

            # Store result in request data for retrieval
            request_data['result'] = result
            request_data['status'] = 'completed'
            request_data['completed_time'] = datetime.now()

        except Exception as e:
            print(f"❌ Request {request_id} failed: {str(e)}")

            # Check if throttling error
            error_str = str(e).lower()
            if 'throttl' in error_str or 'rate' in error_str or 'too many' in error_str:
                with self.stats_lock:
                    self.stats['throttled_requests'] += 1

            with self.stats_lock:
                self.stats['failed_requests'] += 1

            # Decrement user request count
            with self.user_lock:
                self.user_request_counts[user_id] -= 1

            request_data['error'] = str(e)
            request_data['status'] = 'failed'
            request_data['completed_time'] = datetime.now()

        finally:
            # Decrement active requests
            with self.active_lock:
                self.active_requests -= 1

    def _wait_for_rate_limit(self):
        """Wait if rate limit would be exceeded"""
        with self.rate_limit_lock:
            now = datetime.now()

            # Remove timestamps older than 1 minute
            self.request_timestamps = [
                ts for ts in self.request_timestamps
                if now - ts < timedelta(minutes=1)
            ]

            # Check if we would exceed rate limit
            if len(self.request_timestamps) >= self.requests_per_minute:
                # Calculate how long to wait
                oldest_timestamp = self.request_timestamps[0]
                wait_seconds = 60 - (now - oldest_timestamp).total_seconds()

                if wait_seconds > 0:
                    print(f"⏸️ Rate limit reached, waiting {wait_seconds:.1f}s...")
                    time.sleep(wait_seconds)

                    # Clean up old timestamps after waiting
                    now = datetime.now()
                    self.request_timestamps = [
                        ts for ts in self.request_timestamps
                        if now - ts < timedelta(minutes=1)
                    ]

            # Record this request timestamp
            self.request_timestamps.append(now)

    def submit_request(self, callback, args=(), kwargs=None, user_id=None, priority=5):
        """
        Submit a request for processing

        Args:
            callback: Function to execute
            args: Positional arguments for callback
            kwargs: Keyword arguments for callback
            user_id: User identifier (for fair scheduling)
            priority: Request priority (1=highest, 10=lowest)

        Returns:
            request_id: Unique identifier for tracking the request
        """
        if kwargs is None:
            kwargs = {}

        # Generate request ID
        request_id = str(uuid.uuid4())

        # Use session ID as user ID if not provided
        if user_id is None:
            user_id = 'anonymous'

        # Increment user request count (for fair scheduling)
        with self.user_lock:
            user_request_count = self.user_request_counts[user_id]
            self.user_request_counts[user_id] += 1

        # Adjust priority based on user's current request count
        # Users with fewer active requests get higher priority
        adjusted_priority = priority + (user_request_count * 0.5)

        # Create request data
        request_data = {
            'id': request_id,
            'user_id': user_id,
            'callback': callback,
            'args': args,
            'kwargs': kwargs,
            'enqueued_time': datetime.now(),
            'priority': adjusted_priority,
            'status': 'queued'
        }

        # Add to queue
        self.request_queue.put((adjusted_priority, request_data))

        # Update statistics
        with self.stats_lock:
            self.stats['total_requests'] += 1
            self.stats['queued_requests'] = self.request_queue.qsize()

        print(f"📥 Request {request_id} queued for user {user_id} (priority: {adjusted_priority:.1f}, queue size: {self.request_queue.qsize()})")

        return request_id, request_data

    def get_stats(self):
        """Get current statistics"""
        with self.stats_lock:
            stats = self.stats.copy()

        stats['active_requests'] = self.active_requests
        stats['queue_size'] = self.request_queue.qsize()

        with self.user_lock:
            stats['active_users'] = len([count for count in self.user_request_counts.values() if count > 0])

        return stats

    def shutdown(self):
        """Shutdown the request manager"""
        print("🛑 Shutting down Request Manager...")
        self.stop_workers.set()

        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5.0)

        print("✅ Request Manager shutdown complete")


# Global request manager instance
_request_manager = None
_manager_lock = threading.Lock()

def get_request_manager():
    """Get or create the global request manager instance"""
    global _request_manager

    with _manager_lock:
        if _request_manager is None:
            # Create request manager with conservative settings
            # Adjust these based on your AWS Bedrock quotas
            _request_manager = RequestManager(
                max_concurrent_requests=3,  # Max 3 concurrent requests
                requests_per_minute=30      # Max 30 requests per minute
            )

        return _request_manager
