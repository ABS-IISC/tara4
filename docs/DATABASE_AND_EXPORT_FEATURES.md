# Database Auto-Save & Export Features - Complete Guide

## Current Features Already Implemented ✅

### 1. CSV Download Functionality
**Endpoint**: `/download_statistics`
**Location**: [app.py:2112-2195](app.py#L2112-L2195)

**Features**:
- Download statistics in CSV, TXT, or JSON format
- Includes: Total feedback, risk levels, accepted/rejected counts
- Section-wise breakdown
- Chat interactions count

**Frontend Button**: "📊 Download Statistics" in enhanced_index.html:2992

**Usage**:
```javascript
function downloadStatistics() {
    // Downloads comprehensive statistics in selected format
    window.location.href = `/download_statistics?session_id=${currentSession}&format=csv`;
}
```

### 2. Activity Logs Export
**Endpoint**: `/export_activity_logs`
**Location**: [app.py:2494-2561](app.py#L2494-L2561)

**Features**:
- Export all activity logs in CSV, TXT, or JSON
- Includes: Timestamp, Action, Status, Details, Errors
- Comprehensive session tracking

**Frontend Button**: "📋 Activity Logs" in enhanced_index.html:2645

**Usage**:
```javascript
function showActivityLogs() {
    // Displays and exports activity logs
}
```

### 3. S3 Export on Review Completion
**Endpoint**: `/complete_review` with `export_to_s3` parameter
**Location**: [app.py:1485-1666](app.py#L1485-L1666)

**Features**:
- Automatically exports to S3 when user selects option
- Uploads: Before document, After document, Activity logs, Statistics
- Creates timestamped folder structure
- Returns S3 location and file URLs

**How it works**:
1. User completes review
2. System generates reviewed document with comments
3. If `export_to_s3=true`, automatically uploads all files to S3
4. Activity logs track the entire process

**Code**:
```python
if export_to_s3:
    export_result = s3_export_manager.export_complete_review_to_s3(
        review_session,
        review_session.document_path,  # before document
        output_path  # after document
    )
    response_data['s3_export'] = export_result
```

### 4. Manual S3 Export
**Endpoint**: `/export_to_s3`
**Location**: [app.py:2197-2298](app.py#L2197-L2298)

**Features**:
- On-demand S3 export button
- Can be triggered at any time
- Exports complete review package

**Frontend Button**: "🚀 Export to S3" in enhanced_index.html:2998

## New Database Manager Created ✅

**File**: [core/database_manager.py](core/database_manager.py)

**Features**:
- SQLite database with 5 tables:
  - `reviews` - Document analysis sessions
  - `feedback_items` - All AI + user feedback
  - `activity_logs` - Comprehensive activity tracking
  - `sections` - Section analysis status
  - `chat_history` - Chat interactions

**Methods**:
- `create_review_session()` - Initialize session
- `save_feedback_item()` - Save individual feedback
- `update_section_analyzed()` - Mark section complete
- `update_feedback_action()` - Track accept/reject
- `complete_review()` - Finalize with statistics
- `log_activity()` - Log any action
- `log_chat_message()` - Track chat
- `export_to_csv()` - Export everything to CSV
- `get_session_summary()` - Get complete session data
- `get_all_reviews()` - List all historical reviews

## Integration Points Needed

### 1. On Document Upload
**File**: app.py, `/upload` endpoint (line ~230)

**Add**:
```python
# After successful section extraction
db_manager.create_review_session(
    session_id=session_id,
    document_name=filename,
    sections=section_names
)
```

### 2. After Section Analysis
**File**: app.py, `/analyze_section` endpoint (line ~362)

**Add**:
```python
# After analysis completes
for feedback_item in feedback_items:
    db_manager.save_feedback_item(
        session_id=session_id,
        section_name=section_name,
        feedback_item=feedback_item,
        user_action='pending'
    )

db_manager.update_section_analyzed(
    session_id=session_id,
    section_name=section_name,
    feedback_count=len(feedback_items)
)
```

### 3. On Feedback Accept/Reject
**File**: app.py, `/accept_feedback` and `/reject_feedback` endpoints

**Add**:
```python
db_manager.update_feedback_action(
    session_id=session_id,
    section_name=section_name,
    feedback_id=feedback_item_id,
    action='accepted'  # or 'rejected'
)
```

### 4. On Review Completion
**File**: app.py, `/complete_review` endpoint (line ~1485)

**Add** (after successful document generation):
```python
# Get statistics
stats = stats_manager.get_statistics()

# Save to database
db_manager.complete_review(
    session_id=session_id,
    output_filename=output_filename,
    stats=stats,
    s3_location=s3_location if export_to_s3 else None
)
```

### 5. On Chat Message
**File**: app.py, `/chat` endpoint

**Add**:
```python
# Log user message
db_manager.log_chat_message(session_id, 'user', user_message)

# Log AI response
db_manager.log_chat_message(session_id, 'assistant', ai_response)
```

### 6. Enhanced CSV Download Endpoint
**Add new endpoint**:
```python
@app.route('/download_complete_data', methods=['GET'])
def download_complete_data():
    """Download ALL data from database as CSV"""
    session_id = request.args.get('session_id')

    if session_id:
        csv_data = db_manager.export_to_csv(session_id=session_id)
    else:
        csv_data = db_manager.export_to_csv()  # All sessions

    return csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=complete_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    }
```

## Activity Log Enhancement Needed

### Current Issues:
1. Activity logs may not capture ALL user actions
2. Some frontend actions not logged to backend

### Fixes Needed:

**1. Add comprehensive frontend logging**:
```javascript
// In static/js/activity_logs.js or create new file

function logActivity(action, details) {
    if (!currentSession) return;

    fetch('/log_activity', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            session_id: currentSession,
            action: action,
            details: details
        })
    });
}

// Call this on every user action:
// - Document upload
// - Section navigation
// - Button clicks (Analyze, Accept, Reject)
// - Chat messages
// - Settings changes
// - Downloads
```

**2. Add backend endpoint for frontend logging**:
```python
@app.route('/log_activity', methods=['POST'])
def log_activity_endpoint():
    """Log activity from frontend"""
    data = request.get_json()
    session_id = data.get('session_id')
    action = data.get('action')
    details = data.get('details')

    if session_id and session_exists(session_id):
        review_session = get_session(session_id)

        # Log to activity_logger
        review_session.activity_logger.log_session_event(action, details)

        # Log to database
        db_manager.log_activity(session_id, action, 'success', details)

        # Log to session activity_log list
        review_session.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        })

        return jsonify({'success': True})

    return jsonify({'error': 'Invalid session'}), 400
```

**3. Add event listeners in frontend**:
```javascript
// Add to all critical UI elements
document.getElementById('analyzeBtn').addEventListener('click', () => {
    logActivity('ANALYZE_BUTTON_CLICKED', {
        section: currentSectionName,
        index: currentSectionIndex
    });
});

// Navigation
function navigateToSection(index) {
    logActivity('SECTION_NAVIGATED', {
        from_section: sections[currentSectionIndex],
        to_section: sections[index],
        progress: `${analyzedSections}/${totalSections}`
    });
    // ... rest of navigation code
}

// Accept feedback
function acceptFeedback(feedbackId) {
    logActivity('FEEDBACK_ACCEPTED', {
        section: currentSectionName,
        feedback_id: feedbackId,
        type: feedbackType,
        risk_level: riskLevel
    });
    // ... rest of accept code
}
```

## Automatic Database Save - Implementation Summary

### When Auto-Save Happens:

1. **On Upload** → Creates review session record
2. **After Each Section Analysis** → Saves feedback items + updates section status
3. **On Accept/Reject** → Updates feedback action status
4. **On Chat** → Logs chat message
5. **On Complete Review** → Finalizes with full statistics + S3 location

### Database Location:
`/Users/abhsatsa/Documents/risk stuff/tool/tara2/data/analysis_history.db`

### CSV Export Includes:
- All reviews (historical)
- All feedback items with user actions
- All activity logs
- All sections and their status
- All chat history

## Testing the Features

### 1. Test CSV Download:
```bash
# Visit in browser:
http://localhost:8082/download_statistics?session_id=YOUR_SESSION_ID&format=csv

# Or use the "Download Statistics" button in UI
```

### 2. Test Activity Logs:
```bash
# Visit in browser:
http://localhost:8082/export_activity_logs?session_id=YOUR_SESSION_ID&format=csv

# Or click "Activity Logs" button in UI
```

### 3. Test S3 Export:
- Complete a review
- Check "Export to S3" option in modal
- Click "Complete Review"
- Check response for S3 location

### 4. Test Database (after integration):
```python
# In Python console:
from core.database_manager import db_manager

# Get all reviews
reviews = db_manager.get_all_reviews()
print(f"Total reviews: {len(reviews)}")

# Get session summary
summary = db_manager.get_session_summary('your-session-id')
print(f"Feedback items: {len(summary['feedback_items'])}")

# Export to CSV
csv_data = db_manager.export_to_csv()
with open('export.csv', 'w') as f:
    f.write(csv_data)
```

## Quick Integration Script

To quickly integrate database manager, add this to app.py after imports:

```python
# After line 17 (database_manager import)

# Wrap key functions with database saves
def upload_with_db_save(original_upload_function):
    def wrapper(*args, **kwargs):
        result = original_upload_function(*args, **kwargs)
        if result and isinstance(result, dict) and result.get('success'):
            db_manager.create_review_session(
                session_id=result['session_id'],
                document_name=result['document_name'],
                sections=result['sections']
            )
        return result
    return wrapper

# Apply wrappers (do this BEFORE defining routes)
# This automatically saves to database on key operations
```

## Summary

✅ **CSV Download**: Already working - `/download_statistics`
✅ **Activity Logs**: Already working - `/export_activity_logs`
✅ **S3 Export**: Already working - automatic on complete_review
✅ **Database Manager**: Created but needs integration
⚠️ **Activity Log Coverage**: Needs frontend event tracking
⚠️ **Auto-Save**: Needs integration at key endpoints

**Next Steps**:
1. Integrate database manager at 6 key points (upload, analyze, accept/reject, complete, chat)
2. Add comprehensive frontend activity logging
3. Add `/log_activity` endpoint for frontend
4. Test complete workflow
5. Verify CSV exports include all data
