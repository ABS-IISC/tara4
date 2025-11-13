#!/usr/bin/env python3
"""
AWS Credentials Setup Guide for AI-Prism Claude Integration
"""

import os
import subprocess
import sys
from pathlib import Path

def check_aws_cli():
    """Check if AWS CLI is installed"""
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        print(f"✅ AWS CLI installed: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ AWS CLI not installed")
        print("💡 Install with: pip install awscli")
        return False

def setup_credentials_interactive():
    """Interactive AWS credentials setup"""
    print("\n🔧 AWS CREDENTIALS SETUP")
    print("=" * 50)
    
    print("You need AWS credentials to use Claude AI. Choose an option:")
    print("1. Set environment variables (recommended for development)")
    print("2. Use AWS CLI configure")
    print("3. Show setup instructions")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        setup_env_vars()
    elif choice == "2":
        setup_aws_cli()
    elif choice == "3":
        show_setup_instructions()
    else:
        print("Invalid choice. Showing instructions...")
        show_setup_instructions()

def setup_env_vars():
    """Setup environment variables"""
    print("\n📝 ENVIRONMENT VARIABLES SETUP")
    print("=" * 40)
    
    access_key = input("Enter AWS_ACCESS_KEY_ID: ").strip()
    secret_key = input("Enter AWS_SECRET_ACCESS_KEY: ").strip()
    region = input("Enter AWS_REGION (default: us-east-1): ").strip() or "us-east-1"
    
    if access_key and secret_key:
        env_content = f"""# AWS Credentials for AI-Prism
AWS_ACCESS_KEY_ID={access_key}
AWS_SECRET_ACCESS_KEY={secret_key}
AWS_REGION={region}
AWS_DEFAULT_REGION={region}
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Credentials saved to .env file")
        print("🔄 Restart the application to apply changes")
    else:
        print("❌ Invalid credentials provided")

def setup_aws_cli():
    """Setup using AWS CLI"""
    print("\n🔧 AWS CLI SETUP")
    print("=" * 30)
    
    if not check_aws_cli():
        return
    
    print("Running 'aws configure'...")
    try:
        subprocess.run(['aws', 'configure'], check=True)
        print("✅ AWS CLI configured successfully")
    except subprocess.CalledProcessError:
        print("❌ AWS CLI configuration failed")

def show_setup_instructions():
    """Show detailed setup instructions"""
    print("\n📋 SETUP INSTRUCTIONS")
    print("=" * 50)
    
    print("""
🔹 METHOD 1: Environment Variables (.env file)
   Create a .env file in the project directory with:
   
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=us-east-1
   
🔹 METHOD 2: AWS CLI
   1. Install AWS CLI: pip install awscli
   2. Run: aws configure
   3. Enter your credentials when prompted
   
🔹 METHOD 3: Environment Variables (Terminal)
   export AWS_ACCESS_KEY_ID=your_access_key_here
   export AWS_SECRET_ACCESS_KEY=your_secret_key_here
   export AWS_REGION=us-east-1

🔑 Getting AWS Credentials:
   1. Go to AWS Console > IAM > Users
   2. Select your user > Security credentials
   3. Create access key > Command Line Interface (CLI)
   4. Download the credentials

⚠️  Required Permissions:
   - bedrock:InvokeModel
   - bedrock:ListFoundationModels (optional)

🌍 Supported Regions:
   - us-east-1 (N. Virginia) - Recommended
   - us-west-2 (Oregon)
   - eu-west-3 (Paris)
""")

def test_credentials():
    """Test current credentials"""
    print("\n🧪 TESTING CREDENTIALS")
    print("=" * 30)
    
    try:
        from config.model_config import model_config
        
        if model_config.has_credentials():
            print("✅ Credentials detected and validated")
            
            # Test actual Bedrock connection
            print("📡 Testing Bedrock connection...")
            os.system("python3 test_bedrock_simple.py")
        else:
            print("❌ No valid credentials found")
            print("💡 Run setup to configure credentials")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def main():
    """Main setup function"""
    print("🤖 AI-PRISM AWS CREDENTIALS SETUP")
    print("=" * 60)
    
    # Check current status
    try:
        from config.model_config import model_config
        has_creds = model_config.has_credentials()
        
        if has_creds:
            print("✅ AWS credentials are already configured!")
            test_choice = input("Test connection? (y/n): ").strip().lower()
            if test_choice == 'y':
                test_credentials()
            return
        else:
            print("⚠️  No AWS credentials found")
            
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
    
    # Setup credentials
    setup_choice = input("\nSet up AWS credentials now? (y/n): ").strip().lower()
    if setup_choice == 'y':
        setup_credentials_interactive()
        
        # Test after setup
        test_choice = input("\nTest credentials now? (y/n): ").strip().lower()
        if test_choice == 'y':
            test_credentials()
    else:
        print("\n🎭 Using mock responses")
        print("   The chat will work with simulated Claude responses")
        print("   Run this script again to set up real AI later")

if __name__ == "__main__":
    main()