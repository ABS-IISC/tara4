#!/usr/bin/env python3
"""
AI-Prism Configuration Test Script

Tests the App Runner environment configuration and Bedrock connectivity.
"""

import os
import boto3
import json
from datetime import datetime

def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔧 Testing Environment Variables...")
    
    required_vars = {
        'AWS_REGION': os.environ.get('AWS_REGION'),
        'AWS_DEFAULT_REGION': os.environ.get('AWS_DEFAULT_REGION'),
        'BEDROCK_MODEL_ID': os.environ.get('BEDROCK_MODEL_ID'),
        'FLASK_ENV': os.environ.get('FLASK_ENV'),
        'PORT': os.environ.get('PORT'),
        'BEDROCK_MAX_TOKENS': os.environ.get('BEDROCK_MAX_TOKENS'),
        'BEDROCK_TEMPERATURE': os.environ.get('BEDROCK_TEMPERATURE'),
        'REASONING_ENABLED': os.environ.get('REASONING_ENABLED'),
        'REASONING_BUDGET_TOKENS': os.environ.get('REASONING_BUDGET_TOKENS')
    }
    
    for var_name, var_value in required_vars.items():
        if var_value:
            print(f"✅ {var_name} = {var_value}")
        else:
            print(f"❌ {var_name} = NOT SET")
    
    return all(required_vars.values())

def test_bedrock_connectivity():
    """Test Bedrock service connectivity"""
    print("\n🤖 Testing Bedrock Connectivity...")
    
    try:
        region = os.environ.get('AWS_REGION', 'us-east-1')
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-7-sonnet-20250219-v1:0')
        max_tokens = int(os.environ.get('BEDROCK_MAX_TOKENS', '8192'))
        temperature = float(os.environ.get('BEDROCK_TEMPERATURE', '0.7'))
        reasoning_enabled = os.environ.get('REASONING_ENABLED', 'true').lower() == 'true'
        reasoning_budget = int(os.environ.get('REASONING_BUDGET_TOKENS', '2000'))
        
        print(f"Region: {region}")
        print(f"Model: {model_id}")
        print(f"Max Tokens: {max_tokens}")
        print(f"Temperature: {temperature}")
        print(f"Reasoning: {reasoning_enabled}")
        print(f"Reasoning Budget: {reasoning_budget}")
        
        # Create Bedrock client
        runtime = boto3.client('bedrock-runtime', region_name=region)
        
        # Test request
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,  # Small test request
            "temperature": temperature,
            "system": "You are AI-Prism, a document analysis assistant.",
            "messages": [{"role": "user", "content": "Hello, please confirm you are working properly."}]
        }
        
        # Add reasoning if enabled
        if reasoning_enabled and 'sonnet' in model_id and '20250219' in model_id:
            request_body["reasoning"] = {
                "enabled": True,
                "budget_tokens": min(reasoning_budget, 500)  # Small budget for test
            }
            print("✅ Reasoning configuration added to test request")
        
        response = runtime.invoke_model(
            body=json.dumps(request_body),
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        content = response_body.get('content', [])
        
        if content and len(content) > 0:
            response_text = content[0].get('text', '')
            print(f"✅ Bedrock Response: {response_text[:100]}...")
            
            # Check if reasoning was used
            if 'reasoning' in response_body:
                reasoning_tokens = response_body['reasoning'].get('tokens_used', 0)
                print(f"✅ Reasoning tokens used: {reasoning_tokens}")
            
            return True
        else:
            print("❌ No content in Bedrock response")
            return False
            
    except Exception as e:
        print(f"❌ Bedrock Error: {str(e)}")
        return False

def test_app_runner_environment():
    """Test App Runner specific environment"""
    print("\n🚀 Testing App Runner Environment...")
    
    flask_env = os.environ.get('FLASK_ENV')
    port = os.environ.get('PORT')
    
    if flask_env == 'production':
        print("✅ Running in production mode (App Runner)")
    else:
        print(f"ℹ️ Running in {flask_env} mode (Local)")
    
    if port == '8080':
        print("✅ Using App Runner standard port 8080")
    else:
        print(f"ℹ️ Using port {port}")
    
    # Check for IAM role (App Runner provides this)
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        arn = identity.get('Arn', '')
        
        if 'app-runner' in arn.lower() or 'apprunner' in arn.lower():
            print(f"✅ Using App Runner IAM role: {arn}")
        else:
            print(f"ℹ️ Using IAM identity: {arn}")
            
        return True
    except Exception as e:
        print(f"❌ IAM Error: {str(e)}")
        return False

def main():
    """Run all configuration tests"""
    print("🧪 AI-Prism Configuration Test")
    print("=" * 50)
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    
    # Run tests
    env_ok = test_environment_variables()
    bedrock_ok = test_bedrock_connectivity()
    app_runner_ok = test_app_runner_environment()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Bedrock Connectivity: {'✅ PASS' if bedrock_ok else '❌ FAIL'}")
    print(f"App Runner Environment: {'✅ PASS' if app_runner_ok else '❌ FAIL'}")
    
    if all([env_ok, bedrock_ok, app_runner_ok]):
        print("\n🎉 All tests passed! AI-Prism is ready for App Runner deployment.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.")
        return 1

if __name__ == '__main__':
    exit(main())