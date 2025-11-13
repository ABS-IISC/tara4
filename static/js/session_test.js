// Session Test and Debug Functions for AI-Prism

console.log('Session test script loaded');

// Function to manually set a test session (for debugging)
function setTestSession() {
    const testSessionId = 'test-session-' + Date.now();
    
    // Set in all possible locations
    window.currentSession = testSessionId;
    if (typeof currentSession !== 'undefined') {
        currentSession = testSessionId;
    }
    sessionStorage.setItem('currentSession', testSessionId);
    
    // Set test sections
    window.sections = ['Test Section 1', 'Test Section 2'];
    if (typeof sections !== 'undefined') {
        sections = ['Test Section 1', 'Test Section 2'];
    }
    
    console.log('Test session set:', testSessionId);
    showNotification('Test session created: ' + testSessionId, 'success');
    
    // Enable complete review button for testing
    const completeBtn = document.getElementById('completeReviewBtn');
    if (completeBtn) {
        completeBtn.disabled = false;
    }
    
    return testSessionId;
}

// Function to clear all session data
function clearAllSessions() {
    window.currentSession = null;
    if (typeof currentSession !== 'undefined') {
        currentSession = null;
    }
    sessionStorage.removeItem('currentSession');
    
    window.sections = [];
    if (typeof sections !== 'undefined') {
        sections = [];
    }
    
    console.log('All sessions cleared');
    showNotification('All session data cleared', 'info');
    
    // Disable complete review button
    const completeBtn = document.getElementById('completeReviewBtn');
    if (completeBtn) {
        completeBtn.disabled = true;
    }
}

// Function to test S3 connectivity
function testS3Connection() {
    console.log('Testing S3 connection...');
    showNotification('Testing S3 connectivity...', 'info');
    
    fetch('/test_s3_connection')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const status = data.s3_status;
            
            const modalContent = `
                <div style="padding: 20px;">
                    <h3 style="color: #4f46e5; margin-bottom: 20px;">☁️ S3 Connection Status</h3>
                    <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 12px;">
                        <div><strong>Connected:</strong> ${status.connected ? '✅ Yes' : '❌ No'}</div>
                        <div><strong>Bucket Accessible:</strong> ${status.bucket_accessible ? '✅ Yes' : '❌ No'}</div>
                        ${status.bucket_name ? `<div><strong>Bucket:</strong> ${status.bucket_name}</div>` : ''}
                        ${status.base_path ? `<div><strong>Base Path:</strong> ${status.base_path}</div>` : ''}
                        ${status.error ? `<div style="color: red;"><strong>Error:</strong> ${status.error}</div>` : ''}
                    </div>
                    <div style="margin-top: 20px; text-align: center;">
                        <button class="btn btn-primary" onclick="closeModal('genericModal')" style="padding: 10px 20px;">Close</button>
                    </div>
                </div>
            `;
            
            showModal('genericModal', 'S3 Connection Test', modalContent);
            
            if (status.connected && status.bucket_accessible) {
                showNotification('✅ S3 connection successful!', 'success');
            } else {
                showNotification('⚠️ S3 connection issues detected', 'warning');
            }
        } else {
            showNotification('❌ S3 test failed: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('S3 test error:', error);
        showNotification('❌ S3 test failed: ' + error.message, 'error');
    });
}

// Function to test complete review with current session
function testCompleteReview() {
    console.log('Testing complete review...');
    
    // Check session status first
    if (typeof checkSessionStatus === 'function') {
        checkSessionStatus();
    }
    
    // Try to call complete review
    setTimeout(() => {
        if (typeof completeReview === 'function') {
            completeReview();
        } else {
            console.error('completeReview function not found');
            showNotification('completeReview function not found', 'error');
        }
    }, 1000);
}

// Make functions globally available
window.setTestSession = setTestSession;
window.clearAllSessions = clearAllSessions;
window.testCompleteReview = testCompleteReview;
window.testS3Connection = testS3Connection;

// Auto-check session status on load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log('Auto-checking session status...');
        if (typeof checkSessionStatus === 'function') {
            const status = checkSessionStatus();
            console.log('Initial session status:', status);
        }
    }, 2000);
});