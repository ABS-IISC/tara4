#!/usr/bin/env python3
"""
End-to-End Manual Testing Guide
Generates step-by-step instructions for testing every button and feature
"""

import json
from datetime import datetime

class TestGuide:
    def __init__(self):
        self.test_results = []
        self.current_test = None

    def start_test(self, test_id, name, description):
        self.current_test = {
            'id': test_id,
            'name': name,
            'description': description,
            'steps': [],
            'expected_logs': [],
            'expected_backend_calls': [],
            'status': 'PENDING',
            'notes': []
        }

    def add_step(self, step_num, action, expected_result):
        self.current_test['steps'].append({
            'step': step_num,
            'action': action,
            'expected': expected_result
        })

    def add_expected_log(self, log_pattern):
        self.current_test['expected_logs'].append(log_pattern)

    def add_backend_call(self, method, endpoint, payload=None):
        self.current_test['expected_backend_calls'].append({
            'method': method,
            'endpoint': endpoint,
            'payload': payload
        })

    def add_note(self, note):
        self.current_test['notes'].append(note)

    def complete_test(self):
        self.test_results.append(self.current_test)
        self.current_test = None

    def generate_html_guide(self):
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI-Prism E2E Testing Guide</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .test-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .test-header {
            border-bottom: 2px solid #4f46e5;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .test-id {
            color: #4f46e5;
            font-weight: bold;
            font-size: 14px;
        }
        .test-name {
            font-size: 20px;
            font-weight: bold;
            margin: 5px 0;
        }
        .test-description {
            color: #666;
            font-size: 14px;
        }
        .section-title {
            font-weight: bold;
            margin-top: 15px;
            margin-bottom: 10px;
            color: #333;
        }
        .step {
            background: #f9f9f9;
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #4f46e5;
        }
        .step-num {
            color: #4f46e5;
            font-weight: bold;
        }
        .expected {
            color: #059669;
            margin-top: 5px;
            font-size: 13px;
        }
        .log-pattern {
            font-family: 'Courier New', monospace;
            background: #1e293b;
            color: #10b981;
            padding: 5px 10px;
            border-radius: 4px;
            margin: 3px 0;
            font-size: 12px;
        }
        .backend-call {
            background: #eff6ff;
            padding: 8px;
            border-left: 3px solid #3b82f6;
            margin: 5px 0;
            font-size: 13px;
        }
        .method {
            font-weight: bold;
            color: #3b82f6;
        }
        .note {
            background: #fef3c7;
            padding: 10px;
            border-left: 3px solid #f59e0b;
            margin: 5px 0;
            font-size: 13px;
        }
        .checkbox {
            margin-right: 10px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .summary {
            background: #4f46e5;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 AI-Prism End-to-End Testing Guide</h1>
        <p>Complete manual testing instructions for all features</p>
        <p><strong>Generated:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </div>

    <div class="summary">
        <h2>📊 Test Summary</h2>
        <p><strong>Total Tests:</strong> """ + str(len(self.test_results)) + """</p>
        <p><strong>Before starting:</strong></p>
        <ul>
            <li>Ensure application is running on http://localhost:8080</li>
            <li>Open browser Developer Tools (F12)</li>
            <li>Open Console tab to see logs</li>
            <li>Open Network tab to see API calls</li>
            <li>Have test document ready (test_sample.docx)</li>
        </ul>
    </div>
"""

        for test in self.test_results:
            html += f"""
    <div class="test-card">
        <div class="test-header">
            <div class="test-id">{test['id']}</div>
            <div class="test-name">
                <input type="checkbox" class="checkbox" id="{test['id']}">
                <label for="{test['id']}">{test['name']}</label>
            </div>
            <div class="test-description">{test['description']}</div>
        </div>

        <div class="section-title">📝 Test Steps:</div>
"""
            for step in test['steps']:
                html += f"""
        <div class="step">
            <div><span class="step-num">Step {step['step']}:</span> {step['action']}</div>
            <div class="expected">✓ Expected: {step['expected']}</div>
        </div>
"""

            if test['expected_logs']:
                html += """
        <div class="section-title">📋 Expected Console Logs:</div>
"""
                for log in test['expected_logs']:
                    html += f'        <div class="log-pattern">{log}</div>\n'

            if test['expected_backend_calls']:
                html += """
        <div class="section-title">🔌 Expected Backend Calls:</div>
"""
                for call in test['expected_backend_calls']:
                    if call['payload']:
                        # Convert ... (ellipsis) to string representation
                        payload_display = str(call['payload'])
                        payload_str = f" → {payload_display}"
                    else:
                        payload_str = ""
                    html += f"""        <div class="backend-call">
            <span class="method">{call['method']}</span> {call['endpoint']}{payload_str}
        </div>
"""

            if test['notes']:
                html += """
        <div class="section-title">💡 Important Notes:</div>
"""
                for note in test['notes']:
                    html += f'        <div class="note">⚠️ {note}</div>\n'

            html += """
    </div>
"""

        html += """
    <div class="summary">
        <h2>✅ Testing Complete!</h2>
        <p>After completing all tests:</p>
        <ol>
            <li>Count checkboxes checked</li>
            <li>Document any failures</li>
            <li>Take screenshots of issues</li>
            <li>Save console logs</li>
            <li>Report findings</li>
        </ol>
    </div>
</body>
</html>
"""
        return html

def generate_test_guide():
    guide = TestGuide()

    # TEST 1: Document Upload
    guide.start_test(
        'TEST-001',
        'Document Upload - Basic',
        'Test uploading a Word document and verifying section extraction'
    )
    guide.add_step(1, 'Open http://localhost:8080 in browser', 'Landing page loads with upload form')
    guide.add_step(2, 'Click "Choose File" button', 'File picker dialog opens')
    guide.add_step(3, 'Select test_sample.docx', 'Filename appears next to button')
    guide.add_step(4, 'Click "Upload & Start Analysis" button', 'Upload begins, progress indicator appears')
    guide.add_step(5, 'Wait for upload to complete', 'Success notification appears: "Documents uploaded successfully! Select a section to start analysis."')
    guide.add_step(6, 'Check section dropdown', 'Dropdown populated with 4 sections: Executive Summary, Timeline of Events, Root Cause Analysis, Preventative Actions')
    guide.add_expected_log('Document uploaded successfully')
    guide.add_expected_log('Sections extracted: 4')
    guide.add_expected_log('Session ID: ...')
    guide.add_backend_call('POST', '/upload', {'document': 'FormData'})
    guide.add_note('Upload should complete in under 1 second')
    guide.add_note('NO analysis should happen automatically - this is the new workflow!')
    guide.complete_test()

    # TEST 2: Section Analysis On-Demand
    guide.start_test(
        'TEST-002',
        'Section Analysis - On-Demand',
        'Test analyzing a section when user clicks on it'
    )
    guide.add_step(1, 'Click on section dropdown', 'Dropdown opens showing all sections')
    guide.add_step(2, 'Select "Executive Summary"', 'Loading spinner appears with modal overlay')
    guide.add_step(3, 'Verify background is frozen', 'Cannot click on anything behind modal overlay (backdrop is blurred)')
    guide.add_step(4, 'Wait for analysis (20-40 seconds)', 'Spinner continues rotating')
    guide.add_step(5, 'Wait for completion', 'Spinner disappears, modal overlay removed')
    guide.add_step(6, 'Check section content area', 'Executive Summary text displays')
    guide.add_step(7, 'Scroll down to feedback panel', '8-12 feedback cards display')
    guide.add_step(8, 'Verify each card shows: ID, Type badge, Category, Description, Suggestion, Risk level, Hawkeye references', 'All fields populated')
    guide.add_expected_log('📊 Analyzing section "Executive Summary" on-demand...')
    guide.add_expected_log('✅ Async analysis task submitted')
    guide.add_expected_log('Task ID: ...')
    guide.add_expected_log('✅ Stored section content')
    guide.add_expected_log('📊 Analysis polling attempt 1: PROGRESS')
    guide.add_expected_log('✅ Analysis complete for "Executive Summary"')
    guide.add_backend_call('POST', '/analyze_section', {'session_id': '...', 'section_name': 'Executive Summary'})
    guide.add_backend_call('GET', '/task_status/{task_id}', None)
    guide.add_note('Analysis takes 20-40 seconds with Extended Thinking mode')
    guide.add_note('This is the KEY new workflow - analysis ONLY happens when user clicks')
    guide.complete_test()

    # TEST 3: Accept Feedback
    guide.start_test(
        'TEST-003',
        'Feedback Management - Accept',
        'Test accepting AI-generated feedback items'
    )
    guide.add_step(1, 'Locate first feedback card', 'Card visible with Accept/Reject buttons')
    guide.add_step(2, 'Click "Accept" button (green checkmark icon)', 'Button state changes - background turns green')
    guide.add_step(3, 'Check statistics panel', 'Accepted count increases by 1')
    guide.add_step(4, 'Click on different section (Timeline of Events)', 'Section changes')
    guide.add_step(5, 'Return to Executive Summary', 'Previously accepted feedback still shows as accepted (green)')
    guide.add_expected_log('Feedback accepted: FB001')
    guide.add_expected_log('Statistics updated')
    guide.add_note('Accept state stored in window.sectionData')
    guide.add_note('No backend call - client-side state management')
    guide.complete_test()

    # TEST 4: Reject Feedback
    guide.start_test(
        'TEST-004',
        'Feedback Management - Reject',
        'Test rejecting AI-generated feedback items'
    )
    guide.add_step(1, 'Locate second feedback card', 'Card visible with Accept/Reject buttons')
    guide.add_step(2, 'Click "Reject" button (red X icon)', 'Button state changes - background turns red')
    guide.add_step(3, 'Check statistics panel', 'Rejected count increases by 1')
    guide.add_step(4, 'Navigate to different section', 'Section changes')
    guide.add_step(5, 'Return to Executive Summary', 'Previously rejected feedback still shows as rejected (red)')
    guide.add_expected_log('Feedback rejected: FB002')
    guide.add_expected_log('Statistics updated')
    guide.add_note('Reject state stored in window.sectionData')
    guide.complete_test()

    # TEST 5: Text Highlighting
    guide.start_test(
        'TEST-005',
        'Text Highlighting - Apply Highlight',
        'Test highlighting text in document content (THIS IS REPORTED AS BROKEN)'
    )
    guide.add_step(1, 'Scroll to section content area', 'Document text visible')
    guide.add_step(2, 'Select a sentence or phrase with mouse', 'Text becomes selected (blue highlight)')
    guide.add_step(3, 'Look for highlight button or right-click menu', 'Highlight option should appear')
    guide.add_step(4, 'Click "Highlight" option', 'Selected text background changes to yellow')
    guide.add_step(5, 'Click elsewhere to deselect', 'Highlight persists (yellow background)')
    guide.add_step(6, 'Select different text and highlight', 'Second highlight appears')
    guide.add_expected_log('Text highlighted: ...')
    guide.add_expected_log('Highlight saved')
    guide.add_note('🔴 USER REPORTED THIS AS NOT WORKING - CHECK CAREFULLY')
    guide.add_note('Check if CSS classes are applied')
    guide.add_note('Check if highlight state is saved in window.highlightedTexts')
    guide.add_note('Check console for any JavaScript errors')
    guide.complete_test()

    # TEST 6: Remove Highlighting
    guide.start_test(
        'TEST-006',
        'Text Highlighting - Remove Highlight',
        'Test removing highlights from text'
    )
    guide.add_step(1, 'Click on previously highlighted text', 'Highlight becomes selected')
    guide.add_step(2, 'Right-click or look for remove option', '"Remove Highlight" option appears')
    guide.add_step(3, 'Click "Remove Highlight"', 'Yellow background disappears')
    guide.add_step(4, 'Navigate away and return', 'Highlight remains removed')
    guide.add_expected_log('Highlight removed')
    guide.add_note('Check if highlight is removed from window.highlightedTexts array')
    guide.complete_test()

    # TEST 7: Custom Feedback
    guide.start_test(
        'TEST-007',
        'Custom Feedback - Add New Item',
        'Test adding user-created feedback items'
    )
    guide.add_step(1, 'Scroll to feedback panel', 'Feedback cards visible')
    guide.add_step(2, 'Click "Add Custom Feedback" button', 'Modal form appears')
    guide.add_step(3, 'Verify form has fields: Type, Category, Description, Suggestion', 'All fields visible')
    guide.add_step(4, 'Fill in Type: "Enhancement"', 'Field populated')
    guide.add_step(5, 'Fill in Category: "Process Improvement"', 'Field populated')
    guide.add_step(6, 'Fill in Description: "Consider adding stakeholder communication timeline"', 'Field populated')
    guide.add_step(7, 'Fill in Suggestion: "Add section detailing when each stakeholder was contacted"', 'Field populated')
    guide.add_step(8, 'Click "Submit" or "Add Feedback" button', 'Modal closes')
    guide.add_step(9, 'Scroll to feedback panel', 'New feedback card appears at bottom')
    guide.add_step(10, 'Verify card has "Custom" badge', 'Badge visible distinguishing from AI feedback')
    guide.add_expected_log('Custom feedback added')
    guide.add_expected_log('Feedback ID: ...')
    guide.add_backend_call('POST', '/add_user_feedback', {'type': '...', 'category': '...', 'description': '...', 'suggestion': '...'})
    guide.add_note('Custom feedback should be distinguishable from AI feedback')
    guide.complete_test()

    # TEST 8: Chat - Send Message
    guide.start_test(
        'TEST-008',
        'Chat Assistant - Send Message',
        'Test asking questions about current section'
    )
    guide.add_step(1, 'Locate chat panel (right side or bottom)', 'Chat interface visible')
    guide.add_step(2, 'Type question: "What Hawkeye checkpoints apply to Executive Summary?"', 'Text appears in input field')
    guide.add_step(3, 'Press Enter key', 'Message appears in chat history')
    guide.add_step(4, 'Verify "Thinking..." indicator appears', 'Indicator visible with animated dots')
    guide.add_step(5, 'Wait for response (10-30 seconds)', 'Thinking indicator continues')
    guide.add_step(6, 'Verify response appears', 'AI message appears in chat')
    guide.add_step(7, 'Read response', 'Response is relevant to Executive Summary and mentions Hawkeye checkpoints')
    guide.add_expected_log('Chat message sent: ...')
    guide.add_expected_log('Task ID: ...')
    guide.add_expected_log('Chat response received')
    guide.add_backend_call('POST', '/chat', {'message': '...', 'session_id': '...', 'current_section': 'Executive Summary'})
    guide.add_backend_call('GET', '/task_status/{task_id}', None)
    guide.add_note('Response should be contextual to current section')
    guide.add_note('Chat history should persist during session')
    guide.complete_test()

    # TEST 9: Section Navigation - Next
    guide.start_test(
        'TEST-009',
        'Section Navigation - Next Button',
        'Test navigating to next section'
    )
    guide.add_step(1, 'Ensure on "Executive Summary" section', 'Section visible')
    guide.add_step(2, 'Locate "Next Section" button', 'Button visible in content area')
    guide.add_step(3, 'Click "Next Section" button', 'Loading spinner appears (if section not yet analyzed)')
    guide.add_step(4, 'Wait for section to load', 'Timeline of Events section appears')
    guide.add_step(5, 'Verify section content displays', 'Timeline text visible')
    guide.add_step(6, 'If first time viewing: wait for analysis', 'Feedback cards appear after 20-40 seconds')
    guide.add_expected_log('Navigating to next section')
    guide.add_expected_log('Loading section: Timeline of Events')
    guide.add_backend_call('POST', '/analyze_section', {'section_name': 'Timeline of Events'})
    guide.add_note('If section already analyzed, loads instantly from cache')
    guide.add_note('If new section, triggers analysis')
    guide.complete_test()

    # TEST 10: Section Navigation - Previous
    guide.start_test(
        'TEST-010',
        'Section Navigation - Previous Button',
        'Test navigating to previous section'
    )
    guide.add_step(1, 'Ensure on "Timeline of Events" section', 'Section visible')
    guide.add_step(2, 'Click "Previous Section" button', 'Section changes immediately')
    guide.add_step(3, 'Verify returns to "Executive Summary"', 'Executive Summary content visible')
    guide.add_step(4, 'Verify loads instantly', 'No loading spinner (cached)')
    guide.add_step(5, 'Verify previously accepted/rejected feedback states preserved', 'Green/red buttons still show previous states')
    guide.add_expected_log('Navigating to previous section')
    guide.add_expected_log('Loading cached section: Executive Summary')
    guide.add_note('Should load instantly from window.sectionData')
    guide.add_note('No backend call needed')
    guide.complete_test()

    # TEST 11: Statistics Panel
    guide.start_test(
        'TEST-011',
        'Statistics Panel - Real-time Updates',
        'Test statistics panel updates correctly'
    )
    guide.add_step(1, 'Locate statistics panel', 'Panel visible showing counts')
    guide.add_step(2, 'Note current values', 'Values recorded')
    guide.add_step(3, 'Accept a feedback item', 'Accept button turns green')
    guide.add_step(4, 'Check statistics panel', 'Accepted count increases by 1')
    guide.add_step(5, 'Reject a feedback item', 'Reject button turns red')
    guide.add_step(6, 'Check statistics panel', 'Rejected count increases by 1')
    guide.add_step(7, 'Analyze another section', 'Sections analyzed count increases')
    guide.add_expected_log('Statistics updated')
    guide.add_backend_call('GET', '/get_statistics?session_id=...', None)
    guide.add_note('Statistics should update in real-time')
    guide.complete_test()

    # TEST 12: Complete Review
    guide.start_test(
        'TEST-012',
        'Complete Review - Document Generation',
        'Test generating final document with accepted feedback'
    )
    guide.add_step(1, 'Analyze at least 2 sections', 'Multiple sections analyzed')
    guide.add_step(2, 'Accept at least 3 feedback items', 'Green checkmarks visible')
    guide.add_step(3, 'Reject at least 1 feedback item', 'Red X visible')
    guide.add_step(4, 'Locate "Complete Review" button', 'Button visible (should be enabled)')
    guide.add_step(5, 'Click "Complete Review" button', 'Confirmation modal appears')
    guide.add_step(6, 'Verify modal shows summary: X feedback items will be added', 'Count matches accepted items')
    guide.add_step(7, 'Click "Generate Document" button', 'Modal shows processing')
    guide.add_step(8, 'Wait for generation (5-15 seconds)', 'Progress indicator visible')
    guide.add_step(9, 'Verify download link appears', 'Link visible: "Download Reviewed Document"')
    guide.add_step(10, 'Click download link', 'File downloads to browser')
    guide.add_step(11, 'Open downloaded .docx in Microsoft Word', 'Document opens')
    guide.add_step(12, 'Check for comments in right margin', 'Comments visible with feedback text')
    guide.add_step(13, 'Verify only accepted feedback appears', 'Rejected feedback NOT in document')
    guide.add_expected_log('Complete review initiated')
    guide.add_expected_log('Generating document with X feedback items')
    guide.add_expected_log('Document generated: ...')
    guide.add_backend_call('POST', '/complete_review', {'session_id': '...', 'accepted_feedback': [...]})
    guide.add_note('CRITICAL: Only accepted feedback should appear in final document')
    guide.add_note('Comments should be in Word document margins, not inline')
    guide.complete_test()

    # TEST 13: Help System
    guide.start_test(
        'TEST-013',
        'Help System - Access Help',
        'Test help button and documentation'
    )
    guide.add_step(1, 'Locate "Help" or "?" button', 'Button visible in navigation')
    guide.add_step(2, 'Click help button', 'Help modal or panel opens')
    guide.add_step(3, 'Verify help content displays', 'Instructions visible')
    guide.add_step(4, 'Close help modal', 'Modal closes, returns to main interface')
    guide.add_note('Help should explain key features and workflow')
    guide.complete_test()

    # TEST 14: Error Handling - Invalid File
    guide.start_test(
        'TEST-014',
        'Error Handling - Invalid File Type',
        'Test error message for invalid file upload'
    )
    guide.add_step(1, 'Click "Choose File"', 'File picker opens')
    guide.add_step(2, 'Select a .pdf or .txt file', 'Filename appears')
    guide.add_step(3, 'Click "Upload & Start Analysis"', 'Error notification appears')
    guide.add_step(4, 'Verify error message: "Invalid file type. Please upload .docx file"', 'Clear error message')
    guide.add_expected_log('Upload error: Invalid file type')
    guide.add_note('Only .docx files should be accepted')
    guide.complete_test()

    # TEST 15: Multiple Sections - Full Workflow
    guide.start_test(
        'TEST-015',
        'Full Workflow - All 4 Sections',
        'Test analyzing all sections sequentially'
    )
    guide.add_step(1, 'Upload document', 'Upload succeeds')
    guide.add_step(2, 'Analyze Executive Summary', 'Feedback appears')
    guide.add_step(3, 'Accept 2 feedback items', 'Green checkmarks')
    guide.add_step(4, 'Click Next → Timeline of Events', 'Section analyzes')
    guide.add_step(5, 'Accept 1 feedback item', 'Green checkmark')
    guide.add_step(6, 'Click Next → Root Cause Analysis', 'Section analyzes')
    guide.add_step(7, 'Reject 1 feedback item', 'Red X')
    guide.add_step(8, 'Click Next → Preventative Actions', 'Section analyzes')
    guide.add_step(9, 'Accept 2 feedback items', 'Green checkmarks')
    guide.add_step(10, 'Verify statistics: 4 sections analyzed, 5 accepted, 1 rejected', 'Stats correct')
    guide.add_step(11, 'Complete review and download document', 'Document downloads')
    guide.add_note('This tests the complete user journey')
    guide.add_note('Verify state persists across sections')
    guide.complete_test()

    return guide

# Generate the guide
guide = generate_test_guide()
html_content = guide.generate_html_guide()

# Save to file
with open('E2E_TESTING_GUIDE.html', 'w') as f:
    f.write(html_content)

print("✅ E2E Testing Guide generated: E2E_TESTING_GUIDE.html")
print(f"📊 Total tests: {len(guide.test_results)}")
print("\n🌐 Open E2E_TESTING_GUIDE.html in your browser to see the guide")
print("\n📋 Test categories:")
print("   - Document Upload: 1 test")
print("   - Section Analysis: 1 test")
print("   - Feedback Management: 3 tests")
print("   - Text Highlighting: 2 tests")
print("   - Chat: 1 test")
print("   - Navigation: 2 tests")
print("   - Statistics: 1 test")
print("   - Document Generation: 1 test")
print("   - Help System: 1 test")
print("   - Error Handling: 1 test")
print("   - Full Workflow: 1 test")
