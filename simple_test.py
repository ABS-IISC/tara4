#!/usr/bin/env python3
"""
Simple test to verify the HTTP 500 fix
"""

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from core.document_analyzer import DocumentAnalyzer
        print("   DocumentAnalyzer imported OK")
        
        from core.ai_feedback_engine import AIFeedbackEngine
        print("   AIFeedbackEngine imported OK")
        
        from config.model_config import model_config
        print("   model_config imported OK")
        
        from app import app
        print("   Flask app imported OK")
        
        return True
        
    except Exception as e:
        print(f"   Import failed: {e}")
        return False

def test_document_analyzer():
    """Test document analyzer with error handling"""
    print("\nTesting DocumentAnalyzer...")
    
    try:
        from core.document_analyzer import DocumentAnalyzer
        analyzer = DocumentAnalyzer()
        print("   DocumentAnalyzer initialized OK")
        
        # Test with non-existent file (should handle gracefully)
        sections, paragraphs, indices = analyzer.extract_sections_from_docx("nonexistent.docx")
        print(f"   Error handling works: {len(sections)} sections returned")
        
        return True
        
    except Exception as e:
        print(f"   DocumentAnalyzer test failed: {e}")
        return False

def main():
    """Run basic tests"""
    print("HTTP 500 ERROR FIX VERIFICATION")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test document analyzer
    analyzer_ok = test_document_analyzer()
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST RESULTS")
    print("=" * 40)
    print(f"Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"Document Analyzer: {'PASS' if analyzer_ok else 'FAIL'}")
    
    if imports_ok and analyzer_ok:
        print("\nALL TESTS PASSED!")
        print("HTTP 500 error should be fixed")
        print("Ready to run: py main.py")
    else:
        print("\nSOME TESTS FAILED")
        print("Check error messages above")
    
    print("=" * 40)

if __name__ == "__main__":
    main()