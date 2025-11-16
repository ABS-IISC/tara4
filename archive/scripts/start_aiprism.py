#!/usr/bin/env python3
"""
AI-Prism Startup Script with Connection Verification
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python Version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ❌ Python 3.8+ required")
        return False
    
    print("   ✅ Python version compatible")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking Dependencies...")
    
    required_packages = [
        'flask', 'boto3', 'python-docx', 'lxml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n   💡 Install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_aws_setup():
    """Check AWS configuration"""
    print("\n🔐 Checking AWS Setup...")
    
    # Check .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("   ❌ .env file not found")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check for AWS credentials
    if 'AWS_ACCESS_KEY_ID=' in content and not content.count('AWS_ACCESS_KEY_ID=#'):
        print("   ✅ AWS credentials configured in .env")
        return True
    
    # Check AWS CLI
    aws_config = Path.home() / '.aws' / 'credentials'
    if aws_config.exists():
        print("   ✅ AWS CLI credentials found")
        return True
    
    # Check environment variables
    if os.environ.get('AWS_ACCESS_KEY_ID'):
        print("   ✅ AWS credentials in environment")
        return True
    
    print("   ❌ No AWS credentials found")
    print("   💡 Add credentials to .env file:")
    print("      AWS_ACCESS_KEY_ID=your_access_key")
    print("      AWS_SECRET_ACCESS_KEY=your_secret_key")
    return False

def test_claude_connection():
    """Test Claude connection"""
    print("\n🤖 Testing Claude Connection...")
    
    try:
        # Run the connection test
        result = subprocess.run([
            sys.executable, 'test_connection.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Claude connection test passed")
            return True
        else:
            print("   ❌ Claude connection test failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ Connection test timed out")
        return False
    except Exception as e:
        print(f"   ❌ Connection test error: {e}")
        return False

def create_directories():
    """Create required directories"""
    print("\n📁 Creating Required Directories...")
    
    directories = ['uploads', 'data']
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir()
            print(f"   ✅ Created {directory}/")
        else:
            print(f"   ✅ {directory}/ exists")
    
    return True

def start_application():
    """Start the AI-Prism application"""
    print("\n🚀 Starting AI-Prism Application...")
    
    try:
        # Import and run the app
        from app import app
        from config.model_config import model_config
        
        config = model_config.get_model_config()
        
        print("=" * 60)
        print("🎯 AI-PRISM DOCUMENT ANALYSIS TOOL")
        print("=" * 60)
        print(f"🌐 Server: http://localhost:{config['port']}")
        print(f"🏗️ Environment: {config['flask_env']}")
        print(f"🤖 AI Model: {config['model_name']}")
        print(f"🔑 AWS Credentials: {'✅ Available' if model_config.has_credentials() else '❌ Not configured'}")
        print("=" * 60)
        print("📝 Ready for document analysis!")
        print("=" * 60)
        
        app.run(
            debug=config['flask_env'] != 'production',
            host='0.0.0.0',
            port=config['port'],
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

def main():
    """Main startup function"""
    print("🔧 AI-PRISM STARTUP VERIFICATION")
    print("=" * 60)
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Check dependencies
    if not check_dependencies():
        print("\n💡 Install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 3: Create directories
    create_directories()
    
    # Step 4: Check AWS setup
    aws_ok = check_aws_setup()
    
    # Step 5: Test Claude connection (if AWS is configured)
    claude_ok = test_claude_connection() if aws_ok else False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 STARTUP VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"🐍 Python Version: ✅ OK")
    print(f"📦 Dependencies: ✅ OK")
    print(f"📁 Directories: ✅ OK")
    print(f"🔐 AWS Setup: {'✅ OK' if aws_ok else '❌ NEEDS SETUP'}")
    print(f"🤖 Claude Connection: {'✅ OK' if claude_ok else '❌ NEEDS SETUP'}")
    
    if not aws_ok:
        print("\n⚠️ AWS credentials not configured")
        print("🎭 AI-Prism will run with mock responses")
        print("💡 Configure AWS credentials for real AI analysis")
    
    if not claude_ok and aws_ok:
        print("\n⚠️ Claude connection failed")
        print("🎭 AI-Prism will run with mock responses")
        print("💡 Check AWS Bedrock access and model permissions")
    
    print("\n🚀 Starting AI-Prism...")
    print("=" * 60)
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()