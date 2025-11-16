#!/usr/bin/env python3
"""
Test Activity Logging Functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.activity_logger import ActivityLogger
import time

def test_activity_logger():
    """Test the activity logger functionality"""
    print("🧪 Testing Activity Logger Functionality")
    print("=" * 50)
    
    # Create logger
    logger = ActivityLogger("test_session_123")
    
    # Test basic logging
    print("1. Testing basic activity logging...")
    logger.log_activity("test_action", "success", {"test": "data"})
    logger.log_activity("another_action", "failed", {"error": "test"}, "Test error message")
    
    # Test document upload logging
    print("2. Testing document upload logging...")
    logger.log_document_upload("test_document.docx", 1024000, success=True)
    logger.log_document_upload("failed_document.docx", 0, success=False, error="File not found")
    
    # Test AI analysis logging
    print("3. Testing AI analysis logging...")
    logger.log_ai_analysis("Section 1", 5, 2.5, success=True)
    logger.log_ai_analysis("Section 2", 0, 1.2, success=False, error="AI service unavailable")
    
    # Test feedback actions
    print("4. Testing feedback action logging...")
    logger.log_feedback_action("accepted", "fb_123", "Section 1", "This is good feedback")
    logger.log_feedback_action("rejected", "fb_456", "Section 2", "This feedback is not relevant")
    
    # Test user feedback
    print("5. Testing user feedback logging...")
    logger.log_user_feedback("Section 1", "improvement", "Content Quality", "User suggests better examples")
    
    # Test chat interactions
    print("6. Testing chat interaction logging...")
    logger.log_chat_interaction("user_message", 50, 1.5)
    logger.log_chat_interaction("ai_response", 200, 2.1)
    
    # Test S3 operations
    print("7. Testing S3 operation logging...")
    logger.log_s3_operation("connection_test", True, {"bucket": "test-bucket"})
    logger.log_s3_operation("upload", False, error="Access denied")
    
    # Test export operations
    print("8. Testing export operation logging...")
    logger.log_export_operation("s3_export", 10, 5242880, "s3://bucket/path", True)
    logger.log_export_operation("local_export", 0, 0, "local", False, "Disk full")
    
    # Test operation tracking
    print("9. Testing operation tracking...")
    logger.start_operation("complex_operation", {"param": "value"})
    time.sleep(0.1)  # Simulate work
    logger.complete_operation(True, {"result": "success"})
    
    # Test session events
    print("10. Testing session events...")
    logger.log_session_event("started", {"user": "test_user"})
    logger.log_session_event("completed", {"duration": 300})
    
    # Get summary
    print("\n📊 Activity Summary:")
    summary = logger.get_activity_summary()
    print(f"Total Activities: {summary['total_activities']}")
    print(f"Success Count: {summary['success_count']}")
    print(f"Failed Count: {summary['failed_count']}")
    print(f"Success Rate: {summary['success_rate']}%")
    print(f"Session Duration: {summary['session_duration']} minutes")
    
    # Show failed activities
    failed = logger.get_failed_activities()
    print(f"\n❌ Failed Activities ({len(failed)}):")
    for activity in failed:
        print(f"  - {activity['action']}: {activity['error']}")
    
    # Show recent activities
    recent = logger.get_recent_activities(5)
    print(f"\n📝 Recent Activities ({len(recent)}):")
    for activity in recent:
        status_icon = "✅" if activity['status'] == 'success' else "❌"
        print(f"  {status_icon} {activity['action']} - {activity['timestamp']}")
    
    # Test export
    print("\n💾 Testing export functionality...")
    export_data = logger.export_activities()
    print(f"Export contains {len(export_data['activities'])} activities")
    
    print("\n🎉 Activity Logger Test Completed Successfully!")
    return True

if __name__ == "__main__":
    test_activity_logger()