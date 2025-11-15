#!/usr/bin/env python3
"""
Test App Runner startup with import fixes
"""

import os
import sys

# Set App Runner environment
os.environ['BEDROCK_MODEL_ID'] = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['FLASK_ENV'] = 'production'
os.environ['PORT'] = '8080'

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    
    try:
        # Test main app import
        from app import app
        print("✅ Flask app imported successfully")
        
        # Test that app has routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        print(f"✅ {len(routes)} routes registered")
        
        # Test key routes exist
        essential_routes = ['/', '/upload', '/complete_review']
        for route in essential_routes:
            if route in routes:
                print(f"✅ Route {route} available")
            else:
                print(f"❌ Route {route} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from app import model_config
        config = model_config.get_model_config()
        
        print(f"✅ Model: {config.get('model_name', 'Unknown')}")
        print(f"✅ Port: {config.get('port', 'Unknown')}")
        print(f"✅ Environment: {config.get('flask_env', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {str(e)}")
        return False

def test_startup_simulation():
    """Simulate app startup without actually running server"""
    print("\nTesting startup simulation...")
    
    try:
        # Import main without running
        import main
        
        # Test that main module loads
        print("✅ main.py module loaded")
        
        # Check environment variables
        required_vars = ['BEDROCK_MODEL_ID', 'AWS_REGION', 'FLASK_ENV', 'PORT']
        for var in required_vars:
            value = os.environ.get(var)
            if value:
                print(f"✅ {var}: {value}")
            else:
                print(f"❌ {var}: Not set")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Startup simulation failed: {str(e)}")
        return False

def main():
    """Run App Runner startup tests"""
    print("APP RUNNER STARTUP TEST")
    print("=" * 40)
    
    tests = {
        'imports': test_imports(),
        'config': test_config(),
        'startup': test_startup_simulation()
    }
    
    print(f"\n{'='*40}")
    print("TEST RESULTS")
    print("=" * 40)
    
    for test_name, result in tests.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.title()}: {status}")
    
    all_passed = all(tests.values())
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ App Runner deployment should work")
        print(f"✅ Import issues resolved")
        print(f"✅ Configuration working")
        print(f"✅ Environment variables set")
    else:
        print(f"\n⚠️ Some tests failed")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)