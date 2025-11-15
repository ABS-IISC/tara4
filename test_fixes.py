#!/usr/bin/env python3
"""
Test script to verify the fixes for AI-Prism functionality
"""

import os
import sys

def test_file_exists(filepath, description):
    """Test if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def test_html_content(filepath, search_strings, description):
    """Test if HTML file contains expected content"""
    if not os.path.exists(filepath):
        print(f"❌ {description}: File not found")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing = []
        for search_string in search_strings:
            if search_string not in content:
                missing.append(search_string)
        
        if missing:
            print(f"❌ {description}: Missing content - {missing}")
            return False
        else:
            print(f"✅ {description}: All expected content found")
            return True
            
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False

def main():
    print("🔧 Testing AI-Prism Fixes")
    print("=" * 50)
    
    base_path = "/Users/abhsatsa/Documents/risk stuff/tool/tara2"
    
    # Test 1: Check if files exist
    print("\n📁 File Existence Tests:")
    files_ok = True
    files_ok &= test_file_exists(f"{base_path}/templates/enhanced_index.html", "Main HTML template")
    files_ok &= test_file_exists(f"{base_path}/static/js/progress_functions.js", "Progress functions JS")
    files_ok &= test_file_exists(f"{base_path}/app.py", "Flask app")
    
    # Test 2: Check HTML content fixes
    print("\n🔍 HTML Content Tests:")
    html_tests = [
        'getTextHighlightingGuideContent()',  # New function call instead of popup
        'function startAnalysis()',  # StartAnalysis function exists
        'function showMainContent()',  # ShowMainContent function exists
        'function loadSection(index)',  # LoadSection function exists
    ]
    
    html_ok = test_html_content(
        f"{base_path}/templates/enhanced_index.html", 
        html_tests, 
        "HTML template fixes"
    )
    
    # Test 3: Check JavaScript content
    print("\n⚙️ JavaScript Content Tests:")
    js_tests = [
        'window.startAnalysis = startAnalysis',  # Function override
        'window.loadSection = loadSection',  # Function override
        'showSimpleProgressPopup()',  # Progress popup function
    ]
    
    js_ok = test_html_content(
        f"{base_path}/static/js/progress_functions.js", 
        js_tests, 
        "Progress functions JS fixes"
    )
    
    # Test 4: Check for removed problematic content
    print("\n🚫 Removed Content Tests:")
    removed_tests = [
        'showTextHighlightingFeature()',  # Should be removed from button onclick
    ]
    
    with open(f"{base_path}/templates/enhanced_index.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    removed_ok = True
    for test_string in removed_tests:
        if test_string in content:
            print(f"❌ Problematic content still exists: {test_string}")
            removed_ok = False
        else:
            print(f"✅ Problematic content removed: {test_string}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Files exist: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"HTML fixes: {'✅ PASS' if html_ok else '❌ FAIL'}")
    print(f"JS fixes: {'✅ PASS' if js_ok else '❌ FAIL'}")
    print(f"Removed content: {'✅ PASS' if removed_ok else '❌ FAIL'}")
    
    overall_pass = files_ok and html_ok and js_ok and removed_ok
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASS' if overall_pass else '❌ SOME TESTS FAILED'}")
    
    if overall_pass:
        print("\n🚀 Fixes appear to be working correctly!")
        print("You can now:")
        print("1. Run 'python3 main.py' to start the server")
        print("2. Open the tool in your browser")
        print("3. Test the text highlighting feature button (should show modal, not popup)")
        print("4. Test document upload and start analysis (should work properly)")
    else:
        print("\n⚠️ Some issues detected. Please review the failed tests above.")
    
    return 0 if overall_pass else 1

if __name__ == "__main__":
    sys.exit(main())