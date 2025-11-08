// Missing Functions Implementation for AI-Prism Document Analysis Tool
// This file contains all the missing functions that are referenced in the HTML but not implemented

console.log('Loading missing functions...');

// Global variables (ensure they exist)
window.currentSession = window.currentSession || null;
window.sections = window.sections || [];
window.currentSectionIndex = window.currentSectionIndex || 0;
window.selectedFeedbackId = window.selectedFeedbackId || null;
window.feedbackStates = window.feedbackStates || {};
window.analysisFile = window.analysisFile || null;
window.guidelinesFile = window.guidelinesFile || null;
window.chatHistory = window.chatHistory || [];
window.userFeedbackHistory = window.userFeedbackHistory || [];
window.finalDocumentData = window.finalDocumentData || null;
window.isDarkMode = window.isDarkMode || false;
window.documentZoom = window.documentZoom || 100;

// Core missing functions
function startAnalysis() {
    console.log('startAnalysis called');
    
    if (!window.analysisFile) {
        showNotification('Please select a document for analysis', 'error');
        return;
    }
    
    const startBtn = document.getElementById('startAnalysisBtn');
    if (startBtn) {
        startBtn.disabled = true;
        startBtn.textContent = 'Starting...';
    }
    
    handleFileSelection(window.analysisFile, window.guidelinesFile);
}

function handleFileSelection(analysisFile, guidelinesFile = null) {
    console.log('handleFileSelection called');
    
    if (guidelinesFile) {
        showGuidelinesPreferenceModal(analysisFile, guidelinesFile);
        return;
    }
    
    uploadAndAnalyze(analysisFile, guidelinesFile, 'both');
}

function showGuidelinesPreferenceModal(analysisFile, guidelinesFile) {
    const modalContent = `
        <div style="text-align: center; padding: 20px;">
            <h3 style="color: #667eea; margin-bottom: 20px;">📄 Guidelines Document Detected</h3>
            <p style="margin-bottom: 30px;">You've uploaded a custom guidelines document. How should AI-Prism use it?</p>
            
            <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
                <button class="btn btn-primary" onclick="useGuidelinesPreference('new_only')" style="padding: 15px 25px;">
                    🆕 Use Only New Guidelines
                </button>
                <button class="btn btn-success" onclick="useGuidelinesPreference('both')" style="padding: 15px 25px;">
                    🔄 Use Both Old & New Guidelines
                </button>
                <button class="btn btn-secondary" onclick="useGuidelinesPreference('old_only')" style="padding: 15px 25px;">
                    📅 Use Only Default Guidelines
                </button>
            </div>
            
            <p style="margin-top: 20px; font-size: 0.9em; color: #666;">
                AI-Prism will analyze your document according to your preference.
            </p>
        </div>
    `;
    
    showModal('genericModal', 'Guidelines Preference', modalContent);
    
    window.tempAnalysisFile = analysisFile;
    window.tempGuidelinesFile = guidelinesFile;
}

function useGuidelinesPreference(preference) {
    closeModal('genericModal');
    
    const analysisFile = window.tempAnalysisFile;
    const guidelinesFile = window.tempGuidelinesFile;
    
    uploadAndAnalyze(analysisFile, guidelinesFile, preference);
}

function uploadAndAnalyze(analysisFile, guidelinesFile, guidelinesPreference) {
    console.log('uploadAndAnalyze called');
    
    if (!analysisFile) {
        showNotification('No analysis file provided', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('document', analysisFile);
    formData.append('guidelines_preference', guidelinesPreference);
    
    if (guidelinesFile && guidelinesPreference !== 'old_only') {
        formData.append('guidelines', guidelinesFile);
    }

    showProgress('Uploading documents...');

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.currentSession = data.session_id;
            window.sections = data.sections;
            
            populateSectionSelect(data.sections);
            showMainContent();
            
            startComprehensiveAnalysis();
            
            let message = 'Documents uploaded successfully!';
            if (data.guidelines_uploaded) {
                message += ` Using ${guidelinesPreference.replace('_', ' ')} guidelines.`;
            }
            showNotification(message, 'success');
        } else {
            showNotification(data.error || 'Upload failed', 'error');
            hideProgress();
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        showNotification('Upload failed: ' + error.message, 'error');
        hideProgress();
    });
}

function populateSectionSelect(sectionNames) {
    const select = document.getElementById('sectionSelect');
    if (!select) return;
    
    select.innerHTML = '<option value="">Select a section...</option>';
    
    sectionNames.forEach((section, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = section;
        select.appendChild(option);
    });
}

function showMainContent() {
    const mainContent = document.getElementById('mainContent');
    const statisticsPanel = document.getElementById('statisticsPanel');
    const actionButtons = document.getElementById('actionButtons');
    
    if (mainContent) mainContent.style.display = 'grid';
    if (statisticsPanel) statisticsPanel.style.display = 'block';
    if (actionButtons) actionButtons.style.display = 'flex';
    
    updateStatistics();
}

function startComprehensiveAnalysis() {
    showProgress('Starting comprehensive analysis...');
    
    window.currentAnalysisStep = 0;
    analyzeNextSection();
}

function analyzeNextSection() {
    if (window.currentAnalysisStep >= window.sections.length) {
        completeAnalysis();
        return;
    }
    
    const sectionName = window.sections[window.currentAnalysisStep];
    const progressPercent = ((window.currentAnalysisStep + 1) / window.sections.length) * 100;
    
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (progressFill) progressFill.style.width = progressPercent + '%';
    if (progressText) progressText.textContent = `Analyzing: ${sectionName} (${window.currentAnalysisStep + 1}/${window.sections.length})`;
    
    fetch('/analyze_section', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: window.currentSession,
            section_name: sectionName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.sectionData = window.sectionData || {};
            window.sectionData[sectionName] = {
                content: data.section_content,
                feedback: data.feedback_items
            };
            
            window.currentAnalysisStep++;
            setTimeout(analyzeNextSection, 1000);
        } else {
            window.currentAnalysisStep++;
            setTimeout(analyzeNextSection, 500);
        }
    })
    .catch(error => {
        console.error('Analysis error:', error);
        window.currentAnalysisStep++;
        setTimeout(analyzeNextSection, 500);
    });
}

function completeAnalysis() {
    const progressText = document.getElementById('progressText');
    if (progressText) progressText.textContent = 'Analysis Complete!';
    
    setTimeout(() => {
        hideProgress();
        loadSection(0);
        updateStatistics();
        const completeBtn = document.getElementById('completeReviewBtn');
        if (completeBtn) completeBtn.disabled = false;
        showNotification('Comprehensive analysis completed! Navigate through sections to review feedback.', 'success');
    }, 2000);
}

function loadSection(index) {
    console.log('loadSection called with index:', index);
    
    if (index < 0 || index >= window.sections.length) return;
    
    window.currentSectionIndex = index;
    const sectionName = window.sections[index];
    
    const sectionSelect = document.getElementById('sectionSelect');
    if (sectionSelect) sectionSelect.value = index;
    
    const userFeedbackDisplay = document.getElementById('userFeedbackDisplay');
    if (userFeedbackDisplay) userFeedbackDisplay.innerHTML = '';
    
    if (window.sectionData && window.sectionData[sectionName]) {
        const data = window.sectionData[sectionName];
        displaySectionContent(data.content, sectionName);
        displayFeedback(data.feedback, sectionName);
        updateRiskIndicator(data.feedback);
        loadUserFeedbackForSection(sectionName);
    } else {
        showProgress('Loading section...');
        
        fetch('/analyze_section', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: window.currentSession,
                section_name: sectionName
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displaySectionContent(data.section_content, sectionName);
                displayFeedback(data.feedback_items, sectionName);
                updateRiskIndicator(data.feedback_items);
                loadUserFeedbackForSection(sectionName);
            }
            hideProgress();
        })
        .catch(error => {
            hideProgress();
            showNotification('Failed to load section: ' + error.message, 'error');
        });
    }
}

function displaySectionContent(content, sectionName) {
    const container = document.getElementById('documentContent');
    if (!container) return;
    
    const formattedContent = content
        .replace(/\n\n/g, '</p><p style="margin: 12pt 0; text-align: justify;">')
        .replace(/\n/g, '<br>')
        .replace(/^/, '<p style="margin: 12pt 0; text-align: justify;">')
        .replace(/$/, '</p>');
    
    container.innerHTML = `
        <button onclick="expandDocument()" style="position: absolute; top: 10px; right: 10px; background: #667eea; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 12px; z-index: 10;">🔍 Expand</button>
        <div class="document-inner" style="background: inherit; padding: 20px; margin: 0; box-shadow: 0 0 10px rgba(0,0,0,0.1); position: relative;">
            <div style="text-align: center; margin-bottom: 20px; border-bottom: 1pt solid currentColor; padding-bottom: 12pt;">
                <h1 style="font-family: 'Times New Roman', serif; font-size: 16pt; font-weight: bold; margin: 0; text-transform: uppercase;">${sectionName}</h1>
            </div>
            
            <div id="documentText" style="font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.5; text-align: justify; user-select: text; -webkit-user-select: text; -moz-user-select: text; -ms-user-select: text;">
                ${formattedContent}
            </div>
            
            <div style="position: absolute; bottom: 10px; right: 20px; font-family: 'Times New Roman', serif; font-size: 10pt; opacity: 0.7;">
                Page ${window.currentSectionIndex + 1}
            </div>
        </div>
    `;
}

function displayFeedback(feedbackItems, sectionName) {
    const container = document.getElementById('feedbackContainer');
    if (!container) return;
    
    if (!feedbackItems || feedbackItems.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; background: #f0fff4; border-radius: 8px;">
                <p style="color: #2ecc71; font-size: 16px;">
                    ✓ No issues found in this section based on Hawkeye criteria
                </p>
            </div>
        `;
        return;
    }

    let html = '';
    feedbackItems.forEach(item => {
        const riskClass = `risk-${item.risk_level.toLowerCase()}`;
        const typeClass = `type-${item.type}`;
        
        html += `
            <div class="feedback-item" data-feedback-id="${item.id}" onclick="selectFeedback('${item.id}')">
                <div class="feedback-header">
                    <div class="feedback-meta">
                        <span class="feedback-type ${typeClass}">${item.type}</span>
                        <span class="risk-indicator ${riskClass}">${item.risk_level} Risk</span>
                        <span style="color: #7f8c8d; font-size: 0.9em;">${item.category}</span>
                    </div>
                </div>
                <p><strong>Description:</strong> ${item.description}</p>
                ${item.suggestion ? `<p><strong>Suggestion:</strong> ${item.suggestion}</p>` : ''}
                ${item.example ? `<p><strong>Example:</strong> ${item.example}</p>` : ''}
                ${item.questions && item.questions.length > 0 ? `
                    <div>
                        <strong>Key Questions:</strong>
                        <ul>
                            ${item.questions.map(q => `<li>${q}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                ${item.hawkeye_refs && item.hawkeye_refs.length > 0 ? `
                    <p><strong>Hawkeye References:</strong> ${item.hawkeye_refs.map(ref => `#${ref}`).join(', ')}</p>
                ` : ''}
                <p><small>Confidence: ${Math.round(item.confidence * 100)}%</small></p>
                <div class="feedback-actions">
                    <button class="btn btn-success" onclick="acceptFeedback('${item.id}', event)">✓ Accept</button>
                    <button class="btn btn-danger" onclick="rejectFeedback('${item.id}', event)">✗ Reject</button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function selectFeedback(feedbackId) {
    document.querySelectorAll('.feedback-item').forEach(item => {
        item.style.border = '';
    });
    
    const selectedItem = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
    if (selectedItem) {
        selectedItem.style.border = '2px solid #667eea';
        window.selectedFeedbackId = feedbackId;
    }
}

function acceptFeedback(feedbackId, event) {
    if (event) event.stopPropagation();
    
    fetch('/accept_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: window.currentSession,
            section_name: window.sections[window.currentSectionIndex],
            feedback_id: feedbackId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Feedback accepted!', 'success');
            updateFeedbackStatus(feedbackId, 'accepted');
            updateStatistics();
        } else {
            showNotification(data.error || 'Accept failed', 'error');
        }
    })
    .catch(error => {
        showNotification('Accept failed: ' + error.message, 'error');
    });
}

function rejectFeedback(feedbackId, event) {
    if (event) event.stopPropagation();
    
    fetch('/reject_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: window.currentSession,
            section_name: window.sections[window.currentSectionIndex],
            feedback_id: feedbackId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Feedback rejected!', 'info');
            updateFeedbackStatus(feedbackId, 'rejected');
            updateStatistics();
        } else {
            showNotification(data.error || 'Reject failed', 'error');
        }
    })
    .catch(error => {
        showNotification('Reject failed: ' + error.message, 'error');
    });
}

function updateFeedbackStatus(feedbackId, status) {
    const feedbackItem = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
    if (feedbackItem) {
        const actions = feedbackItem.querySelector('.feedback-actions');
        const statusColor = status === 'accepted' ? '#2ecc71' : '#e74c3c';
        const statusText = status === 'accepted' ? '✓ Accepted' : '✗ Rejected';
        
        if (!window.feedbackStates[feedbackId]) {
            window.feedbackStates[feedbackId] = {
                originalHtml: actions.innerHTML,
                status: 'pending'
            };
        }
        window.feedbackStates[feedbackId].status = status;
        
        actions.innerHTML = `
            <span style="color: ${statusColor}; font-weight: bold;">${statusText}</span>
        `;
        feedbackItem.style.opacity = '0.7';
    }
}

function updateRiskIndicator(feedbackItems) {
    const indicator = document.getElementById('riskIndicator');
    if (!indicator || !feedbackItems) return;
    
    const highRisk = feedbackItems.filter(item => item.risk_level === 'High').length;
    const mediumRisk = feedbackItems.filter(item => item.risk_level === 'Medium').length;
    const lowRisk = feedbackItems.filter(item => item.risk_level === 'Low').length;
    
    if (highRisk > 0) {
        indicator.className = 'risk-indicator risk-high';
        indicator.textContent = `High Risk (${highRisk})`;
    } else if (mediumRisk > 0) {
        indicator.className = 'risk-indicator risk-medium';
        indicator.textContent = `Medium Risk (${mediumRisk})`;
    } else {
        indicator.className = 'risk-indicator risk-low';
        indicator.textContent = `Low Risk (${lowRisk})`;
    }
}

function loadUserFeedbackForSection(sectionName) {
    // This function would load user feedback for the current section
    console.log('loadUserFeedbackForSection called for:', sectionName);
}

function updateStatistics() {
    console.log('updateStatistics called');
    
    if (!window.currentSession) return;
    
    fetch(`/get_statistics?session_id=${window.currentSession}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayStatistics(data.statistics);
        }
    })
    .catch(error => {
        console.error('Statistics update failed:', error);
    });
}

function displayStatistics(stats) {
    const container = document.getElementById('statsGrid');
    if (!container) return;
    
    container.innerHTML = `
        <div class="stat-item" onclick="showStatBreakdown('total_feedback')">
            <div class="stat-number">${stats.total_feedback || 0}</div>
            <div class="stat-label">Total Feedback</div>
        </div>
        <div class="stat-item" onclick="showStatBreakdown('high_risk')">
            <div class="stat-number" style="color: #e74c3c;">${stats.high_risk || 0}</div>
            <div class="stat-label">High Risk</div>
        </div>
        <div class="stat-item" onclick="showStatBreakdown('medium_risk')">
            <div class="stat-number" style="color: #f39c12;">${stats.medium_risk || 0}</div>
            <div class="stat-label">Medium Risk</div>
        </div>
        <div class="stat-item" onclick="showStatBreakdown('low_risk')">
            <div class="stat-number" style="color: #2ecc71;">${stats.low_risk || 0}</div>
            <div class="stat-label">Low Risk</div>
        </div>
        <div class="stat-item" onclick="showStatBreakdown('accepted')">
            <div class="stat-number" style="color: #2ecc71;">${stats.accepted || 0}</div>
            <div class="stat-label">Accepted</div>
        </div>
    `;
}

function showStatBreakdown(statType) {
    if (!window.currentSession) return;
    
    fetch(`/get_statistics_breakdown?session_id=${window.currentSession}&stat_type=${statType}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showModal('genericModal', `${statType.replace('_', ' ').toUpperCase()} Breakdown`, data.breakdown_html);
        }
    })
    .catch(error => {
        showNotification('Failed to load breakdown: ' + error.message, 'error');
    });
}

// Navigation functions
function nextSection() {
    if (window.currentSectionIndex < window.sections.length - 1) {
        loadSection(window.currentSectionIndex + 1);
    }
}

function previousSection() {
    if (window.currentSectionIndex > 0) {
        loadSection(window.currentSectionIndex - 1);
    }
}

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    const activeTab = document.querySelector(`.tab:nth-child(${tabName === 'feedback' ? '1' : '2'})`);
    const activeContent = document.getElementById(tabName === 'feedback' ? 'feedbackTab' : 'chatTab');
    
    if (activeTab) activeTab.classList.add('active');
    if (activeContent) activeContent.classList.add('active');
}

// Chat functions
function sendChatMessage() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    addChatMessage(message, 'user');
    input.value = '';
    
    if (!window.currentSession) {
        addChatMessage('Please upload a document first to start chatting.', 'assistant');
        return;
    }
    
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: window.currentSession,
            message: message,
            current_section: window.sections[window.currentSectionIndex] || null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addChatMessage(data.response, 'assistant');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    })
    .catch(error => {
        addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
    });
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

function addChatMessage(message, sender) {
    const container = document.getElementById('chatContainer');
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const timestamp = new Date().toLocaleTimeString();
    
    if (sender === 'user') {
        messageDiv.innerHTML = `<strong>👤 You:</strong> <small style="opacity: 0.7;">${timestamp}</small><br>${message}`;
        messageDiv.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        messageDiv.style.color = 'white';
        messageDiv.style.borderRadius = '12px';
        messageDiv.style.marginLeft = 'auto';
        messageDiv.style.marginRight = '0';
    } else {
        messageDiv.innerHTML = `<strong>🤖 AI-Prism:</strong> <small style="opacity: 0.7;">${timestamp}</small><br>${message}`;
        messageDiv.style.background = 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)';
        messageDiv.style.color = 'white';
        messageDiv.style.borderRadius = '12px';
        messageDiv.style.marginLeft = '0';
        messageDiv.style.marginRight = 'auto';
    }
    
    messageDiv.style.padding = '12px';
    messageDiv.style.marginBottom = '15px';
    messageDiv.style.maxWidth = '80%';
    messageDiv.style.boxShadow = '0 3px 10px rgba(0,0,0,0.2)';
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

// Custom feedback functions
function addCustomFeedback() {
    const type = document.getElementById('customType')?.value;
    const category = document.getElementById('customCategory')?.value;
    const description = document.getElementById('customDescription')?.value?.trim();
    
    if (!description) {
        showNotification('Please enter feedback description', 'error');
        return;
    }
    
    if (!window.currentSession) {
        showNotification('No active session', 'error');
        return;
    }
    
    fetch('/add_custom_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: window.currentSession,
            section_name: window.sections[window.currentSectionIndex],
            type: type,
            category: category,
            description: description
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Custom feedback added!', 'success');
            document.getElementById('customDescription').value = '';
            updateStatistics();
        } else {
            showNotification(data.error || 'Add feedback failed', 'error');
        }
    })
    .catch(error => {
        showNotification('Add feedback failed: ' + error.message, 'error');
    });
}

// Document expansion
function expandDocument() {
    const container = document.getElementById('documentContent');
    if (!container) return;
    
    const content = container.innerHTML;
    
    const modalContent = `
        <div style="max-height: 90vh; overflow-y: auto; padding: 20px;">
            <div class="expanded-document" style="background: inherit; padding: 40px; margin: 0 auto; max-width: 8.5in; box-shadow: 0 0 20px rgba(0,0,0,0.2);">
                ${content.replace('<button onclick="expandDocument()"', '<button onclick="closeModal(\'genericModal\')"').replace('🔍 Expand', '✖ Close')}
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Document Viewer', modalContent);
}

// Zoom functions
function zoomIn() {
    if (window.documentZoom < 200) {
        window.documentZoom += 25;
        applyZoom();
    }
}

function zoomOut() {
    if (window.documentZoom > 50) {
        window.documentZoom -= 25;
        applyZoom();
    }
}

function resetZoom() {
    window.documentZoom = 100;
    applyZoom();
}

function applyZoom() {
    const docContent = document.getElementById('documentContent');
    const zoomLevel = document.getElementById('zoomLevel');
    
    if (docContent) {
        docContent.style.transform = `scale(${window.documentZoom / 100})`;
        docContent.style.transformOrigin = 'top left';
        docContent.style.width = `${10000 / window.documentZoom}%`;
    }
    
    if (zoomLevel) {
        zoomLevel.textContent = `${window.documentZoom}%`;
    }
}

// Utility functions
function showProgress(message) {
    const progressContainer = document.getElementById('progressContainer');
    const progressText = document.getElementById('progressText');
    
    if (progressContainer) progressContainer.style.display = 'block';
    if (progressText) progressText.textContent = message;
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
    if (modal) modal.style.display = 'block';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
}

function showNotification(message, type = 'info') {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    const colors = {
        'success': '#2ecc71',
        'error': '#e74c3c',
        'info': '#3498db',
        'warning': '#f39c12'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1001;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
        background: ${colors[type] || colors.info};
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Missing functions loaded successfully');
    
    // Set up file input handlers
    const fileInput = document.getElementById('fileInput');
    const guidelinesInput = document.getElementById('guidelinesInput');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file && file.name.toLowerCase().endsWith('.docx')) {
                window.analysisFile = file;
                document.getElementById('analysisFileName').textContent = file.name;
                document.getElementById('startAnalysisBtn').disabled = false;
                showNotification('Analysis document ready!', 'success');
            } else {
                showNotification('Please select a .docx file', 'error');
            }
        });
    }
    
    if (guidelinesInput) {
        guidelinesInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file && file.name.toLowerCase().endsWith('.docx')) {
                window.guidelinesFile = file;
                document.getElementById('guidelinesFileName').textContent = file.name;
                showNotification('Guidelines document ready!', 'info');
            } else {
                showNotification('Please select a .docx file for guidelines', 'error');
            }
        });
    }
    
    // Set up section select handler
    const sectionSelect = document.getElementById('sectionSelect');
    if (sectionSelect) {
        sectionSelect.addEventListener('change', function() {
            const selectedIndex = this.selectedIndex - 1;
            if (selectedIndex >= 0) {
                loadSection(selectedIndex);
            }
        });
    }
    
    // Load dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        window.isDarkMode = true;
        document.body.classList.add('dark-mode');
        const button = document.getElementById('darkModeToggle');
        if (button) {
            button.textContent = '☀️ Light Mode';
            button.className = 'btn btn-warning';
        }
    }
});

// Text Highlighting Feature Instructions
function showTextHighlightingFeature() {
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
                            <h5 style="color: #ec4899; margin-bottom: 10px;">💬 Step 3: Save & Add Comment</h5>
                            <p style="margin: 0; color: #555;">Click the "Save & Comment" button that appears. A dialog will open where you can add your specific feedback about the highlighted text.</p>
                        </div>
                        
                        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #f59e0b; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                            <h5 style="color: #f59e0b; margin-bottom: 10px;">🔄 Step 4: Manage Highlights</h5>
                            <p style="margin: 0; color: #555;">Click existing highlights to view/edit comments. Use "Clear All" to remove all highlights, or remove individual ones as needed.</p>
                        </div>
                    </div>
                </div>
                
                <div style="background: rgba(79, 70, 229, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                    <h5 style="color: #4f46e5; margin-bottom: 15px; font-size: 1.2em;">💡 Advanced Tips & Best Practices:</h5>
                    <div style="text-align: left; color: #555; line-height: 1.7;">
                        • <strong>Color Coding:</strong> Use different colors for different feedback types (e.g., Yellow for suggestions, Red for critical issues)<br>
                        • <strong>Automatic Integration:</strong> All highlighted comments automatically appear in your "Custom Feedback" section<br>
                        • <strong>Click to Edit:</strong> Click any existing highlight to view, edit, or add additional comments<br>
                        • <strong>Persistent Storage:</strong> Your highlights are saved with your review session<br>
                        • <strong>Export Ready:</strong> Highlighted feedback is included in your final document export<br>
                        • <strong>Section Specific:</strong> Highlights are organized by document section for easy navigation
                    </div>
                </div>
                
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%); padding: 15px; border-radius: 10px; border: 2px solid #28a745;">
                    <h5 style="color: #28a745; margin-bottom: 10px;">✨ Why Use Text Highlighting?</h5>
                    <div style="text-align: left; color: #155724; font-size: 0.95em; line-height: 1.6;">
                        ✓ Provide precise, context-specific feedback<br>
                        ✓ Visually organize your review comments<br>
                        ✓ Create a clear audit trail of your analysis<br>
                        ✓ Enhance collaboration with specific text references
                    </div>
                </div>
            </div>
            
            <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                <button class="btn btn-primary" onclick="closeModal('genericModal')" style="padding: 12px 25px; border-radius: 20px; font-weight: 600;">
                    ✨ Start Using Highlights
                </button>
                <button class="btn btn-info" onclick="resetHighlightingTutorial()" style="padding: 12px 25px; border-radius: 20px;">
                    🔄 Reset Tutorial
                </button>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Text Highlighting Feature Guide', modalContent);
}

function resetHighlightingTutorial() {
    localStorage.removeItem('hasSeenTextHighlightingPopup');
    showNotification('Tutorial reset! The startup popup will show again on next page load.', 'success');
    closeModal('genericModal');
}

console.log('Missing functions implementation loaded successfully');