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
    # Get port from environment or use 8000 as default
    port = int(os.environ.get('PORT', 8000))
    
    # Always use 0.0.0.0 for deployment compatibility
    host = '0.0.0.0'
    
    # Determine if running in production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    print("Starting Enhanced Document Analysis Tool...")
    print("Features: AI Analysis, Chat Assistant, Pattern Recognition, Learning System")
    print(f"Server will start on http://{host}:{port}")
    print("Upload .docx files for comprehensive Hawkeye framework analysis")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Ensure required directories exist
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        
        # Start the Flask application
        app.run(
            debug=not is_production,
            host=host,
            port=port,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()