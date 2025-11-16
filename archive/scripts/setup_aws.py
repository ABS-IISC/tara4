#!/usr/bin/env python3
"""
Setup AWS credentials for AI-Prism from existing AWS profile
"""

import os
import sys
import configparser
from pathlib import Path

def setup_aws_credentials():
    """Setup AWS credentials from existing profile"""
    
    # Path to AWS credentials
    aws_creds_path = Path.home() / '.aws' / 'credentials'
    aws_config_path = Path.home() / '.aws' / 'config'
    
    if not aws_creds_path.exists():
        print("❌ AWS credentials file not found")
        return False
    
    # Read credentials
    config = configparser.ConfigParser()
    config.read(aws_creds_path)
    
    # Try to find credentials (check admin-abhsatsa profile first, then default)
    profile_name = None
    access_key = None
    secret_key = None
    
    if 'admin-abhsatsa' in config:
        profile_name = 'admin-abhsatsa'
        access_key = config['admin-abhsatsa'].get('aws_access_key_id')
        secret_key = config['admin-abhsatsa'].get('aws_secret_access_key')
    elif 'default' in config:
        profile_name = 'default'
        access_key = config['default'].get('aws_access_key_id')
        secret_key = config['default'].get('aws_secret_access_key')
    
    if not access_key or not secret_key:
        print("❌ AWS credentials not found in profiles")
        return False
    
    # Set environment variables
    os.environ['AWS_ACCESS_KEY_ID'] = access_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    print(f"✅ AWS credentials loaded from profile: {profile_name}")
    print(f"✅ Access Key: {access_key[:8]}...")
    print(f"✅ Region: us-east-1")
    
    return True

def test_bedrock_access():
    """Test if Bedrock is accessible"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Create Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Try to list foundation models (this requires Bedrock access)
        bedrock_models = boto3.client('bedrock', region_name='us-east-1')
        response = bedrock_models.list_foundation_models()
        
        claude_models = [m for m in response.get('modelSummaries', []) if 'claude' in m.get('modelId', '').lower()]
        
        print(f"✅ Bedrock access confirmed")
        print(f"✅ Found {len(claude_models)} Claude models available")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ Bedrock access denied - check IAM permissions")
        else:
            print(f"❌ Bedrock error: {error_code}")
        return False
    except Exception as e:
        print(f"❌ Bedrock test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 AI-PRISM AWS CREDENTIALS SETUP")
    print("=" * 50)
    
    # Setup credentials
    if setup_aws_credentials():
        print("\n🧪 Testing Bedrock access...")
        if test_bedrock_access():
            print("\n🎉 AWS setup complete!")
            print("✅ Credentials configured")
            print("✅ Bedrock access confirmed")
            print("\n🚀 You can now run: python3 main.py")
        else:
            print("\n⚠️ Credentials set but Bedrock access failed")
            print("💡 Check IAM permissions for Bedrock access")
    else:
        print("\n❌ Failed to setup AWS credentials")
        print("💡 Run 'aws configure' to set up credentials")
    
    print("=" * 50)

if __name__ == "__main__":
    main()