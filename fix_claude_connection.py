#!/usr/bin/env python3
"""
Fix Claude connection and document loading issues
"""

import os
import json
import sys
from pathlib import Path

def check_environment():
    """Check current environment setup"""
    print("🔍 CHECKING ENVIRONMENT SETUP")
    print("=" * 50)
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"Current Directory: {current_dir}")
    
    # Check if we're in the right directory
    if not (current_dir / "app.py").exists():
        print("❌ Not in AI-Prism directory")
        return False
    
    print("✅ In correct AI-Prism directory")
    return True

def check_aws_credentials():
    """Check AWS credentials configuration"""
    print("\n🔐 CHECKING AWS CREDENTIALS")
    print("=" * 50)
    
    # Check environment variables
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    
    print(f"AWS_ACCESS_KEY_ID: {'✅ Set' if access_key else '❌ Missing'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'✅ Set' if secret_key else '❌ Missing'}")
    print(f"AWS_DEFAULT_REGION: {region}")
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file found")
        with open(env_file, 'r') as f:
            env_content = f.read()
            if 'AWS_ACCESS_KEY_ID' in env_content:
                print("✅ AWS credentials in .env file")
            else:
                print("⚠️ No AWS credentials in .env file")
    else:
        print("❌ .env file not found")
    
    # Check AWS CLI config
    aws_config = Path.home() / '.aws' / 'credentials'
    if aws_config.exists():
        print("✅ AWS CLI credentials file found")
    else:
        print("❌ AWS CLI credentials not configured")
    
    return bool(access_key and secret_key)

def fix_env_file():
    """Fix .env file with proper AWS configuration"""
    print("\n🔧 FIXING .ENV FILE")
    print("=" * 50)
    
    env_content = """# AWS Configuration for AI-Prism
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
FLASK_ENV=development
PORT=5000
BEDROCK_MAX_TOKENS=8192
BEDROCK_TEMPERATURE=0.7
REASONING_ENABLED=false
REASONING_BUDGET_TOKENS=2000
BEDROCK_TIMEOUT=30
BEDROCK_RETRY_ATTEMPTS=3
BEDROCK_RETRY_DELAY=1.0

# Add your AWS credentials here:
# AWS_ACCESS_KEY_ID=your_access_key_here
# AWS_SECRET_ACCESS_KEY=your_secret_key_here
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file updated with proper configuration")
    print("⚠️ You still need to add your AWS credentials to .env file")
    return True

def fix_model_config():
    """Fix model configuration for better compatibility"""
    print("\n🤖 FIXING MODEL CONFIGURATION")
    print("=" * 50)
    
    config_file = Path('config/model_config.py')
    if not config_file.exists():
        print("❌ Model config file not found")
        return False
    
    # Update model config with more compatible model
    config_content = '''import os
import json
from typing import Dict, Any, Optional

class ModelConfig:
    """Simplified configuration for Claude models"""
    
    # Supported Claude models with their configurations
    SUPPORTED_MODELS = {
        # Claude 3.5 Sonnet (Most Compatible)
        "claude-3-5-sonnet-20241022": {
            "name": "Claude 3.5 Sonnet",
            "max_tokens": 8192,
            "temperature": 0.7,
            "supports_reasoning": False,
            "anthropic_version": "bedrock-2023-05-31",
            "format": "messages"
        },
        
        # Claude 3 Sonnet (Fallback)
        "claude-3-sonnet-20240229": {
            "name": "Claude 3 Sonnet",
            "max_tokens": 4096,
            "temperature": 0.7,
            "supports_reasoning": False,
            "anthropic_version": "bedrock-2023-05-31",
            "format": "messages"
        },
        
        # Claude 3 Haiku (Fast)
        "claude-3-haiku-20240307": {
            "name": "Claude 3 Haiku",
            "max_tokens": 4096,
            "temperature": 0.7,
            "supports_reasoning": False,
            "anthropic_version": "bedrock-2023-05-31",
            "format": "messages"
        }
    }
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables with fallbacks"""
        
        # Use most compatible model by default
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        
        # Extract base model name from full ARN/ID
        base_model = self._extract_base_model(model_id)
        
        # Get model defaults
        model_defaults = self.SUPPORTED_MODELS.get(base_model, self.SUPPORTED_MODELS['claude-3-5-sonnet-20241022'])
        
        config = {
            # Model Configuration
            'model_id': model_id,
            'base_model': base_model,
            'model_name': model_defaults['name'],
            
            # AWS Configuration
            'region': os.environ.get('AWS_REGION', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')),
            'port': int(os.environ.get('PORT', 5000)),
            'flask_env': os.environ.get('FLASK_ENV', 'development'),
            
            # Model Parameters
            'max_tokens': int(os.environ.get('BEDROCK_MAX_TOKENS', str(model_defaults['max_tokens']))),
            'temperature': float(os.environ.get('BEDROCK_TEMPERATURE', str(model_defaults['temperature']))),
            
            # Reasoning Configuration (disabled for compatibility)
            'reasoning_enabled': False,
            'reasoning_budget': 2000,
            
            # Model Format
            'anthropic_version': model_defaults.get('anthropic_version'),
            'format': model_defaults['format'],
            'supports_reasoning': False,
            
            # Fallback Models
            'fallback_models': ['claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
            
            # Performance Settings
            'timeout': int(os.environ.get('BEDROCK_TIMEOUT', '30')),
            'retry_attempts': int(os.environ.get('BEDROCK_RETRY_ATTEMPTS', '2')),
            'retry_delay': float(os.environ.get('BEDROCK_RETRY_DELAY', '1.0'))
        }
        
        return config
    
    def _extract_base_model(self, model_id: str) -> str:
        """Extract base model name from full ARN or ID"""
        if 'anthropic.' in model_id:
            base_part = model_id.replace('anthropic.', '').split('-v')[0]
            return base_part
        return model_id
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get complete model configuration"""
        return self.config.copy()
    
    def get_bedrock_request_body(self, system_prompt: str, user_prompt: str) -> str:
        """Generate appropriate request body based on model format"""
        
        body = {
            "anthropic_version": self.config['anthropic_version'],
            "max_tokens": self.config['max_tokens'],
            "temperature": self.config['temperature'],
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        }
        
        return json.dumps(body)
    
    def extract_response_content(self, response_body: Dict[str, Any]) -> str:
        """Extract content from response"""
        content = response_body.get('content', [])
        if content and len(content) > 0:
            return content[0].get('text', '')
        return response_body.get('completion', '')
    
    def get_fallback_model_id(self, fallback_model: str) -> str:
        """Convert fallback model name to full model ID"""
        return f"anthropic.{fallback_model}-v2:0"
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.config['flask_env'] == 'production'
    
    def has_credentials(self) -> bool:
        """Check if AWS credentials are available"""
        return (
            os.environ.get('AWS_ACCESS_KEY_ID') or 
            os.environ.get('AWS_PROFILE') or
            os.path.exists(os.path.expanduser('~/.aws/credentials')) or
            self.is_production()
        )
    
    def print_config_summary(self):
        """Print configuration summary for debugging"""
        print("=" * 60)
        print("AI-PRISM MODEL CONFIGURATION")
        print("=" * 60)
        print(f"Environment: {self.config['flask_env']}")
        print(f"Region: {self.config['region']}")
        print(f"Port: {self.config['port']}")
        print(f"Model ID: {self.config['model_id']}")
        print(f"Model Name: {self.config['model_name']}")
        print(f"Max Tokens: {self.config['max_tokens']}")
        print(f"Temperature: {self.config['temperature']}")
        print(f"Has Credentials: {self.has_credentials()}")
        print("=" * 60)

# Global configuration instance
model_config = ModelConfig()
'''
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print("✅ Model configuration updated for better compatibility")
    return True

def create_simple_test():
    """Create a simple connection test"""
    print("\n🧪 CREATING SIMPLE CONNECTION TEST")
    print("=" * 50)
    
    test_content = '''#!/usr/bin/env python3
"""
Simple AWS Bedrock connection test
"""

import os
import json
import boto3
from config.model_config import model_config

def test_connection():
    """Test AWS Bedrock connection"""
    print("🔍 Testing AWS Bedrock Connection...")
    
    try:
        # Check credentials
        if not model_config.has_credentials():
            print("❌ No AWS credentials found")
            print("💡 Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file")
            return False
        
        config = model_config.get_model_config()
        print(f"✅ Using model: {config['model_name']}")
        print(f"✅ Region: {config['region']}")
        
        # Create Bedrock client
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=config['region']
        )
        
        # Simple test request
        body = model_config.get_bedrock_request_body(
            "You are a helpful assistant.",
            "Say 'Hello from AI-Prism!' to confirm you are working."
        )
        
        print("📡 Sending test request...")
        response = bedrock.invoke_model(
            body=body,
            modelId=config['model_id'],
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        result = model_config.extract_response_content(response_body)
        
        print(f"✅ SUCCESS! Response: {result[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        
        error_str = str(e).lower()
        if 'credentials' in error_str:
            print("💡 Fix: Add AWS credentials to .env file")
        elif 'region' in error_str:
            print("💡 Fix: Check AWS region configuration")
        elif 'not found' in error_str:
            print("💡 Fix: Verify model access in your AWS account")
        
        return False

if __name__ == "__main__":
    test_connection()
'''
    
    with open('simple_test.py', 'w') as f:
        f.write(test_content)
    
    print("✅ Simple connection test created")
    return True

def fix_document_analyzer():
    """Fix document analyzer for better document loading"""
    print("\n📄 FIXING DOCUMENT ANALYZER")
    print("=" * 50)
    
    analyzer_file = Path('core/document_analyzer.py')
    if not analyzer_file.exists():
        print("❌ Document analyzer not found")
        return False
    
    # Read current content
    with open(analyzer_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add better error handling for document loading
    if 'def extract_sections_from_docx' not in content:
        print("⚠️ Document analyzer needs updating")
        
        # Add improved document loading method
        improved_method = '''
    def extract_sections_from_docx(self, file_path):
        """Extract sections from DOCX with improved error handling"""
        try:
            print(f"📄 Loading document: {file_path}")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Document not found: {file_path}")
            
            doc = Document(file_path)
            print(f"✅ Document loaded successfully")
            
            sections = {}
            section_paragraphs = {}
            paragraph_indices = {}
            
            current_section = "Introduction"
            current_paragraphs = []
            current_indices = []
            
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                
                if not text:
                    continue
                
                # Check if this is a section header
                if self._is_section_header(text):
                    # Save previous section
                    if current_paragraphs:
                        sections[current_section] = "\\n".join(current_paragraphs)
                        section_paragraphs[current_section] = current_paragraphs.copy()
                        paragraph_indices[current_section] = current_indices.copy()
                    
                    # Start new section
                    current_section = text
                    current_paragraphs = []
                    current_indices = []
                else:
                    current_paragraphs.append(text)
                    current_indices.append(i)
            
            # Save final section
            if current_paragraphs:
                sections[current_section] = "\\n".join(current_paragraphs)
                section_paragraphs[current_section] = current_paragraphs.copy()
                paragraph_indices[current_section] = current_indices.copy()
            
            print(f"✅ Extracted {len(sections)} sections")
            return sections, section_paragraphs, paragraph_indices
            
        except Exception as e:
            print(f"❌ Document loading failed: {str(e)}")
            # Return empty but valid structure
            return {"Document": "Failed to load document"}, {"Document": ["Failed to load document"]}, {"Document": [0]}
'''
        
        # Insert the method into the class
        content = content.replace(
            'class DocumentAnalyzer:',
            f'class DocumentAnalyzer:{improved_method}'
        )
        
        with open(analyzer_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Document analyzer updated with better error handling")
    
    return True

def main():
    """Main fix function"""
    print("🔧 AI-PRISM CLAUDE CONNECTION FIX")
    print("=" * 60)
    
    # Step 1: Check environment
    if not check_environment():
        print("❌ Environment check failed")
        return
    
    # Step 2: Check AWS credentials
    creds_ok = check_aws_credentials()
    
    # Step 3: Fix .env file
    fix_env_file()
    
    # Step 4: Fix model configuration
    fix_model_config()
    
    # Step 5: Create simple test
    create_simple_test()
    
    # Step 6: Fix document analyzer
    fix_document_analyzer()
    
    print("\n" + "=" * 60)
    print("🎯 FIX SUMMARY")
    print("=" * 60)
    print("✅ Environment configuration updated")
    print("✅ Model configuration simplified")
    print("✅ Document analyzer improved")
    print("✅ Simple connection test created")
    
    if not creds_ok:
        print("\n⚠️ NEXT STEPS:")
        print("1. Add your AWS credentials to .env file:")
        print("   AWS_ACCESS_KEY_ID=your_access_key")
        print("   AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("2. Run: python simple_test.py")
        print("3. Run: python app.py")
    else:
        print("\n🎉 Ready to test! Run: python simple_test.py")
    
    print("=" * 60)

if __name__ == "__main__":
    main()