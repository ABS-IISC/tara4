#!/usr/bin/env python3
"""
Model Configuration Verification Script
Checks that all Claude models are properly configured in both:
1. config/model_config.py
2. apprunner.yaml
"""

import os
import re
import sys
from config.model_config import ModelConfig

def extract_models_from_yaml(yaml_path):
    """Extract all model names mentioned in apprunner.yaml"""
    with open(yaml_path, 'r') as f:
        content = f.read()

    # Find all claude model references in comments and values
    model_pattern = r'claude-[\w-]+-\d{8}'
    models = set(re.findall(model_pattern, content))

    return sorted(models)

def extract_models_from_config():
    """Extract all model names from model_config.py"""
    config = ModelConfig()
    return sorted(config.SUPPORTED_MODELS.keys())

def compare_models():
    """Compare models between YAML and Python config"""

    print("="*70)
    print("🔍 CLAUDE MODEL CONFIGURATION VERIFICATION")
    print("="*70)

    # Get models from both sources
    yaml_path = 'apprunner.yaml'
    yaml_models = extract_models_from_yaml(yaml_path)
    config_models = extract_models_from_config()

    print(f"\n📄 Models in apprunner.yaml: {len(yaml_models)}")
    print(f"🐍 Models in model_config.py: {len(config_models)}")

    # Find models in YAML but not in config
    yaml_only = set(yaml_models) - set(config_models)

    # Find models in config but not in YAML
    config_only = set(config_models) - set(yaml_models)

    # Check sync status
    print(f"\n{'='*70}")
    print("📊 COMPARISON RESULTS")
    print(f"{'='*70}")

    if not yaml_only and not config_only:
        print("✅ PERFECT SYNC - All models match!")
        print(f"   {len(config_models)} models configured in both files")
    else:
        if yaml_only:
            print(f"\n⚠️  Models in apprunner.yaml but NOT in model_config.py:")
            for model in sorted(yaml_only):
                print(f"   - {model}")

        if config_only:
            print(f"\n⚠️  Models in model_config.py but NOT in apprunner.yaml:")
            for model in sorted(config_only):
                print(f"   - {model}")

    # List all configured models by generation
    print(f"\n{'='*70}")
    print("📋 ALL CONFIGURED MODELS (BY GENERATION)")
    print(f"{'='*70}")

    config = ModelConfig()

    # Group by generation
    generations = {
        'Claude 4.5': [],
        'Claude 4.1': [],
        'Claude 4': [],
        'Claude 3.7': [],
        'Claude 3.5': [],
        'Claude 3': []
    }

    for model_name, model_info in config.SUPPORTED_MODELS.items():
        name = model_info['name']
        for gen in generations.keys():
            if gen in name:
                generations[gen].append(model_name)
                break

    for gen, models in generations.items():
        if models:
            print(f"\n🤖 {gen}:")
            for model in sorted(models):
                model_info = config.SUPPORTED_MODELS[model]
                reasoning = "🧠" if model_info.get('supports_reasoning') else "  "
                print(f"   {reasoning} {model}")

    print(f"\n{'='*70}")
    print("🎯 CURRENT CONFIGURATION")
    print(f"{'='*70}")

    current_config = config.get_model_config()
    print(f"Primary Model: {current_config['model_name']}")
    print(f"Model ID: {current_config['model_id']}")
    print(f"Region: {current_config['region']}")
    print(f"Max Tokens: {current_config['max_tokens']}")
    print(f"Temperature: {current_config['temperature']}")
    print(f"Reasoning: {'✅ Enabled' if current_config.get('reasoning_enabled') else '❌ Disabled'}")

    print(f"\n{'='*70}")
    print("🔄 FALLBACK MODELS (IN PRIORITY ORDER)")
    print(f"{'='*70}")

    for i, fallback in enumerate(current_config['fallback_models'][:10], 1):
        print(f"{i:2d}. {fallback}")

    print(f"\n{'='*70}")
    print("✅ VERIFICATION COMPLETE")
    print(f"{'='*70}")

    return len(yaml_only) == 0 and len(config_only) == 0

def test_model_id_conversion():
    """Test that all models can be converted to proper Bedrock IDs"""
    print(f"\n{'='*70}")
    print("🔧 TESTING MODEL ID CONVERSION")
    print(f"{'='*70}")

    config = ModelConfig()
    errors = []

    for model_name in config.SUPPORTED_MODELS.keys():
        try:
            # Test conversion
            model_id = config.get_fallback_model_id(model_name)

            # Verify format
            if not model_id.startswith(('anthropic.', 'us.anthropic.')):
                errors.append(f"❌ {model_name}: Invalid prefix - {model_id}")
            elif not model_id.endswith(('-v1:0', '-v2:0')):
                errors.append(f"❌ {model_name}: Invalid suffix - {model_id}")
            else:
                print(f"✅ {model_name}")
                print(f"   → {model_id}")
        except Exception as e:
            errors.append(f"❌ {model_name}: {str(e)}")

    if errors:
        print(f"\n⚠️  ERRORS FOUND:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print(f"\n✅ All {len(config.SUPPORTED_MODELS)} models can be converted correctly!")
        return True

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 STARTING MODEL CONFIGURATION VERIFICATION")
    print("="*70 + "\n")

    # Run comparisons
    sync_ok = compare_models()
    conversion_ok = test_model_id_conversion()

    # Final result
    print(f"\n{'='*70}")
    print("🏁 FINAL RESULT")
    print(f"{'='*70}")

    if sync_ok and conversion_ok:
        print("✅ SUCCESS - All models properly configured!")
        print("   - apprunner.yaml and model_config.py are in sync")
        print("   - All models can be converted to Bedrock IDs")
        print("   - Ready for deployment!")
        exit(0)
    else:
        print("⚠️  ISSUES FOUND - Review output above")
        if not sync_ok:
            print("   - Models are not in sync between files")
        if not conversion_ok:
            print("   - Some models cannot be converted properly")
        exit(1)
