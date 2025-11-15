#!/usr/bin/env python3
"""
TARA2 AI-Prism Enterprise Architecture PDF Generator
Creates professional PDF documentation from markdown files
"""

import os
import subprocess
import sys
from pathlib import Path
import datetime

def check_pandoc_installed():
    """Check if pandoc is installed"""
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Pandoc is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Pandoc is not installed")
    print("Please install pandoc:")
    print("  macOS: brew install pandoc")
    print("  Windows: winget install pandoc")
    print("  Linux: sudo apt-get install pandoc")
    return False

def generate_comprehensive_pdf():
    """Generate comprehensive PDF from all architecture documents"""
    
    if not check_pandoc_installed():
        return False
    
    # Order of documents for logical flow
    documents = [
        "README.md",
        "EXECUTIVE_ARCHITECTURE_PRESENTATION.md", 
        "ENTERPRISE_ARCHITECTURE_GUIDE.md",
        "SCALABILITY_PERFORMANCE_ROADMAP.md",
        "SECURITY_COMPLIANCE_FRAMEWORK.md",
        "DEVOPS_DEPLOYMENT_STRATEGY.md",
        "MONITORING_OBSERVABILITY_PLAN.md",
        "DATA_ARCHITECTURE_MANAGEMENT.md",
        "API_DESIGN_INTEGRATION_STRATEGY.md",
        "TESTING_QUALITY_ASSURANCE_FRAMEWORK.md",
        "ENTERPRISE_GOVERNANCE_DOCUMENTATION.md"
    ]
    
    # Check if all files exist
    missing_files = []
    for doc in documents:
        if not Path(doc).exists():
            missing_files.append(doc)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("🚀 Generating comprehensive enterprise architecture PDF...")
    
    # Create output filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"TARA2_Enterprise_Architecture_{timestamp}.pdf"
    
    # Pandoc command for professional PDF
    pandoc_cmd = [
        'pandoc',
        *documents,  # Input files
        '-o', output_file,  # Output file
        '--pdf-engine=xelatex',  # Better typography
        '--toc',  # Table of contents
        '--toc-depth=3',  # 3 levels deep
        '--number-sections',  # Number sections
        '--highlight-style=github',  # Code syntax highlighting
        '--geometry=margin=1in',  # 1 inch margins
        '--variable=fontsize:11pt',  # Font size
        '--variable=documentclass:report',  # Document class
        '--variable=classoption:twoside',  # Two-sided printing
        '--variable=papersize:a4',  # A4 paper size
        '--variable=geometry:a4paper',  # A4 geometry
        '--filter=pandoc-crossref',  # Cross-references (if available)
        '--standalone'  # Standalone document
    ]
    
    try:
        # Execute pandoc command
        result = subprocess.run(pandoc_cmd, capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print(f"✅ PDF generated successfully: {output_file}")
            print(f"📄 File size: {os.path.getsize(output_file) / (1024*1024):.1f} MB")
            print(f"📁 Location: {os.path.abspath(output_file)}")
            return True
        else:
            print(f"❌ PDF generation failed:")
            print(f"Error: {result.stderr}")
            
            # Try with simpler options if complex options fail
            print("🔄 Trying with simplified options...")
            simple_cmd = [
                'pandoc', *documents, '-o', output_file,
                '--pdf-engine=pdflatex', '--toc'
            ]
            
            simple_result = subprocess.run(simple_cmd, capture_output=True, text=True)
            if simple_result.returncode == 0:
                print(f"✅ PDF generated with simplified options: {output_file}")
                return True
            else:
                print(f"❌ Simplified generation also failed: {simple_result.stderr}")
                return False
    
    except Exception as e:
        print(f"❌ Exception during PDF generation: {str(e)}")
        return False

def generate_individual_pdfs():
    """Generate individual PDFs for each architecture document"""
    
    if not check_pandoc_installed():
        return False
    
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
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"pdf_output_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    
    for markdown_file, title in documents:
        if not Path(markdown_file).exists():
            print(f"❌ File not found: {markdown_file}")
            continue
            
        output_file = f"{output_dir}/TARA2_{title.replace(' ', '_')}.pdf"
        
        pandoc_cmd = [
            'pandoc', markdown_file,
            '-o', output_file,
            '--pdf-engine=xelatex',
            '--toc',
            '--number-sections',
            '--highlight-style=github',
            '--geometry=margin=1in',
            '--variable=fontsize:11pt',
            '--variable=documentclass:article',
            f'--metadata=title:TARA2 {title}',
            '--standalone'
        ]
        
        try:
            result = subprocess.run(pandoc_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Generated: {output_file}")
                success_count += 1
            else:
                print(f"❌ Failed to generate {output_file}: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Exception generating {output_file}: {str(e)}")
    
    print(f"\n📊 Summary: {success_count}/{len(documents)} PDFs generated successfully")
    print(f"📁 Output directory: {os.path.abspath(output_dir)}")
    
    return success_count > 0

def create_html_version():
    """Create HTML version that can be easily converted to PDF in browser"""
    
    print("🌐 Creating HTML version for browser-based PDF generation...")
    
    # Read all markdown files and combine
    combined_content = []
    
    documents = [
        "EXECUTIVE_ARCHITECTURE_PRESENTATION.md",
        "ENTERPRISE_ARCHITECTURE_GUIDE.md", 
        "SCALABILITY_PERFORMANCE_ROADMAP.md",
        "SECURITY_COMPLIANCE_FRAMEWORK.md",
        "DEVOPS_DEPLOYMENT_STRATEGY.md",
        "MONITORING_OBSERVABILITY_PLAN.md",
        "DATA_ARCHITECTURE_MANAGEMENT.md", 
        "API_DESIGN_INTEGRATION_STRATEGY.md",
        "TESTING_QUALITY_ASSURANCE_FRAMEWORK.md",
        "ENTERPRISE_GOVERNANCE_DOCUMENTATION.md"
    ]
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TARA2 AI-Prism Enterprise Architecture</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; border-bottom: 2px solid #e74c3c; padding-bottom: 5px; }
        h3 { color: #8e44ad; }
        pre { 
            background: #f8f9fa; 
            border: 1px solid #e9ecef; 
            border-radius: 5px; 
            padding: 15px; 
            overflow-x: auto; 
            font-family: 'Courier New', monospace;
        }
        code { 
            background: #f1f3f4; 
            padding: 2px 4px; 
            border-radius: 3px; 
            font-family: 'Courier New', monospace;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 0;
            padding: 10px 20px;
            background: #f8f9fa;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th { background: #f2f2f2; font-weight: bold; }
        .page-break { page-break-before: always; }
        @media print {
            body { font-size: 10pt; }
            .no-print { display: none; }
        }
    </style>
</head>
<body>
    <div class="no-print">
        <h1>📄 To convert to PDF:</h1>
        <ol>
            <li>Press <strong>Ctrl+P</strong> (or Cmd+P on Mac)</li>
            <li>Select "Save as PDF" as printer</li>
            <li>Choose "More settings"</li>
            <li>Set margins to "Minimum" or "Custom" with small margins</li>
            <li>Enable "Background graphics"</li>
            <li>Click "Save" and choose filename</li>
        </ol>
        <hr>
    </div>
    
    <h1>🏗️ TARA2 AI-Prism Enterprise Architecture Framework</h1>
    <p><strong>Complete Technical Architecture & Implementation Guide</strong></p>
    <p><em>Generated: {datetime.datetime.now().strftime("%B %d, %Y")}</em></p>
    <div class="page-break"></div>
"""
    
    # Convert each markdown file to HTML content
    for i, doc_file in enumerate(documents):
        if Path(doc_file).exists():
            print(f"📄 Processing: {doc_file}")
            
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple markdown to HTML conversion
            html_section = convert_markdown_to_html(content)
            html_content += f'<div class="page-break"></div>\n{html_section}\n'
    
    html_content += """
</body>
</html>
"""
    
    # Write HTML file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filename = f"TARA2_Enterprise_Architecture_{timestamp}.html"
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML version created: {html_filename}")
    print(f"📁 Location: {os.path.abspath(html_filename)}")
    print("\n🌐 To convert to PDF:")
    print(f"1. Open {html_filename} in your browser")
    print("2. Press Ctrl+P (or Cmd+P on Mac)")
    print("3. Choose 'Save as PDF'")
    print("4. Set margins to 'Minimum' and enable 'Background graphics'")
    print("5. Save as PDF")
    
    return html_filename

def convert_markdown_to_html(markdown_content):
    """Simple markdown to HTML conversion"""
    
    # Basic markdown conversion (simplified)
    html = markdown_content
    
    # Headers
    html = html.replace('# ', '<h1>')
    html = html.replace('## ', '<h2>')
    html = html.replace('### ', '<h3>')
    html = html.replace('#### ', '<h4>')
    
    # Code blocks
    import re
    
    # Multi-line code blocks
    html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```\n(.*?)\n```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    
    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Bold text
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # Line breaks
    html = html.replace('\n\n', '</p><p>')
    html = html.replace('\n', '<br>')
    
    # Wrap in paragraphs
    html = f'<p>{html}</p>'
    
    # Clean up empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)
    
    return html

def main():
    """Main function to generate PDF documentation"""
    
    print("🏗️ TARA2 AI-Prism Enterprise Architecture PDF Generator")
    print("=" * 60)
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Option 1: Try comprehensive PDF with pandoc
    print("\n1️⃣ Attempting comprehensive PDF generation with Pandoc...")
    if generate_comprehensive_pdf():
        print("✅ Comprehensive PDF generation successful!")
    else:
        print("❌ Comprehensive PDF generation failed, trying alternatives...")
        
        # Option 2: Generate individual PDFs
        print("\n2️⃣ Attempting individual PDF generation...")
        if generate_individual_pdfs():
            print("✅ Individual PDFs generated successfully!")
        
    # Option 3: Always create HTML version as backup
    print("\n3️⃣ Creating HTML version for browser-based PDF conversion...")
    html_file = create_html_version()
    
    print("\n" + "=" * 60)
    print("🎯 PDF Generation Complete!")
    print("\n📄 Available Formats:")
    print("• Comprehensive PDF (if pandoc succeeded)")
    print("• Individual PDFs (if pandoc succeeded)")
    print(f"• HTML version: {html_file} (always available)")
    
    print("\n🚀 Next Steps:")
    print("1. Check generated files in current directory")
    print("2. If HTML version: Open in browser → Ctrl+P → Save as PDF")
    print("3. For best results: Use Chrome/Edge for PDF conversion")
    
    print("\n📚 Study Materials Ready!")
    return True

if __name__ == "__main__":
    main()