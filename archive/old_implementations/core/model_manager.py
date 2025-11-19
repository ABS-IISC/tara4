"""
Multi-Model Manager with Automatic Fallback
Handles throttling by switching to alternative models automatically
"""
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict

class ModelManager:
    """
    Manages multiple Claude models with automatic fallback on throttling

    Features:
    - Priority-based model selection
    - Automatic fallback on throttling
    - Cooldown period tracking
    - Model health monitoring
    """

    def __init__(self):
        """Initialize model manager with available models"""

        # Define all available Claude models in priority order
        # Priority 1: Latest and most capable (but may throttle first)
        # Priority 2-4: Fallback models with same/similar capabilities
        self.models = self._load_models()

        # Track model health and cooldowns
        self.model_status = {}
        self.throttle_count = defaultdict(int)
        self.last_throttle_time = {}
        self.cooldown_until = {}

        # Initialize status for all models
        for model in self.models:
            self.model_status[model['id']] = 'available'

        print(f"✅ ModelManager initialized with {len(self.models)} models")
        for i, model in enumerate(self.models, 1):
            print(f"   {i}. {model['name']} (Priority {model['priority']})")

    def _load_models(self):
        """Load model configuration from environment or use defaults"""

        # Get primary model from environment
        primary_model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')

        # Define all available models with priorities
        # Users can override this via environment variables
        models = [
            {
                'id': primary_model_id,
                'name': 'Claude 3.5 Sonnet (Primary)',
                'priority': 1,
                'max_tokens': int(os.environ.get('BEDROCK_MAX_TOKENS', 8192)),
                'temperature': float(os.environ.get('BEDROCK_TEMPERATURE', 0.7)),
                'cooldown_seconds': 60  # Wait 60s after throttling before retry
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
                    'cooldown_seconds': 30  # Shorter cooldown for fallback models
                })
        else:
            # Default fallback models if not specified
            # These are alternative Claude 3.5 Sonnet endpoints
            default_fallbacks = [
                'anthropic.claude-3-5-sonnet-20241022-v2:0',  # Newer version
                'anthropic.claude-3-sonnet-20240229-v1:0',    # Claude 3 Sonnet
                'anthropic.claude-3-haiku-20240307-v1:0'      # Claude 3 Haiku (faster, cheaper)
            ]

            for i, model_id in enumerate(default_fallbacks, 2):
                models.append({
                    'id': model_id,
                    'name': f'Claude Fallback {i-1}',
                    'priority': i,
                    'max_tokens': int(os.environ.get('BEDROCK_MAX_TOKENS', 8192)),
                    'temperature': float(os.environ.get('BEDROCK_TEMPERATURE', 0.7)),
                    'cooldown_seconds': 30
                })

        return models

    def get_available_model(self):
        """
        Get next available model considering throttling status

        Returns:
            dict: Model configuration or None if all throttled
        """
        current_time = datetime.now()

        # Try models in priority order
        for model in self.models:
            model_id = model['id']

            # Check if model is in cooldown
            if model_id in self.cooldown_until:
                if current_time < self.cooldown_until[model_id]:
                    cooldown_remaining = (self.cooldown_until[model_id] - current_time).total_seconds()
                    print(f"⏳ {model['name']} in cooldown (${cooldown_remaining:.0f}s remaining)", flush=True)
                    continue
                else:
                    # Cooldown expired, model available again
                    del self.cooldown_until[model_id]
                    self.model_status[model_id] = 'available'
                    print(f"✅ {model['name']} cooldown expired, now available", flush=True)

            # Return first available model
            if self.model_status[model_id] == 'available':
                print(f"🎯 Selected: {model['name']} (Priority {model['priority']})", flush=True)
                return model

        # All models throttled
        print(f"❌ All {len(self.models)} models are currently throttled", flush=True)
        return None

    def mark_throttled(self, model_id, error_message=""):
        """
        Mark a model as throttled and set cooldown period

        Args:
            model_id: Model identifier
            error_message: Throttling error message
        """
        # Find model config
        model = next((m for m in self.models if m['id'] == model_id), None)
        if not model:
            return

        # Track throttling
        self.throttle_count[model_id] += 1
        self.last_throttle_time[model_id] = datetime.now()
        self.model_status[model_id] = 'throttled'

        # Set cooldown period (increases with consecutive throttles)
        base_cooldown = model['cooldown_seconds']
        throttle_multiplier = min(self.throttle_count[model_id], 5)  # Max 5x
        cooldown_seconds = base_cooldown * throttle_multiplier

        self.cooldown_until[model_id] = datetime.now() + timedelta(seconds=cooldown_seconds)

        print(f"🚫 {model['name']} throttled (count: {self.throttle_count[model_id]})", flush=True)
        print(f"   Cooldown: {cooldown_seconds}s", flush=True)
        if error_message:
            print(f"   Error: {error_message[:100]}", flush=True)

    def mark_success(self, model_id):
        """
        Mark a model as successfully used (reset throttle count)

        Args:
            model_id: Model identifier
        """
        # Reset throttle count on success
        if model_id in self.throttle_count:
            self.throttle_count[model_id] = 0

    def get_model_stats(self):
        """
        Get statistics about model usage and health

        Returns:
            dict: Model statistics
        """
        stats = {
            'total_models': len(self.models),
            'available_models': sum(1 for m in self.models if self.model_status[m['id']] == 'available'),
            'throttled_models': sum(1 for m in self.models if self.model_status[m['id']] == 'throttled'),
            'models': []
        }

        for model in self.models:
            model_id = model['id']
            model_stat = {
                'id': model_id,
                'name': model['name'],
                'priority': model['priority'],
                'status': self.model_status[model_id],
                'throttle_count': self.throttle_count.get(model_id, 0),
                'last_throttle': self.last_throttle_time.get(model_id, '').isoformat() if model_id in self.last_throttle_time else None
            }

            if model_id in self.cooldown_until:
                cooldown_remaining = (self.cooldown_until[model_id] - datetime.now()).total_seconds()
                model_stat['cooldown_remaining'] = max(0, int(cooldown_remaining))

            stats['models'].append(model_stat)

        return stats

    def reset_all_cooldowns(self):
        """Reset all cooldowns (emergency recovery)"""
        self.cooldown_until.clear()
        for model_id in self.model_status:
            self.model_status[model_id] = 'available'
        print("🔄 All model cooldowns reset", flush=True)


# Global model manager instance
model_manager = ModelManager()
