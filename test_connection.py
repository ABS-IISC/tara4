#!/usr/bin/env python3
"""
Simple AWS Bedrock connection test for AI-Prism
"""

import os
import json
import sys
from pathlib import Path

def check_credentials():
    """Check if AWS credentials are available"""
    print("🔐 Checking AWS Credentials...")
    
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    
    print(f"   AWS_ACCESS_KEY_ID: {'✅ Set' if access_key else '❌ Missing'}")
    print(f"   AWS_SECRET_ACCESS_KEY: {'✅ Set' if secret_key else '❌ Missing'}")
    print(f"   AWS_DEFAULT_REGION: {region}")
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("   ✅ .env file found")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'AWS_ACCESS_KEY_ID=' in content and not content.count('AWS_ACCESS_KEY_ID=#'):
                print("   ✅ AWS credentials configured in .env")
                return True
            else:
                print("   ⚠️ AWS credentials not set in .env file")
    else:
        print("   ❌ .env file not found")
    
    # Check AWS CLI
    aws_config = Path.home() / '.aws' / 'credentials'
    if aws_config.exists():
        print("   ✅ AWS CLI credentials found")
        return True
    
    return bool(access_key and secret_key)

def test_bedrock():
    """Test AWS Bedrock connection"""
    print("\n🚀 Testing AWS Bedrock Connection...")
    
    try:
        import boto3
        from config.model_config import model_config
        
        if not model_config.has_credentials():
            print("   ❌ No AWS credentials available")
            return False
        
        config = model_config.get_model_config()
        print(f"   📍 Region: {config['region']}")
        print(f"   🤖 Model: {config['model_name']}")
        print(f"   🆔 Model ID: {config['model_id']}")
        
        # Create Bedrock client
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=config['region']
        )
        
        # Simple test request
        body = model_config.get_bedrock_request_body(
            "You are a helpful AI assistant.",
            "Respond with exactly: 'AI-Prism connection successful!'"
        )
        
        print("   📡 Sending test request...")
        response = bedrock.invoke_model(
            body=body,
            modelId=config['model_id'],
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        result = model_config.extract_response_content(response_body)
        
        print(f"   ✅ SUCCESS! Claude responded: {result[:100]}...")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Run: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        
        error_str = str(e).lower()
        if 'credentials' in error_str or 'access' in error_str:
            print("   💡 Fix: Add AWS credentials to .env file")
            print("      AWS_ACCESS_KEY_ID=your_access_key")
            print("      AWS_SECRET_ACCESS_KEY=your_secret_key")
        elif 'region' in error_str:
            print("   💡 Fix: Check AWS region configuration")
        elif 'not found' in error_str or 'model' in error_str:
            print("   💡 Fix: Verify Claude model access in your AWS account")
            print("      - Check Bedrock model access in AWS console")
            print("      - Ensure Claude 3.5 Sonnet is available in us-east-1")
        elif 'throttling' in error_str:
            print("   💡 Fix: Rate limiting - try again in a moment")
        
        return False

def test_document_loading():
    """Test document loading functionality"""
    print("\n📄 Testing Document Loading...")
    
    try:
        from core.document_analyzer import DocumentAnalyzer
        
        analyzer = DocumentAnalyzer()
        print("   ✅ Document analyzer initialized")
        
        # Check if uploads directory exists
        uploads_dir = Path('uploads')
        if not uploads_dir.exists():
            uploads_dir.mkdir()
            print("   ✅ Created uploads directory")
        
        # Look for test documents
        test_docs = list(uploads_dir.glob('*.docx'))
        if test_docs:
            print(f"   ✅ Found {len(test_docs)} test documents")
            
            # Try to load the first document
            test_doc = test_docs[0]
            print(f"   🧪 Testing with: {test_doc.name}")
            
            sections, paragraphs, indices = analyzer.extract_sections_from_docx(str(test_doc))
            print(f"   ✅ Loaded document with {len(sections)} sections")
            
            return True
        else:
            print("   ⚠️ No test documents found in uploads/")
            print("   💡 Upload a .docx file to test document loading")
            return True  # Not a failure, just no test docs
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
        
    except Exception as e:
        print(f"   ❌ Document loading failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 AI-PRISM CONNECTION TEST")
    print("=" * 50)
    
    # Test 1: Check credentials
    creds_ok = check_credentials()
    
    # Test 2: Test Bedrock connection
    bedrock_ok = test_bedrock() if creds_ok else False
    
    # Test 3: Test document loading
    docs_ok = test_document_loading()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"🔐 AWS Credentials: {'✅ OK' if creds_ok else '❌ FAILED'}")
    print(f"🚀 Claude Connection: {'✅ OK' if bedrock_ok else '❌ FAILED'}")
    print(f"📄 Document Loading: {'✅ OK' if docs_ok else '❌ FAILED'}")
    
    if creds_ok and bedrock_ok and docs_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ AI-Prism is ready to use with Claude AI")
        print("🚀 Run: python app.py to start the application")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        if not creds_ok:
            print("🔧 Fix AWS credentials first:")
            print("   1. Edit .env file")
            print("   2. Add: AWS_ACCESS_KEY_ID=your_key")
            print("   3. Add: AWS_SECRET_ACCESS_KEY=your_secret")
        if not bedrock_ok and creds_ok:
            print("🔧 Check AWS Bedrock access:")
            print("   1. Verify Bedrock is enabled in AWS console")
            print("   2. Check Claude model access permissions")
        if not docs_ok:
            print("🔧 Check document processing setup")
    
    print("=" * 50)

if __name__ == "__main__":
    main()