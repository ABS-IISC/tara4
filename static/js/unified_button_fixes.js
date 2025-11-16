// ============================================================================
// UNIFIED BUTTON FIXES - Single Source of Truth for Accept/Reject/Update
// ============================================================================
// This file provides THE ONLY implementation of accept/reject/update functions
// All other files MUST NOT define these functions
// Date: 2025-11-16
// Issue: Multiple conflicting function definitions causing button failures
// Solution: Smart parameter detection + unified implementation
// ============================================================================

console.log('🔧 Loading UNIFIED button fixes...');

/**
 * UNIFIED Accept Feedback Function
 * Smart parameter detection handles BOTH calling patterns:
 * - acceptFeedback(feedbackId, event) - from HTML inline handlers
 * - acceptFeedback(feedbackId, sectionName) - from generated buttons
 */
window.acceptFeedback = function(feedbackId, eventOrSection) {
    console.log('✅ UNIFIED acceptFeedback called:', feedbackId, eventOrSection);

    // Stop event propagation if second param is an event
    if (eventOrSection && typeof eventOrSection === 'object' && eventOrSection.stopPropagation) {
        eventOrSection.stopPropagation();
    }

    // Smart section name extraction
    let sectionName;
    if (typeof eventOrSection === 'string') {
        // Called with sectionName directly
        sectionName = eventOrSection;
    } else {
        // Extract from current context
        sectionName = getCurrentSectionName();
    }

    // Validate section name
    if (!sectionName || typeof sectionName !== 'string') {
        console.error('❌ Invalid section name:', sectionName);
        showNotification('Cannot determine section name. Please try again.', 'error');
        return;
    }

    // Get session from multiple sources
    const sessionId = window.currentSession ||
                     (typeof currentSession !== 'undefined' ? currentSession : null) ||
                     sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    console.log('📤 Accepting feedback:', { feedbackId, sectionName, sessionId });

    // Send to backend
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

            // Update UI without reloading section (preserves state)
            updateFeedbackItemUI(feedbackId, 'accepted');

            // Update statistics
            if (window.updateStatistics) {
                window.updateStatistics();
            }

            // Log activity
            if (window.logAIFeedbackActivity) {
                window.logAIFeedbackActivity(feedbackId, 'accepted');
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

/**
 * UNIFIED Reject Feedback Function
 * Smart parameter detection handles BOTH calling patterns
 */
window.rejectFeedback = function(feedbackId, eventOrSection) {
    console.log('❌ UNIFIED rejectFeedback called:', feedbackId, eventOrSection);

    // Stop event propagation if second param is an event
    if (eventOrSection && typeof eventOrSection === 'object' && eventOrSection.stopPropagation) {
        eventOrSection.stopPropagation();
    }

    // Smart section name extraction
    let sectionName;
    if (typeof eventOrSection === 'string') {
        // Called with sectionName directly
        sectionName = eventOrSection;
    } else {
        // Extract from current context
        sectionName = getCurrentSectionName();
    }

    // Validate section name
    if (!sectionName || typeof sectionName !== 'string') {
        console.error('❌ Invalid section name:', sectionName);
        showNotification('Cannot determine section name. Please try again.', 'error');
        return;
    }

    // Get session from multiple sources
    const sessionId = window.currentSession ||
                     (typeof currentSession !== 'undefined' ? currentSession : null) ||
                     sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    console.log('📤 Rejecting feedback:', { feedbackId, sectionName, sessionId });

    // Send to backend
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

            // Update UI without reloading section (preserves state)
            updateFeedbackItemUI(feedbackId, 'rejected');

            // Update statistics
            if (window.updateStatistics) {
                window.updateStatistics();
            }

            // Log activity
            if (window.logAIFeedbackActivity) {
                window.logAIFeedbackActivity(feedbackId, 'rejected');
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

/**
 * Helper: Get current section name from multiple sources
 */
function getCurrentSectionName() {
    // Try multiple sources
    if (window.sections && typeof window.currentSectionIndex === 'number' && window.currentSectionIndex >= 0) {
        return window.sections[window.currentSectionIndex];
    }

    if (typeof sections !== 'undefined' && typeof currentSectionIndex !== 'undefined' && currentSectionIndex >= 0) {
        return sections[currentSectionIndex];
    }

    // Try to extract from page title or active section indicator
    const sectionSelect = document.getElementById('sectionSelect');
    if (sectionSelect && sectionSelect.selectedIndex > 0) {
        return sectionSelect.options[sectionSelect.selectedIndex].text;
    }

    return null;
}

/**
 * Helper: Update feedback item UI after accept/reject
 * Does NOT reload section - just updates visual state
 */
function updateFeedbackItemUI(feedbackId, status) {
    const feedbackElement = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
    if (!feedbackElement) {
        console.warn('Feedback element not found:', feedbackId);
        return;
    }

    const statusColor = status === 'accepted' ? '#10b981' : '#ef4444';
    const statusText = status === 'accepted' ? '✅ Accepted' : '❌ Rejected';
    const statusIcon = status === 'accepted' ? '✅' : '❌';

    // Update border color
    feedbackElement.style.borderLeftColor = statusColor;
    feedbackElement.style.borderLeftWidth = '5px';

    // Update or add status badge
    let statusBadge = feedbackElement.querySelector('.feedback-status-badge');
    if (!statusBadge) {
        statusBadge = document.createElement('div');
        statusBadge.className = 'feedback-status-badge';
        statusBadge.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        feedbackElement.style.position = 'relative';
        feedbackElement.insertBefore(statusBadge, feedbackElement.firstChild);
    }

    statusBadge.textContent = statusText;
    statusBadge.style.background = statusColor;
    statusBadge.style.color = 'white';

    // Disable action buttons (except revert)
    const actionButtons = feedbackElement.querySelectorAll('.feedback-actions button');
    actionButtons.forEach(btn => {
        const btnText = btn.textContent.toLowerCase();
        if (!btnText.includes('revert')) {
            btn.disabled = true;
            btn.style.opacity = '0.5';
            btn.style.cursor = 'not-allowed';
        }
    });

    console.log(`✅ UI updated for ${feedbackId}: ${status}`);
}

/**
 * UNIFIED Revert Feedback Function
 */
window.revertFeedback = function(feedbackId, eventOrSection) {
    console.log('🔄 UNIFIED revertFeedback called:', feedbackId, eventOrSection);

    // Stop event propagation if second param is an event
    if (eventOrSection && typeof eventOrSection === 'object' && eventOrSection.stopPropagation) {
        eventOrSection.stopPropagation();
    }

    // Smart section name extraction
    let sectionName;
    if (typeof eventOrSection === 'string') {
        sectionName = eventOrSection;
    } else {
        sectionName = getCurrentSectionName();
    }

    if (!sectionName || typeof sectionName !== 'string') {
        console.error('❌ Invalid section name:', sectionName);
        showNotification('Cannot determine section name. Please try again.', 'error');
        return;
    }

    const sessionId = window.currentSession ||
                     (typeof currentSession !== 'undefined' ? currentSession : null) ||
                     sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    // Send revert request
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
            showNotification('🔄 Feedback reverted to pending!', 'success');

            // Restore UI to pending state
            const feedbackElement = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
            if (feedbackElement) {
                // Remove status badge
                const statusBadge = feedbackElement.querySelector('.feedback-status-badge');
                if (statusBadge) {
                    statusBadge.remove();
                }

                // Reset border
                feedbackElement.style.borderLeftColor = '';
                feedbackElement.style.borderLeftWidth = '';

                // Re-enable buttons
                const actionButtons = feedbackElement.querySelectorAll('.feedback-actions button');
                actionButtons.forEach(btn => {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    btn.style.cursor = 'pointer';
                });
            }

            // Update statistics
            if (window.updateStatistics) {
                window.updateStatistics();
            }

            // Update real-time logs
            if (window.updateRealTimeFeedbackLogs) {
                window.updateRealTimeFeedbackLogs();
            }
        } else {
            showNotification('❌ Failed to revert feedback: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Revert feedback error:', error);
        showNotification('❌ Error: ' + error.message, 'error');
    });
};

/**
 * UNIFIED Update Feedback Function
 */
window.updateFeedback = function() {
    console.log('🔄 UNIFIED updateFeedback called');

    const sessionId = window.currentSession ||
                     (typeof currentSession !== 'undefined' ? currentSession : null) ||
                     sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    showNotification('🔄 Refreshing feedback...', 'info');

    // Reload current section
    if (typeof window.currentSectionIndex !== 'undefined' && window.currentSectionIndex >= 0) {
        if (typeof window.loadSection === 'function') {
            window.loadSection(window.currentSectionIndex);
        } else if (typeof loadSection === 'function') {
            loadSection(window.currentSectionIndex);
        }
    }

    // Update statistics
    if (window.updateStatistics) {
        window.updateStatistics();
    } else if (typeof updateStatistics === 'function') {
        updateStatistics();
    }

    setTimeout(() => {
        showNotification('✅ Feedback refreshed!', 'success');
    }, 500);
};

/**
 * UNIFIED Add Comment Function
 */
window.addCommentToFeedback = function(feedbackId, eventOrSection) {
    console.log('💬 UNIFIED addCommentToFeedback called:', feedbackId, eventOrSection);

    // Stop event propagation if second param is an event
    if (eventOrSection && typeof eventOrSection === 'object' && eventOrSection.stopPropagation) {
        eventOrSection.stopPropagation();
    }

    // Smart section name extraction
    let sectionName;
    if (typeof eventOrSection === 'string') {
        sectionName = eventOrSection;
    } else {
        sectionName = getCurrentSectionName();
    }

    if (!sectionName || typeof sectionName !== 'string') {
        console.error('❌ Invalid section name:', sectionName);
        showNotification('Cannot determine section name. Please try again.', 'error');
        return;
    }

    // Call the inline feedback form function if available
    if (window.showInlineFeedbackForm) {
        window.showInlineFeedbackForm(feedbackId, sectionName);
    } else if (window.addCustomComment) {
        window.addCustomComment(feedbackId, sectionName);
    } else {
        showNotification('Comment function not available', 'error');
    }
};

// Log successful load
console.log('✅ UNIFIED button fixes loaded successfully!');
console.log('   - acceptFeedback:', typeof window.acceptFeedback);
console.log('   - rejectFeedback:', typeof window.rejectFeedback);
console.log('   - revertFeedback:', typeof window.revertFeedback);
console.log('   - updateFeedback:', typeof window.updateFeedback);
console.log('   - addCommentToFeedback:', typeof window.addCommentToFeedback);
console.log('🎉 All button functions unified and ready!');
