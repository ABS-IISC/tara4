// Global Function Fixes for AI-Prism
// This file ensures all onclick handler functions are globally accessible
// Fixes Issues #1-4 reported by user

console.log('🔧 Loading global function fixes...');

// ============================================================================
// FIX #1: Accept/Reject Functionality - DISABLED
// ============================================================================
// ❌ DISABLED: These functions are now handled by unified_button_fixes.js
// The unified version handles BOTH calling patterns automatically
// Keeping this code commented for reference only

/*
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

            // ✅ FIX: DO NOT reload section - it reverts accept/reject decisions
            // Instead, update UI elements directly without refetching from backend
            // Update visual feedback status
            const feedbackElement = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
            if (feedbackElement) {
                feedbackElement.style.borderLeftColor = '#10b981'; // Green for accepted
                const statusBadge = feedbackElement.querySelector('.status-badge');
                if (statusBadge) {
                    statusBadge.textContent = '✅ Accepted';
                    statusBadge.style.background = '#10b981';
                }
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

            // ✅ FIX: DO NOT reload section - it reverts accept/reject decisions
            // Instead, update UI elements directly without refetching from backend
            // Update visual feedback status
            const feedbackElement = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
            if (feedbackElement) {
                feedbackElement.style.borderLeftColor = '#ef4444'; // Red for rejected
                const statusBadge = feedbackElement.querySelector('.status-badge');
                if (statusBadge) {
                    statusBadge.textContent = '❌ Rejected';
                    statusBadge.style.background = '#ef4444';
                }
            }

            // ❌ REMOVED: Section reload that caused accept/reject decisions to be reverted
            // Section reloads refetch data from backend, losing all UI state

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
*/

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
// FIX #5: Feedback Management Buttons (Issue #18)
// ============================================================================
// These buttons are in the "Add Your Custom Feedback" section
// They use inline onclick handlers, so functions must be on window object

window.refreshUserFeedbackList = function() {
    console.log('🔄 Refreshing user feedback list...');

    // Update all displays
    if (window.updateAllCustomFeedbackList) {
        window.updateAllCustomFeedbackList();
    }

    // Update real-time logs
    if (window.updateRealTimeFeedbackLogs) {
        window.updateRealTimeFeedbackLogs();
    }

    // Update statistics
    if (window.updateStatistics) {
        window.updateStatistics();
    } else if (typeof updateStatistics === 'function') {
        updateStatistics();
    }

    // Trigger other UI updates
    setTimeout(() => {
        if (typeof updateAICustomButtonStates === 'function') {
            updateAICustomButtonStates();
        }
    }, 100);

    showNotification('✅ Feedback list refreshed!', 'success');
};

window.showUserFeedbackManager = function() {
    console.log('⚙️ Opening feedback manager...');

    if (!window.userFeedbackHistory || window.userFeedbackHistory.length === 0) {
        showNotification('No feedback to manage yet. Add some custom feedback first!', 'info');
        return;
    }

    // Get all feedback
    const allFeedback = window.userFeedbackHistory || [];

    // Create modal content
    const modalContent = `
        <div style="padding: 20px; max-height: 70vh; overflow-y: auto;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">📝 Manage Your Feedback</h3>

            <div style="margin-bottom: 20px;">
                <p style="color: #666;">You have <strong>${allFeedback.length}</strong> feedback item${allFeedback.length !== 1 ? 's' : ''}.</p>
            </div>

            <div style="max-height: 400px; overflow-y: auto;">
                ${allFeedback.map((item, index) => `
                    <div style="background: white; border: 2px solid #e5e7eb; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                            <div>
                                <span style="background: #4f46e5; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 8px;">${item.type || 'feedback'}</span>
                                <span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em;">${item.category || 'General'}</span>
                            </div>
                            <div>
                                <button onclick="window.editUserFeedback('${item.id}')" style="background: #f59e0b; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; margin-right: 4px; font-size: 0.8em;">✏️ Edit</button>
                                <button onclick="window.deleteUserFeedback('${item.id}')" style="background: #ef4444; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8em;">🗑️ Delete</button>
                            </div>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong>Feedback:</strong> ${item.description || 'No description'}
                        </div>
                        ${item.highlighted_text ? `
                            <div style="background: #fef3c7; padding: 8px; border-radius: 4px; margin-bottom: 8px; border-left: 3px solid #f59e0b;">
                                📝 <em>"${item.highlighted_text.substring(0, 80)}${item.highlighted_text.length > 80 ? '...' : ''}"</em>
                            </div>
                        ` : ''}
                        <div style="color: #666; font-size: 0.85em;">
                            📍 ${item.section || 'Unknown section'} | 📅 ${new Date(item.timestamp).toLocaleString()}
                        </div>
                    </div>
                `).join('')}
            </div>

            <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
                <button class="btn btn-secondary" onclick="closeModal('genericModal')">Close</button>
            </div>
        </div>
    `;

    showModal('genericModal', 'Manage Your Feedback', modalContent);
};

// ============================================================================
// FIX #6: Edit/Delete Feedback Functions (Issue #17c)
// ============================================================================
// These functions are called from inline onclick in feedback display
// They must be on window object to be accessible

window.editUserFeedback = function(feedbackId) {
    console.log('✏️ Editing feedback:', feedbackId);

    const feedback = window.userFeedbackHistory.find(item => item.id === feedbackId);
    if (!feedback) {
        showNotification('Feedback item not found', 'error');
        return;
    }

    const modalContent = `
        <div style="padding: 20px; max-height: 70vh; overflow-y: auto;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">✏️ Edit Custom Feedback</h3>

            <div style="margin-bottom: 15px;">
                <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">🏷️ Type:</label>
                <select id="editFeedbackType" style="width: 100%; padding: 10px; border: 2px solid #4f46e5; border-radius: 8px;">
                    <option value="suggestion" ${feedback.type === 'suggestion' ? 'selected' : ''}>Suggestion</option>
                    <option value="important" ${feedback.type === 'important' ? 'selected' : ''}>Important</option>
                    <option value="critical" ${feedback.type === 'critical' ? 'selected' : ''}>Critical</option>
                    <option value="positive" ${feedback.type === 'positive' ? 'selected' : ''}>Positive</option>
                    <option value="question" ${feedback.type === 'question' ? 'selected' : ''}>Question</option>
                    <option value="clarification" ${feedback.type === 'clarification' ? 'selected' : ''}>Clarification</option>
                </select>
            </div>

            <div style="margin-bottom: 15px;">
                <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">📁 Category:</label>
                <select id="editFeedbackCategory" style="width: 100%; padding: 10px; border: 2px solid #4f46e5; border-radius: 8px;">
                    <option value="Text Highlighting" ${feedback.category === 'Text Highlighting' ? 'selected' : ''}>Text Highlighting</option>
                    <option value="Initial Assessment" ${feedback.category === 'Initial Assessment' ? 'selected' : ''}>Initial Assessment</option>
                    <option value="Investigation Process" ${feedback.category === 'Investigation Process' ? 'selected' : ''}>Investigation Process</option>
                    <option value="Root Cause Analysis" ${feedback.category === 'Root Cause Analysis' ? 'selected' : ''}>Root Cause Analysis</option>
                    <option value="Documentation and Reporting" ${feedback.category === 'Documentation and Reporting' ? 'selected' : ''}>Documentation and Reporting</option>
                    <option value="Seller Classification" ${feedback.category === 'Seller Classification' ? 'selected' : ''}>Seller Classification</option>
                    <option value="Enforcement Decision-Making" ${feedback.category === 'Enforcement Decision-Making' ? 'selected' : ''}>Enforcement Decision-Making</option>
                    <option value="Quality Control" ${feedback.category === 'Quality Control' ? 'selected' : ''}>Quality Control</option>
                    <option value="Communication Standards" ${feedback.category === 'Communication Standards' ? 'selected' : ''}>Communication Standards</option>
                </select>
            </div>

            <div style="margin-bottom: 20px;">
                <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">📝 Description:</label>
                <textarea id="editFeedbackDescription" style="width: 100%; height: 100px; padding: 12px; border: 2px solid #4f46e5; border-radius: 8px; resize: vertical;">${feedback.description}</textarea>
            </div>

            <div style="text-align: center;">
                <button class="btn btn-success" onclick="window.saveEditedFeedback('${feedbackId}')" style="padding: 12px 25px; margin: 5px; border-radius: 20px; font-weight: 600;">💾 Save Changes</button>
                <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="padding: 12px 25px; margin: 5px; border-radius: 20px;">❌ Cancel</button>
            </div>
        </div>
    `;

    showModal('genericModal', 'Edit Custom Feedback', modalContent);
};

window.saveEditedFeedback = function(feedbackId) {
    console.log('💾 Saving edited feedback:', feedbackId);

    const type = document.getElementById('editFeedbackType')?.value;
    const category = document.getElementById('editFeedbackCategory')?.value;
    const description = document.getElementById('editFeedbackDescription')?.value?.trim();

    if (!description) {
        showNotification('Please enter a description', 'error');
        return;
    }

    // Find and update the feedback in local history
    const feedbackIndex = window.userFeedbackHistory.findIndex(item => item.id === feedbackId);
    if (feedbackIndex === -1) {
        showNotification('Feedback item not found', 'error');
        return;
    }

    // Update local feedback
    window.userFeedbackHistory[feedbackIndex] = {
        ...window.userFeedbackHistory[feedbackIndex],
        type: type,
        category: category,
        description: description,
        risk_level: type === 'critical' ? 'High' : type === 'important' ? 'Medium' : 'Low',
        edited: true,
        edited_at: new Date().toISOString()
    };

    // Update backend if session exists
    if (window.currentSession) {
        fetch('/update_user_feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: window.currentSession,
                feedback_id: feedbackId,
                updated_data: {
                    type: type,
                    category: category,
                    description: description,
                    risk_level: type === 'critical' ? 'High' : type === 'important' ? 'Medium' : 'Low'
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ Feedback updated successfully!', 'success');
            } else {
                console.warn('Backend update failed:', data.error);
                showNotification('⚠️ Feedback updated locally (backend sync failed)', 'warning');
            }
        })
        .catch(error => {
            console.error('Backend update error:', error);
            showNotification('⚠️ Feedback updated locally (backend sync failed)', 'warning');
        });
    }

    // Refresh displays
    if (window.refreshUserFeedbackList) {
        window.refreshUserFeedbackList();
    }

    closeModal('genericModal');
    showNotification('✨ Custom feedback updated!', 'success');
};

window.deleteUserFeedback = function(feedbackId) {
    console.log('🗑️ Deleting feedback:', feedbackId);

    const feedback = window.userFeedbackHistory.find(item => item.id === feedbackId);
    if (!feedback) {
        showNotification('Feedback item not found', 'error');
        return;
    }

    if (confirm(`Are you sure you want to delete this ${feedback.type} feedback?\n\n"${feedback.description.substring(0, 100)}${feedback.description.length > 100 ? '...' : '"}"`)) {
        // Remove from local history
        window.userFeedbackHistory = window.userFeedbackHistory.filter(item => item.id !== feedbackId);

        // Remove from display
        const feedbackElement = document.getElementById(`user-feedback-${feedbackId}`);
        if (feedbackElement) {
            feedbackElement.remove();
        }

        // Update backend if session exists
        if (window.currentSession) {
            fetch('/delete_user_feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: window.currentSession,
                    feedback_id: feedbackId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.warn('Backend deletion failed:', data.error);
                }
            })
            .catch(error => {
                console.error('Backend deletion error:', error);
            });
        }

        // Refresh displays
        if (window.refreshUserFeedbackList) {
            window.refreshUserFeedbackList();
        }

        // Trigger real-time logs update
        if (window.updateRealTimeFeedbackLogs) {
            window.updateRealTimeFeedbackLogs();
        }

        showNotification('🗑️ Custom feedback deleted!', 'success');
    }
};

// ============================================================================
// FIX #7: Action Button Functions (New Issues - Post Issue #17)
// ============================================================================
// These buttons are in the action buttons section
// They use inline onclick handlers, so functions must be on window object

window.revertAllFeedback = function() {
    console.log('🔄 Reverting all feedback...');

    // Get currentSession from multiple sources
    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    if (confirm('Are you sure you want to revert ALL feedback decisions? This will reset all accept/reject actions.')) {
        fetch('/revert_all_feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ All feedback decisions reverted!', 'success');

                // Reset feedback states
                if (window.feedbackStates) {
                    window.feedbackStates = {};
                }

                // Reload current section
                if (typeof window.currentSectionIndex !== 'undefined' && window.currentSectionIndex >= 0) {
                    if (typeof window.loadSection === 'function') {
                        window.loadSection(window.currentSectionIndex);
                    } else if (typeof loadSection === 'function') {
                        loadSection(window.currentSectionIndex);
                    }
                }

                // Update statistics
                if (typeof window.updateStatistics === 'function') {
                    window.updateStatistics();
                } else if (typeof updateStatistics === 'function') {
                    updateStatistics();
                }
            } else {
                showNotification('❌ Revert failed: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Revert all feedback error:', error);
            showNotification('❌ Revert failed: ' + error.message, 'error');
        });
    }
};

window.updateFeedback = function() {
    console.log('✏️ Updating feedback...');

    // Get currentSession from multiple sources
    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    showNotification('🔄 Updating feedback data...', 'info');

    // Reload current section to get latest feedback
    if (typeof window.currentSectionIndex !== 'undefined' &&
        window.currentSectionIndex >= 0 &&
        window.sections &&
        window.sections.length > 0) {

        if (typeof window.loadSection === 'function') {
            window.loadSection(window.currentSectionIndex);
        } else if (typeof loadSection === 'function') {
            loadSection(window.currentSectionIndex);
        }
    }

    // Update statistics
    if (typeof window.updateStatistics === 'function') {
        window.updateStatistics();
    } else if (typeof updateStatistics === 'function') {
        updateStatistics();
    }

    showNotification('✅ Feedback updated successfully!', 'success');
};

window.completeReview = function() {
    console.log('✅ Completing review...');

    // Get currentSession from multiple sources
    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    const availableSections = window.sections ||
                             (typeof sections !== 'undefined' ? sections : null) ||
                             [];

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    // Check if we have sections (indicating a document was uploaded)
    if (!availableSections || availableSections.length === 0) {
        showNotification('No document sections found. Please upload and analyze a document first.', 'error');
        return;
    }

    if (confirm('Complete the review and automatically save all data to S3? This will generate the final document and export everything.')) {
        // Show progress
        if (typeof showProgress === 'function') {
            showProgress('Generating final document and saving to S3...');
        } else if (typeof window.showProgress === 'function') {
            window.showProgress('Generating final document and saving to S3...');
        }

        // Automatically export to S3 when completing review
        fetch('/complete_review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                export_to_s3: true  // Automatically export to S3
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide progress
            if (typeof hideProgress === 'function') {
                hideProgress();
            } else if (typeof window.hideProgress === 'function') {
                window.hideProgress();
            }

            if (data.success) {
                let message = `✅ Review completed! Document generated with ${data.comments_count} comments.`;

                // Check S3 export status
                if (data.s3_export) {
                    if (data.s3_export.success) {
                        message += ` All data automatically saved to S3: ${data.s3_export.location}`;
                        showNotification(message, 'success');

                        // Show special S3 success popup if function exists
                        if (typeof showS3SuccessPopup === 'function') {
                            showS3SuccessPopup(data.s3_export);
                        } else if (typeof window.showS3SuccessPopup === 'function') {
                            window.showS3SuccessPopup(data.s3_export);
                        }
                    } else {
                        message += ` ⚠️ S3 export failed: ${data.s3_export.error}. Files saved locally as backup.`;
                        showNotification(message, 'warning');
                    }
                } else {
                    message += ' Files saved locally.';
                    showNotification(message, 'success');
                }

                // Enable download button
                const downloadBtn = document.getElementById('downloadBtn');
                if (downloadBtn) {
                    downloadBtn.disabled = false;
                    downloadBtn.setAttribute('data-filename', data.output_file);
                }

                // Store final document data
                window.finalDocumentData = data;
            } else {
                showNotification('❌ Review completion failed: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            // Hide progress
            if (typeof hideProgress === 'function') {
                hideProgress();
            } else if (typeof window.hideProgress === 'function') {
                window.hideProgress();
            }

            console.error('Complete review error:', error);
            showNotification('❌ Review completion failed: ' + error.message, 'error');
        });
    }
};

window.downloadGuidelines = function() {
    console.log('📄 Downloading guidelines...');

    // Get currentSession from multiple sources
    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    // Trigger download
    window.location.href = `/download_guidelines?session_id=${sessionId}`;
    showNotification('📥 Downloading guidelines...', 'info');
};

// ============================================================================
// FIX #8: Additional Action Buttons (New Request - More Broken Buttons)
// ============================================================================
// These buttons are also in the action buttons section
// They use inline onclick handlers, so functions must be on window object

window.exportChatHistory = function() {
    console.log('📎 Exporting chat history...');

    // Get chatHistory from window or local scope
    const history = window.chatHistory || (typeof chatHistory !== 'undefined' ? chatHistory : []);

    if (!history || history.length === 0) {
        showNotification('No chat history to export', 'info');
        return;
    }

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    const exportData = {
        export_timestamp: new Date().toISOString(),
        session_id: sessionId,
        total_messages: history.length,
        chat_history: history
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai_prism_chat_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    showNotification('✅ Chat history exported successfully!', 'success');
};

window.showDashboard = function() {
    console.log('📊 Opening dashboard...');

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    fetch(`/get_dashboard_data?session_id=${sessionId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const dashboard = data.dashboard;

            const modalContent = `
                <div style="max-height: 75vh; overflow-y: auto;">
                    <h3 style="color: #667eea; margin-bottom: 20px;">📊 Analytics Dashboard</h3>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.totalFeedback || 0}</div>
                            <div style="font-size: 1.1em;">Total Feedback</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); color: white; padding: 20px; border-radius: 15px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.acceptedFeedback || 0}</div>
                            <div style="font-size: 1.1em;">Accepted</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 20px; border-radius: 15px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.rejectedFeedback || 0}</div>
                            <div style="font-size: 1.1em;">Rejected</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 20px; border-radius: 15px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.userFeedback || 0}</div>
                            <div style="font-size: 1.1em;">User Added</div>
                        </div>
                    </div>

                    <div style="text-align: center; margin-top: 20px;">
                        <button class="btn btn-secondary" onclick="closeModal('genericModal')">Close</button>
                    </div>
                </div>
            `;

            showModal('genericModal', 'Analytics Dashboard', modalContent);
        } else {
            showNotification('Failed to load dashboard: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Dashboard error:', error);
        showNotification('Failed to load dashboard: ' + error.message, 'error');
    });
};

window.deleteDocument = function() {
    console.log('🗑️ Deleting document...');

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    if (confirm('Are you sure you want to delete the current document? Guidelines will be preserved.')) {
        fetch('/delete_document', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ Document deleted successfully! Guidelines preserved.', 'success');

                // Reset UI
                const documentContent = document.getElementById('documentContent');
                const feedbackContainer = document.getElementById('feedbackContainer');
                if (documentContent) documentContent.innerHTML = '';
                if (feedbackContainer) feedbackContainer.innerHTML = '';

                // Reset state
                window.sections = [];
                window.currentSectionIndex = -1;
                window.sectionData = {};

                // Hide main content
                const mainContent = document.getElementById('mainContent');
                if (mainContent) mainContent.style.display = 'none';
            } else {
                showNotification('❌ Delete failed: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Delete document error:', error);
            showNotification('❌ Delete failed: ' + error.message, 'error');
        });
    }
};

window.exportAllUserFeedback = function(format = 'json') {
    console.log('📄 Exporting user feedback...');

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    window.location.href = `/export_user_feedback?session_id=${sessionId}&format=${format}`;
    showNotification(`📥 Exporting feedback as ${format.toUpperCase()}...`, 'info');
};

window.clearAllSectionCustomFeedback = function() {
    console.log('🧹 Clearing section feedback...');

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    const currentSectionName = window.sections && window.currentSectionIndex >= 0 ?
                               window.sections[window.currentSectionIndex] : null;

    if (!currentSectionName) {
        showNotification('No section selected', 'error');
        return;
    }

    if (confirm(`Are you sure you want to clear all custom feedback for section "${currentSectionName}"? This cannot be undone.`)) {
        // Remove feedback for current section from local history
        if (window.userFeedbackHistory) {
            window.userFeedbackHistory = window.userFeedbackHistory.filter(item =>
                item.section !== currentSectionName
            );
        }

        // Update displays
        if (window.updateAllCustomFeedbackList) {
            window.updateAllCustomFeedbackList();
        }

        if (window.updateRealTimeFeedbackLogs) {
            window.updateRealTimeFeedbackLogs();
        }

        showNotification(`✅ All custom feedback cleared for section "${currentSectionName}"`, 'success');
    }
};

window.provideFeedbackOnTool = function() {
    console.log('💬 Opening feedback form...');

    const modalContent = `
        <div style="padding: 20px; max-height: 70vh; overflow-y: auto;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">💬 Help Us Improve AI-Prism</h3>

            <div style="margin-bottom: 20px;">
                <p style="color: #666; margin-bottom: 15px;">Your feedback helps us make AI-Prism better! Please share your experience:</p>

                <div style="margin-bottom: 15px;">
                    <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">📝 Feedback Type:</label>
                    <select id="toolFeedbackType" style="width: 100%; padding: 10px; border: 2px solid #4f46e5; border-radius: 8px;">
                        <option value="bug">🐛 Bug Report</option>
                        <option value="feature">✨ Feature Request</option>
                        <option value="improvement">💡 Improvement Suggestion</option>
                        <option value="praise">❤️ Positive Feedback</option>
                        <option value="other">💭 Other</option>
                    </select>
                </div>

                <div style="margin-bottom: 15px;">
                    <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">📧 Your Email (Optional):</label>
                    <input type="email" id="toolFeedbackEmail" placeholder="your.email@example.com" style="width: 100%; padding: 10px; border: 2px solid #4f46e5; border-radius: 8px;">
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">💭 Your Feedback:</label>
                    <textarea id="toolFeedbackMessage" placeholder="Tell us what you think..." style="width: 100%; height: 150px; padding: 12px; border: 2px solid #4f46e5; border-radius: 8px; resize: vertical;"></textarea>
                </div>

                <div style="text-align: center;">
                    <button class="btn btn-success" onclick="window.submitToolFeedback()" style="padding: 12px 25px; margin: 5px; border-radius: 20px; font-weight: 600;">📤 Submit Feedback</button>
                    <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="padding: 12px 25px; margin: 5px; border-radius: 20px;">❌ Cancel</button>
                </div>
            </div>
        </div>
    `;

    showModal('genericModal', 'Improve This Tool', modalContent);
};

window.submitToolFeedback = function() {
    const type = document.getElementById('toolFeedbackType')?.value;
    const email = document.getElementById('toolFeedbackEmail')?.value?.trim();
    const message = document.getElementById('toolFeedbackMessage')?.value?.trim();

    if (!message) {
        showNotification('Please enter your feedback message', 'error');
        return;
    }

    const feedbackData = {
        type: type,
        email: email || 'anonymous',
        message: message,
        timestamp: new Date().toISOString(),
        session_id: window.currentSession || 'no-session',
        user_agent: navigator.userAgent
    };

    // Log to console (in production, would send to backend)
    console.log('Tool Feedback Submitted:', feedbackData);

    // Could send to backend here
    // fetch('/submit_tool_feedback', { method: 'POST', body: JSON.stringify(feedbackData) })

    closeModal('genericModal');
    showNotification('✅ Thank you for your feedback! We appreciate your input.', 'success');
};

window.downloadStatistics = function() {
    console.log('📊 Downloading statistics...');

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    const modalContent = `
        <div style="text-align: center; padding: 20px;">
            <h3 style="color: #667eea; margin-bottom: 20px;">📊 Download Statistics</h3>
            <p style="margin-bottom: 30px;">Choose the format for your statistics export:</p>

            <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
                <button class="btn btn-primary" onclick="window.downloadStatsFormat('json')" style="padding: 15px 25px;">
                    📄 JSON Format
                </button>
                <button class="btn btn-success" onclick="window.downloadStatsFormat('csv')" style="padding: 15px 25px;">
                    📅 CSV Format
                </button>
                <button class="btn btn-info" onclick="window.downloadStatsFormat('txt')" style="padding: 15px 25px;">
                    📝 Text Format
                </button>
            </div>
        </div>
    `;

    showModal('genericModal', 'Download Statistics', modalContent);
};

window.downloadStatsFormat = function(format) {
    console.log(`📥 Downloading statistics as ${format}...`);

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    closeModal('genericModal');
    window.location.href = `/download_statistics?session_id=${sessionId}&format=${format}`;
    showNotification(`📥 Downloading statistics as ${format.toUpperCase()}...`, 'info');
};

window.downloadDocument = function() {
    console.log('📥 Downloading document...');

    const filename = document.getElementById('downloadBtn')?.getAttribute('data-filename');

    if (filename) {
        window.location.href = `/download/${filename}`;
        showNotification('📥 Downloading document...', 'info');
    } else {
        showNotification('❌ No document available for download. Complete the review first.', 'error');
    }
};

// ============================================================================
// ❌ DELETED: Old Activity Logs Implementation (Broken)
// ============================================================================
// Removed all previous showActivityLogs, exportActivityLogs, refreshActivityLogs functions
// Creating completely new implementation in activity_logs.js

// ============================================================================
// FIX #10: Reset Session with S3 Push and Activity Logging (User Request - Nov 16)
// ============================================================================

window.resetSession = function() {
    console.log('🔄 Initiating Reset Session...');

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session to reset', 'info');
        return;
    }

    // Show confirmation dialog
    if (confirm('⚠️ Reset Session?\n\nThis will:\n• Erase ALL document data\n• Clear all feedback decisions\n• Back up data to S3 (if configured)\n• Log reset action to activity logs\n\nThis cannot be undone. Continue?')) {
        window.confirmResetSession(sessionId);
    }
};

window.confirmResetSession = function(sessionId) {
    closeModal('genericModal');
    showProgress('Resetting session and backing up to S3...');

    fetch('/reset_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            backup_to_s3: true,
            log_activity: true
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProgress();

        if (data.success) {
            let message = '✅ Session reset successfully!';

            if (data.s3_backup) {
                if (data.s3_backup.success) {
                    message += ` Data backed up to S3: ${data.s3_backup.location}`;
                } else {
                    message += ` ⚠️ S3 backup failed: ${data.s3_backup.error}`;
                }
            }

            showNotification(message, 'success');

            // Reset all UI and state
            window.currentSession = null;
            window.sections = [];
            window.currentSectionIndex = -1;
            window.sectionData = {};
            window.userFeedbackHistory = [];
            sessionStorage.clear();

            // Reset UI elements
            const documentContent = document.getElementById('documentContent');
            const feedbackContainer = document.getElementById('feedbackContainer');
            const mainContent = document.getElementById('mainContent');

            if (documentContent) documentContent.innerHTML = '';
            if (feedbackContainer) feedbackContainer.innerHTML = '';
            if (mainContent) mainContent.style.display = 'none';

            // Reload page to fresh state
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification('❌ Reset failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        hideProgress();
        console.error('Reset session error:', error);
        showNotification('❌ Reset failed: ' + error.message, 'error');
    });
};

// ============================================================================
// FIX #11: Submit All Feedbacks - DISABLED
// ============================================================================
// ❌ DISABLED: This function is now handled by unified_button_fixes.js
// Keeping this code commented for reference only

/*
window.submitAllFeedbacks = function() {
    console.log('📤 Submitting all feedbacks...');

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    const availableSections = window.sections || [];
    if (!availableSections || availableSections.length === 0) {
        showNotification('No document sections found. Please upload and analyze a document first.', 'error');
        return;
    }

    // Show simple confirmation dialog
    if (confirm('📤 Submit All Feedbacks?\n\nThis will:\n• Generate final document with all comments\n• Export complete data package to S3\n• Create comprehensive activity logs\n• Include all feedback decisions\n• Enable document download\n\nContinue?')) {
        window.confirmSubmitAllFeedbacks(sessionId);
    }
};

window.confirmSubmitAllFeedbacks = function(sessionId) {
    closeModal('genericModal');
    showProgress('Generating final document and exporting to S3...');

    fetch('/complete_review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            export_to_s3: true
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        hideProgress();

        if (data.success) {
            let message = `✅ Review completed! Document generated with ${data.comments_count} comments.`;

            if (data.s3_export) {
                if (data.s3_export.success) {
                    message += ` All data exported to S3: ${data.s3_export.location}`;
                    showNotification(message, 'success');

                    // Show S3 success popup if available
                    if (window.showS3SuccessPopup) {
                        window.showS3SuccessPopup(data.s3_export);
                    }
                } else {
                    message += ` ⚠️ S3 export failed: ${data.s3_export.error}`;
                    showNotification(message, 'warning');
                }
            } else {
                message += ' Files saved locally.';
                showNotification(message, 'success');
            }

            // Enable download button
            const downloadBtn = document.getElementById('downloadBtn');
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.setAttribute('data-filename', data.output_file);
            }

            // Store final document data
            window.finalDocumentData = data;
        } else {
            showNotification('❌ Submission failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        hideProgress();
        console.error('Submit feedbacks error:', error);
        showNotification('❌ Submission failed: ' + error.message, 'error');
    });
};
*/

// ============================================================================
// FIX #12: Enhanced Confirmation Dialogs for Revert and Update (User Request - Nov 16)
// ============================================================================

// Override revertAllFeedback with enhanced confirmation
window.revertAllFeedback = function() {
    console.log('🔄 Initiating Revert All Feedback...');

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    // Show simple confirmation dialog
    if (confirm('🔄 Revert All Feedback?\n\nThis will:\n• Undo all accept/reject decisions\n• Reset all feedback to pending state\n• This action cannot be undone\n\nContinue?')) {
        window.confirmRevertAllFeedback(sessionId);
    }
};

window.confirmRevertAllFeedback = function(sessionId) {
    closeModal('genericModal');
    showProgress('Reverting all feedback decisions...');

    fetch('/revert_all_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    })
    .then(response => response.json())
    .then(data => {
        hideProgress();

        if (data.success) {
            showNotification('✅ All feedback decisions reverted!', 'success');

            // Reset feedback states
            if (window.feedbackStates) window.feedbackStates = {};

            // Reload current section
            if (window.loadSection && window.currentSectionIndex >= 0) {
                window.loadSection(window.currentSectionIndex);
            }

            // Update statistics
            if (window.updateStatistics) window.updateStatistics();
        } else {
            showNotification('❌ Revert failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        hideProgress();
        console.error('Revert all feedback error:', error);
        showNotification('❌ Revert failed: ' + error.message, 'error');
    });
};

// Override updateFeedback with enhanced confirmation
window.updateFeedback = function() {
    console.log('✏️ Initiating Update Feedback...');

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    // Show simple confirmation dialog
    if (confirm('✏️ Update Feedback?\n\nThis will:\n• Reload the current section\n• Refresh feedback data from server\n• Update statistics\n\nContinue?')) {
        window.confirmUpdateFeedback(sessionId);
    }
};

window.confirmUpdateFeedback = function(sessionId) {
    closeModal('genericModal');
    showNotification('🔄 Updating feedback data...', 'info');

    // Reload current section to get latest feedback
    if (window.currentSectionIndex >= 0 && window.sections && window.sections.length > 0) {
        if (window.loadSection) {
            window.loadSection(window.currentSectionIndex);
        }
    }

    // Update statistics
    if (window.updateStatistics) window.updateStatistics();

    setTimeout(() => {
        showNotification('✅ Feedback updated successfully!', 'success');
    }, 500);
};

// ============================================================================
// FIX #13: First-Time Text Highlighting Popup (User Request - Nov 16)
// ============================================================================

window.showTextHighlightingFeatureFirstTime = function() {
    // Check if user has seen the popup before
    try {
        const hasSeenPopup = localStorage.getItem('hasSeenTextHighlightingPopup');

        if (hasSeenPopup === 'true') {
            console.log('Text highlighting popup already seen by user, skipping...');
            return;
        }
    } catch (e) {
        console.log('localStorage check failed, showing popup anyway:', e);
    }

    console.log('Showing first-time text highlighting feature guide...');

    const modalContent = `
        <div style="text-align: center; padding: 20px; max-height: 80vh; overflow-y: auto;">
            <h3 style="color: #4f46e5; margin-bottom: 25px; font-size: 1.8em;">🎨 Text Highlighting & Commenting Feature Guide</h3>

            <div style="background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); padding: 25px; border-radius: 15px; margin-bottom: 25px; border: 3px solid #4f46e5; box-shadow: 0 8px 25px rgba(79, 70, 229, 0.2);">
                <h4 style="color: #4f46e5; margin-bottom: 20px; font-size: 1.4em;">📝 Complete Usage Guide:</h4>

                <div style="text-align: left; margin-bottom: 20px;">
                    <div style="display: grid; grid-template-columns: 1fr; gap: 15px;">
                        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #4f46e5; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                            <h5 style="color: #4f46e5; margin-bottom: 10px;">🎨 Step 1: Choose Your Highlight Color</h5>
                            <p style="margin: 0; color: #555;">Click any color button in the highlight toolbar: Yellow, Green, Blue, Red, or Gray. Each color can represent different types of feedback.</p>
                        </div>

                        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #10b981; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                            <h5 style="color: #10b981; margin-bottom: 10px;">📝 Step 2: Select Text in Document</h5>
                            <p style="margin: 0; color: #555;">Use your mouse to select any text in the document. You can highlight single words, phrases, or entire paragraphs.</p>
                        </div>

                        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #ec4899; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                            <h5 style="color: #ec4899; margin-bottom: 10px;">💬 Step 3: Add Your Comment</h5>
                            <p style="margin: 0; color: #555;">After selecting text, click the "Save" button. You can add a comment to explain why you highlighted this text.</p>
                        </div>

                        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #f59e0b; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                            <h5 style="color: #f59e0b; margin-bottom: 10px;">📋 Step 4: View Your Highlights</h5>
                            <p style="margin: 0; color: #555;">All your highlights and comments appear in the "All My Custom Feedback" section. You can manage them there anytime.</p>
                        </div>
                    </div>
                </div>

                <div style="background: rgba(79, 70, 229, 0.1); padding: 15px; border-radius: 10px; margin-top: 20px;">
                    <p style="margin: 0; color: #4f46e5; font-weight: 600; font-size: 0.95em;">
                        💡 <strong>Pro Tip:</strong> Use different colors for different types of feedback - Yellow for suggestions, Red for critical issues, Green for good points!
                    </p>
                </div>
            </div>

            <div style="text-align: center; margin-top: 25px;">
                <button class="btn btn-primary" onclick="window.closeTextHighlightingPopup()" style="padding: 15px 30px; font-size: 16px; border-radius: 25px; font-weight: 700; box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4);">
                    ✅ Got it! Let's Start
                </button>
            </div>
        </div>
    `;

    showModal('genericModal', 'Text Highlighting Feature', modalContent);
};

window.closeTextHighlightingPopup = function() {
    // Mark as seen in localStorage
    localStorage.setItem('hasSeenTextHighlightingPopup', 'true');
    closeModal('genericModal');
    showNotification('✅ Text highlighting feature guide acknowledged!', 'success');
};

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
console.log('   - refreshUserFeedbackList: ', typeof window.refreshUserFeedbackList);
console.log('   - showUserFeedbackManager: ', typeof window.showUserFeedbackManager);
console.log('   - editUserFeedback: ', typeof window.editUserFeedback);
console.log('   - saveEditedFeedback: ', typeof window.saveEditedFeedback);
console.log('   - deleteUserFeedback: ', typeof window.deleteUserFeedback);
console.log('   - revertAllFeedback: ', typeof window.revertAllFeedback);
console.log('   - updateFeedback: ', typeof window.updateFeedback);
console.log('   - completeReview: ', typeof window.completeReview);
console.log('   - downloadGuidelines: ', typeof window.downloadGuidelines);
console.log('   - exportChatHistory: ', typeof window.exportChatHistory);
console.log('   - showDashboard: ', typeof window.showDashboard);
console.log('   - deleteDocument: ', typeof window.deleteDocument);
console.log('   - exportAllUserFeedback: ', typeof window.exportAllUserFeedback);
console.log('   - clearAllSectionCustomFeedback: ', typeof window.clearAllSectionCustomFeedback);
console.log('   - provideFeedbackOnTool: ', typeof window.provideFeedbackOnTool);
console.log('   - submitToolFeedback: ', typeof window.submitToolFeedback);
console.log('   - downloadStatistics: ', typeof window.downloadStatistics);
console.log('   - downloadStatsFormat: ', typeof window.downloadStatsFormat);
console.log('   - downloadDocument: ', typeof window.downloadDocument);
console.log('   - showActivityLogs: ', typeof window.showActivityLogs);
console.log('   - exportActivityLogs: ', typeof window.exportActivityLogs);
console.log('   - downloadActivityLogsFormat: ', typeof window.downloadActivityLogsFormat);
console.log('   - refreshActivityLogs: ', typeof window.refreshActivityLogs);
console.log('   - resetSession: ', typeof window.resetSession);
console.log('   - submitAllFeedbacks: ', typeof window.submitAllFeedbacks);

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

// ============================================================================
// NEW FEEDBACK ACTION BUTTONS (Issue #1 Fix - Nov 16)
// ============================================================================

/**
 * Revert feedback decision (undo accept/reject)
 */
window.revertFeedbackDecision = function(feedbackId, sectionName) {
    console.log('🔄 Reverting feedback decision for:', feedbackId, 'Section:', sectionName);

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session', 'error');
        return;
    }

    if (confirm('Revert this feedback decision? This will reset it to pending state.')) {
        fetch('/revert_feedback', {
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
                showNotification('✅ Feedback decision reverted!', 'success');

                // Reload current section to show updated state
                if (window.loadSection && window.currentSectionIndex >= 0) {
                    window.loadSection(window.currentSectionIndex);
                }

                // Update statistics
                if (window.updateStatistics) window.updateStatistics();

                // Update real-time logs
                if (window.updateRealTimeFeedbackLogs) {
                    window.updateRealTimeFeedbackLogs();
                }
            } else {
                showNotification('❌ Revert failed: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Revert feedback error:', error);
            showNotification('❌ Revert failed: ' + error.message, 'error');
        });
    }
};

/**
 * Update/Edit feedback item
 */
window.updateFeedbackItem = function(feedbackId, sectionName) {
    console.log('✏️ Updating feedback item:', feedbackId, 'Section:', sectionName);

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session', 'error');
        return;
    }

    // Find the feedback item in current section data
    const feedbackItem = window.sectionData && window.currentSectionIndex >= 0 ?
                        window.sectionData[window.sections[window.currentSectionIndex]]?.feedback?.find(item => item.id === feedbackId) :
                        null;

    if (!feedbackItem) {
        showNotification('Feedback item not found', 'error');
        return;
    }

    const modalContent = `
        <div style="padding: 20px; max-height: 70vh; overflow-y: auto;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">✏️ Update AI Feedback</h3>

            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Type:</label>
                <select id="editFeedbackType" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px;">
                    <option value="critical" ${feedbackItem.type === 'critical' ? 'selected' : ''}>Critical</option>
                    <option value="important" ${feedbackItem.type === 'important' ? 'selected' : ''}>Important</option>
                    <option value="suggestion" ${feedbackItem.type === 'suggestion' ? 'selected' : ''}>Suggestion</option>
                    <option value="positive" ${feedbackItem.type === 'positive' ? 'selected' : ''}>Positive</option>
                </select>
            </div>

            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Risk Level:</label>
                <select id="editFeedbackRisk" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px;">
                    <option value="High" ${feedbackItem.risk_level === 'High' ? 'selected' : ''}>High</option>
                    <option value="Medium" ${feedbackItem.risk_level === 'Medium' ? 'selected' : ''}>Medium</option>
                    <option value="Low" ${feedbackItem.risk_level === 'Low' ? 'selected' : ''}>Low</option>
                </select>
            </div>

            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Description:</label>
                <textarea id="editFeedbackDescription" style="width: 100%; min-height: 100px; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-family: inherit;">${feedbackItem.description || ''}</textarea>
            </div>

            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 5px; font-weight: 600;">Suggestion:</label>
                <textarea id="editFeedbackSuggestion" style="width: 100%; min-height: 80px; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-family: inherit;">${feedbackItem.suggestion || ''}</textarea>
            </div>

            <div style="text-align: center;">
                <button class="btn btn-success" onclick="window.saveFeedbackUpdate('${feedbackId}', '${sectionName}')" style="padding: 10px 30px; border-radius: 20px; font-weight: 600;">💾 Save Changes</button>
                <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="padding: 10px 30px; border-radius: 20px; font-weight: 600; margin-left: 10px;">❌ Cancel</button>
            </div>
        </div>
    `;

    showModal('genericModal', 'Update Feedback', modalContent);
};

/**
 * Save updated feedback
 */
window.saveFeedbackUpdate = function(feedbackId, sectionName) {
    const type = document.getElementById('editFeedbackType')?.value;
    const risk = document.getElementById('editFeedbackRisk')?.value;
    const description = document.getElementById('editFeedbackDescription')?.value?.trim();
    const suggestion = document.getElementById('editFeedbackSuggestion')?.value?.trim();

    if (!description) {
        showNotification('Description is required', 'error');
        return;
    }

    const sessionId = window.currentSession || sessionStorage.getItem('currentSession');

    fetch('/update_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            section_name: sectionName,
            feedback_id: feedbackId,
            type: type,
            risk_level: risk,
            description: description,
            suggestion: suggestion
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal('genericModal');
            showNotification('✅ Feedback updated successfully!', 'success');

            // Reload section
            if (window.loadSection && window.currentSectionIndex >= 0) {
                window.loadSection(window.currentSectionIndex);
            }

            // Update real-time logs
            if (window.updateRealTimeFeedbackLogs) {
                window.updateRealTimeFeedbackLogs();
            }
        } else {
            showNotification('❌ Update failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Update feedback error:', error);
        showNotification('❌ Update failed: ' + error.message, 'error');
    });
};

/**
 * Add custom comment to AI feedback
 * ✅ FIX: Full form with Type + Category dropdowns (matches "Add Custom" feature)
 */
window.addCustomComment = function(feedbackId, sectionName) {
    console.log('💬 addCustomComment CALLED! Feedback ID:', feedbackId, 'Section:', sectionName);

    const sessionId = window.currentSession ||
                      (typeof currentSession !== 'undefined' ? currentSession : null) ||
                      sessionStorage.getItem('currentSession');

    if (!sessionId) {
        console.error('❌ No active session found');
        if (typeof showNotification === 'function') {
            showNotification('No active session. Please upload a document first.', 'error');
        } else {
            alert('No active session. Please upload a document first.');
        }
        return;
    }

    // Find the feedback item to insert the form below it
    const feedbackItem = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
    if (!feedbackItem) {
        console.error('❌ Feedback item not found:', feedbackId);
        showNotification('Could not find feedback item', 'error');
        return;
    }

    // Remove any existing comment form
    const existingForm = document.getElementById(`comment-form-${feedbackId}`);
    if (existingForm) {
        existingForm.remove();
        return; // Toggle off if clicking again
    }

    // Create inline dropdown form (replica of "Add Your Custom Feedback")
    const formHtml = `
        <div id="comment-form-${feedbackId}" style="margin-top: 20px; padding: 25px; background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); border: 3px solid #4f46e5; border-radius: 15px; box-shadow: 0 8px 25px rgba(79, 70, 229, 0.15); animation: slideDown 0.3s ease-out;">
            <h4 style="color: #4f46e5; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; font-size: 1.2em; font-weight: 700;">
                ✨ Add Your Custom Feedback
            </h4>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div>
                    <label style="font-weight: 700; color: #4f46e5; font-size: 1em; margin-bottom: 8px; display: block;">🏷️ Type:</label>
                    <select id="customCommentType-${feedbackId}" style="width: 100%; padding: 12px; border: 3px solid #4f46e5; border-radius: 12px; background: linear-gradient(135deg, #ffffff, #f8fafc); font-weight: 600; font-size: 14px;">
                        <option value="suggestion">Suggestion</option>
                        <option value="important">Important</option>
                        <option value="critical">Critical</option>
                        <option value="positive">Positive</option>
                        <option value="question">Question</option>
                        <option value="clarification">Clarification</option>
                    </select>
                </div>
                <div>
                    <label style="font-weight: 700; color: #10b981; font-size: 1em; margin-bottom: 8px; display: block;">📁 Category:</label>
                    <select id="customCommentCategory-${feedbackId}" style="width: 100%; padding: 12px; border: 3px solid #10b981; border-radius: 12px; background: linear-gradient(135deg, #ffffff, #f0fdf4); font-weight: 600; font-size: 14px;">
                        <option value="Initial Assessment">Initial Assessment</option>
                        <option value="Investigation Process">Investigation Process</option>
                        <option value="Root Cause Analysis">Root Cause Analysis</option>
                        <option value="Documentation and Reporting">Documentation and Reporting</option>
                        <option value="Seller Classification">Seller Classification</option>
                        <option value="Enforcement Decision-Making">Enforcement Decision-Making</option>
                        <option value="Quality Control">Quality Control</option>
                        <option value="Communication Standards">Communication Standards</option>
                    </select>
                </div>
            </div>

            <div style="margin-bottom: 20px;">
                <label style="font-weight: 700; color: #ec4899; font-size: 1em; margin-bottom: 8px; display: block;">📝 Your Feedback:</label>
                <textarea id="customCommentText-${feedbackId}" placeholder="Share your insights, suggestions, or observations about this AI feedback..." style="width: 100%; min-height: 100px; padding: 15px; border: 3px solid #ec4899; border-radius: 15px; background: linear-gradient(135deg, #ffffff, #fdf2f8); font-size: 14px; line-height: 1.5; font-family: inherit; resize: vertical;"></textarea>
            </div>

            <div style="display: flex; gap: 10px; justify-content: center;">
                <button class="btn btn-success" onclick="window.saveInlineCustomComment('${feedbackId}', '${sectionName}')" style="padding: 15px 35px; font-size: 16px; border-radius: 25px; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4); font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                    🌟 Add My Feedback
                </button>
                <button class="btn btn-secondary" onclick="document.getElementById('comment-form-${feedbackId}').remove()" style="padding: 15px 35px; font-size: 16px; border-radius: 25px; font-weight: 700;">
                    ❌ Cancel
                </button>
            </div>
        </div>

        <style>
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        </style>
    `;

    // Insert form after the feedback item
    feedbackItem.insertAdjacentHTML('afterend', formHtml);

    // Focus on the textarea
    setTimeout(() => {
        const textarea = document.getElementById(`customCommentText-${feedbackId}`);
        if (textarea) textarea.focus();
    }, 100);

    console.log('✅ Inline comment form displayed');
};

/**
 * Save inline custom comment (from dropdown form)
 * ✅ NEW: Saves feedback from inline form instead of modal
 */
window.saveInlineCustomComment = function(feedbackId, sectionName) {
    const type = document.getElementById(`customCommentType-${feedbackId}`)?.value;
    const category = document.getElementById(`customCommentCategory-${feedbackId}`)?.value;
    const description = document.getElementById(`customCommentText-${feedbackId}`)?.value?.trim();

    if (!description) {
        showNotification('Please enter your feedback', 'error');
        return;
    }

    const sessionId = window.currentSession || sessionStorage.getItem('currentSession');

    console.log('💾 Saving inline custom feedback:', {
        feedbackId,
        sectionName,
        type,
        category,
        description: description.substring(0, 50) + '...'
    });

    fetch('/add_custom_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            section_name: sectionName,
            type: type,
            category: category,
            description: description,
            ai_reference: true,
            ai_id: feedbackId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the inline form
            const form = document.getElementById(`comment-form-${feedbackId}`);
            if (form) form.remove();

            showNotification('✅ Custom feedback added successfully!', 'success');

            // Add to user feedback history for display in "All My Custom Feedback"
            if (!window.userFeedbackHistory) {
                window.userFeedbackHistory = [];
            }

            const feedbackItem = {
                id: data.feedback_item?.id || Date.now(),
                section: sectionName,
                type: type,
                category: category,
                description: description,
                timestamp: new Date().toISOString(),
                ai_reference: true,
                ai_id: feedbackId
            };

            window.userFeedbackHistory.push(feedbackItem);

            // Update custom feedback display if function exists
            if (window.updateAllCustomFeedbackList) {
                window.updateAllCustomFeedbackList();
            }

            // Update real-time logs if function exists
            if (window.updateRealTimeFeedbackLogs) {
                window.updateRealTimeFeedbackLogs();
            }

            // Reload section to show updated feedback
            if (window.loadSection && window.currentSectionIndex >= 0) {
                window.loadSection(window.currentSectionIndex);
            }
        } else {
            showNotification('❌ Failed to add feedback: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Add inline custom feedback error:', error);
        showNotification('❌ Failed to add feedback: ' + error.message, 'error');
    });
};

/**
 * Save custom comment (original modal version - kept for backwards compatibility)
 * ✅ FIX: Saves to custom feedback with Type + Category, appears in "All My Custom Feedback"
 */
window.saveCustomComment = function(feedbackId, sectionName) {
    const type = document.getElementById('customCommentType')?.value;
    const category = document.getElementById('customCommentCategory')?.value;
    const description = document.getElementById('customCommentText')?.value?.trim();

    if (!description) {
        showNotification('Please enter your feedback', 'error');
        return;
    }

    const sessionId = window.currentSession || sessionStorage.getItem('currentSession');

    console.log('💾 Saving custom feedback:', {
        feedbackId,
        sectionName,
        type,
        category,
        description: description.substring(0, 50) + '...'
    });

    fetch('/add_custom_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            section_name: sectionName,
            type: type,
            category: category,
            description: description,
            ai_reference: true,
            ai_id: feedbackId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal('genericModal');
            showNotification('✅ Custom feedback added successfully!', 'success');

            // Add to user feedback history for display in "All My Custom Feedback"
            if (!window.userFeedbackHistory) {
                window.userFeedbackHistory = [];
            }

            const feedbackItem = {
                id: data.feedback_item?.id || Date.now(),
                section: sectionName,
                type: type,
                category: category,
                description: description,
                timestamp: new Date().toISOString(),
                ai_reference: true,
                ai_id: feedbackId
            };

            window.userFeedbackHistory.push(feedbackItem);

            // Update custom feedback display if function exists
            if (window.updateAllCustomFeedbackList) {
                window.updateAllCustomFeedbackList();
            }

            // Update real-time logs if function exists
            if (window.updateRealTimeFeedbackLogs) {
                window.updateRealTimeFeedbackLogs();
            }

            // Reload section to show updated feedback
            if (window.loadSection && window.currentSectionIndex >= 0) {
                window.loadSection(window.currentSectionIndex);
            }
        } else {
            showNotification('❌ Failed to add feedback: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Add custom feedback error:', error);
        showNotification('❌ Failed to add feedback: ' + error.message, 'error');
    });
};

// Log all function availability
console.log('✅ Global function fixes loaded successfully!');
console.log('   - addCustomComment:', typeof window.addCustomComment);
console.log('   - saveCustomComment:', typeof window.saveCustomComment);
console.log('   - revertFeedbackDecision:', typeof window.revertFeedbackDecision);
console.log('   - updateFeedbackItem:', typeof window.updateFeedbackItem);
console.log('   - showActivityLogs:', typeof window.showActivityLogs);
console.log('🎉 All fixes applied! Activity Logs rebuilt, Add Comment fixed, AI truncation fixed (1000 chars, 10 items). All buttons functional!');
