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
 * ✅ FIXED: Added comprehensive debugging and fallback to sectionData
 */
function getCurrentSectionName() {
    console.log('🔍 getCurrentSectionName called - checking all sources...');

    // Source 1: window.sections + window.currentSectionIndex
    if (window.sections && typeof window.currentSectionIndex === 'number' && window.currentSectionIndex >= 0) {
        const sectionName = window.sections[window.currentSectionIndex];
        console.log('✅ Found section from window.sections:', sectionName);
        return sectionName;
    }

    // Source 2: Global sections + currentSectionIndex (without window prefix)
    if (typeof sections !== 'undefined' && typeof currentSectionIndex !== 'undefined' && currentSectionIndex >= 0) {
        const sectionName = sections[currentSectionIndex];
        console.log('✅ Found section from global sections:', sectionName);
        return sectionName;
    }

    // Source 3: sectionData keys (last analyzed section)
    if (window.sectionData && Object.keys(window.sectionData).length > 0) {
        const lastSection = Object.keys(window.sectionData)[Object.keys(window.sectionData).length - 1];
        console.log('✅ Found section from sectionData:', lastSection);
        return lastSection;
    }

    // Source 4: Section dropdown selection
    const sectionSelect = document.getElementById('sectionSelect');
    if (sectionSelect && sectionSelect.selectedIndex > 0) {
        const sectionName = sectionSelect.options[sectionSelect.selectedIndex].text;
        console.log('✅ Found section from dropdown:', sectionName);
        return sectionName;
    }

    console.error('❌ Could not determine current section name from any source!');
    console.error('   window.sections:', window.sections);
    console.error('   window.currentSectionIndex:', window.currentSectionIndex);
    console.error('   global sections:', typeof sections !== 'undefined' ? sections : 'undefined');
    console.error('   global currentSectionIndex:', typeof currentSectionIndex !== 'undefined' ? currentSectionIndex : 'undefined');
    console.error('   window.sectionData:', window.sectionData ? Object.keys(window.sectionData) : 'undefined');

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

/**
 * UNIFIED Submit All Feedbacks Function
 * Replaces complete_review - generates final document and exports to S3
 */
window.submitAllFeedbacks = function() {
    console.log('📤 UNIFIED submitAllFeedbacks called');

    const sessionId = window.currentSession ||
                     (typeof currentSession !== 'undefined' ? currentSession : null) ||
                     sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }

    const availableSections = window.sections || (typeof sections !== 'undefined' ? sections : []);
    if (!availableSections || availableSections.length === 0) {
        showNotification('No document sections found. Please upload and analyze a document first.', 'error');
        return;
    }

    // Show confirmation dialog
    if (!confirm('📤 Submit All Feedbacks?\n\nThis will:\n• Generate final document with all comments\n• Export complete data package to S3\n• Create comprehensive activity logs\n• Include all feedback decisions\n• Enable document download\n\nContinue?')) {
        return;
    }

    // Show progress
    if (typeof showProgress === 'function') {
        showProgress('Generating final document and exporting to S3...');
    } else if (window.showProgress) {
        window.showProgress('Generating final document and exporting to S3...');
    }

    // Call backend
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
        // Hide progress
        if (typeof hideProgress === 'function') {
            hideProgress();
        } else if (window.hideProgress) {
            window.hideProgress();
        }

        if (data.success) {
            let message = `✅ Review completed! Document generated with ${data.comments_count || 0} comments.`;

            // Handle S3 export result
            if (data.s3_export) {
                if (data.s3_export.success) {
                    message += ` All data exported to S3: ${data.s3_export.location}`;
                    showNotification(message, 'success');

                    // Show S3 success popup if available
                    if (window.showS3SuccessPopup) {
                        window.showS3SuccessPopup(data.s3_export);
                    }
                } else {
                    message += ` ⚠️ S3 export failed: ${data.s3_export.error || 'Unknown error'}`;
                    showNotification(message, 'warning');
                }
            } else {
                message += ' Files saved locally.';
                showNotification(message, 'success');
            }

            // Set filename for download button (buttons are always enabled now)
            const downloadBtn = document.getElementById('downloadBtn');
            if (downloadBtn) {
                downloadBtn.setAttribute('data-filename', data.output_file);
                console.log('✅ Download filename set:', data.output_file);
                console.log('✅ Button element:', downloadBtn);
                console.log('✅ Attribute verified:', downloadBtn.getAttribute('data-filename'));
            } else {
                console.error('❌ Download button element not found!');
            }

            // Store final document data AND filename globally as backup
            window.finalDocumentData = data;
            window.reviewedDocumentFilename = data.output_file;  // Global backup
            console.log('✅ Stored globally: window.reviewedDocumentFilename =', window.reviewedDocumentFilename);

            console.log('✅ Submit all feedbacks completed successfully');
            console.log('📄 Output file:', data.output_file);
            console.log('💬 Comments count:', data.comments_count);
        } else {
            showNotification('❌ Submission failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        // Hide progress
        if (typeof hideProgress === 'function') {
            hideProgress();
        } else if (window.hideProgress) {
            window.hideProgress();
        }

        console.error('Submit feedbacks error:', error);
        showNotification('❌ Submission failed: ' + error.message, 'error');
    });
};

/**
 * UNIFIED Download Document Function
 * Downloads the final reviewed document
 */
window.downloadDocument = function() {
    console.log('📥 UNIFIED downloadDocument called');

    // Get session ID
    const sessionId = window.currentSession ||
                     (typeof currentSession !== 'undefined' ? currentSession : null) ||
                     sessionStorage.getItem('currentSession');

    if (!sessionId) {
        if (typeof showNotification === 'function') {
            showNotification('No active session. Please upload a document first.', 'error');
        } else {
            alert('No active session. Please upload a document first.');
        }
        return;
    }

    console.log('📥 Session ID:', sessionId);

    // Check multiple sources for filename
    const downloadBtn = document.getElementById('downloadBtn');
    let filename = null;

    if (downloadBtn) {
        filename = downloadBtn.getAttribute('data-filename');
        console.log('📥 Button data-filename attribute:', filename);
    }

    // Fallback to global variable
    if (!filename && window.reviewedDocumentFilename) {
        console.log('⚠️ Using global fallback filename:', window.reviewedDocumentFilename);
        filename = window.reviewedDocumentFilename;
    }

    // Fallback to finalDocumentData
    if (!filename && window.finalDocumentData && window.finalDocumentData.output_file) {
        console.log('⚠️ Using finalDocumentData filename:', window.finalDocumentData.output_file);
        filename = window.finalDocumentData.output_file;
    }

    if (filename) {
        console.log('📥 Downloading:', filename);
        window.location.href = `/download/${filename}`;

        if (typeof showNotification === 'function') {
            showNotification('📥 Downloading document...', 'info');
        }
    } else {
        // Make API call to get latest document for session
        console.log('📥 No cached filename, fetching from backend...');

        fetch(`/get_latest_document?session_id=${sessionId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.filename) {
                    console.log('📥 Got filename from backend:', data.filename);
                    // Store for future use
                    window.reviewedDocumentFilename = data.filename;
                    if (downloadBtn) {
                        downloadBtn.setAttribute('data-filename', data.filename);
                    }
                    // Download
                    window.location.href = `/download/${data.filename}`;
                    if (typeof showNotification === 'function') {
                        showNotification('📥 Downloading document...', 'info');
                    }
                } else {
                    if (typeof showNotification === 'function') {
                        showNotification('No reviewed document yet. Click "Submit All Feedbacks" first to generate the final document.', 'warning');
                    } else {
                        alert('No reviewed document yet. Click "Submit All Feedbacks" first to generate the final document.');
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching document:', error);
                if (typeof showNotification === 'function') {
                    showNotification('No reviewed document yet. Click "Submit All Feedbacks" first to generate the final document.', 'warning');
                } else {
                    alert('No reviewed document yet. Click "Submit All Feedbacks" first to generate the final document.');
                }
            });
    }
};

// CRITICAL: Ensure downloadDocument is immediately accessible
if (typeof window.downloadDocument !== 'function') {
    console.error('❌ CRITICAL: downloadDocument not attached to window!');
}

/**
 * UNIFIED Export to S3 Function
 * Exports complete review to AWS S3 cloud storage
 */
window.exportToS3 = function() {
    console.log('☁️ UNIFIED exportToS3 called');

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

    console.log('☁️ Session ID found:', sessionId);

    // Confirm export
    if (!confirm('Export complete review to AWS S3?\n\nThis will include:\n• Original document\n• Reviewed document with comments\n• All feedback and analysis data\n• Activity logs\n\nThe data will be uploaded to S3 bucket.\n\nContinue?')) {
        console.log('☁️ User cancelled S3 export');
        return;
    }

    console.log('☁️ User confirmed S3 export, proceeding...');

    // Show progress
    if (typeof showProgress === 'function') {
        showProgress('Exporting to S3...');
    } else if (window.showProgress) {
        window.showProgress('Exporting to S3...');
    }

    // Call backend
    fetch('/export_to_s3', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId
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
        } else if (window.hideProgress) {
            window.hideProgress();
        }

        if (data.success) {
            const exportResult = data.export_result;

            if (exportResult && exportResult.success) {
                // Show detailed success message
                const message = `✅ Successfully exported to S3!\n\n` +
                              `📁 Folder: ${exportResult.folder_name || 'Unknown'}\n` +
                              `📦 Files: ${exportResult.total_files || 0}\n` +
                              `☁️ Bucket: ${exportResult.bucket || 'felix-s3-bucket'}\n` +
                              `📍 Location: ${exportResult.location || 'S3'}`;

                showNotification(message, 'success');

                // Show modal if showModal function exists
                if (typeof showModal === 'function') {
                    showModal('genericModal', '☁️ S3 Export Successful', `
                        <div style="padding: 20px; text-align: center;">
                            <div style="font-size: 4em; margin-bottom: 20px;">✅</div>
                            <h3 style="color: #2ecc71; margin-bottom: 20px;">Successfully Exported to S3!</h3>

                            <div style="background: #f0fff4; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: left;">
                                <h4 style="color: #2ecc71; margin-bottom: 15px;">📊 Export Details:</h4>
                                <p style="margin: 5px 0;"><strong>📁 Folder:</strong> ${exportResult.folder_name || 'Unknown'}</p>
                                <p style="margin: 5px 0;"><strong>📦 Files Uploaded:</strong> ${exportResult.total_files || 0}</p>
                                <p style="margin: 5px 0;"><strong>☁️ Bucket:</strong> ${exportResult.bucket || 'felix-s3-bucket'}</p>
                                <p style="margin: 5px 0;"><strong>💬 Comments:</strong> ${data.comments_count || 0}</p>
                                <p style="margin: 5px 0;"><strong>📍 S3 Location:</strong> <code style="background: #e8f5e9; padding: 2px 6px; border-radius: 3px;">${exportResult.location || 'S3'}</code></p>
                            </div>

                            <div style="background: #fff3cd; padding: 15px; border-radius: 10px; text-align: left;">
                                <h4 style="color: #f39c12; margin-bottom: 10px;">📝 Exported Files:</h4>
                                <ul style="margin: 10px 0; padding-left: 20px;">
                                    <li>Original Document</li>
                                    <li>Reviewed Document with Comments</li>
                                    <li>Feedback Data (JSON)</li>
                                    <li>Activity Logs</li>
                                    <li>Statistics Report</li>
                                </ul>
                            </div>

                            <button class="btn btn-success" onclick="closeModal('genericModal')" style="margin-top: 20px; padding: 12px 30px;">
                                ✅ Close
                            </button>
                        </div>
                    `);
                }

                console.log('✅ S3 export completed successfully');
            } else {
                // S3 export failed
                const errorMsg = exportResult?.error || 'Unknown error';
                showNotification(`❌ S3 export failed: ${errorMsg}`, 'error');

                if (typeof showModal === 'function') {
                    showModal('genericModal', '❌ S3 Export Failed', `
                        <div style="padding: 20px; text-align: center;">
                            <div style="font-size: 4em; margin-bottom: 20px;">❌</div>
                            <h3 style="color: #e74c3c; margin-bottom: 20px;">S3 Export Failed</h3>
                            <p style="color: #666; margin-bottom: 20px;">${errorMsg}</p>
                            <p style="color: #999; font-size: 0.9em;">Your data is still saved locally. Check S3 configuration or try again.</p>
                            <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="margin-top: 20px;">Close</button>
                        </div>
                    `);
                }
            }
        } else {
            showNotification('❌ Export failed: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        // Hide progress
        if (typeof hideProgress === 'function') {
            hideProgress();
        } else if (window.hideProgress) {
            window.hideProgress();
        }

        console.error('Export to S3 error:', error);

        if (typeof showNotification === 'function') {
            showNotification('❌ Export failed: ' + error.message, 'error');
        } else {
            alert('❌ Export failed: ' + error.message);
        }
    });
};

// CRITICAL: Ensure exportToS3 is immediately accessible
if (typeof window.exportToS3 !== 'function') {
    console.error('❌ CRITICAL: exportToS3 not attached to window!');
}

/**
 * UNIFIED Revert Feedback Decision Function
 * Alias for revertFeedback - handles button calls
 */
window.revertFeedbackDecision = function(feedbackId, eventOrSection) {
    console.log('🔄 UNIFIED revertFeedbackDecision called (delegating to revertFeedback)');
    // Delegate to the main revertFeedback function
    return window.revertFeedback(feedbackId, eventOrSection);
};

// CRITICAL: Ensure revertFeedbackDecision is immediately accessible
if (typeof window.revertFeedbackDecision !== 'function') {
    console.error('❌ CRITICAL: revertFeedbackDecision not attached to window!');
}

// Log successful load
console.log('✅ UNIFIED button fixes loaded successfully!');
console.log('   - acceptFeedback:', typeof window.acceptFeedback);
console.log('   - rejectFeedback:', typeof window.rejectFeedback);
console.log('   - revertFeedback:', typeof window.revertFeedback);
console.log('   - revertFeedbackDecision:', typeof window.revertFeedbackDecision);
console.log('   - updateFeedback:', typeof window.updateFeedback);
console.log('   - addCommentToFeedback:', typeof window.addCommentToFeedback);
console.log('   - submitAllFeedbacks:', typeof window.submitAllFeedbacks);
console.log('   - downloadDocument:', typeof window.downloadDocument);
console.log('   - exportToS3:', typeof window.exportToS3);

// CRITICAL VALIDATION: Ensure all functions are properly attached
const requiredFunctions = [
    'acceptFeedback',
    'rejectFeedback',
    'revertFeedback',
    'revertFeedbackDecision',
    'updateFeedback',
    'addCommentToFeedback',
    'submitAllFeedbacks',
    'downloadDocument',
    'exportToS3'
];

let allFunctionsValid = true;
requiredFunctions.forEach(funcName => {
    if (typeof window[funcName] !== 'function') {
        console.error(`❌ CRITICAL: window.${funcName} is NOT a function!`);
        allFunctionsValid = false;
    }
});

if (allFunctionsValid) {
    console.log('🎉 All button functions unified and ready!');
    console.log('✅ All 9 critical functions verified and accessible globally');
} else {
    console.error('❌ CRITICAL ERROR: Some functions failed to attach to window object!');
}
