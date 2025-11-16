#!/usr/bin/env python3
"""
S3 Functionality Test Script
Tests if data is being saved to S3 bucket correctly
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.s3_export_manager import S3ExportManager

def test_s3_connection():
    """Test S3 connection and bucket access"""
    print("🔍 Testing S3 Connection...")
    
    s3_manager = S3ExportManager()
    connection_status = s3_manager.test_s3_connection()
    
    print(f"Connection Status: {json.dumps(connection_status, indent=2)}")
    
    if connection_status['connected'] and connection_status['bucket_accessible']:
        print("✅ S3 is fully functional")
        return True
    else:
        print("❌ S3 connection failed")
        return False

def test_s3_upload():
    """Test actual file upload to S3"""
    print("\n📤 Testing S3 File Upload...")
    
    s3_manager = S3ExportManager()
    
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = {
            'test_timestamp': datetime.now().isoformat(),
            'test_message': 'This is a test file for S3 functionality',
            'test_data': [1, 2, 3, 4, 5]
        }
        json.dump(test_data, f, indent=2)
        test_file_path = f.name
    
    try:
        # Test upload
        test_key = f"tara/test_uploads/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if s3_manager.s3_client:
            s3_manager.s3_client.upload_file(test_file_path, s3_manager.bucket_name, test_key)
            print(f"✅ Test file uploaded to: s3://{s3_manager.bucket_name}/{test_key}")
            
            # Verify upload by listing
            response = s3_manager.s3_client.list_objects_v2(
                Bucket=s3_manager.bucket_name,
                Prefix=test_key
            )
            
            if 'Contents' in response and len(response['Contents']) > 0:
                print("✅ Upload verified - file exists in S3")
                file_size = response['Contents'][0]['Size']
                print(f"📊 File size: {file_size} bytes")
                return True
            else:
                print("❌ Upload failed - file not found in S3")
                return False
        else:
            print("❌ S3 client not available")
            return False
            
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

def test_s3_list_objects():
    """Test listing objects in S3 bucket"""
    print("\n📋 Testing S3 Object Listing...")
    
    s3_manager = S3ExportManager()
    
    if not s3_manager.s3_client:
        print("❌ S3 client not available")
        return False
    
    try:
        # List objects in tara/ folder
        response = s3_manager.s3_client.list_objects_v2(
            Bucket=s3_manager.bucket_name,
            Prefix=s3_manager.base_path,
            MaxKeys=10
        )
        
        if 'Contents' in response:
            print(f"✅ Found {len(response['Contents'])} objects in {s3_manager.base_path}")
            for obj in response['Contents'][:5]:  # Show first 5
                print(f"  📄 {obj['Key']} ({obj['Size']} bytes)")
            return True
        else:
            print(f"📭 No objects found in {s3_manager.base_path}")
            return True  # Empty is still valid
            
    except Exception as e:
        print(f"❌ Listing failed: {str(e)}")
        return False

def test_aws_credentials():
    """Test AWS credentials configuration"""
    print("\n🔑 Testing AWS Credentials...")
    
    try:
        import boto3.session
        session = boto3.session.Session()
        credentials = session.get_credentials()
        
        if credentials:
            print("✅ AWS credentials found")
            print(f"  Access Key: {credentials.access_key[:8]}...")
            print(f"  Region: {session.region_name or 'default'}")
            return True
        else:
            print("❌ No AWS credentials found")
            print("💡 Configure with: aws configure")
            return False
            
    except Exception as e:
        print(f"❌ Credential check failed: {str(e)}")
        return False

def main():
    """Run all S3 functionality tests"""
    print("🧪 S3 Functionality Test Suite")
    print("=" * 50)
    
    tests = [
        ("AWS Credentials", test_aws_credentials),
        ("S3 Connection", test_s3_connection),
        ("S3 Object Listing", test_s3_list_objects),
        ("S3 File Upload", test_s3_upload)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! S3 functionality is working correctly.")
    else:
        print("⚠️ Some tests failed. Check S3 configuration.")
        print("\n💡 Troubleshooting tips:")
        print("  1. Run: aws configure")
        print("  2. Check bucket permissions")
        print("  3. Verify network connectivity")
        print("  4. Review AWS credentials")

if __name__ == "__main__":
    main()