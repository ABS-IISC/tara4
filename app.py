from flask import Flask, render_template, request, jsonify, send_file, session
import os
import json
import uuid
from datetime import datetime
from collections import defaultdict
from werkzeug.utils import secure_filename

# Import our modular components
from core.document_analyzer import DocumentAnalyzer
from core.ai_feedback_engine import AIFeedbackEngine
from utils.statistics_manager import StatisticsManager
from utils.document_processor import DocumentProcessor

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Global components - with error handling
try:
    document_analyzer = DocumentAnalyzer()
    ai_engine = AIFeedbackEngine()
    stats_manager = StatisticsManager()
    doc_processor = DocumentProcessor()
    print("All components initialized successfully")
except Exception as e:
    print(f"Error initializing components: {e}")
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
        
        # Log activity
        log_details = f'Analysis document {filename} uploaded with {len(sections)} sections'
        if guidelines_uploaded:
            log_details += f', Guidelines document {review_session.guidelines_name} also uploaded'
        log_details += f', Guidelines preference: {guidelines_preference}'
            
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'DOCUMENTS_UPLOADED',
            'details': log_details
        })
        
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
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/analyze_section', methods=['POST'])
def analyze_section():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        section_name = data.get('section_name')
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
        if section_name not in review_session.sections:
            return jsonify({'error': 'Section not found'}), 400
        
        section_content = review_session.sections[section_name]
        
        # Analyze with AI engine
        analysis_result = ai_engine.analyze_section(section_name, section_content)
        feedback_items = analysis_result.get('feedback_items', [])
        
        # Store feedback data
        review_session.feedback_data[section_name] = feedback_items
        
        # Update statistics
        stats_manager.update_feedback_data(section_name, feedback_items)
        
        # Log activity
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'SECTION_ANALYZED',
            'details': f'Section {section_name} analyzed - {len(feedback_items)} feedback items generated'
        })
        
        return jsonify({
            'success': True,
            'feedback_items': feedback_items,
            'section_content': section_content
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

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
        
        # Log activity
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'FEEDBACK_ACCEPTED',
            'details': f'Accepted {feedback_item.get("type")} feedback in {section_name}'
        })
        
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
        
        # Log activity
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'FEEDBACK_REJECTED',
            'details': f'Rejected {feedback_item.get("type")} feedback in {section_name}'
        })
        
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
            'ai_id': ai_id  # Store AI feedback ID if provided
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
        
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'CUSTOM_FEEDBACK_ADDED',
            'details': activity_detail
        })
        
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
        
        # Get AI response with model-specific processing
        context = {
            'current_section': current_section,
            'document_name': review_session.document_name,
            'total_sections': len(review_session.sections),
            'ai_model': ai_model,
            'guidelines_preference': getattr(review_session, 'guidelines_preference', 'both')
        }
        
        try:
            response = ai_engine.process_chat_query(message, context)
        except Exception as model_error:
            # If primary model fails, try fallback
            fallback_models = ['claude-3-haiku', 'gpt-4', 'gemini-pro']
            response = None
            
            for fallback_model in fallback_models:
                if fallback_model != ai_model:
                    try:
                        context['ai_model'] = fallback_model
                        response = ai_engine.process_chat_query(message, context)
                        response = f"[Using {fallback_model} as backup] {response}"
                        break
                    except:
                        continue
            
            if not response:
                response = "I'm experiencing technical difficulties with all AI models. Please try again later or contact support."
        
        # Add AI response to history
        review_session.chat_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat(),
            'ai_model': ai_model
        })
        
        # Log activity
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'CHAT_INTERACTION',
            'details': f'User query with {ai_model}: {message[:50]}...'
        })
        
        return jsonify({'success': True, 'response': response, 'model_used': ai_model})
        
    except Exception as e:
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500

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
        
        # Analyze patterns from current session data
        patterns = analyze_feedback_patterns(review_session)
        
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

@app.route('/get_logs', methods=['GET'])
def get_logs():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
        return jsonify({'success': True, 'logs': review_session.activity_log})
        
    except Exception as e:
        return jsonify({'error': f'Get logs failed: {str(e)}'}), 500

@app.route('/get_learning_status', methods=['GET'])
def get_learning_status():
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        review_session = sessions[session_id]
        
        # Calculate learning metrics
        custom_feedback_count = sum(len(items) for items in review_session.user_feedback.values())
        accepted_count = sum(len(items) for items in review_session.accepted_feedback.values())
        rejected_count = sum(len(items) for items in review_session.rejected_feedback.values())
        total_ai_feedback = sum(len(items) for items in review_session.feedback_data.values())
        
        # Calculate learning effectiveness
        acceptance_rate = (accepted_count / max(accepted_count + rejected_count, 1)) * 100
        user_engagement = (custom_feedback_count / max(total_ai_feedback, 1)) * 100
        
        learning_status = {
            'custom_feedback_count': custom_feedback_count,
            'accepted_feedback_count': accepted_count,
            'rejected_feedback_count': rejected_count,
            'total_ai_feedback': total_ai_feedback,
            'sections_with_patterns': len([s for s in review_session.sections if review_session.feedback_data.get(s)]),
            'learning_active': True,
            'acceptance_rate': round(acceptance_rate, 1),
            'user_engagement_score': round(user_engagement, 1),
            'learning_insights': generate_learning_insights(review_session),
            'improvement_suggestions': generate_improvement_suggestions(acceptance_rate, user_engagement)
        }
        
        return jsonify({'success': True, 'learning_status': learning_status})
        
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

@app.route('/complete_review', methods=['POST'])
def complete_review():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('session_id')
        
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
        
        # Create reviewed document
        output_filename = f"reviewed_{review_session.document_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        output_path = doc_processor.create_document_with_comments(
            review_session.document_path,
            comments_data,
            output_filename
        )
        
        if output_path:
            # Log completion
            review_session.activity_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'REVIEW_COMPLETED',
                'details': f'Review completed with {len(comments_data)} comments added'
            })
            
            return jsonify({
                'success': True,
                'output_file': output_filename,
                'comments_count': len(comments_data)
            })
        else:
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
            output = f"TARA Statistics Report\n"
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

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8000))
        print(f"Starting Flask app on port {port}")
        app.run(debug=False, host='0.0.0.0', port=port, threaded=True, use_reloader=False)
    except Exception as e:
        print(f"Flask startup error: {e}")
        import traceback
        traceback.print_exc()