// Global Function Fixes for AI-Prism
// This file ensures all onclick handler functions are globally accessible
// Fixes Issues #1-4 reported by user

console.log('🔧 Loading global function fixes...');

// ============================================================================
// FIX #1: Accept/Reject Functionality
// ============================================================================
// ROOT CAUSE: acceptFeedback and rejectFeedback were not attached to window object
// SOLUTION: Attach them globally so onclick handlers can find them

window.acceptFeedback = function(feedbackId, sectionName) {
    console.log('✅ Accept feedback called:', feedbackId, sectionName);

    // Get currentSession from multiple sources (same pattern as chat fix)
    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session found. Please upload a document first.', 'error');
        return;
    }

    fetch('/accept_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            section_name: sectionName,
            feedback_id: feedbackId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('✅ Feedback accepted!', 'success');

            // Log activity for real-time display (Fix #4)
            if (window.logAIFeedbackActivity) {
                window.logAIFeedbackActivity(feedbackId, 'accepted');
            }

            // Refresh the section to update UI
            if (typeof loadSection === 'function' && typeof currentSectionIndex !== 'undefined') {
                loadSection(currentSectionIndex);
            } else if (typeof window.loadSection === 'function' && typeof window.currentSectionIndex !== 'undefined') {
                window.loadSection(window.currentSectionIndex);
            }

            // Update statistics if function exists
            if (typeof updateStatistics === 'function') {
                updateStatistics();
            } else if (typeof window.updateStatistics === 'function') {
                window.updateStatistics();
            }

            // Update real-time logs
            if (window.updateRealTimeFeedbackLogs) {
                window.updateRealTimeFeedbackLogs();
            }
        } else {
            showNotification('❌ Failed to accept feedback: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Accept feedback error:', error);
        showNotification('❌ Error: ' + error.message, 'error');
    });
};

window.rejectFeedback = function(feedbackId, sectionName) {
    console.log('❌ Reject feedback called:', feedbackId, sectionName);

    // Get currentSession from multiple sources
    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session found. Please upload a document first.', 'error');
        return;
    }

    fetch('/reject_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            section_name: sectionName,
            feedback_id: feedbackId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('❌ Feedback rejected!', 'info');

            // Log activity for real-time display (Fix #4)
            if (window.logAIFeedbackActivity) {
                window.logAIFeedbackActivity(feedbackId, 'rejected');
            }

            // Refresh the section to update UI
            if (typeof loadSection === 'function' && typeof currentSectionIndex !== 'undefined') {
                loadSection(currentSectionIndex);
            } else if (typeof window.loadSection === 'function' && typeof window.currentSectionIndex !== 'undefined') {
                window.loadSection(window.currentSectionIndex);
            }

            // Update statistics if function exists
            if (typeof updateStatistics === 'function') {
                updateStatistics();
            } else if (typeof window.updateStatistics === 'function') {
                window.updateStatistics();
            }

            // Update real-time logs
            if (window.updateRealTimeFeedbackLogs) {
                window.updateRealTimeFeedbackLogs();
            }
        } else {
            showNotification('❌ Failed to reject feedback: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Reject feedback error:', error);
        showNotification('❌ Error: ' + error.message, 'error');
    });
};

// ============================================================================
// FIX #2: Text Highlighting Functionality
// ============================================================================
// ROOT CAUSE 1: setHighlightColor uses 'event' parameter but doesn't receive it
// ROOT CAUSE 2: Functions not attached to window object
// SOLUTION: Fix parameter and attach globally

window.setHighlightColor = function(color, event) {
    console.log('🎨 Setting highlight color:', color);

    window.currentHighlightColor = color;

    // Update button states
    document.querySelectorAll('.highlight-tools button').forEach(btn => {
        btn.style.border = '1px solid #ddd';
    });

    // Fix: Check if event exists before using it
    if (event && event.target) {
        event.target.style.border = '3px solid #333';
    }

    showNotification(`🎨 Highlight color set to ${color}. Select text to highlight.`, 'info');

    // Enable text selection
    if (window.enableTextSelection) {
        window.enableTextSelection();
    }
};

window.saveHighlightedText = function() {
    console.log('💾 Saving highlighted text...');

    if (!window.currentSelectedText || !window.currentSelectedRange) {
        showNotification('No text selected. Please select text first.', 'error');
        return;
    }

    const highlightId = `highlight_${++window.highlightCounter}_${Date.now()}`;

    try {
        // Create highlight span
        const highlightSpan = document.createElement('span');
        highlightSpan.className = 'text-highlight';
        highlightSpan.id = highlightId;
        highlightSpan.style.backgroundColor = window.currentHighlightColor || 'yellow';
        highlightSpan.style.padding = '2px 4px';
        highlightSpan.style.borderRadius = '3px';
        highlightSpan.style.cursor = 'pointer';
        highlightSpan.style.border = '1px solid rgba(0,0,0,0.2)';
        highlightSpan.title = 'Click to add comment or view existing comments';

        // Wrap the selected text
        window.currentSelectedRange.surroundContents(highlightSpan);

        // Store highlight data
        if (!window.highlightedTexts) {
            window.highlightedTexts = [];
        }

        const highlightData = {
            id: highlightId,
            text: window.currentSelectedText,
            color: window.currentHighlightColor || 'yellow',
            section: window.sections && window.currentSectionIndex >= 0 ? window.sections[window.currentSectionIndex] : 'Unknown',
            timestamp: new Date().toISOString(),
            comments: []
        };

        window.highlightedTexts.push(highlightData);

        // Clear selection
        window.getSelection().removeAllRanges();
        window.currentSelectedText = '';
        window.currentSelectedRange = null;

        // Hide save button
        const saveBtn = document.getElementById('saveHighlightBtn');
        if (saveBtn) saveBtn.style.display = 'none';

        // Show comment dialog immediately
        if (window.showHighlightCommentDialog) {
            window.showHighlightCommentDialog(highlightId, highlightData.text);
        }

        showNotification(`✅ Text highlighted with ${highlightData.color}! Add your comment.`, 'success');

    } catch (error) {
        console.error('Highlighting error:', error);
        showNotification('Could not highlight this text. Try selecting simpler text.', 'error');
    }
};

window.clearHighlights = function() {
    console.log('🧹 Clearing all highlights...');

    if (confirm('Are you sure you want to clear all highlights and their comments? This will also remove the associated feedback from your custom feedback list.')) {
        const docContent = document.getElementById('documentContent');
        if (!docContent) {
            showNotification('Document content not found', 'error');
            return;
        }

        const highlights = docContent.querySelectorAll('.text-highlight');

        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
            parent.normalize();
        });

        // Clear highlight data
        const currentSectionName = window.sections && window.currentSectionIndex >= 0 ?
            window.sections[window.currentSectionIndex] : null;
        if (!currentSectionName) return;

        const highlightIds = window.highlightedTexts ?
            window.highlightedTexts.filter(h => h.section === currentSectionName).map(h => h.id) : [];

        // Remove highlights for current section
        if (window.highlightedTexts) {
            window.highlightedTexts = window.highlightedTexts.filter(h => h.section !== currentSectionName);
        }

        // Remove highlight-related user feedback from display
        highlightIds.forEach(highlightId => {
            const feedbackElements = document.querySelectorAll(`[id*="${highlightId}"]`);
            feedbackElements.forEach(el => el.remove());
        });

        // Remove from user feedback history
        if (window.userFeedbackHistory) {
            window.userFeedbackHistory = window.userFeedbackHistory.filter(item =>
                !(item.section === currentSectionName && item.highlight_id)
            );
        }

        // Clear from session storage
        sessionStorage.removeItem(`highlights_${currentSectionName}`);

        // Update displays
        if (typeof updateAllCustomFeedbackList === 'function') {
            updateAllCustomFeedbackList();
        } else if (typeof window.updateAllCustomFeedbackList === 'function') {
            window.updateAllCustomFeedbackList();
        }

        if (typeof updateStatistics === 'function') {
            updateStatistics();
        } else if (typeof window.updateStatistics === 'function') {
            window.updateStatistics();
        }

        showNotification('🧹 All highlights and associated comments cleared!', 'success');
    }
};

// ============================================================================
// FIX #3: Custom Comments Functionality
// ============================================================================
// ROOT CAUSE: Custom feedback functions not attached to window object
// SOLUTION: Attach them globally

window.addCustomToAI = function(aiId, event) {
    console.log('✨ Adding custom to AI:', aiId);

    if (event) event.stopPropagation();

    const customDiv = document.getElementById(`custom-${aiId}`);
    if (!customDiv) {
        console.warn('Custom div not found for AI:', aiId);
        return;
    }

    if (customDiv.style.display === 'none' || customDiv.style.display === '') {
        // Hide all other custom forms
        document.querySelectorAll('.ai-custom-feedback').forEach(div => {
            div.style.display = 'none';
        });
        customDiv.style.display = 'block';

        // Focus on the description textarea
        const descTextarea = document.getElementById(`aiCustomDesc-${aiId}`);
        if (descTextarea) {
            setTimeout(() => descTextarea.focus(), 100);
        }
    } else {
        customDiv.style.display = 'none';
    }
};

window.cancelAICustom = function(aiId) {
    console.log('❌ Canceling AI custom:', aiId);

    const customDiv = document.getElementById(`custom-${aiId}`);
    const descTextarea = document.getElementById(`aiCustomDesc-${aiId}`);

    if (customDiv) customDiv.style.display = 'none';
    if (descTextarea) descTextarea.value = '';
};

window.saveAICustomFeedback = function(aiId) {
    console.log('💾 Saving AI custom feedback:', aiId);

    const type = document.getElementById(`aiCustomType-${aiId}`)?.value;
    const category = document.getElementById(`aiCustomCategory-${aiId}`)?.value;
    const description = document.getElementById(`aiCustomDesc-${aiId}`)?.value.trim();

    if (!description) {
        showNotification('Please enter your custom feedback', 'error');
        return;
    }

    // Ensure global variables exist
    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session found', 'error');
        return;
    }

    if (!window.sections || typeof window.currentSectionIndex === 'undefined' || window.currentSectionIndex < 0) {
        showNotification('No section selected', 'error');
        return;
    }

    // Find the AI feedback item for reference
    let aiItem = null;
    let aiReference = 'AI Suggestion';

    try {
        if (window.sectionData && window.sections[window.currentSectionIndex]) {
            const sectionName = window.sections[window.currentSectionIndex];
            if (window.sectionData[sectionName] && window.sectionData[sectionName].feedback) {
                aiItem = window.sectionData[sectionName].feedback.find(item => item.id === aiId);
                if (aiItem) {
                    aiReference = `${aiItem.type}: ${aiItem.description.substring(0, 50)}...`;
                }
            }
        }
    } catch (error) {
        console.warn('Error finding AI item reference:', error);
    }

    // Create the feedback item for immediate local logging
    const feedbackItem = {
        type: type,
        category: category,
        description: description,
        section: window.sections[window.currentSectionIndex],
        timestamp: new Date().toISOString(),
        session_id: sessionId,
        user_created: true,
        ai_reference: aiReference,
        ai_id: aiId,
        id: `ai_custom_${aiId}_${Date.now()}`,
        risk_level: type === 'critical' ? 'High' : type === 'important' ? 'Medium' : 'Low'
    };

    // Add to local history immediately for live logging
    if (!window.userFeedbackHistory) {
        window.userFeedbackHistory = [];
    }
    window.userFeedbackHistory.push(feedbackItem);

    fetch('/add_custom_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            section_name: window.sections[window.currentSectionIndex],
            type: type,
            category: category,
            description: description,
            ai_reference: aiReference,
            ai_id: aiId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('✨ Custom feedback added to AI suggestion!', 'success');

            // Update the feedback item with server data if available
            if (data.feedback_item && data.feedback_item.id) {
                feedbackItem.id = data.feedback_item.id;
                // Update the item in history
                const index = window.userFeedbackHistory.findIndex(item =>
                    item.timestamp === feedbackItem.timestamp && item.ai_id === aiId
                );
                if (index !== -1) {
                    window.userFeedbackHistory[index] = feedbackItem;
                }
            }

            // Display the user feedback immediately in current section
            if (window.displayUserFeedback) {
                window.displayUserFeedback(feedbackItem);
            }

            // Hide the custom form after successful save
            window.cancelAICustom(aiId);

            // Update statistics
            if (typeof updateStatistics === 'function') {
                updateStatistics();
            } else if (typeof window.updateStatistics === 'function') {
                window.updateStatistics();
            }

            // Update all custom feedback list
            if (window.updateAllCustomFeedbackList) {
                window.updateAllCustomFeedbackList();
            }

            // Trigger real-time logs update (Fix #4)
            if (window.updateRealTimeFeedbackLogs) {
                window.updateRealTimeFeedbackLogs();
            }

            console.log('✅ AI Custom feedback added and logged:', feedbackItem);
        } else {
            // Remove from local history if server failed
            window.userFeedbackHistory = window.userFeedbackHistory.filter(item => item.id !== feedbackItem.id);
            showNotification(data.error || 'Failed to add custom feedback to AI suggestion', 'error');
        }
    })
    .catch(error => {
        // Remove from local history if network failed
        window.userFeedbackHistory = window.userFeedbackHistory.filter(item => item.id !== feedbackItem.id);
        showNotification('Failed to add custom feedback: ' + error.message, 'error');
        console.error('AI Custom feedback error:', error);
    });
};

// ============================================================================
// FIX #4: Real-Time Feedback Display
// ============================================================================
// NOTE: The display functions (displayUserFeedback, updateRealTimeFeedbackLogs, etc.)
// are already properly attached to window in user_feedback_management.js
// The issue was that accept/reject wasn't working (Fix #1), so no activities were logged
// Now that accept/reject work, the real-time display should automatically work!

// Add helper to ensure real-time logs update on any feedback action
function ensureRealTimeLogsUpdate() {
    if (window.updateRealTimeFeedbackLogs) {
        // Small delay to ensure all updates are processed
        setTimeout(() => {
            window.updateRealTimeFeedbackLogs();
        }, 100);
    }
}

// ============================================================================
// Initialize and Log
// ============================================================================

console.log('✅ Global function fixes loaded successfully!');
console.log('   - acceptFeedback: ', typeof window.acceptFeedback);
console.log('   - rejectFeedback: ', typeof window.rejectFeedback);
console.log('   - setHighlightColor: ', typeof window.setHighlightColor);
console.log('   - saveHighlightedText: ', typeof window.saveHighlightedText);
console.log('   - clearHighlights: ', typeof window.clearHighlights);
console.log('   - addCustomToAI: ', typeof window.addCustomToAI);
console.log('   - saveAICustomFeedback: ', typeof window.saveAICustomFeedback);

// Initialize global variables if they don't exist
if (typeof window.currentHighlightColor === 'undefined') {
    window.currentHighlightColor = 'yellow';
}
if (typeof window.highlightedTexts === 'undefined') {
    window.highlightedTexts = [];
}
if (typeof window.highlightCounter === 'undefined') {
    window.highlightCounter = 0;
}
if (typeof window.currentSelectedText === 'undefined') {
    window.currentSelectedText = '';
}
if (typeof window.currentSelectedRange === 'undefined') {
    window.currentSelectedRange = null;
}
if (typeof window.userFeedbackHistory === 'undefined') {
    window.userFeedbackHistory = [];
}

console.log('🎉 All fixes applied! Issues #1-4 should now be resolved.');
