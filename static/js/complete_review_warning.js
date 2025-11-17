/**
 * Complete Review Warning System
 *
 * This file adds a warning system before completing review to ensure users
 * have accepted/rejected feedback items properly.
 *
 * Prevents the issue where users complete review without accepting any feedback,
 * resulting in a document with no comments.
 */

// Override the performCompleteReview function with feedback check
const originalPerformCompleteReview = window.performCompleteReview;

window.performCompleteReview = function(exportToS3 = false) {
    const sessionId = window.currentSession || currentSession || sessionStorage.getItem('currentSession');

    if (!sessionId) {
        showNotification('No active session available', 'error');
        return;
    }

    // STEP 1: Check if any feedback was accepted before proceeding
    showProgress('Checking feedback status...');

    fetch(`/get_accepted_feedback_count?session_id=${sessionId}`)
    .then(response => response.json())
    .then(countData => {
        hideProgress();

        if (!countData.success) {
            showNotification('Failed to check feedback status', 'error');
            return;
        }

        const willBeInDocument = countData.will_be_in_document || 0;
        const totalGenerated = countData.total_generated || 0;
        const pendingCount = countData.pending_count || 0;
        const rejectedCount = countData.rejected_count || 0;
        const acceptedCount = countData.accepted_count || 0;
        const customCount = countData.custom_count || 0;

        // STEP 2: Warn user if no feedback will be in document
        if (willBeInDocument === 0 && totalGenerated > 0) {
            const warningModalContent = `
                <div style="padding: 30px; text-align: center;">
                    <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);">
                        <h2 style="margin: 0 0 15px 0; font-size: 2em;">⚠️ WARNING</h2>
                        <h3 style="margin: 0; font-size: 1.5em; font-weight: 600;">NO FEEDBACK ACCEPTED</h3>
                    </div>

                    <div style="background: #fef2f2; padding: 25px; border-radius: 15px; margin-bottom: 25px; border: 3px solid #ef4444; text-align: left;">
                        <h4 style="color: #dc2626; margin-bottom: 20px;">⚠️ The final document will have ZERO comments!</h4>

                        <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                            <h5 style="color: #4f46e5; margin-bottom: 15px;">📊 Feedback Status:</h5>
                            <div style="display: grid; gap: 10px;">
                                <div style="padding: 10px; background: #f8f9ff; border-radius: 8px; border-left: 4px solid #4f46e5;">
                                    <strong>🤖 AI Generated:</strong> ${totalGenerated} items
                                </div>
                                <div style="padding: 10px; background: #f0fdf4; border-radius: 8px; border-left: 4px solid #10b981;">
                                    <strong>✅ Accepted:</strong> ${willBeInDocument} items
                                </div>
                                <div style="padding: 10px; background: #fef2f2; border-radius: 8px; border-left: 4px solid #ef4444;">
                                    <strong>❌ Rejected:</strong> ${rejectedCount} items
                                </div>
                                <div style="padding: 10px; background: #fffbeb; border-radius: 8px; border-left: 4px solid #f59e0b;">
                                    <strong>⏳ Pending:</strong> ${pendingCount} items (not reviewed yet)
                                </div>
                            </div>
                        </div>

                        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 20px; border-radius: 12px; border: 2px solid #f59e0b;">
                            <h5 style="color: #b45309; margin-bottom: 15px;">📋 How to Accept Feedback:</h5>
                            <ol style="color: #78350f; margin: 0; padding-left: 20px; line-height: 1.8;">
                                <li>Go to each section that was analyzed</li>
                                <li>Review the AI feedback items shown</li>
                                <li>Click <strong>✅ Accept</strong> for items you want in the document</li>
                                <li>Click <strong>❌ Reject</strong> for items you don't want</li>
                                <li>Optionally add custom feedback using the "Add Custom Feedback" button</li>
                                <li>Then come back and complete the review</li>
                            </ol>
                        </div>
                    </div>

                    <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 25px;">
                        <p style="margin: 0; color: #dc2626; font-weight: 600; font-size: 1.1em;">
                            ⚠️ If you continue, the document will have NO comments at all!
                        </p>
                    </div>

                    <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                        <button class="btn btn-success" onclick="closeModal('genericModal')" style="padding: 15px 30px; font-size: 16px; border-radius: 25px; font-weight: 700; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);">
                            ✅ Go Back and Accept Feedback
                        </button>
                        <button class="btn btn-danger" onclick="confirmProceedWithoutFeedback(${exportToS3})" style="padding: 15px 30px; font-size: 16px; border-radius: 25px; font-weight: 700;">
                            ⚠️ Continue Anyway (No Comments)
                        </button>
                    </div>
                </div>
            `;

            showModal('genericModal', 'WARNING: No Feedback Accepted', warningModalContent);
            return;
        }

        // STEP 3: Show summary and final confirmation (if some feedback accepted)
        if (totalGenerated > 0) {
            const summaryModalContent = `
                <div style="padding: 30px; text-align: center;">
                    <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);">
                        <h3 style="margin: 0 0 15px 0; font-size: 1.8em;">📊 Final Confirmation</h3>
                        <p style="margin: 0; font-size: 1.1em; opacity: 0.9;">Review your feedback before generating the document</p>
                    </div>

                    <div style="background: #f8f9ff; padding: 25px; border-radius: 15px; margin-bottom: 25px; border: 3px solid #4f46e5; text-align: left;">
                        <h4 style="color: #4f46e5; margin-bottom: 20px; text-align: center;">
                            <strong style="font-size: 1.5em; color: #10b981;">${willBeInDocument}</strong> comments will be added to your document
                        </h4>

                        <div style="display: grid; gap: 15px; margin-bottom: 20px;">
                            <div style="padding: 15px; background: white; border-radius: 12px; border-left: 5px solid #10b981; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                                <strong style="color: #10b981; font-size: 1.1em;">✅ Accepted AI Feedback:</strong>
                                <span style="float: right; font-size: 1.3em; font-weight: bold; color: #10b981;">${acceptedCount}</span>
                            </div>
                            <div style="padding: 15px; background: white; border-radius: 12px; border-left: 5px solid #3b82f6; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                                <strong style="color: #3b82f6; font-size: 1.1em;">📝 Custom Feedback:</strong>
                                <span style="float: right; font-size: 1.3em; font-weight: bold; color: #3b82f6;">${customCount}</span>
                            </div>
                            <div style="padding: 15px; background: white; border-radius: 12px; border-left: 5px solid #ef4444; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                                <strong style="color: #ef4444; font-size: 1.1em;">❌ Rejected (excluded):</strong>
                                <span style="float: right; font-size: 1.3em; font-weight: bold; color: #ef4444;">${rejectedCount}</span>
                            </div>
                            ${pendingCount > 0 ? `
                                <div style="padding: 15px; background: white; border-radius: 12px; border-left: 5px solid #f59e0b; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                                    <strong style="color: #f59e0b; font-size: 1.1em;">⏳ Pending (excluded):</strong>
                                    <span style="float: right; font-size: 1.3em; font-weight: bold; color: #f59e0b;">${pendingCount}</span>
                                </div>
                            ` : ''}
                        </div>

                        <div style="background: rgba(79, 70, 229, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                            <p style="margin: 0; color: #4f46e5; font-weight: 600; font-size: 0.95em;">
                                💡 Only <strong>accepted AI feedback</strong> and <strong>custom feedback</strong> will appear as comments in the final document.
                            </p>
                        </div>
                    </div>

                    <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                        <button class="btn btn-success" onclick="confirmProceedWithReview(${exportToS3})" style="padding: 15px 30px; font-size: 16px; border-radius: 25px; font-weight: 700; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);">
                            ✅ Generate Document (${willBeInDocument} comments)
                        </button>
                        <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="padding: 15px 30px; font-size: 16px; border-radius: 25px;">
                            ❌ Cancel
                        </button>
                    </div>
                </div>
            `;

            showModal('genericModal', 'Confirm Document Generation', summaryModalContent);
        } else {
            // No feedback generated at all - proceed directly
            proceedWithCompleteReview(exportToS3);
        }
    })
    .catch(error => {
        hideProgress();
        console.error('Failed to check feedback count:', error);
        // Proceed anyway if check fails
        if (confirm('Failed to verify feedback status. Continue with review completion anyway?')) {
            proceedWithCompleteReview(exportToS3);
        }
    });
};

// Helper function to proceed after user confirms
window.confirmProceedWithReview = function(exportToS3) {
    closeModal('genericModal');
    proceedWithCompleteReview(exportToS3);
};

// Helper function for proceeding without feedback
window.confirmProceedWithoutFeedback = function(exportToS3) {
    closeModal('genericModal');
    if (confirm('⚠️ FINAL WARNING\n\nYou are about to generate a document with ZERO comments.\n\nAre you absolutely sure?')) {
        proceedWithCompleteReview(exportToS3);
    }
};

// The actual complete review function (original logic)
window.proceedWithCompleteReview = function(exportToS3 = false) {
    const sessionId = window.currentSession || currentSession || sessionStorage.getItem('currentSession');

    showProgress('Completing review and generating final document...');

    fetch('/complete_review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: sessionId,
            export_to_s3: exportToS3
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProgress();

        if (data.success) {
            let message = `🎉 Review completed successfully!\n\n📄 Final document: ${data.output_file}\n💬 Comments added: ${data.comments_count}`;

            // Show S3 export success popup if all data saved successfully
            if (exportToS3 && data.s3_export) {
                if (data.s3_export.success) {
                    message += `\n\n☁️ S3 Export: SUCCESS\n📁 Location: ${data.s3_export.location}\n📦 Files exported: ${data.s3_export.total_files || 'Multiple'}`;

                    // Show special popup for successful S3 save
                    if (typeof showS3SuccessPopup === 'function') {
                        showS3SuccessPopup(data.s3_export);
                    }
                    showNotification('✅ All data saved in S3 successfully! Check the logs for details.', 'success');
                } else {
                    message += `\n\n⚠️ S3 Export: FAILED\n❌ Error: ${data.s3_export.error}\n💾 Files saved locally as backup`;
                    showNotification('⚠️ Review completed but S3 export failed. Files saved locally.', 'warning');
                }
            } else {
                showNotification('✅ Review completed successfully!', 'success');
            }

            // Show detailed results
            const modalContent = `
                <div style="text-align: center; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;">
                        <h3 style="margin: 0 0 10px 0;">🎉 Review Completed Successfully!</h3>
                        <p style="margin: 0; opacity: 0.9;">Your document analysis is complete</p>
                    </div>

                    <div style="background: #f8f9ff; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: left;">
                        <h4 style="color: #4f46e5; margin-bottom: 15px;">📊 Review Summary:</h4>
                        <div style="display: grid; gap: 10px;">
                            <div style="padding: 10px; background: white; border-radius: 8px; border-left: 4px solid #4f46e5;">
                                <strong>📄 Final Document:</strong> ${data.output_file}
                            </div>
                            <div style="padding: 10px; background: white; border-radius: 8px; border-left: 4px solid #10b981;">
                                <strong>💬 Comments Added:</strong> ${data.comments_count}
                            </div>
                            ${exportToS3 && data.s3_export ? `
                                <div style="padding: 10px; background: white; border-radius: 8px; border-left: 4px solid ${data.s3_export.success ? '#10b981' : '#ef4444'};">
                                    <strong>☁️ S3 Export:</strong> ${data.s3_export.success ? 'SUCCESS' : 'FAILED'}
                                    ${data.s3_export.success ? `<br><small>📁 ${data.s3_export.location}</small>` : `<br><small>❌ ${data.s3_export.error}</small>`}
                                </div>
                            ` : ''}
                        </div>
                    </div>

                    <div style="display: flex; gap: 15px; justify-center; flex-wrap: wrap;">
                        <button class="btn btn-primary" onclick="downloadFinalDocument('${data.output_file}')" style="padding: 12px 25px; border-radius: 20px;">
                            📥 Download Document
                        </button>
                        <button class="btn btn-info" onclick="startNewReview()" style="padding: 12px 25px; border-radius: 20px;">
                            🔄 Start New Review
                        </button>
                        <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="padding: 12px 25px; border-radius: 20px;">
                            ✅ Done
                        </button>
                    </div>
                </div>
            `;

            showModal('genericModal', 'Review Complete', modalContent);

            // Store final document data globally
            window.finalDocumentData = data;
        } else {
            showNotification(data.error || 'Review completion failed', 'error');
        }
    })
    .catch(error => {
        hideProgress();
        showNotification('Review completion failed: ' + error.message, 'error');
        console.error('Complete review error:', error);
    });
};

console.log('✅ Complete Review Warning System loaded');
