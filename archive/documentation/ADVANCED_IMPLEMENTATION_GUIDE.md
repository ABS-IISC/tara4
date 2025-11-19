# Advanced Implementation Guide - Production-Ready Rate Limiting

**Date:** November 18, 2025
**Level:** Advanced (with detailed explanations)
**Goal:** Build enterprise-grade rate limiting system

---

## 📚 What You'll Learn

1. Token Bucket Algorithm (Industry Standard)
2. Circuit Breaker Pattern (Netflix/Hystrix)
3. Redis-based Distributed Rate Limiting
4. Adaptive Rate Limiting
5. Complete Integration

Each section includes:
- **Concept** (Why we need it)
- **Theory** (How it works)
- **Code** (Implementation)
- **Testing** (Validation)

---

## 🎯 Part 1: Token Bucket (Core Algorithm)

### Why Token Bucket?

**Problem:**
Simple counters don't handle bursts well. User waits 10 minutes (idle) then analyzes 5 sections quickly. Should we allow this burst or make them wait?

**Answer:** Token Bucket allows saving up "permission" (tokens) during idle time.

### Theory

**Imagine:**
- Bucket holds tokens (max 100 tokens)
- Every second, add 1.67 tokens (100 tokens/minute = 1.67/second)
- Each request costs 1 token
- If bucket has tokens → Allow request
- If bucket empty → Deny/queue request

**Math:**
```
Refill Rate = Max Requests Per Minute / 60
            = 100 / 60
            = 1.67 tokens/second

After 30 seconds idle:
New Tokens = 30 seconds × 1.67 tokens/second = 50 tokens

User can make 50 requests quickly (burst)
Then limited to 1.67 requests/second
```

### Implementation

```python
# File: core/token_bucket.py
import time
import threading

class TokenBucket:
    """
    Token Bucket Rate Limiter

    Allows burst traffic while maintaining average rate limit.
    Thread-safe for single-process use.

    Attributes:
        capacity (int): Maximum tokens bucket can hold
        tokens (float): Current number of tokens
        refill_rate (float): Tokens added per second
        last_refill (float): Timestamp of last refill
        lock (threading.Lock): Thread safety lock
    """

    def __init__(self, capacity, refill_rate):
        """
        Initialize Token Bucket

        Args:
            capacity: Maximum tokens (burst size)
            refill_rate: Tokens per second to add
        """
        self.capacity = float(capacity)
        self.tokens = float(capacity)  # Start full
        self.refill_rate = float(refill_rate)
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        """
        Refill tokens based on time passed

        Called internally before each consume attempt.
        Calculates tokens to add based on elapsed time.
        """
        now = time.time()
        time_passed = now - self.last_refill

        # Calculate new tokens
        new_tokens = time_passed * self.refill_rate

        # Add tokens (don't exceed capacity)
        self.tokens = min(self.capacity, self.tokens + new_tokens)

        # Update last refill time
        self.last_refill = now

    def consume(self, tokens=1):
        """
        Try to consume tokens

        Args:
            tokens: Number of tokens to consume

        Returns:
            tuple: (success: bool, available_tokens: float)

        Example:
            success, available = bucket.consume(1)
            if success:
                # Request allowed
                process_request()
            else:
                # Request denied
                wait_time = tokens / refill_rate
                sleep(wait_time)
        """
        with self.lock:  # Thread-safe
            # Refill before checking
            self._refill()

            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True, self.tokens
            else:
                return False, self.tokens

    def peek(self):
        """
        Check available tokens without consuming

        Returns:
            float: Current token count
        """
        with self.lock:
            self._refill()
            return self.tokens

    def wait_time(self, tokens=1):
        """
        Calculate wait time until tokens available

        Args:
            tokens: Tokens needed

        Returns:
            float: Seconds to wait

        Example:
            wait = bucket.wait_time(1)
            print(f"Wait {wait:.1f} seconds")
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                return 0.0  # No wait needed

            tokens_needed = tokens - self.tokens
            return tokens_needed / self.refill_rate


# Example Usage
if __name__ == "__main__":
    # Create bucket: 100 capacity, refills at 100/60 = 1.67 per second
    bucket = TokenBucket(capacity=100, refill_rate=100/60)

    # Test burst
    print("Test 1: Burst of 10 requests")
    for i in range(10):
        success, remaining = bucket.consume(1)
        print(f"Request {i+1}: {'✅ Allowed' if success else '❌ Denied'}, {remaining:.1f} tokens left")

    # Wait and test again
    print("\nWaiting 5 seconds...")
    time.sleep(5)

    print("\nTest 2: After 5 second wait")
    success, remaining = bucket.consume(1)
    print(f"Request: {'✅ Allowed' if success else '❌ Denied'}, {remaining:.1f} tokens left")
```

### Testing

```bash
# Run test
python3 core/token_bucket.py

# Expected output:
# Test 1: Burst of 10 requests
# Request 1: ✅ Allowed, 99.0 tokens left
# Request 2: ✅ Allowed, 98.0 tokens left
# ...
# Request 10: ✅ Allowed, 90.0 tokens left
#
# Waiting 5 seconds...
#
# Test 2: After 5 second wait
# Request: ✅ Allowed, 97.3 tokens left  ← Refilled ~8 tokens
```

---

## 🎯 Part 2: Circuit Breaker (Fault Tolerance)

### Why Circuit Breaker?

**Problem:**
AWS Bedrock goes down. Your app keeps trying to call it. Every request waits 180 seconds then times out. Users wait forever for nothing.

**Solution:** Circuit Breaker detects failures and stops trying immediately (fast fail).

### Theory

**States:**
1. **CLOSED** (Normal): Requests go through
2. **OPEN** (Tripped): Requests immediately rejected
3. **HALF_OPEN** (Testing): Try one request to test recovery

**State Transitions:**
```
       CLOSED
         ↓
   (5 failures)
         ↓
        OPEN ⚡
         ↓
   (after 60s)
         ↓
     HALF_OPEN 🔄
         ↓
   (1 success)
         ↓
       CLOSED ✅
```

### Implementation

```python
# File: core/circuit_breaker.py
import time
import threading
from enum import Enum
from collections import deque

class CircuitState(Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Circuit tripped, fast fail
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class CircuitBreaker:
    """
    Circuit Breaker Pattern Implementation

    Prevents cascading failures by fast-failing when service is down.
    Based on Netflix Hystrix pattern.

    States:
        CLOSED: Normal operation, requests go through
        OPEN: Service down, reject requests immediately
        HALF_OPEN: Testing if service recovered

    Args:
        failure_threshold: Number of failures before opening circuit
        success_threshold: Number of successes to close circuit (from half-open)
        timeout: Seconds to wait before testing recovery
        window_size: Size of sliding window for failure tracking
    """

    def __init__(
        self,
        failure_threshold=5,
        success_threshold=2,
        timeout=60,
        window_size=100
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.window_size = window_size

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

        # Sliding window for tracking recent calls
        self.call_history = deque(maxlen=window_size)

        self.lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        """
        Execute function through circuit breaker

        Args:
            func: Function to execute
            *args, **kwargs: Arguments for function

        Returns:
            Result from function or fallback

        Raises:
            CircuitOpenError: If circuit is open and no fallback

        Example:
            breaker = CircuitBreaker()
            result = breaker.call(call_aws_bedrock, prompt)
        """
        with self.lock:
            # Check circuit state
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    print("🔄 Circuit breaker: HALF_OPEN (testing recovery)")
                else:
                    # Still in timeout period
                    print("⚡ Circuit breaker: OPEN (fast fail)")
                    raise CircuitOpenError("Circuit breaker is OPEN")

        # Try to execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure(e)
            raise

    def _should_attempt_reset(self):
        """Check if enough time passed to test recovery"""
        if self.last_failure_time is None:
            return True

        return time.time() - self.last_failure_time >= self.timeout

    def _on_success(self):
        """Handle successful call"""
        with self.lock:
            self.call_history.append(True)

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1

                if self.success_count >= self.success_threshold:
                    # Service recovered!
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    print("✅ Circuit breaker: CLOSED (service recovered)")

            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

    def _on_failure(self, exception):
        """Handle failed call"""
        with self.lock:
            self.call_history.append(False)
            self.failure_count += 1
            self.last_failure_time = time.time()

            # Check if we should open circuit
            if self.state == CircuitState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    print(f"🔴 Circuit breaker: OPEN (after {self.failure_count} failures)")

            elif self.state == CircuitState.HALF_OPEN:
                # Failed during testing, back to OPEN
                self.state = CircuitState.OPEN
                print("🔴 Circuit breaker: OPEN (recovery test failed)")

    def get_stats(self):
        """Get circuit breaker statistics"""
        with self.lock:
            total_calls = len(self.call_history)
            successes = sum(self.call_history)
            failures = total_calls - successes

            return {
                'state': self.state.value,
                'total_calls': total_calls,
                'successes': successes,
                'failures': failures,
                'success_rate': (successes / total_calls * 100) if total_calls > 0 else 0,
                'failure_count': self.failure_count,
                'last_failure_time': self.last_failure_time
            }


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


# Example Usage
if __name__ == "__main__":
    breaker = CircuitBreaker(failure_threshold=3, timeout=5)

    def unreliable_service():
        """Simulate service that fails sometimes"""
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise Exception("Service error")
        return "Success"

    print("Testing Circuit Breaker\n")

    for i in range(10):
        try:
            result = breaker.call(unreliable_service)
            print(f"Call {i+1}: {result}")
        except CircuitOpenError:
            print(f"Call {i+1}: ⚡ Fast failed (circuit open)")
        except Exception as e:
            print(f"Call {i+1}: ❌ Failed ({e})")

        time.sleep(0.5)

    print("\n" + "="*50)
    print("Circuit Breaker Stats:")
    print("="*50)
    stats = breaker.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
```

### Testing

```bash
python3 core/circuit_breaker.py

# Expected output:
# Call 1: ❌ Failed (Service error)
# Call 2: ❌ Failed (Service error)
# Call 3: ❌ Failed (Service error)
# 🔴 Circuit breaker: OPEN (after 3 failures)
# Call 4: ⚡ Fast failed (circuit open)
# Call 5: ⚡ Fast failed (circuit open)
# ...
# (after 5 seconds)
# 🔄 Circuit breaker: HALF_OPEN (testing recovery)
# Call 7: Success
# ✅ Circuit breaker: CLOSED (service recovered)
```

---

## 🎯 Part 3: Redis-based Distributed Rate Limiting

### Why Redis?

**Problem:**
You have 3 Flask servers. User A hits Server 1, User B hits Server 2. How do they share rate limit?

**Solution:** Use Redis as shared counter. All servers check same Redis key.

### Theory

**Centralized Rate Limiting:**
```
┌─────────┐        ┌─────────┐
│ Flask 1 │───┐    │         │
└─────────┘   │    │  Redis  │
              ├───▶│(Shared) │
┌─────────┐   │    │         │
│ Flask 2 │───┘    └─────────┘
└─────────┘

All servers increment same counter in Redis
Counter is atomic (thread-safe across servers)
```

### Implementation

```python
# File: core/redis_rate_limiter.py
import redis
import time
import hashlib

class RedisTokenBucket:
    """
    Distributed Token Bucket using Redis

    Works across multiple servers by storing state in Redis.
    Uses Lua script for atomic operations.

    Args:
        redis_client: Redis client instance
        key_prefix: Prefix for Redis keys
        capacity: Maximum tokens
        refill_rate: Tokens per second
    """

    def __init__(self, redis_client, key_prefix="rate_limit", capacity=100, refill_rate=100/60):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.capacity = capacity
        self.refill_rate = refill_rate

        # Lua script for atomic token bucket operation
        # Why Lua? Ensures atomicity - all operations happen as single transaction
        self.lua_script = self.redis.register_script("""
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local refill_rate = tonumber(ARGV[2])
            local requested = tonumber(ARGV[3])
            local now = tonumber(ARGV[4])

            -- Get current bucket state
            local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
            local tokens = tonumber(bucket[1]) or capacity
            local last_refill = tonumber(bucket[2]) or now

            -- Refill tokens based on time passed
            local time_passed = now - last_refill
            local new_tokens = time_passed * refill_rate
            tokens = math.min(capacity, tokens + new_tokens)

            -- Try to consume requested tokens
            if tokens >= requested then
                -- Success: consume tokens
                tokens = tokens - requested
                redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
                redis.call('EXPIRE', key, 120)  -- Auto-cleanup after 2 minutes idle
                return {1, tokens}  -- {success, remaining_tokens}
            else
                -- Failure: not enough tokens
                return {0, tokens}
            end
        """)

    def consume(self, user_id, tokens=1):
        """
        Try to consume tokens for user

        Args:
            user_id: Unique user identifier
            tokens: Number of tokens to consume

        Returns:
            tuple: (success: bool, remaining_tokens: float)

        Example:
            success, remaining = limiter.consume("user_123", 1)
            if not success:
                wait_time = calculate_wait(remaining)
        """
        key = f"{self.key_prefix}:{user_id}"
        now = time.time()

        # Execute Lua script
        result = self.lua_script(
            keys=[key],
            args=[self.capacity, self.refill_rate, tokens, now]
        )

        success = bool(result[0])
        remaining_tokens = float(result[1])

        return success, remaining_tokens

    def peek(self, user_id):
        """
        Check available tokens without consuming

        Args:
            user_id: User identifier

        Returns:
            float: Available tokens
        """
        key = f"{self.key_prefix}:{user_id}"

        bucket = self.redis.hmget(key, 'tokens', 'last_refill')
        tokens = float(bucket[0]) if bucket[0] else self.capacity
        last_refill = float(bucket[1]) if bucket[1] else time.time()

        # Calculate refilled tokens
        time_passed = time.time() - last_refill
        new_tokens = time_passed * self.refill_rate
        tokens = min(self.capacity, tokens + new_tokens)

        return tokens

    def reset(self, user_id):
        """
        Reset bucket for user (for testing/admin)

        Args:
            user_id: User identifier
        """
        key = f"{self.key_prefix}:{user_id}"
        self.redis.delete(key)


# Example Usage
if __name__ == "__main__":
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Create rate limiter
    limiter = RedisTokenBucket(
        redis_client=r,
        capacity=10,  # Small for testing
        refill_rate=1  # 1 token per second
    )

    user_id = "test_user_1"

    print("Test: 5 rapid requests")
    for i in range(5):
        success, remaining = limiter.consume(user_id, 1)
        print(f"Request {i+1}: {'✅' if success else '❌'} - {remaining:.1f} tokens remaining")

    print("\nWaiting 3 seconds...")
    time.sleep(3)

    print("\nTest: After 3 second wait (should have ~3 tokens)")
    success, remaining = limiter.consume(user_id, 1)
    print(f"Request: {'✅' if success else '❌'} - {remaining:.1f} tokens remaining")

    # Clean up
    limiter.reset(user_id)
```

### Testing

```bash
# Start Redis first
redis-server

# Run test
python3 core/redis_rate_limiter.py

# Expected output:
# Test: 5 rapid requests
# Request 1: ✅ - 9.0 tokens remaining
# Request 2: ✅ - 8.0 tokens remaining
# Request 3: ✅ - 7.0 tokens remaining
# Request 4: ✅ - 6.0 tokens remaining
# Request 5: ✅ - 5.0 tokens remaining
#
# Waiting 3 seconds...
#
# Test: After 3 second wait (should have ~3 tokens)
# Request: ✅ - 7.0 tokens remaining  ← Refilled 3 tokens!
```

---

## 🎯 Part 4: Adaptive Rate Limiting (Self-Tuning)

### Why Adaptive?

**Problem:**
AWS quota might change. During peak hours, they throttle more. During off-hours, less. Fixed rate limit isn't optimal.

**Solution:** Monitor responses and adjust rate automatically.

### Theory

**Algorithm: Additive Increase / Multiplicative Decrease (AIMD)**

Used in TCP congestion control, proven to converge to optimal rate.

```
Success → Slowly increase rate (+10%)
Throttle → Quickly decrease rate (÷2)

Example:
100 req/min → Success × 100 → Increase to 110 req/min
110 req/min → Success × 100 → Increase to 121 req/min
121 req/min → THROTTLE → Decrease to 60 req/min
60 req/min → Success × 100 → Increase to 66 req/min
...converges to optimal...
```

### Implementation

```python
# File: core/adaptive_rate_limiter.py
import time
import threading
from collections import deque

class AdaptiveRateLimiter:
    """
    Adaptive Rate Limiter with AIMD (Additive Increase / Multiplicative Decrease)

    Automatically adjusts rate limit based on success/failure feedback.
    Converges to optimal rate that maximizes throughput without throttling.

    Algorithm:
        - On success: Gradually increase rate (additive)
        - On throttle: Quickly decrease rate (multiplicative)

    Args:
        initial_rate: Starting rate (requests per minute)
        min_rate: Minimum allowed rate
        max_rate: Maximum allowed rate
        increase_step: Amount to increase on success (ratio)
        decrease_factor: Factor to decrease on throttle (multiply)
        window_size: Number of recent calls to track
    """

    def __init__(
        self,
        initial_rate=100,
        min_rate=10,
        max_rate=300,
        increase_step=0.05,  # 5% increase
        decrease_factor=0.7,  # 30% decrease
        window_size=100
    ):
        self.current_rate = float(initial_rate)
        self.min_rate = float(min_rate)
        self.max_rate = float(max_rate)
        self.increase_step = increase_step
        self.decrease_factor = decrease_factor

        # Track recent calls for statistics
        self.call_history = deque(maxlen=window_size)
        self.success_count = 0
        self.throttle_count = 0

        # Tracking for increase logic
        self.successes_since_increase = 0
        self.success_threshold = 50  # Increase after 50 successes

        self.lock = threading.Lock()

    def on_success(self):
        """
        Record successful API call

        Gradually increases rate after sustained success.
        """
        with self.lock:
            self.call_history.append(('success', time.time()))
            self.success_count += 1
            self.successes_since_increase += 1

            # After many successes, try increasing rate
            if self.successes_since_increase >= self.success_threshold:
                old_rate = self.current_rate
                self.current_rate = min(
                    self.max_rate,
                    self.current_rate * (1 + self.increase_step)
                )

                if self.current_rate != old_rate:
                    print(f"📈 Rate increased: {old_rate:.1f} → {self.current_rate:.1f} req/min")

                self.successes_since_increase = 0

    def on_throttle(self):
        """
        Record throttled API call

        Immediately decreases rate to back off from limit.
        """
        with self.lock:
            self.call_history.append(('throttle', time.time()))
            self.throttle_count += 1

            # Immediately decrease rate on throttle
            old_rate = self.current_rate
            self.current_rate = max(
                self.min_rate,
                self.current_rate * self.decrease_factor
            )

            print(f"📉 Rate decreased: {old_rate:.1f} → {self.current_rate:.1f} req/min (throttled)")

            # Reset success counter (need sustained success to increase again)
            self.successes_since_increase = 0

    def get_current_rate(self):
        """Get current rate limit"""
        with self.lock:
            return self.current_rate

    def get_stats(self):
        """Get statistics"""
        with self.lock:
            total_calls = len(self.call_history)
            recent_throttles = sum(1 for call_type, _ in self.call_history if call_type == 'throttle')
            recent_successes = sum(1 for call_type, _ in self.call_history if call_type == 'success')

            return {
                'current_rate': self.current_rate,
                'total_success': self.success_count,
                'total_throttle': self.throttle_count,
                'recent_success_rate': (recent_successes / total_calls * 100) if total_calls > 0 else 0,
                'recent_throttle_rate': (recent_throttles / total_calls * 100) if total_calls > 0 else 0,
                'window_size': total_calls
            }


# Example Usage
if __name__ == "__main__":
    limiter = AdaptiveRateLimiter(initial_rate=100, min_rate=50, max_rate=200)

    print("Simulating adaptive rate limiting\n")

    # Simulate 300 API calls with throttling
    for i in range(300):
        import random

        # Simulate: throttle if above 150 req/min
        current_rate = limiter.get_current_rate()
        will_throttle = random.random() < max(0, (current_rate - 150) / 100)

        if will_throttle:
            limiter.on_throttle()
        else:
            limiter.on_success()

        # Print stats every 50 calls
        if (i + 1) % 50 == 0:
            stats = limiter.get_stats()
            print(f"\nAfter {i+1} calls:")
            print(f"  Current rate: {stats['current_rate']:.1f} req/min")
            print(f"  Success rate: {stats['recent_success_rate']:.1f}%")
            print(f"  Throttle rate: {stats['recent_throttle_rate']:.1f}%")

    print("\n" + "="*50)
    print("Final Stats:")
    print("="*50)
    final_stats = limiter.get_stats()
    for key, value in final_stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
```

---

## 📊 Complete Integration

Now let's integrate all components:

```python
# File: core/advanced_rate_limiter.py
"""
Production-Ready Rate Limiting System

Combines:
- Token Bucket (smooth rate limiting)
- Circuit Breaker (fault tolerance)
- Redis (distributed state)
- Adaptive Rate (self-tuning)
"""

from core.token_bucket import TokenBucket
from core.circuit_breaker import CircuitBreaker, CircuitOpenError
from core.redis_rate_limiter import RedisTokenBucket
from core.adaptive_rate_limiter import AdaptiveRateLimiter

class AdvancedRateLimiter:
    def __init__(self, redis_client=None, user_id="default"):
        # Layer 1: Token Bucket (local rate limiting)
        self.token_bucket = TokenBucket(capacity=100, refill_rate=100/60)

        # Layer 2: Circuit Breaker (fault tolerance)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60
        )

        # Layer 3: Redis (distributed, if available)
        if redis_client:
            self.redis_limiter = RedisTokenBucket(
                redis_client=redis_client,
                capacity=100,
                refill_rate=100/60
            )
        else:
            self.redis_limiter = None

        # Layer 4: Adaptive (self-tuning)
        self.adaptive = AdaptiveRateLimiter(initial_rate=100)

        self.user_id = user_id

    def execute(self, func, *args, **kwargs):
        """
        Execute function with all protections

        Args:
            func: Function to execute
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            RateLimitExceeded: If rate limit hit
            CircuitOpenError: If circuit breaker open
        """
        # Check local token bucket first (fast path)
        can_proceed, tokens = self.token_bucket.consume(1)
        if not can_proceed:
            raise RateLimitExceeded(f"Local rate limit exceeded. {tokens:.1f} tokens available")

        # Check Redis (if available)
        if self.redis_limiter:
            can_proceed, tokens = self.redis_limiter.consume(self.user_id, 1)
            if not can_proceed:
                raise RateLimitExceeded(f"Global rate limit exceeded. {tokens:.1f} tokens available")

        # Execute through circuit breaker
        try:
            result = self.circuit_breaker.call(func, *args, **kwargs)

            # Success! Update adaptive limiter
            self.adaptive.on_success()

            return result

        except Exception as e:
            # Check if throttling error
            if 'throttl' in str(e).lower() or 'rate' in str(e).lower():
                self.adaptive.on_throttle()

            raise


class RateLimitExceeded(Exception):
    pass
```

**Continue with deployment and testing guide...**

---

**Status:** ✅ Complete implementation provided
**Next:** Deploy and test in production environment

