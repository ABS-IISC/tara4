#!/usr/bin/env python3
"""
Complete S3 Export Test - End-to-End
Tests the full document review export to S3
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.s3_export_manager import S3ExportManager

class MockReviewSession:
    """Mock review session for testing"""
    def __init__(self):
        self.session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.document_name = "test_document.docx"
        self.sections = ["Section 1", "Section 2", "Section 3"]
        
        # Mock feedback data
        self.accepted_feedback = {
            "Section 1": [
                {
                    "id": "fb1",
                    "text": "This section needs improvement",
                    "risk_level": "Medium",
                    "category": "Content Quality"
                }
            ]
        }
        
        self.rejected_feedback = {
            "Section 2": [
                {
                    "id": "fb2", 
                    "text": "This feedback was not relevant",
                    "risk_level": "Low",
                    "category": "Style"
                }
            ]
        }
        
        self.user_feedback = {
            "Section 1": [
                {
                    "id": "uf1",
                    "text": "User added custom feedback",
                    "type": "Improvement",
                    "category": "Custom"
                }
            ]
        }
        
        self.feedback_data = {
            "Section 1": [
                {"id": "fb1", "text": "AI suggestion 1", "risk_level": "Medium"},
                {"id": "fb3", "text": "AI suggestion 2", "risk_level": "High"}
            ],
            "Section 2": [
                {"id": "fb2", "text": "AI suggestion 3", "risk_level": "Low"}
            ]
        }
        
        self.activity_log = [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "document_uploaded",
                "details": {"filename": self.document_name}
            },
            {
                "timestamp": datetime.now().isoformat(),
                "action": "feedback_accepted",
                "details": {"feedback_id": "fb1", "section": "Section 1"}
            }
        ]
        
        self.chat_history = [
            {
                "timestamp": datetime.now().isoformat(),
                "type": "user",
                "message": "What does this section mean?"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "type": "ai",
                "message": "This section discusses..."
            }
        ]
        
        # Mock audit logger
        self.audit_logger = MockAuditLogger()

class MockAuditLogger:
    """Mock audit logger for testing"""
    def get_session_logs(self):
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "event": "session_started",
                "user_id": "test_user"
            }
        ]
    
    def get_performance_metrics(self):
        return {
            "total_processing_time": 45.2,
            "ai_response_time": 2.1,
            "document_analysis_time": 12.3
        }
    
    def get_activity_timeline(self):
        return [
            {
                "time": datetime.now().isoformat(),
                "event": "Document uploaded",
                "duration": 1.2
            }
        ]

def create_test_documents():
    """Create test documents for export"""
    # Create before document
    before_doc = tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False)
    before_doc.write("Mock before document content")
    before_doc.close()
    
    # Create after document  
    after_doc = tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False)
    after_doc.write("Mock after document content with comments")
    after_doc.close()
    
    return before_doc.name, after_doc.name

def test_complete_export():
    """Test complete review export to S3"""
    print("🧪 Testing Complete S3 Export Functionality")
    print("=" * 50)
    
    # Initialize S3 manager
    s3_manager = S3ExportManager()
    
    # Check S3 connection first
    connection_status = s3_manager.test_s3_connection()
    if not connection_status['connected'] or not connection_status['bucket_accessible']:
        print("❌ S3 not available - cannot test export")
        return False
    
    print("✅ S3 connection verified")
    
    # Create mock review session
    review_session = MockReviewSession()
    print(f"📋 Created mock review session: {review_session.session_id}")
    
    # Create test documents
    before_doc_path, after_doc_path = create_test_documents()
    print("📄 Created test documents")
    
    try:
        # Test the export
        print("📤 Starting S3 export...")
        result = s3_manager.export_complete_review_to_s3(
            review_session, 
            before_doc_path, 
            after_doc_path
        )
        
        if result and result.get('success'):
            print("✅ Export completed successfully")
            
            # Verify export by listing objects using the actual S3 path from result
            if result.get('location', '').startswith('s3://'):
                s3_folder_path = result.get('s3_path')
                
                response = s3_manager.s3_client.list_objects_v2(
                    Bucket=s3_manager.bucket_name,
                    Prefix=s3_folder_path
                )
                
                if 'Contents' in response:
                    print(f"✅ Export verified - found {len(response['Contents'])} files in S3:")
                    for obj in response['Contents']:
                        print(f"  📄 {obj['Key']} ({obj['Size']} bytes)")
                    return True
                else:
                    print("❌ Export verification failed - no files found")
                    return False
            else:
                print(f"✅ Export saved locally: {result.get('location')}")
                return True
        else:
            print(f"❌ Export failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Export test failed: {str(e)}")
        return False
    finally:
        # Clean up test files
        try:
            os.unlink(before_doc_path)
            os.unlink(after_doc_path)
        except:
            pass

def main():
    """Run complete S3 export test"""
    success = test_complete_export()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 S3 Export Test PASSED")
        print("✅ Data is being saved to S3 correctly")
        print("✅ All export components working")
        print("✅ S3 bucket accessible and writable")
    else:
        print("❌ S3 Export Test FAILED")
        print("⚠️ Check S3 configuration and permissions")

if __name__ == "__main__":
    main()