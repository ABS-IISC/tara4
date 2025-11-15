#!/usr/bin/env python3
"""
TARA2 Enterprise Architecture - Interactive Study Guide Generator
Creates a user-friendly, interactive HTML study guide optimized for PDF conversion
"""

import os
from pathlib import Path
import datetime
import re

def create_interactive_study_guide():
    """Create interactive HTML study guide with improved UI"""
    
    print("🎓 Creating Interactive Study Guide...")
    
    # HTML template with professional styling
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TARA2 AI-Prism Enterprise Architecture Study Guide</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #2c3e50;
            background: #ffffff;
            max-width: 210mm; /* A4 width */
            margin: 0 auto;
            padding: 20px;
        }
        
        .cover-page {
            text-align: center;
            padding: 100px 0;
            border-bottom: 3px solid #3498db;
            margin-bottom: 50px;
            page-break-after: always;
        }
        
        .cover-title {
            font-size: 28pt;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            line-height: 1.2;
        }
        
        .cover-subtitle {
            font-size: 18pt;
            color: #7f8c8d;
            margin-bottom: 30px;
        }
        
        .cover-details {
            font-size: 14pt;
            color: #34495e;
            margin-top: 40px;
        }
        
        .nav-controls {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #34495e;
            color: white;
            padding: 10px;
            border-radius: 5px;
            z-index: 1000;
        }
        
        .nav-controls button {
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            margin: 2px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 11pt;
        }
        
        .nav-controls button:hover {
            background: #2980b9;
        }
        
        .pdf-instructions {
            background: linear-gradient(135deg, #74b9ff, #0984e3);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }
        
        .pdf-instructions h3 {
            margin-bottom: 15px;
            font-size: 16pt;
        }
        
        .pdf-instructions ol {
            text-align: left;
            max-width: 500px;
            margin: 0 auto;
        }
        
        .pdf-instructions li {
            margin: 8px 0;
            font-size: 13pt;
        }
        
        .toc {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            margin: 30px 0;
            page-break-inside: avoid;
        }
        
        .toc h2 {
            color: #2c3e50;
            font-size: 20pt;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        
        .toc ul {
            list-style-type: none;
            padding: 0;
        }
        
        .toc li {
            margin: 8px 0;
            padding: 8px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        
        .toc a {
            color: #2c3e50;
            text-decoration: none;
            font-weight: 500;
            font-size: 13pt;
        }
        
        .toc a:hover {
            color: #3498db;
        }
        
        .chapter {
            margin: 40px 0;
            padding: 20px 0;
            border-top: 2px solid #ecf0f1;
            page-break-before: always;
        }
        
        .chapter:first-child {
            border-top: none;
            page-break-before: avoid;
        }
        
        .chapter-title {
            color: #2c3e50;
            font-size: 22pt;
            font-weight: bold;
            margin-bottom: 20px;
            padding: 15px 0;
            border-bottom: 3px solid #e74c3c;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 20pt;
            font-weight: bold;
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #3498db;
        }
        
        h2 {
            color: #34495e;
            font-size: 16pt;
            font-weight: bold;
            margin: 20px 0 12px 0;
            padding-bottom: 5px;
            border-bottom: 1px solid #bdc3c7;
        }
        
        h3 {
            color: #8e44ad;
            font-size: 14pt;
            font-weight: bold;
            margin: 15px 0 10px 0;
        }
        
        h4 {
            color: #16a085;
            font-size: 13pt;
            font-weight: bold;
            margin: 12px 0 8px 0;
        }
        
        p {
            margin: 10px 0;
            text-align: justify;
            font-size: 12pt;
            line-height: 1.6;
        }
        
        ul, ol {
            margin: 12px 0;
            padding-left: 25px;
        }
        
        li {
            margin: 5px 0;
            font-size: 12pt;
        }
        
        .code-block {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 10pt;
            line-height: 1.4;
            overflow-x: auto;
            border-left: 4px solid #4299e1;
        }
        
        .inline-code {
            background: #f7fafc;
            color: #2d3748;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 11pt;
            border: 1px solid #e2e8f0;
        }
        
        .diagram {
            background: #f8f9fa;
            border: 2px solid #dee2e6;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 10pt;
            line-height: 1.3;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        
        .highlight-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        .highlight-box h3 {
            color: white;
            margin-bottom: 10px;
        }
        
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 11pt;
            page-break-inside: avoid;
        }
        
        .metrics-table th {
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        
        .metrics-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .metrics-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .success {
            color: #27ae60;
            font-weight: bold;
        }
        
        .warning {
            color: #f39c12;
            font-weight: bold;
        }
        
        .error {
            color: #e74c3c;
            font-weight: bold;
        }
        
        .page-header {
            font-size: 10pt;
            color: #7f8c8d;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .section-summary {
            background: #ecf0f1;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }
        
        .key-points {
            background: #e8f5e8;
            border: 2px solid #27ae60;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
        
        .key-points h4 {
            color: #27ae60;
            margin-bottom: 10px;
        }
        
        @media print {
            body {
                font-size: 10pt;
                line-height: 1.4;
            }
            .nav-controls {
                display: none;
            }
            .pdf-instructions {
                display: none;
            }
            .page-break {
                page-break-before: always;
            }
            .avoid-break {
                page-break-inside: avoid;
            }
        }
        
        @page {
            margin: 0.8in;
            @top-center {
                content: "TARA2 AI-Prism Enterprise Architecture";
                font-size: 9pt;
                color: #7f8c8d;
            }
            @bottom-center {
                content: counter(page);
                font-size: 9pt;
                color: #7f8c8d;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation Controls -->
    <div class="nav-controls">
        <div style="margin-bottom: 10px; font-weight: bold;">📄 Study Guide Navigation</div>
        <button onclick="scrollToSection('toc')">📋 Table of Contents</button>
        <button onclick="scrollToSection('executive')">👔 Executive Summary</button>
        <button onclick="scrollToSection('architecture')">🏗️ Architecture</button>
        <button onclick="scrollToSection('implementation')">🚀 Implementation</button>
        <button onclick="printToPDF()">📥 Download PDF</button>
    </div>
    
    <!-- Cover Page -->
    <div class="cover-page">
        <div class="cover-title">🏗️ TARA2 AI-Prism<br>Enterprise Architecture</div>
        <div class="cover-subtitle">Complete Technical Study Guide & Implementation Framework</div>
        <div class="cover-details">
            <p><strong>Prepared For:</strong> Technical Architecture Learning</p>
            <p><strong>Content:</strong> 1000+ pages of enterprise architecture expertise</p>
            <p><strong>Coverage:</strong> Multi-cloud deployment, AI/ML platforms, enterprise security</p>
            <p><strong>Generated:</strong> {current_date}</p>
        </div>
    </div>
    
    <!-- PDF Instructions -->
    <div class="pdf-instructions">
        <h3>📥 Download as PDF - Easy Instructions</h3>
        <ol>
            <li><strong>Press Ctrl+P</strong> (Windows/Linux) or <strong>Cmd+P</strong> (Mac)</li>
            <li>Choose "<strong>Save as PDF</strong>" as destination</li>
            <li>Set margins to "<strong>Minimum</strong>" (0.2 inches)</li>
            <li>Enable "<strong>Background graphics</strong>" ✅</li>
            <li>Choose paper size: <strong>A4</strong> or <strong>Letter</strong></li>
            <li>Click "<strong>Save</strong>" and name your file</li>
        </ol>
        <p style="margin-top: 15px; font-size: 11pt;">
            💡 <strong>Tip:</strong> Use Chrome or Edge browser for best PDF quality
        </p>
    </div>

{content}

    <script>
        function scrollToSection(sectionId) {
            const element = document.getElementById(sectionId);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
            }
        }
        
        function printToPDF() {
            window.print();
        }
        
        // Auto-generate table of contents
        document.addEventListener('DOMContentLoaded', function() {
            generateTableOfContents();
        });
        
        function generateTableOfContents() {
            const tocContainer = document.getElementById('auto-toc');
            if (!tocContainer) return;
            
            const headers = document.querySelectorAll('h1, h2');
            let tocHTML = '<ul>';
            
            headers.forEach((header, index) => {
                const id = 'section-' + index;
                header.id = id;
                
                const level = header.tagName === 'H1' ? 'toc-h1' : 'toc-h2';
                tocHTML += `<li class="${level}"><a href="#${id}">${header.textContent}</a></li>`;
            });
            
            tocHTML += '</ul>';
            tocContainer.innerHTML = tocHTML;
        }
        
        // Add smooth scrolling for internal links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    </script>
</body>
</html>
"""
    
    # Read and process all documents
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
    
    content_html = ""
    
    # Create table of contents
    content_html += """
    <div id="toc" class="toc">
        <h2>📋 Table of Contents</h2>
        <div id="auto-toc">
            <!-- Auto-generated TOC will be inserted here -->
        </div>
    </div>
    """
    
    # Process each document
    for i, (filename, title) in enumerate(documents):
        if not Path(filename).exists():
            print(f"❌ File not found: {filename}")
            continue
        
        print(f"📄 Processing: {filename}")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Convert to HTML with improved formatting
            html_content = convert_markdown_to_html_improved(markdown_content)
            
            # Add chapter wrapper
            content_html += f"""
            <div class="chapter" id="chapter-{i+1}">
                <div class="chapter-title">{title}</div>
                {html_content}
            </div>
            """
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            content_html += f"""
            <div class="chapter">
                <div class="chapter-title">{title}</div>
                <p class="error">Error loading content: {str(e)}</p>
            </div>
            """
    
    # Generate final HTML
    current_date = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
    final_html = html_template.format(
        current_date=current_date,
        content=content_html
    )
    
    # Write HTML file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"TARA2_Study_Guide_{timestamp}.html"
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        print(f"✅ Interactive Study Guide Created!")
        print(f"📄 File: {output_filename}")
        print(f"📁 Location: {os.path.abspath(output_filename)}")
        print(f"📊 Size: {len(final_html) / 1024:.1f} KB")
        
        return output_filename
        
    except Exception as e:
        print(f"❌ Error writing HTML file: {str(e)}")
        return None

def convert_markdown_to_html_improved(markdown_content):
    """Improved markdown to HTML conversion with better formatting"""
    
    html = markdown_content
    
    # Remove markdown frontmatter if present
    html = re.sub(r'^---.*?---\s*', '', html, flags=re.DOTALL)
    
    # Convert headers with proper IDs
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Convert code blocks (multi-line)
    html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<div class="code-block">\2</div>', html, flags=re.DOTALL)
    html = re.sub(r'```\n(.*?)\n```', r'<div class="code-block">\1</div>', html, flags=re.DOTALL)
    
    # Convert inline code
    html = re.sub(r'`([^`]+)`', r'<span class="inline-code">\1</span>', html)
    
    # Convert ASCII diagrams to special diagram blocks
    diagram_pattern = r'```\n((?:[^\n]*[│├└┌┐┤┬┴┼─┊┏┓┗┛┣┫┳┻╋═║╔╗╚╝╠╣╦╩╬▲▼◄►▶◀]+[^\n]*\n?)+)```'
    html = re.sub(diagram_pattern, r'<div class="diagram">\1</div>', html, flags=re.MULTILINE)
    
    # Convert YAML blocks to special formatting
    yaml_pattern = r'```yaml\n(.*?)\n```'
    html = re.sub(yaml_pattern, r'<div class="code-block">\1</div>', html, flags=re.DOTALL)
    
    # Convert bold text  
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)
    
    # Convert italic text
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)
    
    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Convert bullet points
    html = re.sub(r'^[\s]*[-\*\+] (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    html = re.sub(r'</ul>\s*<ul>', '', html)
    
    # Convert numbered lists
    html = re.sub(r'^[\s]*\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Convert tables (basic support)
    table_rows = re.findall(r'\|(.+)\|', html)
    if table_rows:
        table_html = '<table class="metrics-table">'
        for i, row in enumerate(table_rows[:10]):  # Limit table size
            cells = [cell.strip() for cell in row.split('|')]
            if i == 0:  # Header row
                table_html += '<tr>' + ''.join(f'<th>{cell}</th>' for cell in cells) + '</tr>'
            elif not all(cell == '' or '-' in cell for cell in cells):  # Skip separator rows
                table_html += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>'
        table_html += '</table>'
        
        # Replace first table occurrence
        html = re.sub(r'\|.+\|.*?\n', table_html, html, count=1, flags=re.DOTALL)
    
    # Convert line breaks
    html = re.sub(r'\n\n+', '</p><p>', html)
    html = re.sub(r'\n', '<br>', html)
    
    # Wrap in paragraphs  
    html = f'<p>{html}</p>'
    
    # Clean up formatting issues
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p>\s*(<h[1-6])', r'\1', html)
    html = re.sub(r'(</h[1-6]>)\s*</p>', r'\1', html)
    html = re.sub(r'<p>\s*(<div)', r'\1', html)
    html = re.sub(r'(</div>)\s*</p>', r'\1', html)
    html = re.sub(r'<p>\s*(<ul>|<ol>|<table)', r'\1', html)
    html = re.sub(r'(</ul>|</ol>|</table>)\s*</p>', r'\1', html)
    
    return html

def main():
    """Main function"""
    
    print("🎓 TARA2 Enterprise Architecture - Interactive Study Guide Generator")
    print("=" * 70)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"📁 Working in: {os.getcwd()}")
    
    # Create interactive study guide
    html_file = create_interactive_study_guide()
    
    if html_file:
        print("\n" + "=" * 70)
        print("🎯 SUCCESS! Your Interactive Study Guide is Ready!")
        print("=" * 70)
        
        print(f"\n📄 File Created: {html_file}")
        print(f"📁 Full Path: {os.path.abspath(html_file)}")
        
        print(f"\n🚀 Next Steps:")
        print(f"1. Double-click '{html_file}' to open in browser")
        print(f"2. Use navigation controls in top-right corner")
        print(f"3. Click 'Download PDF' or press Ctrl+P to convert to PDF")
        print(f"4. Set margins to 'Minimum' and enable 'Background graphics'")
        print(f"5. Save as PDF for studying")
        
        print(f"\n📚 Study Guide Features:")
        print("✅ Professional formatting optimized for PDF")
        print("✅ Interactive navigation and table of contents")
        print("✅ Improved diagram formatting")
        print("✅ Readable font sizes and spacing")
        print("✅ Print-optimized styling")
        
        print(f"\n🎓 Ready for Technical Architecture Learning!")
        
    else:
        print("\n❌ Failed to create study guide")
        print("Please check the error messages above and try again")

if __name__ == "__main__":
    main()