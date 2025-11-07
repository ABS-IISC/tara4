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
        
        print(f"Starting AI-Prism Flask app on {host}:{port}")
        print(f"Environment: {flask_env}")
        print(f"AWS Region: {aws_region}")
        print(f"Bedrock Model: {model_id}")
        print(f"Max Tokens: {max_tokens}")
        print(f"Temperature: {temperature}")
        print(f"Reasoning Enabled: {reasoning_enabled}")
        print(f"Reasoning Budget: {reasoning_budget}")
        
        # Ensure required directories exist
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # Start the Flask application
        # Use debug=False for production (App Runner)
        debug_mode = flask_env != 'production'
        
        print(f"Debug mode: {debug_mode}")
        print("AI-Prism configured for AWS App Runner deployment")
        
        app.run(
            debug=debug_mode,
            host=host,
            port=port,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()