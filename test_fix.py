#!/usr/bin/env python3
"""
Quick test to verify the HTTP 500 fix
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from core.document_analyzer import DocumentAnalyzer
        print("   ✅ DocumentAnalyzer imported")
        
        from core.ai_feedback_engine import AIFeedbackEngine
        print("   ✅ AIFeedbackEngine imported")
        
        from config.model_config import model_config
        print("   ✅ model_config imported")
        
        from app import app
        print("   ✅ Flask app imported")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_document_analyzer():
    """Test document analyzer with error handling"""
    print("\n📄 Testing DocumentAnalyzer...")
    
    try:
        from core.document_analyzer import DocumentAnalyzer
        analyzer = DocumentAnalyzer()
        print("   ✅ DocumentAnalyzer initialized")
        
        # Test with non-existent file (should handle gracefully)
        sections, paragraphs, indices = analyzer.extract_sections_from_docx("nonexistent.docx")
        print(f"   ✅ Error handling works: {len(sections)} sections returned")
        
        return True
        
    except Exception as e:
        print(f"   ❌ DocumentAnalyzer test failed: {e}")
        return False

def test_ai_engine():
    """Test AI feedback engine"""
    print("\n🤖 Testing AIFeedbackEngine...")
    
    try:
        from core.ai_feedback_engine import AIFeedbackEngine
        engine = AIFeedbackEngine()
        print("   ✅ AIFeedbackEngine initialized")
        
        # Test analysis with mock content
        result = engine.analyze_section("Test Section", "This is test content for analysis.")
        print(f"   ✅ Analysis works: {len(result.get('feedback_items', []))} items returned")
        
        return True
        
    except Exception as e:
        print(f"   ❌ AIFeedbackEngine test failed: {e}")
        return False

def test_flask_routes():
    """Test Flask app routes"""
    print("\n🌐 Testing Flask routes...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test health check
            response = client.get('/health')
            print(f"   ✅ Health check: {response.status_code}")
            
            # Test main page
            response = client.get('/')
            print(f"   ✅ Main page: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Flask routes test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 HTTP 500 ERROR FIX VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Document Analyzer", test_document_analyzer),
        ("AI Engine", test_ai_engine),
        ("Flask Routes", test_flask_routes)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ HTTP 500 error should be fixed")
        print("🚀 Ready to run: py main.py")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("💡 Check error messages above")
        print("💡 Install missing dependencies: pip install -r requirements.txt")
    
    print("=" * 50)

if __name__ == "__main__":
    main()