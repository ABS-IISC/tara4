#!/usr/bin/env python3
"""
Comprehensive verification script for AI-Prism application
Tests all critical workflows and endpoints
"""

import sys
import importlib.util

def test_import(module_name, file_path=None):
    """Test if a module can be imported"""
    try:
        if file_path:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            __import__(module_name)
        print(f"✅ {module_name}: Import successful")
        return True
    except Exception as e:
        print(f"❌ {module_name}: Import failed - {str(e)}")
        return False

def test_syntax(file_path):
    """Test if a Python file has valid syntax"""
    import py_compile
    try:
        py_compile.compile(file_path, doraise=True)
        print(f"✅ {file_path}: Syntax valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ {file_path}: Syntax error - {str(e)}")
        return False

def check_function_exists(module, function_name):
    """Check if a function exists in a module"""
    try:
        func = getattr(module, function_name)
        print(f"✅ Function '{function_name}' exists")
        return True
    except AttributeError:
        print(f"❌ Function '{function_name}' not found")
        return False

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("AI-PRISM VERIFICATION TEST SUITE")
    print("=" * 60)
    print()

    results = {
        'passed': 0,
        'failed': 0
    }

    # Test 1: Syntax Checks
    print("📝 TEST 1: Syntax Validation")
    print("-" * 60)
    syntax_files = [
        'app.py',
        'main.py',
        'celery_tasks_enhanced.py',
        'core/ai_feedback_engine.py',
        'core/async_request_manager.py',
        'celery_config.py'
    ]

    for file_path in syntax_files:
        if test_syntax(file_path):
            results['passed'] += 1
        else:
            results['failed'] += 1
    print()

    # Test 2: Import Checks
    print("📦 TEST 2: Module Imports")
    print("-" * 60)

    # Test core imports
    core_modules = [
        ('flask', None),
        ('boto3', None),
        ('celery', None),
    ]

    for module_name, file_path in core_modules:
        if test_import(module_name, file_path):
            results['passed'] += 1
        else:
            results['failed'] += 1
    print()

    # Test 3: Application Structure
    print("🏗️  TEST 3: Application Structure")
    print("-" * 60)

    try:
        # Import app without running it
        import app as flask_app

        # Check critical functions exist
        functions_to_check = [
            'upload_document',
            'analyze_section',
            'get_session',
            'set_session',
            'session_exists'
        ]

        for func_name in functions_to_check:
            if hasattr(flask_app, func_name):
                print(f"✅ Function '{func_name}' exists in app.py")
                results['passed'] += 1
            else:
                print(f"❌ Function '{func_name}' missing in app.py")
                results['failed'] += 1

        # Check Flask app created
        if hasattr(flask_app, 'app'):
            print(f"✅ Flask app instance created")
            results['passed'] += 1

            # Check critical routes
            routes = [rule.rule for rule in flask_app.app.url_map.iter_rules()]
            critical_routes = [
                '/upload',
                '/analyze_section',
                '/get_section_content',
                '/chat',
                '/complete_review',
                '/health'
            ]

            for route in critical_routes:
                if route in routes:
                    print(f"✅ Route '{route}' registered")
                    results['passed'] += 1
                else:
                    print(f"❌ Route '{route}' not registered")
                    results['failed'] += 1
        else:
            print(f"❌ Flask app instance not found")
            results['failed'] += 1

    except Exception as e:
        print(f"❌ App structure test failed: {str(e)}")
        results['failed'] += 1
    print()

    # Test 4: Celery Configuration
    print("⚙️  TEST 4: Celery Configuration")
    print("-" * 60)

    try:
        import celery_config

        if hasattr(celery_config, 'celery_app'):
            print("✅ Celery app configured")
            results['passed'] += 1
        else:
            print("❌ Celery app not found")
            results['failed'] += 1

    except Exception as e:
        print(f"❌ Celery configuration test failed: {str(e)}")
        results['failed'] += 1
    print()

    # Test 5: Task Definitions
    print("📋 TEST 5: Celery Task Definitions")
    print("-" * 60)

    try:
        import celery_tasks_enhanced

        tasks = [
            'analyze_section_task',
            'process_chat_task',
            'monitor_health'
        ]

        for task_name in tasks:
            if hasattr(celery_tasks_enhanced, task_name):
                print(f"✅ Task '{task_name}' defined")
                results['passed'] += 1
            else:
                print(f"❌ Task '{task_name}' not found")
                results['failed'] += 1

    except Exception as e:
        print(f"❌ Task definitions test failed: {str(e)}")
        results['failed'] += 1
    print()

    # Test 6: Core Components
    print("🔧 TEST 6: Core Components")
    print("-" * 60)

    try:
        from core.ai_feedback_engine import AIFeedbackEngine
        from core.async_request_manager import get_async_request_manager

        # Test AIFeedbackEngine
        engine = AIFeedbackEngine()
        if hasattr(engine, 'analyze_section'):
            print("✅ AIFeedbackEngine initialized")
            results['passed'] += 1
        else:
            print("❌ AIFeedbackEngine missing analyze_section")
            results['failed'] += 1

        # Test AsyncRequestManager
        manager = get_async_request_manager()
        if manager:
            print("✅ AsyncRequestManager initialized")
            results['passed'] += 1
        else:
            print("❌ AsyncRequestManager failed to initialize")
            results['failed'] += 1

    except Exception as e:
        print(f"❌ Core components test failed: {str(e)}")
        results['failed'] += 1
    print()

    # Test 7: Critical Fixes Verification
    print("🔍 TEST 7: Critical Fixes Verification")
    print("-" * 60)

    try:
        # Check that the session_data fix was applied
        with open('app.py', 'r') as f:
            app_content = f.read()

        if 'review_session = get_session(session_id)' in app_content and \
           'sections_dict = review_session.sections' in app_content:
            print("✅ Critical fix applied: session_data → get_session()")
            results['passed'] += 1
        else:
            print("❌ Critical fix NOT applied: session_data still broken")
            results['failed'] += 1

        # Check no duplicate get_section_content
        if app_content.count('def get_section_content('):
            count = app_content.count('def get_section_content(')
            if count == 1:
                print(f"✅ No duplicate get_section_content() functions")
                results['passed'] += 1
            else:
                print(f"❌ Found {count} get_section_content() functions (should be 1)")
                results['failed'] += 1
        else:
            print("❌ get_section_content() function not found")
            results['failed'] += 1

    except Exception as e:
        print(f"❌ Fix verification test failed: {str(e)}")
        results['failed'] += 1
    print()

    # Print Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    total = results['passed'] + results['failed']
    if total > 0:
        success_rate = (results['passed'] / total) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
    print()

    if results['failed'] == 0:
        print("🎉 ALL TESTS PASSED! Application is healthy.")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED. Review issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
