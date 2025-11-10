#!/usr/bin/env python3
"""
AWS Credentials Setup for AI-Prism
"""

import os
from pathlib import Path

def setup_credentials():
    """Interactive AWS credentials setup"""
    print("🔐 AWS CREDENTIALS SETUP FOR AI-PRISM")
    print("=" * 50)
    print("You need AWS credentials to use Claude AI for document analysis.")
    print("Without credentials, AI-Prism will use mock responses for testing.")
    print()
    
    # Check if credentials already exist
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        if 'AWS_ACCESS_KEY_ID=' in content and not content.count('AWS_ACCESS_KEY_ID=#'):
            print("✅ AWS credentials already configured in .env file")
            
            choice = input("Do you want to update them? (y/n): ").lower().strip()
            if choice != 'y':
                print("Keeping existing credentials.")
                return
    
    print("\n📝 Please provide your AWS credentials:")
    print("(You can find these in AWS Console > IAM > Users > Security credentials)")
    print()
    
    # Get credentials from user
    access_key = input("AWS Access Key ID: ").strip()
    if not access_key:
        print("❌ Access Key ID is required")
        return
    
    secret_key = input("AWS Secret Access Key: ").strip()
    if not secret_key:
        print("❌ Secret Access Key is required")
        return
    
    region = input("AWS Region (default: us-east-1): ").strip()
    if not region:
        region = "us-east-1"
    
    # Update .env file
    env_content = f"""# AWS Configuration for AI-Prism
AWS_REGION={region}
AWS_DEFAULT_REGION={region}
AWS_ACCESS_KEY_ID={access_key}
AWS_SECRET_ACCESS_KEY={secret_key}

# Model Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
FLASK_ENV=development
PORT=5000
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
REASONING_ENABLED=false
REASONING_BUDGET_TOKENS=2000
BEDROCK_TIMEOUT=30
BEDROCK_RETRY_ATTEMPTS=2
BEDROCK_RETRY_DELAY=1.0
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ AWS credentials saved to .env file")
    print("🔒 Keep your .env file secure and don't share it")
    
    # Test the credentials
    print("\n🧪 Testing credentials...")
    
    try:
        import subprocess
        import sys
        
        result = subprocess.run([
            sys.executable, 'test_connection.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Credentials test passed!")
            print("🎉 AI-Prism is ready to use Claude AI")
        else:
            print("⚠️ Credentials test failed")
            print("💡 Check your AWS account has Bedrock access")
            print("💡 Verify Claude models are enabled in AWS Console")
            
    except Exception as e:
        print(f"⚠️ Could not test credentials: {e}")
        print("💡 You can test manually with: python test_connection.py")
    
    print("\n🚀 Ready to start AI-Prism!")
    print("Run: python start_aiprism.py")

def main():
    setup_credentials()

if __name__ == "__main__":
    main()