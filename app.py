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
    
    # Create minimal fallback classes
    class DocumentAnalyzer:
        def extract_sections_from_docx(self, file_path):
            return {"Section 1": "Sample content"}, {"Section 1": ["Sample paragraph"]}, {"Section 1": [0]}
    
    class AIFeedbackEngine:
        def analyze_section(self, section_name, content):
            return {"feedback_items": []}
        def process_chat_query(self, query, context):
            return "AI chat temporarily unavailable"
    
    class StatisticsManager:
        def get_statistics(self): return {}
        def update_feedback_data(self, *args): pass
        def record_acceptance(self, *args): pass
        def record_rejection(self, *args): pass
        def add_user_feedback(self, *args): pass
        def get_detailed_breakdown(self, *args): return {}
        def generate_breakdown_html(self, *args): return "<p>Statistics unavailable</p>"
    
    class DocumentProcessor:
        def create_document_with_comments(self, *args): return None
    
    class DocumentPatternAnalyzer:
        def find_recurring_patterns(self): return []
        def get_category_trends(self): return {}
        def get_risk_patterns(self): return {}
        def get_pattern_report_html(self): return "<p>Pattern analysis unavailable</p>"
        def add_document_feedback(self, *args): pass
    
    class AuditLogger:
        def log(self, *args): pass
        def get_session_logs(self): return []
        def get_performance_metrics(self): return {}
        def get_activity_timeline(self): return []
    
    class FeedbackLearningSystem:
        def record_ai_feedback_response(self, *args): pass
        def add_custom_feedback(self, *args): pass
        def get_learning_statistics(self): return {}
        def generate_learning_report_html(self): return "<p>Learning system unavailable</p>"
        def get_recommended_feedback(self, *args): return []
    
    class S3ExportManager:
        def export_complete_review_to_s3(self, *args): return {"success": False, "error": "S3 export unavailable"}
        def test_s3_connection(self): return {"connected": False, "error": "S3 unavailable"}
    
    class ActivityLogger:
        def __init__(self, session_id): self.session_id = session_id
        def log_document_upload(self, *args, **kwargs): pass
        def log_ai_analysis(self, *args, **kwargs): pass
        def log_feedback_action(self, *args, **kwargs): pass
        def log_s3_operation(self, *args, **kwargs): pass
        def log_activity(self, *args, **kwargs): pass  # ✅ FIX: Added missing method
        def log_session_event(self, *args, **kwargs): pass
        def get_activity_summary(self): return {"total_activities": 0, "success_count": 0, "failed_count": 0, "success_rate": 0}
        def export_activities(self): return {"activities": [], "summary": {}}

# Try to import model config with fallback
try:
    from config.model_config import model_config
except ImportError:
    class FallbackModelConfig:
        def get_model_config(self):
            return {
                'model_id': os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0'),
                'model_name': 'Claude 3.5 Sonnet',
                'region': os.environ.get('AWS_REGION', 'us-east-1'),
                'port': int(os.environ.get('PORT', 8080)),
                'flask_env': os.environ.get('FLASK_ENV', 'production')
            }
        def has_credentials(self): return True
        def print_config_summary(self): print("⚠️ Using fallback configuration")
    
    model_config = FallbackModelConfig()

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

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

# Session storage
sessions = {}

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
        
        # Store session
        sessions[session_id] = review_session
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
            
        if session_id not in sessions:
            return jsonify({'success': False, 'error': 'Invalid or expired session'}), 400
        
        if not section_name:
            return jsonify({'success': False, 'error': 'No section name provided'}), 400
        
        review_session = sessions[session_id]
        
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
        
        print(f"ANALYZING section: {section_name} ({len(section_content)} characters)")
        
        # Analyze with AI engine with timing
        analysis_start_time = datetime.now()
        try:
            print(f"Starting AI analysis for section: {section_name}")
            review_session.activity_logger.start_operation('ai_analysis', {
                'section': section_name,
                'content_length': len(section_content)
            })
            
            analysis_result = ai_engine.analyze_section(section_name, section_content)
            
            analysis_duration = (datetime.now() - analysis_start_time).total_seconds()
            feedback_count = len(analysis_result.get('feedback_items', []))
            
            review_session.activity_logger.complete_operation(success=True, details={
                'feedback_generated': feedback_count,
                'analysis_duration': analysis_duration
            })
            
            review_session.activity_logger.log_ai_analysis(section_name, feedback_count, analysis_duration, success=True)
            print(f"AI analysis completed")
            
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        # Log activity with comprehensive tracking
        review_session.activity_logger.log_feedback_action(
            'accepted', 
            feedback_id, 
            section_name, 
            feedback_item.get('description')
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        # Log activity with comprehensive tracking
        review_session.activity_logger.log_feedback_action(
            'rejected', 
            feedback_id, 
            section_name, 
            feedback_item.get('description')
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
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Reject failed: {str(e)}'}), 500

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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        if ai_reference:
            activity_detail += f' (Related to AI: {ai_reference[:30]}...)'
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        # Track chat response time
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
        actual_model = model_config.get_model_config()['model_name']
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
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR Chat error: {str(e)}")
        print(f"ERROR Traceback:\n{error_trace}")

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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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

@app.route('/get_section_content', methods=['GET'])
def get_section_content():
    """
    NEW ENDPOINT: Get section content WITHOUT analysis
    Used for on-demand analysis workflow
    """
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        section_name = request.args.get('section_name')

        if not session_id or session_id not in sessions:
            return jsonify({'success': False, 'error': 'Invalid session'}), 400

        if not section_name:
            return jsonify({'success': False, 'error': 'No section name provided'}), 400

        review_session = sessions[session_id]

        # Get section content from document analyzer (use 'sections' not 'document_sections')
        if hasattr(review_session, 'sections') and section_name in review_session.sections:
            content = review_session.sections[section_name]

            return jsonify({
                'success': True,
                'content': content,
                'section_name': section_name
            })
        else:
            # Log available sections for debugging
            available_sections = list(review_session.sections.keys()) if hasattr(review_session, 'sections') else []
            print(f"ERROR: Section '{section_name}' not found. Available sections: {available_sections}")

            return jsonify({
                'success': False,
                'error': f'Section "{section_name}" not found. Available sections: {available_sections}'
            }), 404

    except Exception as e:
        print(f"ERROR Get section content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/complete_review', methods=['POST'])
def complete_review():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        export_to_s3 = data.get('export_to_s3', False)
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
        # Prepare comments data
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

@app.route('/reset_session', methods=['POST'])
def reset_session():
    try:
        session_id = session.get('session_id')
        
        if session_id and session_id in sessions:
            # Clean up old session
            del sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        if session_id and session_id in sessions:
            review_session = sessions[session_id]
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
        if session_id and session_id in sessions:
            review_session = sessions[session_id]
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

        # Test Claude connection with a simple test prompt
        test_response = ai_engine.test_connection()

        # Get model configuration for additional details
        from config.model_config import model_config
        config = model_config.get_model_config()

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
            'credentials_source': 'AWS Profile (admin-abhsatsa)' if os.environ.get('AWS_PROFILE') else 'Environment Variables'
        }

        # Log the test if we have a session
        if session_id and session_id in sessions:
            review_session = sessions[session_id]
            review_session.activity_logger.log_activity(
                action='Claude Connection Test',
                status='success' if test_response['connected'] else 'failed',
                details={
                    'model': test_response.get('model', 'unknown'),
                    'response_time': test_response.get('response_time', 0)
                }
            )

        return jsonify({
            'success': True,
            'claude_status': detailed_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        # Log the failed test if we have a session
        if session_id and session_id in sessions:
            review_session = sessions[session_id]
            review_session.activity_logger.log_activity(
                'Claude Connection Test',
                {
                    'status': 'failed',
                    'error': str(e)
                },
                category='AI'
            )

        return jsonify({
            'success': False,
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

        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
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