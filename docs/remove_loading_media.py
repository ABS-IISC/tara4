#!/usr/bin/env python3
"""
Script to remove all loadingMediaWithContent references from enhanced_index.html
"""

import re

# Read the file
with open('/Users/abhsatsa/Documents/risk stuff/tool/tara2/templates/enhanced_index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("Original file size:", len(content), "characters")

# Count original references
original_count = content.count('loadingMediaWithContent')
print(f"Found {original_count} references to 'loadingMediaWithContent'")

# Replace all references to loadingMediaWithContent with empty array or simple fallback
# Pattern 1: loadingMediaWithContent.length -> 0
content = re.sub(r'loadingMediaWithContent\.length', '0', content)

# Pattern 2: loadingMediaWithContent[...] -> empty object
content = re.sub(r'loadingMediaWithContent\[currentMediaIndex\]', '{}', content)
content = re.sub(r'loadingMediaWithContent\[[^\]]+\]', '{}', content)

# Verify changes
final_count = content.count('loadingMediaWithContent')
print(f"After replacement: {final_count} references remaining")

# Write back
with open('/Users/abhsatsa/Documents/risk stuff/tool/tara2/templates/enhanced_index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ File updated successfully!")
print("New file size:", len(content), "characters")
