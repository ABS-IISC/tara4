"""
Multi-Model Manager V2 with Per-Request Isolation
Handles throttling with adaptive cooldowns while maintaining user independence
"""
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock

class ModelManagerV2:
    """
    Improved model manager with per-request isolation

    Key Features:
    - Each request tries primary model first (user independence)
    - Adaptive cooldowns based on throttle frequency
    - Short cooldowns prevent retry storms
    - No global model blocking
    - Thread-safe for concurrent requests
    """

    def __init__(self):
        """Initialize model manager with available models"""

        # Define all available Claude models in priority order
        self.models = self._load_models()

        # Track throttle events per model (for statistics only)
        self.throttle_events = defaultdict(list)  # {model_id: [timestamp1, timestamp2, ...]}
        self.success_count = defaultdict(int)
        self.total_attempts = defaultdict(int)

        # Adaptive cooldown tracking
        self.recent_throttles = defaultdict(list)  # {model_id: [timestamp1, timestamp2, ...]}
        self.cooldown_until = {}  # {model_id: datetime} - when cooldown expires

        # Thread safety for concurrent requests
        self.lock = Lock()

        print(f"✅ ModelManagerV2 initialized with {len(self.models)} models")
        for i, model in enumerate(self.models, 1):
            print(f"   {i}. {model['name']} (Priority {model['priority']})")
        print(f"🔄 Per-request isolation enabled - each user tries primary model first")

    def _load_models(self):
        """Load model configuration from environment or use defaults"""

        # Get primary model from environment
        primary_model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')

        # Define all available models with priorities
        models = [
            {
                'id': primary_model_id,
                'name': 'Claude 3.5 Sonnet (Primary)',
                'priority': 1,
                'max_tokens': int(os.environ.get('BEDROCK_MAX_TOKENS', 8192)),
                'temperature': float(os.environ.get('BEDROCK_TEMPERATURE', 0.7)),
                'base_cooldown_seconds': 10  # Short cooldown - just prevent retry storm
            }
        ]

        # Add fallback models from environment (comma-separated)
        fallback_models_str = os.environ.get('BEDROCK_FALLBACK_MODELS', '')
        if fallback_models_str:
            fallback_ids = [m.strip() for m in fallback_models_str.split(',') if m.strip()]
            for i, model_id in enumerate(fallback_ids, 2):
                models.append({
                    'id': model_id,
                    'name': f'Claude Fallback {i-1}',
                    'priority': i,
                    'max_tokens': int(os.environ.get('BEDROCK_MAX_TOKENS', 8192)),
                    'temperature': float(os.environ.get('BEDROCK_TEMPERATURE', 0.7)),
                    'base_cooldown_seconds': 5  # Even shorter for fallbacks
                })
        else:
            # Default fallback models if not specified
            default_fallbacks = [
                'anthropic.claude-3-5-sonnet-20241022-v2:0',  # Newer version
                'anthropic.claude-3-sonnet-20240229-v1:0',    # Claude 3 Sonnet
                'anthropic.claude-3-haiku-20240307-v1:0'      # Claude 3 Haiku
            ]

            for i, model_id in enumerate(default_fallbacks, 2):
                models.append({
                    'id': model_id,
                    'name': f'Claude Fallback {i-1}',
                    'priority': i,
                    'max_tokens': int(os.environ.get('BEDROCK_MAX_TOKENS', 8192)),
                    'temperature': float(os.environ.get('BEDROCK_TEMPERATURE', 0.7)),
                    'base_cooldown_seconds': 5
                })

        return models

    def get_models_for_request(self, request_id=None):
        """
        Get ordered list of models to try for a single request

        Key Design:
        - ALWAYS returns primary model first (unless in critical cooldown)
        - Each request is independent
        - Short cooldowns only prevent immediate retry storms
        - User isolation maintained

        Args:
            request_id: Optional request identifier for logging

        Returns:
            list: Ordered list of models to try
        """
        current_time = datetime.now()
        available_models = []

        with self.lock:
            for model in self.models:
                model_id = model['id']

                # Check if model is in ACTIVE cooldown (just throttled)
                if model_id in self.cooldown_until:
                    if current_time < self.cooldown_until[model_id]:
                        cooldown_remaining = (self.cooldown_until[model_id] - current_time).total_seconds()

                        # Only skip if cooldown is significant (> 2 seconds)
                        # This prevents immediate retry but allows other users to try
                        if cooldown_remaining > 2:
                            print(f"⏳ {model['name']} in active cooldown ({cooldown_remaining:.0f}s remaining)", flush=True)
                            continue
                    else:
                        # Cooldown expired
                        del self.cooldown_until[model_id]

                # Model is available for this request
                available_models.append(model)

        if not available_models:
            print(f"⚠️ All models in active cooldown, waiting 2s...", flush=True)
            time.sleep(2)  # Brief wait, then return all models
            return self.models

        return available_models

    def record_throttle(self, model_id, error_message=""):
        """
        Record a throttle event and set adaptive cooldown

        Adaptive Cooldown Strategy:
        - First throttle: 10s cooldown (prevent immediate retry)
        - Multiple throttles in 60s: 30s cooldown (model is busy)
        - Frequent throttles: up to 60s cooldown (back off more)

        Args:
            model_id: Model identifier
            error_message: Throttling error message
        """
        with self.lock:
            current_time = datetime.now()

            # Find model config
            model = next((m for m in self.models if m['id'] == model_id), None)
            if not model:
                return

            # Record throttle event
            self.throttle_events[model_id].append(current_time)
            self.recent_throttles[model_id].append(current_time)
            self.total_attempts[model_id] += 1

            # Clean up old throttle events (older than 60 seconds)
            cutoff_time = current_time - timedelta(seconds=60)
            self.recent_throttles[model_id] = [
                t for t in self.recent_throttles[model_id] if t > cutoff_time
            ]

            # Calculate adaptive cooldown based on recent throttle frequency
            recent_throttle_count = len(self.recent_throttles[model_id])
            base_cooldown = model['base_cooldown_seconds']

            if recent_throttle_count <= 1:
                # First throttle in last 60s - short cooldown
                cooldown_seconds = base_cooldown
            elif recent_throttle_count <= 3:
                # Multiple throttles - medium cooldown
                cooldown_seconds = base_cooldown * 3
            else:
                # Frequent throttles - longer cooldown
                cooldown_seconds = min(base_cooldown * 6, 60)  # Max 60s

            # Set cooldown
            self.cooldown_until[model_id] = current_time + timedelta(seconds=cooldown_seconds)

            print(f"🚫 {model['name']} throttled (recent: {recent_throttle_count} in 60s)", flush=True)
            print(f"   Adaptive cooldown: {cooldown_seconds}s", flush=True)
            if error_message:
                print(f"   Error: {error_message[:100]}", flush=True)

    def record_success(self, model_id):
        """
        Record a successful request

        Args:
            model_id: Model identifier
        """
        with self.lock:
            self.success_count[model_id] += 1
            self.total_attempts[model_id] += 1

            # Clear recent throttles on success (model recovered)
            if model_id in self.recent_throttles:
                self.recent_throttles[model_id].clear()

    def get_model_stats(self):
        """
        Get statistics about model usage and health

        Returns:
            dict: Model statistics
        """
        with self.lock:
            current_time = datetime.now()

            stats = {
                'total_models': len(self.models),
                'active_cooldowns': sum(1 for model_id in self.cooldown_until
                                       if current_time < self.cooldown_until[model_id]),
                'models': []
            }

            for model in self.models:
                model_id = model['id']

                # Calculate success rate
                total = self.total_attempts.get(model_id, 0)
                success = self.success_count.get(model_id, 0)
                success_rate = (success / total * 100) if total > 0 else 0

                # Check cooldown status
                in_cooldown = False
                cooldown_remaining = 0
                if model_id in self.cooldown_until:
                    if current_time < self.cooldown_until[model_id]:
                        in_cooldown = True
                        cooldown_remaining = int((self.cooldown_until[model_id] - current_time).total_seconds())

                # Recent throttle count
                recent_throttles = len(self.recent_throttles.get(model_id, []))

                model_stat = {
                    'id': model_id,
                    'name': model['name'],
                    'priority': model['priority'],
                    'status': 'in_cooldown' if in_cooldown else 'available',
                    'total_attempts': total,
                    'successful_requests': success,
                    'success_rate': round(success_rate, 1),
                    'recent_throttles_60s': recent_throttles,
                    'total_throttles': len(self.throttle_events.get(model_id, [])),
                    'cooldown_remaining': cooldown_remaining if in_cooldown else 0
                }

                stats['models'].append(model_stat)

            return stats

    def reset_all_cooldowns(self):
        """Reset all cooldowns (emergency recovery)"""
        with self.lock:
            self.cooldown_until.clear()
            self.recent_throttles.clear()
            print("🔄 All model cooldowns and throttle history reset", flush=True)

    def get_throttle_summary(self):
        """Get a summary of throttling patterns for analysis"""
        with self.lock:
            current_time = datetime.now()
            cutoff_5min = current_time - timedelta(minutes=5)
            cutoff_1hour = current_time - timedelta(hours=1)

            summary = {
                'last_5_minutes': {},
                'last_hour': {},
                'all_time': {}
            }

            for model in self.models:
                model_id = model['id']
                events = self.throttle_events.get(model_id, [])

                summary['last_5_minutes'][model['name']] = len([e for e in events if e > cutoff_5min])
                summary['last_hour'][model['name']] = len([e for e in events if e > cutoff_1hour])
                summary['all_time'][model['name']] = len(events)

            return summary


# Global model manager instance (V2)
model_manager_v2 = ModelManagerV2()
