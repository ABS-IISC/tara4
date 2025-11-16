// Button functionality fixes for AI-Prism Document Analysis Tool

// Global variables - synchronized with window scope
let currentSession = null;
let sections = [];
let currentSectionIndex = 0;
let analysisFile = null;
let guidelinesFile = null;
let chatHistory = [];
let userFeedbackHistory = [];
let feedbackStates = {};
let selectedFeedbackId = null;
let isDarkMode = false;
let documentZoom = 100;
let finalDocumentData = null;
let dashboardData = {
    totalFeedback: 0,
    acceptedFeedback: 0,
    rejectedFeedback: 0,
    userFeedback: 0
};

// Synchronize with window scope for cross-file compatibility
function syncSessionVariables() {
    if (window.currentSession && !currentSession) {
        currentSession = window.currentSession;
    }
    if (window.sections && sections.length === 0) {
        sections = window.sections;
    }
    if (window.currentSectionIndex !== undefined) {
        currentSectionIndex = window.currentSectionIndex;
    }
}

// Call sync function periodically
setInterval(syncSessionVariables, 1000);

// Loading media content for progress animations
let loadingMediaWithContent = [
    {
        gif: 'https://media.giphy.com/media/26tn33aiTi1jkl6H6/giphy.gif',
        joke: "What's Iron Man's favorite type of music? Heavy metal! 🎵",
        math: "Physics: If light travels at 300,000 km/s, how far in 1 minute? Answer: 18 million km! ⚡"
    },
    {
        gif: 'https://media.giphy.com/media/3o7btPCcdNniyf0ArS/giphy.gif',
        joke: "Why is Sherlock Holmes so good at solving crimes? He always finds the clues elementary! 🔍",
        math: "Deduction: If A > B and B > C, then A > C. This is called? Answer: Transitive property! 📊"
    }
];

let currentMediaIndex = 0;
let mediaRotationInterval = null;
let isMediaRotating = false;
let usedMediaIndices = [];
let currentContentType = 'gif';
let showGraphics = true;

// Missing button functions

function revertAllFeedback() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    if (confirm('Are you sure you want to revert ALL feedback decisions? This will reset all accept/reject actions.')) {
        fetch('/revert_all_feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSession })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('All feedback decisions reverted!', 'success');
                feedbackStates = {};
                if (currentSectionIndex >= 0) {
                    loadSection(currentSectionIndex);
                }
                updateStatistics();
            } else {
                showNotification(data.error || 'Revert failed', 'error');
            }
        })
        .catch(error => {
            showNotification('Revert failed: ' + error.message, 'error');
        });
    }
}

function updateFeedback() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    showNotification('Updating feedback data...', 'info');
    
    if (currentSectionIndex >= 0 && sections.length > 0) {
        loadSection(currentSectionIndex);
    }
    
    updateStatistics();
    showNotification('Feedback updated successfully!', 'success');
}

function showDashboard() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    fetch(`/get_dashboard_data?session_id=${currentSession}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const dashboard = data.dashboard;
            
            const modalContent = `
                <div style="max-height: 75vh; overflow-y: auto;">
                    <h3 style="color: #667eea; margin-bottom: 20px;">📊 Analytics Dashboard</h3>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.totalFeedback}</div>
                            <div style="font-size: 1.1em;">Total Feedback</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); color: white; padding: 20px; border-radius: 15px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.acceptedFeedback}</div>
                            <div style="font-size: 1.1em;">Accepted</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 20px; border-radius: 15px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.rejectedFeedback}</div>
                            <div style="font-size: 1.1em;">Rejected</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 20px; border-radius: 15px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.userFeedback}</div>
                            <div style="font-size: 1.1em;">User Added</div>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h4 style="color: #667eea; margin-bottom: 15px;">📈 Progress Overview</h4>
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Sections Analyzed</span>
                                <span style="font-weight: bold;">${dashboard.sectionsAnalyzed}</span>
                            </div>
                            <div style="background: #ecf0f1; height: 10px; border-radius: 5px; overflow: hidden;">
                                <div style="background: #667eea; height: 100%; width: 100%; transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Acceptance Rate</span>
                                <span style="font-weight: bold; color: #2ecc71;">${dashboard.totalFeedback > 0 ? Math.round((dashboard.acceptedFeedback / dashboard.totalFeedback) * 100) : 0}%</span>
                            </div>
                            <div style="background: #ecf0f1; height: 10px; border-radius: 5px; overflow: hidden;">
                                <div style="background: #2ecc71; height: 100%; width: ${dashboard.totalFeedback > 0 ? (dashboard.acceptedFeedback / dashboard.totalFeedback) * 100 : 0}%; transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px;">
                        <button class="btn btn-primary" onclick="exportDashboardData()" style="margin: 5px;">📥 Export Dashboard</button>
                        <button class="btn btn-info" onclick="refreshDashboard()" style="margin: 5px;">🔄 Refresh</button>
                    </div>
                </div>
            `;
            
            showModal('genericModal', 'Analytics Dashboard', modalContent);
        } else {
            showNotification('Failed to load dashboard: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        showNotification('Failed to load dashboard: ' + error.message, 'error');
    });
}

function deleteDocument() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    if (confirm('Are you sure you want to delete the current document? This will keep guidelines but remove the analysis document.')) {
        fetch('/delete_document', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: currentSession,
                keep_guidelines: true 
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Document deleted successfully!', 'success');
                
                document.getElementById('mainContent').style.display = 'none';
                document.getElementById('statisticsPanel').style.display = 'none';
                document.getElementById('actionButtons').style.display = 'none';
                
                document.getElementById('analysisFileName').textContent = '';
                document.getElementById('startAnalysisBtn').disabled = true;
                
                analysisFile = null;
                sections = [];
                currentSectionIndex = 0;
                
                if (data.guidelines_preserved) {
                    showNotification('Guidelines document preserved for future use', 'info');
                }
            } else {
                showNotification(data.error || 'Delete failed', 'error');
            }
        })
        .catch(error => {
            showNotification('Delete failed: ' + error.message, 'error');
        });
    }
}

function provideFeedbackOnTool() {
    const modalContent = `
        <div style="padding: 20px;">
            <h3 style="color: #667eea; margin-bottom: 20px;">💬 Help Us Improve AI-Prism</h3>
            <div style="margin-bottom: 15px;">
                <label style="font-weight: bold; margin-bottom: 5px; display: block;">How would you rate your experience?</label>
                <select id="toolRating" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <option value="5">⭐⭐⭐⭐⭐ Excellent</option>
                    <option value="4">⭐⭐⭐⭐ Good</option>
                    <option value="3">⭐⭐⭐ Average</option>
                    <option value="2">⭐⭐ Poor</option>
                    <option value="1">⭐ Very Poor</option>
                </select>
            </div>
            <div style="margin-bottom: 15px;">
                <label style="font-weight: bold; margin-bottom: 5px; display: block;">What can we improve?</label>
                <textarea id="toolFeedbackText" placeholder="Share your thoughts on how we can make AI-Prism better..." style="width: 100%; height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"></textarea>
            </div>
            <div style="text-align: center;">
                <button class="btn btn-success" onclick="submitToolFeedback()" style="margin: 5px;">📤 Submit Feedback</button>
                <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="margin: 5px;">✗ Cancel</button>
            </div>
        </div>
    `;
    showModal('genericModal', 'Tool Feedback', modalContent);
}

function submitToolFeedback() {
    const rating = document.getElementById('toolRating').value;
    const feedbackText = document.getElementById('toolFeedbackText').value.trim();
    
    const feedbackData = {
        rating: rating,
        feedback: feedbackText,
        timestamp: new Date().toISOString(),
        session_id: currentSession
    };
    
    fetch('/submit_tool_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Thank you for your feedback!', 'success');
            closeModal('genericModal');
        } else {
            showNotification('Failed to submit feedback.', 'error');
        }
    })
    .catch(error => {
        showNotification('Feedback submission failed: ' + error.message, 'error');
    });
}

function completeReview() {
    // Sync variables first
    syncSessionVariables();
    
    // Check multiple possible session variables
    const sessionId = currentSession || window.currentSession || sessionStorage.getItem('currentSession');
    const availableSections = sections || window.sections || [];
    
    console.log('Complete Review Debug:', {
        currentSession,
        windowCurrentSession: window.currentSession,
        sessionStorage: sessionStorage.getItem('currentSession'),
        sections: availableSections.length,
        finalSessionId: sessionId
    });
    
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
        showProgress('Generating final document and saving to S3...');
        
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
            hideProgress();
            if (data.success) {
                let message = `Review completed! Document generated with ${data.comments_count} comments.`;
                
                // Check S3 export status
                if (data.s3_export) {
                    if (data.s3_export.success) {
                        message += ` All data automatically saved to S3: ${data.s3_export.location}`;
                        
                        // Show special S3 success popup
                        showS3SuccessPopup(data.s3_export);
                    } else {
                        message += ` S3 export failed: ${data.s3_export.error}. Files saved locally as backup.`;
                        showNotification('S3 export failed, but files saved locally', 'warning');
                    }
                } else {
                    message += ' Files saved locally.';
                }
                
                showNotification(message, 'success');
                
                const downloadBtn = document.getElementById('downloadBtn');
                if (downloadBtn) {
                    downloadBtn.disabled = false;
                    downloadBtn.setAttribute('data-filename', data.output_file);
                }
                finalDocumentData = data;
            } else {
                showNotification(data.error || 'Review completion failed', 'error');
            }
        })
        .catch(error => {
            hideProgress();
            console.error('Complete review error:', error);
            showNotification('Review completion failed: ' + error.message, 'error');
        });
    }
}

function exportChatHistory() {
    if (chatHistory.length === 0) {
        showNotification('No chat history to export', 'info');
        return;
    }
    
    const exportData = {
        export_timestamp: new Date().toISOString(),
        session_id: currentSession,
        total_messages: chatHistory.length,
        chat_history: chatHistory
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
    
    showNotification('Chat history exported successfully!', 'success');
}

function downloadGuidelines() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    window.location.href = `/download_guidelines?session_id=${currentSession}`;
    showNotification('Downloading guidelines...', 'info');
}

function exportStatistics(statType) {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    const exportData = {
        export_timestamp: new Date().toISOString(),
        session_id: currentSession,
        stat_type: statType,
        statistics: 'Exported from breakdown view'
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${statType}_statistics_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showNotification(`${statType.replace('_', ' ')} statistics exported!`, 'success');
}

function exportDashboardData() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    fetch(`/get_dashboard_data?session_id=${currentSession}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const exportData = {
                export_timestamp: new Date().toISOString(),
                session_id: currentSession,
                dashboard_data: data.dashboard
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `dashboard_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('Dashboard data exported successfully!', 'success');
        } else {
            showNotification('Export failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        showNotification('Export failed: ' + error.message, 'error');
    });
}

function refreshDashboard() {
    closeModal('genericModal');
    setTimeout(() => showDashboard(), 100);
}

function showAutoSuggestions(value) {
    const dropdown = document.getElementById('suggestionDropdown');
    if (!dropdown) return;
    
    if (value.length < 3) {
        dropdown.style.display = 'none';
        return;
    }
    
    const suggestions = [
        'This section needs more detailed analysis of the root cause',
        'Consider adding specific examples to support the findings',
        'The risk assessment could be more comprehensive',
        'Additional verification steps should be included',
        'The documentation lacks sufficient detail for audit purposes',
        'Cross-reference with established quality standards',
        'Include preventative measures to avoid recurrence',
        'The timeline for resolution needs clarification',
        'Consider the impact on customer experience',
        'Add references to relevant compliance requirements'
    ];
    
    const filtered = suggestions.filter(s => 
        s.toLowerCase().includes(value.toLowerCase())
    ).slice(0, 5);
    
    if (filtered.length > 0) {
        dropdown.innerHTML = filtered.map(suggestion => 
            `<div class="suggestion-item" onclick="selectSuggestion('${suggestion}')">${suggestion}</div>`
        ).join('');
        dropdown.style.display = 'block';
    } else {
        dropdown.style.display = 'none';
    }
}

function selectSuggestion(suggestion) {
    document.getElementById('customDescription').value = suggestion;
    document.getElementById('suggestionDropdown').style.display = 'none';
}

function showNotification(message, type = 'info') {
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add styles for better visibility
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        max-width: 400px;
        word-wrap: break-word;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#17a2b8'};
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, type === 'error' ? 6000 : 4000);
}

// Essential functions that are referenced in the HTML
function loadSection(index) {
    console.log('loadSection called with index:', index);
}

function updateStatistics() {
    console.log('updateStatistics called');
}

// ❌ REMOVED: acceptFeedback and rejectFeedback functions
// These functions are now ONLY defined in global_function_fixes.js (single source of truth)
// All action button functions (accept, reject, revert, update) are centralized there
// This eliminates conflicts from multiple function definitions

// Update Feedback Status Function
function updateFeedbackStatus(feedbackId, status) {
    const feedbackItem = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
    if (feedbackItem) {
        const actions = feedbackItem.querySelector('.feedback-actions');
        const statusColor = status === 'accepted' ? '#2ecc71' : '#e74c3c';
        const statusText = status === 'accepted' ? '✓ Accepted' : '✗ Rejected';
        
        if (!feedbackStates[feedbackId]) {
            feedbackStates[feedbackId] = {
                originalHtml: actions.innerHTML,
                status: 'pending'
            };
        }
        feedbackStates[feedbackId].status = status;
        
        actions.innerHTML = `
            <span style="color: ${statusColor}; font-weight: bold;">${statusText}</span>
            <button class="btn btn-warning revert-btn" onclick="revertFeedback('${feedbackId}', event)" style="font-size: 12px; padding: 5px 10px; margin-left: 10px;">🔄 Revert</button>
        `;
        feedbackItem.style.opacity = '0.7';
    }
}

// Revert Feedback Function
function revertFeedback(feedbackId, event) {
    if (event) event.stopPropagation();
    
    const feedbackItem = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
    if (feedbackItem && feedbackStates[feedbackId]) {
        const actions = feedbackItem.querySelector('.feedback-actions');
        actions.innerHTML = feedbackStates[feedbackId].originalHtml;
        feedbackItem.style.opacity = '1';
        
        feedbackStates[feedbackId].status = 'pending';
        
        showNotification('Feedback reverted to original state', 'success');
        updateStatistics();
    }
}

function showProgress(text) {
    const progressContainer = document.getElementById('progressContainer');
    const progressText = document.getElementById('progressText');
    
    if (progressContainer) {
        progressContainer.style.display = 'block';
        progressContainer.style.cssText += `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(255,255,255,0.95);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            z-index: 9999;
            text-align: center;
            min-width: 300px;
        `;
    }
    if (progressText) {
        progressText.textContent = text;
        progressText.style.cssText = `
            font-size: 16px;
            color: #333;
            margin-bottom: 15px;
        `;
    }
}

function hideProgress() {
    const progressContainer = document.getElementById('progressContainer');
    const docProgress = document.getElementById('documentProgress');
    
    if (progressContainer) progressContainer.style.display = 'none';
    if (docProgress) docProgress.style.display = 'none';
}

function showModal(modalId, title, content) {
    const modal = document.getElementById(modalId);
    const titleElement = document.getElementById('genericModalTitle');
    const contentElement = document.getElementById('genericModalContent');
    
    if (titleElement) titleElement.textContent = title;
    if (contentElement) contentElement.innerHTML = content;
    if (modal) {
        modal.style.display = 'block';
        modal.style.cssText += `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.cssText += `
                background: white;
                border-radius: 10px;
                padding: 0;
                max-width: 90vw;
                max-height: 90vh;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            `;
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        // Reset any custom styles
        modal.style.cssText = '';
    }
}

function downloadDocument() {
    const filename = document.getElementById('downloadBtn')?.getAttribute('data-filename');
    if (filename) {
        window.location.href = `/download/${filename}`;
    } else {
        showNotification('No document available for download', 'error');
    }
}

function downloadStatistics() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    const modalContent = `
        <div style="text-align: center; padding: 20px;">
            <h3 style="color: #667eea; margin-bottom: 20px;">📊 Download Statistics</h3>
            <p style="margin-bottom: 30px;">Choose the format for your statistics export:</p>
            
            <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
                <button class="btn btn-primary" onclick="downloadStatsFormat('json')" style="padding: 15px 25px;">
                    📄 JSON Format
                </button>
                <button class="btn btn-success" onclick="downloadStatsFormat('csv')" style="padding: 15px 25px;">
                    📅 CSV Format
                </button>
                <button class="btn btn-info" onclick="downloadStatsFormat('txt')" style="padding: 15px 25px;">
                    📝 Text Format
                </button>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Download Statistics', modalContent);
}

function downloadStatsFormat(format) {
    closeModal('genericModal');
    window.location.href = `/download_statistics?session_id=${currentSession}&format=${format}`;
    showNotification(`Downloading statistics as ${format.toUpperCase()}...`, 'info');
}

function exportAllUserFeedback(format = 'json') {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    window.location.href = `/export_user_feedback?session_id=${currentSession}&format=${format}`;
    showNotification(`Exporting feedback as ${format.toUpperCase()}...`, 'info');
}

function showUserFeedbackManager() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    showNotification('User feedback manager loaded', 'info');
}

// DEPRECATED: toggleDarkMode() is now handled by core_fixes.js
// This function is disabled to prevent conflicts
// Dark mode functionality is managed exclusively by core_fixes.js
/*
function toggleDarkMode() {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark-mode', isDarkMode);

    const button = document.getElementById('darkModeToggle');
    if (button) {
        button.textContent = isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode';
        button.className = isDarkMode ? 'btn btn-warning' : 'btn btn-secondary';
    }

    localStorage.setItem('darkMode', isDarkMode.toString());
}
*/

function showShortcuts() {
    const modal = document.getElementById('shortcutsModal');
    if (modal) modal.style.display = 'block';
}

function showTutorial() {
    showModal('genericModal', '🔍 Interactive Tutorial', `
        <div>
            <h4>Welcome to the Document Analysis Tool!</h4>
            <p>This tool helps you review documents using the Hawkeye framework.</p>
            <ol>
                <li><strong>Upload Document:</strong> Drag and drop or click to upload a .docx file</li>
                <li><strong>Review Sections:</strong> Navigate through sections using the dropdown</li>
                <li><strong>Analyze Feedback:</strong> Review AI-generated feedback and accept/reject items</li>
                <li><strong>Add Custom Feedback:</strong> Use the form to add your own insights</li>
                <li><strong>Complete Review:</strong> Generate final document with comments</li>
            </ol>
        </div>
    `);
}

function showFAQ() {
    const modal = document.getElementById('faqModal');
    if (modal) modal.style.display = 'block';
}

function showPatterns() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    showProgress('Loading pattern analysis...');
    
    fetch(`/get_patterns?session_id=${currentSession}`)
    .then(response => response.json())
    .then(data => {
        hideProgress();
        if (data.success) {
            const patterns = data.patterns;
            
            const modalContent = `
                <div style="max-height: 70vh; overflow-y: auto;">
                    ${patterns.pattern_report_html || '<p>No patterns found yet. Review more documents to identify patterns.</p>'}
                </div>
            `;
            
            showModal('genericModal', '📊 Pattern Analysis', modalContent);
        } else {
            showNotification('Failed to load patterns: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        hideProgress();
        showNotification('Failed to load patterns: ' + error.message, 'error');
    });
}

// ❌ DELETED: Activity logs functions moved to global_function_fixes.js
// All activity logs functionality now centralized in ONE location
// See global_function_fixes.js for: showActivityLogs(), exportActivityLogs(), refreshActivityLogs()

function showLearning() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    showProgress('Loading AI learning status...');
    
    fetch(`/get_learning_status?session_id=${currentSession}&format=html`)
    .then(response => response.json())
    .then(data => {
        hideProgress();
        if (data.success) {
            const modalContent = `
                <div style="max-height: 70vh; overflow-y: auto;">
                    ${data.learning_html || '<p>No learning data available.</p>'}
                    <div style="text-align: center; margin-top: 20px;">
                        <button class="btn btn-info" onclick="exportLearningData()" style="margin: 5px;">📥 Export Learning Data</button>
                        <button class="btn btn-secondary" onclick="refreshLearning()" style="margin: 5px;">🔄 Refresh</button>
                    </div>
                </div>
            `;
            
            showModal('genericModal', '🧠 AI Learning System', modalContent);
        } else {
            showNotification('Failed to load learning status: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        hideProgress();
        showNotification('Failed to load learning status: ' + error.message, 'error');
    });
}

function resetSession() {
    if (confirm('Are you sure you want to reset the session? All progress will be lost.')) {
        fetch('/reset_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                analysisFile = null;
                guidelinesFile = null;
                chatHistory = [];
                currentSession = null;
                sections = [];
                currentSectionIndex = 0;
                
                const analysisFileName = document.getElementById('analysisFileName');
                const guidelinesFileName = document.getElementById('guidelinesFileName');
                const startBtn = document.getElementById('startAnalysisBtn');
                
                if (analysisFileName) analysisFileName.textContent = '';
                if (guidelinesFileName) guidelinesFileName.textContent = '';
                if (startBtn) startBtn.disabled = true;
                
                const mainContent = document.getElementById('mainContent');
                const statisticsPanel = document.getElementById('statisticsPanel');
                const actionButtons = document.getElementById('actionButtons');
                
                if (mainContent) mainContent.style.display = 'none';
                if (statisticsPanel) statisticsPanel.style.display = 'none';
                if (actionButtons) actionButtons.style.display = 'none';
                
                showNotification('Session reset successfully', 'success');
            } else {
                showNotification(data.error || 'Reset failed', 'error');
            }
        })
        .catch(error => {
            showNotification('Reset failed: ' + error.message, 'error');
        });
    }
}

// Helper functions for new features
function exportLogs() {
    // Use the new exportActivityLogs function
    exportActivityLogs();
}

function refreshLogs() {
    closeModal('genericModal');
    setTimeout(() => showActivityLogs(), 100);
}

function exportLearningData() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    fetch(`/get_learning_status?session_id=${currentSession}&format=json`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const exportData = {
                export_timestamp: new Date().toISOString(),
                session_id: currentSession,
                learning_status: data.learning_status,
                recommendations: data.recommendations
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `learning_data_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('Learning data exported successfully!', 'success');
        } else {
            showNotification('Export failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        showNotification('Export failed: ' + error.message, 'error');
    });
}

function refreshLearning() {
    closeModal('genericModal');
    setTimeout(() => showLearning(), 100);
}

// S3 Success Popup Function
function showS3SuccessPopup(s3ExportData) {
    const modalContent = `
        <div style="text-align: center; padding: 30px;">
            <div style="font-size: 4em; margin-bottom: 20px;">🎉</div>
            <h3 style="color: #28a745; margin-bottom: 20px;">S3 Export Successful!</h3>
            
            <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 20px; margin-bottom: 20px; text-align: left;">
                <h4 style="color: #155724; margin-bottom: 15px;">📦 Export Details</h4>
                <div style="margin-bottom: 10px;"><strong>Location:</strong> ${s3ExportData.location || 'S3 Bucket'}</div>
                <div style="margin-bottom: 10px;"><strong>Folder:</strong> ${s3ExportData.folder_name || 'Unknown'}</div>
                <div style="margin-bottom: 10px;"><strong>Files Uploaded:</strong> ${s3ExportData.total_files || 0}</div>
                <div style="margin-bottom: 10px;"><strong>Bucket:</strong> ${s3ExportData.bucket || 'felix-s3-bucket'}</div>
                ${s3ExportData.s3_path ? `<div style="margin-bottom: 10px;"><strong>S3 Path:</strong> ${s3ExportData.s3_path}</div>` : ''}
            </div>
            
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
                <h5 style="color: #856404; margin-bottom: 10px;">📋 What was saved:</h5>
                <ul style="text-align: left; color: #856404; margin: 0; padding-left: 20px;">
                    <li>Original document (before review)</li>
                    <li>Reviewed document (with comments)</li>
                    <li>All feedback data (accepted, rejected, custom)</li>
                    <li>Activity logs and chat history</li>
                    <li>Comprehensive analysis report</li>
                    <li>Guidelines document (if uploaded)</li>
                </ul>
            </div>
            
            <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                <button class="btn btn-success" onclick="testS3Connection()" style="padding: 12px 25px;">
                    🔗 Test S3 Connection
                </button>
                <button class="btn btn-info" onclick="showActivityLogs()" style="padding: 12px 25px;">
                    📋 View Activity Logs
                </button>
                <button class="btn btn-primary" onclick="closeModal('genericModal')" style="padding: 12px 25px;">
                    ✅ Continue
                </button>
            </div>
        </div>
    `;
    
    showModal('genericModal', '🎉 S3 Export Complete', modalContent);
}

// Export Activity Logs Function
// ❌ DELETED: exportActivityLogs, downloadActivityLogs, refreshActivityLogs
// All activity logs functions moved to global_function_fixes.js for centralization

// Test S3 Connection Function
function testS3Connection() {
    showProgress('Testing S3 connection...');
    
    fetch('/test_s3_connection')
    .then(response => response.json())
    .then(data => {
        hideProgress();
        
        if (data.success && data.s3_status) {
            const status = data.s3_status;
            let statusMessage = '';
            let statusColor = '';
            let statusIcon = '';
            
            if (status.connected && status.bucket_accessible) {
                statusMessage = `✅ S3 Connection Successful!\n\nBucket: ${status.bucket_name}\nStatus: Connected and accessible`;
                statusColor = '#28a745';
                statusIcon = '✅';
            } else if (status.connected && !status.bucket_accessible) {
                statusMessage = `⚠️ S3 Connected but Bucket Issues\n\nBucket: ${status.bucket_name}\nError: ${status.error || 'Bucket not accessible'}`;
                statusColor = '#ffc107';
                statusIcon = '⚠️';
            } else {
                statusMessage = `❌ S3 Connection Failed\n\nError: ${status.error || 'Unable to connect to S3'}`;
                statusColor = '#dc3545';
                statusIcon = '❌';
            }
            
            const modalContent = `
                <div style="text-align: center; padding: 30px;">
                    <div style="font-size: 4em; margin-bottom: 20px;">${statusIcon}</div>
                    <h3 style="color: ${statusColor}; margin-bottom: 20px;">S3 Connection Test</h3>
                    
                    <div style="background: ${statusColor === '#28a745' ? '#d4edda' : statusColor === '#ffc107' ? '#fff3cd' : '#f8d7da'}; 
                                border: 1px solid ${statusColor === '#28a745' ? '#c3e6cb' : statusColor === '#ffc107' ? '#ffeaa7' : '#f5c6cb'}; 
                                border-radius: 8px; padding: 20px; margin-bottom: 20px; white-space: pre-line;">
                        ${statusMessage}
                    </div>
                    
                    <div style="display: flex; gap: 15px; justify-content: center;">
                        <button class="btn btn-info" onclick="testS3Connection()" style="padding: 10px 20px;">
                            🔄 Test Again
                        </button>
                        <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="padding: 10px 20px;">
                            ✅ Close
                        </button>
                    </div>
                </div>
            `;
            
            showModal('genericModal', 'S3 Connection Test Results', modalContent);
        } else {
            showNotification('S3 connection test failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        hideProgress();
        showNotification('S3 connection test failed: ' + error.message, 'error');
    });
}

function exportPatterns() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    fetch(`/get_patterns?session_id=${currentSession}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const exportData = {
                export_timestamp: new Date().toISOString(),
                session_id: currentSession,
                patterns: data.patterns
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `patterns_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('Patterns exported successfully!', 'success');
        } else {
            showNotification('Export failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        showNotification('Export failed: ' + error.message, 'error');
    });
}

// Manual S3 Export Function (for testing)
function manualS3Export() {
    const sessionId = currentSession || window.currentSession || sessionStorage.getItem('currentSession');
    
    if (!sessionId) {
        showNotification('No active session', 'error');
        return;
    }
    
    if (confirm('Export current review data to S3? This will save all documents, feedback, and logs.')) {
        showProgress('Exporting to S3...');
        
        fetch('/export_to_s3', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        })
        .then(response => response.json())
        .then(data => {
            hideProgress();
            
            if (data.success && data.export_result) {
                if (data.export_result.success) {
                    showS3SuccessPopup(data.export_result);
                    showNotification('Manual S3 export completed successfully!', 'success');
                } else {
                    showNotification('S3 export failed: ' + (data.export_result.error || 'Unknown error'), 'error');
                }
            } else {
                showNotification('Export failed: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            hideProgress();
            showNotification('Export failed: ' + error.message, 'error');
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Button fixes loaded successfully');
    
    // Ensure all buttons have proper event listeners
    const buttons = document.querySelectorAll('button[onclick]');
    buttons.forEach(button => {
        const onclick = button.getAttribute('onclick');
        if (onclick && !window[onclick.split('(')[0]]) {
            console.warn(`Function ${onclick.split('(')[0]} not found for button:`, button);
        }
    });
    
    // Auto-sync session variables
    syncSessionVariables();
});