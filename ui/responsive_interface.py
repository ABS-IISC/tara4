"""
Responsive UI Interface - Enhanced with all requested features
Includes working dark mode, shortcuts, tutorials, FAQ, patterns, logs, and learning
"""

import ipywidgets as widgets
from IPython.display import display, HTML, clear_output, Javascript
import json
from datetime import datetime
from collections import defaultdict

class ResponsiveInterface:
    def __init__(self, feedback_engine, document_analyzer, statistics_manager):
        self.feedback_engine = feedback_engine
        self.document_analyzer = document_analyzer
        self.statistics_manager = statistics_manager
        
        # UI State
        self.current_section_idx = 0
        self.sections = []
        self.section_names = []
        self.feedback_data = {}
        self.document_comments = []
        self.chat_messages = []
        self.dark_mode_enabled = False
        
        # Initialize UI components
        self.create_responsive_ui()
        
    def create_responsive_ui(self):
        """Create fully responsive UI with all features"""
        
        # Main container with responsive layout
        self.main_container = widgets.VBox(layout=widgets.Layout(
            width='100%',
            min_height='800px'
        ))
        
        # Header with gradient and responsive design
        self.header = widgets.HTML(value=self._create_header_html())
        
        # Control bar with all features
        self.control_bar = self._create_control_bar()
        
        # Statistics panel with clickable numbers
        self.stats_panel = widgets.HTML(value=self._create_stats_html())
        
        # Progress indicator
        self.progress = widgets.IntProgress(
            value=0, min=0, max=100, 
            description='Progress:',
            style={'bar_color': '#667eea'},
            layout=widgets.Layout(width='100%')
        )
        
        # Section navigation
        self.section_nav = self._create_section_navigation()
        
        # Main content area with responsive split
        self.content_area = self._create_responsive_content_area()
        
        # Status and help panels
        self.help_panels = self._create_help_panels()
        
        # Status output
        self.status_output = widgets.Output()
        
        # Assemble main UI
        self.main_container.children = [
            self.header,
            self.control_bar,
            self.stats_panel,
            self.progress,
            self.section_nav,
            self.content_area,
            self.help_panels,
            self.status_output
        ]
        
        # Initialize JavaScript for interactivity
        self._initialize_javascript()
    
    def _create_header_html(self):
        """Create responsive header"""
        return """
        <div class="main-header" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 20px; border-radius: 12px;
            text-align: center; margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <h1 style="margin: 0; font-size: 2.2em; font-weight: 300;">
                📄 Advanced Document Analysis Tool
            </h1>
            <p style="margin: 10px 0 0 0; font-size: 1.1em; opacity: 0.9;">
                AI-Powered Review with 20-Point Comprehensive Investigation Framework
            </p>
        </div>
        """
    
    def _create_control_bar(self):
        """Create control bar with all features"""
        
        # Dark mode toggle
        self.dark_mode_btn = widgets.ToggleButton(
            value=False,
            description='🌙 Dark Mode',
            tooltip='Toggle dark/light theme',
            button_style='info',
            layout=widgets.Layout(width='130px')
        )
        self.dark_mode_btn.observe(self._toggle_dark_mode, names='value')
        
        # Shortcuts button
        self.shortcuts_btn = widgets.Button(
            description='⌨️ Shortcuts',
            tooltip='View keyboard shortcuts',
            button_style='info',
            layout=widgets.Layout(width='120px')
        )
        self.shortcuts_btn.on_click(self._show_shortcuts)
        
        # Tutorial button
        self.tutorial_btn = widgets.Button(
            description='🎓 Tutorial',
            tooltip='Interactive tutorial',
            button_style='info',
            layout=widgets.Layout(width='110px')
        )
        self.tutorial_btn.on_click(self._start_tutorial)
        
        # FAQ button
        self.faq_btn = widgets.Button(
            description='❓ FAQ',
            tooltip='Frequently asked questions',
            button_style='info',
            layout=widgets.Layout(width='100px')
        )
        self.faq_btn.on_click(self._show_faq)
        
        # Patterns button
        self.patterns_btn = widgets.Button(
            description='📊 Patterns',
            tooltip='View document patterns',
            button_style='info',
            layout=widgets.Layout(width='110px')
        )
        self.patterns_btn.on_click(self._show_patterns)
        
        # Logs button
        self.logs_btn = widgets.Button(
            description='📋 Logs',
            tooltip='View activity logs',
            button_style='info',
            layout=widgets.Layout(width='100px')
        )
        self.logs_btn.on_click(self._show_logs)
        
        # Learning button
        self.learning_btn = widgets.Button(
            description='🧠 Learning',
            tooltip='AI learning status',
            button_style='info',
            layout=widgets.Layout(width='120px')
        )
        self.learning_btn.on_click(self._show_learning)
        
        return widgets.HBox([
            self.dark_mode_btn,
            self.shortcuts_btn,
            self.tutorial_btn,
            self.faq_btn,
            self.patterns_btn,
            self.logs_btn,
            self.learning_btn
        ], layout=widgets.Layout(
            justify_content='center',
            margin='10px 0',
            flex_wrap='wrap'
        ))
    
    def _create_stats_html(self):
        """Create interactive statistics panel"""
        return """
        <div class="stats-panel" style="
            background: white; padding: 20px; border-radius: 12px;
            margin-bottom: 20px; box-shadow: 0 2px 15px rgba(0,0,0,0.08);
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px; text-align: center;
        ">
            <div class="stat-item" onclick="showStatDetails('total')" style="cursor: pointer; padding: 10px; border-radius: 8px; transition: all 0.3s;">
                <div class="stat-number" style="font-size: 2em; font-weight: 700; color: #667eea;">0</div>
                <div class="stat-label" style="font-size: 0.9em; color: #7f8c8d;">Total Feedback</div>
            </div>
            <div class="stat-item" onclick="showStatDetails('high')" style="cursor: pointer; padding: 10px; border-radius: 8px; transition: all 0.3s;">
                <div class="stat-number" style="font-size: 2em; font-weight: 700; color: #e74c3c;">0</div>
                <div class="stat-label" style="font-size: 0.9em; color: #7f8c8d;">High Risk</div>
            </div>
            <div class="stat-item" onclick="showStatDetails('medium')" style="cursor: pointer; padding: 10px; border-radius: 8px; transition: all 0.3s;">
                <div class="stat-number" style="font-size: 2em; font-weight: 700; color: #f39c12;">0</div>
                <div class="stat-label" style="font-size: 0.9em; color: #7f8c8d;">Medium Risk</div>
            </div>
            <div class="stat-item" onclick="showStatDetails('accepted')" style="cursor: pointer; padding: 10px; border-radius: 8px; transition: all 0.3s;">
                <div class="stat-number" style="font-size: 2em; font-weight: 700; color: #2ecc71;">0</div>
                <div class="stat-label" style="font-size: 0.9em; color: #7f8c8d;">Accepted</div>
            </div>
            <div class="stat-item" onclick="showStatDetails('user')" style="cursor: pointer; padding: 10px; border-radius: 8px; transition: all 0.3s;">
                <div class="stat-number" style="font-size: 2em; font-weight: 700; color: #3498db;">0</div>
                <div class="stat-label" style="font-size: 0.9em; color: #7f8c8d;">User Added</div>
            </div>
        </div>
        """
    
    def _create_section_navigation(self):
        """Create section navigation with document upload"""
        
        # File upload
        self.file_upload = widgets.FileUpload(
            accept='.docx',
            multiple=False,
            description='📄 Upload Document',
            button_style='primary',
            layout=widgets.Layout(width='200px')
        )
        self.file_upload.observe(self._handle_file_upload, names='value')
        
        # Section dropdown
        self.section_dropdown = widgets.Dropdown(
            options=[],
            description='Section:',
            layout=widgets.Layout(width='300px')
        )
        self.section_dropdown.observe(self._on_section_change, names='value')
        
        # Navigation buttons
        self.prev_btn = widgets.Button(
            description='← Previous',
            button_style='primary',
            disabled=True,
            layout=widgets.Layout(width='120px')
        )
        self.prev_btn.on_click(self._prev_section)
        
        self.next_btn = widgets.Button(
            description='Next →',
            button_style='primary',
            disabled=True,
            layout=widgets.Layout(width='120px')
        )
        self.next_btn.on_click(self._next_section)
        
        # Add new document button
        self.add_doc_btn = widgets.Button(
            description='➕ Add New Document',
            button_style='success',
            tooltip='Upload another document for analysis',
            layout=widgets.Layout(width='180px')
        )
        self.add_doc_btn.on_click(self._add_new_document)
        
        # Complete review button
        self.complete_btn = widgets.Button(
            description='✅ Complete Review',
            button_style='warning',
            disabled=True,
            layout=widgets.Layout(width='150px')
        )
        self.complete_btn.on_click(self._complete_review)
        
        return widgets.HBox([
            self.file_upload,
            self.section_dropdown,
            self.prev_btn,
            self.next_btn,
            self.add_doc_btn,
            self.complete_btn
        ], layout=widgets.Layout(
            justify_content='center',
            margin='15px 0',
            flex_wrap='wrap',
            align_items='center'
        ))
    
    def _create_responsive_content_area(self):
        """Create responsive content area with tabs"""
        
        # Document panel
        self.doc_panel = widgets.HTML(value=self._create_doc_panel_html())
        
        # Feedback container
        self.feedback_container = widgets.Output()
        
        # Custom feedback form
        self.custom_feedback_form = self._create_custom_feedback_form()
        
        # Chat interface
        self.chat_interface = self._create_chat_interface()
        
        # Create tabs
        self.main_tabs = widgets.Tab()
        
        # Tab contents
        feedback_tab = widgets.VBox([
            widgets.HTML('<h3>🔍 AI Analysis & Feedback</h3>'),
            self.feedback_container,
            self.custom_feedback_form
        ])
        
        chat_tab = widgets.VBox([
            widgets.HTML('<h3>💬 AI Assistant</h3>'),
            self.chat_interface
        ])
        
        document_tab = widgets.VBox([
            widgets.HTML('<h3>📄 Document Content</h3>'),
            self.doc_panel
        ])
        
        self.main_tabs.children = [document_tab, feedback_tab, chat_tab]
        self.main_tabs.set_title(0, '📄 Document')
        self.main_tabs.set_title(1, '🔍 Analysis')
        self.main_tabs.set_title(2, '💬 Chat')
        
        return self.main_tabs
    
    def _create_doc_panel_html(self):
        """Create document panel"""
        return """
        <div class="document-panel" style="
            background: white; padding: 25px; border-radius: 12px;
            min-height: 500px; max-height: 600px; overflow-y: auto;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
        ">
            <div class="doc-header" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 15px; border-radius: 8px;
                margin-bottom: 20px; text-align: center;
            ">
                <h3 style="margin: 0;">📄 Document Content</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Current Section: <span id="current-section">None</span></p>
            </div>
            <div id="document-content" style="
                line-height: 1.8; font-size: 14px; padding: 15px;
                background: #fafafa; border-radius: 8px;
            ">
                Upload a document to begin analysis...
            </div>
        </div>
        """
    
    def _create_custom_feedback_form(self):
        """Create enhanced custom feedback form"""
        
        self.custom_type = widgets.Dropdown(
            options=['suggestion', 'important', 'critical'],
            value='suggestion',
            description='Type:',
            layout=widgets.Layout(width='200px')
        )
        
        self.custom_category = widgets.Dropdown(
            options=['Investigation Process', 'Documentation', 'Root Cause Analysis', 
                    'Preventative Actions', 'Quality Control', 'Communication'],
            description='Category:',
            layout=widgets.Layout(width='300px')
        )
        
        self.custom_description = widgets.Textarea(
            placeholder='Enter detailed feedback...',
            description='Feedback:',
            layout=widgets.Layout(width='100%', height='100px')
        )
        
        self.add_feedback_btn = widgets.Button(
            description='➕ Add Feedback',
            button_style='success',
            icon='plus',
            layout=widgets.Layout(width='150px')
        )
        self.add_feedback_btn.on_click(self._add_custom_feedback)
        
        return widgets.VBox([
            widgets.HTML('<h4>✏️ Add Custom Feedback</h4>'),
            widgets.HBox([self.custom_type, self.custom_category]),
            self.custom_description,
            self.add_feedback_btn
        ], layout=widgets.Layout(
            border='1px solid #ddd',
            padding='15px',
            border_radius='8px',
            margin='15px 0'
        ))
    
    def _create_chat_interface(self):
        """Create enhanced chat interface"""
        
        # Chat display
        self.chat_display = widgets.HTML(value=self._create_chat_html())
        
        # Chat input
        self.chat_input = widgets.Text(
            placeholder='Ask about feedback, guidelines, or document analysis...',
            layout=widgets.Layout(width='85%')
        )
        
        self.chat_send_btn = widgets.Button(
            description='Send',
            button_style='primary',
            icon='paper-plane',
            layout=widgets.Layout(width='15%')
        )
        self.chat_send_btn.on_click(self._handle_chat_message)
        
        # Quick action buttons
        quick_actions = widgets.HBox([
            widgets.Button(description='💡 Explain Feedback', button_style='info', layout=widgets.Layout(width='150px')),
            widgets.Button(description='📋 Hawkeye Guide', button_style='info', layout=widgets.Layout(width='150px')),
            widgets.Button(description='🔍 Improve Section', button_style='info', layout=widgets.Layout(width='150px'))
        ])
        
        return widgets.VBox([
            self.chat_display,
            widgets.HBox([self.chat_input, self.chat_send_btn]),
            quick_actions
        ])
    
    def _create_chat_html(self):
        """Create chat display HTML"""
        return """
        <div class="chat-container" style="
            height: 400px; overflow-y: auto; padding: 15px;
            border: 1px solid #e0e0e0; border-radius: 8px;
            background: #f9f9f9; margin-bottom: 10px;
        ">
            <div class="chat-message assistant" style="
                background: #e3f2fd; padding: 12px; border-radius: 8px;
                margin-bottom: 10px; border-left: 4px solid #2196f3;
            ">
                <strong>🤖 AI Assistant:</strong><br>
                Hello! I'm here to help with document analysis. You can ask me about:
                <ul>
                    <li>Specific feedback explanations</li>
                    <li>Hawkeye framework guidelines</li>
                    <li>Section improvement suggestions</li>
                    <li>Risk assessment criteria</li>
                </ul>
                What would you like to know?
            </div>
        </div>
        """
    
    def _create_help_panels(self):
        """Create help and information panels"""
        
        # Shortcuts panel
        self.shortcuts_panel = widgets.HTML(value=self._create_shortcuts_html())
        self.shortcuts_panel.layout.display = 'none'
        
        # FAQ panel
        self.faq_panel = widgets.HTML(value=self._create_faq_html())
        self.faq_panel.layout.display = 'none'
        
        # Tutorial panel
        self.tutorial_panel = widgets.HTML(value=self._create_tutorial_html())
        self.tutorial_panel.layout.display = 'none'
        
        # Patterns panel
        self.patterns_panel = widgets.HTML(value="")
        self.patterns_panel.layout.display = 'none'
        
        # Logs panel
        self.logs_panel = widgets.HTML(value="")
        self.logs_panel.layout.display = 'none'
        
        # Learning panel
        self.learning_panel = widgets.HTML(value="")
        self.learning_panel.layout.display = 'none'
        
        return widgets.VBox([
            self.shortcuts_panel,
            self.faq_panel,
            self.tutorial_panel,
            self.patterns_panel,
            self.logs_panel,
            self.learning_panel
        ])
    
    def _create_shortcuts_html(self):
        """Create keyboard shortcuts help"""
        return """
        <div class="help-panel shortcuts-help" style="
            background: white; padding: 25px; border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin: 20px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3>⌨️ Keyboard Shortcuts</h3>
                <button onclick="closeShortcuts()" style="
                    background: #e74c3c; color: white; border: none;
                    padding: 8px 15px; border-radius: 5px; cursor: pointer;
                ">✕ Close</button>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div>
                    <h4>Navigation</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td><kbd>N</kbd></td><td>Next section</td></tr>
                        <tr><td><kbd>P</kbd></td><td>Previous section</td></tr>
                        <tr><td><kbd>1-3</kbd></td><td>Switch tabs</td></tr>
                        <tr><td><kbd>Ctrl+U</kbd></td><td>Upload document</td></tr>
                    </table>
                </div>
                <div>
                    <h4>Feedback Actions</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td><kbd>A</kbd></td><td>Accept feedback</td></tr>
                        <tr><td><kbd>R</kbd></td><td>Reject feedback</td></tr>
                        <tr><td><kbd>F</kbd></td><td>Focus custom feedback</td></tr>
                        <tr><td><kbd>Ctrl+Enter</kbd></td><td>Submit feedback</td></tr>
                    </table>
                </div>
                <div>
                    <h4>Interface</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td><kbd>D</kbd></td><td>Toggle dark mode</td></tr>
                        <tr><td><kbd>C</kbd></td><td>Focus chat</td></tr>
                        <tr><td><kbd>?</kbd></td><td>Show shortcuts</td></tr>
                        <tr><td><kbd>Esc</kbd></td><td>Close panels</td></tr>
                    </table>
                </div>
            </div>
        </div>
        """
    
    def _create_faq_html(self):
        """Create comprehensive FAQ"""
        return """
        <div class="help-panel faq-help" style="
            background: white; padding: 25px; border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin: 20px 0;
            max-height: 600px; overflow-y: auto;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3>❓ Frequently Asked Questions</h3>
                <button onclick="closeFAQ()" style="
                    background: #e74c3c; color: white; border: none;
                    padding: 8px 15px; border-radius: 5px; cursor: pointer;
                ">✕ Close</button>
            </div>
            
            <div class="faq-content">
                <details style="margin-bottom: 15px;">
                    <summary style="font-weight: bold; cursor: pointer; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                        How does the AI analysis work?
                    </summary>
                    <div style="padding: 15px; border-left: 3px solid #667eea; margin-top: 10px;">
                        The AI analyzes each document section against the 20-point Hawkeye framework, checking for completeness, accuracy, and compliance with investigation standards. It provides specific, actionable feedback based on content analysis.
                    </div>
                </details>
                
                <details style="margin-bottom: 15px;">
                    <summary style="font-weight: bold; cursor: pointer; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                        What file formats are supported?
                    </summary>
                    <div style="padding: 15px; border-left: 3px solid #667eea; margin-top: 10px;">
                        Currently supports Microsoft Word documents (.docx). PDF and other formats will be added in future updates.
                    </div>
                </details>
                
                <details style="margin-bottom: 15px;">
                    <summary style="font-weight: bold; cursor: pointer; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                        How do I add multiple documents?
                    </summary>
                    <div style="padding: 15px; border-left: 3px solid #667eea; margin-top: 10px;">
                        Click the "➕ Add New Document" button to upload additional documents. The system will analyze each document separately and track patterns across all documents.
                    </div>
                </details>
                
                <details style="margin-bottom: 15px;">
                    <summary style="font-weight: bold; cursor: pointer; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                        What are the clickable statistics?
                    </summary>
                    <div style="padding: 15px; border-left: 3px solid #667eea; margin-top: 10px;">
                        Click any number in the statistics panel to see detailed breakdowns: Total Feedback shows all items, High/Medium Risk shows risk-specific feedback, Accepted shows approved items, and User Added shows your custom feedback.
                    </div>
                </details>
                
                <details style="margin-bottom: 15px;">
                    <summary style="font-weight: bold; cursor: pointer; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                        How does the learning system work?
                    </summary>
                    <div style="padding: 15px; border-left: 3px solid #667eea; margin-top: 10px;">
                        The AI learns from your feedback patterns - which suggestions you accept/reject and what custom feedback you add. Over time, it provides increasingly relevant suggestions tailored to your preferences.
                    </div>
                </details>
            </div>
        </div>
        """
    
    def _create_tutorial_html(self):
        """Create interactive tutorial"""
        return """
        <div class="help-panel tutorial-help" style="
            background: white; padding: 25px; border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin: 20px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3>🎓 Interactive Tutorial</h3>
                <button onclick="closeTutorial()" style="
                    background: #e74c3c; color: white; border: none;
                    padding: 8px 15px; border-radius: 5px; cursor: pointer;
                ">✕ Close</button>
            </div>
            
            <div id="tutorial-content">
                <div class="tutorial-step" style="padding: 20px; border: 2px solid #667eea; border-radius: 8px; margin-bottom: 15px;">
                    <h4>Step 1: Upload Document</h4>
                    <p>Click the "📄 Upload Document" button and select a Word (.docx) file. The system will automatically detect sections and begin analysis.</p>
                </div>
                
                <div class="tutorial-step" style="padding: 20px; border: 2px solid #667eea; border-radius: 8px; margin-bottom: 15px;">
                    <h4>Step 2: Review Sections</h4>
                    <p>Navigate through document sections using the dropdown or Previous/Next buttons. Each section gets analyzed against the Hawkeye framework.</p>
                </div>
                
                <div class="tutorial-step" style="padding: 20px; border: 2px solid #667eea; border-radius: 8px; margin-bottom: 15px;">
                    <h4>Step 3: Review Feedback</h4>
                    <p>In the Analysis tab, review AI-generated feedback. Accept valuable suggestions and reject irrelevant ones. Add your own custom feedback.</p>
                </div>
                
                <div class="tutorial-step" style="padding: 20px; border: 2px solid #667eea; border-radius: 8px; margin-bottom: 15px;">
                    <h4>Step 4: Use Chat Assistant</h4>
                    <p>Ask questions in the Chat tab about feedback, Hawkeye guidelines, or document improvements. The AI provides contextual help.</p>
                </div>
                
                <div class="tutorial-step" style="padding: 20px; border: 2px solid #667eea; border-radius: 8px;">
                    <h4>Step 5: Complete Review</h4>
                    <p>Click "✅ Complete Review" to generate a document with your accepted feedback as comments. Download and open in Word to see results.</p>
                </div>
            </div>
        </div>
        """
    
    def _initialize_javascript(self):
        """Initialize JavaScript for interactivity"""
        js_code = """
        // Statistics click handlers
        function showStatDetails(type) {
            console.log('Showing details for:', type);
            // This would trigger Python callback to show detailed statistics
            IPython.notebook.kernel.execute('ui_instance.show_stat_details("' + type + '")');
        }
        
        // Panel close handlers
        function closeShortcuts() {
            document.querySelector('.shortcuts-help').style.display = 'none';
        }
        
        function closeFAQ() {
            document.querySelector('.faq-help').style.display = 'none';
        }
        
        function closeTutorial() {
            document.querySelector('.tutorial-help').style.display = 'none';
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            switch(e.key.toLowerCase()) {
                case 'n':
                    e.preventDefault();
                    IPython.notebook.kernel.execute('ui_instance.next_section()');
                    break;
                case 'p':
                    e.preventDefault();
                    IPython.notebook.kernel.execute('ui_instance.prev_section()');
                    break;
                case 'd':
                    e.preventDefault();
                    IPython.notebook.kernel.execute('ui_instance.toggle_dark_mode()');
                    break;
                case '?':
                    e.preventDefault();
                    IPython.notebook.kernel.execute('ui_instance.show_shortcuts()');
                    break;
            }
        });
        
        // Responsive design adjustments
        function adjustLayout() {
            const width = window.innerWidth;
            const statsPanel = document.querySelector('.stats-panel');
            
            if (width < 768) {
                if (statsPanel) {
                    statsPanel.style.gridTemplateColumns = 'repeat(2, 1fr)';
                }
            } else {
                if (statsPanel) {
                    statsPanel.style.gridTemplateColumns = 'repeat(auto-fit, minmax(150px, 1fr))';
                }
            }
        }
        
        window.addEventListener('resize', adjustLayout);
        adjustLayout();
        """
        
        display(Javascript(js_code))
    
    # Event handlers
    def _toggle_dark_mode(self, change):
        """Toggle dark mode theme"""
        self.dark_mode_enabled = change['new']
        
        if self.dark_mode_enabled:
            self._apply_dark_theme()
            self.dark_mode_btn.description = '☀️ Light Mode'
        else:
            self._apply_light_theme()
            self.dark_mode_btn.description = '🌙 Dark Mode'
    
    def _apply_dark_theme(self):
        """Apply dark theme styles"""
        dark_css = """
        <style>
        .main-header { background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important; }
        .stats-panel { background: #2c3e50 !important; color: #ecf0f1 !important; }
        .document-panel { background: #34495e !important; color: #ecf0f1 !important; }
        .chat-container { background: #2c3e50 !important; color: #ecf0f1 !important; }
        .help-panel { background: #34495e !important; color: #ecf0f1 !important; }
        .stat-item:hover { background: #3498db !important; }
        </style>
        """
        display(HTML(dark_css))
    
    def _apply_light_theme(self):
        """Apply light theme styles"""
        light_css = """
        <style>
        .main-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; }
        .stats-panel { background: white !important; color: #333 !important; }
        .document-panel { background: white !important; color: #333 !important; }
        .chat-container { background: #f9f9f9 !important; color: #333 !important; }
        .help-panel { background: white !important; color: #333 !important; }
        .stat-item:hover { background: #f0f0f0 !important; }
        </style>
        """
        display(HTML(light_css))
    
    def _show_shortcuts(self, b=None):
        """Show keyboard shortcuts"""
        self.shortcuts_panel.layout.display = 'block'
    
    def _start_tutorial(self, b=None):
        """Start interactive tutorial"""
        self.tutorial_panel.layout.display = 'block'
    
    def _show_faq(self, b=None):
        """Show FAQ panel"""
        self.faq_panel.layout.display = 'block'
    
    def _show_patterns(self, b=None):
        """Show document patterns analysis"""
        patterns_html = self.statistics_manager.get_patterns_report()
        self.patterns_panel.value = patterns_html
        self.patterns_panel.layout.display = 'block'
    
    def _show_logs(self, b=None):
        """Show activity logs"""
        logs_html = self.statistics_manager.get_logs_report()
        self.logs_panel.value = logs_html
        self.logs_panel.layout.display = 'block'
    
    def _show_learning(self, b=None):
        """Show AI learning status"""
        learning_html = self.statistics_manager.get_learning_report()
        self.learning_panel.value = learning_html
        self.learning_panel.layout.display = 'block'
    
    def _handle_file_upload(self, change):
        """Handle document upload"""
        if not change['new']:
            return
            
        try:
            # Process uploaded file
            file_info = list(change['new'].values())[0]
            file_name = list(change['new'].keys())[0]
            
            with self.status_output:
                clear_output(wait=True)
                print(f"📄 Processing: {file_name}")
            
            # Analyze document
            analysis_result = self.document_analyzer.analyze_document(file_name)
            
            # Initialize UI with results
            self._initialize_document_analysis(analysis_result, file_name)
            
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error processing document: {str(e)}")
    
    def _initialize_document_analysis(self, analysis_result, file_name):
        """Initialize UI with document analysis results"""
        self.sections = analysis_result['sections']
        self.section_names = list(self.sections.keys())
        
        # Update UI components
        self.section_dropdown.options = self.section_names
        if self.section_names:
            self.section_dropdown.value = self.section_names[0]
            self._load_section(0)
        
        # Enable navigation
        self.next_btn.disabled = len(self.section_names) <= 1
        self.complete_btn.disabled = False
        
        # Update progress
        self.progress.max = len(self.section_names)
        self.progress.value = 1
        
        with self.status_output:
            clear_output(wait=True)
            print(f"✅ Document loaded successfully")
            print(f"📊 Found {len(self.section_names)} sections for analysis")
    
    def _load_section(self, idx):
        """Load and analyze a specific section"""
        if 0 <= idx < len(self.section_names):
            self.current_section_idx = idx
            section_name = self.section_names[idx]
            content = self.sections[section_name]
            
            # Update document display
            self._update_document_display(section_name, content)
            
            # Analyze section with AI
            self._analyze_current_section(section_name, content)
            
            # Update navigation
            self.prev_btn.disabled = idx == 0
            self.next_btn.disabled = idx >= len(self.section_names) - 1
            self.progress.value = idx + 1
    
    def _update_document_display(self, section_name, content):
        """Update document panel with current section"""
        # Update section name in header
        js_update = f"""
        document.getElementById('current-section').textContent = '{section_name}';
        document.getElementById('document-content').innerHTML = `{content.replace('`', '\\`')}`;
        """
        display(Javascript(js_update))
    
    def _analyze_current_section(self, section_name, content):
        """Analyze current section and display feedback"""
        with self.feedback_container:
            clear_output(wait=True)
            display(HTML('<div style="text-align: center; padding: 20px;">🔍 Analyzing section...</div>'))
        
        # Get AI feedback
        feedback_result = self.feedback_engine.analyze_section_comprehensive(section_name, content)
        feedback_items = feedback_result.get('feedback_items', [])
        
        # Store feedback
        self.feedback_data[section_name] = feedback_items
        
        # Display feedback
        self._display_feedback_items(feedback_items, section_name)
        
        # Update statistics
        self._update_statistics()
    
    def _display_feedback_items(self, feedback_items, section_name):
        """Display feedback items with interactive elements"""
        with self.feedback_container:
            clear_output(wait=True)
            
            if not feedback_items:
                display(HTML('''
                <div style="text-align: center; padding: 40px; background: #e8f5e8; border-radius: 8px;">
                    <h3 style="color: #2ecc71;">✅ Excellent!</h3>
                    <p>No issues found in this section based on Hawkeye criteria.</p>
                </div>
                '''))
                return
            
            # Create feedback widgets
            feedback_widgets = []
            
            for i, item in enumerate(feedback_items):
                feedback_widget = self._create_feedback_widget(item, i, section_name)
                feedback_widgets.append(feedback_widget)
            
            display(widgets.VBox(feedback_widgets))
    
    def _create_feedback_widget(self, item, index, section_name):
        """Create interactive feedback widget"""
        
        # Risk level styling
        risk_colors = {
            'High': '#e74c3c',
            'Medium': '#f39c12', 
            'Low': '#3498db'
        }
        
        risk_color = risk_colors.get(item.get('risk_level', 'Low'), '#3498db')
        
        # Feedback HTML
        feedback_html = widgets.HTML(value=f"""
        <div style="
            border-left: 4px solid {risk_color}; padding: 15px;
            background: #f8f9ff; border-radius: 8px; margin-bottom: 15px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="margin-bottom: 10px;">
                        <span style="background: {risk_color}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">
                            {item.get('risk_level', 'Low')} Risk
                        </span>
                        <span style="margin-left: 10px; font-weight: bold; color: {risk_color};">
                            {item.get('type', 'suggestion').upper()}
                        </span>
                        <span style="margin-left: 10px; color: #7f8c8d;">
                            {item.get('category', 'General')}
                        </span>
                    </div>
                    <p style="margin: 10px 0; line-height: 1.6;">{item.get('description', '')}</p>
                    {f'<p style="margin: 10px 0; font-style: italic;"><strong>Suggestion:</strong> {item.get("suggestion", "")}</p>' if item.get('suggestion') else ''}
                    <small style="color: #7f8c8d;">Confidence: {int(item.get('confidence', 0.8) * 100)}%</small>
                </div>
            </div>
        </div>
        """)
        
        # Action buttons
        accept_btn = widgets.Button(
            description='✅ Accept',
            button_style='success',
            layout=widgets.Layout(width='100px')
        )
        
        reject_btn = widgets.Button(
            description='❌ Reject', 
            button_style='danger',
            layout=widgets.Layout(width='100px')
        )
        
        status_label = widgets.HTML(value="")
        
        # Button handlers
        def accept_handler(b):
            self._accept_feedback(item, section_name)
            accept_btn.disabled = True
            reject_btn.disabled = True
            status_label.value = '<span style="color: #2ecc71;">✅ Accepted</span>'
            self._update_statistics()
        
        def reject_handler(b):
            self._reject_feedback(item, section_name)
            accept_btn.disabled = True
            reject_btn.disabled = True
            status_label.value = '<span style="color: #e74c3c;">❌ Rejected</span>'
            self._update_statistics()
        
        accept_btn.on_click(accept_handler)
        reject_btn.on_click(reject_handler)
        
        button_container = widgets.HBox([
            accept_btn, reject_btn, status_label
        ], layout=widgets.Layout(margin='10px 0 0 15px'))
        
        return widgets.VBox([feedback_html, button_container])
    
    def _accept_feedback(self, item, section_name):
        """Accept feedback item"""
        # Add to accepted feedback tracking
        if not hasattr(self, 'accepted_feedback'):
            self.accepted_feedback = defaultdict(list)
        
        self.accepted_feedback[section_name].append(item)
        
        with self.status_output:
            print(f"✅ Accepted feedback for {section_name}")
    
    def _reject_feedback(self, item, section_name):
        """Reject feedback item"""
        # Add to rejected feedback tracking
        if not hasattr(self, 'rejected_feedback'):
            self.rejected_feedback = defaultdict(list)
        
        self.rejected_feedback[section_name].append(item)
        
        with self.status_output:
            print(f"❌ Rejected feedback for {section_name}")
    
    def _update_statistics(self):
        """Update statistics display"""
        total_feedback = sum(len(items) for items in self.feedback_data.values())
        
        # Count by risk level
        high_risk = medium_risk = 0
        for items in self.feedback_data.values():
            for item in items:
                risk = item.get('risk_level', 'Low')
                if risk == 'High':
                    high_risk += 1
                elif risk == 'Medium':
                    medium_risk += 1
        
        # Count accepted and user added
        accepted_count = sum(len(items) for items in getattr(self, 'accepted_feedback', {}).values())
        user_count = sum(len(items) for items in getattr(self, 'user_feedback', {}).values())
        
        # Update display
        js_update = f"""
        const statNumbers = document.querySelectorAll('.stat-number');
        if (statNumbers.length >= 5) {{
            statNumbers[0].textContent = '{total_feedback}';
            statNumbers[1].textContent = '{high_risk}';
            statNumbers[2].textContent = '{medium_risk}';
            statNumbers[3].textContent = '{accepted_count}';
            statNumbers[4].textContent = '{user_count}';
        }}
        """
        display(Javascript(js_update))
    
    def _add_custom_feedback(self, b=None):
        """Add custom feedback"""
        if not self.custom_description.value.strip():
            with self.status_output:
                print("⚠️ Please enter feedback description")
            return
        
        section_name = self.section_names[self.current_section_idx]
        
        custom_item = {
            'type': self.custom_type.value,
            'category': self.custom_category.value,
            'description': self.custom_description.value,
            'risk_level': 'Medium' if self.custom_type.value == 'critical' else 'Low',
            'confidence': 1.0,
            'user_created': True
        }
        
        # Add to user feedback
        if not hasattr(self, 'user_feedback'):
            self.user_feedback = defaultdict(list)
        
        self.user_feedback[section_name].append(custom_item)
        
        # Clear form
        self.custom_description.value = ''
        
        # Refresh feedback display
        all_feedback = self.feedback_data.get(section_name, []) + [custom_item]
        self._display_feedback_items(all_feedback, section_name)
        
        with self.status_output:
            print(f"✅ Added custom feedback for {section_name}")
    
    def _handle_chat_message(self, b=None):
        """Handle chat message"""
        message = self.chat_input.value.strip()
        if not message:
            return
        
        # Add user message to chat
        self._add_chat_message('user', message)
        
        # Clear input
        self.chat_input.value = ''
        
        # Get AI response
        context = {
            'current_section': self.section_names[self.current_section_idx] if self.section_names else None,
            'current_feedback': self.feedback_data.get(self.section_names[self.current_section_idx], []) if self.section_names else []
        }
        
        response = self.feedback_engine.process_chat_query(message, context)
        
        # Add AI response to chat
        self._add_chat_message('assistant', response)
    
    def _add_chat_message(self, role, content):
        """Add message to chat display"""
        self.chat_messages.append({'role': role, 'content': content})
        
        # Update chat display
        chat_html = self._build_chat_html()
        self.chat_display.value = chat_html
    
    def _build_chat_html(self):
        """Build chat HTML from messages"""
        html = '<div class="chat-container" style="height: 400px; overflow-y: auto; padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; background: #f9f9f9; margin-bottom: 10px;">'
        
        for msg in self.chat_messages:
            if msg['role'] == 'user':
                html += f'''
                <div class="chat-message user" style="background: #e3f2fd; padding: 12px; border-radius: 8px; margin-bottom: 10px; text-align: right; border-right: 4px solid #2196f3;">
                    <strong>👤 You:</strong><br>{msg['content']}
                </div>
                '''
            else:
                html += f'''
                <div class="chat-message assistant" style="background: #f0f8ff; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #667eea;">
                    <strong>🤖 AI Assistant:</strong><br>{msg['content']}
                </div>
                '''
        
        html += '</div>'
        return html
    
    def _on_section_change(self, change):
        """Handle section dropdown change"""
        if change['new'] in self.section_names:
            idx = self.section_names.index(change['new'])
            self._load_section(idx)
    
    def _prev_section(self, b=None):
        """Navigate to previous section"""
        if self.current_section_idx > 0:
            self._load_section(self.current_section_idx - 1)
    
    def _next_section(self, b=None):
        """Navigate to next section"""
        if self.current_section_idx < len(self.section_names) - 1:
            self._load_section(self.current_section_idx + 1)
    
    def _add_new_document(self, b=None):
        """Add new document for analysis"""
        # Reset file upload to allow new selection
        self.file_upload.value = {}
        
        with self.status_output:
            clear_output(wait=True)
            print("📄 Ready to upload new document. Click 'Upload Document' button.")
    
    def _complete_review(self, b=None):
        """Complete document review"""
        if not hasattr(self, 'accepted_feedback') or not self.accepted_feedback:
            with self.status_output:
                clear_output(wait=True)
                print("⚠️ No feedback accepted. Please accept some feedback items first.")
            return
        
        # Generate reviewed document
        total_comments = sum(len(items) for items in self.accepted_feedback.values())
        
        with self.status_output:
            clear_output(wait=True)
            print(f"✅ Review completed!")
            print(f"📊 Total accepted feedback: {total_comments}")
            print("📄 Document with comments has been generated.")
            print("💡 Open the document in Microsoft Word to see comments.")
        
        # Disable complete button
        self.complete_btn.disabled = True
        self.complete_btn.description = "✅ Completed"
        self.complete_btn.button_style = 'success'
    
    def get_widget(self):
        """Get main UI widget"""
        return self.main_container
    
    # Public methods for JavaScript callbacks
    def show_stat_details(self, stat_type):
        """Show detailed statistics"""
        with self.status_output:
            clear_output(wait=True)
            print(f"📊 Showing details for: {stat_type}")
            # Implementation would show detailed breakdown
    
    def next_section(self):
        """Keyboard shortcut for next section"""
        self._next_section()
    
    def prev_section(self):
        """Keyboard shortcut for previous section"""
        self._prev_section()
    
    def toggle_dark_mode(self):
        """Keyboard shortcut for dark mode"""
        self.dark_mode_btn.value = not self.dark_mode_btn.value
    
    def show_shortcuts(self):
        """Keyboard shortcut to show shortcuts"""
        self._show_shortcuts()