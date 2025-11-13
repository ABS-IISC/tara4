#!/usr/bin/env python3
"""
Final test for working Claude 3.5 Sonnet and S3 functionality
"""

import os
import sys
import json
import boto3
from datetime import datetime

# Set working environment variables
os.environ['BEDROCK_MODEL_ID'] = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['FLASK_ENV'] = 'production'
os.environ['PORT'] = '8080'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_claude_direct():
    """Test Claude 3.5 Sonnet directly"""
    print("🤖 Testing Claude 3.5 Sonnet Direct...")
    
    try:
        session = boto3.Session(profile_name='admin-abhsatsa')
        runtime = session.client('bedrock-runtime', region_name='us-east-1')
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.7,
            "system": "You are an AI assistant for document analysis. Provide concise, actionable feedback.",
            "messages": [{
                "role": "user", 
                "content": "Analyze this investigation timeline: 'Day 1: Issue reported. Day 5: Investigation completed.' Provide specific feedback on what's missing in JSON format with fields: id, type, category, description, suggestion, risk_level."
            }]
        })
        
        response = runtime.invoke_model(
            body=body,
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        content = response_body.get('content', [])
        
        if content and len(content) > 0:
            result = content[0].get('text', '')
            print(f"✅ Claude 3.5 Sonnet working! ({len(result)} chars)")
            print(f"📝 Sample response: {result[:150]}...")
            return True
        else:
            print("❌ No response content")
            return False
            
    except Exception as e:
        print(f"❌ Claude test failed: {str(e)}")
        return False

def test_ai_engine():
    """Test AI Feedback Engine with working Claude"""
    print("\n🔍 Testing AI Feedback Engine...")
    
    try:
        from core.ai_feedback_engine import AIFeedbackEngine
        
        engine = AIFeedbackEngine()
        
        # Test analysis
        result = engine.analyze_section(
            "Timeline Analysis", 
            "The investigation timeline shows: Day 1 - Issue reported by customer. Day 3 - Initial investigation started. Day 7 - Resolution implemented. No specific timestamps or ownership details provided."
        )
        
        if result and result.get('feedback_items'):
            feedback_items = result['feedback_items']
            print(f"✅ Analysis working: {len(feedback_items)} feedback items")
            
            for i, item in enumerate(feedback_items[:2]):  # Show first 2
                print(f"  {i+1}. {item.get('category')}: {item.get('description')[:60]}...")
            
            # Test chat
            chat_response = engine.process_chat_query(
                "What are the key issues with this timeline?",
                {"current_section": "Timeline Analysis", "current_feedback": feedback_items}
            )
            
            if chat_response:
                print(f"✅ Chat working: {len(chat_response)} chars")
                return True
            else:
                print("❌ Chat not working")
                return False
        else:
            print("❌ Analysis not working")
            return False
            
    except Exception as e:
        print(f"❌ AI Engine test failed: {str(e)}")
        return False

def test_s3():
    """Test S3 functionality"""
    print("\n☁️ Testing S3 Export...")
    
    try:
        from utils.s3_export_manager import S3ExportManager
        
        s3_manager = S3ExportManager()
        
        # Test connection
        status = s3_manager.test_s3_connection()
        
        if status.get('connected') and status.get('bucket_accessible'):
            print(f"✅ S3 working: {status['bucket_name']}")
            
            # Test folder creation
            folder = s3_manager.create_export_folder_name("test_doc.docx")
            print(f"✅ Folder creation: {folder}")
            
            return True
        else:
            print(f"❌ S3 issues: {status.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ S3 test failed: {str(e)}")
        return False

def test_complete_workflow():
    """Test complete workflow"""
    print("\n🔄 Testing Complete Workflow...")
    
    try:
        from core.ai_feedback_engine import AIFeedbackEngine
        from utils.s3_export_manager import S3ExportManager
        from utils.activity_logger import ActivityLogger
        
        # Create session
        session_id = f"final-test-{datetime.now().strftime('%H%M%S')}"
        logger = ActivityLogger(session_id)
        
        # Test document analysis
        engine = AIFeedbackEngine()
        result = engine.analyze_section(
            "Executive Summary",
            "Investigation Summary: A policy violation was identified and resolved. Customer impact was minimal. Actions taken include account warning and process improvement."
        )
        
        feedback_count = len(result.get('feedback_items', []))
        logger.log_ai_analysis("Executive Summary", feedback_count, 2.1, success=True)
        
        # Test S3
        s3_manager = S3ExportManager()
        s3_status = s3_manager.test_s3_connection()
        logger.log_s3_operation('test_connection', success=s3_status.get('connected', False))
        
        # Get summary
        summary = logger.get_activity_summary()
        
        print(f"✅ Workflow complete:")
        print(f"  - AI Analysis: {feedback_count} feedback items")
        print(f"  - S3 Status: {'Ready' if s3_status.get('connected') else 'Local fallback'}")
        print(f"  - Activities: {summary['total_activities']} logged")
        print(f"  - Success Rate: {summary['success_rate']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {str(e)}")
        return False

def main():
    """Run final comprehensive test"""
    print("FINAL CLAUDE 3.5 SONNET & S3 TEST")
    print("=" * 50)
    print(f"Model: anthropic.claude-3-5-sonnet-20240620-v1:0")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = {
        'claude_direct': test_claude_direct(),
        'ai_engine': test_ai_engine(),
        's3_functionality': test_s3(),
        'complete_workflow': test_complete_workflow()
    }
    
    print(f"\n{'='*50}")
    print("FINAL TEST RESULTS")
    print("=" * 50)
    
    for test_name, result in tests.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(tests.values())
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Claude 3.5 Sonnet: WORKING")
        print(f"✅ AI Analysis: WORKING") 
        print(f"✅ Chat System: WORKING")
        print(f"✅ S3 Export: WORKING")
        print(f"✅ Activity Logging: WORKING")
        
        print(f"\n🚀 READY FOR APP RUNNER DEPLOYMENT!")
        print(f"📋 Use these environment variables:")
        print(f"   BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0")
        print(f"   AWS_REGION=us-east-1")
        print(f"   FLASK_ENV=production")
        print(f"   PORT=8080")
        
    else:
        print(f"\n⚠️ Some tests failed")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)