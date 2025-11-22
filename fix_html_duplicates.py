#!/usr/bin/env python3
"""
Script to remove duplicate JavaScript functions from enhanced_index.html
and add descriptive comments to each function.
"""

import re
from collections import OrderedDict

# Function names and their descriptions
FUNCTION_DESCRIPTIONS = {
    'showNotification': 'Display a notification message to the user with specified type (success, error, info, warning)',
    'cancelAnalysis': 'Cancel the ongoing document analysis and reset the UI to initial state',
    'setupEventListeners': 'Initialize all event listeners for file inputs, section selection, and UI interactions',
    'setupKeyboardShortcuts': 'Set up keyboard shortcuts for navigation and quick actions (n, p, a, r, f, c, d, 1, 2, ?)',
    'setupDragAndDrop': 'Configure drag-and-drop functionality for file upload area',
    'ensureCustomFeedbackVisible': 'Ensure the custom feedback panel is visible in the UI',
    'showShortcuts': 'Display the keyboard shortcuts modal to help users learn hotkeys',
    'closeModal': 'Close a modal dialog by its ID',
    'showModal': 'Display a modal dialog with specified ID, title, and content',
    'handleAnalysisFileUpload': 'Handle the file selection event for analysis document upload',
    'handleGuidelinesFileUpload': 'Handle the file selection event for guidelines document upload',
    'showProgress': 'Display the progress modal with a status message',
    'showDocumentProgress': 'Show the document analysis progress panel',
    'hideDocumentProgress': 'Hide the document analysis progress panel',
    'updateDocumentProgress': 'Update the progress bar and section status for document analysis',
    'updateDocumentProgressMessage': 'Update the progress modal title and description text',
    'rotateLoadingMedia': 'Rotate through loading GIFs, jokes, and math facts during analysis',
    'resetHighlightingTutorial': 'Reset the text highlighting tutorial state',
    'showTutorial': 'Display the interactive tutorial modal for new users',
    'showFAQ': 'Show the frequently asked questions modal',
    'showPatterns': 'Display pattern analysis functionality (currently not implemented)',
    'showMainContent': 'Show the main content area after successful document upload and analysis',
    'loadSection': 'Load and display a specific document section by index',
    'updateStatistics': 'Refresh and update the statistics display with current feedback counts',
    'showLearning': 'Display the learning insights and AI feedback patterns',
    'checkSessionStatus': 'Check if there is an active analysis session',
    'setTestSession': 'Set up a test session for development/debugging purposes',
    'testCompleteReview': 'Test the complete review functionality',
    'testS3Connection': 'Test the connection to AWS S3 for document storage',
    'resetSession': 'Reset the current session and clear all analysis data',
    'completeReview': 'Finalize the document review and prepare the final output',
    'completeReviewWithS3Export': 'Complete review and export results to AWS S3',
    'completeReviewLocalOnly': 'Complete review without S3 export (local download only)',
    'performCompleteReview': 'Execute the complete review process with optional S3 export',
    'downloadFinalDocument': 'Download the final reviewed document with applied feedback',
    'showS3SuccessPopup': 'Display success modal after successful S3 upload',
    'startNewReview': 'Start a new document review session',
    'confirmFinalDownload': 'Confirm and execute the final document download',
    'showAddCommentDialog': 'Show dialog to add a comment to highlighted text',
    'showUpdateCommentsDialog': 'Show dialog to update existing comments',
    'clearAllHighlights': 'Remove all text highlights from the current section',
    'addQuickCustomFeedback': 'Add custom feedback quickly without opening full dialog',
    'addChatMessage': 'Add a message to the chat interface (user or AI)',
    'formatAIResponse': 'Format AI response text with proper markdown and styling',
    'showThinkingIndicator': 'Show the "AI is thinking" animated indicator',
    'hideThinkingIndicator': 'Hide the "AI is thinking" animated indicator',
    'sendChatMessage': 'Send a chat message to the AI and handle the response',
    'handleChatKeyPress': 'Handle Enter key press in chat input to send messages',
    'pollTaskStatus': 'Poll the server for async task completion status',
    'pollAnalysisTask': 'Poll the server for section analysis task completion',
    'startAnalysis': 'Start the document analysis process',
    'handleFileSelection': 'Handle file selection and determine if guidelines should be used',
    'showGuidelinesPreferenceModal': 'Show modal to ask user about guidelines preference',
    'useGuidelinesPreference': 'Apply user\'s guidelines preference selection',
    'uploadAndAnalyze': 'Upload files to server and initiate analysis',
    'populateSectionSelect': 'Populate the section dropdown with document sections',
    'showSimpleLoadingModal': 'Show a simple loading modal for section analysis',
    'hideSimpleLoadingModal': 'Hide the simple loading modal',
    'startSectionAnalysis': 'Start analyzing a specific document section',
    'showStartAnalysisButton': 'Display the start analysis button for a section',
    'showAnalysisInstruction': 'Show instructions for starting section analysis',
    'saveCurrentSectionHighlights': 'Save text highlights for the current section',
    'restoreSectionHighlights': 'Restore previously saved highlights for a section',
    'restoreHighlight': 'Restore a single highlight with its styling and data',
    'loadUserFeedbackForSection': 'Load user-added feedback items for a specific section',
    'displaySectionContent': 'Display the content of a document section',
    'expandDocument': 'Expand the document panel to full width',
    'selectFeedback': 'Select a feedback item for review',
    'acceptFeedback': 'Mark a feedback item as accepted',
    'rejectFeedback': 'Mark a feedback item as rejected',
    'updateFeedbackStatus': 'Update the status of a feedback item in the backend',
    'revertFeedback': 'Revert a feedback item to pending status',
    'zoomIn': 'Increase document zoom level',
    'zoomOut': 'Decrease document zoom level',
    'resetZoom': 'Reset document zoom to 100%',
    'applyZoom': 'Apply the current zoom level to document content',
    'addCustomFeedback': 'Add custom feedback to the current section',
    'editUserFeedback': 'Edit an existing user-added feedback item',
    'saveEditedFeedback': 'Save changes to an edited feedback item',
    'deleteUserFeedback': 'Delete a user-added feedback item',
    'showUserFeedbackManager': 'Show the user feedback management panel',
    'updateFeedbackManagerList': 'Refresh the list in feedback manager',
    'exportUserFeedbackCSV': 'Export user feedback as CSV file',
    'clearAllUserFeedback': 'Clear all user-added feedback items',
    'refreshUserFeedbackManager': 'Refresh the user feedback manager display',
    'editUserFeedbackInManager': 'Edit feedback from the manager panel',
    'deleteUserFeedbackFromManager': 'Delete feedback from the manager panel',
    'exportAllUserFeedback': 'Export all user feedback in specified format (JSON/CSV)',
    'saveHighlightedText': 'Save highlighted text selection',
    'applyHighlight': 'Apply highlight styling to selected text',
    'enableTextSelection': 'Enable text selection mode for highlighting',
    'handleTextSelection': 'Handle text selection events',
    'handleHighlightClick': 'Handle click events on highlighted text',
    'showHighlightOptionsDialog': 'Show options dialog for a highlighted section',
    'removeHighlight': 'Remove a specific highlight by ID',
    'showHighlightCommentDialog': 'Show dialog to add/edit comment on a highlight',
    'saveHighlightComment': 'Save a comment for a highlighted text section',
    'updateRiskIndicator': 'Update the risk level indicator based on feedback analysis',
    'displayStatistics': 'Display analysis statistics in the UI',
    'showStatisticBreakdown': 'Show detailed breakdown of a specific statistic',
    'generateEnhancedBreakdown': 'Generate enhanced breakdown HTML for statistics',
    'previousSection': 'Navigate to the previous document section',
    'nextSection': 'Navigate to the next document section',
    'switchTab': 'Switch between feedback and chat tabs',
    'toggleAIPrismChat': 'Toggle the AI chat panel visibility',
    'changeAIModel': 'Change the AI model used for analysis',
    'testAIModel': 'Test the currently selected AI model',
    'regenerateResponse': 'Regenerate the last AI response',
    'downloadDocument': 'Download the analyzed document',
    'downloadStatistics': 'Download analysis statistics in various formats',
    'downloadStatsFormat': 'Download statistics in a specific format (JSON/CSV/TXT)',
    'exportPatterns': 'Export detected patterns from analysis',
    'refreshPatterns': 'Refresh the patterns display',
    'exportLearningData': 'Export learning insights and AI patterns',
    'refreshLearning': 'Refresh the learning insights display',
    'exportToS3': 'Export the final document to AWS S3',
    'showFinalReviewModal': 'Show the final review confirmation modal',
    'revertAllFeedback': 'Revert all feedback decisions to pending state',
    'updateFeedback': 'Update feedback and refresh statistics',
    'showDashboard': 'Show the analytics dashboard',
    'createDashboardCharts': 'Create charts for the dashboard',
    'drawPieChart': 'Draw a pie chart on canvas',
    'drawBarChart': 'Draw a bar chart on canvas',
    'generateDashboardHtml': 'Generate HTML for dashboard display',
    'downloadGuidelines': 'Download the guidelines document',
    'downloadUserFeedback': 'Download user-added feedback',
    'deleteDocument': 'Delete the current document from session',
    'updateSpecificFeedback': 'Update a specific feedback item',
    'reanalyzeAllSections': 'Re-analyze all document sections',
    'provideFeedbackOnTool': 'Provide feedback on the tool itself',
    'submitToolFeedback': 'Submit tool feedback to the server',
    'exportChatHistory': 'Export the chat conversation history',
    'exportStatistics': 'Export statistics in specified format',
    'hideProgress': 'Hide the progress modal',
    'startMediaRotation': 'Start rotating loading media content',
    'stopMediaRotation': 'Stop rotating loading media content',
    'rotateMedia': 'Rotate to next media content item',
    'toggleGraphics': 'Toggle graphics/animations on or off'
}

def extract_functions(content):
    """Extract all function definitions with their full content."""
    # Pattern to match function definitions
    pattern = r'(function\s+(\w+)\s*\([^)]*\)\s*\{)'

    functions = OrderedDict()
    matches = list(re.finditer(pattern, content))

    for i, match in enumerate(matches):
        func_name = match.group(2)
        start_pos = match.start()

        # Find the end of this function by counting braces
        brace_count = 0
        in_function = False
        func_start = match.end() - 1  # Start from the opening brace

        for j in range(func_start, len(content)):
            char = content[j]
            if char == '{':
                brace_count += 1
                in_function = True
            elif char == '}':
                brace_count -= 1
                if in_function and brace_count == 0:
                    # Found the end of function
                    func_content = content[start_pos:j+1]

                    # Only keep the first occurrence of each function
                    if func_name not in functions:
                        functions[func_name] = {
                            'content': func_content,
                            'start': start_pos,
                            'end': j+1
                        }
                    break

    return functions

def add_comment_to_function(func_content, func_name):
    """Add a descriptive comment at the start of a function."""
    description = FUNCTION_DESCRIPTIONS.get(func_name, f'Handle {func_name} functionality')

    # Find the opening brace
    match = re.search(r'(function\s+\w+\s*\([^)]*\)\s*\{)', func_content)
    if match:
        before_brace = match.group(1)
        after_brace = func_content[match.end():]

        # Add comment right after the opening brace
        comment = f'\n            // Purpose: {description}\n'
        return before_brace + comment + after_brace

    return func_content

def main():
    input_file = '/Users/abhsatsa/Documents/risk stuff/tool/tara2/templates/enhanced_index.html'
    output_file = '/Users/abhsatsa/Documents/risk stuff/tool/tara2/templates/enhanced_index_final.html'

    print("Reading file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("Extracting functions...")
    functions = extract_functions(content)

    print(f"Found {len(functions)} unique functions")
    print("Functions found:", ', '.join(functions.keys()))

    # Find all duplicate function definitions to remove
    print("\nFinding duplicates...")
    pattern = r'function\s+(\w+)\s*\([^)]*\)\s*\{'
    all_matches = list(re.finditer(pattern, content))

    seen_functions = {}
    duplicates_to_remove = []

    for match in all_matches:
        func_name = match.group(1)
        if func_name in seen_functions:
            # This is a duplicate
            duplicates_to_remove.append((func_name, match.start()))
        else:
            seen_functions[func_name] = match.start()

    print(f"Found {len(duplicates_to_remove)} duplicate function definitions")

    # Remove duplicates from end to start to preserve positions
    duplicates_to_remove.sort(key=lambda x: x[1], reverse=True)

    for func_name, start_pos in duplicates_to_remove:
        # Find the end of this function
        brace_count = 0
        in_function = False

        # Find the opening brace
        for j in range(start_pos, len(content)):
            if content[j] == '{':
                func_start = j
                break

        for j in range(func_start, len(content)):
            char = content[j]
            if char == '{':
                brace_count += 1
                in_function = True
            elif char == '}':
                brace_count -= 1
                if in_function and brace_count == 0:
                    # Found the end, remove this function
                    end_pos = j + 1
                    print(f"Removing duplicate: {func_name} at position {start_pos}-{end_pos}")
                    content = content[:start_pos] + content[end_pos:]
                    break

    # Now add comments to remaining functions
    print("\nAdding descriptive comments to functions...")
    for func_name in FUNCTION_DESCRIPTIONS.keys():
        # Find the function in content
        pattern = rf'(function\s+{func_name}\s*\([^)]*\)\s*\{{)'
        match = re.search(pattern, content)

        if match:
            # Find the full function
            start_pos = match.start()
            func_start = match.end() - 1
            brace_count = 0
            in_function = False

            for j in range(func_start, len(content)):
                char = content[j]
                if char == '{':
                    brace_count += 1
                    in_function = True
                elif char == '}':
                    brace_count -= 1
                    if in_function and brace_count == 0:
                        end_pos = j + 1
                        func_content = content[start_pos:end_pos]

                        # Check if comment already exists
                        if '// Purpose:' not in func_content:
                            new_func_content = add_comment_to_function(func_content, func_name)
                            content = content[:start_pos] + new_func_content + content[end_pos:]
                            print(f"Added comment to: {func_name}")
                        break

    print("\nWriting fixed file...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ Done! Fixed file saved to: {output_file}")
    print(f"Original file size: {len(content)} bytes")

if __name__ == '__main__':
    main()
