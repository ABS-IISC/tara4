// Missing JavaScript functions for AI-Prism buttons

// Function to show auto-suggestions for custom feedback
function showAutoSuggestions(value) {
    const dropdown = document.getElementById('suggestionDropdown');
    const type = document.getElementById('customType').value;
    
    if (!value || value.length < 3) {
        dropdown.style.display = 'none';
        return;
    }
    
    const suggestions = feedbackSuggestions[type] || [];
    const filteredSuggestions = suggestions.filter(s => 
        s.toLowerCase().includes(value.toLowerCase())
    );
    
    if (filteredSuggestions.length === 0) {
        dropdown.style.display = 'none';
        return;
    }
    
    dropdown.innerHTML = filteredSuggestions.map(suggestion => 
        `<div class="suggestion-item" onclick="selectSuggestion('${suggestion}')">${suggestion}</div>`
    ).join('');
    
    dropdown.style.display = 'block';
}

function selectSuggestion(suggestion) {
    document.getElementById('customDescription').value = suggestion;
    document.getElementById('suggestionDropdown').style.display = 'none';
}

// Function to show progress with rotating media
function showProgress(text) {
    const progressContainer = document.getElementById('progressContainer');
    const docProgress = document.getElementById('documentProgress');
    
    if (progressContainer) {
        progressContainer.style.display = 'block';
    }
    
    if (docProgress) {
        docProgress.style.display = 'block';
        startMediaRotation();
    }
}

function hideProgress() {
    const progressContainer = document.getElementById('progressContainer');
    const docProgress = document.getElementById('documentProgress');
    
    if (progressContainer) {
        progressContainer.style.display = 'none';
    }
    
    if (docProgress) {
        docProgress.style.display = 'none';
        stopMediaRotation();
    }
}

function startMediaRotation() {
    if (isMediaRotating) return;
    
    isMediaRotating = true;
    currentMediaIndex = 0;
    usedMediaIndices = [];
    
    rotateMedia();
    mediaRotationInterval = setInterval(rotateMedia, 5000);
}

function stopMediaRotation() {
    if (mediaRotationInterval) {
        clearInterval(mediaRotationInterval);
        mediaRotationInterval = null;
    }
    isMediaRotating = false;
}

function rotateMedia() {
    if (!showGraphics || loadingMediaWithContent.length === 0) return;
    
    // Get next unused media index
    if (usedMediaIndices.length >= loadingMediaWithContent.length) {
        usedMediaIndices = [];
    }
    
    let nextIndex;
    do {
        nextIndex = Math.floor(Math.random() * loadingMediaWithContent.length);
    } while (usedMediaIndices.includes(nextIndex));
    
    usedMediaIndices.push(nextIndex);
    currentMediaIndex = nextIndex;
    
    const media = loadingMediaWithContent[currentMediaIndex];
    const progressGif = document.getElementById('progressGif');
    const progressTitle = document.getElementById('progressTitle');
    const progressDesc = document.getElementById('progressDesc');
    
    if (progressGif && media.gif) {
        progressGif.src = media.gif;
        progressGif.onerror = function() {
            this.style.display = 'none';
        };
    }
    
    // Rotate between gif, joke, and math content
    const contentTypes = ['gif', 'joke', 'math'];
    const currentType = contentTypes[Math.floor(Math.random() * contentTypes.length)];
    
    if (progressDesc && media[currentType]) {
        progressDesc.textContent = media[currentType];
    }
}

// Function to show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Function to revert all feedback
function revertAllFeedback() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    if (confirm('Are you sure you want to revert ALL feedback decisions? This will reset all accepted/rejected items.')) {
        fetch('/revert_all_feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSession })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('All feedback reverted successfully!', 'success');
                // Reload current section to refresh display
                loadSection(currentSectionIndex);
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

// Function to update feedback (placeholder)
function updateFeedback() {
    showNotification('Feedback updated! Statistics refreshed.', 'success');
    updateStatistics();
}

// Function to show dashboard
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
                <div style="max-height: 70vh; overflow-y: auto;">
                    <h3 style="color: #667eea; margin-bottom: 20px;">📊 Analytics Dashboard</h3>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.totalDocuments}</div>
                            <div>Documents Analyzed</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.acceptedFeedback}</div>
                            <div>Accepted Feedback</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.rejectedFeedback}</div>
                            <div>Rejected Feedback</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                            <div style="font-size: 2.5em; font-weight: bold;">${dashboard.userFeedback}</div>
                            <div>User Added</div>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h4 style="color: #667eea; margin-bottom: 15px;">📈 Session Overview</h4>
                        <p><strong>Total Feedback:</strong> ${dashboard.totalFeedback}</p>
                        <p><strong>Sections Analyzed:</strong> ${dashboard.sectionsAnalyzed}</p>
                        <p><strong>Completion Rate:</strong> ${dashboard.totalFeedback > 0 ? Math.round(((dashboard.acceptedFeedback + dashboard.rejectedFeedback) / dashboard.totalFeedback) * 100) : 0}%</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                        <h4 style="color: #667eea; margin-bottom: 15px;">📋 Recent Activity</h4>
                        ${dashboard.recentActivity.length > 0 ? 
                            dashboard.recentActivity.slice(-5).map(activity => 
                                `<div style="padding: 8px 0; border-bottom: 1px solid #eee;">
                                    <strong>${activity.action}:</strong> ${activity.details}
                                    <small style="color: #666; display: block;">${new Date(activity.timestamp).toLocaleString()}</small>
                                </div>`
                            ).join('') : 
                            '<p style="color: #666; text-align: center;">No recent activity</p>'
                        }
                    </div>
                </div>
            `;
            
            showModal('genericModal', '📊 Analytics Dashboard', modalContent);
        } else {
            showNotification('Failed to load dashboard data', 'error');
        }
    })
    .catch(error => {
        showNotification('Dashboard error: ' + error.message, 'error');
    });
}

// Function to delete document
function deleteDocument() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    if (confirm('Are you sure you want to delete the current document? Guidelines will be preserved.')) {
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
                showNotification('Document deleted successfully! Guidelines preserved.', 'success');
                // Reset UI to upload state
                document.getElementById('mainContent').style.display = 'none';
                document.getElementById('statisticsPanel').style.display = 'none';
                document.getElementById('actionButtons').style.display = 'none';
                document.getElementById('analysisFileName').textContent = '';
                document.getElementById('startAnalysisBtn').disabled = true;
            } else {
                showNotification(data.error || 'Delete failed', 'error');
            }
        })
        .catch(error => {
            showNotification('Delete failed: ' + error.message, 'error');
        });
    }
}

// Function to provide feedback on tool
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
                <label style="font-weight: bold; margin-bottom: 5px; display: block;">What did you like most?</label>
                <textarea id="toolLikes" placeholder="Tell us what worked well..." style="width: 100%; height: 80px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"></textarea>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="font-weight: bold; margin-bottom: 5px; display: block;">What could be improved?</label>
                <textarea id="toolImprovements" placeholder="Share your suggestions for improvement..." style="width: 100%; height: 80px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"></textarea>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="font-weight: bold; margin-bottom: 5px; display: block;">Would you recommend AI-Prism to others?</label>
                <select id="toolRecommend" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <option value="yes">Yes, definitely</option>
                    <option value="maybe">Maybe</option>
                    <option value="no">No</option>
                </select>
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
    const likes = document.getElementById('toolLikes').value;
    const improvements = document.getElementById('toolImprovements').value;
    const recommend = document.getElementById('toolRecommend').value;
    
    const feedbackData = {
        rating: rating,
        likes: likes,
        improvements: improvements,
        recommend: recommend,
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
            showNotification('Thank you for your feedback! It helps us improve AI-Prism.', 'success');
            closeModal('genericModal');
        } else {
            showNotification('Failed to submit feedback. Please try again.', 'error');
        }
    })
    .catch(error => {
        showNotification('Feedback submission failed: ' + error.message, 'error');
    });
}

// Function to complete review
function completeReview() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    if (confirm('Complete the review and generate the final document with comments?')) {
        showProgress('Generating final document...');
        
        fetch('/complete_review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSession })
        })
        .then(response => response.json())
        .then(data => {
            hideProgress();
            
            if (data.success) {
                showNotification(`Review completed! Document generated with ${data.comments_count} comments.`, 'success');
                
                // Enable download button
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
            showNotification('Review completion failed: ' + error.message, 'error');
        });
    }
}

// Function to export chat history
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

// Function to download guidelines
function downloadGuidelines() {
    if (!currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    window.location.href = `/download_guidelines?session_id=${currentSession}`;
    showNotification('Downloading guidelines...', 'info');
}

// Function to export statistics
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