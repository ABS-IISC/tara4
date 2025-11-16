#!/usr/bin/env python3
"""
Test S3 with specific AWS profile
"""

import boto3
import json
from datetime import datetime
import tempfile
import os

def test_with_profile():
    """Test S3 with admin-abhsatsa profile"""
    print("🔍 Testing S3 with admin-abhsatsa profile...")
    
    try:
        # Create session with specific profile
        session = boto3.Session(profile_name='admin-abhsatsa')
        s3_client = session.client('s3')
        
        print("✅ S3 client created with profile")
        
        # Test bucket access
        bucket_name = 'felix-s3-bucket'
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' is accessible")
        except Exception as e:
            print(f"❌ Bucket access failed: {str(e)}")
            return False
        
        # Test upload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_data = {
                'test_timestamp': datetime.now().isoformat(),
                'message': 'S3 functionality test with profile',
                'profile': 'admin-abhsatsa'
            }
            json.dump(test_data, f, indent=2)
            test_file = f.name
        
        try:
            test_key = f"tara/test_uploads/profile_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            s3_client.upload_file(test_file, bucket_name, test_key)
            print(f"✅ File uploaded to: s3://{bucket_name}/{test_key}")
            
            # Verify upload
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=test_key)
            if 'Contents' in response:
                print("✅ Upload verified successfully")
                return True
            else:
                print("❌ Upload verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
            return False
        finally:
            os.unlink(test_file)
            
    except Exception as e:
        print(f"❌ Profile test failed: {str(e)}")
        return False

def test_default_profile():
    """Test with default profile"""
    print("\n🔍 Testing S3 with default profile...")
    
    try:
        s3_client = boto3.client('s3')
        bucket_name = 'felix-s3-bucket'
        s3_client.head_bucket(Bucket=bucket_name)
        print("✅ Default profile works")
        return True
    except Exception as e:
        print(f"❌ Default profile failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 S3 Profile Test")
    print("=" * 30)
    
    profile_works = test_with_profile()
    default_works = test_default_profile()
    
    print("\n📊 Results:")
    print(f"Profile 'admin-abhsatsa': {'✅ WORKS' if profile_works else '❌ FAILED'}")
    print(f"Default profile: {'✅ WORKS' if default_works else '❌ FAILED'}")
    
    if profile_works:
        print("\n💡 S3 works with 'admin-abhsatsa' profile")
        print("   Update S3ExportManager to use this profile")
    elif default_works:
        print("\n💡 S3 works with default profile")
    else:
        print("\n⚠️ Neither profile works - check credentials and permissions")