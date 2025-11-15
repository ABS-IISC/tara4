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

// Core missing functions - Updated to use new progress system
function startAnalysis() {
    console.log('startAnalysis called - using new progress system');
    
    if (!window.analysisFile) {
        showNotification('Please select a document for analysis', 'error');
        return;
    }
    
    const startBtn = document.getElementById('startAnalysisBtn');
    if (startBtn) {
        startBtn.disabled = true;
        startBtn.textContent = 'Starting...';
    }
    
    // Use the new progress system from progress_functions.js
    if (typeof window.startAnalysis !== 'undefined' && window.startAnalysis !== startAnalysis) {
        // Call the new progress system function
        window.startAnalysis();
    } else {
        // Fallback to original system
        handleFileSelection(window.analysisFile, window.guidelinesFile);
    }
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
    
    // Clean up temp variables
    window.tempAnalysisFile = null;
    window.tempGuidelinesFile = null;
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
            // Set session in multiple places to ensure compatibility
            window.currentSession = data.session_id;
            currentSession = data.session_id; // For button_fixes.js compatibility
            sessionStorage.setItem('currentSession', data.session_id);
            
            window.sections = data.sections;
            sections = data.sections; // For button_fixes.js compatibility
            
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
    const customFeedbackSection = document.getElementById('customFeedbackSection');
    
    if (mainContent) mainContent.style.display = 'grid';
    if (statisticsPanel) statisticsPanel.style.display = 'block';
    if (actionButtons) actionButtons.style.display = 'flex';
    
    // CRITICAL: Show the custom feedback section in the highlighted area
    if (customFeedbackSection) {
        customFeedbackSection.style.display = 'block';
        console.log('✅ Custom feedback section made visible');
    } else {
        console.error('❌ Custom feedback section not found - check ID: customFeedbackSection');
    }
    
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
    
    // Update progress bar
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (progressFill) progressFill.style.width = progressPercent + '%';
    if (progressText) progressText.textContent = `🔍 Analyzing: ${sectionName} (${window.currentAnalysisStep + 1}/${window.sections.length}) - ${Math.round(progressPercent)}%`;
    
    // Show detailed progress in document progress panel
    showSectionLoadingProgress(sectionName);
    
    // Update detailed progress
    const progressTitle = document.getElementById('progressTitle');
    const progressDesc = document.getElementById('progressDesc');
    
    if (progressTitle) {
        progressTitle.textContent = `🤖 Analyzing...`;
    }

    if (progressDesc) {
        const percent = Math.round(((window.currentAnalysisStep + 1) / window.sections.length) * 100);
        progressDesc.textContent = `${percent}% complete - Section ${window.currentAnalysisStep + 1} of ${window.sections.length}`;
    }
    
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
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.text();
    })
    .then(text => {
        let data;
        try {
            data = JSON.parse(text);
        } catch (jsonError) {
            console.error('JSON Parse Error in analysis:', jsonError);
            console.error('Response text:', text);
            throw new Error('Invalid JSON response during analysis');
        }
        
        if (data.success) {
            window.sectionData = window.sectionData || {};
            window.sectionData[sectionName] = {
                content: data.section_content,
                feedback: data.feedback_items
            };
            
            // Show success message
            const feedbackCount = data.feedback_items ? data.feedback_items.length : 0;
            if (progressDesc) {
                progressDesc.textContent = `✅ "${sectionName}" analysis complete! Generated ${feedbackCount} feedback items.`;
            }
            
            window.currentAnalysisStep++;
            
            // Continue with next section after showing success briefly
            setTimeout(() => {
                hideSectionLoadingProgress();
                setTimeout(analyzeNextSection, 500);
            }, 1500);
        } else {
            console.warn(`Analysis failed for section ${sectionName}:`, data.error);
            if (progressDesc) {
                progressDesc.textContent = `⚠️ "${sectionName}" analysis had issues. Continuing with next section...`;
            }
            
            window.currentAnalysisStep++;
            setTimeout(() => {
                hideSectionLoadingProgress();
                setTimeout(analyzeNextSection, 1000);
            }, 1000);
        }
    })
    .catch(error => {
        console.error('Analysis error for section', sectionName, ':', error);
        
        if (progressDesc) {
            progressDesc.textContent = `❌ "${sectionName}" analysis failed. Continuing with next section...`;
        }
        
        window.currentAnalysisStep++;
        setTimeout(() => {
            hideSectionLoadingProgress();
            setTimeout(analyzeNextSection, 1000);
        }, 1000);
    });
}

function completeAnalysis() {
    const progressText = document.getElementById('progressText');
    const progressTitle = document.getElementById('progressTitle');
    const progressDesc = document.getElementById('progressDesc');
    
    if (progressText) progressText.textContent = '🎉 Comprehensive Analysis Complete!';
    if (progressTitle) progressTitle.textContent = '🎉 All sections analyzed successfully!';
    if (progressDesc) progressDesc.textContent = '📋 Ready to review feedback and complete your document analysis';
    
    // Show completion for a moment
    setTimeout(() => {
        hideProgress();
        hideSectionLoadingProgress();
        
        // Load first section
        loadSection(0);
        updateStatistics();
        
        // Enable complete review button
        const completeBtn = document.getElementById('completeReviewBtn');
        if (completeBtn) completeBtn.disabled = false;
        
        // Show success notification
        showNotification('🎉 Comprehensive analysis completed! Navigate through sections to review AI-generated feedback.', 'success');
        
        // Show helpful tip
        setTimeout(() => {
            showNotification('💡 Tip: Use the section dropdown or Previous/Next buttons to navigate between sections', 'info');
        }, 3000);
    }, 3000);
}

function loadSection(index) {
    console.log('loadSection called with index:', index, '- checking for new progress system');
    
    // Check if the new progress system loadSection exists
    if (typeof window.loadSection !== 'undefined' && window.loadSection !== loadSection) {
        console.log('Using new progress system loadSection');
        window.loadSection(index);
        return;
    }
    
    // Fallback to original system
    console.log('Using fallback loadSection');
    
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
        // Show enhanced loading with progress
        showSectionLoadingProgress(sectionName);
        
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
        .then(response => {
            // Check if response is ok before parsing JSON
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.text(); // Get as text first
        })
        .then(text => {
            // Try to parse JSON with better error handling
            let data;
            try {
                data = JSON.parse(text);
            } catch (jsonError) {
                console.error('JSON Parse Error:', jsonError);
                console.error('Response text:', text);
                throw new Error('Invalid JSON response from server. Please check server logs.');
            }
            
            if (data.success) {
                // Store the data for future use
                window.sectionData = window.sectionData || {};
                window.sectionData[sectionName] = {
                    content: data.section_content,
                    feedback: data.feedback_items
                };
                
                displaySectionContent(data.section_content, sectionName);
                displayFeedback(data.feedback_items, sectionName);
                updateRiskIndicator(data.feedback_items);
                loadUserFeedbackForSection(sectionName);
                
                showNotification(`Section "${sectionName}" loaded successfully!`, 'success');
            } else {
                throw new Error(data.error || 'Failed to analyze section');
            }
            hideProgress();
            hideSectionLoadingProgress();
        })
        .catch(error => {
            console.error('Section loading error:', error);
            hideProgress();
            hideSectionLoadingProgress();
            
            // Show user-friendly error message
            const errorMsg = error.message.includes('JSON') ? 
                'Server response error. Please try refreshing the page.' : 
                error.message;
            
            showNotification('Failed to load section: ' + errorMsg, 'error');
            
            // Show fallback content
            displaySectionContent('Section content could not be loaded. Please try again.', sectionName);
            displayFeedback([], sectionName);
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
                    <button class="btn btn-warning revert-btn" onclick="revertFeedback('${item.id}', event)">🔄 Revert</button>
                    <button class="btn btn-info" onclick="addCustomToAI('${item.id}', event)">✨ Add Custom</button>
                    <button class="btn btn-warning" onclick="clearAICustomFeedback('${item.id}', event)" style="display: none;">🧹 Clear Custom</button>
                </div>
                
                <!-- Custom feedback form for this AI suggestion -->
                <div id="custom-${item.id}" class="ai-custom-feedback" style="display: none; margin-top: 15px; padding: 15px; background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); border-radius: 10px; border: 2px solid #4f46e5;">
                    <h4 style="color: #4f46e5; margin-bottom: 15px;">✨ Add Your Custom Feedback</h4>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <div>
                            <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">🏷️ Type:</label>
                            <select id="aiCustomType-${item.id}" style="width: 100%; padding: 8px; border: 2px solid #4f46e5; border-radius: 6px;">
                                <option value="suggestion">Suggestion</option>
                                <option value="important">Important</option>
                                <option value="critical">Critical</option>
                                <option value="positive">Positive</option>
                                <option value="question">Question</option>
                                <option value="clarification">Clarification</option>
                            </select>
                        </div>
                        <div>
                            <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">📁 Category:</label>
                            <select id="aiCustomCategory-${item.id}" style="width: 100%; padding: 8px; border: 2px solid #4f46e5; border-radius: 6px;">
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
                    
                    <div style="margin-bottom: 15px;">
                        <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">📝 Your Custom Feedback:</label>
                        <textarea id="aiCustomDesc-${item.id}" placeholder="Add your thoughts, additional context, or specific observations about this AI suggestion..." style="width: 100%; height: 80px; padding: 10px; border: 2px solid #4f46e5; border-radius: 6px; resize: vertical;"></textarea>
                    </div>
                    
                    <div style="text-align: center;">
                        <button class="btn btn-success" onclick="saveAICustomFeedback('${item.id}')" style="margin: 5px; padding: 8px 16px; border-radius: 20px; font-weight: 600;">💾 Save Custom Feedback</button>
                        <button class="btn btn-secondary" onclick="cancelAICustom('${item.id}')" style="margin: 5px; padding: 8px 16px; border-radius: 20px;">❌ Cancel</button>
                    </div>
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

            // Log activity for real-time display (Fix for Issue #13)
            if (window.logAIFeedbackActivity) {
                window.logAIFeedbackActivity(feedbackId, 'accepted');
            }

            // Update real-time logs
            if (window.updateRealTimeFeedbackLogs) {
                window.updateRealTimeFeedbackLogs();
            }
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

            // Log activity for real-time display (Fix for Issue #13)
            if (window.logAIFeedbackActivity) {
                window.logAIFeedbackActivity(feedbackId, 'rejected');
            }

            // Update real-time logs
            if (window.updateRealTimeFeedbackLogs) {
                window.updateRealTimeFeedbackLogs();
            }
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
            <button class="btn btn-warning revert-btn" onclick="revertFeedback('${feedbackId}', event)" style="font-size: 12px; padding: 5px 10px; margin-left: 10px;">🔄 Revert</button>
        `;
        feedbackItem.style.opacity = '0.7';
    }
}

/**
 * Revert feedback to its original pending state
 * @param {string} feedbackId - The feedback item ID
 * @param {Event} event - The click event
 */
function revertFeedback(feedbackId, event) {
    if (event) event.stopPropagation();
    
    // Send revert request to server
    fetch('/revert_feedback', {
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
            // Restore original feedback actions
            const feedbackItem = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
            if (feedbackItem && window.feedbackStates[feedbackId]) {
                const actions = feedbackItem.querySelector('.feedback-actions');
                actions.innerHTML = window.feedbackStates[feedbackId].originalHtml;
                feedbackItem.style.opacity = '1';
                
                window.feedbackStates[feedbackId].status = 'pending';
                
                showNotification('Feedback reverted to original state', 'success');
                updateStatistics();
            }
        } else {
            showNotification(data.error || 'Revert failed', 'error');
        }
    })
    .catch(error => {
        // Fallback: revert locally even if server call fails
        const feedbackItem = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
        if (feedbackItem && window.feedbackStates[feedbackId]) {
            const actions = feedbackItem.querySelector('.feedback-actions');
            actions.innerHTML = window.feedbackStates[feedbackId].originalHtml;
            feedbackItem.style.opacity = '1';
            
            window.feedbackStates[feedbackId].status = 'pending';
            
            showNotification('Feedback reverted locally', 'info');
            updateStatistics();
        }
        console.warn('Server revert failed, reverted locally:', error);
    });
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

    // Check for session in multiple locations (window, currentSession global, sessionStorage)
    const sessionId = window.currentSession || (typeof currentSession !== 'undefined' ? currentSession : null) || sessionStorage.getItem('currentSession');

    if (!sessionId) {
        addChatMessage('Please upload a document first to start chatting.', 'assistant');
        return;
    }

    // Add thinking indicator
    const thinkingMessage = addChatMessage('🤔 Thinking...', 'assistant', true);

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: message,
            current_section: window.sections[window.currentSectionIndex] || null
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove thinking indicator
        if (thinkingMessage && thinkingMessage.parentNode) {
            thinkingMessage.remove();
        }

        if (data.success) {
            addChatMessage(data.response, 'assistant');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    })
    .catch(error => {
        // Remove thinking indicator
        if (thinkingMessage && thinkingMessage.parentNode) {
            thinkingMessage.remove();
        }
        addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
    });
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

function addChatMessage(message, sender, isThinking = false) {
    const container = document.getElementById('chatContainer');
    if (!container) return null;

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
        // If thinking indicator, add pulsing animation
        if (isThinking) {
            messageDiv.innerHTML = `<strong>🤖 AI-Prism:</strong> <small style="opacity: 0.7;">${timestamp}</small><br><span style="animation: pulse 1.5s infinite;">${message}</span>`;
            messageDiv.style.opacity = '0.8';
        } else {
            messageDiv.innerHTML = `<strong>🤖 AI-Prism:</strong> <small style="opacity: 0.7;">${timestamp}</small><br>${message}`;
        }
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

    // Return the message element so it can be removed later (for thinking indicator)
    return messageDiv;
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
            
            // Create feedback item for display and logging
            const feedbackItem = {
                id: data.feedback_item.id,
                type: type,
                category: category,
                description: description,
                section: window.sections[window.currentSectionIndex],
                timestamp: new Date().toISOString(),
                user_created: true,
                risk_level: type === 'critical' ? 'High' : type === 'important' ? 'Medium' : 'Low'
            };
            
            // Add to user feedback history
            if (!window.userFeedbackHistory) {
                window.userFeedbackHistory = [];
            }
            window.userFeedbackHistory.push(feedbackItem);
            
            // Display the feedback
            if (typeof window.displayUserFeedback === 'function') {
                window.displayUserFeedback(feedbackItem);
            }
            
            // Clear the form
            document.getElementById('customDescription').value = '';
            
            // Update all displays including real-time logs
            updateStatistics();
            
            if (typeof window.updateAllCustomFeedbackList === 'function') {
                window.updateAllCustomFeedbackList();
            }
            
            if (typeof window.refreshUserFeedbackList === 'function') {
                window.refreshUserFeedbackList();
            }
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

// Enhanced loading functions for better user experience
function showSectionLoadingProgress(sectionName) {
    const progressPanel = document.getElementById('documentProgress');
    if (progressPanel) {
        progressPanel.style.display = 'block';
        
        // Update progress content
        const progressTitle = document.getElementById('progressTitle');
        const progressDesc = document.getElementById('progressDesc');
        const progressGif = document.getElementById('progressGif');
        
        if (progressTitle) {
            progressTitle.textContent = `🔍 AI-Prism is analyzing "${sectionName}"...`;
        }
        
        if (progressDesc) {
            progressDesc.textContent = 'Applying Hawkeye framework and generating intelligent feedback...';
        }
        
        if (progressGif) {
            // Use a default loading GIF
            progressGif.src = 'https://media.giphy.com/media/3o7btPCcdNniyf0ArS/giphy.gif';
            progressGif.alt = 'AI-Prism is analyzing...';
        }
        
        // Start a simple animation cycle
        startLoadingAnimation();
    }
}

function hideSectionLoadingProgress() {
    const progressPanel = document.getElementById('documentProgress');
    if (progressPanel) {
        progressPanel.style.display = 'none';
    }
    stopLoadingAnimation();
}

function startLoadingAnimation() {
    const progressTitle = document.getElementById('progressTitle');
    if (!progressTitle) return;
    
    let dots = 0;
    window.loadingInterval = setInterval(() => {
        dots = (dots + 1) % 4;
        const dotString = '.'.repeat(dots);
        const baseText = progressTitle.textContent.replace(/\.+$/, '');
        progressTitle.textContent = baseText + dotString;
    }, 500);
}

function stopLoadingAnimation() {
    if (window.loadingInterval) {
        clearInterval(window.loadingInterval);
        window.loadingInterval = null;
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
                // Save current section highlights before switching
                if (typeof saveCurrentSectionHighlights === 'function') {
                    saveCurrentSectionHighlights();
                }
                loadSection(selectedIndex);
            }
        });
    }

    // DEPRECATED: Dark mode preference loading is now handled by core_fixes.js
    // This section is disabled to prevent conflicts
    // Dark mode initialization is managed exclusively by core_fixes.js
    /*
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
    */

    // Initialize text highlighting if available
    if (typeof enableTextSelection === 'function') {
        // Enable text selection after a short delay to ensure DOM is ready
        setTimeout(enableTextSelection, 500);
    }
    
    // Initialize user feedback display
    setTimeout(() => {
        if (typeof updateAllCustomFeedbackList === 'function') {
            updateAllCustomFeedbackList();
        }
    }, 1000);
    
    // Show text highlighting tutorial on first visit
    const hasSeenHighlightingPopup = localStorage.getItem('hasSeenTextHighlightingPopup');
    if (!hasSeenHighlightingPopup && typeof showTextHighlightingFeature === 'function') {
        setTimeout(() => {
            showTextHighlightingFeature();
            localStorage.setItem('hasSeenTextHighlightingPopup', 'true');
        }, 2000);
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



// Quick custom feedback function for the static form in feedback panel
function addQuickCustomFeedback() {
    const type = document.getElementById('quickCustomType')?.value;
    const category = document.getElementById('quickCustomCategory')?.value;
    const description = document.getElementById('quickCustomDescription')?.value?.trim();
    
    if (!description) {
        showNotification('Please enter your feedback description', 'error');
        document.getElementById('quickCustomDescription')?.focus();
        return;
    }
    
    if (!window.currentSession) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }
    
    if (!window.sections || window.currentSectionIndex < 0) {
        showNotification('No section selected. Please select a section first.', 'error');
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
            showNotification('✨ Custom feedback added successfully!', 'success');
            
            // Clear the form
            document.getElementById('quickCustomDescription').value = '';
            
            // Create feedback item for local history
            const feedbackItem = {
                id: data.feedback_item.id,
                type: type,
                category: category,
                description: description,
                section: window.sections[window.currentSectionIndex],
                timestamp: new Date().toISOString(),
                user_created: true,
                risk_level: type === 'critical' ? 'High' : type === 'important' ? 'Medium' : 'Low'
            };
            
            // Add to user feedback history
            if (!window.userFeedbackHistory) {
                window.userFeedbackHistory = [];
            }
            window.userFeedbackHistory.push(feedbackItem);
            
            // Display the feedback using available functions
            if (typeof window.displayUserFeedback === 'function') {
                window.displayUserFeedback(feedbackItem);
            } else if (typeof displayUserFeedback === 'function') {
                displayUserFeedback(feedbackItem);
            }
            
            // Update all displays including real-time logs
            updateStatistics();
            
            if (typeof window.updateAllCustomFeedbackList === 'function') {
                window.updateAllCustomFeedbackList();
            } else if (typeof updateAllCustomFeedbackList === 'function') {
                updateAllCustomFeedbackList();
            }
            
            if (typeof window.updateRealTimeFeedbackLogs === 'function') {
                window.updateRealTimeFeedbackLogs();
            }
            
            if (typeof window.refreshUserFeedbackList === 'function') {
                window.refreshUserFeedbackList();
            }
        } else {
            showNotification(data.error || 'Failed to add custom feedback', 'error');
        }
    })
    .catch(error => {
        console.error('Add quick custom feedback error:', error);
        showNotification('Failed to add custom feedback: ' + error.message, 'error');
    });
}