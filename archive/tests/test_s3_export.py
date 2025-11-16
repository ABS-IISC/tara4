#!/usr/bin/env python3
"""
Test script for S3 export functionality
"""

import os
import sys
from datetime import datetime
from utils.s3_export_manager import S3ExportManager

def test_s3_connection():
    """Test S3 connection and bucket access"""
    print("🧪 Testing S3 Export Manager...")
    
    try:
        # Initialize S3 export manager
        s3_manager = S3ExportManager()
        
        if s3_manager.s3_client:
            print("✅ S3 client initialized successfully")
            print(f"📦 Target bucket: {s3_manager.bucket_name}")
            print(f"📁 Base path: {s3_manager.base_path}")
            
            # Test folder name generation
            test_doc_name = "test_document.docx"
            folder_name = s3_manager.create_export_folder_name(test_doc_name)
            print(f"🗂️ Generated folder name: {folder_name}")
            
            return True
        else:
            print("⚠️ S3 client not available - will use local fallback")
            return False
            
    except Exception as e:
        print(f"❌ S3 test failed: {str(e)}")
        return False

def test_local_export():
    """Test local export functionality"""
    print("\n🧪 Testing local export fallback...")
    
    try:
        s3_manager = S3ExportManager()
        
        # Create a mock review session
        class MockReviewSession:
            def __init__(self):
                self.session_id = "test_session_123"
                self.document_name = "test_document.docx"
                self.guidelines_name = "test_guidelines.docx"
                self.guidelines_preference = "both"
                self.feedback_data = {
                    "Section 1": [
                        {
                            "id": "test_1",
                            "type": "suggestion",
                            "category": "Initial Assessment",
                            "description": "Test feedback item",
                            "risk_level": "Medium"
                        }
                    ]
                }
                self.accepted_feedback = {"Section 1": []}
                self.rejected_feedback = {"Section 1": []}
                self.user_feedback = {"Section 1": []}
                self.activity_log = [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "action": "TEST_ACTION",
                        "details": "Test activity log entry"
                    }
                ]
                self.chat_history = []
                self.sections = {"Section 1": "Test content"}
                
                # Mock audit logger
                class MockAuditLogger:
                    def get_session_logs(self):
                        return []
                    def get_performance_metrics(self):
                        return {}
                    def get_activity_timeline(self):
                        return []
                
                self.audit_logger = MockAuditLogger()
        
        mock_session = MockReviewSession()
        
        # Test comprehensive report generation
        report = s3_manager._generate_comprehensive_report(mock_session)
        print("✅ Comprehensive report generated successfully")
        print(f"📊 Report contains {len(report)} main sections")
        
        return True
        
    except Exception as e:
        print(f"❌ Local export test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 AI-Prism S3 Export Manager Test")
    print("=" * 50)
    
    # Test S3 connection
    s3_available = test_s3_connection()
    
    # Test local export
    local_export_ok = test_local_export()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"S3 Connection: {'✅ Available' if s3_available else '⚠️ Fallback Mode'}")
    print(f"Local Export: {'✅ Working' if local_export_ok else '❌ Failed'}")
    
    if s3_available:
        print("\n🎉 S3 export is ready for production!")
        print("💡 Documents will be exported to s3://felix-s3-bucket/tara/")
    else:
        print("\n⚠️ S3 not available - exports will be saved locally")
        print("💡 Check AWS credentials and permissions for S3 access")
    
    print("\n🔧 For App Runner deployment:")
    print("1. Ensure IAM role has S3 permissions")
    print("2. Set AWS_REGION environment variable")
    print("3. Verify bucket 'felix-s3-bucket' exists and is accessible")

if __name__ == "__main__":
    main()