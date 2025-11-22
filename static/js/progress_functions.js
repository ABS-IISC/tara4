// Progress and Analysis Functions for AI-Prism Document Analysis Tool

// Global variables for progress tracking
let currentAnalysisStep = 0;
let totalSections = 0;
let sectionAnalysisStatus = {};
let isAnalyzing = false;


// ✅ CORRECTED: Load section and AUTO-ANALYZE (matches Jupyter notebook _load_section() workflow)
function loadSectionAndAnalyze(index) {
    if (!sections || index < 0 || index >= sections.length) {
        console.error('Invalid section index:', index);
        return;
    }

    currentSectionIndex = index;
    const sectionName = sections[index];

    console.log('✅ Loading section WITH AUTO-ANALYSIS:', sectionName);

    // Update section selector
    const sectionSelect = document.getElementById('sectionSelect');
    if (sectionSelect) {
        sectionSelect.selectedIndex = index + 1;
    }

    // Fetch section content from backend
    fetch('/get_section_content', {
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
        if (data.success && data.content) {
            // Display section content
            const documentContent = document.getElementById('documentContent');
            if (documentContent) {
                documentContent.innerHTML = `
                    <div style="padding: 20px;">
                        <h3 style="color: #4f46e5; margin-bottom: 15px; border-bottom: 2px solid #4f46e5; padding-bottom: 10px;">
                            Section: "${sectionName}"
                        </h3>
                        <div style="line-height: 1.8; white-space: pre-wrap; font-size: 1.05em;">
                            ${data.content}
                        </div>
                    </div>
                `;
            }

            // Show "Analyzing..." state with progress tracking
            const feedbackContainer = document.getElementById('feedbackContainer');
            if (feedbackContainer) {
                // Calculate progress percentage based on analyzed sections
                const totalSections = sections ? sections.length : 0;
                const analyzedSections = Object.keys(sectionAnalysisStatus).filter(s => sectionAnalysisStatus[s] === 'analyzed').length;
                const progressPercent = totalSections > 0 ? Math.round((analyzedSections / totalSections) * 100) : 0;

                feedbackContainer.innerHTML = `
                    <div style="text-align: center; padding: 40px 30px; background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); border-radius: 15px; border: 3px solid #4f46e5; margin: 20px 0;">
                        <div style="font-size: 4em; margin-bottom: 20px;">🔍</div>
                        <h3 style="color: #4f46e5; margin-bottom: 15px; font-size: 1.6em;">Section: "${sectionName}"</h3>

                        <!-- Progress Bar -->
                        <div style="margin: 20px 0;">
                            <div style="background: #e0e0e0; height: 30px; border-radius: 15px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);">
                                <div style="background: linear-gradient(90deg, #4f46e5 0%, #667eea 100%); height: 100%; width: ${progressPercent}%; transition: width 0.3s ease; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 14px;">
                                    ${progressPercent > 10 ? progressPercent + '% Complete' : ''}
                                </div>
                            </div>
                            <p style="color: #666; margin-top: 10px; font-size: 0.95em;">
                                ${analyzedSections} of ${totalSections} sections analyzed
                            </p>
                        </div>

                        <p style="color: #4f46e5; margin-bottom: 20px; font-size: 1.2em; font-weight: 600;">
                            🔍 Analyzing with Hawkeye Framework...
                        </p>
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="sr-only">Loading...</span>
                        </div>
                        <p style="color: #999; margin-top: 15px; font-size: 0.9em;">
                            ⏱️ Analysis takes 10-30 seconds
                        </p>
                    </div>
                `;
            }

            updateNavigationButtons();

            // ✅ AUTO-ANALYZE: Trigger analysis automatically (like Jupyter notebook _load_section() -> _analyze_section())
            console.log('🤖 AUTO-TRIGGERING ANALYSIS for section:', sectionName);
            analyzeCurrentSection();

        } else {
            showNotification('Failed to load section content', 'error');
        }
    })
    .catch(error => {
        console.error('Error loading section:', error);
        showNotification('Error loading section: ' + error.message, 'error');
    });
}

// Simple progress popup functions
function showSimpleProgressPopup() {
    // Remove any existing progress popup and backdrop
    const existingPopup = document.getElementById('simpleProgressPopup');
    if (existingPopup) {
        existingPopup.remove();
    }
    const existingBackdrop = document.getElementById('simpleProgressBackdrop');
    if (existingBackdrop) {
        existingBackdrop.remove();
    }

    // Create backdrop overlay (semi-transparent, not completely blocking)
    const backdrop = document.createElement('div');
    backdrop.id = 'simpleProgressBackdrop';
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9999;
        backdrop-filter: blur(3px);
    `;

    // Create simple progress popup
    const popup = document.createElement('div');
    popup.id = 'simpleProgressPopup';
    popup.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 10000;
        text-align: center;
        min-width: 400px;
        border: 3px solid #4f46e5;
    `;

    popup.innerHTML = `
        <div style="margin-bottom: 20px;">
            <div style="font-size: 2em; margin-bottom: 10px;">🤖</div>
            <h3 style="color: #4f46e5; margin-bottom: 10px;">AI-Prism Analysis</h3>
            <p style="color: #666; margin: 0;">Analyzing document sections...</p>
        </div>

        <div style="margin-bottom: 20px;">
            <div style="background: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden; margin-bottom: 10px;">
                <div id="simpleProgressBar" style="background: linear-gradient(90deg, #4f46e5, #7c3aed); height: 100%; width: 0%; transition: width 0.3s ease; border-radius: 10px;"></div>
            </div>
            <div id="simpleProgressText" style="font-weight: bold; color: #4f46e5;">0% Complete</div>
        </div>

        <div id="simpleProgressStatus" style="color: #666; font-size: 0.9em; margin-bottom: 20px;">
            Starting analysis...
        </div>

        <button onclick="window.cancelUpload()" style="background: #ef4444; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.2s;" onmouseover="this.style.background='#dc2626'" onmouseout="this.style.background='#ef4444'">
            ❌ Cancel Upload
        </button>
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(popup);
    return popup;
}

function updateSimpleProgress(percentage, statusText) {
    const progressBar = document.getElementById('simpleProgressBar');
    const progressText = document.getElementById('simpleProgressText');
    const progressStatus = document.getElementById('simpleProgressStatus');
    
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
    }
    
    if (progressText) {
        progressText.textContent = `${Math.round(percentage)}% Complete`;
    }
    
    if (progressStatus) {
        progressStatus.textContent = statusText;
    }
}

function hideSimpleProgressPopup() {
    const popup = document.getElementById('simpleProgressPopup');
    if (popup) {
        popup.remove();
    }
    const backdrop = document.getElementById('simpleProgressBackdrop');
    if (backdrop) {
        backdrop.remove();
    }
}

// Cancel upload function
window.cancelUpload = function() {
    if (confirm('Are you sure you want to cancel the upload? You will need to start over.')) {
        hideSimpleProgressPopup();
        showNotification('Upload cancelled by user', 'info');
        // Reset any upload state if needed
        window.analysisFile = null;
    }
};

// Modified startAnalysis function
function startAnalysis() {
    if (!analysisFile) {
        showNotification('Please select an analysis document first', 'error');
        return;
    }
    
    // Show simple progress popup
    showSimpleProgressPopup();
    updateSimpleProgress(10, 'Uploading document...');
    
    const formData = new FormData();
    formData.append('document', analysisFile);
    
    if (guidelinesFile) {
        formData.append('guidelines', guidelinesFile);
    }
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // CRITICAL: Set session in multiple scopes for reliability
            currentSession = data.session_id;
            window.currentSession = data.session_id;
            sessionStorage.setItem('currentSession', data.session_id);

            // Validate and sanitize sections array
            if (!Array.isArray(data.sections)) {
                console.error('❌ ERROR: data.sections is not an array!', data.sections);
                throw new Error('Invalid sections data from server');
            }

            // Ensure all sections are strings
            sections = data.sections.map((section, index) => {
                if (typeof section === 'string') {
                    return section;
                } else if (section && typeof section === 'object' && section.name) {
                    console.warn(`⚠️ Section ${index} was an object, extracting name:`, section);
                    return section.name;
                } else {
                    console.error(`❌ Section ${index} is invalid:`, section);
                    return `Section ${index + 1}`;  // Fallback
                }
            });

            window.sections = sections;

            totalSections = sections.length;

            console.log('✅ Sections loaded and validated:', sections);

            // ✅ FIX: Populate section dropdown (Issue #2 Fix)
            populateSectionSelect(data.sections);

            // Update progress
            updateSimpleProgress(30, 'Document uploaded successfully!');
            
            // Initialize section analysis status
            sectionAnalysisStatus = {};
            sections.forEach(section => {
                sectionAnalysisStatus[section] = 'pending';
            });
            
            setTimeout(() => {
                updateSimpleProgress(50, 'Setting up analysis environment...');
                
                setTimeout(() => {
                    updateSimpleProgress(100, 'Analysis setup complete!');
                    
                    setTimeout(() => {
                        hideSimpleProgressPopup();

                        // Show main content
                        showMainContent();

                        // ✅ CORRECTED WORKFLOW: Auto-analyze section when loaded (matches Jupyter notebook)
                        // Analyze ONE section at a time when user navigates to it
                        if (sections.length > 0) {
                            // Load first section and AUTO-ANALYZE (like Jupyter notebook _load_section())
                            loadSectionAndAnalyze(0);

                            // Enable Submit All Feedbacks button immediately after upload
                            setTimeout(() => {
                                const submitBtn = document.getElementById('submitAllFeedbacksBtn');
                                if (submitBtn) submitBtn.disabled = false;
                                showNotification('✅ Document uploaded! Analyzing first section...', 'success');
                            }, 500);
                        }
                    }, 500);
                }, 1000);
            }, 1000);
        } else {
            hideSimpleProgressPopup();
            showNotification('Upload failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        hideSimpleProgressPopup();
        console.error('Upload error:', error);
        showNotification('Upload failed: ' + error.message, 'error');
    });
}

// Section-by-section analysis function
function analyzeCurrentSection() {
    console.log('🔍 analyzeCurrentSection() CALLED - Function entry');
    console.log('📊 Variable Check:', {
        currentSession: currentSession,
        sections: sections,
        currentSectionIndex: currentSectionIndex,
        sectionsLength: sections ? sections.length : 'null/undefined'
    });

    if (!currentSession || !sections || currentSectionIndex < 0) {
        console.error('❌ Early return triggered:', {
            noSession: !currentSession,
            noSections: !sections,
            invalidIndex: currentSectionIndex < 0
        });
        showNotification('No section available for analysis', 'error');
        return;
    }

    console.log('✅ Passed validation checks, proceeding with analysis...');
    
    const sectionName = sections[currentSectionIndex];
    
    // Check if section is already analyzed
    if (sectionAnalysisStatus[sectionName] === 'analyzed') {
        console.log('Section already analyzed:', sectionName);
        return;
    }
    
    // Check if section is currently being analyzed
    if (sectionAnalysisStatus[sectionName] === 'analyzing') {
        console.log('Section is currently being analyzed:', sectionName);
        return;
    }
    
    // Mark section as being analyzed
    sectionAnalysisStatus[sectionName] = 'analyzing';
    isAnalyzing = true;
    
    // Show feedback container with "Analysis in progress" message
    const feedbackContainer = document.getElementById('feedbackContainer');
    if (feedbackContainer) {
        feedbackContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); border-radius: 15px; border: 3px solid #4f46e5; margin: 20px 0;">
                <div style="font-size: 3em; margin-bottom: 20px; animation: pulse 2s infinite;">🤖</div>
                <h3 style="color: #4f46e5; margin-bottom: 15px;">AI-Prism is Analyzing...</h3>
                <p style="color: #666; margin-bottom: 20px;">Section: "${sectionName}"</p>
                <div style="background: #f0f0f0; height: 8px; border-radius: 4px; overflow: hidden; margin: 20px auto; max-width: 300px;">
                    <div style="background: linear-gradient(90deg, #4f46e5, #7c3aed); height: 100%; width: 100%; animation: progress 2s infinite;"></div>
                </div>
                <p style="color: #4f46e5; font-weight: 600; font-size: 0.9em;">Applying Hawkeye framework analysis...</p>
            </div>
            
            <style>
                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                }
                @keyframes progress {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
            </style>
        `;
    }
    
    console.log('Starting analysis for section:', sectionName);
    
    // Start the actual analysis
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
        if (data.success && data.task_id) {
            // Async processing - poll for result
            console.log('Task submitted:', data.task_id);
            pollTaskResult(data.task_id, sectionName);
        } else if (data.success && data.feedback_items) {
            // Synchronous result
            isAnalyzing = false;
            sectionAnalysisStatus[sectionName] = 'analyzed';

            console.log('Analysis completed for section:', sectionName);

            // Display the feedback
            displaySectionFeedback(data.feedback_items, sectionName);

            showNotification(`Analysis completed for "${sectionName}"!`, 'success');
        } else {
            // Mark section as failed
            sectionAnalysisStatus[sectionName] = 'failed';
            
            console.error('Analysis failed for section:', sectionName, data.error);
            
            // Show error message
            if (feedbackContainer) {
                feedbackContainer.innerHTML = `
                    <div style="text-align: center; padding: 40px; background: #fff5f5; border: 2px solid #ef4444; border-radius: 15px; margin: 20px 0;">
                        <div style="font-size: 3em; margin-bottom: 20px;">❌</div>
                        <h3 style="color: #ef4444; margin-bottom: 15px;">Analysis Failed</h3>
                        <p style="color: #666; margin-bottom: 20px;">Section: "${sectionName}"</p>
                        <p style="color: #ef4444; font-size: 0.9em;">${data.error || 'Unknown error occurred'}</p>
                        <button class="btn btn-primary" onclick="retryAnalysis()" style="margin-top: 15px;">🔄 Retry Analysis</button>
                    </div>
                `;
            }
            
            showNotification('Analysis failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        isAnalyzing = false;
        sectionAnalysisStatus[sectionName] = 'failed';
        
        console.error('Analysis error for section:', sectionName, error);
        
        // Show error message
        if (feedbackContainer) {
            feedbackContainer.innerHTML = `
                <div style="text-align: center; padding: 40px; background: #fff5f5; border: 2px solid #ef4444; border-radius: 15px; margin: 20px 0;">
                    <div style="font-size: 3em; margin-bottom: 20px;">❌</div>
                    <h3 style="color: #ef4444; margin-bottom: 15px;">Analysis Error</h3>
                    <p style="color: #666; margin-bottom: 20px;">Section: "${sectionName}"</p>
                    <p style="color: #ef4444; font-size: 0.9em;">${error.message}</p>
                    <button class="btn btn-primary" onclick="retryAnalysis()" style="margin-top: 15px;">🔄 Retry Analysis</button>
                </div>
            `;
        }
        
        showNotification('Analysis error: ' + error.message, 'error');
    });
}

// ✅ NEW: Load section WITHOUT analysis - show "Ready to analyze" state

// Retry analysis function
function retryAnalysis() {
    if (!sections || currentSectionIndex < 0) {
        showNotification('No section available for retry', 'error');
        return;
    }

    const sectionName = sections[currentSectionIndex];

    // Reset section status
    sectionAnalysisStatus[sectionName] = 'pending';

    // Retry analysis
    analyzeCurrentSection();
}

// Display section feedback
function displaySectionFeedback(feedbackItems, sectionName) {
    console.log('🎨 displaySectionFeedback CALLED:', {
        feedbackItems: feedbackItems,
        feedbackCount: feedbackItems ? feedbackItems.length : 0,
        sectionName: sectionName,
        sectionType: typeof sectionName
    });

    const feedbackContainer = document.getElementById('feedbackContainer');
    console.log('📦 feedbackContainer element:', feedbackContainer ? 'FOUND' : 'NOT FOUND');
    if (!feedbackContainer) {
        console.error('❌ feedbackContainer element is missing from DOM!');
        return;
    }

    // ✅ CRITICAL: Validate sectionName is a string to prevent dict errors
    if (typeof sectionName !== 'string') {
        console.error('❌ displaySectionFeedback: sectionName must be a string!', 'Type:', typeof sectionName, 'Value:', sectionName);

        // Try to extract string if it's an object with a name property
        if (sectionName && typeof sectionName === 'object' && sectionName.name) {
            console.log('🔧 Extracting section name from object');
            sectionName = sectionName.name;
        } else {
            showNotification('Error: Invalid section name format', 'error');
            return;
        }
    }

    if (!feedbackItems || feedbackItems.length === 0) {
        feedbackContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; background: #f0fff4; border: 2px solid #10b981; border-radius: 15px; margin: 20px 0;">
                <div style="font-size: 3em; margin-bottom: 20px;">✅</div>
                <h3 style="color: #10b981; margin-bottom: 15px;">Analysis Complete</h3>
                <p style="color: #666; margin-bottom: 10px;">Section: "${sectionName}"</p>
                <p style="color: #10b981; font-weight: 600;">No issues found - section looks good!</p>
            </div>
        `;
        return;
    }
    
    // ✅ SORT: Order feedback by confidence (high to low)
    const sortedFeedbackItems = [...feedbackItems].sort((a, b) => {
        const confidenceA = a.confidence || 0.8;
        const confidenceB = b.confidence || 0.8;
        return confidenceB - confidenceA; // High confidence first
    });

    let feedbackHtml = `
        <div style="margin-bottom: 20px; padding: 15px; background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); border-radius: 12px; border: 2px solid #4f46e5;">
            <h3 style="color: #4f46e5; margin-bottom: 10px;">📝 AI Analysis Results</h3>
            <p style="color: #666; margin: 0;">Section: <strong>"${sectionName}"</strong> - ${sortedFeedbackItems.length} feedback item${sortedFeedbackItems.length !== 1 ? 's' : ''} found (sorted by confidence)</p>
        </div>
    `;

    sortedFeedbackItems.forEach((item, index) => {
        const riskColor = item.risk_level === 'High' ? '#ef4444' : 
                         item.risk_level === 'Medium' ? '#f59e0b' : '#10b981';
        
        const typeColor = item.type === 'critical' ? '#ef4444' :
                         item.type === 'important' ? '#f59e0b' : '#3b82f6';
        
        feedbackHtml += `
            <div class="feedback-item" data-feedback-id="${item.id}" style="background: white; border-left: 4px solid ${riskColor}; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div class="feedback-header" style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
                    <div class="feedback-meta" style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                        <span class="feedback-type" style="background: ${typeColor}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600; text-transform: uppercase;">${item.type}</span>
                        <span class="risk-indicator" style="background: ${riskColor}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600;">${item.risk_level} Risk</span>
                        <span style="background: #e5e7eb; color: #374151; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 500;">${item.category}</span>
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <p style="margin: 0; line-height: 1.6; color: #374151;"><strong>Issue:</strong> ${item.description}</p>
                </div>
                
                ${item.suggestion ? `
                    <div style="margin-bottom: 15px; padding: 12px; background: #f0f9ff; border-left: 3px solid #3b82f6; border-radius: 4px;">
                        <p style="margin: 0; color: #1e40af;"><strong>💡 Suggestion:</strong> ${item.suggestion}</p>
                    </div>
                ` : ''}
                
                ${item.questions && item.questions.length > 0 ? `
                    <div style="margin-bottom: 15px; padding: 12px; background: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 4px;">
                        <p style="margin: 0 0 8px 0; color: #92400e; font-weight: 600;">❓ Key Questions:</p>
                        <ul style="margin: 0; padding-left: 20px; color: #92400e;">
                            ${item.questions.map(q => `<li>${q}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${item.hawkeye_refs && item.hawkeye_refs.length > 0 ? `
                    <div style="margin-bottom: 15px;">
                        <span style="font-size: 0.9em; color: #6b7280; margin-right: 8px;">🎯 Hawkeye References:</span>
                        ${item.hawkeye_refs.map(ref => `<span style="background: #4f46e5; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; margin-right: 4px;">#${ref}</span>`).join('')}
                    </div>
                ` : ''}
                
                <div class="feedback-actions" style="display: flex; gap: 8px; margin-top: 15px; flex-wrap: wrap; align-items: center;">
                    <button class="btn btn-success" onclick="window.acceptFeedback('${item.id}', '${sectionName}')" style="font-size: 12px; padding: 6px 12px; border-radius: 6px;">✅ Accept</button>
                    <button class="btn btn-danger" onclick="window.rejectFeedback('${item.id}', '${sectionName}')" style="font-size: 12px; padding: 6px 12px; border-radius: 6px;">❌ Reject</button>
                    <button class="btn btn-warning" onclick="window.revertFeedbackDecision('${item.id}', '${sectionName}')" style="font-size: 12px; padding: 6px 12px; border-radius: 6px;">🔄 Revert</button>
                    <button class="btn btn-info" onclick="window.updateFeedback()" style="font-size: 12px; padding: 6px 12px; border-radius: 6px;">✏️ Update</button>
                    <button class="btn btn-primary" onclick="window.showInlineFeedbackForm('${item.id}', '${sectionName}')" style="font-size: 12px; padding: 6px 12px; border-radius: 6px;">✨ Add Custom Feedback</button>
                    <span style="font-size: 0.8em; color: #6b7280; margin-left: 10px;">Confidence: ${Math.round((item.confidence || 0.8) * 100)}%</span>
                </div>
            </div>
        `;
    });
    
    feedbackContainer.innerHTML = feedbackHtml;
}

// Modified loadSection function to trigger analysis - DELEGATES TO missing_functions.js
function loadSection(index) {
    // IMPORTANT: This function now delegates to the proper implementation in missing_functions.js
    // which correctly fetches and displays content

    // Check if displaySectionContent exists (from missing_functions.js)
    if (typeof displaySectionContent === 'function') {
        console.log('progress_functions.js: Delegating to missing_functions.js loadSection');

        // Call the proper loadSection if it exists in missing_functions.js
        // The logic is already there, we just need to not override it

        // Use window.sections explicitly to avoid any local variable issues
        const sectionsArray = window.sections || sections;

        if (!sectionsArray || index < 0 || index >= sectionsArray.length) {
            console.error('Invalid section index:', index, 'sections:', sectionsArray);
            return;
        }

        currentSectionIndex = index;
        window.currentSectionIndex = index;  // Update global as well

        let sectionName = sectionsArray[index];

        // Defensive check: ensure sectionName is a string, not an object
        if (typeof sectionName !== 'string') {
            console.error('❌ ERROR: sectionName is not a string!', 'Type:', typeof sectionName, 'Value:', sectionName);
            console.error('sections array:', sectionsArray);

            // Try to extract string if it's an object with a name property
            if (sectionName && typeof sectionName === 'object' && sectionName.name) {
                console.log('🔧 Attempting to extract section name from object');
                sectionName = sectionName.name;
            } else {
                showNotification('Error: Invalid section name. Please refresh and try again.', 'error');
                return;
            }
        }

        console.log('Loading section:', sectionName, 'Index:', index, 'Type:', typeof sectionName);

        // Update section selector
        const sectionSelect = document.getElementById('sectionSelect');
        if (sectionSelect) {
            sectionSelect.selectedIndex = index + 1; // +1 because first option is placeholder
        }

        // Show enhanced loading state with section name
        const documentContent = document.getElementById('documentContent');
        if (documentContent) {
            documentContent.innerHTML = `
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

        // Fetch and display content properly
        if (window.sectionData && window.sectionData[sectionName]) {
            const data = window.sectionData[sectionName];
            displaySectionContent(data.content, sectionName);
            displayFeedback(data.feedback, sectionName);
        } else {
            fetch('/analyze_section', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: currentSession,
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
                    displaySectionContent(data.section_content, sectionName);
                    displayFeedback(data.feedback_items, sectionName);
                    showNotification(`Section "${sectionName}" loaded successfully!`, 'success');

                    // Mark section as analyzed
                    sectionAnalysisStatus[sectionName] = 'analyzed';
                } else {
                    throw new Error(data.error || 'Failed to analyze section');
                }
            })
            .catch(error => {
                console.error('Section loading error:', error);
                showNotification('Failed to load section: ' + error.message, 'error');
                displaySectionContent('Section content could not be loaded. Please try again.', sectionName);
                displayFeedback([], sectionName);
                sectionAnalysisStatus[sectionName] = 'failed';
            });
        }

        // Update navigation buttons
        updateNavigationButtons();
    } else {
        console.error('progress_functions.js: displaySectionContent not available!');
        console.log('progress_functions.js: Ensure missing_functions.js is loaded');
    }
}

// Load existing feedback for analyzed sections
function loadExistingFeedback(sectionName) {
    if (!currentSession) {
        console.error('No current session');
        return;
    }
    
    // This would typically fetch existing feedback from the server
    // For now, show a placeholder
    const feedbackContainer = document.getElementById('feedbackContainer');
    if (feedbackContainer) {
        feedbackContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; background: #f0fff4; border: 2px solid #10b981; border-radius: 15px; margin: 20px 0;">
                <div style="font-size: 3em; margin-bottom: 20px;">✅</div>
                <h3 style="color: #10b981; margin-bottom: 15px;">Section Already Analyzed</h3>
                <p style="color: #666; margin-bottom: 10px;">Section: "${sectionName}"</p>
                <p style="color: #10b981; font-weight: 600;">Feedback has been generated for this section</p>
                <button class="btn btn-info" onclick="reanalyzeSection()" style="margin-top: 15px;">🔄 Re-analyze Section</button>
            </div>
        `;
    }
}

// Re-analyze section function
function reanalyzeSection() {
    if (!sections || currentSectionIndex < 0) {
        showNotification('No section available for re-analysis', 'error');
        return;
    }
    
    const sectionName = sections[currentSectionIndex];
    
    // Reset section status
    sectionAnalysisStatus[sectionName] = 'pending';
    
    // Start analysis
    analyzeCurrentSection();
}

// Update navigation buttons
function updateNavigationButtons() {
    // This would update the Previous/Next buttons based on current section
    console.log('Navigation updated for section:', currentSectionIndex);
}

// Navigation functions - UPDATED for on-demand analysis
function nextSection() {
    if (currentSectionIndex < sections.length - 1) {
        loadSectionAndAnalyze(currentSectionIndex + 1);  // ✅ AUTO-ANALYZE on navigation
    } else {
        showNotification('Already at the last section', 'info');
    }
}

function previousSection() {
    if (currentSectionIndex > 0) {
        loadSectionAndAnalyze(currentSectionIndex - 1);  // ✅ AUTO-ANALYZE on navigation
    } else {
        showNotification('Already at the first section', 'info');
    }
}

// Show main content function
function showMainContent() {
    const mainContent = document.getElementById('mainContent');
    const statisticsPanel = document.getElementById('statisticsPanel');
    const actionButtons = document.getElementById('actionButtons');
    const customFeedbackSection = document.getElementById('customFeedbackSection');
    
    if (mainContent) mainContent.style.display = 'grid';
    if (statisticsPanel) statisticsPanel.style.display = 'block';
    if (actionButtons) actionButtons.style.display = 'flex';
    if (customFeedbackSection) customFeedbackSection.style.display = 'block';
    
    console.log('Main content displayed');
}

// ✅ NEW: Clean inline feedback form function (no conflicts with old code)
window.showInlineFeedbackForm = function(feedbackId, sectionName) {
    console.log('✨ showInlineFeedbackForm called:', feedbackId, sectionName);

    // ✅ CRITICAL: Validate sectionName is a string to prevent dict errors
    if (typeof sectionName !== 'string') {
        console.error('❌ showInlineFeedbackForm: sectionName must be a string!', 'Type:', typeof sectionName, 'Value:', sectionName);

        // Try to extract string if it's an object with a name property
        if (sectionName && typeof sectionName === 'object' && sectionName.name) {
            console.log('🔧 Extracting section name from object');
            sectionName = sectionName.name;
        } else {
            console.error('❌ Cannot extract section name, returning early');
            showNotification('Error: Invalid section name format. Cannot show feedback form.', 'error');
            return;
        }
    }

    console.log('✅ Step 1 passed: sectionName validated as string:', sectionName);

    // Enhanced session lookup - check multiple sources
    console.log('🔍 Session ID check from multiple sources:');
    console.log('   - window.currentSession:', window.currentSession);
    console.log('   - global currentSession:', typeof currentSession !== 'undefined' ? currentSession : 'undefined');
    console.log('   - sessionStorage:', sessionStorage.getItem('currentSession'));

    const sessionId = window.currentSession ||
                     (typeof currentSession !== 'undefined' ? currentSession : null) ||
                     sessionStorage.getItem('currentSession');

    console.log('   - Final sessionId resolved to:', sessionId);

    if (!sessionId) {
        console.error('❌ No session ID found from any source, returning early');
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    console.log('✅ Step 2 passed: sessionId found:', sessionId);

    // Find the feedback item
    console.log('🔍 Looking for feedback item with selector:', `[data-feedback-id="${feedbackId}"]`);
    const feedbackItem = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
    console.log('🔍 Query result:', feedbackItem);

    if (!feedbackItem) {
        console.error('❌ Feedback item not found for ID:', feedbackId);
        console.error('❌ Tried selector:', `[data-feedback-id="${feedbackId}"]`);
        console.error('❌ Listing all feedback items with data-feedback-id attribute:');
        const allFeedbackItems = document.querySelectorAll('[data-feedback-id]');
        console.error(`Found ${allFeedbackItems.length} feedback items in DOM:`);
        allFeedbackItems.forEach(item => {
            console.error(`  - ID: ${item.getAttribute('data-feedback-id')}`);
        });
        showNotification('Could not find feedback item in page. The feedback may not have loaded yet.', 'error');
        return;
    }

    console.log('✅ Step 3 passed: feedbackItem found:', feedbackItem);

    // Toggle: Remove if already exists
    const existingForm = document.getElementById(`inline-feedback-form-${feedbackId}`);
    if (existingForm) {
        console.log('🔄 Form already exists, toggling (removing)');
        existingForm.remove();
        return;
    }

    console.log('✅ Step 4 passed: No existing form, proceeding to create new form');

    // Create inline dropdown form
    const formHtml = `
        <div id="inline-feedback-form-${feedbackId}" style="margin-top: 20px; padding: 25px; background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); border: 3px solid #4f46e5; border-radius: 15px; box-shadow: 0 8px 25px rgba(79, 70, 229, 0.15); animation: slideDown 0.3s ease-out;">
            <h4 style="color: #4f46e5; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; font-size: 1.2em; font-weight: 700;">
                ✨ Add Your Custom Feedback
            </h4>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div>
                    <label style="font-weight: 700; color: #4f46e5; font-size: 1em; margin-bottom: 8px; display: block;">🏷️ Type:</label>
                    <select id="inlineFeedbackType-${feedbackId}" style="width: 100%; padding: 12px; border: 3px solid #4f46e5; border-radius: 12px; background: linear-gradient(135deg, #ffffff, #f8fafc); font-weight: 600; font-size: 14px;">
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
                    <select id="inlineFeedbackCategory-${feedbackId}" style="width: 100%; padding: 12px; border: 3px solid #10b981; border-radius: 12px; background: linear-gradient(135deg, #ffffff, #f0fdf4); font-weight: 600; font-size: 14px;">
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
                <textarea id="inlineFeedbackText-${feedbackId}" placeholder="Share your insights, suggestions, or observations about this AI feedback..." style="width: 100%; min-height: 100px; padding: 15px; border: 3px solid #ec4899; border-radius: 15px; background: linear-gradient(135deg, #ffffff, #fdf2f8); font-size: 14px; line-height: 1.5; font-family: inherit; resize: vertical;"></textarea>
            </div>

            <div style="display: flex; gap: 10px; justify-content: center;">
                <button class="btn btn-success" onclick="window.saveInlineFeedback('${feedbackId}', '${sectionName}')" style="padding: 15px 35px; font-size: 16px; border-radius: 25px; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4); font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                    🌟 Add My Feedback
                </button>
                <button class="btn btn-secondary" onclick="document.getElementById('inline-feedback-form-${feedbackId}').remove()" style="padding: 15px 35px; font-size: 16px; border-radius: 25px; font-weight: 700;">
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
    console.log('🔍 Inserting form HTML after feedback item...');
    feedbackItem.insertAdjacentHTML('afterend', formHtml);

    // Verify form was inserted
    const insertedForm = document.getElementById(`inline-feedback-form-${feedbackId}`);
    if (insertedForm) {
        console.log('✅ Step 5 passed: Form successfully inserted into DOM');
        console.log('📋 Form element:', insertedForm);
    } else {
        console.error('❌ Form was NOT inserted into DOM!');
        showNotification('Form could not be created. Please try again.', 'error');
        return;
    }

    // Auto-focus on textarea
    setTimeout(() => {
        const textarea = document.getElementById(`inlineFeedbackText-${feedbackId}`);
        if (textarea) {
            textarea.focus();
            console.log('✅ Textarea focused successfully');
        } else {
            console.warn('⚠️ Could not find textarea to focus');
        }
    }, 100);

    console.log('✅ ✨ COMPLETE: Inline feedback form displayed successfully!');
};

// ✅ NEW: Save inline feedback function
window.saveInlineFeedback = function(feedbackId, sectionName) {
    // ✅ CRITICAL: Validate sectionName is a string to prevent dict errors
    if (typeof sectionName !== 'string') {
        console.error('❌ saveInlineFeedback: sectionName must be a string!', 'Type:', typeof sectionName, 'Value:', sectionName);

        // Try to extract string if it's an object with a name property
        if (sectionName && typeof sectionName === 'object' && sectionName.name) {
            console.log('🔧 Extracting section name from object');
            sectionName = sectionName.name;
        } else {
            showNotification('Error: Invalid section name format. Cannot save feedback.', 'error');
            return;
        }
    }

    const type = document.getElementById(`inlineFeedbackType-${feedbackId}`)?.value;
    const category = document.getElementById(`inlineFeedbackCategory-${feedbackId}`)?.value;
    const description = document.getElementById(`inlineFeedbackText-${feedbackId}`)?.value?.trim();

    if (!description) {
        showNotification('Please enter your feedback', 'error');
        return;
    }

    const sessionId = window.currentSession || sessionStorage.getItem('currentSession');

    console.log('💾 Saving inline feedback:', {
        feedbackId,
        sectionName,
        sectionNameType: typeof sectionName,
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
            // Remove the form
            const form = document.getElementById(`inline-feedback-form-${feedbackId}`);
            if (form) form.remove();

            showNotification('✅ Custom feedback added successfully!', 'success');

            // Update feedback history
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

            // Update displays
            if (window.updateAllCustomFeedbackList) {
                window.updateAllCustomFeedbackList();
            }

            if (window.updateRealTimeFeedbackLogs) {
                window.updateRealTimeFeedbackLogs();
            }

            // ✅ FIX: DO NOT reload section - it reverts accept/reject decisions
            // Just update the feedback lists, section state should remain unchanged
            console.log('✅ Custom feedback saved without reloading section (preserves accept/reject state)');
        } else {
            showNotification('❌ Failed to add feedback: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Save inline feedback error:', error);
        showNotification('❌ Failed to add feedback: ' + error.message, 'error');
    });
};

// Initialize progress functions
document.addEventListener('DOMContentLoaded', function() {
    console.log('Progress functions loaded successfully');

    // Always override the global functions with our enhanced versions
    window.startAnalysis = startAnalysis;
    window.loadSection = loadSection;
    window.showMainContent = showMainContent;

    // ✅ FIX: Attach analysis and navigation functions to window for onclick handlers
    window.analyzeCurrentSection = analyzeCurrentSection;
    window.loadSectionAndAnalyze = loadSectionAndAnalyze;
    window.nextSection = nextSection;
    window.previousSection = previousSection;
    window.retryAnalysis = retryAnalysis;

    console.log('✅ Progress functions: All functions attached to window object');
    console.log('   - analyzeCurrentSection:', typeof window.analyzeCurrentSection);
    console.log('   - nextSection:', typeof window.nextSection);
    console.log('   - previousSection:', typeof window.previousSection);
    console.log('   - showInlineFeedbackForm:', typeof window.showInlineFeedbackForm);
    console.log('   - saveInlineFeedback:', typeof window.saveInlineFeedback);
});

// Task polling function for async analysis
function pollTaskResult(taskId, sectionName) {
    console.log(`Polling task ${taskId} for section: ${sectionName}`);

    const maxAttempts = 120; // 2 minutes max (120 * 1 second)
    let attempts = 0;

    const pollInterval = setInterval(() => {
        attempts++;

        // ✅ CRITICAL FIX: Pass session_id so backend can store feedback_data
        fetch(`/task_status/${taskId}?session_id=${currentSession}`)
            .then(response => response.json())
            .then(data => {
                console.log(`Task ${taskId} status:`, data.status, 'state:', data.state);

                // Check both data.state and data.status for SUCCESS
                if (data.state === 'SUCCESS' || data.status === 'SUCCESS' || data.status === 'Task completed successfully') {
                    clearInterval(pollInterval);

                    // ✅ CRITICAL FIX: Check if task completed but analysis actually failed
                    if (data.result && data.result.success === false) {
                        isAnalyzing = false;
                        sectionAnalysisStatus[sectionName] = 'failed';

                        const error = data.result.error || 'Analysis failed';
                        console.error('❌ Task completed but analysis failed for section:', sectionName, error);

                        // Show error message in feedback container
                        const feedbackContainer = document.getElementById('feedbackContainer');
                        if (feedbackContainer) {
                            feedbackContainer.innerHTML = `
                                <div style="text-align: center; padding: 40px; background: #fff5f5; border: 2px solid #ef4444; border-radius: 15px; margin: 20px 0;">
                                    <div style="font-size: 3em; margin-bottom: 20px;">⏱️</div>
                                    <h3 style="color: #ef4444; margin-bottom: 15px;">Analysis Failed</h3>
                                    <p style="color: #666; margin-bottom: 20px;">Section: "${sectionName}"</p>
                                    <p style="color: #ef4444; font-size: 0.9em; margin-bottom: 10px;"><strong>Error:</strong> ${error}</p>
                                    <p style="color: #999; font-size: 0.85em; margin-bottom: 20px;">This is usually due to AWS Bedrock API timeout. Please try again.</p>
                                    <button class="btn btn-primary" onclick="retryAnalysis()" style="margin-top: 15px;">🔄 Retry Analysis</button>
                                </div>
                            `;
                        }

                        showNotification('Analysis failed: ' + error, 'error');
                        return; // Stop here, don't proceed to success path
                    }

                    // Normal success path - analysis actually succeeded
                    isAnalyzing = false;
                    sectionAnalysisStatus[sectionName] = 'analyzed';

                    // Extract feedback items from result
                    const feedbackItems = data.result?.feedback_items || [];
                    console.log('📊 Extracted feedback items:', {
                        count: feedbackItems.length,
                        items: feedbackItems,
                        sectionName: sectionName
                    });

                    console.log('✅ Analysis completed for section:', sectionName, 'Feedback items:', feedbackItems.length);
                    displaySectionFeedback(feedbackItems, sectionName);
                    showNotification(`Analysis completed for "${sectionName}"!`, 'success');

                } else if (data.state === 'FAILURE' || data.status === 'FAILURE') {
                    clearInterval(pollInterval);
                    isAnalyzing = false;
                    sectionAnalysisStatus[sectionName] = 'failed';

                    const error = data.result?.error || data.error || 'Task failed';
                    console.error('Analysis failed for section:', sectionName, error);

                    const feedbackContainer = document.getElementById('feedbackContainer');
                    if (feedbackContainer) {
                        feedbackContainer.innerHTML = `
                            <div style="text-align: center; padding: 40px; background: #fff5f5; border: 2px solid #ef4444; border-radius: 15px; margin: 20px 0;">
                                <div style="font-size: 3em; margin-bottom: 20px;">❌</div>
                                <h3 style="color: #ef4444; margin-bottom: 15px;">Analysis Failed</h3>
                                <p style="color: #666; margin-bottom: 20px;">Section: "${sectionName}"</p>
                                <p style="color: #ef4444; font-size: 0.9em;">${error}</p>
                                <button class="btn btn-primary" onclick="retryAnalysis()" style="margin-top: 15px;">🔄 Retry Analysis</button>
                            </div>
                        `;
                    }

                    showNotification('Analysis failed: ' + error, 'error');

                } else if (attempts >= maxAttempts) {
                    clearInterval(pollInterval);
                    isAnalyzing = false;
                    sectionAnalysisStatus[sectionName] = 'failed';

                    console.error('Analysis timeout for section:', sectionName);
                    showNotification('Analysis timeout - please try again', 'error');

                    const feedbackContainer = document.getElementById('feedbackContainer');
                    if (feedbackContainer) {
                        feedbackContainer.innerHTML = `
                            <div style="text-align: center; padding: 40px; background: #fff5f5; border: 2px solid #f59e0b; border-radius: 15px; margin: 20px 0;">
                                <div style="font-size: 3em; margin-bottom: 20px;">⏱️</div>
                                <h3 style="color: #f59e0b; margin-bottom: 15px;">Analysis Timeout</h3>
                                <p style="color: #666; margin-bottom: 20px;">Section: "${sectionName}"</p>
                                <p style="color: #f59e0b; font-size: 0.9em;">The analysis is taking longer than expected</p>
                                <button class="btn btn-primary" onclick="retryAnalysis()" style="margin-top: 15px;">🔄 Retry Analysis</button>
                            </div>
                        `;
                    }
                }
            })
            .catch(error => {
                console.error('Error polling task:', error);
                // Don't stop polling on network errors, just log and continue
            });
    }, 1000); // Poll every 1 second
}