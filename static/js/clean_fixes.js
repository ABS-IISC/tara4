// Clean fixes for AI-Prism issues
// This file contains minimal fixes for the two main issues

// Global variables
let analysisFile = null;
let guidelinesFile = null;
let currentSession = null;
let sections = [];
let currentSectionIndex = 0;

// Fix 1: Remove popup and use clean modal for text highlighting feature
function showTextHighlightingGuide() {
    const content = `
        <div style="padding: 20px;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">🎨 Text Highlighting Guide</h3>
            <div style="background: #f8f9ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h4>How to Use:</h4>
                <p>1. Choose a color from the toolbar</p>
                <p>2. Select text in the document</p>
                <p>3. Add your comment</p>
                <p>4. Comments appear in Custom Feedback section</p>
            </div>
            <button class="btn btn-primary" onclick="closeModal('genericModal')">Got it!</button>
        </div>
    `;
    showModal('genericModal', 'Text Highlighting Guide', content);
}

// Fix 2: Working startAnalysis function
function startAnalysis() {
    console.log('Starting analysis...');
    
    if (!analysisFile) {
        showNotification('Please select a document first', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('document', analysisFile);
    
    if (guidelinesFile) {
        formData.append('guidelines', guidelinesFile);
    }
    
    // Show progress
    showProgress('Uploading document...');
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideProgress();

        if (data.success) {
            currentSession = data.session_id;
            sections = data.sections;

            // CRITICAL: Set currentSession in multiple scopes for reliability
            window.currentSession = data.session_id;
            sessionStorage.setItem('currentSession', data.session_id);

            console.log('✅ Session created:', data.session_id);
            console.log('✅ Sections loaded:', sections.length);

            showNotification('Document uploaded successfully!', 'success');
            showMainContent();

            if (sections.length > 0) {
                loadSection(0);
            }
        } else {
            showNotification('Upload failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        hideProgress();
        console.error('Upload error:', error);
        showNotification('Upload failed: ' + error.message, 'error');
    });
}

// Helper functions
function showProgress(message) {
    const container = document.getElementById('progressContainer');
    const text = document.getElementById('progressText');
    
    if (container) container.style.display = 'block';
    if (text) text.textContent = message;
}

function hideProgress() {
    const container = document.getElementById('progressContainer');
    if (container) container.style.display = 'none';
}

function showMainContent() {
    const elements = [
        'mainContent',
        'statisticsPanel', 
        'actionButtons',
        'customFeedbackSection'
    ];
    
    elements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = id === 'mainContent' ? 'grid' : 
                                   id === 'actionButtons' ? 'flex' : 'block';
        }
    });
}

function loadSection(index) {
    if (!sections || index < 0 || index >= sections.length) return;

    currentSectionIndex = index;
    const sectionName = sections[index];

    // Update section selector
    const select = document.getElementById('sectionSelect');
    if (select) select.selectedIndex = index + 1;

    // Show enhanced loading state with section name
    const content = document.getElementById('documentContent');
    if (content) {
        content.innerHTML = `
            <div style="padding: 40px; text-align: center; background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); border-radius: 15px; margin: 20px; border: 2px solid #4f46e5;">
                <div style="font-size: 3em; margin-bottom: 20px; animation: pulse 1.5s infinite;">🔄</div>
                <h2 style="color: #4f46e5; margin-bottom: 15px; font-size: 1.5em;">Analyzing Section</h2>
                <h3 style="color: #7c3aed; margin-bottom: 20px; font-weight: normal;">"${sectionName}"</h3>
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px auto; max-width: 500px; box-shadow: 0 4px 15px rgba(79, 70, 229, 0.2);">
                    <p style="color: #666; font-size: 1.1em; margin: 0;">
                        ⏳ Please wait while AI Prism analyzes this section...
                    </p>
                    <div style="margin-top: 15px;">
                        <div style="height: 4px; background: #e0e0e0; border-radius: 2px; overflow: hidden;">
                            <div style="height: 100%; background: linear-gradient(90deg, #4f46e5, #7c3aed); animation: loading 2s infinite;"></div>
                        </div>
                    </div>
                </div>
                <p style="color: #999; font-size: 0.9em; margin-top: 20px;">This usually takes 5-15 seconds...</p>
            </div>
            <style>
                @keyframes pulse {
                    0%, 100% { transform: scale(1); opacity: 1; }
                    50% { transform: scale(1.1); opacity: 0.8; }
                }
                @keyframes loading {
                    0% { transform: translateX(-100%); }
                    50% { transform: translateX(100%); }
                    100% { transform: translateX(-100%); }
                }
            </style>
        `;
    }

    const feedback = document.getElementById('feedbackContainer');
    if (feedback) {
        feedback.innerHTML = `
            <div style="text-align: center; padding: 30px; background: #f8f9ff; border-radius: 10px;">
                <p style="color: #666; font-size: 1.1em;">⏳ Generating AI feedback...</p>
            </div>
        `;
    }

    console.log(`🔍 Starting analysis for section: ${sectionName}`);

    // Fetch section content and analysis from backend
    fetch('/analyze_section', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: currentSession,
            section_name: sectionName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Display actual document content
            if (content) {
                const sectionContent = data.section_content || 'No content available';
                content.innerHTML = `
                    <div style="padding: 20px;">
                        <h2 style="color: #4f46e5; margin-bottom: 20px;">${sectionName}</h2>
                        <div style="white-space: pre-wrap; font-family: 'Times New Roman', serif; line-height: 1.8; text-align: justify;">
                            ${sectionContent}
                        </div>
                    </div>
                `;
            }

            // Display feedback items
            if (feedback) {
                const feedbackItems = data.feedback_items || [];
                if (feedbackItems.length > 0) {
                    feedback.innerHTML = feedbackItems.map((item, idx) => `
                        <div class="feedback-item" style="margin-bottom: 15px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #f8f9ff;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <strong style="color: #4f46e5;">${item.category || 'Feedback'}</strong>
                                <span class="badge badge-${item.type}" style="padding: 4px 8px; border-radius: 4px; font-size: 0.85em;">
                                    ${item.type || 'suggestion'}
                                </span>
                            </div>
                            <p style="margin: 10px 0;"><strong>Issue:</strong> ${item.description || ''}</p>
                            <p style="margin: 10px 0;"><strong>Suggestion:</strong> ${item.suggestion || ''}</p>
                            ${item.questions && item.questions.length > 0 ? `
                                <p style="margin: 10px 0;"><strong>Questions:</strong></p>
                                <ul style="margin: 5px 0 10px 20px;">
                                    ${item.questions.map(q => `<li>${q}</li>`).join('')}
                                </ul>
                            ` : ''}
                            <div style="margin-top: 10px;">
                                <button class="btn btn-success btn-sm" onclick="window.acceptFeedback('${item.id}', '${sectionName}')" style="margin-right: 5px;">✓ Accept</button>
                                <button class="btn btn-danger btn-sm" onclick="window.rejectFeedback('${item.id}', '${sectionName}')">✗ Reject</button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    feedback.innerHTML = '<p>No feedback items generated for this section.</p>';
                }
            }

            showNotification('Section loaded successfully!', 'success');
        } else {
            if (content) {
                content.innerHTML = `<div style="padding: 20px;"><p style="color: #e74c3c;">Error: ${data.error || 'Failed to load section'}</p></div>`;
            }
            if (feedback) {
                feedback.innerHTML = '<p>Unable to load feedback.</p>';
            }
            showNotification('Failed to load section: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Load section error:', error);
        if (content) {
            content.innerHTML = `<div style="padding: 20px;"><p style="color: #e74c3c;">Error loading section: ${error.message}</p></div>`;
        }
        if (feedback) {
            feedback.innerHTML = '<p>Error loading feedback.</p>';
        }
        showNotification('Error loading section: ' + error.message, 'error');
    });
}

// ❌ REMOVED: acceptFeedback and rejectFeedback functions
// These functions are now ONLY defined in global_function_fixes.js (single source of truth)
// All action button functions (accept, reject, revert, update) are centralized there
// This eliminates conflicts from multiple function definitions

function showModal(modalId, title, content) {
    const modal = document.getElementById(modalId);
    const titleEl = document.getElementById('genericModalTitle');
    const contentEl = document.getElementById('genericModalContent');
    
    if (titleEl) titleEl.textContent = title;
    if (contentEl) contentEl.innerHTML = content;
    if (modal) modal.style.display = 'block';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
}

function showNotification(message, type) {
    // Remove existing notifications
    document.querySelectorAll('.notification').forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10001;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 350px;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#2ecc71',
        error: '#e74c3c', 
        info: '#3498db',
        warning: '#f39c12'
    };
    notification.style.background = colors[type] || '#95a5a6';
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => notification.style.transform = 'translateX(0)', 100);
    
    // Hide notification after 4 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// File upload handlers
function handleAnalysisFileUpload(event) {
    const file = event.target.files[0];
    if (file && file.name.toLowerCase().endsWith('.docx')) {
        analysisFile = file;
        document.getElementById('analysisFileName').textContent = file.name;
        document.getElementById('startAnalysisBtn').disabled = false;
        showNotification('Analysis document ready!', 'success');
    } else {
        showNotification('Please select a .docx file', 'error');
    }
}

function handleGuidelinesFileUpload(event) {
    const file = event.target.files[0];
    if (file && file.name.toLowerCase().endsWith('.docx')) {
        guidelinesFile = file;
        document.getElementById('guidelinesFileName').textContent = file.name;
        showNotification('Guidelines document ready!', 'info');
    } else {
        showNotification('Please select a .docx file for guidelines', 'error');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Clean fixes loaded');
    
    // Set up file input handlers
    const fileInput = document.getElementById('fileInput');
    const guidelinesInput = document.getElementById('guidelinesInput');
    
    if (fileInput) fileInput.addEventListener('change', handleAnalysisFileUpload);
    if (guidelinesInput) guidelinesInput.addEventListener('change', handleGuidelinesFileUpload);
    
    // Override global functions
    window.startAnalysis = startAnalysis;
    window.showTextHighlightingGuide = showTextHighlightingGuide;
    
    console.log('Functions overridden successfully');
});