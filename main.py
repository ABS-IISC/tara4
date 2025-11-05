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
from app import app

def main():
    """Main entry point for the application"""
    try:
        # Get port from environment or use 8000 as default
        port = int(os.environ.get('PORT', 8000))
        
        # Always use 0.0.0.0 for deployment compatibility
        host = '0.0.0.0'
        
        print(f"Starting Flask app on {host}:{port}")
        
        # Ensure required directories exist
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # Start the Flask application
        app.run(
            debug=False,
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