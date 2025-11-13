#!/usr/bin/env python3
"""
AWS S3 Setup Script for AI-Prism Document Analysis Tool

This script helps configure AWS credentials and test S3 connectivity
for the document export functionality.
"""

import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import json

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials:
            print("✅ AWS credentials found:")
            print(f"   Access Key ID: {credentials.access_key[:8]}...")
            print(f"   Secret Key: {'*' * 20}")
            return True
        else:
            print("❌ No AWS credentials found")
            return False
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return False

def test_s3_connection(bucket_name='felix-s3-bucket'):
    """Test S3 connection and bucket access"""
    try:
        s3_client = boto3.client('s3')
        
        # Test bucket access
        print(f"🔍 Testing access to bucket: {bucket_name}")
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' is accessible")
        
        # Test list permissions
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='tara/', MaxKeys=1)
        print("✅ List permissions confirmed")
        
        # Test write permissions (create a test file)
        test_key = 'tara/test_connection.txt'
        test_content = f"AI-Prism S3 connection test - {os.getenv('USER', 'unknown')} - {boto3.__version__}"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        print("✅ Write permissions confirmed")
        
        # Clean up test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ S3 connection test completed successfully")
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not configured")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Bucket '{bucket_name}' not found")
        elif error_code == '403':
            print(f"❌ Access denied to bucket '{bucket_name}'")
        else:
            print(f"❌ S3 error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def setup_aws_credentials():
    """Interactive AWS credentials setup"""
    print("\n🔧 AWS Credentials Setup")
    print("=" * 40)
    
    access_key = input("Enter your AWS Access Key ID: ").strip()
    secret_key = input("Enter your AWS Secret Access Key: ").strip()
    region = input("Enter your AWS region (default: us-east-1): ").strip() or 'us-east-1'
    
    if not access_key or not secret_key:
        print("❌ Access Key ID and Secret Access Key are required")
        return False
    
    # Create AWS credentials directory
    aws_dir = os.path.expanduser('~/.aws')
    os.makedirs(aws_dir, exist_ok=True)
    
    # Write credentials file
    credentials_file = os.path.join(aws_dir, 'credentials')
    config_file = os.path.join(aws_dir, 'config')
    
    with open(credentials_file, 'w') as f:
        f.write(f"""[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
""")
    
    with open(config_file, 'w') as f:
        f.write(f"""[default]
region = {region}
output = json
""")
    
    print(f"✅ AWS credentials saved to {credentials_file}")
    print(f"✅ AWS config saved to {config_file}")
    
    return True

def create_env_file():
    """Create .env file with AWS configuration"""
    env_content = """# AWS Configuration for AI-Prism
AWS_DEFAULT_REGION=us-east-1
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=felix-s3-bucket
S3_BASE_PATH=tara/

# Optional: Uncomment and set if not using AWS credentials file
# AWS_ACCESS_KEY_ID=your_access_key_here
# AWS_SECRET_ACCESS_KEY=your_secret_key_here
"""
    
    env_file = '.env'
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_file} with AWS configuration")
    else:
        print(f"ℹ️  {env_file} already exists")

def main():
    """Main setup function"""
    print("🌟 AI-Prism AWS S3 Setup")
    print("=" * 50)
    
    # Check current credentials
    if check_aws_credentials():
        print("\n🔍 Testing S3 connection...")
        if test_s3_connection():
            print("\n🎉 AWS S3 is properly configured!")
            print("   Documents will be exported to S3 when you complete reviews.")
        else:
            print("\n⚠️  S3 connection failed. Check bucket permissions.")
    else:
        print("\n❓ Would you like to configure AWS credentials now? (y/n): ", end="")
        if input().lower().startswith('y'):
            if setup_aws_credentials():
                print("\n🔍 Testing new credentials...")
                if check_aws_credentials() and test_s3_connection():
                    print("\n🎉 AWS S3 setup completed successfully!")
                else:
                    print("\n⚠️  Setup completed but S3 test failed. Check your credentials and bucket access.")
        else:
            print("\n💡 You can configure AWS credentials later using:")
            print("   aws configure")
            print("   or by running this script again")
    
    # Create .env file
    create_env_file()
    
    print("\n📋 Next Steps:")
    print("1. Start the AI-Prism application: python main.py")
    print("2. Upload a document for analysis")
    print("3. Complete your review - documents will be exported to S3")
    print("4. Use the 'Test S3' button in the app to verify connectivity")

if __name__ == "__main__":
    main()