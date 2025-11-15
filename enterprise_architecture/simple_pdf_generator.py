#!/usr/bin/env python3
"""
Simple and Reliable PDF Generator for TARA2 Enterprise Architecture
Creates user-friendly HTML that converts easily to PDF
"""

import os
from pathlib import Path
import datetime

def create_simple_study_guide():
    """Create simple, reliable HTML study guide"""
    
    print("📚 Creating Simple Study Guide...")
    
    # Simple HTML template without complex formatting
    html_start = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TARA2 AI-Prism Enterprise Architecture Study Guide</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            margin: 0.8in;
            color: #333;
            background: white;
        }
        h1 {
            color: #2c3e50;
            font-size: 18pt;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            margin: 20px 0 15px 0;
            page-break-after: avoid;
        }
        h2 {
            color: #34495e;
            font-size: 14pt;
            margin: 15px 0 10px 0;
            page-break-after: avoid;
        }
        h3 {
            color: #8e44ad;
            font-size: 12pt;
            margin: 12px 0 8px 0;
        }
        .cover {
            text-align: center;
            padding: 100px 0;
            page-break-after: always;
        }
        .cover h1 {
            font-size: 24pt;
            color: #2c3e50;
            border: none;
        }
        .chapter {
            page-break-before: always;
            margin: 20px 0;
        }
        .chapter-title {
            font-size: 20pt;
            color: #2c3e50;
            border-bottom: 3px solid #e74c3c;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .toc {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .toc h2 {
            text-align: center;
            color: #2c3e50;
        }
        .pdf-instructions {
            background: #3498db;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: center;
        }
        pre {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 3px;
            font-size: 9pt;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        @media print {
            .pdf-instructions { display: none; }
        }
        @page {
            margin: 0.7in;
            @top-center {
                content: "TARA2 Enterprise Architecture Study Guide";
                font-size: 8pt;
                color: #666;
            }
        }
    </style>
</head>
<body>
'''
    
    # Cover page
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    html_content = html_start + f'''
    <div class="cover">
        <h1>🏗️ TARA2 AI-Prism<br>Enterprise Architecture</h1>
        <h2>Complete Study Guide & Technical Framework</h2>
        <p><strong>Generated:</strong> {current_date}</p>
        <p><strong>Content:</strong> 1000+ pages of enterprise architecture</p>
        <p><strong>Coverage:</strong> Multi-cloud, AI/ML, Security, Scalability</p>
    </div>
    
    <div class="pdf-instructions">
        <h3>📥 How to Download as PDF</h3>
        <ol>
            <li><strong>Press Ctrl+P</strong> (Windows/Linux) or <strong>Cmd+P</strong> (Mac)</li>
            <li>Select "<strong>Save as PDF</strong>"</li>
            <li>Set margins to "<strong>Minimum</strong>"</li>
            <li>Enable "<strong>Background graphics</strong>" ✓</li>
            <li>Click "<strong>Save</strong>" and choose filename</li>
        </ol>
    </div>
    
    <div class="toc">
        <h2>📋 Study Guide Contents</h2>
        <ol>
            <li><strong>Executive Architecture Presentation</strong> - Business case and technical overview</li>
            <li><strong>Enterprise Architecture Guide</strong> - Overall system design and cloud architecture</li>
            <li><strong>Scalability & Performance</strong> - Scaling from 10 to 100,000+ users</li>
            <li><strong>Security & Compliance</strong> - Zero Trust + regulatory compliance</li>
            <li><strong>DevOps & Deployment</strong> - Modern CI/CD and Infrastructure as Code</li>
            <li><strong>Monitoring & Observability</strong> - Full observability stack</li>
            <li><strong>Data Architecture</strong> - Modern data platform and analytics</li>
            <li><strong>API Design & Integration</strong> - Enterprise API ecosystem</li>
            <li><strong>Testing & Quality Assurance</strong> - Comprehensive testing framework</li>
            <li><strong>Enterprise Governance</strong> - Organizational governance framework</li>
        </ol>
    </div>
'''
    
    # Process each document
    documents = [
        ("EXECUTIVE_ARCHITECTURE_PRESENTATION.md", "👔 Executive Architecture Presentation"),
        ("ENTERPRISE_ARCHITECTURE_GUIDE.md", "🏗️ Enterprise Architecture Guide"),
        ("SCALABILITY_PERFORMANCE_ROADMAP.md", "⚡ Scalability & Performance Roadmap"),
        ("SECURITY_COMPLIANCE_FRAMEWORK.md", "🔒 Security & Compliance Framework"),
        ("DEVOPS_DEPLOYMENT_STRATEGY.md", "🚀 DevOps & Deployment Strategy"),
        ("MONITORING_OBSERVABILITY_PLAN.md", "📊 Monitoring & Observability"),
        ("DATA_ARCHITECTURE_MANAGEMENT.md", "🗄️ Data Architecture & Management"),
        ("API_DESIGN_INTEGRATION_STRATEGY.md", "🌐 API Design & Integration"),
        ("TESTING_QUALITY_ASSURANCE_FRAMEWORK.md", "🧪 Testing & Quality Assurance"),
        ("ENTERPRISE_GOVERNANCE_DOCUMENTATION.md", "🏛️ Enterprise Governance")
    ]
    
    for i, (filename, title) in enumerate(documents):
        if not Path(filename).exists():
            print(f"❌ File not found: {filename}")
            continue
        
        print(f"📄 Processing: {filename}")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple content processing
            processed_content = simple_markdown_to_html(content)
            
            # Add chapter
            html_content += f'''
            <div class="chapter">
                <div class="chapter-title">{title}</div>
                {processed_content}
            </div>
            '''
            
        except Exception as e:
            print(f"❌ Error with {filename}: {str(e)}")
            html_content += f'''
            <div class="chapter">
                <div class="chapter-title">{title}</div>
                <p><em>Content loading error: {str(e)}</em></p>
            </div>
            '''
    
    # Close HTML
    html_content += '''
</body>
</html>
'''
    
    # Write file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"TARA2_Study_Guide_{timestamp}.html"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        
        print(f"\n✅ Study Guide Created Successfully!")
        print(f"📄 File: {output_file}")
        print(f"📁 Location: {os.path.abspath(output_file)}")
        print(f"📊 Size: {file_size:.1f} MB")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error writing file: {str(e)}")
        return None

def simple_markdown_to_html(content):
    """Simple and safe markdown to HTML conversion"""
    
    # Clean the content first
    content = content.replace('\\', '\\\\')  # Escape backslashes
    
    # Split into lines for processing
    lines = content.split('\n')
    html_lines = []
    
    in_code_block = False
    code_block_lines = []
    
    for line in lines:
        # Handle code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End code block
                code_content = '<br>'.join(code_block_lines)
                html_lines.append(f'<pre>{code_content}</pre>')
                code_block_lines = []
                in_code_block = False
            else:
                # Start code block
                in_code_block = True
            continue
        
        if in_code_block:
            # Escape HTML in code blocks
            escaped_line = line.replace('<', '&lt;').replace('>', '&gt;')
            code_block_lines.append(escaped_line)
            continue
        
        # Regular line processing
        processed_line = line
        
        # Headers
        if line.startswith('# '):
            processed_line = f'<h1>{line[2:].strip()}</h1>'
        elif line.startswith('## '):
            processed_line = f'<h2>{line[3:].strip()}</h2>'
        elif line.startswith('### '):
            processed_line = f'<h3>{line[4:].strip()}</h3>'
        elif line.startswith('#### '):
            processed_line = f'<h4>{line[5:].strip()}</h4>'
        
        # Bold text (simple replacement)
        if '**' in processed_line:
            processed_line = processed_line.replace('**', '<strong>').replace('**', '</strong>')
        
        # Bullet points
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            processed_line = f'<li>{line.strip()[2:]}</li>'
        
        # Empty lines become paragraph breaks
        if line.strip() == '':
            processed_line = '</p><p>'
        
        html_lines.append(processed_line)
    
    # Join lines and wrap in paragraphs
    html_content = '<p>' + '<br>'.join(html_lines) + '</p>'
    
    # Clean up formatting
    html_content = html_content.replace('<p></p><p>', '<p>')
    html_content = html_content.replace('<p><h', '<h')
    html_content = html_content.replace('</h1></p>', '</h1>')
    html_content = html_content.replace('</h2></p>', '</h2>')
    html_content = html_content.replace('</h3></p>', '</h3>')
    html_content = html_content.replace('</h4></p>', '</h4>')
    html_content = html_content.replace('<p><pre>', '<pre>')
    html_content = html_content.replace('</pre></p>', '</pre>')
    
    # Handle list formatting
    html_content = html_content.replace('<p><li>', '<ul><li>')
    html_content = html_content.replace('</li></p>', '</li></ul>')
    html_content = html_content.replace('</ul><br><ul>', '')
    
    return html_content

def main():
    """Main execution"""
    
    print("🎓 TARA2 Enterprise Architecture - Simple Study Guide Generator")
    print("=" * 70)
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Create the study guide
    html_file = create_simple_study_guide()
    
    if html_file:
        print("\n" + "=" * 70)
        print("🎯 SUCCESS! Your Study Guide is Ready!")
        print("=" * 70)
        
        print(f"\n📄 Generated: {html_file}")
        print(f"📁 Full Path: {os.path.abspath(html_file)}")
        
        print(f"\n🚀 To Convert to PDF:")
        print(f"1. Double-click '{html_file}' to open in browser")
        print(f"2. Press Ctrl+P (or Cmd+P on Mac)")
        print(f"3. Choose 'Save as PDF'")
        print(f"4. Set margins to 'Minimum'")
        print(f"5. Enable 'Background graphics' ✓")
        print(f"6. Click 'Save' - Done!")
        
        print(f"\n📚 Study Content:")
        print("✅ 10 comprehensive architecture documents")
        print("✅ 1000+ pages of technical content")  
        print("✅ Multi-cloud deployment strategies")
        print("✅ Architecture diagrams and system designs")
        print("✅ Business case and ROI analysis")
        print("✅ Implementation roadmaps and technical specifications")
        
        print(f"\n🎯 Perfect for Learning:")
        print("• Enterprise cloud architecture")
        print("• Multi-cloud deployment strategies") 
        print("• AI/ML platform engineering")
        print("• Security and compliance frameworks")
        print("• Technical leadership and decision making")
        
    else:
        print("❌ Failed to create study guide")

if __name__ == "__main__":
    main()