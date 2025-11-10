#!/usr/bin/env python3
"""
Enhanced Document Analysis Tool - Main Entry Point

A comprehensive AI-powered document analysis tool with deep investigation capabilities,
modular architecture, and responsive UI.

Features:
- Deep Document Analysis with AI-powered feedback
- Interactive UI with dark mode support
- Clickable statistics with detailed breakdowns
- Working AI chat assistant
- Pattern recognition across documents
- Activity logging and audit trails
- AI learning from user feedback
- Keyboard shortcuts for efficiency
- Responsive design for different screen sizes
- Document upload with drag-and-drop
- Real-time notifications
- Comprehensive FAQ and tutorial system

Usage:
    python main.py

The application will start on http://localhost:5000
"""

import os
import sys
import random
from app import app

def main():
    """Main entry point for the application"""
    try:
        # Load environment variables from .env file if it exists
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        # Get port from environment or generate random port
        if 'PORT' in os.environ:
            port = int(os.environ.get('PORT'))
        else:
            port = random.randint(5000, 9999)
        
        # Always use 0.0.0.0 for deployment compatibility
        host = '0.0.0.0'
        
        # Log environment info
        flask_env = os.environ.get('FLASK_ENV', 'development')
        aws_region = os.environ.get('AWS_REGION', os.environ.get('AWS_DEFAULT_REGION', 'not set'))
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'not set')
        max_tokens = os.environ.get('BEDROCK_MAX_TOKENS', '8192')
        temperature = os.environ.get('BEDROCK_TEMPERATURE', '0.7')
        reasoning_enabled = os.environ.get('REASONING_ENABLED', 'false')
        reasoning_budget = os.environ.get('REASONING_BUDGET_TOKENS', '2000')
        
        print("=" * 60)
        print("AI-PRISM DOCUMENT ANALYSIS TOOL")
        print("=" * 60)
        print(f"Server: http://{host}:{port}")
        print(f"Environment: {flask_env}")
        print(f"AWS Region: {aws_region}")
        print(f"Bedrock Model: {model_id}")
        print(f"Max Tokens: {max_tokens}")
        print(f"Temperature: {temperature}")
        print(f"Reasoning: {reasoning_enabled} (Budget: {reasoning_budget})")
        
        # Check AWS credentials
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        if aws_access_key and aws_secret_key:
            print(f"AWS Credentials: [OK] Configured")
            print(f"Real AI analysis enabled with Claude Sonnet!")
        else:
            print(f"AWS Credentials: [NOT SET] Not configured")
            print(f"Mock AI responses will be used for testing")
            print(f"Run 'python test_bedrock_connection.py' to test AWS setup")
        
        # Ensure required directories exist
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # Start the Flask application
        # Use debug=False for production (App Runner)
        debug_mode = flask_env != 'production'
        
        print(f"Debug mode: {debug_mode}")
        print("AI-Prism configured for AWS App Runner deployment")
        print("=" * 60)
        print("Ready for document analysis with Hawkeye framework!")
        print("=" * 60)
        
        app.run(
            debug=debug_mode,
            host=host,
            port=port,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        print("=" * 60)
        print("[ERROR] AI-PRISM STARTUP ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        print("Check configuration and dependencies")
        print("See AWS_SETUP_GUIDE.md for help")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()