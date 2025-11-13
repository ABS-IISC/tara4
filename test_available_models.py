#!/usr/bin/env python3
"""
Test available Claude models that support on-demand throughput
"""

import boto3
import json

def test_claude_models():
    """Test different Claude model IDs to find working ones"""
    
    # Try with admin-abhsatsa profile
    session = boto3.Session(profile_name='admin-abhsatsa')
    runtime = session.client('bedrock-runtime', region_name='us-east-1')
    
    # List of Claude models to test (older versions that support on-demand)
    models_to_test = [
        'anthropic.claude-3-sonnet-20240229-v1:0',
        'anthropic.claude-3-haiku-20240307-v1:0',
        'anthropic.claude-3-5-sonnet-20240620-v1:0',
        'anthropic.claude-v2:1',
        'anthropic.claude-v2',
        'anthropic.claude-instant-v1'
    ]
    
    working_models = []
    
    for model_id in models_to_test:
        try:
            print(f"Testing: {model_id}")
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "temperature": 0.7,
                "system": "You are a helpful assistant.",
                "messages": [{"role": "user", "content": "Hello, can you respond with 'Working' if you receive this?"}]
            })
            
            response = runtime.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            content = response_body.get('content', [])
            
            if content and len(content) > 0:
                result = content[0].get('text', '')
                print(f"✅ {model_id}: WORKING - {result[:50]}...")
                working_models.append(model_id)
            else:
                print(f"❌ {model_id}: No content")
                
        except Exception as e:
            print(f"❌ {model_id}: {str(e)}")
    
    print(f"\n🎯 WORKING MODELS ({len(working_models)}):")
    for model in working_models:
        print(f"  ✅ {model}")
    
    if working_models:
        recommended = working_models[0]
        print(f"\n🚀 RECOMMENDED: {recommended}")
        return recommended
    else:
        print("\n❌ No working models found")
        return None

if __name__ == "__main__":
    print("TESTING AVAILABLE CLAUDE MODELS")
    print("=" * 50)
    
    working_model = test_claude_models()
    
    if working_model:
        print(f"\n✅ Use this model ID in your configuration: {working_model}")
    else:
        print("\n❌ No Claude models available with on-demand throughput")
        print("💡 You may need to request access to Claude models in AWS Bedrock console")