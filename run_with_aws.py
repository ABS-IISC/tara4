#!/usr/bin/env python3
"""
Run AI-Prism with AWS credentials properly configured
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Setup AWS environment variables from existing credentials"""
    
    # Set AWS credentials from environment or AWS profile
    # Replace with your actual AWS credentials or use AWS CLI profile
    os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID', 'YOUR_ACCESS_KEY_HERE')
    os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY', 'YOUR_SECRET_KEY_HERE')
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    # Set Bedrock model configuration
    os.environ['BEDROCK_MODEL_ID'] = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    os.environ['BEDROCK_MAX_TOKENS'] = '8192'
    os.environ['BEDROCK_TEMPERATURE'] = '0.7'
    
    print("✅ AWS credentials configured")
    print("✅ Bedrock model configured")

def run_application():
    """Run the main application"""
    try:
        # Import and run main
        from main import main
        main()
    except ImportError:
        # Fallback to subprocess if import fails
        subprocess.run([sys.executable, 'main.py'])

if __name__ == "__main__":
    print("🚀 Starting AI-Prism with AWS credentials...")
    setup_environment()
    run_application()