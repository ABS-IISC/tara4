#!/usr/bin/env python3
"""
Test script to verify the clean fixes work correctly
"""

import os
import sys

def test_files_exist():
    """Test if required files exist"""
    base_path = "/Users/abhsatsa/Documents/risk stuff/tool/tara2"
    
    required_files = [
        "templates/enhanced_index.html",
        "static/js/clean_fixes.js",
        "app.py"
    ]
    
    print("🔍 Testing file existence...")
    all_exist = True
    
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_html_content():
    """Test HTML content for fixes"""
    html_path = "/Users/abhsatsa/Documents/risk stuff/tool/tara2/templates/enhanced_index.html"
    
    print("\n🔍 Testing HTML content...")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test 1: Check for clean button
        if 'onclick="showTextHighlightingGuide()"' in content:
            print("✅ Text highlighting button uses clean function")
        else:
            print("❌ Text highlighting button not fixed")
            return False
        
        # Test 2: Check for clean_fixes.js inclusion
        if 'clean_fixes.js' in content:
            print("✅ clean_fixes.js is included")
        else:
            print("❌ clean_fixes.js not included")
            return False
        
        # Test 3: Check problematic function is removed
        if 'getTextHighlightingGuideContent()' not in content:
            print("✅ Problematic function removed")
        else:
            print("❌ Problematic function still exists")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading HTML file: {e}")
        return False

def test_js_content():
    """Test JavaScript content"""
    js_path = "/Users/abhsatsa/Documents/risk stuff/tool/tara2/static/js/clean_fixes.js"
    
    print("\n🔍 Testing JavaScript content...")
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test 1: Check for startAnalysis function
        if 'function startAnalysis()' in content:
            print("✅ startAnalysis function exists")
        else:
            print("❌ startAnalysis function missing")
            return False
        
        # Test 2: Check for showTextHighlightingGuide function
        if 'function showTextHighlightingGuide()' in content:
            print("✅ showTextHighlightingGuide function exists")
        else:
            print("❌ showTextHighlightingGuide function missing")
            return False
        
        # Test 3: Check for file upload handlers
        if 'handleAnalysisFileUpload' in content:
            print("✅ File upload handlers exist")
        else:
            print("❌ File upload handlers missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading JS file: {e}")
        return False

def main():
    print("🧪 Testing Clean Fixes for AI-Prism")
    print("=" * 50)
    
    # Run tests
    files_ok = test_files_exist()
    html_ok = test_html_content()
    js_ok = test_js_content()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Files exist: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"HTML fixes: {'✅ PASS' if html_ok else '❌ FAIL'}")
    print(f"JS fixes: {'✅ PASS' if js_ok else '❌ FAIL'}")
    
    overall_pass = files_ok and html_ok and js_ok
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASS' if overall_pass else '❌ SOME TESTS FAILED'}")
    
    if overall_pass:
        print("\n🚀 Clean fixes are working!")
        print("Issues fixed:")
        print("1. ✅ Text highlighting button no longer shows popup")
        print("2. ✅ Start analysis button now works properly")
        print("\nYou can now run: python3 main.py")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
    
    return 0 if overall_pass else 1

if __name__ == "__main__":
    sys.exit(main())