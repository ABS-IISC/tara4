#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""

import os
import sys
import requests
import json
from pathlib import Path

def test_backend():
    """Test the Flask backend"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing TARA Backend...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not running: {e}")
        print("💡 Please start the server with: python app.py")
        return False
    
    # Test 2: Check upload endpoint
    try:
        # Create a simple test file
        test_content = """
        Test Document
        
        Executive Summary
        This is a test document for TARA analysis.
        
        Timeline of Events
        - Event 1: Test event occurred
        - Event 2: Analysis was performed
        
        Root Causes and Preventative Actions
        RC1: Test root cause identified
        PA1: Test preventative action implemented
        """
        
        test_file_path = "test_document.txt"
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        # Test upload (this will fail but should return proper error)
        with open(test_file_path, 'rb') as f:
            files = {'document': ('test.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {'guidelines_preference': 'both'}
            
            response = requests.post(f"{base_url}/upload", files=files, data=data, timeout=10)
            
        # Clean up test file
        os.remove(test_file_path)
        
        if response.status_code in [200, 400, 500]:
            print("✅ Upload endpoint is responding")
            result = response.json()
            if 'error' in result:
                print(f"   Expected error: {result['error']}")
        else:
            print(f"❌ Upload endpoint returned unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
    
    # Test 3: Check required modules
    try:
        from core.document_analyzer import DocumentAnalyzer
        from core.ai_feedback_engine import AIFeedbackEngine
        from utils.statistics_manager import StatisticsManager
        from utils.document_processor import DocumentProcessor
        print("✅ All required modules are importable")
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        return False
    
    # Test 4: Check directories
    required_dirs = ['uploads', 'data', 'core', 'utils', 'templates']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory '{dir_name}' exists")
        else:
            print(f"❌ Directory '{dir_name}' missing")
    
    print("\n🎉 Backend test completed!")
    return True

if __name__ == "__main__":
    test_backend()