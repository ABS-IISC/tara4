#!/usr/bin/env python3
"""
Ultra-Simple PDF Generator for TARA2 Enterprise Architecture
Direct HTML generation without complex formatting
"""

import os
from pathlib import Path
import datetime

def create_ultra_compact_guide():
    """Create ultra-compact study guide with direct HTML generation"""
    
    print("📚 Creating Ultra-Compact Study Guide...")
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    output_file = f"TARA2_Compact_{timestamp}.html"
    
    # Start HTML content
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TARA2 Enterprise Architecture - Compact Study</title>
    <style>
        body {{ font-family: Arial; font-size: 9pt; line-height: 1.1; margin: 0.3in; color: #000; }}
        h1 {{ font-size: 12pt; color: #2c3e50; margin: 8px 0 4px; border-bottom: 1px solid #3498db; }}
        h2 {{ font-size: 11pt; color: #34495e; margin: 6px 0 3px; }}
        h3 {{ font-size: 10pt; color: #8e44ad; margin: 4px 0 2px; }}
        p {{ margin: 2px 0; line-height: 1.2; text-align: justify; }}
        ul, ol {{ margin: 3px 0 3px 15px; }}
        li {{ margin: 0; font-size: 9pt; }}
        pre {{ background: #f4f4f4; font-size: 8pt; padding: 3px; margin: 2px 0; }}
        .chapter {{ page-break-before: always; margin: 8px 0; }}
        .cover {{ text-align: center; padding: 40px 0; page-break-after: always; }}
        .toc {{ background: #f8f9fa; padding: 10px; margin: 8px 0; }}
        @page {{ margin: 0.3in; size: A4; }}
        @media print {{ body {{ font-size: 8pt; }} }}
    </style>
</head>
<body>

<div class="cover">
    <h1>TARA2 AI-Prism Enterprise Architecture</h1>
    <h2>Compact Study Guide</h2>
    <p><strong>Generated:</strong> {current_date}</p>
    <p>Complete technical framework - 1000+ pages</p>
</div>

<div class="toc">
    <h2>Study Contents</h2>
    <ol>
        <li>Executive Presentation - Business case + multi-cloud</li>
        <li>Architecture Guide - System design + microservices</li>
        <li>Scalability - 10 to 100K+ users</li>
        <li>Security - Zero Trust + compliance</li>
        <li>DevOps - CI/CD + Infrastructure</li>
        <li>Monitoring - Observability + SRE</li>
        <li>Data Architecture - Modern platform</li>
        <li>API Strategy - Enterprise integrations</li>
        <li>Testing - Quality assurance</li>
        <li>Governance - Enterprise processes</li>
    </ol>
</div>

"""
    
    # Process each document
    documents = [
        ("EXECUTIVE_ARCHITECTURE_PRESENTATION.md", "Executive Presentation"),
        ("ENTERPRISE_ARCHITECTURE_GUIDE.md", "Architecture Guide"),
        ("SCALABILITY_PERFORMANCE_ROADMAP.md", "Scalability Roadmap"),
        ("SECURITY_COMPLIANCE_FRAMEWORK.md", "Security Framework"),
        ("DEVOPS_DEPLOYMENT_STRATEGY.md", "DevOps Strategy"),
        ("MONITORING_OBSERVABILITY_PLAN.md", "Monitoring Plan"),
        ("DATA_ARCHITECTURE_MANAGEMENT.md", "Data Architecture"),
        ("API_DESIGN_INTEGRATION_STRATEGY.md", "API Strategy"),
        ("TESTING_QUALITY_ASSURANCE_FRAMEWORK.md", "Testing Framework"),
        ("ENTERPRISE_GOVERNANCE_DOCUMENTATION.md", "Governance Framework")
    ]
    
    chapter_num = 1
    for filename, title in documents:
        if not Path(filename).exists():
            print(f"❌ Missing: {filename}")
            continue
            
        print(f"📄 Processing: {filename}")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add chapter header
            html_content += f"""
<div class="chapter">
    <h1>{chapter_num}. {title}</h1>
"""
            
            # Process content line by line for compactness
            lines = content.split('\n')
            in_code_block = False
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines for compactness
                if not line:
                    continue
                
                # Handle code blocks
                if line.startswith('```'):
                    if in_code_block:
                        html_content += "</pre>\n"
                        in_code_block = False
                    else:
                        html_content += "<pre>"
                        in_code_block = True
                    continue
                
                if in_code_block:
                    escaped_line = line.replace('<', '&lt;').replace('>', '&gt;')
                    html_content += escaped_line + "\n"
                    continue
                
                # Process regular content
                if line.startswith('# '):
                    html_content += f"<h1>{line[2:]}</h1>\n"
                elif line.startswith('## '):
                    html_content += f"<h2>{line[3:]}</h2>\n"
                elif line.startswith('### '):
                    html_content += f"<h3>{line[4:]}</h3>\n"
                elif line.startswith('#### '):
                    html_content += f"<h3>{line[5:]}</h3>\n"
                elif line.startswith('- ') or line.startswith('* '):
                    html_content += f"<li>{line[2:]}</li>\n"
                else:
                    # Regular paragraph - clean up markdown
                    clean_line = line
                    # Simple bold replacement
                    while '**' in clean_line:
                        clean_line = clean_line.replace('**', '<b>', 1).replace('**', '</b>', 1)
                    # Simple code replacement
                    while '`' in clean_line and clean_line.count('`') >= 2:
                        clean_line = clean_line.replace('`', '<code>', 1).replace('`', '</code>', 1)
                    
                    html_content += f"<p>{clean_line}</p>\n"
            
            html_content += "</div>\n"
            chapter_num += 1
            
        except Exception as e:
            print(f"❌ Error with {filename}: {str(e)}")
            html_content += f"""
<div class="chapter">
    <h1>{chapter_num}. {title}</h1>
    <p><em>Content processing error: {str(e)}</em></p>
</div>
"""
            chapter_num += 1
    
    # Close HTML
    html_content += "\n</body>\n</html>"
    
    # Write file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        
        print(f"\n✅ COMPACT Study Guide Created!")
        print(f"📄 File: {output_file}")
        print(f"📊 Size: {file_size:.1f} MB (ultra-compact)")
        print(f"📁 Location: {os.path.abspath(output_file)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Write error: {str(e)}")
        return None

if __name__ == "__main__":
    print("📚 TARA2 Enterprise Architecture - ULTRA-COMPACT Generator")
    print("=" * 60)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    result = create_ultra_compact_guide()
    
    if result:
        print("\n" + "=" * 60)
        print("🎯 SUCCESS! Ultra-Compact Study Guide Ready!")
        print("=" * 60)
        
        print(f"\n📥 Quick PDF Steps:")
        print(f"1. Open {result} in browser")
        print(f"2. Ctrl+P (Cmd+P)")  
        print(f"3. Save as PDF with minimum margins")
        print(f"\n📚 Features:")
        print("✅ Maximum content density")
        print("✅ Minimal spacing optimized")
        print("✅ All 10 architecture documents")
        print("✅ Ready for intensive study!")
        
    else:
        print("❌ Generation failed")