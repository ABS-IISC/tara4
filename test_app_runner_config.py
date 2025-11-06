#!/usr/bin/env python3
"""
Test script to verify AWS App Runner configuration
"""
import os
import sys

def test_configuration():
    """Test the App Runner configuration"""
    print("Testing AWS App Runner Configuration")
    print("=" * 50)
    
    # Load .env file if exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print("Found .env file, loading configuration...")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    else:
        print("No .env file found")
    
    # Test environment variables
    config_vars = {
        'AWS_REGION': os.environ.get('AWS_REGION'),
        'BEDROCK_MODEL_ID': os.environ.get('BEDROCK_MODEL_ID'),
        'FLASK_ENV': os.environ.get('FLASK_ENV'),
        'PORT': os.environ.get('PORT'),
        'AWS_DEFAULT_REGION': os.environ.get('AWS_DEFAULT_REGION'),
        'BEDROCK_MAX_TOKENS': os.environ.get('BEDROCK_MAX_TOKENS'),
        'BEDROCK_TEMPERATURE': os.environ.get('BEDROCK_TEMPERATURE'),
        'REASONING_ENABLED': os.environ.get('REASONING_ENABLED'),
        'REASONING_BUDGET_TOKENS': os.environ.get('REASONING_BUDGET_TOKENS')
    }
    
    print("\nConfiguration Variables:")
    print("-" * 30)
    all_configured = True
    
    for key, value in config_vars.items():
        if value:
            print(f"OK {key}: {value}")
        else:
            print(f"MISSING {key}: NOT SET")
            all_configured = False
    
    print("\nConfiguration Analysis:")
    print("-" * 30)
    
    # Check AWS region
    aws_region = config_vars.get('AWS_REGION')
    if aws_region == 'us-east-1':
        print("OK AWS Region: Correctly set to us-east-1")
    else:
        print(f"WARNING AWS Region: {aws_region} (expected us-east-1)")
    
    # Check Bedrock model
    model_id = config_vars.get('BEDROCK_MODEL_ID')
    if model_id == 'anthropic.claude-3-7-sonnet-20250219-v1:0':
        print("OK Bedrock Model: Correctly set to Claude 3.7 Sonnet with reasoning")
    else:
        print(f"WARNING Bedrock Model: {model_id}")
    
    # Check Flask environment
    flask_env = config_vars.get('FLASK_ENV')
    if flask_env == 'production':
        print("OK Flask Environment: Production mode (App Runner ready)")
    else:
        print(f"WARNING Flask Environment: {flask_env} (should be 'production' for App Runner)")
    
    # Check port
    port = config_vars.get('PORT')
    if port == '8080':
        print("OK Port: Correctly set to 8080 (App Runner standard)")
    else:
        print(f"WARNING Port: {port} (App Runner expects 8080)")
    
    # Check reasoning configuration
    reasoning_enabled = config_vars.get('REASONING_ENABLED')
    reasoning_budget = config_vars.get('REASONING_BUDGET_TOKENS')
    if reasoning_enabled == 'true' and reasoning_budget == '2000':
        print("OK Reasoning: Enabled with 2000 token budget")
    else:
        print(f"WARNING Reasoning: enabled={reasoning_enabled}, budget={reasoning_budget}")
    
    print("\nApp Runner Readiness:")
    print("-" * 30)
    
    if all_configured:
        print("OK All configuration variables are set")
    else:
        print("ERROR Some configuration variables are missing")
    
    # Check for required files
    required_files = [
        'main.py',
        'app.py',
        'requirements.txt',
        'Dockerfile',
        'apprunner.yaml'
    ]
    
    print("\nRequired Files Check:")
    print("-" * 30)
    
    for file in required_files:
        if os.path.exists(file):
            print(f"OK {file}: Found")
        else:
            print(f"MISSING {file}: Missing")
    
    print("\nSummary:")
    print("-" * 30)
    
    if all_configured and flask_env == 'production' and port == '8080':
        print("SUCCESS: Configuration is READY for AWS App Runner deployment!")
        print("\nNext steps:")
        print("1. Deploy to ECR: ./deploy.sh us-east-1 ai-prism-app latest")
        print("2. Create App Runner service with these environment variables")
        print("3. Configure IAM role with Bedrock permissions")
    else:
        print("WARNING: Configuration needs adjustment for optimal App Runner deployment")
        print("\nRecommendations:")
        if flask_env != 'production':
            print("- Set FLASK_ENV=production for App Runner")
        if port != '8080':
            print("- Set PORT=8080 for App Runner")
        if not all_configured:
            print("- Ensure all environment variables are set")
    
    return all_configured

if __name__ == '__main__':
    test_configuration()