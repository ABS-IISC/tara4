#!/usr/bin/env python3
"""
Test script for S3 connectivity and activity logging functionality
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.s3_export_manager import S3ExportManager
from utils.activity_logger import ActivityLogger

def test_s3_connection():
    """Test S3 connection and bucket access"""
    print("=" * 60)
    print("TESTING S3 CONNECTIVITY")
    print("=" * 60)
    
    try:
        s3_manager = S3ExportManager()
        
        print(f"Bucket: {s3_manager.bucket_name}")
        print(f"Base Path: {s3_manager.base_path}")
        print(f"S3 Client Initialized: {'Yes' if s3_manager.s3_client else 'No'}")
        
        # Test connection
        connection_status = s3_manager.test_s3_connection()
        
        print("\nConnection Test Results:")
        print(f"Connected: {connection_status.get('connected', False)}")
        print(f"Bucket Accessible: {connection_status.get('bucket_accessible', False)}")
        
        if connection_status.get('error'):
            print(f"Error: {connection_status['error']}")
        
        if connection_status.get('connected') and connection_status.get('bucket_accessible'):
            print("✅ S3 is ready for exports!")
            return True
        else:
            print("❌ S3 is not ready - will use local fallback")
            return False
            
    except Exception as e:
        print(f"❌ S3 test failed: {str(e)}")
        return False

def test_activity_logger():
    """Test activity logging functionality"""
    print("\n" + "=" * 60)
    print("TESTING ACTIVITY LOGGER")
    print("=" * 60)
    
    try:
        # Create test session
        test_session_id = f"test-session-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger = ActivityLogger(test_session_id)
        
        print(f"Test Session ID: {test_session_id}")
        
        # Test various logging operations
        print("\n1. Testing document upload logging...")
        logger.log_document_upload("test_document.docx", 1024000, success=True)
        
        print("2. Testing AI analysis logging...")
        logger.log_ai_analysis("Test Section", 5, 2.5, success=True)
        
        print("3. Testing feedback action logging...")
        logger.log_feedback_action("accepted", "feedback_123", "Test Section", "Test feedback description")
        
        print("4. Testing S3 operation logging...")
        logger.log_s3_operation("export_test", success=True, details={"location": "s3://test-bucket/test-folder/"})
        
        print("5. Testing session event logging...")
        logger.log_session_event("test_completed", {"test_items": 4})
        
        # Get activity summary
        summary = logger.get_activity_summary()
        print(f"\nActivity Summary:")
        print(f"Total Activities: {summary['total_activities']}")
        print(f"Success Count: {summary['success_count']}")
        print(f"Failed Count: {summary['failed_count']}")
        print(f"Success Rate: {summary['success_rate']}%")
        
        # Export activities
        export_data = logger.export_activities()
        print(f"\nExport Data Keys: {list(export_data.keys())}")
        print(f"Activities Count: {len(export_data['activities'])}")
        
        print("✅ Activity logger test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Activity logger test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between S3 and activity logging"""
    print("\n" + "=" * 60)
    print("TESTING INTEGRATION")
    print("=" * 60)
    
    try:
        # Create test session with activity logger
        test_session_id = f"integration-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger = ActivityLogger(test_session_id)
        s3_manager = S3ExportManager()
        
        # Simulate a complete review workflow
        print("1. Simulating document upload...")
        logger.log_document_upload("integration_test.docx", 2048000, success=True)
        
        print("2. Simulating AI analysis...")
        logger.log_ai_analysis("Introduction", 3, 1.8, success=True)
        logger.log_ai_analysis("Methodology", 5, 2.2, success=True)
        
        print("3. Simulating feedback actions...")
        logger.log_feedback_action("accepted", "fb_001", "Introduction", "Good analysis point")
        logger.log_feedback_action("rejected", "fb_002", "Introduction", "Not relevant")
        logger.log_feedback_action("accepted", "fb_003", "Methodology", "Important consideration")
        
        print("4. Testing S3 connection with logging...")
        connection_status = s3_manager.test_s3_connection()
        logger.log_s3_operation(
            "connection_test",
            success=connection_status.get('connected', False) and connection_status.get('bucket_accessible', False),
            details={
                'bucket_name': connection_status.get('bucket_name'),
                'connected': connection_status.get('connected', False),
                'bucket_accessible': connection_status.get('bucket_accessible', False)
            },
            error=connection_status.get('error')
        )
        
        print("5. Simulating review completion...")
        logger.log_session_event("review_completed", {
            "comments_added": 2,
            "sections_analyzed": 2,
            "total_feedback": 3
        })
        
        # Get final summary
        final_summary = logger.get_activity_summary()
        print(f"\nFinal Integration Test Summary:")
        print(f"Total Activities: {final_summary['total_activities']}")
        print(f"Success Rate: {final_summary['success_rate']}%")
        print(f"Session Duration: {final_summary['session_duration']} minutes")
        
        # Test export functionality
        export_data = logger.export_activities()
        print(f"Export ready with {len(export_data['activities'])} activities")
        
        print("✅ Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("AI-PRISM S3 AND LOGGING TEST SUITE")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        's3_connection': test_s3_connection(),
        'activity_logger': test_activity_logger(),
        'integration': test_integration()
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! S3 and logging functionality is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        print("Note: S3 failures will use local fallback, which is expected if AWS credentials are not configured.")
    
    print("\nNext steps:")
    print("1. Run 'python3 main.py' to start the application")
    print("2. Upload a document and complete a review")
    print("3. Check the activity logs button to see comprehensive logging")
    print("4. Complete review will automatically attempt S3 export")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)