#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock connection and Claude Sonnet model access
"""

import os
import json
import boto3
from datetime import datetime
from config.model_config import model_config

def test_aws_credentials():
    """Test AWS credentials availability"""
    print("🔐 Testing AWS Credentials...")
    
    # Check environment variables
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    
    print(f"   AWS_ACCESS_KEY_ID: {'✅ Set' if access_key else '❌ Not set'}")
    print(f"   AWS_SECRET_ACCESS_KEY: {'✅ Set' if secret_key else '❌ Not set'}")
    print(f"   AWS_DEFAULT_REGION: {region}")
    
    # Check AWS CLI configuration
    aws_config_path = os.path.expanduser('~/.aws/credentials')
    aws_config_exists = os.path.exists(aws_config_path)
    print(f"   AWS CLI Config: {'✅ Found' if aws_config_exists else '❌ Not found'}")
    
    return access_key and secret_key

def test_bedrock_access():
    """Test AWS Bedrock service access"""
    print("\n🚀 Testing AWS Bedrock Access...")
    
    try:
        config = model_config.get_model_config()
        
        # Create Bedrock client
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=config['region'],
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN')
        )
        
        print(f"   ✅ Bedrock client created successfully")
        print(f"   📍 Region: {config['region']}")
        print(f"   🤖 Model ID: {config['model_id']}")
        
        return bedrock, config
        
    except Exception as e:
        print(f"   ❌ Failed to create Bedrock client: {str(e)}")
        return None, None

def test_claude_model(bedrock_client, config):
    """Test Claude Sonnet model invocation"""
    print("\n🧠 Testing Claude Sonnet Model...")
    
    if not bedrock_client:
        print("   ❌ No Bedrock client available")
        return False
    
    try:
        # Simple test prompt
        system_prompt = "You are a helpful AI assistant."
        user_prompt = "Say 'Hello from AI-Prism!' and confirm you are working correctly."
        
        # Generate request body
        body = model_config.get_bedrock_request_body(system_prompt, user_prompt)
        
        print(f"   📤 Sending test request to {config['model_id']}...")
        print(f"   ⏱️ Timeout: {config['timeout']}s")
        
        # Make the API call
        response = bedrock_client.invoke_model(
            body=body,
            modelId=config['model_id'],
            accept="application/json",
            contentType="application/json"
        )
        
        # Parse response
        response_body = json.loads(response.get('body').read())
        result = model_config.extract_response_content(response_body)
        
        print(f"   ✅ Model responded successfully!")
        print(f"   💬 Response: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Model invocation failed: {str(e)}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if 'credentials' in error_str or 'access' in error_str:
            print("   💡 Solution: Configure AWS credentials")
            print("      - Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
            print("      - Or run 'aws configure' to set up AWS CLI")
        elif 'region' in error_str:
            print(f"   💡 Solution: Check AWS region configuration (current: {config['region']})")
        elif 'not found' in error_str or 'model' in error_str:
            print(f"   💡 Solution: Verify model access in region {config['region']}")
            print("      - Check if Claude 3.7 Sonnet is available in your region")
            print("      - Verify Bedrock model access permissions")
        elif 'throttling' in error_str:
            print("   💡 Solution: Rate limiting - try again in a few moments")
        
        return False

def test_fallback_models(bedrock_client, config):
    """Test fallback models"""
    print("\n🔄 Testing Fallback Models...")
    
    if not bedrock_client:
        print("   ❌ No Bedrock client available")
        return
    
    fallback_models = config['fallback_models'][:2]  # Test first 2 fallbacks
    
    for fallback_model in fallback_models:
        try:
            fallback_id = model_config.get_fallback_model_id(fallback_model)
            print(f"   🧪 Testing fallback: {fallback_id}")
            
            # Simple test
            body = model_config.get_bedrock_request_body(
                "You are a helpful assistant.", 
                "Respond with 'Fallback model working!'"
            )
            
            response = bedrock_client.invoke_model(
                body=body,
                modelId=fallback_id,
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            result = model_config.extract_response_content(response_body)
            
            print(f"      ✅ {fallback_model} working!")
            
        except Exception as e:
            print(f"      ❌ {fallback_model} failed: {str(e)[:50]}...")

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 AI-PRISM AWS BEDROCK CONNECTION TEST")
    print("=" * 60)
    print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: AWS Credentials
    creds_ok = test_aws_credentials()
    
    # Test 2: Bedrock Access
    bedrock_client, config = test_bedrock_access()
    
    # Test 3: Claude Model
    model_ok = False
    if bedrock_client and config:
        model_ok = test_claude_model(bedrock_client, config)
        
        # Test 4: Fallback Models (if primary fails)
        if not model_ok:
            test_fallback_models(bedrock_client, config)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"🔐 AWS Credentials: {'✅ OK' if creds_ok else '❌ FAILED'}")
    print(f"🚀 Bedrock Access: {'✅ OK' if bedrock_client else '❌ FAILED'}")
    print(f"🧠 Claude Model: {'✅ OK' if model_ok else '❌ FAILED'}")
    
    if creds_ok and bedrock_client and model_ok:
        print("\n🎉 ALL TESTS PASSED! AI-Prism is ready to use AWS Bedrock.")
    else:
        print("\n⚠️ SOME TESTS FAILED. AI-Prism will use mock responses.")
        print("💡 Fix the issues above to enable real AI analysis.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()