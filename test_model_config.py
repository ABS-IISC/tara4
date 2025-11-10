#!/usr/bin/env python3
"""
Test script for model configuration system
Run this to verify your model configuration is working correctly
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config.model_config import model_config
    from core.ai_feedback_engine import AIFeedbackEngine
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def test_configuration():
    """Test the model configuration system"""
    print("🔧 TESTING AI-PRISM MODEL CONFIGURATION")
    print("=" * 60)
    
    # Print configuration summary
    model_config.print_config_summary()
    
    # Test configuration access
    config = model_config.get_model_config()
    
    print("\n📋 CONFIGURATION DETAILS:")
    print(f"Model ID: {config['model_id']}")
    print(f"Base Model: {config['base_model']}")
    print(f"Format: {config['format']}")
    print(f"Supports Reasoning: {config['supports_reasoning']}")
    print(f"Reasoning Enabled: {config['reasoning_enabled']}")
    print(f"Max Tokens: {config['max_tokens']}")
    print(f"Temperature: {config['temperature']}")
    print(f"Region: {config['region']}")
    print(f"Environment: {config['flask_env']}")
    
    # Test fallback models
    print(f"\n🔄 FALLBACK MODELS:")
    for i, fallback in enumerate(config['fallback_models'][:3], 1):
        fallback_id = model_config.get_fallback_model_id(fallback)
        print(f"{i}. {fallback} → {fallback_id}")
    
    # Test credentials
    print(f"\n🔐 CREDENTIALS CHECK:")
    print(f"Has Credentials: {model_config.has_credentials()}")
    print(f"Is Production: {model_config.is_production()}")
    
    # Test request body generation
    print(f"\n📤 REQUEST BODY TEST:")
    try:
        body = model_config.get_bedrock_request_body("Test system prompt", "Test user prompt")
        body_obj = json.loads(body)
        print("✅ Request body generation: SUCCESS")
        print(f"Body keys: {list(body_obj.keys())}")
        if 'reasoning' in body_obj:
            print(f"Reasoning config: {body_obj['reasoning']}")
    except Exception as e:
        print(f"❌ Request body generation: FAILED - {e}")
    
    return config

def test_ai_engine():
    """Test the AI feedback engine with current configuration"""
    print(f"\n🤖 TESTING AI FEEDBACK ENGINE")
    print("=" * 60)
    
    try:
        ai_engine = AIFeedbackEngine()
        print("✅ AI Engine initialization: SUCCESS")
        
        # Test mock response (always works)
        print("\n📝 Testing mock response...")
        mock_response = ai_engine._mock_ai_response("test prompt")
        mock_data = json.loads(mock_response)
        print(f"✅ Mock response: {len(mock_data.get('feedback_items', []))} feedback items")
        
        # Test actual Bedrock if credentials available
        if model_config.has_credentials():
            print("\n🌐 Testing Bedrock connection...")
            try:
                # Test with a simple prompt
                test_response = ai_engine._invoke_bedrock(
                    "You are a helpful assistant.", 
                    "Say 'Configuration test successful' if you can respond."
                )
                
                if test_response.startswith('{"error"'):
                    error_data = json.loads(test_response)
                    print(f"❌ Bedrock test: FAILED - {error_data['error']}")
                else:
                    print(f"✅ Bedrock test: SUCCESS")
                    print(f"Response preview: {test_response[:100]}...")
                    
            except Exception as e:
                print(f"❌ Bedrock test: FAILED - {str(e)}")
        else:
            print("⚠️  Bedrock test: SKIPPED (no credentials)")
            
    except Exception as e:
        print(f"❌ AI Engine initialization: FAILED - {e}")

def test_environment_variables():
    """Test environment variable configuration"""
    print(f"\n🌍 ENVIRONMENT VARIABLES CHECK")
    print("=" * 60)
    
    required_vars = [
        'AWS_REGION',
        'BEDROCK_MODEL_ID',
        'FLASK_ENV',
        'PORT'
    ]
    
    optional_vars = [
        'AWS_DEFAULT_REGION',
        'BEDROCK_MAX_TOKENS',
        'BEDROCK_TEMPERATURE',
        'REASONING_ENABLED',
        'REASONING_BUDGET_TOKENS',
        'BEDROCK_TIMEOUT',
        'BEDROCK_RETRY_ATTEMPTS'
    ]
    
    print("Required Variables:")
    for var in required_vars:
        value = os.environ.get(var, 'NOT SET')
        status = "✅" if value != 'NOT SET' else "❌"
        print(f"{status} {var}: {value}")
    
    print("\nOptional Variables:")
    for var in optional_vars:
        value = os.environ.get(var, 'NOT SET')
        status = "✅" if value != 'NOT SET' else "⚠️ "
        print(f"{status} {var}: {value}")

def test_model_compatibility():
    """Test model compatibility and format detection"""
    print(f"\n🔍 MODEL COMPATIBILITY TEST")
    print("=" * 60)
    
    config = model_config.get_model_config()
    base_model = config['base_model']
    
    # Check if model is in supported list
    if base_model in model_config.SUPPORTED_MODELS:
        model_info = model_config.SUPPORTED_MODELS[base_model]
        print(f"✅ Model '{base_model}' is supported")
        print(f"   Name: {model_info['name']}")
        print(f"   Format: {model_info['format']}")
        print(f"   Max Tokens: {model_info['max_tokens']}")
        print(f"   Supports Reasoning: {model_info.get('supports_reasoning', False)}")
    else:
        print(f"⚠️  Model '{base_model}' not in supported list")
        print("   Using default configuration")
    
    # Test format detection
    print(f"\n📋 Format Detection:")
    print(f"Detected format: {config['format']}")
    print(f"Anthropic version: {config.get('anthropic_version', 'N/A')}")

def main():
    """Run all tests"""
    print(f"🚀 AI-PRISM MODEL CONFIGURATION TEST")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Test configuration
        config = test_configuration()
        
        # Test environment variables
        test_environment_variables()
        
        # Test model compatibility
        test_model_compatibility()
        
        # Test AI engine
        test_ai_engine()
        
        print(f"\n🎉 TESTING COMPLETE")
        print("=" * 60)
        
        # Summary
        print(f"✅ Configuration loaded successfully")
        print(f"✅ Model: {config['model_name']}")
        print(f"✅ Region: {config['region']}")
        print(f"✅ Environment: {config['flask_env']}")
        
        if model_config.has_credentials():
            print(f"✅ AWS credentials available")
        else:
            print(f"⚠️  AWS credentials not configured (will use mock responses)")
        
        print(f"\n🚀 Ready to run AI-Prism with {config['model_name']}!")
        
    except Exception as e:
        print(f"\n❌ TESTING FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)