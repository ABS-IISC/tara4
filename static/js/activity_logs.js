/**
 * ============================================================================
 * ACTIVITY LOGS - BRAND NEW IMPLEMENTATION
 * ============================================================================
 * Created: 2025-11-16
 * Purpose: Clean, simple, bulletproof activity logs display
 * Replaces: All previous broken implementations
 *
 * Features:
 * - Simple panel display with real-time logs
 * - Live activity tracking
 * - Export functionality (JSON, CSV, TXT)
 * - Auto-refresh capability
 * - Session-based logging
 * ============================================================================
 */

console.log('🔥 Loading NEW Activity Logs module...');

// ============================================================================
// CONFIGURATION
// ============================================================================

const ACTIVITY_LOGS_CONFIG = {
    refreshInterval: 5000,  // 5 seconds auto-refresh
    maxDisplayLogs: 50,     // Maximum logs to display
    autoRefresh: false      // Auto-refresh disabled by default
};

// ============================================================================
// GLOBAL STATE
// ============================================================================

let activityLogsState = {
    isOpen: false,
    autoRefreshTimer: null,
    lastFetchTime: null,
    cachedLogs: []
};

// ============================================================================
// CORE FUNCTION: Show Activity Logs
// ============================================================================

window.showActivityLogs = function() {
    console.log('📋 Opening NEW Activity Logs...');

    // Get session ID
    const sessionId = getSessionId();

    if (!sessionId) {
        showNoSessionMessage();
        return;
    }

    // Mark as open
    activityLogsState.isOpen = true;

    // Show loading
    showLoadingState();

    // Fetch logs
    fetchActivityLogs(sessionId);
};

// ============================================================================
// SESSION MANAGEMENT
// ============================================================================

function getSessionId() {
    // Check multiple sources
    return window.currentSession ||
           (typeof currentSession !== 'undefined' ? currentSession : null) ||
           sessionStorage.getItem('currentSession');
}

// ============================================================================
// UI DISPLAY FUNCTIONS
// ============================================================================

function showNoSessionMessage() {
    const content = `
        <div style="text-align: center; padding: 60px 30px;">
            <div style="font-size: 5em; margin-bottom: 20px;">📋</div>
            <h2 style="color: #4f46e5; margin-bottom: 15px;">No Active Session</h2>
            <p style="color: #666; font-size: 1.1em; margin-bottom: 30px;">
                Please upload a document first to start tracking activities
            </p>
            <button class="btn btn-primary" onclick="closeModal('genericModal')"
                    style="padding: 12px 30px; border-radius: 20px; font-weight: 600;">
                Got It!
            </button>
        </div>
    `;

    if (typeof showModal === 'function') {
        showModal('genericModal', '📋 Activity Logs', content);
    } else {
        alert('No active session. Please upload a document first.');
    }
}

function showLoadingState() {
    const content = `
        <div style="text-align: center; padding: 60px 30px;">
            <div class="loading-spinner" style="font-size: 5em; margin-bottom: 20px; animation: spin 2s linear infinite;">
                ⏳
            </div>
            <h2 style="color: #4f46e5; margin-bottom: 15px;">Loading Activity Logs...</h2>
            <p style="color: #666;">Fetching session data...</p>
            <style>
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            </style>
        </div>
    `;

    if (typeof showModal === 'function') {
        showModal('genericModal', '📋 Activity Logs', content);
    }
}

function showErrorState(errorMessage) {
    const content = `
        <div style="text-align: center; padding: 60px 30px; background: linear-gradient(135deg, #fff5f5 0%, #fee2e2 100%); border-radius: 15px;">
            <div style="font-size: 5em; margin-bottom: 20px;">❌</div>
            <h2 style="color: #ef4444; margin-bottom: 15px;">Failed to Load Logs</h2>
            <p style="color: #666; margin-bottom: 30px;">${errorMessage || 'Unknown error occurred'}</p>
            <button class="btn btn-primary" onclick="closeModal('genericModal')"
                    style="padding: 12px 30px; border-radius: 20px; font-weight: 600;">
                Close
            </button>
        </div>
    `;

    if (typeof showModal === 'function') {
        showModal('genericModal', '📋 Activity Logs - Error', content);
    } else {
        alert('Error loading activity logs: ' + errorMessage);
    }
}

// ============================================================================
// DATA FETCHING
// ============================================================================

function fetchActivityLogs(sessionId) {
    console.log('🔍 Fetching activity logs for session:', sessionId);

    fetch(`/get_activity_logs?session_id=${sessionId}&format=json`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Activity logs received:', data);

            if (data.success) {
                activityLogsState.cachedLogs = data.logs || [];
                activityLogsState.lastFetchTime = new Date();
                displayActivityLogs(data);
            } else {
                throw new Error(data.error || 'Failed to load activity logs');
            }
        })
        .catch(error => {
            console.error('❌ Activity logs fetch error:', error);
            showErrorState(error.message);
        });
}

// ============================================================================
// DISPLAY ACTIVITY LOGS
// ============================================================================

function displayActivityLogs(data) {
    const logs = data.logs || [];
    const summary = data.summary || {};

    console.log(`📊 Displaying ${logs.length} activity logs`);

    const content = `
        <div style="max-height: 80vh; overflow-y: auto; padding: 20px;">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                        color: white; padding: 25px; border-radius: 12px; margin-bottom: 20px;">
                <h2 style="margin: 0 0 8px 0; font-size: 1.8em;">📋 Activity Logs</h2>
                <p style="margin: 0; opacity: 0.9;">Session activity tracking</p>
            </div>

            <!-- Summary Stats -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                        gap: 12px; margin-bottom: 20px;">

                <div style="background: #4f46e5; color: white; padding: 18px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 2em; font-weight: bold; margin-bottom: 5px;">
                        ${summary.total_activities || logs.length || 0}
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">Total</div>
                </div>

                <div style="background: #10b981; color: white; padding: 18px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 2em; font-weight: bold; margin-bottom: 5px;">
                        ${summary.success_count || 0}
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">Success</div>
                </div>

                <div style="background: #ef4444; color: white; padding: 18px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 2em; font-weight: bold; margin-bottom: 5px;">
                        ${summary.failed_count || 0}
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">Failed</div>
                </div>

                <div style="background: #f59e0b; color: white; padding: 18px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 2em; font-weight: bold; margin-bottom: 5px;">
                        ${summary.success_rate || 0}%
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">Rate</div>
                </div>
            </div>

            <!-- Activity List -->
            <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3 style="color: #4f46e5; margin: 0 0 15px 0; font-size: 1.2em;">📝 Recent Activities</h3>

                <div style="max-height: 400px; overflow-y: auto;">
                    ${logs && logs.length > 0 ? renderActivityList(logs) : '<p style="text-align: center; color: #999; padding: 40px;">No activities recorded yet</p>'}
                </div>
            </div>

            <!-- Action Buttons -->
            <div style="display: flex; gap: 10px; justify-content: center; margin-top: 20px; flex-wrap: wrap;">
                <button class="btn btn-success" onclick="exportActivityLogs()"
                        style="padding: 10px 24px; border-radius: 20px; font-weight: 600;">
                    📥 Export
                </button>
                <button class="btn btn-info" onclick="refreshActivityLogs()"
                        style="padding: 10px 24px; border-radius: 20px; font-weight: 600;">
                    🔄 Refresh
                </button>
                <button class="btn btn-secondary" onclick="closeModal('genericModal')"
                        style="padding: 10px 24px; border-radius: 20px; font-weight: 600;">
                    ✅ Close
                </button>
            </div>
        </div>
    `;

    if (typeof showModal === 'function') {
        showModal('genericModal', '📋 Activity Logs', content);
    }
}

// ============================================================================
// RENDER ACTIVITY LIST
// ============================================================================

function renderActivityList(logs) {
    // Take last 50 logs and reverse (newest first)
    const displayLogs = logs.slice(-ACTIVITY_LOGS_CONFIG.maxDisplayLogs).reverse();

    return displayLogs.map((log, index) => {
        const statusColor = getStatusColor(log.status);
        const statusIcon = getStatusIcon(log.status);
        const timestamp = log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A';
        const action = log.action ? log.action.replace(/_/g, ' ').toUpperCase() : 'UNKNOWN';

        return `
            <div style="display: flex; gap: 10px; padding: 12px;
                        background: ${index % 2 === 0 ? '#f8f9ff' : '#ffffff'};
                        border-radius: 8px; margin-bottom: 8px;
                        border-left: 4px solid ${statusColor};">

                <div style="font-size: 1.5em; min-width: 30px;">${statusIcon}</div>

                <div style="flex: 1;">
                    <div style="font-weight: 600; color: ${statusColor}; margin-bottom: 4px; font-size: 0.95em;">
                        ${action}
                    </div>

                    <div style="font-size: 0.85em; color: #666; margin-bottom: 4px;">
                        🕐 ${timestamp}
                    </div>

                    ${renderActivityDetails(log)}

                    ${log.error ? `
                        <div style="background: rgba(239, 68, 68, 0.1); padding: 8px;
                                    border-radius: 6px; margin-top: 6px; color: #ef4444; font-size: 0.85em;">
                            ❌ Error: ${log.error}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function renderActivityDetails(log) {
    if (!log.details || typeof log.details !== 'object') {
        return '';
    }

    const details = Object.entries(log.details)
        .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
        .join(' • ');

    if (details) {
        return `<div style="font-size: 0.8em; color: #555; margin-top: 4px;">${details}</div>`;
    }

    return '';
}

function getStatusColor(status) {
    const colors = {
        'success': '#10b981',
        'failed': '#ef4444',
        'warning': '#f59e0b',
        'in_progress': '#3b82f6'
    };
    return colors[status] || '#6b7280';
}

function getStatusIcon(status) {
    const icons = {
        'success': '✅',
        'failed': '❌',
        'warning': '⚠️',
        'in_progress': '🔄'
    };
    return icons[status] || '📌';
}

// ============================================================================
// EXPORT FUNCTIONALITY
// ============================================================================

window.exportActivityLogs = function() {
    console.log('📥 Exporting activity logs...');

    const sessionId = getSessionId();
    if (!sessionId) {
        if (typeof showNotification === 'function') {
            showNotification('No active session', 'error');
        } else {
            alert('No active session');
        }
        return;
    }

    // Show format selection
    const content = `
        <div style="text-align: center; padding: 40px 30px;">
            <h2 style="color: #4f46e5; margin-bottom: 25px;">📥 Export Activity Logs</h2>
            <p style="color: #666; margin-bottom: 30px;">Choose export format:</p>

            <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-bottom: 25px;">
                <button class="btn btn-primary" onclick="downloadActivityLogs('json')"
                        style="padding: 15px 30px; border-radius: 12px; font-weight: 600;">
                    📄 JSON
                </button>
                <button class="btn btn-success" onclick="downloadActivityLogs('csv')"
                        style="padding: 15px 30px; border-radius: 12px; font-weight: 600;">
                    📊 CSV
                </button>
                <button class="btn btn-info" onclick="downloadActivityLogs('txt')"
                        style="padding: 15px 30px; border-radius: 12px; font-weight: 600;">
                    📝 TXT
                </button>
            </div>

            <button class="btn btn-secondary" onclick="closeModal('genericModal')"
                    style="padding: 10px 24px; border-radius: 20px;">
                Cancel
            </button>
        </div>
    `;

    if (typeof showModal === 'function') {
        showModal('genericModal', 'Export Activity Logs', content);
    }
};

window.downloadActivityLogs = function(format) {
    console.log(`📥 Downloading activity logs as ${format}...`);

    const sessionId = getSessionId();
    if (!sessionId) {
        return;
    }

    // Close modal
    if (typeof closeModal === 'function') {
        closeModal('genericModal');
    }

    // Trigger download
    window.location.href = `/export_activity_logs?session_id=${sessionId}&format=${format}`;

    // Show notification
    if (typeof showNotification === 'function') {
        showNotification(`📥 Downloading as ${format.toUpperCase()}...`, 'info');
    }
};

// ============================================================================
// REFRESH FUNCTIONALITY
// ============================================================================

window.refreshActivityLogs = function() {
    console.log('🔄 Refreshing activity logs...');

    const sessionId = getSessionId();
    if (!sessionId) {
        return;
    }

    // Show loading
    showLoadingState();

    // Fetch fresh data
    setTimeout(() => {
        fetchActivityLogs(sessionId);
    }, 300);
};

// ============================================================================
// AUTO-REFRESH (Optional)
// ============================================================================

function startAutoRefresh() {
    if (activityLogsState.autoRefreshTimer) {
        return; // Already running
    }

    activityLogsState.autoRefreshTimer = setInterval(() => {
        if (activityLogsState.isOpen) {
            const sessionId = getSessionId();
            if (sessionId) {
                console.log('🔄 Auto-refreshing activity logs...');
                fetchActivityLogs(sessionId);
            }
        }
    }, ACTIVITY_LOGS_CONFIG.refreshInterval);

    console.log('✅ Auto-refresh enabled');
}

function stopAutoRefresh() {
    if (activityLogsState.autoRefreshTimer) {
        clearInterval(activityLogsState.autoRefreshTimer);
        activityLogsState.autoRefreshTimer = null;
        console.log('⏸️ Auto-refresh stopped');
    }
}

// ============================================================================
// CLEANUP
// ============================================================================

// Stop auto-refresh when modal closes
document.addEventListener('click', function(e) {
    if (e.target && e.target.matches && e.target.matches('.close')) {
        activityLogsState.isOpen = false;
        stopAutoRefresh();
    }
});

// ============================================================================
// INITIALIZATION
// ============================================================================

console.log('✅ NEW Activity Logs module loaded successfully!');
console.log('   - showActivityLogs:', typeof window.showActivityLogs);
console.log('   - exportActivityLogs:', typeof window.exportActivityLogs);
console.log('   - refreshActivityLogs:', typeof window.refreshActivityLogs);
console.log('   - downloadActivityLogs:', typeof window.downloadActivityLogs);

// ============================================================================
// END OF ACTIVITY LOGS MODULE
// ============================================================================
