#!/usr/bin/env python3
"""
AWS Bedrock Configuration Test Script
Run this to diagnose AWS/Bedrock connectivity issues
"""

import boto3
import json
import os
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_configuration():
    """Test AWS configuration and Bedrock access"""
    
    print("=== AWS Bedrock Configuration Test ===\n")
    
    # Check environment variables
    print("1. Environment Variables:")
    aws_region = os.environ.get('AWS_REGION', 'Not set')
    model_id = os.environ.get('BEDROCK_MODEL_ID', 'Not set')
    access_key = os.environ.get('AWS_ACCESS_KEY_ID', 'Not set')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', 'Not set')
    
    print(f"   AWS_REGION: {aws_region}")
    print(f"   BEDROCK_MODEL_ID: {model_id}")
    print(f"   AWS_ACCESS_KEY_ID: {'Set' if access_key != 'Not set' else 'Not set'}")
    print(f"   AWS_SECRET_ACCESS_KEY: {'Set' if secret_key != 'Not set' else 'Not set'}")
    print()
    
    # Test AWS credentials
    print("2. AWS Credentials Test:")
    try:
        sts = boto3.client('sts', region_name=aws_region if aws_region != 'Not set' else 'us-east-1')
        identity = sts.get_caller_identity()
        print(f"   ✅ AWS credentials working")
        print(f"   Account: {identity.get('Account', 'Unknown')}")
        print(f"   User/Role: {identity.get('Arn', 'Unknown')}")
    except NoCredentialsError:
        print("   ❌ No AWS credentials found")
        print("   Solution: Configure AWS credentials using one of these methods:")
        print("      - AWS CLI: aws configure")
        print("      - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("      - IAM role (for EC2/Lambda)")
        return False
    except Exception as e:
        print(f"   ❌ AWS credentials error: {str(e)}")
        return False
    
    print()
    
    # Test Bedrock service access
    print("3. Bedrock Service Test:")
    try:
        region = aws_region if aws_region != 'Not set' else 'us-east-1'
        bedrock = boto3.client('bedrock', region_name=region)
        
        # List available models
        models = bedrock.list_foundation_models()
        claude_models = [m for m in models['modelSummaries'] if 'claude' in m['modelId'].lower()]
        
        print(f"   ✅ Bedrock service accessible in {region}")
        print(f"   Available Claude models: {len(claude_models)}")
        
        for model in claude_models[:3]:  # Show first 3
            print(f"      - {model['modelId']}")
        
    except Exception as e:
        print(f"   ❌ Bedrock service error: {str(e)}")
        print("   Common issues:")
        print("      - Bedrock not available in your region")
        print("      - Insufficient IAM permissions")
        print("      - Service not enabled")
        return False
    
    print()
    
    # Test Bedrock Runtime (actual AI calls)
    print("4. Bedrock Runtime Test:")
    try:
        region = aws_region if aws_region != 'Not set' else 'us-east-1'
        test_model = model_id if model_id != 'Not set' else 'anthropic.claude-3-sonnet-20240229-v1:0'
        
        runtime = boto3.client('bedrock-runtime', region_name=region)
        
        # Test with Claude 3 format first
        if 'claude-v2' in test_model:
            body = json.dumps({
                "prompt": "\\n\\nHuman: Say 'Hello from Bedrock'\\n\\nAssistant:",
                "max_tokens_to_sample": 50,
                "temperature": 0.1
            })
        else:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 50,
                "messages": [{"role": "user", "content": "Say 'Hello from Bedrock'"}]
            })
        
        response = runtime.invoke_model(
            body=body,
            modelId=test_model,
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        
        if 'claude-v2' in test_model:
            ai_response = response_body.get('completion', '')
        else:
            ai_response = response_body['content'][0]['text']
        
        print(f"   ✅ Bedrock Runtime working with {test_model}")
        print(f"   Test response: {ai_response.strip()}")
        
    except Exception as e:
        print(f"   ❌ Bedrock Runtime error: {str(e)}")
        print("   Common issues:")
        print("      - Model not available in your region")
        print("      - Model access not granted")
        print("      - Incorrect model ID format")
        print("      - Rate limiting or quota exceeded")
        return False
    
    print()
    print("🎉 All tests passed! Bedrock should work in your application.")
    return True

def suggest_fixes():
    """Suggest configuration fixes"""
    print("\n=== Configuration Suggestions ===")
    print()
    print("For AWS App Runner, ensure these environment variables are set:")
    print("   AWS_REGION=us-east-1")
    print("   BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0")
    print()
    print("For IAM permissions, your role needs:")
    print("   - bedrock:InvokeModel")
    print("   - bedrock:ListFoundationModels")
    print()
    print("Available model IDs:")
    print("   - anthropic.claude-3-sonnet-20240229-v1:0 (recommended)")
    print("   - anthropic.claude-3-haiku-20240307-v1:0")
    print("   - anthropic.claude-v2 (legacy)")
    print()

if __name__ == "__main__":
    success = test_aws_configuration()
    if not success:
        suggest_fixes()