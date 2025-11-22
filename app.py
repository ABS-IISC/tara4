from flask import Flask, render_template, request, jsonify, send_file, session
import os
import sys
import json
import uuid
from datetime import datetime
from collections import defaultdict
from werkzeug.utils import secure_filename

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modular components with error handling
try:
    from core.document_analyzer import DocumentAnalyzer
    from core.ai_feedback_engine import AIFeedbackEngine
    from core.database_manager import db_manager  # ✅ NEW: Auto-save database
    from utils.statistics_manager import StatisticsManager
    from utils.document_processor import DocumentProcessor
    from utils.pattern_analyzer import DocumentPatternAnalyzer
    from utils.audit_logger import AuditLogger
    from utils.learning_system import FeedbackLearningSystem
    from utils.s3_export_manager import S3ExportManager
    from utils.activity_logger import ActivityLogger
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Creating fallback components...")

# ✅ RQ (Redis Queue) - Simpler, no signature expiration, no S3 polling
# Replaced Celery + SQS + S3 backend with RQ + Redis (100% free, open source)

# ✅ Import RQ Tasks (NEW - Multi-model fallback WITHOUT Celery complexity)
ENHANCED_MODE = False
RQ_ENABLED = False  # Track if RQ is available
try:
    from rq_tasks import (
        analyze_section_task,
        process_chat_task,
        monitor_health
    )
    from rq_config import get_queue, is_rq_available, redis_conn
    from rq.job import Job
    from core.async_request_manager import get_async_request_manager
    from config.model_config_enhanced import get_default_models

    # Check if Redis is actually running
    if is_rq_available():
        ENHANCED_MODE = True
        RQ_ENABLED = True  # RQ is available when Redis is running
        print("✅ ✨ ENHANCED MODE ACTIVATED (RQ) ✨")
        print("   Features enabled:")
        print("   • Multi-model fallback (Claude Sonnet 4.5)")
        print("   • Extended thinking capability")
        print("   • RQ task queue (NO signature expiration!)")
        print("   • Redis result storage (NO S3 polling!)")
        print("   • 100% Free & Open Source")
        print("   • us-east-2 region for Bedrock")
    else:
        print("⚠️ Redis not running - RQ disabled")
        print("   Start Redis: brew services start redis")

    # Display available models
    try:
        models = get_default_models()
        print(f"   • Loaded {len(models)} Claude models:")
        for model in models:
            thinking = " [Extended Thinking]" if model.supports_extended_thinking else ""
            print(f"     {model.priority}. {model.name}{thinking}")
    except Exception as e:
        print(f"   ⚠️  Could not load model details: {e}")

except ImportError as e:
    print(f"❌ CRITICAL: Enhanced mode import failed: {e}")
    print("   Application requires these components to function.")
    print("   Please ensure all dependencies are installed: pip install -r requirements.txt")
    ENHANCED_MODE = False
    # Don't create fallback classes - let the real import errors show
    raise ImportError(f"Required components not available: {e}")

# Simple model config class for Flask app settings
class SimpleModelConfig:
    """Simplified model config for Flask application settings"""
    def get_model_config(self):
        return {
            'model_id': os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'),
            'model_name': 'Claude Sonnet 4.5 (Enhanced)',
            'region': os.environ.get('AWS_REGION', 'us-east-2'),
            'port': int(os.environ.get('PORT', 8080)),
            'flask_env': os.environ.get('FLASK_ENV', 'production')
        }

    def has_credentials(self):
        """Check if AWS credentials are configured"""
        return bool(os.environ.get('AWS_ACCESS_KEY_ID') or os.environ.get('AWS_PROFILE'))

    def print_config_summary(self):
        """Print configuration summary"""
        config = self.get_model_config()
        print(f"✅ Model Configuration:")
        print(f"   • Model: {config['model_name']}")
        print(f"   • Region: {config['region']}")
        print(f"   • Port: {config['port']}")
        print(f"   • Environment: {config['flask_env']}")
        print(f"   • AWS Credentials: {'✅ Configured' if self.has_credentials() else '❌ Not configured'}")

model_config = SimpleModelConfig()

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Add CORS support to fix NetworkError issues
@app.after_request
def after_request(response):
    """Add CORS headers to all responses to prevent NetworkError"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    response.headers.add('Pragma', 'no-cache')
    return response

# Handle OPTIONS requests for CORS preflight
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path=''):
    """Handle CORS preflight requests"""
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Load environment variables from .env file if it exists
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Global components - with error handling
try:
    document_analyzer = DocumentAnalyzer()
    ai_engine = AIFeedbackEngine()
    stats_manager = StatisticsManager()
    doc_processor = DocumentProcessor()
    pattern_analyzer = DocumentPatternAnalyzer()
    audit_logger = AuditLogger()
    learning_system = FeedbackLearningSystem()
    s3_export_manager = S3ExportManager()
    
    print("AI-Prism components initialized successfully")
    
    # Print comprehensive model configuration
    model_config.print_config_summary()
        
except Exception as e:
    print(f"Error initializing AI-Prism components: {e}")
    import traceback
    traceback.print_exc()

# Session storage with thread safety
import threading
sessions = {}
sessions_lock = threading.Lock()  # Protect concurrent access to sessions dictionary

# Thread-safe session access helpers
def get_session(session_id):
    """Thread-safe session retrieval"""
    with sessions_lock:
        return sessions.get(session_id)

def set_session(session_id, review_session):
    """Thread-safe session storage"""
    with sessions_lock:
        sessions[session_id] = review_session

def delete_session(session_id):
    """Thread-safe session deletion"""
    with sessions_lock:
        if session_id in sessions:
            del sessions[session_id]

def session_exists(session_id):
    """Thread-safe session existence check"""
    with sessions_lock:
        return session_id in sessions

class ReviewSession:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.document_name = ""
        self.document_path = ""
        self.guidelines_name = ""
        self.guidelines_path = ""
        self.guidelines_preference = "both"
        self.sections = {}
        self.section_paragraphs = {}
        self.paragraph_indices = {}
        self.current_section = 0
        self.feedback_data = {}
        self.accepted_feedback = defaultdict(list)
        self.rejected_feedback = defaultdict(list)
        self.user_feedback = defaultdict(list)
        self.chat_history = []
        self.activity_log = []
        self.patterns_data = {}
        self.learning_data = {}
        self.audit_logger = AuditLogger()
        self.pattern_analyzer = DocumentPatternAnalyzer()
        self.learning_system = FeedbackLearningSystem()
        self.activity_logger = ActivityLogger(self.session_id)

@app.route('/')
def index():
    return render_template('enhanced_index.html')

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        if 'document' not in request.files:
            return jsonify({'error': 'No analysis document uploaded'}), 400
        
        analysis_file = request.files['document']
        if analysis_file.filename == '':
            return jsonify({'error': 'No analysis document selected'}), 400
        
        if not analysis_file.filename.lower().endswith('.docx'):
            return jsonify({'error': 'Only .docx files are supported for analysis document'}), 400
        
        # Get guidelines preference
        guidelines_preference = request.form.get('guidelines_preference', 'both')
        
        # Create new session
        session_id = str(uuid.uuid4())
        review_session = ReviewSession()
        review_session.session_id = session_id
        review_session.guidelines_preference = guidelines_preference
        
        # Save analysis document
        filename = secure_filename(analysis_file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        analysis_file.save(file_path)
        
        review_session.document_name = filename
        review_session.document_path = file_path
        
        # Handle optional guidelines document
        guidelines_uploaded = False
        if 'guidelines' in request.files and guidelines_preference != 'old_only':
            guidelines_file = request.files['guidelines']
            if guidelines_file.filename != '' and guidelines_file.filename.lower().endswith('.docx'):
                guidelines_filename = secure_filename(guidelines_file.filename)
                guidelines_safe_filename = f"{timestamp}_guidelines_{guidelines_filename}"
                guidelines_path = os.path.join(app.config['UPLOAD_FOLDER'], guidelines_safe_filename)
                guidelines_file.save(guidelines_path)
                
                review_session.guidelines_path = guidelines_path
                review_session.guidelines_name = guidelines_filename
                guidelines_uploaded = True
        
        # Extract sections using document analyzer
        sections, section_paragraphs, paragraph_indices = document_analyzer.extract_sections_from_docx(file_path)
        
        review_session.sections = sections
        review_session.section_paragraphs = section_paragraphs
        review_session.paragraph_indices = paragraph_indices

        # Store session (thread-safe)
        set_session(session_id, review_session)
        session['session_id'] = session_id
        
        # Log activity with comprehensive tracking
        file_size = os.path.getsize(file_path)
        review_session.activity_logger.log_document_upload(filename, file_size, success=True)
        
        if guidelines_uploaded:
            guidelines_size = os.path.getsize(review_session.guidelines_path)
            review_session.activity_logger.log_document_upload(review_session.guidelines_name, guidelines_size, success=True)
        
        review_session.activity_logger.log_session_event('documents_uploaded', {
            'analysis_document': filename,
            'guidelines_document': review_session.guidelines_name if guidelines_uploaded else None,
            'sections_detected': len(sections),
            'guidelines_preference': guidelines_preference
        })
        
        # Legacy logging
        log_details = f'Analysis document {filename} uploaded with {len(sections)} sections'
        if guidelines_uploaded:
            log_details += f', Guidelines document {review_session.guidelines_name} also uploaded'
        log_details += f', Guidelines preference: {guidelines_preference}'
            
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'DOCUMENTS_UPLOADED',
            'details': log_details
        })
        
        # Log with audit logger
        review_session.audit_logger.log('DOCUMENTS_UPLOADED', log_details)

        # ✅ NEW: Save to database
        try:
            db_manager.create_review_session(
                session_id=session_id,
                document_name=filename,
                sections=list(sections.keys())
            )
            print(f"✅ Database: Review session created for {session_id}")
        except Exception as db_error:
            print(f"⚠️ Database save error: {db_error}")

        return jsonify({
            'success': True,
            'session_id': session_id,
            'document_name': filename,
            'sections': list(sections.keys()),
            'total_sections': len(sections),
            'guidelines_uploaded': guidelines_uploaded,
            'guidelines_preference': guidelines_preference
        })
        
    except Exception as e:
        print(f"ERROR Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

# ✅ NEW ENDPOINT: Get section content without analysis
@app.route('/get_section_content', methods=['POST'])
def get_section_content():
    """Get section content without triggering analysis - for manual workflow"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        section_name = data.get('section_name')

        if not session_id or not section_name:
            return jsonify({'success': False, 'error': 'Missing session_id or section_name'}), 400

        if not session_exists(session_id):
            return jsonify({'success': False, 'error': 'Invalid or expired session'}), 400

        # Get document sections
        review_session = get_session(session_id)
        sections_dict = review_session.sections

        if section_name not in sections_dict:
            return jsonify({'success': False, 'error': f'Section "{section_name}" not found'}), 404

        # Return just the content
        return jsonify({
            'success': True,
            'content': sections_dict[section_name],
            'section_name': section_name
        })

    except Exception as e:
        print(f"ERROR getting section content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/analyze_section', methods=['POST'])
def analyze_section():
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
            
        session_id = data.get('session_id') or session.get('session_id')
        section_name = data.get('section_name')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'No session ID provided'}), 400

        if not session_exists(session_id):
            return jsonify({'success': False, 'error': 'Invalid or expired session'}), 400

        if not section_name:
            return jsonify({'success': False, 'error': 'No section name provided'}), 400

        review_session = get_session(session_id)
        
        if section_name not in review_session.sections:
            return jsonify({'success': False, 'error': f'Section "{section_name}" not found in document'}), 400
        
        section_content = review_session.sections[section_name]
        
        if not section_content or section_content.strip() == '':
            return jsonify({
                'success': True,
                'feedback_items': [],
                'section_content': 'This section appears to be empty.',
                'message': 'Section is empty - no analysis needed'
            })
        
        import sys
        sys.stdout.flush()  # Force flush print buffer

        print("=" * 80, flush=True)
        print(f"🔍 ANALYZE_SECTION CALLED", flush=True)
        print(f"   Section: {section_name}", flush=True)
        print(f"   Content length: {len(section_content)} characters", flush=True)
        print(f"   Content preview: {section_content[:100]}", flush=True)
        print("=" * 80, flush=True)
        sys.stdout.flush()

        # ✅ Check if Enhanced Mode is available (NEW - RQ with multi-model fallback)
        if ENHANCED_MODE and RQ_ENABLED:
            # Use RQ async processing (simpler than Celery, no signature expiration!)
            print(f"✨ Submitting to RQ task queue (NO signature expiration!)", flush=True)

            # Submit task to RQ queue
            queue = get_queue('analysis')
            job = queue.enqueue(
                analyze_section_task,
                args=(section_name, section_content, "Full Write-up", session_id),
                job_timeout=300  # 5 minutes timeout
            )

            # Return job ID for async polling + section content for immediate display
            return jsonify({
                'success': True,
                'task_id': job.id,
                'status': 'queued',
                'message': 'Analysis started with RQ (NO AWS signature expiration!)',
                'async': True,
                'enhanced': True,
                'section_content': section_content,  # ✅ Include section content for frontend display
                'features': {
                    'rq_queue': True,
                    'multi_model_fallback': True,
                    'extended_thinking': True,
                    'no_signature_expiration': True,
                    'redis_result_storage': True
                }
            })

        # Check if standard Celery is available
        elif RQ_ENABLED:
            # Submit task to standard Celery queue
            print(f"📤 Submitting analysis task to standard Celery queue", flush=True)
            task_id, is_async = submit_analysis_task(
                section_name=section_name,
                content=section_content,
                doc_type="Full Write-up",
                session_id=session_id
            )

            if is_async:
                # Return task ID for async polling
                return jsonify({
                    'success': True,
                    'task_id': task_id,
                    'status': 'processing',
                    'message': 'Analysis task submitted to queue',
                    'async': True
                })
            else:
                # Celery not available, got result directly
                analysis_result = task_id  # task_id is actually the result in sync mode
        else:
            # Analyze with AI engine with timing (synchronous fallback)
            analysis_start_time = datetime.now()
            try:
                print(f"📞 Calling ai_engine.analyze_section()", flush=True)
                sys.stdout.flush()

                review_session.activity_logger.start_operation('ai_analysis', {
                    'section': section_name,
                    'content_length': len(section_content)
                })

                analysis_result = ai_engine.analyze_section(section_name, section_content)

                analysis_duration = (datetime.now() - analysis_start_time).total_seconds()
                feedback_count = len(analysis_result.get('feedback_items', []))

                print(f"✅ AI analysis completed!", flush=True)
                print(f"   Duration: {analysis_duration:.2f}s", flush=True)
                print(f"   Feedback items: {feedback_count}", flush=True)
                print(f"   Result keys: {list(analysis_result.keys())}", flush=True)
                sys.stdout.flush()

                review_session.activity_logger.complete_operation(success=True, details={
                    'feedback_generated': feedback_count,
                    'analysis_duration': analysis_duration
                })

                review_session.activity_logger.log_ai_analysis(section_name, feedback_count, analysis_duration, success=True)

            except Exception as ai_error:
                analysis_duration = (datetime.now() - analysis_start_time).total_seconds()

                review_session.activity_logger.complete_operation(success=False, error=str(ai_error))
                review_session.activity_logger.log_ai_analysis(section_name, 0, analysis_duration, success=False, error=str(ai_error))

                print(f"AI analysis failed: {str(ai_error)}")
                analysis_result = {
                    'feedback_items': [],
                    'error': f'AI analysis failed: {str(ai_error)}',
                    'fallback': True
                }
        
        # Ensure we have a valid result structure
        if not isinstance(analysis_result, dict):
            print(f"Invalid analysis result type: {type(analysis_result)}")
            analysis_result = {'feedback_items': [], 'error': 'Invalid result format'}
        
        feedback_items = analysis_result.get('feedback_items', [])
        if not isinstance(feedback_items, list):
            print(f"Invalid feedback_items type: {type(feedback_items)}")
            feedback_items = []
        
        # If no feedback items and analysis failed, create a basic feedback item
        if not feedback_items and analysis_result.get('error'):
            print(f"Creating fallback feedback for failed analysis")
            feedback_items = [{
                'id': f"{section_name}_fallback_{datetime.now().strftime('%H%M%S')}",
                'type': 'suggestion',
                'category': 'Analysis Status',
                'description': f'AI analysis temporarily unavailable for this section. Content appears to be {len(section_content)} characters long.',
                'suggestion': 'Manual review recommended. Check AWS credentials and Bedrock access if real AI analysis is needed.',
                'example': '',
                'questions': ['Is the content complete and accurate?', 'Are there any obvious gaps or issues?'],
                'hawkeye_refs': [13],
                'risk_level': 'Low',
                'confidence': 0.5
            }]
        
        # Validate feedback items structure
        if not isinstance(feedback_items, list):
            print(f"Invalid feedback_items type: {type(feedback_items)}")
            feedback_items = []
        
        # Ensure each feedback item has required fields
        validated_feedback = []
        for i, item in enumerate(feedback_items):
            if isinstance(item, dict):
                # Ensure required fields exist
                validated_item = {
                    'id': item.get('id', f"{section_name}_{i}_{datetime.now().strftime('%H%M%S')}"),
                    'type': item.get('type', 'suggestion'),
                    'category': item.get('category', 'General'),
                    'description': item.get('description', 'No description provided'),
                    'suggestion': item.get('suggestion', ''),
                    'example': item.get('example', ''),
                    'questions': item.get('questions', []) if isinstance(item.get('questions'), list) else [],
                    'hawkeye_refs': item.get('hawkeye_refs', []) if isinstance(item.get('hawkeye_refs'), list) else [],
                    'risk_level': item.get('risk_level', 'Low'),
                    'confidence': float(item.get('confidence', 0.8)) if isinstance(item.get('confidence'), (int, float)) else 0.8
                }
                validated_feedback.append(validated_item)
            else:
                print(f"Skipping invalid feedback item {i}: {type(item)}")
        
        feedback_items = validated_feedback
        
        # Log final result
        print(f"Section analysis completed: {section_name} - {len(feedback_items)} validated feedback items")
        
        # Store feedback data
        review_session.feedback_data[section_name] = feedback_items
        
        # Update statistics immediately
        try:
            stats_manager.update_feedback_data(section_name, feedback_items)
        except Exception as stats_error:
            print(f"WARNING Statistics update failed: {stats_error}")
        
        # Log activity
        try:
            review_session.activity_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'SECTION_ANALYZED',
                'details': f'Section {section_name} analyzed - {len(feedback_items)} feedback items generated'
            })
            
            # Log with audit logger
            review_session.audit_logger.log('SECTION_ANALYZED', f'Section {section_name} analyzed - {len(feedback_items)} feedback items generated')
        except Exception as log_error:
            print(f"WARNING Logging failed: {log_error}")
        
        print(f"SUCCESS Section analysis completed: {section_name} - {len(feedback_items)} feedback items")
        
        return jsonify({
            'success': True,
            'feedback_items': feedback_items,
            'section_content': section_content,
            'section_name': section_name,
            'analysis_timestamp': datetime.now().isoformat()
        })
        
    except json.JSONDecodeError as json_error:
        print(f"❌ JSON decode error: {str(json_error)}")
        return jsonify({'success': False, 'error': 'Invalid JSON in request'}), 400
        
    except Exception as e:
        print(f"ERROR Analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Always return valid JSON even on error
        return jsonify({
            'success': False, 
            'error': f'Analysis failed: {str(e)}',
            'error_type': type(e).__name__,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/accept_feedback', methods=['POST'])
def accept_feedback():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        section_name = data.get('section_name')
        feedback_id = data.get('feedback_id')

        # Validate that section_name is a string, not a dict
        if isinstance(section_name, dict):
            return jsonify({'error': 'Invalid section_name format (expected string, got dict)'}), 400

        if not section_name or not isinstance(section_name, str):
            return jsonify({'error': 'Invalid or missing section_name'}), 400

        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400

        review_session = get_session(session_id)

        # Find the feedback item
        feedback_item = None
        for item in review_session.feedback_data.get(section_name, []):
            if item.get('id') == feedback_id:
                feedback_item = item
                break

        if not feedback_item:
            return jsonify({'error': 'Feedback item not found'}), 400

        # Add to accepted feedback
        review_session.accepted_feedback[section_name].append(feedback_item)
        
        # Update statistics
        stats_manager.record_acceptance(section_name, feedback_item)
        
        # Log activity with comprehensive tracking - ENHANCED with more details
        review_session.activity_logger.log_feedback_action(
            'accepted',
            feedback_id,
            section_name,
            feedback_item.get('description'),
            feedback_type=feedback_item.get('type'),
            risk_level=feedback_item.get('risk_level'),
            confidence=feedback_item.get('confidence', 0.8)
        )
        
        # Legacy logging
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'FEEDBACK_ACCEPTED',
            'details': f'Accepted {feedback_item.get("type")} feedback in {section_name}'
        })
        
        # Log with audit logger and learning system
        review_session.audit_logger.log('FEEDBACK_ACCEPTED', f'Accepted {feedback_item.get("type")} feedback in {section_name}')
        review_session.learning_system.record_ai_feedback_response(feedback_item, section_name, accepted=True)

        # ✅ NEW: Save to database
        try:
            db_manager.log_activity(session_id, 'FEEDBACK_ACCEPTED', 'success', {
                'section': section_name,
                'type': feedback_item.get('type'),
                'risk_level': feedback_item.get('risk_level')
            })
        except Exception as db_error:
            print(f"⚠️ Database log error: {db_error}")

        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Accept failed: {str(e)}'}), 500

@app.route('/reject_feedback', methods=['POST'])
def reject_feedback():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        section_name = data.get('section_name')
        feedback_id = data.get('feedback_id')

        # Validate that section_name is a string, not a dict
        if isinstance(section_name, dict):
            return jsonify({'error': 'Invalid section_name format (expected string, got dict)'}), 400

        if not section_name or not isinstance(section_name, str):
            return jsonify({'error': 'Invalid or missing section_name'}), 400

        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400

        review_session = get_session(session_id)

        # Find the feedback item
        feedback_item = None
        for item in review_session.feedback_data.get(section_name, []):
            if item.get('id') == feedback_id:
                feedback_item = item
                break

        if not feedback_item:
            return jsonify({'error': 'Feedback item not found'}), 400

        # Add to rejected feedback
        review_session.rejected_feedback[section_name].append(feedback_item)
        
        # Update statistics
        stats_manager.record_rejection(section_name, feedback_item)
        
        # Log activity with comprehensive tracking - ENHANCED with more details
        review_session.activity_logger.log_feedback_action(
            'rejected',
            feedback_id,
            section_name,
            feedback_item.get('description'),
            feedback_type=feedback_item.get('type'),
            risk_level=feedback_item.get('risk_level'),
            confidence=feedback_item.get('confidence', 0.8)
        )
        
        # Legacy logging
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'FEEDBACK_REJECTED',
            'details': f'Rejected {feedback_item.get("type")} feedback in {section_name}'
        })
        

        # Log with audit logger and learning system
        review_session.audit_logger.log('FEEDBACK_REJECTED', f'Rejected {feedback_item.get("type")} feedback in {section_name}')
        review_session.learning_system.record_ai_feedback_response(feedback_item, section_name, accepted=False)

        # ✅ NEW: Save to database
        try:
            db_manager.log_activity(session_id, 'FEEDBACK_REJECTED', 'success', {
                'section': section_name,
                'type': feedback_item.get('type'),
                'risk_level': feedback_item.get('risk_level')
            })
        except Exception as db_error:
            print(f"⚠️ Database log error: {db_error}")

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': f'Reject failed: {str(e)}'}), 500

@app.route('/revert_feedback', methods=['POST'])
def revert_feedback():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        section_name = data.get('section_name')
        feedback_id = data.get('feedback_id')

        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400

        review_session = get_session(session_id)

        # Remove from accepted feedback if present
        if section_name in review_session.accepted_feedback:
            review_session.accepted_feedback[section_name] = [
                item for item in review_session.accepted_feedback[section_name]
                if item.get('id') != feedback_id
            ]

        # Remove from rejected feedback if present
        if section_name in review_session.rejected_feedback:
            review_session.rejected_feedback[section_name] = [
                item for item in review_session.rejected_feedback[section_name]
                if item.get('id') != feedback_id
            ]

        # Log activity
        review_session.activity_logger.log_feedback_action(
            'reverted',
            feedback_id,
            section_name,
            feedback_text="Feedback decision reverted to pending"
        )

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': f'Revert failed: {str(e)}'}), 500

@app.route('/add_custom_feedback', methods=['POST'])
def add_custom_feedback():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        section_name = data.get('section_name')
        feedback_type = data.get('type')
        category = data.get('category')
        description = data.get('description')
        ai_reference = data.get('ai_reference')  # New field for AI-related feedback
        ai_id = data.get('ai_id')  # New field for AI feedback ID
        highlight_id = data.get('highlight_id')  # New field for highlighted text
        highlighted_text = data.get('highlighted_text')  # New field for highlighted text content
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Create custom feedback item
        custom_feedback = {
            'id': f"custom_{datetime.now().strftime('%H%M%S_%f')}",
            'type': feedback_type,
            'category': category,
            'description': description,
            'risk_level': 'Medium' if feedback_type == 'critical' else 'Low',
            'user_created': True,
            'timestamp': datetime.now().isoformat(),
            'hawkeye_refs': [1],  # Default reference
            'confidence': 1.0,
            'ai_reference': ai_reference,  # Store AI reference if provided
            'ai_id': ai_id,  # Store AI feedback ID if provided
            'highlight_id': highlight_id,  # Store highlight ID if provided
            'highlighted_text': highlighted_text  # Store highlighted text if provided
        }
        
        # Add to user feedback and accepted feedback
        review_session.user_feedback[section_name].append(custom_feedback)
        review_session.accepted_feedback[section_name].append(custom_feedback)
        
        # Update statistics
        stats_manager.add_user_feedback(section_name, custom_feedback)
        stats_manager.record_acceptance(section_name, custom_feedback)
        
        # Log activity
        activity_detail = f'Added custom {feedback_type} feedback in {section_name}: {description[:50]}...'
        if ai_reference and ai_id:
            activity_detail += f' (Related to AI feedback: {ai_id})'
        if highlighted_text:
            activity_detail += f' (Highlighted: "{highlighted_text[:30]}...")' if len(highlighted_text) > 30 else f' (Highlighted: "{highlighted_text}")'
        
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'CUSTOM_FEEDBACK_ADDED',
            'details': activity_detail
        })
        
        # Log with audit logger and learning system
        review_session.audit_logger.log('CUSTOM_FEEDBACK_ADDED', activity_detail)
        review_session.learning_system.add_custom_feedback(custom_feedback, section_name)
        
        return jsonify({'success': True, 'feedback_item': custom_feedback})
        
    except Exception as e:
        return jsonify({'error': f'Add custom feedback failed: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        message = data.get('message')
        current_section = data.get('current_section')
        ai_model = data.get('ai_model', 'claude-3-sonnet')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Add user message to history
        review_session.chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat(),
            'ai_model': ai_model
        })
        
        # Get AI response with enhanced context including current feedback
        current_feedback = review_session.feedback_data.get(current_section, [])
        
        context = {
            'current_section': current_section,
            'document_name': review_session.document_name,
            'total_sections': len(review_session.sections),
            'current_feedback': current_feedback,
            'ai_model': ai_model,
            'guidelines_preference': getattr(review_session, 'guidelines_preference', 'both'),
            'accepted_count': len(review_session.accepted_feedback.get(current_section, [])),
            'rejected_count': len(review_session.rejected_feedback.get(current_section, []))
        }
        
        # Check if RQ is available for async processing
        if RQ_ENABLED and ENHANCED_MODE:
            # Submit task to RQ queue
            print(f"📤 Submitting chat task to RQ queue", flush=True)

            queue = get_queue('chat')
            job = queue.enqueue(
                process_chat_task,
                args=(message, context),
                job_timeout=120  # 2 minutes timeout
            )

            # Return job ID for async polling
            return jsonify({
                'success': True,
                'task_id': job.id,
                'status': 'queued',
                'message': 'Chat task submitted to RQ queue',
                'async': True
            })
        else:
            # Track chat response time (synchronous fallback)
            chat_start_time = datetime.now()

            # AI engine now handles fallback internally
            response = ai_engine.process_chat_query(message, context)

            response_time = (datetime.now() - chat_start_time).total_seconds()

            # Log chat interaction
            review_session.activity_logger.log_chat_interaction(
                'user_query',
                len(message),
                response_time
            )

        # Add AI response to history
        # Get actual model name with fallback if config module not available
        try:
            from config.model_config import model_config as mc
            actual_model = mc.get_model_config()['model_name']
        except (ImportError, ModuleNotFoundError, KeyError):
            actual_model = os.environ.get('BEDROCK_MODEL_ID', 'claude-3-5-sonnet')

        review_session.chat_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat(),
            'ai_model': actual_model
        })
        
        # Log activity
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'CHAT_INTERACTION',
            'details': f'User query with {ai_model}: {message[:50]}...'
        })
        
        return jsonify({'success': True, 'response': response, 'model_used': actual_model})
        
    except Exception as e:
        import sys
        import traceback
        error_trace = traceback.format_exc()
        print("=" * 80, flush=True)
        print(f"❌ CHAT ERROR OCCURRED", flush=True)
        print(f"   Error: {str(e)}", flush=True)
        print(f"   Error type: {type(e).__name__}", flush=True)
        print(f"   Traceback:", flush=True)
        print(error_trace, flush=True)
        print("=" * 80, flush=True)
        sys.stdout.flush()

        # Return detailed error for debugging
        error_message = f'Chat failed: {str(e)}'

        # Check if it's an AI engine issue
        if 'ai_engine' in str(e).lower() or 'process_chat_query' in str(e).lower():
            error_message = 'AI engine not available. Please try again or check system configuration.'
        elif 'session' in str(e).lower():
            error_message = 'Invalid session. Please upload a document first.'

        return jsonify({
            'success': False,
            'error': error_message,
            'details': str(e) if app.debug else None
        }), 500

@app.route('/delete_document', methods=['POST'])
def delete_document():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        keep_guidelines = data.get('keep_guidelines', True)
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Delete document file but keep guidelines
        if review_session.document_path and os.path.exists(review_session.document_path):
            os.remove(review_session.document_path)
        
        # Reset document-related data but preserve guidelines
        guidelines_path = getattr(review_session, 'guidelines_path', None)
        guidelines_name = getattr(review_session, 'guidelines_name', None)
        guidelines_preference = getattr(review_session, 'guidelines_preference', 'both')
        
        # Clear document data
        review_session.document_name = ""
        review_session.document_path = ""
        review_session.sections = {}
        review_session.section_paragraphs = {}
        review_session.paragraph_indices = {}
        review_session.feedback_data = {}
        review_session.accepted_feedback = defaultdict(list)
        review_session.rejected_feedback = defaultdict(list)
        review_session.user_feedback = defaultdict(list)
        
        # Restore guidelines if keeping them
        if keep_guidelines:
            review_session.guidelines_path = guidelines_path
            review_session.guidelines_name = guidelines_name
            review_session.guidelines_preference = guidelines_preference
        
        # Log activity
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'DOCUMENT_DELETED',
            'details': f'Document deleted, guidelines {"preserved" if keep_guidelines else "also deleted"}'
        })
        
        return jsonify({'success': True, 'guidelines_preserved': keep_guidelines})
        
    except Exception as e:
        return jsonify({'error': f'Delete document failed: {str(e)}'}), 500

@app.route('/submit_tool_feedback', methods=['POST'])
def submit_tool_feedback():
    try:
        feedback_data = request.get_json()
        
        # Save feedback to file for analysis
        feedback_file = 'data/tool_feedback.json'
        os.makedirs('data', exist_ok=True)
        
        existing_feedback = []
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r') as f:
                    existing_feedback = json.load(f)
            except:
                existing_feedback = []
        
        existing_feedback.append(feedback_data)
        
        with open(feedback_file, 'w') as f:
            json.dump(existing_feedback, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Feedback received and will be reviewed'})
        
    except Exception as e:
        return jsonify({'error': f'Submit feedback failed: {str(e)}'}), 500

@app.route('/get_statistics', methods=['GET'])
def get_statistics():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Reset and rebuild statistics from current session
        global stats_manager
        stats_manager = StatisticsManager()
        
        # Update statistics manager with current session data
        for section_name, feedback_items in review_session.feedback_data.items():
            stats_manager.update_feedback_data(section_name, feedback_items)
        
        for section_name, accepted_items in review_session.accepted_feedback.items():
            for item in accepted_items:
                stats_manager.record_acceptance(section_name, item)
        
        for section_name, rejected_items in review_session.rejected_feedback.items():
            for item in rejected_items:
                stats_manager.record_rejection(section_name, item)
        
        for section_name, user_items in review_session.user_feedback.items():
            for item in user_items:
                stats_manager.add_user_feedback(section_name, item)
        
        statistics = stats_manager.get_statistics()
        
        return jsonify({'success': True, 'statistics': statistics})
        
    except Exception as e:
        return jsonify({'error': f'Get statistics failed: {str(e)}'}), 500

@app.route('/get_statistics_breakdown', methods=['GET'])
def get_statistics_breakdown():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        stat_type = request.args.get('stat_type')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Reset and rebuild statistics from current session
        global stats_manager
        stats_manager = StatisticsManager()
        
        # Update statistics manager with current session data
        for section_name, feedback_items in review_session.feedback_data.items():
            stats_manager.update_feedback_data(section_name, feedback_items)
        
        for section_name, accepted_items in review_session.accepted_feedback.items():
            for item in accepted_items:
                stats_manager.record_acceptance(section_name, item)
        
        for section_name, rejected_items in review_session.rejected_feedback.items():
            for item in rejected_items:
                stats_manager.record_rejection(section_name, item)
        
        for section_name, user_items in review_session.user_feedback.items():
            for item in user_items:
                stats_manager.add_user_feedback(section_name, item)
        
        breakdown = stats_manager.get_detailed_breakdown(stat_type)
        breakdown_html = stats_manager.generate_breakdown_html(breakdown, stat_type)
        
        return jsonify({'success': True, 'breakdown_html': breakdown_html})
        
    except Exception as e:
        return jsonify({'error': f'Get breakdown failed: {str(e)}'}), 500

@app.route('/get_patterns', methods=['GET'])
def get_patterns():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Add current session data to pattern analyzer
        all_feedback = []
        for section_name, feedback_items in review_session.feedback_data.items():
            all_feedback.extend(feedback_items)
        
        if all_feedback:
            review_session.pattern_analyzer.add_document_feedback(review_session.document_name, all_feedback)
        
        # Get patterns
        patterns = {
            'recurring_patterns': review_session.pattern_analyzer.find_recurring_patterns(),
            'category_trends': review_session.pattern_analyzer.get_category_trends(),
            'risk_patterns': review_session.pattern_analyzer.get_risk_patterns(),
            'pattern_report_html': review_session.pattern_analyzer.get_pattern_report_html()
        }
        
        return jsonify({'success': True, 'patterns': patterns})
        
    except Exception as e:
        return jsonify({'error': f'Get patterns failed: {str(e)}'}), 500

def analyze_feedback_patterns(review_session):
    """Analyze patterns in feedback data"""
    patterns = {
        'recurring_patterns': [],
        'risk_distribution': {},
        'category_trends': {},
        'section_analysis': {}
    }
    
    # Collect all feedback for analysis
    all_feedback = []
    for section_name, feedback_items in review_session.feedback_data.items():
        for item in feedback_items:
            item_copy = item.copy()
            item_copy['section'] = section_name
            all_feedback.append(item_copy)
    
    if not all_feedback:
        return patterns
    
    # Analyze risk distribution
    risk_counts = {'High': 0, 'Medium': 0, 'Low': 0}
    category_counts = {}
    type_counts = {}
    
    for item in all_feedback:
        risk_level = item.get('risk_level', 'Low')
        category = item.get('category', 'Unknown')
        item_type = item.get('type', 'unknown')
        
        risk_counts[risk_level] += 1
        category_counts[category] = category_counts.get(category, 0) + 1
        type_counts[item_type] = type_counts.get(item_type, 0) + 1
    
    patterns['risk_distribution'] = risk_counts
    patterns['category_trends'] = category_counts
    
    # Find recurring patterns (categories appearing in multiple sections)
    category_sections = {}
    for item in all_feedback:
        category = item.get('category', 'Unknown')
        section = item.get('section', 'Unknown')
        
        if category not in category_sections:
            category_sections[category] = set()
        category_sections[category].add(section)
    
    # Identify patterns that appear in multiple sections
    for category, sections in category_sections.items():
        if len(sections) > 1:  # Appears in multiple sections
            # Get examples from different sections
            examples = []
            for section in list(sections)[:3]:  # Max 3 examples
                section_items = [item for item in all_feedback 
                               if item.get('category') == category and item.get('section') == section]
                if section_items:
                    example_item = section_items[0]
                    examples.append({
                        'section': section,
                        'risk_level': example_item.get('risk_level', 'Low'),
                        'description': example_item.get('description', '')[:100] + '...' if len(example_item.get('description', '')) > 100 else example_item.get('description', '')
                    })
            
            patterns['recurring_patterns'].append({
                'pattern': f'Issues related to {category}',
                'category': category.lower(),
                'occurrence_count': len(sections),
                'sections_affected': list(sections),
                'examples': examples
            })
    
    # Section-level analysis
    for section_name in review_session.sections:
        section_feedback = [item for item in all_feedback if item.get('section') == section_name]
        if section_feedback:
            patterns['section_analysis'][section_name] = {
                'total_items': len(section_feedback),
                'high_risk_count': len([item for item in section_feedback if item.get('risk_level') == 'High']),
                'most_common_category': max(set([item.get('category', 'Unknown') for item in section_feedback]), 
                                          key=[item.get('category', 'Unknown') for item in section_feedback].count),
                'accepted_count': len(review_session.accepted_feedback.get(section_name, [])),
                'rejected_count': len(review_session.rejected_feedback.get(section_name, []))
            }
    
    return patterns

@app.route('/get_activity_logs', methods=['GET'])
def get_activity_logs():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        format_type = request.args.get('format', 'json')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        if format_type == 'html':
            # Generate comprehensive HTML logs including all activities
            activity_summary = review_session.activity_logger.get_activity_summary()
            failed_activities = review_session.activity_logger.get_failed_activities()
            recent_activities = review_session.activity_logger.get_recent_activities(20)
            
            logs_html = f"""
            <div class="logs-container">
                <div class="logs-header">
                    <h3>📋 Complete Activity Log</h3>
                    <div class="logs-summary">
                        <span class="stat">Total: {activity_summary['total_activities']}</span>
                        <span class="stat success">✅ Success: {activity_summary['success_count']}</span>
                        <span class="stat failed">❌ Failed: {activity_summary['failed_count']}</span>
                        <span class="stat rate">Success Rate: {activity_summary['success_rate']}%</span>
                    </div>
                </div>
                
                <div class="logs-sections">
                    <div class="logs-section">
                        <h4>🔥 Failed Activities</h4>
                        <div class="failed-activities">
            """
            
            if failed_activities:
                for activity in failed_activities:
                    logs_html += f"""
                    <div class="activity-item failed">
                        <div class="activity-header">
                            <span class="action">{activity['action']}</span>
                            <span class="timestamp">{activity['timestamp']}</span>
                        </div>
                        <div class="activity-error">❌ {activity.get('error', 'Unknown error')}</div>
                        {f'<div class="activity-details">{activity["details"]}</div>' if activity.get('details') else ''}
                    </div>
                    """
            else:
                logs_html += '<div class="no-failures">✅ No failed activities</div>'
            
            logs_html += """
                        </div>
                    </div>
                    
                    <div class="logs-section">
                        <h4>📝 Recent Activities</h4>
                        <div class="recent-activities">
            """
            
            for activity in recent_activities:
                status_icon = {
                    'success': '✅',
                    'failed': '❌', 
                    'in_progress': '⏳',
                    'warning': '⚠️'
                }.get(activity['status'], '📝')
                
                logs_html += f"""
                <div class="activity-item {activity['status']}">
                    <div class="activity-header">
                        <span class="status-icon">{status_icon}</span>
                        <span class="action">{activity['action']}</span>
                        <span class="timestamp">{activity['timestamp']}</span>
                    </div>
                    {f'<div class="activity-details">{activity["details"]}</div>' if activity.get('details') else ''}
                    {f'<div class="activity-error">{activity["error"]}</div>' if activity.get('error') else ''}
                </div>
                """
            
            logs_html += """
                        </div>
                    </div>
                    
                    <div class="logs-section">
                        <h4>📊 Activity Breakdown</h4>
                        <div class="activity-breakdown">
            """
            
            for action, count in activity_summary['action_breakdown'].items():
                logs_html += f'<div class="breakdown-item"><span class="action">{action.title()}</span><span class="count">{count}</span></div>'
            
            logs_html += """
                        </div>
                    </div>
                </div>
                
                <div class="logs-footer">
                    <div class="session-info">
                        <span>Session Duration: {session_duration} minutes</span>
                        <span>Last Activity: {last_activity}</span>
                    </div>
                </div>
            </div>
            
            <style>
            .logs-container {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
            .logs-header {{ margin-bottom: 20px; }}
            .logs-summary {{ display: flex; gap: 15px; margin-top: 10px; }}
            .stat {{ padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: 500; }}
            .stat.success {{ background: #d4edda; color: #155724; }}
            .stat.failed {{ background: #f8d7da; color: #721c24; }}
            .stat.rate {{ background: #d1ecf1; color: #0c5460; }}
            .logs-section {{ margin-bottom: 25px; }}
            .logs-section h4 {{ margin-bottom: 10px; color: #333; }}
            .activity-item {{ padding: 12px; margin-bottom: 8px; border-radius: 6px; border-left: 4px solid #ddd; }}
            .activity-item.success {{ border-left-color: #28a745; background: #f8fff9; }}
            .activity-item.failed {{ border-left-color: #dc3545; background: #fff8f8; }}
            .activity-item.warning {{ border-left-color: #ffc107; background: #fffdf5; }}
            .activity-item.in_progress {{ border-left-color: #17a2b8; background: #f8fdff; }}
            .activity-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }}
            .action {{ font-weight: 600; color: #333; }}
            .timestamp {{ font-size: 11px; color: #666; }}
            .activity-details {{ font-size: 13px; color: #555; margin-top: 5px; }}
            .activity-error {{ font-size: 13px; color: #dc3545; margin-top: 5px; font-weight: 500; }}
            .no-failures {{ text-align: center; padding: 20px; color: #28a745; font-weight: 500; }}
            .breakdown-item {{ display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee; }}
            .logs-footer {{ margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee; }}
            .session-info {{ display: flex; gap: 20px; font-size: 12px; color: #666; }}
            </style>
            """.format(
                session_duration=activity_summary['session_duration'],
                last_activity=activity_summary['last_activity'] or 'None'
            )
            
            return jsonify({'success': True, 'logs_html': logs_html})
        else:
            # Return JSON format with comprehensive activity data
            activities = review_session.activity_logger.activities
            activity_summary = review_session.activity_logger.get_activity_summary()
            failed_activities = review_session.activity_logger.get_failed_activities()
            
            return jsonify({
                'success': True,
                'logs': activities,
                'summary': activity_summary,
                'failed_activities': failed_activities,
                'audit_logs': review_session.audit_logger.get_session_logs(),
                'performance_metrics': review_session.audit_logger.get_performance_metrics(),
                'activity_timeline': review_session.audit_logger.get_activity_timeline()
            })
        
    except Exception as e:
        return jsonify({'error': f'Get logs failed: {str(e)}'}), 500

@app.route('/get_learning_status', methods=['GET'])
def get_learning_status():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        format_type = request.args.get('format', 'json')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        if format_type == 'html':
            learning_html = review_session.learning_system.generate_learning_report_html()
            return jsonify({'success': True, 'learning_html': learning_html})
        else:
            learning_stats = review_session.learning_system.get_learning_statistics()
            
            # Get recommended feedback for current sections
            recommendations = {}
            for section_name in review_session.sections:
                section_content = review_session.sections[section_name]
                recs = review_session.learning_system.get_recommended_feedback(section_name, section_content)
                if recs:
                    recommendations[section_name] = recs
            
            return jsonify({
                'success': True, 
                'learning_status': learning_stats,
                'recommendations': recommendations
            })
        
    except Exception as e:
        return jsonify({'error': f'Get learning status failed: {str(e)}'}), 500

def generate_learning_insights(review_session):
    """Generate insights about AI learning patterns"""
    insights = []
    
    # Analyze acceptance patterns
    accepted_categories = {}
    rejected_categories = {}
    
    for section_feedback in review_session.accepted_feedback.values():
        for item in section_feedback:
            category = item.get('category', 'Unknown')
            accepted_categories[category] = accepted_categories.get(category, 0) + 1
    
    for section_feedback in review_session.rejected_feedback.values():
        for item in section_feedback:
            category = item.get('category', 'Unknown')
            rejected_categories[category] = rejected_categories.get(category, 0) + 1
    
    # Find most accepted category
    if accepted_categories:
        most_accepted = max(accepted_categories, key=accepted_categories.get)
        insights.append(f"You most often accept feedback about '{most_accepted}' ({accepted_categories[most_accepted]} times)")
    
    # Find most rejected category
    if rejected_categories:
        most_rejected = max(rejected_categories, key=rejected_categories.get)
        insights.append(f"You most often reject feedback about '{most_rejected}' ({rejected_categories[most_rejected]} times)")
    
    # User feedback patterns
    user_categories = {}
    for section_feedback in review_session.user_feedback.values():
        for item in section_feedback:
            category = item.get('category', 'Unknown')
            user_categories[category] = user_categories.get(category, 0) + 1
    
    if user_categories:
        most_user_category = max(user_categories, key=user_categories.get)
        insights.append(f"You add most custom feedback about '{most_user_category}' ({user_categories[most_user_category]} times)")
    
    return insights

def generate_improvement_suggestions(acceptance_rate, user_engagement):
    """Generate suggestions for improving AI performance"""
    suggestions = []
    
    if acceptance_rate < 50:
        suggestions.append("Consider providing more specific feedback to help AI learn your preferences")
    elif acceptance_rate > 80:
        suggestions.append("Great! AI is learning your preferences well")
    
    if user_engagement < 20:
        suggestions.append("Try adding more custom feedback to help AI understand your specific needs")
    elif user_engagement > 50:
        suggestions.append("Excellent engagement! Your custom feedback is helping AI improve")
    
    suggestions.append("Continue reviewing documents to improve AI accuracy")
    suggestions.append("Use the chat feature to clarify feedback when needed")
    
    return suggestions

# ✅ REMOVED DUPLICATE: get_section_content already defined at line 321

@app.route('/complete_review', methods=['POST'])
def complete_review():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        export_to_s3 = data.get('export_to_s3', False)
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Prepare comments data
        comments_data = []

        # DEBUG: Log accepted feedback collection
        print(f"\n{'='*60}")
        print(f"🔍 DEBUGGING COMMENT INSERTION")
        print(f"{'='*60}")
        print(f"Total sections in document: {len(review_session.sections)}")
        print(f"Total accepted_feedback sections: {len(review_session.accepted_feedback)}")

        for section_name, accepted_items in review_session.accepted_feedback.items():
            print(f"\n📍 Section: {section_name}")
            print(f"   Accepted items: {len(accepted_items)}")
            print(f"   Has paragraph_indices: {section_name in review_session.paragraph_indices}")

            if section_name in review_session.paragraph_indices:
                para_indices = review_session.paragraph_indices[section_name]
                print(f"   Paragraph indices: {para_indices}")

                for item in accepted_items:
                    comment_text = f"[{item.get('type', 'feedback').upper()} - {item.get('risk_level', 'Low')} Risk]\n"
                    comment_text += f"{item.get('description', '')}\n"

                    if item.get('suggestion'):
                        comment_text += f"\nSuggestion: {item['suggestion']}\n"

                    if item.get('questions'):
                        comment_text += "\nKey Questions:\n"
                        for i, q in enumerate(item['questions'], 1):
                            comment_text += f"{i}. {q}\n"

                    if item.get('hawkeye_refs'):
                        refs = [f"#{r}" for r in item['hawkeye_refs']]
                        comment_text += f"\nHawkeye References: {', '.join(refs)}"

                    comment_item = {
                        'section': section_name,
                        'paragraph_index': para_indices[0] if para_indices else 0,
                        'comment': comment_text,
                        'type': item.get('type', 'feedback'),
                        'risk_level': item.get('risk_level', 'Low'),
                        'author': 'User Feedback' if item.get('user_created') else 'AI Feedback'
                    }
                    comments_data.append(comment_item)
                    print(f"   ✅ Added comment: {item.get('type')} - {comment_text[:50]}...")
            else:
                print(f"   ⚠️ No paragraph_indices for section: {section_name}")

        print(f"\n{'='*60}")
        print(f"📊 FINAL COMMENT DATA:")
        print(f"Total comments to add: {len(comments_data)}")
        print(f"{'='*60}\n")
        
        # Create reviewed document with tracking
        output_filename = f"reviewed_{review_session.document_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        
        review_session.activity_logger.start_operation('document_generation', {
            'comments_count': len(comments_data),
            'output_filename': output_filename
        })
        output_path = doc_processor.create_document_with_comments(
            review_session.document_path,
            comments_data,
            output_filename
        )
        
        if output_path:
            file_size = os.path.getsize(output_path)
            review_session.activity_logger.complete_operation(success=True, details={
                'output_file': output_filename,
                'file_size_bytes': file_size
            })
            
            # Log completion
            review_session.activity_logger.log_session_event('review_completed', {
                'comments_added': len(comments_data),
                'output_file': output_filename,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            })
            
            review_session.activity_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'REVIEW_COMPLETED',
                'details': f'Review completed with {len(comments_data)} comments added'
            })

            # Store output filename in session for retrieval
            review_session.output_filename = output_filename

            response_data = {
                'success': True,
                'output_file': output_filename,
                'comments_count': len(comments_data)
            }
            
            # Export to S3 if requested
            if export_to_s3:
                try:
                    review_session.activity_logger.start_operation('s3_export', {
                        'before_document': review_session.document_path,
                        'after_document': output_path
                    })
                    
                    export_result = s3_export_manager.export_complete_review_to_s3(
                        review_session,
                        review_session.document_path,  # before document
                        output_path  # after document
                    )
                    response_data['s3_export'] = export_result
                    
                    # Log S3 export with detailed tracking
                    if export_result.get('success'):
                        review_session.activity_logger.complete_operation(success=True, details={
                            'location': export_result.get('location'),
                            'files_uploaded': export_result.get('total_files', 0),
                            'folder_name': export_result.get('folder_name')
                        })
                        
                        review_session.activity_logger.log_s3_operation(
                            'export_complete_review',
                            success=True,
                            details={
                                'location': export_result.get('location'),
                                'files_count': export_result.get('total_files', 0),
                                'bucket': export_result.get('bucket'),
                                'folder_name': export_result.get('folder_name')
                            }
                        )
                        
                        review_session.activity_log.append({
                            'timestamp': datetime.now().isoformat(),
                            'action': 'S3_EXPORT_COMPLETED',
                            'details': f'Complete review exported to {export_result.get("location", "S3")}'
                        })
                    else:
                        review_session.activity_logger.complete_operation(success=False, error=export_result.get('error'))
                        
                        review_session.activity_logger.log_s3_operation(
                            'export_complete_review',
                            success=False,
                            error=export_result.get('error')
                        )
                        
                        review_session.activity_log.append({
                            'timestamp': datetime.now().isoformat(),
                            'action': 'S3_EXPORT_FAILED',
                            'details': f'S3 export failed: {export_result.get("error", "Unknown error")}'
                        })
                        
                except Exception as s3_error:
                    review_session.activity_logger.complete_operation(success=False, error=str(s3_error))
                    review_session.activity_logger.log_s3_operation(
                        'export_complete_review',
                        success=False,
                        error=str(s3_error)
                    )
                    
                    print(f"S3 export error: {str(s3_error)}")
                    response_data['s3_export'] = {
                        'success': False,
                        'error': str(s3_error),
                        'location': 'failed'
                    }

            # ✅ NEW: Save completion to database
            try:
                stats = stats_manager.get_statistics()
                s3_loc = export_result.get('location') if export_to_s3 and export_result.get('success') else None

                db_manager.complete_review(
                    session_id=session_id,
                    output_filename=output_filename,
                    stats=stats,
                    s3_location=s3_loc
                )
                print(f"✅ Database: Review completed and saved for {session_id}")
            except Exception as db_error:
                print(f"⚠️ Database completion error: {db_error}")

            return jsonify(response_data)
        else:
            review_session.activity_logger.complete_operation(success=False, error='Failed to create reviewed document')
            return jsonify({'error': 'Failed to create reviewed document'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Complete review failed: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/get_accepted_feedback_count', methods=['GET'])
def get_accepted_feedback_count():
    """Get count of accepted feedback items for a session - used to warn user before completing review"""
    try:
        session_id = request.args.get('session_id')

        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400

        review_session = get_session(session_id)

        # Count all accepted feedback across all sections
        accepted_count = sum(
            len(items)
            for items in review_session.accepted_feedback.values()
        )

        # Count custom feedback (also included in document)
        custom_count = sum(
            len(items)
            for items in review_session.user_feedback.values()
        )

        # Count total feedback items generated by AI
        total_generated = sum(
            len(items)
            for items in review_session.feedback_data.values()
        )

        # Count rejected feedback
        rejected_count = sum(
            len(items)
            for items in review_session.rejected_feedback.values()
        )

        return jsonify({
            'success': True,
            'accepted_count': accepted_count,
            'custom_count': custom_count,
            'total_generated': total_generated,
            'rejected_count': rejected_count,
            'pending_count': total_generated - accepted_count - rejected_count,
            'will_be_in_document': accepted_count  # This is what will actually be in the document
        })

    except Exception as e:
        return jsonify({'error': f'Count failed: {str(e)}'}), 500

@app.route('/get_latest_document', methods=['GET'])
def get_latest_document():
    """Get the latest reviewed document filename for a session"""
    try:
        session_id = request.args.get('session_id')

        if not session_id or not session_exists(session_id):
            return jsonify({'success': False, 'error': 'Invalid session'}), 400

        review_session = get_session(session_id)

        # Look for the most recent reviewed document
        # Check if finalDocumentData or similar exists
        if hasattr(review_session, 'output_filename') and review_session.output_filename:
            return jsonify({
                'success': True,
                'filename': review_session.output_filename
            })

        # Try to find any reviewed document for this session
        import glob
        pattern = f"reviewed_{review_session.document_name}_*.docx"
        matching_files = glob.glob(pattern)

        if matching_files:
            # Get the most recent file
            latest_file = max(matching_files, key=os.path.getmtime)
            filename = os.path.basename(latest_file)
            return jsonify({
                'success': True,
                'filename': filename
            })

        return jsonify({
            'success': False,
            'error': 'No reviewed document found for this session'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/reset_session', methods=['POST'])
def reset_session():
    try:
        session_id = session.get('session_id')
        
        if session_id and session_exists(session_id):
            # Clean up old session
            delete_session(session_id)
        
        # Clear session
        session.clear()
        
        # Reset statistics manager
        global stats_manager
        stats_manager = StatisticsManager()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Reset failed: {str(e)}'}), 500

@app.route('/revert_all_feedback', methods=['POST'])
def revert_all_feedback():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Clear all feedback
        review_session.accepted_feedback = defaultdict(list)
        review_session.rejected_feedback = defaultdict(list)
        
        # Reset statistics
        global stats_manager
        stats_manager = StatisticsManager()
        
        # Log activity
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'ALL_FEEDBACK_REVERTED',
            'details': 'User reverted all feedback decisions'
        })
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Revert failed: {str(e)}'}), 500

@app.route('/get_dashboard_data', methods=['GET'])
def get_dashboard_data():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Calculate dashboard metrics
        total_accepted = sum(len(items) for items in review_session.accepted_feedback.values())
        total_rejected = sum(len(items) for items in review_session.rejected_feedback.values())
        total_user = sum(len(items) for items in review_session.user_feedback.values())
        
        dashboard_data = {
            'totalDocuments': 1,  # Current session
            'acceptedFeedback': total_accepted,
            'rejectedFeedback': total_rejected,
            'userFeedback': total_user,
            'totalFeedback': sum(len(items) for items in review_session.feedback_data.values()),
            'sectionsAnalyzed': len(review_session.sections),
            'recentActivity': review_session.activity_log[-10:] if review_session.activity_log else []
        }
        
        return jsonify({'success': True, 'dashboard': dashboard_data})
        
    except Exception as e:
        return jsonify({'error': f'Dashboard data failed: {str(e)}'}), 500

@app.route('/download_guidelines', methods=['GET'])
def download_guidelines():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        if hasattr(review_session, 'guidelines_path') and review_session.guidelines_path:
            return send_file(review_session.guidelines_path, as_attachment=True)
        else:
            # Create default guidelines document
            guidelines_content = """
            HAWKEYE INVESTIGATION FRAMEWORK - 20 POINT CHECKLIST
            
            1. Initial Assessment - Evaluate customer experience impact
            2. Investigation Process - Challenge SOPs and enforcement decisions
            3. Seller Classification - Identify good/bad/confused actors
            4. Enforcement Decision-Making - Proper violation assessment
            5. Additional Verification - High-risk case handling
            6. Multiple Appeals Handling - Pattern recognition
            7. Account Hijacking Prevention - Security measures
            8. Funds Management - Financial impact assessment
            9. REs-Q Outreach Process - Communication protocols
            10. Sentiment Analysis - Escalation and health safety
            11. Root Cause Analysis - Process gaps identification
            12. Preventative Actions - Solution implementation
            13. Documentation and Reporting - Proper record keeping
            14. Cross-Team Collaboration - Stakeholder engagement
            15. Quality Control - Audit and review processes
            16. Continuous Improvement - Training and updates
            17. Communication Standards - Clear messaging
            18. Performance Metrics - Tracking and measurement
            19. Legal and Compliance - Regulatory adherence
            20. New Service Launch Considerations - Pilot and rollback
            """
            
            # Create temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(guidelines_content)
                temp_path = f.name
            
            return send_file(temp_path, as_attachment=True, download_name='Hawkeye_Guidelines.txt')
        
    except Exception as e:
        return jsonify({'error': f'Download guidelines failed: {str(e)}'}), 500

@app.route('/get_user_feedback', methods=['GET'])
def get_user_feedback():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Collect all user feedback across sections
        all_user_feedback = []
        for section_name, feedback_list in review_session.user_feedback.items():
            for feedback in feedback_list:
                feedback_copy = feedback.copy()
                feedback_copy['section'] = section_name
                all_user_feedback.append(feedback_copy)
        
        # Sort by timestamp (newest first)
        all_user_feedback.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({
            'success': True, 
            'user_feedback': all_user_feedback,
            'total_count': len(all_user_feedback),
            'sections_with_feedback': len([s for s in review_session.user_feedback.keys() if review_session.user_feedback[s]])
        })
        
    except Exception as e:
        return jsonify({'error': f'Get user feedback failed: {str(e)}'}), 500

@app.route('/update_user_feedback', methods=['POST'])
def update_user_feedback():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        feedback_id = data.get('feedback_id')
        updated_data = data.get('updated_data')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Find and update the feedback item
        updated = False
        for section_name, feedback_list in review_session.user_feedback.items():
            for i, feedback in enumerate(feedback_list):
                if feedback.get('id') == feedback_id:
                    # Update the feedback
                    feedback.update(updated_data)
                    feedback['edited'] = True
                    feedback['edited_at'] = datetime.now().isoformat()
                    updated = True
                    
                    # Also update in accepted feedback if it exists there
                    for j, accepted in enumerate(review_session.accepted_feedback[section_name]):
                        if accepted.get('id') == feedback_id:
                            review_session.accepted_feedback[section_name][j].update(updated_data)
                            break
                    
                    # Log activity
                    review_session.activity_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'action': 'USER_FEEDBACK_UPDATED',
                        'details': f'Updated user feedback in {section_name}: {feedback_id}'
                    })
                    
                    break
            if updated:
                break
        
        if updated:
            return jsonify({'success': True, 'message': 'Feedback updated successfully'})
        else:
            return jsonify({'error': 'Feedback item not found'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Update user feedback failed: {str(e)}'}), 500

@app.route('/delete_user_feedback', methods=['POST'])
def delete_user_feedback():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        feedback_id = data.get('feedback_id')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Find and delete the feedback item
        deleted = False
        for section_name, feedback_list in review_session.user_feedback.items():
            for i, feedback in enumerate(feedback_list):
                if feedback.get('id') == feedback_id:
                    # Remove from user feedback
                    removed_feedback = feedback_list.pop(i)
                    deleted = True
                    
                    # Also remove from accepted feedback if it exists there
                    for j, accepted in enumerate(review_session.accepted_feedback[section_name]):
                        if accepted.get('id') == feedback_id:
                            review_session.accepted_feedback[section_name].pop(j)
                            break
                    
                    # Log activity
                    review_session.activity_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'action': 'USER_FEEDBACK_DELETED',
                        'details': f'Deleted user feedback from {section_name}: {removed_feedback.get("description", "")[:50]}...'
                    })
                    
                    break
            if deleted:
                break
        
        if deleted:
            return jsonify({'success': True, 'message': 'Feedback deleted successfully'})
        else:
            return jsonify({'error': 'Feedback item not found'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Delete user feedback failed: {str(e)}'}), 500

@app.route('/export_user_feedback', methods=['GET'])
def export_user_feedback():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        format_type = request.args.get('format', 'json')  # json, csv, txt
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Collect all user feedback
        all_user_feedback = []
        for section_name, feedback_list in review_session.user_feedback.items():
            for feedback in feedback_list:
                feedback_copy = feedback.copy()
                feedback_copy['section'] = section_name
                all_user_feedback.append(feedback_copy)
        
        if format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            headers = ['Timestamp', 'Section', 'Type', 'Category', 'Description', 'AI Reference', 'Edited']
            writer.writerow(headers)
            
            # Write data
            for feedback in all_user_feedback:
                row = [
                    feedback.get('timestamp', ''),
                    feedback.get('section', ''),
                    feedback.get('type', ''),
                    feedback.get('category', ''),
                    feedback.get('description', ''),
                    feedback.get('ai_reference', ''),
                    'Yes' if feedback.get('edited') else 'No'
                ]
                writer.writerow(row)
            
            output.seek(0)
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=user_feedback_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        
        elif format_type == 'txt':
            output = f"User Feedback Export\n"
            output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"Session ID: {session_id}\n"
            output += f"Total Feedback Items: {len(all_user_feedback)}\n"
            output += "=" * 50 + "\n\n"
            
            for i, feedback in enumerate(all_user_feedback, 1):
                output += f"#{i} - {feedback.get('type', '').upper()} FEEDBACK\n"
                output += f"Section: {feedback.get('section', '')}\n"
                output += f"Category: {feedback.get('category', '')}\n"
                output += f"Timestamp: {feedback.get('timestamp', '')}\n"
                if feedback.get('ai_reference'):
                    output += f"Related to AI: {feedback.get('ai_reference', '')}\n"
                output += f"Description: {feedback.get('description', '')}\n"
                if feedback.get('edited'):
                    output += f"Edited: {feedback.get('edited_at', '')}\n"
                output += "-" * 30 + "\n\n"
            
            return output, 200, {
                'Content-Type': 'text/plain',
                'Content-Disposition': f'attachment; filename=user_feedback_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            }
        
        else:  # JSON format
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'session_id': session_id,
                'total_feedback': len(all_user_feedback),
                'sections_with_feedback': len(set(f.get('section') for f in all_user_feedback)),
                'feedback_items': all_user_feedback
            }
            
            return jsonify(export_data), 200, {
                'Content-Disposition': f'attachment; filename=user_feedback_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        
    except Exception as e:
        return jsonify({'error': f'Export user feedback failed: {str(e)}'}), 500

@app.route('/download_statistics', methods=['GET'])
def download_statistics():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        format_type = request.args.get('format', 'json')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Get comprehensive statistics
        stats = stats_manager.get_statistics()
        
        # Add session-specific data
        stats_data = {
            'session_id': session_id,
            'document_name': review_session.document_name,
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'sections_analyzed': len(review_session.sections),
            'total_sections': len(review_session.sections),
            'accepted_feedback_by_section': {k: len(v) for k, v in review_session.accepted_feedback.items()},
            'rejected_feedback_by_section': {k: len(v) for k, v in review_session.rejected_feedback.items()},
            'user_feedback_by_section': {k: len(v) for k, v in review_session.user_feedback.items()},
            'chat_interactions': len(review_session.chat_history),
            'activity_log_count': len(review_session.activity_log)
        }
        
        if format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Metric', 'Value', 'Percentage'])
            
            # Write statistics
            total = stats.get('total_feedback', 1)
            writer.writerow(['Total Feedback', stats.get('total_feedback', 0), '100%'])
            writer.writerow(['High Risk', stats.get('high_risk', 0), f"{(stats.get('high_risk', 0)/total*100):.1f}%"])
            writer.writerow(['Medium Risk', stats.get('medium_risk', 0), f"{(stats.get('medium_risk', 0)/total*100):.1f}%"])
            writer.writerow(['Low Risk', stats.get('low_risk', 0), f"{(stats.get('low_risk', 0)/total*100):.1f}%"])
            writer.writerow(['Accepted', stats.get('accepted', 0), f"{(stats.get('accepted', 0)/total*100):.1f}%"])
            writer.writerow(['Rejected', stats.get('rejected', 0), f"{(stats.get('rejected', 0)/total*100):.1f}%"])
            writer.writerow(['User Added', stats.get('user_added', 0), f"{(stats.get('user_added', 0)/total*100):.1f}%"])
            
            output.seek(0)
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=statistics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        
        elif format_type == 'txt':
            output = f"AI-Prism Statistics Report\n"
            output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"Document: {review_session.document_name}\n"
            output += f"Session ID: {session_id}\n"
            output += "=" * 50 + "\n\n"
            
            output += "SUMMARY STATISTICS:\n"
            output += f"Total Feedback Items: {stats.get('total_feedback', 0)}\n"
            output += f"High Risk Items: {stats.get('high_risk', 0)}\n"
            output += f"Medium Risk Items: {stats.get('medium_risk', 0)}\n"
            output += f"Low Risk Items: {stats.get('low_risk', 0)}\n"
            output += f"Accepted Items: {stats.get('accepted', 0)}\n"
            output += f"Rejected Items: {stats.get('rejected', 0)}\n"
            output += f"User Added Items: {stats.get('user_added', 0)}\n"
            output += f"Sections Analyzed: {len(review_session.sections)}\n"
            output += f"Chat Interactions: {len(review_session.chat_history)}\n"
            
            return output, 200, {
                'Content-Type': 'text/plain',
                'Content-Disposition': f'attachment; filename=statistics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            }
        
        else:  # JSON format
            return jsonify(stats_data), 200, {
                'Content-Disposition': f'attachment; filename=statistics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        
    except Exception as e:
        return jsonify({'error': f'Download statistics failed: {str(e)}'}), 500

@app.route('/export_to_s3', methods=['POST'])
def export_to_s3():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Create the reviewed document first if not exists
        comments_data = []
        for section_name, accepted_items in review_session.accepted_feedback.items():
            if section_name in review_session.paragraph_indices:
                para_indices = review_session.paragraph_indices[section_name]
                
                for item in accepted_items:
                    comment_text = f"[{item.get('type', 'feedback').upper()} - {item.get('risk_level', 'Low')} Risk]\n"
                    comment_text += f"{item.get('description', '')}\n"
                    
                    if item.get('suggestion'):
                        comment_text += f"\nSuggestion: {item['suggestion']}\n"
                    
                    if item.get('questions'):
                        comment_text += "\nKey Questions:\n"
                        for i, q in enumerate(item['questions'], 1):
                            comment_text += f"{i}. {q}\n"
                    
                    if item.get('hawkeye_refs'):
                        refs = [f"#{r}" for r in item['hawkeye_refs']]
                        comment_text += f"\nHawkeye References: {', '.join(refs)}"
                    
                    comments_data.append({
                        'section': section_name,
                        'paragraph_index': para_indices[0] if para_indices else 0,
                        'comment': comment_text,
                        'type': item.get('type', 'feedback'),
                        'risk_level': item.get('risk_level', 'Low'),
                        'author': 'User Feedback' if item.get('user_created') else 'AI Feedback'
                    })
        
        # Create reviewed document
        output_filename = f"reviewed_{review_session.document_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        output_path = doc_processor.create_document_with_comments(
            review_session.document_path,
            comments_data,
            output_filename
        )
        
        if not output_path:
            return jsonify({'error': 'Failed to create reviewed document'}), 500
        
        # Export to S3 with comprehensive tracking
        review_session.activity_logger.start_operation('s3_manual_export', {
            'before_document': review_session.document_path,
            'after_document': output_path,
            'comments_count': len(comments_data)
        })
        
        export_result = s3_export_manager.export_complete_review_to_s3(
            review_session,
            review_session.document_path,  # before document
            output_path  # after document
        )
        
        # Log S3 export attempt with detailed tracking
        if export_result.get('success'):
            review_session.activity_logger.complete_operation(success=True, details={
                'location': export_result.get('location'),
                'files_uploaded': export_result.get('total_files', 0),
                'folder_name': export_result.get('folder_name'),
                'bucket': export_result.get('bucket')
            })
            
            review_session.activity_logger.log_export_operation(
                'manual_s3_export',
                file_count=export_result.get('total_files', 0),
                location=export_result.get('location'),
                success=True
            )
            
            review_session.activity_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'S3_EXPORT_COMPLETED',
                'details': f'Complete review exported to {export_result.get("location", "S3")} - Folder: {export_result.get("folder_name", "Unknown")}'
            })
        else:
            review_session.activity_logger.complete_operation(success=False, error=export_result.get('error'))
            
            review_session.activity_logger.log_export_operation(
                'manual_s3_export',
                location='failed',
                success=False,
                error=export_result.get('error')
            )
            
            review_session.activity_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'S3_EXPORT_FAILED',
                'details': f'S3 export failed: {export_result.get("error", "Unknown error")}'
            })
        
        return jsonify({
            'success': True,
            'export_result': export_result,
            'output_file': output_filename,
            'comments_count': len(comments_data)
        })
        
    except Exception as e:
        return jsonify({'error': f'S3 export failed: {str(e)}'}), 500

@app.route('/test_s3_connection', methods=['GET'])
def test_s3_connection():
    """Test S3 connectivity and return detailed status"""
    try:
        session_id = request.args.get('session_id') or session.get('session_id')

        # Test S3 connection
        connection_status = s3_export_manager.test_s3_connection()

        # Add detailed configuration information
        detailed_status = {
            **connection_status,
            'region': os.environ.get('S3_REGION', 'us-east-1'),
            'connection_type': 'AWS Bedrock SDK (boto3)',
            'base_path': s3_export_manager.base_path,
            'full_path': f"s3://{connection_status.get('bucket_name', 'unknown')}/{s3_export_manager.base_path}",
            'credentials_source': 'AWS Profile (admin-abhsatsa)' if os.environ.get('AWS_PROFILE') else 'Environment Variables',
            'service': 'Amazon S3',
            'sdk_version': 'boto3',
            'access_permissions': 'Read/Write' if connection_status.get('bucket_accessible') else 'None'
        }

        # Log the test if we have a session
        if session_id and session_exists(session_id):
            review_session = get_session(session_id)
            review_session.activity_logger.log_s3_operation(
                'connection_test',
                success=connection_status.get('connected', False) and connection_status.get('bucket_accessible', False),
                details={
                    'bucket_name': connection_status.get('bucket_name'),
                    'connected': connection_status.get('connected', False),
                    'bucket_accessible': connection_status.get('bucket_accessible', False)
                },
                error=connection_status.get('error')
            )

        return jsonify({
            'success': True,
            's3_status': detailed_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        # Log the failed test if we have a session
        if session_id and session_exists(session_id):
            review_session = get_session(session_id)
            review_session.activity_logger.log_s3_operation(
                'connection_test',
                success=False,
                error=str(e)
            )
        
        return jsonify({
            'success': False,
            'error': str(e),
            's3_status': {
                'connected': False,
                'error': f'Test failed: {str(e)}'
            }
        }), 500

@app.route('/test_claude_connection', methods=['GET'])
def test_claude_connection():
    """Test Claude AI connectivity and return detailed status"""
    try:
        session_id = request.args.get('session_id') or session.get('session_id')

        # Test Claude connection directly (synchronous)
        print(f"🔍 Testing Claude connection directly...", flush=True)
        test_response = ai_engine.test_connection()

        # Get model configuration for additional details (with fallback)
        try:
            from config.model_config import model_config
            config = model_config.get_model_config()
        except (ImportError, ModuleNotFoundError, AttributeError, NameError) as e:
            # Fallback configuration if config module not found
            print(f"⚠️  Using fallback config: {e}", flush=True)
            config = {
                'region': os.environ.get('AWS_REGION', 'us-east-1'),
                'max_tokens': int(os.environ.get('BEDROCK_MAX_TOKENS', 8192)),
                'temperature': float(os.environ.get('BEDROCK_TEMPERATURE', 0.7)),
                'reasoning_enabled': os.environ.get('REASONING_ENABLED', 'false').lower() == 'true',
                'anthropic_version': 'bedrock-2023-05-31',
                'supports_reasoning': False,
                'fallback_models': []
            }

        # Add detailed configuration information
        detailed_status = {
            **test_response,
            'connection_type': 'AWS Bedrock Runtime',
            'service': 'Amazon Bedrock',
            'sdk_version': 'boto3',
            'region': config.get('region', 'us-east-1'),
            'max_tokens': config.get('max_tokens', 8192),
            'temperature': config.get('temperature', 0.7),
            'reasoning_enabled': config.get('reasoning_enabled', False),
            'anthropic_version': config.get('anthropic_version', 'bedrock-2023-05-31'),
            'supports_reasoning': config.get('supports_reasoning', False),
            'fallback_models': config.get('fallback_models', []),
            'credentials_source': 'IAM Role (App Runner)' if not os.environ.get('AWS_ACCESS_KEY_ID') else 'Environment Variables'
        }

        # Log the test if we have a session
        if session_id and session_exists(session_id):
            review_session = get_session(session_id)
            # Use correct log_activity signature (action, details_dict)
            review_session.activity_logger.log_activity(
                'Claude Connection Test - Success' if test_response['connected'] else 'Claude Connection Test - Failed',
                {
                    'model': test_response.get('model', 'unknown'),
                    'response_time': test_response.get('response_time', 0)
                }
            )

        # ✅ FIXED: Return connection status at root level for test compatibility
        return jsonify({
            'success': True,
            'connected': test_response.get('connected', False),
            'model': test_response.get('model', 'unknown'),
            'response_time': test_response.get('response_time', 0),
            'claude_status': detailed_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        # Log the failed test if we have a session
        try:
            if session_id and session_exists(session_id):
                review_session = get_session(session_id)
                # Use correct log_activity signature (action, details_dict)
                review_session.activity_logger.log_activity(
                    'Claude Connection Test - Error',
                    {
                        'error': str(e)
                    }
                )
        except:
            pass  # Don't let logging errors prevent error response

        # ✅ FIXED: Return connection status at root level for test compatibility
        return jsonify({
            'success': False,
            'connected': False,
            'error': str(e),
            'claude_status': {
                'connected': False,
                'error': f'Test failed: {str(e)}'
            }
        }), 500

@app.route('/clear_all_user_feedback', methods=['POST'])
def clear_all_user_feedback():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')

        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Clear all user feedback
        cleared_count = sum(len(items) for items in review_session.user_feedback.values())
        review_session.user_feedback = defaultdict(list)
        
        # Also remove user feedback from accepted feedback
        for section_name in review_session.accepted_feedback:
            review_session.accepted_feedback[section_name] = [
                item for item in review_session.accepted_feedback[section_name]
                if not item.get('user_created', False)
            ]
        
        # Log activity
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'ALL_USER_FEEDBACK_CLEARED',
            'details': f'Cleared {cleared_count} user feedback items'
        })
        
        return jsonify({'success': True, 'cleared_count': cleared_count})
        
    except Exception as e:
        return jsonify({'error': f'Clear all user feedback failed: {str(e)}'}), 500

@app.route('/export_activity_logs', methods=['GET'])
def export_activity_logs():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        format_type = request.args.get('format', 'json')
        
        if not session_id or not session_exists(session_id):
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = get_session(session_id)
        
        # Export activity logs
        export_data = review_session.activity_logger.export_activities()
        
        if format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Timestamp', 'Action', 'Status', 'Details', 'Error'])
            
            # Write activities
            for activity in export_data['activities']:
                writer.writerow([
                    activity.get('timestamp', ''),
                    activity.get('action', ''),
                    activity.get('status', ''),
                    str(activity.get('details', '')),
                    activity.get('error', '')
                ])
            
            output.seek(0)
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=activity_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        
        elif format_type == 'txt':
            output = f"AI-Prism Activity Logs\n"
            output += f"Generated: {export_data['export_timestamp']}\n"
            output += f"Session ID: {export_data['session_id']}\n"
            output += f"Total Activities: {export_data['summary']['total_activities']}\n"
            output += "=" * 50 + "\n\n"
            
            for activity in export_data['activities']:
                output += f"[{activity.get('timestamp', '')}] {activity.get('action', '').upper()}\n"
                output += f"Status: {activity.get('status', '').upper()}\n"
                if activity.get('details'):
                    output += f"Details: {activity.get('details', '')}\n"
                if activity.get('error'):
                    output += f"Error: {activity.get('error', '')}\n"
                output += "-" * 30 + "\n\n"
            
            return output, 200, {
                'Content-Type': 'text/plain',
                'Content-Disposition': f'attachment; filename=activity_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            }
        
        else:  # JSON format
            return jsonify(export_data), 200, {
                'Content-Disposition': f'attachment; filename=activity_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        
    except Exception as e:
        return jsonify({'error': f'Export activity logs failed: {str(e)}'}), 500

# ============================================================================
# MODEL HEALTH AND MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/model_stats', methods=['GET'])
def model_stats():
    """Get statistics about available models and their health status"""
    try:
        # Try V2 first (per-request isolation)
        try:
            from core.model_manager_v2 import model_manager_v2 as model_manager
            version = "V2 (Per-Request Isolation)"
        except ImportError:
            # Fallback to V1
            from core.model_manager import model_manager
            version = "V1"

        stats = model_manager.get_model_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'multi_model_enabled': True,
            'version': version
        })
    except ImportError:
        return jsonify({
            'success': False,
            'multi_model_enabled': False,
            'message': 'Multi-model fallback not configured'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/reset_model_cooldowns', methods=['POST'])
def reset_model_cooldowns():
    """Emergency endpoint to reset all model cooldowns"""
    try:
        # Try V2 first (per-request isolation)
        try:
            from core.model_manager_v2 import model_manager_v2 as model_manager
        except ImportError:
            # Fallback to V1
            from core.model_manager import model_manager

        model_manager.reset_all_cooldowns()
        return jsonify({
            'success': True,
            'message': 'All model cooldowns have been reset'
        })
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Multi-model fallback not configured'
        }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# CELERY TASK MANAGEMENT HELPERS
# ============================================================================

def get_task_status(task_id):
    """
    Get Celery task status and result from S3 backend

    ✅ RQ Version: Results stored directly in Redis (NO S3 polling needed!)
    Much simpler than Celery + S3 backend.

    Returns dict with task state and result (if completed)
    """
    print(f"📊 [CHECKPOINT] Fetching RQ task status for: {task_id}", flush=True)

    try:
        # Fetch job from RQ (simple!)
        job = Job.fetch(task_id, connection=redis_conn)

        # Get job status - RQ has clear states
        job_status = job.get_status()  # queued, started, finished, failed, deferred, scheduled, stopped, canceled

        # Build response
        response = {
            'task_id': task_id,
            'state': job_status.upper(),  # Convert to uppercase like Celery states
            'ready': job.is_finished or job.is_failed
        }

        print(f"   RQ Job state: {job_status}, Ready: {response['ready']}", flush=True)

        # Handle different states
        if job.is_finished:
            # Job completed successfully
            response['state'] = 'SUCCESS'
            response['status'] = 'Task completed successfully'
            response['progress'] = 100
            response['result'] = job.result
            print(f"✅ [RQ] Task SUCCESS, result keys: {response['result'].keys() if isinstance(response['result'], dict) else 'not a dict'}", flush=True)

        elif job.is_failed:
            # Job failed
            response['state'] = 'FAILURE'
            response['status'] = 'Task failed'
            response['progress'] = 0
            response['error'] = job.exc_info if job.exc_info else 'Unknown error'
            print(f"❌ [RQ] Task FAILURE: {response['error']}", flush=True)

        elif job.is_started:
            # Job is currently running
            response['state'] = 'PROGRESS'
            response['status'] = 'Task is running'
            response['progress'] = job.meta.get('progress', 50) if hasattr(job, 'meta') else 50
            print(f"⏳ [RQ] Task PROGRESS: {response['progress']}%", flush=True)

        elif job.is_queued or job.is_deferred:
            # Job is waiting in queue
            response['state'] = 'PENDING'
            response['status'] = 'Task is queued'
            response['progress'] = 0
            print(f"⏸️  [RQ] Task PENDING (queued)", flush=True)

        return response

    except Exception as e:
        # Job not found or error accessing Redis
        print(f"⚠️ Error fetching RQ job {task_id}: {e}", flush=True)

        # Return pending state if job not found
        response = {
            'task_id': task_id,
            'state': 'PENDING',
            'status': 'Task not found or Redis connection error',
            'progress': 0,
            'ready': False,
            'error': str(e)
        }
        return response

    # Should never reach here due to early returns in try/except
    return response


def get_queue_stats():
    """
    Get Celery queue statistics

    Returns dict with queue stats and worker info
    """
    from celery_config import celery_app

    try:
        # Get active tasks
        inspect = celery_app.control.inspect()

        active_tasks = inspect.active() or {}
        scheduled_tasks = inspect.scheduled() or {}
        registered_tasks = inspect.registered() or {}

        # Count total active tasks across all workers
        total_active = sum(len(tasks) for tasks in active_tasks.values())
        total_scheduled = sum(len(tasks) for tasks in scheduled_tasks.values())

        # Get worker count
        worker_count = len(active_tasks.keys())

        return {
            'available': True,
            'workers': worker_count,
            'active_tasks': total_active,
            'scheduled_tasks': total_scheduled,
            'registered_tasks': list(registered_tasks.values())[0] if registered_tasks else [],
            'details': {
                'active': active_tasks,
                'scheduled': scheduled_tasks
            }
        }

    except Exception as e:
        return {
            'available': False,
            'error': str(e),
            'workers': 0,
            'active_tasks': 0,
            'scheduled_tasks': 0
        }


# ============================================================================
# CELERY TASK MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    """Get status of a Celery task"""
    try:
        if not RQ_ENABLED:
            return jsonify({
                'error': 'Celery not available',
                'task_id': task_id,
                'state': 'UNAVAILABLE'
            }), 503

        status = get_task_status(task_id)

        # ✅ CRITICAL FIX: Store feedback_items in backend session when task completes
        # This fixes the "Feedback item not found" error when accepting/rejecting feedback
        if status.get('state') == 'SUCCESS' and status.get('result'):
            result = status.get('result')

            # Check if result contains feedback items from analysis task
            if isinstance(result, dict) and 'feedback_items' in result and 'section' in result:
                section_name = result.get('section')
                feedback_items = result.get('feedback_items', [])

                # Get session_id from request parameter
                session_id = request.args.get('session_id') or session.get('session_id')

                if session_id and session_exists(session_id):
                    review_session = get_session(session_id)

                    # Store feedback in backend session (THIS WAS MISSING!)
                    review_session.feedback_data[section_name] = feedback_items

                    print(f"✅ [TASK_STATUS] Stored {len(feedback_items)} feedback items for section '{section_name}' in backend session")
                    print(f"   Task ID: {task_id}")
                    print(f"   Session ID: {session_id}")
                else:
                    print(f"⚠️ [TASK_STATUS] Could not store feedback - session not found: {session_id}")

        return jsonify(status)

    except Exception as e:
        print(f"❌ [TASK_STATUS] Error: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'error': str(e),
            'task_id': task_id,
            'state': 'ERROR'
        }), 500


@app.route('/queue_stats', methods=['GET'])
def queue_stats():
    """Get Celery queue statistics"""
    try:
        stats = get_queue_stats()
        return jsonify(stats)

    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e)
        }), 500


@app.route('/cancel_task/<task_id>', methods=['POST'])
def cancel_task(task_id):
    """Cancel a running Celery task"""
    try:
        if not RQ_ENABLED:
            return jsonify({
                'error': 'Celery not available',
                'cancelled': False
            }), 503

        from celery_config import celery_app
        celery_app.control.revoke(task_id, terminate=True, signal='SIGKILL')

        return jsonify({
            'success': True,
            'task_id': task_id,
            'cancelled': True,
            'message': 'Task cancellation requested'
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'task_id': task_id,
            'cancelled': False
        }), 500

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    try:
        config = model_config.get_model_config()
        
        print("=" * 60)
        print("STARTING AI-PRISM DOCUMENT ANALYSIS TOOL")
        print("=" * 60)
        print(f"Server: http://localhost:{config['port']}")
        print(f"Environment: {config['flask_env']}")
        print(f"Debug mode: {config['flask_env'] != 'production'}")
        print(f"AI Model: {config['model_name']}")
        print(f"AWS Credentials: {'Available' if model_config.has_credentials() else 'Not configured'}")
        print(f"All routes and functionality loaded successfully")
        print("=" * 60)
        print("Ready for document analysis with Hawkeye framework!")
        print("=" * 60)
        
        app.run(
            debug=config['flask_env'] != 'production', 
            host='0.0.0.0', 
            port=config['port'], 
            threaded=True, 
            use_reloader=False
        )
    except Exception as e:
        print("=" * 60)
        print("AI-PRISM STARTUP ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        print("Check configuration and try again")
        print("=" * 60)