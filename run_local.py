#!/usr/bin/env python3
"""
Local Development Runner for TARA
Forces mock mode for development without AWS credentials
"""

import os
import sys

# Force mock mode by ensuring no AWS credentials are detected
os.environ.pop('AWS_ACCESS_KEY_ID', None)
os.environ.pop('AWS_SECRET_ACCESS_KEY', None)
os.environ.pop('AWS_PROFILE', None)

# Set development mode
os.environ['FLASK_ENV'] = 'development'
os.environ['TARA_MOCK_MODE'] = 'true'

# Import and run the main application
from main import main

if __name__ == '__main__':
    print("Starting TARA in LOCAL MOCK MODE")
    print("AWS credentials disabled - using mock AI responses")
    print("All features will work with sample data")
    print("-" * 50)
    main()