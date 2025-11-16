#!/usr/bin/env python3
"""
Quick test for Claude 3.5 Sonnet functionality
"""

import os
import sys
import json
import boto3

# Set environment for Claude 3.5 Sonnet
os.environ['BEDROCK_MODEL_ID'] = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
os.environ['AWS_REGION'] = 'us-east-1'

def test_claude_35_sonnet():
    """Test Claude 3.5 Sonnet with on-demand throughput"""
    print("Testing Claude 3.5 Sonnet...")
    
    try:
        # Use admin-abhsatsa profile
        session = boto3.Session(profile_name='admin-abhsatsa')
        runtime = session.client('bedrock-runtime', region_name='us-east-1')
        
        model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "temperature": 0.7,
            "system": "You are a helpful AI assistant for document analysis.",
            "messages": [
                {
                    "role": "user", 
                    "content": "Analyze this text for investigation quality: 'The timeline shows the issue was reported on Monday and resolved on Friday.' Provide 1 specific feedback item in JSON format."
                }
            ]
        })
        
        print(f"🤖 Testing: {model_id}")
        
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
            print(f"✅ SUCCESS! Claude 3.5 Sonnet working")
            print(f"📝 Response: {result[:200]}...")
            return True
        else:
            print("❌ No response content")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_ai_engine_with_35():
    """Test AI engine with Claude 3.5 Sonnet"""
    print("\nTesting AI Engine with Claude 3.5 Sonnet...")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from core.ai_feedback_engine import AIFeedbackEngine
        
        engine = AIFeedbackEngine()
        
        result = engine.analyze_section(
            "Test Timeline", 
            "The investigation timeline shows events from Monday to Friday with no specific timestamps."
        )
        
        if result and result.get('feedback_items'):
            print(f"✅ AI Engine working with {len(result['feedback_items'])} feedback items")
            return True
        else:
            print("❌ AI Engine not working properly")
            return False
            
    except Exception as e:
        print(f"❌ AI Engine error: {str(e)}")
        return False

if __name__ == "__main__":
    print("CLAUDE 3.5 SONNET COMPATIBILITY TEST")
    print("=" * 50)
    
    test1 = test_claude_35_sonnet()
    test2 = test_ai_engine_with_35()
    
    if test1 and test2:
        print("\n🎉 SUCCESS! Claude 3.5 Sonnet is working!")
        print("✅ Direct Bedrock call: WORKING")
        print("✅ AI Feedback Engine: WORKING")
    else:
        print("\n❌ Some tests failed")
        
    print(f"\nRecommendation: Use Claude 3.5 Sonnet for App Runner deployment")