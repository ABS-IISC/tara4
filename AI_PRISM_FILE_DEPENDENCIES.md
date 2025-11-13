# AI-Prism File Relationships & Dependencies

## 🎯 Complete File Dependency Tree

```
AI-PRISM PROJECT ROOT
├── 📁 ENTRY POINTS & MAIN APPLICATION
│   ├── app.py ⭐ (MAIN FLASK APPLICATION)
│   │   ├── Imports: core.*, utils.*, config.model_config
│   │   ├── Depends on: ALL core modules, ALL utils modules
│   │   ├── Creates: Flask app, API endpoints, session management
│   │   └── Used by: All startup scripts
│   │
│   ├── main.py 🚀 (PRIMARY ENTRY POINT)
│   │   ├── Imports: app (from app.py)
│   │   ├── Depends on: app.py, environment configuration
│   │   ├── Creates: Production server setup
│   │   └── Used by: Production deployments
│   │
│   ├── start_aiprism.py 🔧 (ENHANCED STARTUP)
│   │   ├── Imports: app, config.model_config
│   │   ├── Depends on: System verification, AWS testing
│   │   ├── Creates: Comprehensive startup with checks
│   │   └── Used by: Advanced production setup
│   │
│   ├── run_local.py 🧪 (DEVELOPMENT)
│   │   ├── Imports: main (from main.py)
│   │   ├── Depends on: Mock mode configuration
│   │   ├── Creates: Local development server
│   │   └── Used by: Development and testing
│   │
│   └── simple_working_app.py 🏃 (LIGHTWEIGHT)
│       ├── Imports: Flask, docx, basic libraries
│       ├── Depends on: Minimal dependencies only
│       ├── Creates: Simple document analysis
│       └── Used by: Quick testing, demos
│
├── 📁 CORE ANALYSIS ENGINE
│   ├── core/__init__.py 📦
│   │   └── Purpose: Package initialization
│   │
│   ├── core/document_analyzer.py 📄 (DOCUMENT PROCESSING)
│   │   ├── Imports: json, re, os, docx, boto3
│   │   ├── Depends on: python-docx library, AWS SDK (optional)
│   │   ├── Used by: app.py (/upload, /analyze_section)
│   │   └── Functions: extract_sections_from_docx(), section detection
│   │
│   ├── core/ai_feedback_engine.py 🧠 (AI ANALYSIS)
│   │   ├── Imports: json, boto3, config.model_config
│   │   ├── Depends on: AWS Bedrock, Claude models
│   │   ├── Used by: app.py (/analyze_section, /chat)
│   │   └── Functions: analyze_section(), process_chat_query()
│   │
│   └── core/ai_feedback_engine_enhanced.py 🧠⚡ (ENHANCED AI)
│       ├── Imports: json, boto3, config.model_config
│       ├── Depends on: AWS Bedrock, advanced prompting
│       ├── Used by: Alternative to standard AI engine
│       └── Functions: Enhanced analysis with better context
│
├── 📁 UTILITY MODULES
│   ├── utils/__init__.py 📦
│   │   └── Purpose: Package initialization
│   │
│   ├── utils/statistics_manager.py 📊 (ANALYTICS)
│   │   ├── Imports: json, collections.defaultdict, datetime
│   │   ├── Depends on: Session data, feedback tracking
│   │   ├── Used by: app.py (all statistics endpoints)
│   │   └── Functions: get_statistics(), track metrics
│   │
│   ├── utils/document_processor.py 📝 (DOCUMENT GENERATION)
│   │   ├── Imports: docx, lxml, zipfile, shutil, uuid
│   │   ├── Depends on: python-docx, XML manipulation
│   │   ├── Used by: app.py (/complete_review)
│   │   └── Functions: create_document_with_comments()
│   │
│   ├── utils/pattern_analyzer.py 🔍 (PATTERN RECOGNITION)
│   │   ├── Imports: json, os, datetime, collections
│   │   ├── Depends on: Persistent data files
│   │   ├── Used by: app.py (/get_patterns)
│   │   └── Functions: find_recurring_patterns(), trend analysis
│   │
│   ├── utils/audit_logger.py 📋 (ACTIVITY LOGGING)
│   │   ├── Imports: json, os, uuid, datetime, collections
│   │   ├── Depends on: File system, session data
│   │   ├── Used by: app.py (all user actions), ReviewSession
│   │   └── Functions: log(), generate_audit_report_html()
│   │
│   └── utils/learning_system.py 🧠📚 (AI LEARNING)
│       ├── Imports: json, os, datetime, collections
│       ├── Depends on: User feedback patterns, persistent storage
│       ├── Used by: app.py (/get_learning_status), ReviewSession
│       └── Functions: record_feedback_response(), get_recommendations()
│
├── 📁 USER INTERFACE
│   ├── templates/
│   │   ├── enhanced_index.html 🎨 (MAIN INTERFACE)
│   │   │   ├── Includes: ALL static/js/*.js files
│   │   │   ├── Depends on: Complete JavaScript ecosystem
│   │   │   ├── Used by: Flask app.py (@app.route('/'))
│   │   │   └── Features: Complete web interface
│   │   │
│   │   ├── enhanced_index_backup.html 💾 (BACKUP)
│   │   │   └── Purpose: Backup copy of main interface
│   │   │
│   │   └── abc.html 🅰️ (ALTERNATIVE)
│   │       └── Purpose: Alternative interface layout
│   │
│   ├── static/js/
│   │   ├── app.js 📱 (MAIN ENTRY)
│   │   │   ├── Purpose: JavaScript initialization
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Coordinates: All other JS modules
│   │   │
│   │   ├── button_fixes.js 🔘 (CORE UI FUNCTIONS)
│   │   │   ├── Depends on: Global variables, session state
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Functions: Core button functionality, modals
│   │   │
│   │   ├── text_highlighting.js 🎨 (TEXT FEATURES)
│   │   │   ├── Depends on: DOM manipulation, session storage
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Functions: Text selection, highlighting, comments
│   │   │
│   │   ├── user_feedback_management.js 👤 (FEEDBACK MGMT)
│   │   │   ├── Depends on: User feedback state, real-time updates
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Functions: Display user feedback, management
│   │   │
│   │   ├── custom_feedback_functions.js ✨ (AI ENHANCEMENT)
│   │   │   ├── Depends on: AI feedback state, custom forms
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Functions: Add custom feedback to AI suggestions
│   │   │
│   │   ├── progress_functions.js ⏳ (PROGRESS TRACKING)
│   │   │   ├── Depends on: Loading states, media rotation
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Functions: Progress bars, loading animations
│   │   │
│   │   ├── enhanced_help_system.js ❓ (HELP SYSTEM)
│   │   │   ├── Depends on: Modal system, interactive elements
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Functions: Tutorials, FAQ, shortcuts
│   │   │
│   │   ├── text_highlight_comments.js 💬 (HIGHLIGHTING COMMENTS)
│   │   │   ├── Depends on: Text highlighting base functionality
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Functions: Comment management for highlights
│   │   │
│   │   ├── custom_feedback_fix.js 🔧 (BUG FIXES)
│   │   │   ├── Depends on: Core feedback functionality
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Functions: Custom feedback consolidation
│   │   │
│   │   ├── custom_feedback_help.js 💡 (HELP FUNCTIONS)
│   │   │   ├── Depends on: Help system, custom feedback
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Functions: Custom feedback guidance
│   │   │
│   │   ├── missing_functions.js 🔄 (UTILITY FUNCTIONS)
│   │   │   ├── Depends on: Core application state
│   │   │   ├── Used by: enhanced_index.html
│   │   │   └── Functions: Missing/utility functions
│   │   │
│   │   └── button_fixes_backup.js 💾 (BACKUP)
│   │       └── Purpose: Backup of button fixes
│   │
│   └── ui/
│       ├── __init__.py 📦
│       │   └── Purpose: Package initialization
│       │
│       └── responsive_interface.py 📱 (JUPYTER INTERFACE)
│           ├── Imports: ipywidgets, IPython.display
│           ├── Depends on: Jupyter environment
│           ├── Used by: Notebook environments
│           └── Functions: Widget-based interface
│
├── 📁 CONFIGURATION & DATA
│   ├── config/
│   │   └── model_config.py ⚙️ (AI MODEL CONFIG)
│   │       ├── Imports: os, json, boto3
│   │       ├── Depends on: Environment variables, AWS config
│   │       ├── Used by: core/ai_feedback_engine*.py, app.py
│   │       └── Functions: Model configuration, AWS setup
│   │
│   ├── data/ 📁 (PERSISTENT STORAGE)
│   │   ├── learning_data.json 🧠 (AI learning patterns)
│   │   ├── pattern_analysis.json 🔍 (Document patterns)
│   │   ├── audit_logs.json 📋 (Activity logs)
│   │   └── tool_feedback.json 💬 (User feedback on tool)
│   │
│   └── uploads/ 📁 (TEMPORARY FILES)
│       ├── [timestamp]_*.docx (Uploaded documents)
│       └── reviewed_*.docx (Generated documents)
│
└── 📁 DEPLOYMENT & SCRIPTS
    ├── Dockerfile 🐳 (Container setup)
    ├── requirements.txt 📋 (Python dependencies)
    ├── apprunner.yaml ☁️ (AWS App Runner config)
    ├── deploy*.sh/bat 🚀 (Deployment scripts)
    └── test_*.py 🧪 (Testing scripts)
```

## 🔗 Import Dependency Chain

### **Core Application Dependencies**

```python
# app.py (Main Flask Application)
from flask import Flask, render_template, request, jsonify, send_file, session
import os, json, uuid, datetime
from collections import defaultdict
from werkzeug.utils import secure_filename

# Import our modular components
from core.document_analyzer import DocumentAnalyzer
from core.ai_feedback_engine import AIFeedbackEngine  
from utils.statistics_manager import StatisticsManager
from utils.document_processor import DocumentProcessor
from utils.pattern_analyzer import DocumentPatternAnalyzer
from utils.audit_logger import AuditLogger
from utils.learning_system import FeedbackLearningSystem
from config.model_config import model_config
```

### **Core Module Dependencies**

```python
# core/document_analyzer.py
import json, re, os, datetime
from collections import defaultdict
try:
    import boto3          # Optional: For AI-based section detection
    from docx import Document  # Required: Document parsing
except ImportError:
    # Graceful degradation

# core/ai_feedback_engine.py  
import json, re, boto3, os, time
from datetime import datetime
from collections import defaultdict
from config.model_config import model_config  # Model configuration
```

### **Utility Module Dependencies**

```python
# utils/statistics_manager.py
import json
from collections import defaultdict
from datetime import datetime

# utils/document_processor.py
import os, json, zipfile, shutil, uuid
from datetime import datetime
from docx import Document
from docx.shared import RGBColor, Pt
from lxml import etree

# utils/pattern_analyzer.py
import json, os
from datetime import datetime  
from collections import defaultdict

# utils/audit_logger.py
import json, os, uuid
from datetime import datetime
from collections import defaultdict

# utils/learning_system.py
import json, os
from datetime import datetime
from collections import defaultdict
```

## 🎪 Frontend Script Loading Order & Dependencies

### **HTML Template Dependencies**
```html
<!-- templates/enhanced_index.html -->
<script src="/static/js/app.js"></script>                    <!-- 1. Base application -->
<script src="/static/js/button_fixes.js"></script>           <!-- 2. Core UI functions -->
<script src="/static/js/missing_functions.js"></script>      <!-- 3. Utility functions -->
<script src="/static/js/text_highlighting.js"></script>      <!-- 4. Text features -->
<script src="/static/js/custom_feedback_functions.js"></script> <!-- 5. AI enhancements -->
<script src="/static/js/user_feedback_management.js"></script>  <!-- 6. User feedback -->
<script src="/static/js/custom_feedback_help.js"></script>    <!-- 7. Help functions -->
<script src="/static/js/text_highlight_comments.js"></script> <!-- 8. Comment system -->
<script src="/static/js/enhanced_help_system.js"></script>    <!-- 9. Help system -->
<script src="/static/js/custom_feedback_fix.js"></script>     <!-- 10. Bug fixes -->
```

### **JavaScript Module Relationships**
```javascript
// Global Variables Flow
app.js
├── Defines: console.log('AI-Prism app.js loaded')
└── Coordinates: Module loading

button_fixes.js  
├── Defines: Core UI variables (currentSession, sections, etc.)
├── Depends on: Global window scope
└── Used by: ALL other modules

text_highlighting.js
├── Defines: window.currentHighlightColor, highlightedTexts
├── Depends on: DOM manipulation, session storage
└── Used by: text_highlight_comments.js

user_feedback_management.js
├── Defines: window.userFeedbackHistory, display functions
├── Depends on: Global session state
└── Used by: custom_feedback_functions.js

custom_feedback_functions.js
├── Defines: AI enhancement functions
├── Depends on: User feedback management
└── Used by: Button event handlers

progress_functions.js  
├── Defines: Progress display functions
├── Depends on: Loading media, animation systems
└── Used by: Section loading, analysis progress

enhanced_help_system.js
├── Defines: Help system functions (tutorials, FAQ)
├── Depends on: Modal system, DOM manipulation
└── Used by: Help buttons, keyboard shortcuts

custom_feedback_fix.js
├── Defines: Consolidated feedback functions
├── Depends on: ALL feedback-related modules
└── Used by: Main feedback form
```

## 🔄 Data Flow Dependencies

### **Session Data Relationships**

```
ReviewSession Object (app.py:60-83)
├── session_id: str (UUID)
├── document_name: str
├── document_path: str  
├── guidelines_name: str
├── guidelines_path: str
├── guidelines_preference: str
├── sections: dict
├── section_paragraphs: dict  
├── paragraph_indices: dict
├── current_section: int
├── feedback_data: dict
├── accepted_feedback: defaultdict(list)
├── rejected_feedback: defaultdict(list)
├── user_feedback: defaultdict(list)
├── chat_history: list
├── activity_log: list
├── patterns_data: dict
├── learning_data: dict
├── audit_logger: AuditLogger instance
├── pattern_analyzer: DocumentPatternAnalyzer instance
└── learning_system: FeedbackLearningSystem instance
```

### **Frontend State Dependencies**

```javascript
// Global State Variables (Enhanced Index HTML)
window.currentSession = null;           // Current session ID
window.sections = [];                   // Section names array
window.currentSectionIndex = 0;         // Current section index
window.selectedFeedbackId = null;       // Selected feedback item
window.feedbackStates = {};            // Accept/reject states
window.analysisFile = null;            // Uploaded analysis file
window.guidelinesFile = null;          // Uploaded guidelines file
window.chatHistory = [];               // Chat message history
window.userFeedbackHistory = [];       // User feedback tracking
window.finalDocumentData = null;       // Export document data
window.isDarkMode = false;             // Theme state
window.documentZoom = 100;             // Zoom level
window.dashboardData = {};             // Analytics data

// Text Highlighting State
window.currentHighlightColor = 'yellow';
window.highlightedTexts = [];
window.highlightCounter = 0;
window.currentSelectedText = '';
window.currentSelectedRange = null;
```

## 🎯 API Endpoint Dependencies

### **Flask Route → Function → Module Mapping**

```python
# app.py Flask Routes and their Dependencies

@app.route('/')
└── render_template('enhanced_index.html')
    └── Loads: ALL frontend JavaScript modules

@app.route('/upload', methods=['POST'])  
├── Uses: DocumentAnalyzer.extract_sections_from_docx()
├── Creates: ReviewSession object
├── Updates: AuditLogger, StatisticsManager
└── Returns: Session data + sections list

@app.route('/analyze_section', methods=['POST'])
├── Uses: AIFeedbackEngine.analyze_section()
├── Updates: StatisticsManager, AuditLogger, LearningSystem  
├── Stores: Feedback data in session
└── Returns: Analyzed feedback items

@app.route('/accept_feedback', methods=['POST'])
├── Updates: ReviewSession.accepted_feedback
├── Uses: StatisticsManager.record_acceptance()
├── Uses: LearningSystem.record_ai_feedback_response()
└── Uses: AuditLogger.log()

@app.route('/reject_feedback', methods=['POST'])  
├── Updates: ReviewSession.rejected_feedback
├── Uses: StatisticsManager.record_rejection()
├── Uses: LearningSystem.record_ai_feedback_response()
└── Uses: AuditLogger.log()

@app.route('/add_custom_feedback', methods=['POST'])
├── Updates: ReviewSession.user_feedback
├── Uses: StatisticsManager.add_user_feedback()  
├── Uses: LearningSystem.add_custom_feedback()
└── Uses: AuditLogger.log()

@app.route('/chat', methods=['POST'])
├── Uses: AIFeedbackEngine.process_chat_query()
├── Updates: ReviewSession.chat_history
├── Uses: AuditLogger.log()  
└── Returns: AI chat response

@app.route('/complete_review', methods=['POST'])
├── Uses: DocumentProcessor.create_document_with_comments()
├── Processes: All accepted feedback + user feedback
├── Generates: Final Word document with comments
└── Uses: AuditLogger.log()

@app.route('/get_statistics', methods=['GET'])
├── Uses: StatisticsManager.get_statistics()
├── Rebuilds: Statistics from current session
└── Returns: Complete analytics data

@app.route('/get_patterns', methods=['GET'])  
├── Uses: PatternAnalyzer.find_recurring_patterns()
├── Uses: PatternAnalyzer.get_pattern_report_html()
└── Returns: Pattern analysis results

@app.route('/get_logs', methods=['GET'])
├── Uses: AuditLogger.generate_audit_report_html()
├── Uses: AuditLogger.get_session_logs()
└── Returns: Activity logs and metrics

@app.route('/get_learning_status', methods=['GET'])
├── Uses: LearningSystem.get_learning_statistics()
├── Uses: LearningSystem.generate_learning_report_html()  
└── Returns: AI learning status and recommendations
```

## 🔧 Cross-Module Communication

### **Module Interaction Patterns**

```
app.py (Central Coordinator)
├── Initializes ALL modules in try/except block
├── Passes data between modules
├── Manages module lifecycles
└── Handles module errors gracefully

Core Modules Communication:
DocumentAnalyzer → AIFeedbackEngine
    ├── Provides: Parsed document sections
    └── Receives: AI analysis requests

AIFeedbackEngine → Multiple Utilities  
    ├── Triggers: StatisticsManager updates
    ├── Feeds: LearningSystem with response data
    └── Logs: AuditLogger activity

Utility Modules Cross-Communication:
StatisticsManager ↔ All other utilities
    ├── Collects: Data from all sources
    └── Provides: Analytics to frontend

PatternAnalyzer ↔ LearningSystem
    ├── Shares: User behavior patterns
    └── Identifies: Learning opportunities

AuditLogger ← ALL modules
    └── Records: All activities across system
```

### **Frontend Module Dependencies**

```javascript
// JavaScript Module Communication Chain

app.js (Base initialization)
    ↓
button_fixes.js (Core functionality)
    ├── Defines global functions used by ALL modules
    ├── Provides: showNotification(), showModal(), etc.
    └── Used by: Every other JS module
    ↓
text_highlighting.js (Text features)
    ├── Depends on: Global variables from button_fixes
    ├── Provides: Highlighting functionality
    └── Used by: text_highlight_comments.js
    ↓
user_feedback_management.js (Feedback display)
    ├── Depends on: Global session state
    ├── Provides: User feedback display functions  
    └── Used by: custom_feedback_functions.js
    ↓
custom_feedback_functions.js (AI enhancements)
    ├── Depends on: User feedback management
    ├── Provides: AI suggestion enhancement
    └── Used by: Main feedback workflows
    ↓
enhanced_help_system.js (Help system)
    ├── Depends on: Modal system from button_fixes
    ├── Provides: Interactive help features
    └── Used by: Help buttons and tutorials
```

## 🎭 File Size & Complexity Analysis

### **Code Complexity Matrix**

| File | Lines | Complexity | Dependencies | Usage |
|------|-------|------------|--------------|-------|
| [`app.py`](app.py:1) | 1,526 | **HIGH** ⚡ | 8 modules | **CRITICAL** 🎯 |
| [`enhanced_index.html`](templates/enhanced_index.html:1) | 7,621 | **VERY HIGH** ⚡⚡ | 10 JS files | **CRITICAL** 🎯 |
| [`core/ai_feedback_engine.py`](core/ai_feedback_engine.py:1) | 635 | **HIGH** ⚡ | AWS/Bedrock | **CRITICAL** 🎯 |
| [`button_fixes.js`](static/js/button_fixes.js:1) | 892 | **HIGH** ⚡ | Global state | **CRITICAL** 🎯 |
| [`user_feedback_management.js`](static/js/user_feedback_management.js:1) | 615 | **MEDIUM** 📊 | UI components | **HIGH** 📈 |
| [`text_highlighting.js`](static/js/text_highlighting.js:1) | 558 | **MEDIUM** 📊 | DOM/Storage | **HIGH** 📈 |
| [`utils/statistics_manager.py`](utils/statistics_manager.py:1) | 375 | **MEDIUM** 📊 | Collections | **HIGH** 📈 |
| [`utils/document_processor.py`](utils/document_processor.py:1) | 359 | **MEDIUM** 📊 | docx/XML | **HIGH** 📈 |

### **Dependency Risk Assessment**

| Dependency Type | Risk Level | Files Affected | Mitigation |
|-----------------|------------|----------------|------------|
| **AWS Bedrock** | 🟡 MEDIUM | `core/ai_feedback_engine*.py` | Mock fallback system |
| **python-docx** | 🟢 LOW | `core/document_analyzer.py`, `utils/document_processor.py` | Standard library |
| **Frontend JS** | 🟡 MEDIUM | `templates/*.html` | Graceful degradation |
| **File System** | 🟢 LOW | `utils/*.py` | Error handling + cleanup |
| **Session Memory** | 🟠 HIGH | `app.py` session storage | Persistent backup options |

## 🎪 Component Startup Sequence

### **Application Bootstrap Order**

```
1. Environment Setup
   ├── Load .env file (if exists)
   ├── Set AWS credentials  
   ├── Configure Flask settings
   └── Create required directories

2. Module Initialization (app.py:38-56)
   ├── DocumentAnalyzer() ✅
   ├── AIFeedbackEngine() ✅  
   ├── StatisticsManager() ✅
   ├── DocumentProcessor() ✅
   ├── DocumentPatternAnalyzer() ✅
   ├── AuditLogger() ✅
   └── FeedbackLearningSystem() ✅

3. Flask Application Setup
   ├── Route registration
   ├── Session configuration
   ├── Error handler setup
   └── Static file serving

4. Web Server Start
   ├── Host: 0.0.0.0 (production) 
   ├── Port: Configurable
   ├── Threading: Enabled
   └── Debug: Environment-based

5. Frontend Loading (browser)
   ├── HTML template render
   ├── CSS styling application
   ├── JavaScript modules loading
   ├── Event listener setup
   └── User interface ready
```

## 🔄 Data Persistence Strategy

### **Storage Architecture**

```
MEMORY STORAGE (Runtime)
├── sessions{} dict
│   └── ReviewSession objects
│       ├── Document content
│       ├── AI feedback data
│       ├── User interactions
│       └── Session state

PERSISTENT STORAGE (Files)
├── data/learning_data.json
│   ├── User preferences
│   ├── Feedback patterns  
│   └── Learning metrics

├── data/pattern_analysis.json
│   ├── Cross-document patterns
│   ├── Recurring issues
│   └── Trend analysis

├── data/audit_logs.json  
│   ├── User activities
│   ├── System events
│   └── Performance metrics

└── data/tool_feedback.json
    ├── User tool feedback
    └── Improvement suggestions

TEMPORARY STORAGE (Session-based)
├── uploads/[timestamp]_*.docx
│   └── User uploaded documents
├── reviewed_*.docx
│   └── Generated documents  
└── sessionStorage (browser)
    └── Highlighted text data
```

## 🎯 Critical Path Analysis

### **Essential Files for Core Functionality**

**🔴 CRITICAL (System breaks without these)**
- [`app.py`](app.py:1) - Main application logic
- [`core/document_analyzer.py`](core/document_analyzer.py:1) - Document processing
- [`templates/enhanced_index.html`](templates/enhanced_index.html:1) - User interface
- [`static/js/button_fixes.js`](static/js/button_fixes.js:1) - Core UI functions

**🟡 HIGH PRIORITY (Major features break)**
- [`core/ai_feedback_engine.py`](core/ai_feedback_engine.py:1) - AI analysis
- [`utils/statistics_manager.py`](utils/statistics_manager.py:1) - Analytics
- [`static/js/user_feedback_management.js`](static/js/user_feedback_management.js:1) - User feedback

**🟢 MEDIUM PRIORITY (Advanced features)**
- [`utils/document_processor.py`](utils/document_processor.py:1) - Document export
- [`static/js/text_highlighting.js`](static/js/text_highlighting.js:1) - Text features
- [`utils/pattern_analyzer.py`](utils/pattern_analyzer.py:1) - Pattern analysis

**🔵 LOW PRIORITY (Enhancement features)**
- [`utils/learning_system.py`](utils/learning_system.py:1) - AI learning
- [`static/js/enhanced_help_system.js`](static/js/enhanced_help_system.js:1) - Help system
- [`ui/responsive_interface.py`](ui/responsive_interface.py:1) - Jupyter interface

## 🎪 Module Interaction Summary

### **File Relationship Categories**

**🏗️ Foundation Layer**
```
app.py (Flask application core)
├── Orchestrates: ALL backend modules
├── Manages: Session lifecycle, API endpoints
└── Coordinates: Frontend-backend communication
```

**🧠 Processing Layer**
```  
core/*.py (Analysis engines)
├── document_analyzer.py: Document → Sections
├── ai_feedback_engine.py: Sections → AI feedback
└── Shared: Hawkeye framework knowledge
```

**🛠️ Service Layer**
```
utils/*.py (Supporting services)
├── statistics_manager.py: Metrics & analytics
├── document_processor.py: Export generation  
├── pattern_analyzer.py: Cross-document insights
├── audit_logger.py: Activity tracking
└── learning_system.py: AI improvement
```

**🎨 Presentation Layer**
```
templates/ + static/ (User interface)
├── enhanced_index.html: Complete UI framework
├── static/js/*.js: Interactive functionality
├── Responsive design: Mobile/tablet/desktop
└── Rich features: Dark mode, shortcuts, help
```

**⚙️ Configuration Layer**
```
config/ + Environment (Settings & setup)
├── model_config.py: AI model configuration
├── Environment variables: AWS, Flask settings  
├── Deployment configs: Docker, App Runner
└── Testing scripts: Validation & diagnostics
```

This comprehensive dependency analysis shows how AI-Prism's 50+ files work together in a sophisticated, interconnected system to deliver professional document analysis capabilities.