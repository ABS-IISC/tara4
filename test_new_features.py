#!/usr/bin/env python3
"""
Test script for the new Patterns, Logs, and Learning functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils.pattern_analyzer import DocumentPatternAnalyzer
from utils.audit_logger import AuditLogger
from utils.learning_system import FeedbackLearningSystem

def test_pattern_analyzer():
    print("Testing Pattern Analyzer...")
    
    analyzer = DocumentPatternAnalyzer()
    
    # Test with sample feedback data
    sample_feedback = [
        {
            'id': '1',
            'type': 'critical',
            'category': 'Root Cause Analysis',
            'description': 'Missing detailed root cause analysis',
            'risk_level': 'High'
        },
        {
            'id': '2',
            'type': 'suggestion',
            'category': 'Documentation',
            'description': 'Documentation could be more comprehensive',
            'risk_level': 'Medium'
        },
        {
            'id': '3',
            'type': 'critical',
            'category': 'Root Cause Analysis',
            'description': 'Root cause analysis lacks depth',
            'risk_level': 'High'
        }
    ]
    
    # Add document feedback
    analyzer.add_document_feedback("test_document_1.docx", sample_feedback)
    analyzer.add_document_feedback("test_document_2.docx", sample_feedback[:2])
    
    # Test pattern finding
    patterns = analyzer.find_recurring_patterns()
    print(f"Found {len(patterns)} recurring patterns")
    
    # Test HTML report generation
    html_report = analyzer.get_pattern_report_html()
    print(f"Generated HTML report with {len(html_report)} characters")
    
    print("✅ Pattern Analyzer test passed\n")

def test_audit_logger():
    print("Testing Audit Logger...")
    
    logger = AuditLogger()
    
    # Test logging
    logger.log("TEST_ACTION", "This is a test log entry")
    logger.log("DOCUMENT_UPLOADED", "Test document uploaded", "INFO")
    logger.log("FEEDBACK_ACCEPTED", "Test feedback accepted", "INFO")
    
    # Test getting logs
    logs = logger.get_session_logs()
    print(f"Retrieved {len(logs)} log entries")
    
    # Test HTML report generation
    html_report = logger.generate_audit_report_html()
    print(f"Generated HTML audit report with {len(html_report)} characters")
    
    # Test performance metrics
    metrics = logger.get_performance_metrics()
    print(f"Performance metrics: {metrics}")
    
    print("✅ Audit Logger test passed\n")

def test_learning_system():
    print("Testing Learning System...")
    
    learning = FeedbackLearningSystem()
    
    # Test adding custom feedback
    custom_feedback = {
        'type': 'suggestion',
        'category': 'Documentation',
        'description': 'Add more detailed examples',
        'risk_level': 'Low'
    }
    
    learning.add_custom_feedback(custom_feedback, "Executive Summary")
    
    # Test recording AI feedback responses
    ai_feedback = {
        'type': 'critical',
        'category': 'Root Cause Analysis',
        'description': 'Missing root cause details',
        'risk_level': 'High'
    }
    
    learning.record_ai_feedback_response(ai_feedback, "Executive Summary", accepted=True)
    learning.record_ai_feedback_response(ai_feedback, "Timeline", accepted=False)
    
    # Test getting recommendations
    recommendations = learning.get_recommended_feedback("Executive Summary", "Sample content")
    print(f"Generated {len(recommendations)} recommendations")
    
    # Test HTML report generation
    html_report = learning.generate_learning_report_html()
    print(f"Generated HTML learning report with {len(html_report)} characters")
    
    # Test statistics
    stats = learning.get_learning_statistics()
    print(f"Learning statistics: {stats}")
    
    print("✅ Learning System test passed\n")

def main():
    print("🧪 Testing new AI-Prism features...\n")
    
    try:
        test_pattern_analyzer()
        test_audit_logger()
        test_learning_system()
        
        print("🎉 All tests passed successfully!")
        print("\nThe new Patterns, Logs, and Learning features are working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())