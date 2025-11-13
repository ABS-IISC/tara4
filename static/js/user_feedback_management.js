// User Feedback Management Functions for AI-Prism
// Handles display and management of custom user feedback

console.log('Loading user feedback management...');

// Global variables to ensure they exist
window.userFeedbackHistory = window.userFeedbackHistory || [];

/**
 * Display user feedback in the feedback display area
 * @param {Object} feedbackItem - The feedback item to display
 */
window.displayUserFeedback = function displayUserFeedback(feedbackItem) {
    const userFeedbackDisplay = document.getElementById('userFeedbackDisplay');
    if (!userFeedbackDisplay) {
        console.warn('userFeedbackDisplay element not found');
        return;
    }
    
    // Create feedback element
    const feedbackElement = document.createElement('div');
    feedbackElement.className = 'user-feedback-item';
    feedbackElement.id = `user-feedback-${feedbackItem.id}`;
    feedbackElement.setAttribute('data-feedback-id', feedbackItem.id);
    if (feedbackItem.ai_id) {
        feedbackElement.setAttribute('data-ai-id', feedbackItem.ai_id);
    }
    if (feedbackItem.highlight_id) {
        feedbackElement.setAttribute('data-highlight-id', feedbackItem.highlight_id);
    }
    
    // Determine risk level color and icon
    const riskColors = {
        'High': '#e74c3c',
        'Medium': '#f39c12', 
        'Low': '#2ecc71'
    };
    
    const riskIcons = {
        'High': '🔴',
        'Medium': '🟡',
        'Low': '🟢'
    };
    
    const typeIcons = {
        'suggestion': '💡',
        'important': '⚠️',
        'critical': '🚨',
        'positive': '✅',
        'question': '❓',
        'clarification': '📝'
    };
    
    const riskColor = riskColors[feedbackItem.risk_level] || riskColors.Low;
    const riskIcon = riskIcons[feedbackItem.risk_level] || riskIcons.Low;
    const typeIcon = typeIcons[feedbackItem.type] || '📝';
    
    feedbackElement.innerHTML = `
        <div style="background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); border: 2px solid ${riskColor}; border-radius: 12px; padding: 15px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.2em;">${typeIcon}</span>
                    <span style="font-weight: bold; color: #4f46e5; text-transform: uppercase;">${feedbackItem.type}</span>
                    <span style="background: ${riskColor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold;">${riskIcon} ${feedbackItem.risk_level}</span>
                    <span style="background: #667eea; color: white; padding: 2px 8px; border-radius: 8px; font-size: 0.8em;">${feedbackItem.category}</span>
                </div>
                <div style="display: flex; gap: 5px;">
                    <button onclick="editUserFeedback('${feedbackItem.id}')" style="background: #4f46e5; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8em;" title="Edit">✏️</button>
                    <button onclick="deleteUserFeedback('${feedbackItem.id}')" style="background: #e74c3c; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8em;" title="Delete">🗑️</button>
                </div>
            </div>
            
            <div style="margin-bottom: 10px; line-height: 1.5; color: #333;">
                ${feedbackItem.description}
            </div>
            
            ${feedbackItem.ai_reference ? `
                <div style="background: rgba(79, 70, 229, 0.1); padding: 8px; border-radius: 6px; margin-top: 8px; font-size: 0.9em;">
                    <strong>🤖 Related to AI:</strong> ${feedbackItem.ai_reference}
                </div>
            ` : ''}
            
            ${feedbackItem.highlighted_text ? `
                <div style="background: rgba(255, 215, 0, 0.2); padding: 8px; border-radius: 6px; margin-top: 8px; font-size: 0.9em; border-left: 3px solid #ffd700;">
                    <strong>📝 Highlighted Text:</strong> "${feedbackItem.highlighted_text.length > 100 ? feedbackItem.highlighted_text.substring(0, 100) + '...' : feedbackItem.highlighted_text}"
                </div>
            ` : ''}
            
            <div style="margin-top: 10px; font-size: 0.8em; color: #666; display: flex; justify-content: space-between;">
                <span>📅 ${new Date(feedbackItem.timestamp).toLocaleString()}</span>
                <span>📍 Section: ${feedbackItem.section || 'Unknown'}</span>
            </div>
        </div>
    `;
    
    // Add to display (prepend to show newest first)
    userFeedbackDisplay.insertBefore(feedbackElement, userFeedbackDisplay.firstChild);
    
    console.log('User feedback displayed:', feedbackItem.id);
}

/**
 * Update the comprehensive custom feedback list
 */
function updateAllCustomFeedbackList() {
    console.log('updateAllCustomFeedbackList called');
    
    if (!userFeedbackHistory || userFeedbackHistory.length === 0) {
        console.log('No user feedback history to display');
        return;
    }
    
    // Update counters and displays across the interface
    updateFeedbackCounters();
    updateCustomFeedbackSectionDisplay();
    
    // Update button states for AI custom feedback
    if (typeof updateAICustomButtonStates === 'function') {
        updateAICustomButtonStates();
    }
    
    console.log('Custom feedback list updated');
}

/**
 * Update feedback counters throughout the interface
 */
function updateFeedbackCounters() {
    const totalCustomFeedback = userFeedbackHistory.length;
    
    // Update various counter elements if they exist
    const counters = [
        'customFeedbackCount',
        'totalCustomFeedbackCount',
        'userFeedbackCounter'
    ];
    
    counters.forEach(counterId => {
        const counter = document.getElementById(counterId);
        if (counter) {
            counter.textContent = totalCustomFeedback;
        }
    });
    
    // Update section-specific counters
    if (typeof updateSectionCustomFeedbackCounter === 'function') {
        updateSectionCustomFeedbackCounter();
    }
}

/**
 * Update the custom feedback section display
 */
function updateCustomFeedbackSectionDisplay() {
    const userFeedbackDisplay = document.getElementById('userFeedbackDisplay');
    if (!userFeedbackDisplay) return;
    
    // Get current section feedback
    if (typeof sections !== 'undefined' && typeof currentSectionIndex !== 'undefined' && currentSectionIndex >= 0) {
        const currentSectionName = sections[currentSectionIndex];
        const sectionFeedback = userFeedbackHistory.filter(item => item.section === currentSectionName);
        
        // Clear and redisplay
        userFeedbackDisplay.innerHTML = '';
        
        if (sectionFeedback.length === 0) {
            userFeedbackDisplay.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #666; font-style: italic;">
                    📝 No custom feedback added for this section yet.
                </div>
            `;
        } else {
            sectionFeedback.forEach(feedback => displayUserFeedback(feedback));
        }
    }
}

/**
 * Refresh the user feedback list display
 */
function refreshUserFeedbackList() {
    console.log('refreshUserFeedbackList called');
    
    // Update all displays
    updateAllCustomFeedbackList();
    
    // Update real-time logs in the "All My Custom Feedback" section
    if (window.updateRealTimeFeedbackLogs) {
        window.updateRealTimeFeedbackLogs();
    }
    
    // Update statistics if function exists
    if (typeof updateStatistics === 'function') {
        updateStatistics();
    }
    
    // Trigger other UI updates
    setTimeout(() => {
        if (typeof updateAICustomButtonStates === 'function') {
            updateAICustomButtonStates();
        }
    }, 100);
}

/**
 * Edit user feedback
 * @param {string} feedbackId - The feedback ID to edit
 */
function editUserFeedback(feedbackId) {
    const feedback = userFeedbackHistory.find(item => item.id === feedbackId);
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
                <button class="btn btn-success" onclick="saveEditedFeedback('${feedbackId}')" style="padding: 12px 25px; margin: 5px; border-radius: 20px; font-weight: 600;">💾 Save Changes</button>
                <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="padding: 12px 25px; margin: 5px; border-radius: 20px;">❌ Cancel</button>
            </div>
        </div>
    `;
    
    if (typeof showModal === 'function') {
        showModal('genericModal', 'Edit Custom Feedback', modalContent);
    }
}

/**
 * Save edited feedback
 * @param {string} feedbackId - The feedback ID to save
 */
function saveEditedFeedback(feedbackId) {
    const type = document.getElementById('editFeedbackType')?.value;
    const category = document.getElementById('editFeedbackCategory')?.value;
    const description = document.getElementById('editFeedbackDescription')?.value?.trim();
    
    if (!description) {
        showNotification('Please enter a description', 'error');
        return;
    }
    
    // Find and update the feedback in local history
    const feedbackIndex = userFeedbackHistory.findIndex(item => item.id === feedbackId);
    if (feedbackIndex === -1) {
        showNotification('Feedback item not found', 'error');
        return;
    }
    
    // Update local feedback
    userFeedbackHistory[feedbackIndex] = {
        ...userFeedbackHistory[feedbackIndex],
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
                showNotification('Feedback updated successfully!', 'success');
            } else {
                console.warn('Backend update failed:', data.error);
                showNotification('Feedback updated locally (backend sync failed)', 'warning');
            }
        })
        .catch(error => {
            console.error('Backend update error:', error);
            showNotification('Feedback updated locally (backend sync failed)', 'warning');
        });
    }
    
    // Refresh displays
    refreshUserFeedbackList();
    
    if (typeof closeModal === 'function') {
        closeModal('genericModal');
    }
    
    showNotification('Custom feedback updated!', 'success');
}

/**
 * Update real-time feedback logs showing all user activities
 */
window.updateRealTimeFeedbackLogs = function updateRealTimeFeedbackLogs() {
    const container = document.getElementById('customFeedbackList');
    if (!container) {
        console.warn('customFeedbackList container not found');
        return;
    }
    
    // Get all feedback activities
    const allActivities = [];
    
    // Add custom feedback entries
    if (window.userFeedbackHistory) {
        window.userFeedbackHistory.forEach(item => {
            allActivities.push({
                type: 'custom_added',
                timestamp: item.timestamp,
                data: item,
                action: 'Added Custom Feedback',
                icon: '✨',
                color: '#10b981'
            });
        });
    }
    
    // Add accept/reject activities from feedback states
    if (window.feedbackStates) {
        Object.entries(window.feedbackStates).forEach(([feedbackId, state]) => {
            if (state.status !== 'pending') {
                allActivities.push({
                    type: state.status === 'accepted' ? 'ai_accepted' : 'ai_rejected',
                    timestamp: state.timestamp || new Date().toISOString(),
                    feedbackId: feedbackId,
                    action: state.status === 'accepted' ? 'Accepted AI Feedback' : 'Rejected AI Feedback',
                    icon: state.status === 'accepted' ? '✅' : '❌',
                    color: state.status === 'accepted' ? '#2ecc71' : '#e74c3c'
                });
            }
        });
    }
    
    // Sort by timestamp (newest first)
    allActivities.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    if (allActivities.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 12px; color: #6c757d; border: 2px dashed #dee2e6;">
                <div style="font-size: 2em; margin-bottom: 10px;">📝</div>
                <h4 style="margin: 0; color: #495057;">No Activity Yet</h4>
                <p style="margin: 10px 0 0 0; font-size: 0.9em;">Your custom feedback and AI interactions will appear here in real-time</p>
            </div>
        `;
        return;
    }
    
    // Generate real-time activity log
    container.innerHTML = allActivities.map((activity, index) => {
        const timestamp = new Date(activity.timestamp).toLocaleString();
        const timeAgo = getTimeAgo(activity.timestamp);
        
        if (activity.type === 'custom_added') {
            const item = activity.data;
            const typeColors = {
                'suggestion': '#10b981',
                'important': '#f59e0b', 
                'critical': '#ef4444',
                'positive': '#22c55e',
                'question': '#3b82f6',
                'clarification': '#8b5cf6'
            };
            const typeColor = typeColors[item.type] || '#6b7280';
            
            return `
                <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 16px; margin: 12px 0; border-radius: 12px; border-left: 5px solid ${typeColor}; box-shadow: 0 4px 15px rgba(0,0,0,0.08); transition: all 0.3s ease;" onmouseover="this.style.transform='translateX(3px)'; this.style.boxShadow='0 6px 20px rgba(0,0,0,0.12)'" onmouseout="this.style.transform='translateX(0)'; this.style.boxShadow='0 4px 15px rgba(0,0,0,0.08)'">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                            <span style="font-size: 1.2em;">${activity.icon}</span>
                            <span style="font-weight: 700; color: #1f2937; font-size: 0.9em;">${activity.action}</span>
                            <span style="background: ${typeColor}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: 600; text-transform: uppercase;">${item.type}</span>
                            <span style="background: #e5e7eb; color: #374151; padding: 3px 8px; border-radius: 8px; font-size: 0.7em; font-weight: 500;">${item.category}</span>
                        </div>
                        <div style="text-align: right; font-size: 0.75em; color: #6b7280;">
                            <div style="font-weight: 600; color: #059669;">${timeAgo}</div>
                            <div>${timestamp}</div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 12px; color: #374151; line-height: 1.5; background: #f9fafb; padding: 12px; border-radius: 8px; font-size: 0.9em; border-left: 3px solid ${typeColor};">
                        <strong>Feedback:</strong> "${item.description}"
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em; color: #6b7280; padding-top: 8px; border-top: 1px solid #e5e7eb;">
                        <span>📍 Section: <strong style="color: #374151;">${item.section || 'Document Content'}</strong></span>
                        <div style="display: flex; gap: 8px;">
                            <button onclick="window.editUserFeedback && window.editUserFeedback('${item.id}')" style="background: #f59e0b; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px; transition: all 0.2s;" onmouseover="this.style.background='#d97706'" onmouseout="this.style.background='#f59e0b'" title="Edit">✏️</button>
                            <button onclick="window.deleteUserFeedback && window.deleteUserFeedback('${item.id}')" style="background: #ef4444; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px; transition: all 0.2s;" onmouseover="this.style.background='#dc2626'" onmouseout="this.style.background='#ef4444'" title="Delete">🗑️</button>
                        </div>
                    </div>
                    
                    ${item.ai_reference ? `
                        <div style="margin-top: 10px; background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); padding: 10px; border-radius: 6px; font-size: 0.8em; color: #1e40af; border: 1px solid #93c5fd;">
                            <strong>🤖 Related to AI:</strong> ${item.ai_reference}
                        </div>
                    ` : ''}
                    
                    ${item.highlighted_text ? `
                        <div style="margin-top: 10px; background: rgba(255, 215, 0, 0.15); padding: 8px; border-radius: 6px; font-size: 0.8em; color: #92400e; border-left: 3px solid #fbbf24;">
                            <strong>🎨 From Highlighted Text:</strong> "${item.highlighted_text.length > 80 ? item.highlighted_text.substring(0, 80) + '...' : item.highlighted_text}"
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            // AI accept/reject activities
            return `
                <div style="background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%); padding: 14px; margin: 10px 0; border-radius: 10px; border-left: 4px solid ${activity.color}; box-shadow: 0 3px 12px rgba(0,0,0,0.06); transition: all 0.3s ease;" onmouseover="this.style.boxShadow='0 5px 18px rgba(0,0,0,0.1)'" onmouseout="this.style.boxShadow='0 3px 12px rgba(0,0,0,0.06)'">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.1em;">${activity.icon}</span>
                            <span style="font-weight: 600; color: #374151; font-size: 0.85em;">${activity.action}</span>
                            <span style="background: ${activity.color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.7em; font-weight: 600;">AI FEEDBACK</span>
                        </div>
                        <div style="font-size: 0.75em; color: #6b7280; text-align: right;">
                            <div style="font-weight: 600; color: ${activity.color};">${timeAgo}</div>
                            <div>${timestamp}</div>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.8em; color: #6b7280; background: #f9fafb; padding: 6px 10px; border-radius: 6px;">
                        📍 Section: <strong style="color: #374151;">${window.sections && window.currentSectionIndex >= 0 ? window.sections[window.currentSectionIndex] : 'Document Content'}</strong>
                        | 🆔 ID: <code style="background: #e5e7eb; padding: 1px 4px; border-radius: 3px; font-size: 0.7em;">${activity.feedbackId}</code>
                    </div>
                </div>
            `;
        }
    }).join('');
    
    console.log('✅ Real-time feedback logs updated with', allActivities.length, 'activities');
};

/**
 * Get human-readable time ago string
 */
function getTimeAgo(timestamp) {
    const now = new Date();
    const past = new Date(timestamp);
    const diffInSeconds = Math.floor((now - past) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} min ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hr ago`;
    return `${Math.floor(diffInSeconds / 86400)} day(s) ago`;
}

/**
 * Log AI feedback acceptance/rejection activities
 */
window.logAIFeedbackActivity = function logAIFeedbackActivity(feedbackId, action) {
    // Update feedback states with timestamp for tracking
    if (!window.feedbackStates) {
        window.feedbackStates = {};
    }
    
    if (!window.feedbackStates[feedbackId]) {
        window.feedbackStates[feedbackId] = {};
    }
    
    window.feedbackStates[feedbackId].status = action;
    window.feedbackStates[feedbackId].timestamp = new Date().toISOString();
    
    // Refresh the real-time logs
    if (window.updateRealTimeFeedbackLogs) {
        window.updateRealTimeFeedbackLogs();
    }
    
    console.log('✅ AI feedback activity logged:', action, feedbackId);
};

// Override the original updateAllCustomFeedbackList to use the enhanced version
window.updateAllCustomFeedbackList = function updateAllCustomFeedbackList() {
    console.log('updateAllCustomFeedbackList called - enhanced version');
    
    // Update counters and displays across the interface
    updateFeedbackCounters();
    updateCustomFeedbackSectionDisplay();
    
    // Update real-time logs
    if (window.updateRealTimeFeedbackLogs) {
        window.updateRealTimeFeedbackLogs();
    }
    
    // Update button states for AI custom feedback
    if (typeof updateAICustomButtonStates === 'function') {
        updateAICustomButtonStates();
    }
    
    console.log('✅ Enhanced custom feedback list updated with real-time logs');
};

/**
 * Delete user feedback
 * @param {string} feedbackId - The feedback ID to delete
 */
function deleteUserFeedback(feedbackId) {
    const feedback = userFeedbackHistory.find(item => item.id === feedbackId);
    if (!feedback) {
        showNotification('Feedback item not found', 'error');
        return;
    }
    
    if (confirm(`Are you sure you want to delete this ${feedback.type} feedback?`)) {
        // Remove from local history
        userFeedbackHistory = userFeedbackHistory.filter(item => item.id !== feedbackId);
        
        // Remove from display
        const feedbackElement = document.getElementById(`user-feedback-${feedbackId}`);
        if (feedbackElement) {
            feedbackElement.remove();
        }
        
        // Update backend if session exists
        if (typeof currentSession !== 'undefined' && currentSession) {
            fetch('/delete_user_feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: currentSession,
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
        refreshUserFeedbackList();
        
        // Trigger real-time logs update
        if (window.updateRealTimeFeedbackLogs) {
            window.updateRealTimeFeedbackLogs();
        }
        
        showNotification('Custom feedback deleted!', 'success');
    }
}

/**
 * Initialize user feedback management when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('User feedback management initialized');
    
    // Set up periodic refresh of user feedback display
    if (typeof sections !== 'undefined' && typeof currentSectionIndex !== 'undefined') {
        // Watch for section changes to update display
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                    // Section select changed
                    setTimeout(updateCustomFeedbackSectionDisplay, 100);
                }
            });
        });
        
        const sectionSelect = document.getElementById('sectionSelect');
        if (sectionSelect) {
            observer.observe(sectionSelect, { attributes: true });
        }
    }
});

console.log('User feedback management functions loaded successfully');