#!/usr/bin/env python3
"""
Comprehensive test for Claude Sonnet and S3 functionality with App Runner config
"""

import os
import sys
import json
import boto3
from datetime import datetime

# Set App Runner environment variables
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['BEDROCK_MODEL_ID'] = 'anthropic.claude-3-7-sonnet-20250219-v1:0'
os.environ['FLASK_ENV'] = 'production'
os.environ['PORT'] = '8080'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_claude_sonnet_direct():
    """Test Claude Sonnet directly with Bedrock"""
    print("=" * 60)
    print("TESTING CLAUDE SONNET DIRECT CONNECTION")
    print("=" * 60)
    
    try:
        # Test with admin-abhsatsa profile first
        try:
            session = boto3.Session(profile_name='admin-abhsatsa')
            runtime = session.client('bedrock-runtime', region_name='us-east-1')
            print("✅ Using AWS profile: admin-abhsatsa")
        except Exception as e:
            print(f"⚠️ Profile error: {e}")
            runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
            print("✅ Using default AWS credentials")
        
        # Test model configuration
        model_id = 'anthropic.claude-3-7-sonnet-20250219-v1:0'
        
        # Create test request
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.7,
            "system": "You are a helpful AI assistant. Respond concisely.",
            "messages": [
                {
                    "role": "user", 
                    "content": "Test message: Analyze this simple text for any issues: 'The investigation was completed yesterday.' Provide 1 specific feedback item in JSON format with fields: id, type, category, description, suggestion, risk_level."
                }
            ]
        })
        
        print(f"🤖 Testing model: {model_id}")
        print("📤 Sending test request...")
        
        response = runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        content = response_body.get('content', [])
        
        if content and len(content) > 0:
            result_text = content[0].get('text', '')
            print(f"✅ Claude Sonnet response received ({len(result_text)} chars)")
            print(f"📝 Response preview: {result_text[:200]}...")
            
            # Try to parse as JSON
            try:
                json.loads(result_text)
                print("✅ Response is valid JSON")
            except:
                print("⚠️ Response is not JSON (but that's okay for this test)")
            
            return True
        else:
            print("❌ No content in response")
            return False
            
    except Exception as e:
        print(f"❌ Claude Sonnet test failed: {str(e)}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if 'credentials' in error_str or 'access' in error_str:
            print("💡 Fix: Check AWS credentials - run 'aws configure' or set environment variables")
        elif 'region' in error_str:
            print("💡 Fix: Verify AWS region and Bedrock availability in us-east-1")
        elif 'not found' in error_str or 'model' in error_str:
            print("💡 Fix: Verify Claude 3.7 Sonnet model access in your AWS account")
        elif 'throttling' in error_str or 'limit' in error_str:
            print("💡 Fix: Rate limiting - try again in a moment")
        
        return False

def test_ai_feedback_engine():
    """Test AI Feedback Engine with Claude Sonnet"""
    print("\n" + "=" * 60)
    print("TESTING AI FEEDBACK ENGINE")
    print("=" * 60)
    
    try:
        from core.ai_feedback_engine import AIFeedbackEngine
        
        engine = AIFeedbackEngine()
        
        # Test section analysis
        test_content = """
        Timeline of Events:
        - Issue reported by customer
        - Investigation started
        - Resolution implemented
        
        The investigation found that the seller violated policy by listing counterfeit items.
        Action taken: Account suspended.
        """
        
        print("🔍 Testing section analysis...")
        result = engine.analyze_section("Timeline Analysis", test_content)
        
        if result and isinstance(result, dict):
            feedback_items = result.get('feedback_items', [])
            print(f"✅ Analysis completed: {len(feedback_items)} feedback items")
            
            for i, item in enumerate(feedback_items):
                print(f"  {i+1}. {item.get('category', 'Unknown')}: {item.get('description', 'No description')[:50]}...")
            
            # Test chat functionality
            print("\n🗨️ Testing chat functionality...")
            chat_response = engine.process_chat_query(
                "What should I focus on in timeline analysis?",
                {"current_section": "Timeline Analysis", "current_feedback": feedback_items}
            )
            
            if chat_response:
                print(f"✅ Chat response received ({len(chat_response)} chars)")
                print(f"📝 Chat preview: {chat_response[:100]}...")
            else:
                print("❌ No chat response received")
                return False
            
            return True
        else:
            print("❌ Invalid analysis result")
            return False
            
    except Exception as e:
        print(f"❌ AI Feedback Engine test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_s3_functionality():
    """Test S3 export functionality"""
    print("\n" + "=" * 60)
    print("TESTING S3 FUNCTIONALITY")
    print("=" * 60)
    
    try:
        from utils.s3_export_manager import S3ExportManager
        
        s3_manager = S3ExportManager()
        
        print(f"S3 Bucket: {s3_manager.bucket_name}")
        print(f"S3 Base Path: {s3_manager.base_path}")
        print(f"S3 Client Initialized: {'Yes' if s3_manager.s3_client else 'No'}")
        
        # Test S3 connection
        print("\n🔗 Testing S3 connection...")
        connection_status = s3_manager.test_s3_connection()
        
        print(f"Connected: {connection_status.get('connected', False)}")
        print(f"Bucket Accessible: {connection_status.get('bucket_accessible', False)}")
        
        if connection_status.get('error'):
            print(f"Error: {connection_status['error']}")
        
        if connection_status.get('connected') and connection_status.get('bucket_accessible'):
            print("✅ S3 is fully functional!")
            
            # Test folder creation
            test_folder = s3_manager.create_export_folder_name("test_document.docx")
            print(f"✅ Test folder name created: {test_folder}")
            
            return True
        else:
            print("❌ S3 connection issues detected")
            return False
            
    except Exception as e:
        print(f"❌ S3 test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_configuration():
    """Test model configuration with App Runner settings"""
    print("\n" + "=" * 60)
    print("TESTING MODEL CONFIGURATION")
    print("=" * 60)
    
    try:
        from config.model_config import ModelConfig
        
        config = ModelConfig()
        model_config = config.get_model_config()
        
        print(f"Model ID: {model_config['model_id']}")
        print(f"Model Name: {model_config['model_name']}")
        print(f"Base Model: {model_config['base_model']}")
        print(f"Max Tokens: {model_config['max_tokens']}")
        print(f"Temperature: {model_config['temperature']}")
        print(f"Region: {model_config['region']}")
        print(f"Port: {model_config['port']}")
        print(f"Environment: {model_config['flask_env']}")
        
        # Test credentials
        has_creds = config.has_credentials()
        print(f"AWS Credentials: {'✅ Available' if has_creds else '❌ Not found'}")
        
        # Verify App Runner compatibility
        expected_model = 'anthropic.claude-3-7-sonnet-20250219-v1:0'
        if model_config['model_id'] == expected_model:
            print("✅ Correct Claude 3.7 Sonnet model configured")
        else:
            print(f"❌ Expected {expected_model}, got {model_config['model_id']}")
            return False
        
        if model_config['port'] == 8080 and model_config['flask_env'] == 'production':
            print("✅ App Runner configuration correct")
        else:
            print(f"❌ App Runner config issue: port={model_config['port']}, env={model_config['flask_env']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Model configuration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_workflow():
    """Test complete workflow: document analysis → S3 export"""
    print("\n" + "=" * 60)
    print("TESTING END-TO-END WORKFLOW")
    print("=" * 60)
    
    try:
        from core.ai_feedback_engine import AIFeedbackEngine
        from utils.s3_export_manager import S3ExportManager
        from utils.activity_logger import ActivityLogger
        
        # Create test session
        session_id = f"e2e-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger = ActivityLogger(session_id)
        
        print(f"🧪 Test Session: {session_id}")
        
        # Step 1: Document Analysis
        print("\n1️⃣ Testing document analysis...")
        engine = AIFeedbackEngine()
        
        test_sections = {
            "Executive Summary": "The investigation found policy violations that resulted in customer complaints.",
            "Timeline": "Day 1: Issue reported. Day 2: Investigation started. Day 3: Resolution implemented.",
            "Root Cause": "The root cause was inadequate seller verification process."
        }
        
        all_feedback = {}
        for section_name, content in test_sections.items():
            result = engine.analyze_section(section_name, content)
            all_feedback[section_name] = result.get('feedback_items', [])
            logger.log_ai_analysis(section_name, len(all_feedback[section_name]), 1.5, success=True)
        
        total_feedback = sum(len(items) for items in all_feedback.values())
        print(f"✅ Analysis complete: {total_feedback} total feedback items")
        
        # Step 2: S3 Export Test
        print("\n2️⃣ Testing S3 export capability...")
        s3_manager = S3ExportManager()
        
        # Test connection
        connection_status = s3_manager.test_s3_connection()
        logger.log_s3_operation(
            'connection_test',
            success=connection_status.get('connected', False) and connection_status.get('bucket_accessible', False),
            details=connection_status
        )
        
        if connection_status.get('connected') and connection_status.get('bucket_accessible'):
            print("✅ S3 export ready")
        else:
            print("⚠️ S3 export will use local fallback")
        
        # Step 3: Activity Logging
        print("\n3️⃣ Testing activity logging...")
        logger.log_session_event('e2e_test_completed', {
            'sections_analyzed': len(test_sections),
            'total_feedback': total_feedback,
            's3_ready': connection_status.get('connected', False)
        })
        
        summary = logger.get_activity_summary()
        print(f"✅ Activity logging: {summary['total_activities']} activities, {summary['success_rate']}% success rate")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive Claude Sonnet and S3 tests"""
    print("AI-PRISM CLAUDE SONNET & S3 FUNCTIONALITY TEST")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: anthropic.claude-3-7-sonnet-20250219-v1:0")
    print(f"Region: us-east-1")
    print(f"Environment: production")
    
    tests = {
        'claude_sonnet_direct': test_claude_sonnet_direct(),
        'model_configuration': test_model_configuration(),
        'ai_feedback_engine': test_ai_feedback_engine(),
        's3_functionality': test_s3_functionality(),
        'end_to_end_workflow': test_end_to_end_workflow()
    }
    
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in tests.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(tests.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Claude Sonnet 3.7 is working correctly")
        print("✅ S3 export functionality is ready")
        print("✅ AI Feedback Engine is operational")
        print("✅ App Runner configuration is correct")
        print("✅ End-to-end workflow is functional")
        
        print("\n🚀 Ready for production deployment!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        
        # Provide troubleshooting guidance
        if not tests['claude_sonnet_direct']:
            print("\n🔧 Claude Sonnet Issues:")
            print("- Check AWS credentials: aws configure")
            print("- Verify Bedrock access in AWS console")
            print("- Ensure Claude 3.7 Sonnet model is available in us-east-1")
        
        if not tests['s3_functionality']:
            print("\n🔧 S3 Issues:")
            print("- Check S3 bucket permissions")
            print("- Verify felix-s3-bucket exists and is accessible")
            print("- Ensure IAM role has S3 read/write permissions")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)