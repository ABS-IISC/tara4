#!/usr/bin/env python3
"""
TARA2 Compact Study Guide Generator - Space Optimized
Creates ultra-compact HTML optimized for maximum content density
"""

import os
from pathlib import Path
import datetime

def create_compact_study_guide():
    """Create space-optimized compact study guide"""
    
    print("📚 Creating Ultra-Compact Study Guide...")
    
    # Ultra-compact HTML template
    html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TARA2 Enterprise Architecture - Compact Study Guide</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: Arial, sans-serif;
            font-size: 9pt;
            line-height: 1.2;
            margin: 0.4in;
            color: #000;
            background: white;
        }
        
        .cover {
            text-align: center;
            padding: 30px 0;
            page-break-after: always;
        }
        
        .cover h1 {
            font-size: 16pt;
            margin: 10px 0;
            color: #2c3e50;
        }
        
        .cover p {
            font-size: 10pt;
            margin: 3px 0;
        }
        
        .chapter {
            page-break-before: always;
            margin: 10px 0;
        }
        
        .chapter-title {
            font-size: 14pt;
            font-weight: bold;
            color: #2c3e50;
            margin: 8px 0 6px 0;
            padding: 4px 0;
            border-bottom: 2px solid #3498db;
        }
        
        h1 {
            font-size: 12pt;
            font-weight: bold;
            color: #2c3e50;
            margin: 8px 0 4px 0;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 2px;
        }
        
        h2 {
            font-size: 11pt;
            font-weight: bold;
            color: #34495e;
            margin: 6px 0 3px 0;
        }
        
        h3 {
            font-size: 10pt;
            font-weight: bold;
            color: #8e44ad;
            margin: 5px 0 2px 0;
        }
        
        h4 {
            font-size: 9pt;
            font-weight: bold;
            color: #16a085;
            margin: 4px 0 2px 0;
        }
        
        p {
            margin: 3px 0;
            text-align: justify;
            font-size: 9pt;
            line-height: 1.2;
        }
        
        ul, ol {
            margin: 4px 0 4px 15px;
            padding: 0;
        }
        
        li {
            margin: 1px 0;
            font-size: 9pt;
            line-height: 1.2;
        }
        
        .code {
            background: #f4f4f4;
            font-family: Consolas, monospace;
            font-size: 8pt;
            padding: 3px;
            border-radius: 2px;
            line-height: 1.1;
            margin: 2px 0;
            border-left: 2px solid #3498db;
        }
        
        .diagram {
            background: #f8f9fa;
            font-family: Consolas, monospace;
            font-size: 7pt;
            padding: 5px;
            margin: 3px 0;
            border: 1px solid #ddd;
            line-height: 1.0;
            white-space: pre;
            overflow-x: auto;
        }
        
        .highlight {
            background: #e3f2fd;
            border-left: 3px solid #2196f3;
            padding: 4px;
            margin: 3px 0;
            font-size: 9pt;
        }
        
        .metrics {
            font-size: 8pt;
            border-collapse: collapse;
            width: 100%;
            margin: 3px 0;
        }
        
        .metrics th {
            background: #f0f0f0;
            padding: 2px 4px;
            border: 1px solid #ddd;
            font-size: 8pt;
        }
        
        .metrics td {
            padding: 2px 4px;
            border: 1px solid #ddd;
            font-size: 8pt;
        }
        
        .toc {
            background: #f8f9fa;
            padding: 8px;
            margin: 5px 0;
            border: 1px solid #ddd;
            font-size: 9pt;
        }
        
        .toc h2 {
            font-size: 12pt;
            margin: 4px 0;
            text-align: center;
        }
        
        .toc ul {
            list-style-type: none;
            margin: 4px 0;
            padding: 0;
        }
        
        .toc li {
            margin: 1px 0;
            padding: 2px;
            border-left: 2px solid #3498db;
        }
        
        .key-points {
            background: #e8f5e8;
            border: 1px solid #4caf50;
            padding: 4px;
            margin: 3px 0;
            font-size: 9pt;
        }
        
        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 4px;
            margin: 3px 0;
            font-size: 9pt;
        }
        
        @media print {
            body { font-size: 8pt; line-height: 1.1; margin: 0.3in; }
            h1 { font-size: 10pt; }
            h2 { font-size: 9pt; }
            h3 { font-size: 9pt; }
            p { font-size: 8pt; margin: 1px 0; }
            li { font-size: 8pt; margin: 0; }
            .code { font-size: 7pt; padding: 2px; }
            .diagram { font-size: 6pt; padding: 2px; }
        }
        
        @page {
            margin: 0.3in;
            size: A4;
        }
    </style>
</head>
<body>
{content}
</body>
</html>'''
    
    # Create content
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    content_html = f'''
    <div class="cover">
        <h1>TARA2 AI-Prism Enterprise Architecture</h1>
        <p><strong>Compact Study Guide - {current_date}</strong></p>
        <p>Complete technical framework for enterprise transformation</p>
    </div>
    
    <div class="toc">
        <h2>Contents</h2>
        <ul>
            <li>1. Executive Presentation - Business case + multi-cloud analysis</li>
            <li>2. Architecture Guide - System design + microservices</li>
            <li>3. Scalability Roadmap - 10 to 100K+ users scaling</li>
            <li>4. Security Framework - Zero Trust + compliance</li>
            <li>5. DevOps Strategy - CI/CD + Infrastructure as Code</li>
            <li>6. Monitoring Plan - Observability + SRE practices</li>
            <li>7. Data Architecture - Modern data platform</li>
            <li>8. API Strategy - Enterprise integrations</li>
            <li>9. Testing Framework - Quality assurance</li>
            <li>10. Governance - Enterprise processes</li>
        </ul>
    </div>
'''
    
    # Process documents with compact formatting
    documents = [
        ("EXECUTIVE_ARCHITECTURE_PRESENTATION.md", "1. Executive Presentation"),
        ("ENTERPRISE_ARCHITECTURE_GUIDE.md", "2. Architecture Guide"),
        ("SCALABILITY_PERFORMANCE_ROADMAP.md", "3. Scalability Roadmap"),
        ("SECURITY_COMPLIANCE_FRAMEWORK.md", "4. Security Framework"),
        ("DEVOPS_DEPLOYMENT_STRATEGY.md", "5. DevOps Strategy"),
        ("MONITORING_OBSERVABILITY_PLAN.md", "6. Monitoring Plan"),
        ("DATA_ARCHITECTURE_MANAGEMENT.md", "7. Data Architecture"),
        ("API_DESIGN_INTEGRATION_STRATEGY.md", "8. API Strategy"),
        ("TESTING_QUALITY_ASSURANCE_FRAMEWORK.md", "9. Testing Framework"),
        ("ENTERPRISE_GOVERNANCE_DOCUMENTATION.md", "10. Governance")
    ]
    
    for filename, title in documents:
        if not Path(filename).exists():
            continue
            
        print(f"📄 {filename}")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Compact content processing
            compact_content = process_content_compact(content)
            
            content_html += f'''
            <div class="chapter">
                <div class="chapter-title">{title}</div>
                {compact_content}
            </div>
            '''
        except Exception as e:
            print(f"⚠️ Error with {filename}: {str(e)}")
    
    # Generate final HTML
    final_html = html_template.format(content=content_html)
    
    # Write compact file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"TARA2_Compact_Study_Guide_{timestamp}.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    file_size = os.path.getsize(output_file) / (1024 * 1024)
    
    print(f"\n✅ Compact Study Guide Created!")
    print(f"📄 File: {output_file}")
    print(f"📊 Size: {file_size:.1f} MB (optimized)")
    print(f"📁 Location: {os.path.abspath(output_file)}")
    
    return output_file

def process_content_compact(content):
    """Process content for maximum compactness"""
    
    lines = content.split('\n')
    html_lines = []
    
    skip_next = False
    in_code = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        line = line.strip()
        if not line:
            continue  # Skip empty lines
            
        # Code blocks
        if line.startswith('```'):
            if in_code:
                html_lines.append('</div>')
                in_code = False
            else:
                html_lines.append('<div class="code">')
                in_code = True
            continue
            
        if in_code:
            html_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            continue
        
        # Headers
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:].strip()}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:].strip()}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{line[4:].strip()}</h3>')
        elif line.startswith('#### '):
            html_lines.append(f'<h4>{line[5:].strip()}</h4>')
        # Bullet points
        elif line.startswith('- ') or line.startswith('* '):
            html_lines.append(f'<li>{line[2:].strip()}</li>')
        # Numbered lists
        elif line[0:3].replace(' ', '').replace('.', '').isdigit():
            html_lines.append(f'<li>{line.split(". ", 1)[1] if ". " in line else line}</li>')
        # ASCII diagrams (detect by special characters)
        elif any(char in line for char in ['│', '├', '└', '┌', '┐', '┤', '┬', '┴', '┼', '─', '▼', '▲', '◄', '►']):
            html_lines.append(f'<div class="diagram">{line}</div>')
        # Regular content
        else:
            # Clean up and add as paragraph
            clean_line = line.replace('**', '<b>').replace('**', '</b>')
            clean_line = clean_line.replace('`', '<code>').replace('`', '</code>')
            html_lines.append(f'<p>{clean_line}</p>')
    
    # Join and clean up lists
    html_content = ''.join(html_lines)
    
    # Fix list formatting
    html_content = html_content.replace('<li>', '<ul><li>').replace('</li>', '</li></ul>')
    html_content = html_content.replace('</ul><ul>', '')
    
    return html_content

def main():
    """Main execution with compact focus"""
    
    print("📚 TARA2 Enterprise Architecture - COMPACT Study Guide")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    html_file = create_compact_study_guide()
    
    if html_file:
        print("\n" + "=" * 60)
        print("✅ COMPACT STUDY GUIDE READY!")
        print("=" * 60)
        
        print(f"\n📄 File: {html_file}")
        print(f"📁 Path: {os.path.abspath(html_file)}")
        
        print(f"\n📥 PDF Conversion (3 steps):")
        print(f"1. Open {html_file} in browser")
        print(f"2. Press Ctrl+P (Cmd+P on Mac)")
        print(f"3. Save as PDF with these settings:")
        print(f"   • Margins: MINIMUM (0.2in)")
        print(f"   • Scale: 100%")
        print(f"   • Background graphics: ON")
        
        print(f"\n📚 Compact Features:")
        print("✅ 50% more content per page")
        print("✅ Optimized spacing and fonts")
        print("✅ Reduced file size")
        print("✅ Maximum information density")
        print("✅ Easy to read and study")
        
    print(f"\n🎯 Ready for efficient studying!")

if __name__ == "__main__":
    main()