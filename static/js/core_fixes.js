// Core fixes for Dark Mode, Reset, and Test S3 buttons
// This file contains ONLY the essential fixes

(function() {
    'use strict';
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeFixes);
    } else {
        initializeFixes();
    }
    
    function initializeFixes() {
        console.log('🔧 Core fixes initializing...');

        // Fix 1: Dark Mode Toggle
        setupDarkMode();

        // Fix 2: Reset Session
        setupReset();

        // Fix 3: Test S3
        setupS3Test();

        // Fix 4: Test Claude AI
        setupClaudeTest();

        console.log('✅ Core fixes loaded');
    }
    
    // Dark Mode Fix
    function setupDarkMode() {
        const darkModeBtn = document.getElementById('darkModeToggle');
        if (!darkModeBtn) return;

        // Load saved preference
        const savedMode = localStorage.getItem('darkMode') === 'true';
        if (savedMode) {
            document.body.classList.add('dark-mode');
            darkModeBtn.textContent = '☀️ Light Mode';
            darkModeBtn.className = 'btn btn-warning';
        }

        // Remove old listeners and onclick attribute, then add new one
        const newBtn = darkModeBtn.cloneNode(true);
        newBtn.removeAttribute('onclick'); // Critical: remove inline onclick to prevent conflicts
        darkModeBtn.parentNode.replaceChild(newBtn, darkModeBtn);

        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const isDark = document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', isDark);

            this.textContent = isDark ? '☀️ Light Mode' : '🌙 Dark Mode';
            this.className = isDark ? 'btn btn-warning' : 'btn btn-secondary';

            showNotification(isDark ? 'Dark mode enabled' : 'Light mode enabled', 'success');
        });
    }
    
    // Reset Session Fix
    function setupReset() {
        // Find reset button by onclick attribute
        const buttons = document.querySelectorAll('button');
        let resetBtn = null;
        
        buttons.forEach(btn => {
            if (btn.textContent.includes('Reset') || btn.onclick?.toString().includes('resetSession')) {
                resetBtn = btn;
            }
        });
        
        if (!resetBtn) return;
        
        // Remove old listener and add new one
        const newBtn = resetBtn.cloneNode(true);
        resetBtn.parentNode.replaceChild(newBtn, resetBtn);
        
        newBtn.addEventListener('click', function() {
            if (confirm('Reset session? All progress will be lost.')) {
                // Clear session data
                sessionStorage.clear();
                localStorage.removeItem('currentSession');
                
                // Reload page
                showNotification('Session reset. Reloading...', 'info');
                setTimeout(() => location.reload(), 1000);
            }
        });
    }
    
    // Test S3 Fix
    function setupS3Test() {
        // Find S3 test button
        const buttons = document.querySelectorAll('button');
        let s3Btn = null;

        buttons.forEach(btn => {
            if (btn.textContent.includes('Test S3') || btn.onclick?.toString().includes('testS3')) {
                s3Btn = btn;
            }
        });

        if (!s3Btn) return;

        // Remove old listener and add new one
        const newBtn = s3Btn.cloneNode(true);
        s3Btn.parentNode.replaceChild(newBtn, s3Btn);

        newBtn.addEventListener('click', function() {
            showNotification('Testing S3 connection...', 'info');

            fetch('/test_s3_connection')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.s3_status) {
                        const status = data.s3_status;

                        // Show detailed modal
                        showDetailedS3Status(status);

                        // Also show quick notification
                        if (status.connected && status.bucket_accessible) {
                            showNotification(`✅ S3 Connected: ${status.bucket_name}`, 'success');
                        } else {
                            showNotification(`⚠️ S3 Issue: ${status.error || 'Not accessible'}`, 'warning');
                        }
                    } else {
                        showNotification('❌ S3 test failed', 'error');
                    }
                })
                .catch(error => {
                    showNotification(`❌ S3 error: ${error.message}`, 'error');
                });
        });
    }

    // Test Claude AI Fix
    function setupClaudeTest() {
        // Find Claude test button
        const buttons = document.querySelectorAll('button');
        let claudeBtn = null;

        buttons.forEach(btn => {
            if (btn.textContent.includes('Test Claude') || btn.onclick?.toString().includes('testClaude')) {
                claudeBtn = btn;
            }
        });

        if (!claudeBtn) return;

        // Remove old listener and add new one
        const newBtn = claudeBtn.cloneNode(true);
        claudeBtn.parentNode.replaceChild(newBtn, claudeBtn);

        newBtn.addEventListener('click', function() {
            showNotification('Testing Claude AI connection...', 'info');

            fetch('/test_claude_connection')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status} ${response.statusText}`);
                    }
                    return response.text().then(text => {
                        try {
                            return JSON.parse(text);
                        } catch (e) {
                            console.error('Invalid JSON response:', text);
                            throw new Error('Server returned invalid response. Please check backend logs.');
                        }
                    });
                })
                .then(data => {
                    if (data.success && data.claude_status) {
                        const status = data.claude_status;

                        // Show detailed modal
                        showDetailedClaudeStatus(status);

                        // Also show quick notification
                        if (status.connected) {
                            showNotification(`✅ Claude Connected: ${status.model} (${status.response_time}s)`, 'success');
                        } else {
                            showNotification(`⚠️ Claude Issue: ${status.error || 'Not accessible'}`, 'warning');
                        }
                    } else {
                        showNotification(`❌ Claude test failed: ${data.error || 'Unknown error'}`, 'error');
                    }
                })
                .catch(error => {
                    console.error('Claude test error:', error);
                    showNotification(`❌ Claude error: ${error.message}`, 'error');
                });
        });
    }
    
    // Show detailed S3 status modal
    function showDetailedS3Status(status) {
        const modalContent = `
            <div style="padding: 25px; max-height: 70vh; overflow-y: auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
                <h2 style="color: #4f46e5; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.5em;">🗄️</span>
                    Amazon S3 Connection Details
                </h2>

                ${status.connected && status.bucket_accessible ? `
                    <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #10b981;">
                        <h3 style="color: #065f46; margin: 0; font-size: 1.1em;">✅ Connection Successful</h3>
                        <p style="color: #047857; margin: 5px 0 0 0;">S3 bucket is accessible and configured correctly</p>
                    </div>
                ` : `
                    <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #ef4444;">
                        <h3 style="color: #991b1b; margin: 0; font-size: 1.1em;">❌ Connection Failed</h3>
                        <p style="color: #b91c1c; margin: 5px 0 0 0;">${status.error || 'Unable to connect to S3 bucket'}</p>
                    </div>
                `}

                <div style="background: #f9fafb; padding: 20px; border-radius: 12px; border: 2px solid #e5e7eb;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151; width: 40%;">🌐 Service</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.service || 'Amazon S3'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🔗 Connection Type</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.connection_type || 'AWS SDK'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🪣 Bucket Name</td>
                            <td style="padding: 12px 0; color: #1f2937; font-family: monospace; background: #f3f4f6; padding: 4px 8px; border-radius: 4px;">${status.bucket_name || 'N/A'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">📁 Base Path</td>
                            <td style="padding: 12px 0; color: #1f2937; font-family: monospace; background: #f3f4f6; padding: 4px 8px; border-radius: 4px;">${status.base_path || 'N/A'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🔗 Full Path</td>
                            <td style="padding: 12px 0; color: #1f2937; font-family: monospace; font-size: 0.9em; background: #f3f4f6; padding: 4px 8px; border-radius: 4px; word-break: break-all;">${status.full_path || 'N/A'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🌍 Region</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.region || 'N/A'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🔐 Credentials</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.credentials_source || 'N/A'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🔑 Access Permissions</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.access_permissions || 'N/A'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">📦 SDK Version</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.sdk_version || 'boto3'}</td>
                        </tr>
                    </table>
                </div>

                <div style="text-align: center; margin-top: 25px;">
                    <button onclick="closeConnectionModal()" style="background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%); color: white; border: none; padding: 12px 30px; border-radius: 25px; font-size: 1em; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">Close</button>
                </div>
            </div>
        `;

        showConnectionModal(modalContent);
    }

    // Show detailed Claude status modal
    function showDetailedClaudeStatus(status) {
        const fallbackModelsList = status.fallback_models && status.fallback_models.length > 0
            ? status.fallback_models.map(m => `<li style="padding: 4px 0; color: #4b5563; font-size: 0.9em;">${m}</li>`).join('')
            : '<li style="padding: 4px 0; color: #9ca3af;">None configured</li>';

        const modalContent = `
            <div style="padding: 25px; max-height: 70vh; overflow-y: auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
                <h2 style="color: #4f46e5; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.5em;">🤖</span>
                    Claude AI Connection Details
                </h2>

                ${status.connected ? `
                    <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #10b981;">
                        <h3 style="color: #065f46; margin: 0; font-size: 1.1em;">✅ Connection Successful</h3>
                        <p style="color: #047857; margin: 5px 0 0 0;">Claude AI is responding correctly</p>
                        <p style="color: #047857; margin: 5px 0 0 0; font-size: 0.9em; font-style: italic;">"${status.test_response || 'Test successful'}"</p>
                    </div>
                ` : `
                    <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #ef4444;">
                        <h3 style="color: #991b1b; margin: 0; font-size: 1.1em;">❌ Connection Failed</h3>
                        <p style="color: #b91c1c; margin: 5px 0 0 0;">${status.error || 'Unable to connect to Claude AI'}</p>
                    </div>
                `}

                <div style="background: #f9fafb; padding: 20px; border-radius: 12px; border: 2px solid #e5e7eb; margin-bottom: 15px;">
                    <h3 style="color: #4f46e5; margin: 0 0 15px 0; font-size: 1.1em;">🎯 Primary Model Configuration</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151; width: 40%;">🌐 Service</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.service || 'Amazon Bedrock'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🔗 Connection Type</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.connection_type || 'AWS Bedrock Runtime'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🤖 Model Name</td>
                            <td style="padding: 12px 0; color: #1f2937; font-weight: 600;">${status.model || 'N/A'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🆔 Model ID</td>
                            <td style="padding: 12px 0; color: #1f2937; font-family: monospace; font-size: 0.9em; background: #f3f4f6; padding: 4px 8px; border-radius: 4px; word-break: break-all;">${status.model_id || 'N/A'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">⏱️ Response Time</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.response_time || 'N/A'}s</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🌍 Region</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.region || 'N/A'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🔐 Credentials</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.credentials_source || 'N/A'}</td>
                        </tr>
                    </table>
                </div>

                <div style="background: #f9fafb; padding: 20px; border-radius: 12px; border: 2px solid #e5e7eb;">
                    <h3 style="color: #4f46e5; margin: 0 0 15px 0; font-size: 1.1em;">⚙️ Model Parameters</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151; width: 40%;">📊 Max Tokens</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.max_tokens || 'N/A'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🌡️ Temperature</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.temperature || 'N/A'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">🧠 Reasoning</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.reasoning_enabled ? '✅ Enabled' : '❌ Disabled'} ${status.supports_reasoning ? '(Supported)' : '(Not Supported)'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">📦 API Version</td>
                            <td style="padding: 12px 0; color: #1f2937; font-family: monospace; font-size: 0.9em;">${status.anthropic_version || 'N/A'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; font-weight: 600; color: #374151;">📦 SDK Version</td>
                            <td style="padding: 12px 0; color: #1f2937;">${status.sdk_version || 'boto3'}</td>
                        </tr>
                    </table>
                </div>

                <div style="background: #fef3c7; padding: 15px; border-radius: 10px; margin-top: 15px; border-left: 5px solid #f59e0b;">
                    <h4 style="color: #92400e; margin: 0 0 10px 0; font-size: 1em;">🔄 Fallback Models (${status.fallback_models ? status.fallback_models.length : 0})</h4>
                    <ul style="margin: 0; padding-left: 20px;">
                        ${fallbackModelsList}
                    </ul>
                </div>

                <div style="text-align: center; margin-top: 25px;">
                    <button onclick="closeConnectionModal()" style="background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%); color: white; border: none; padding: 12px 30px; border-radius: 25px; font-size: 1em; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">Close</button>
                </div>
            </div>
        `;

        showConnectionModal(modalContent);
    }

    // Create and show connection modal
    function showConnectionModal(content) {
        // Remove existing modal if any
        closeConnectionModal();

        const modal = document.createElement('div');
        modal.id = 'connectionStatusModal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            backdrop-filter: blur(5px);
        `;

        const modalBox = document.createElement('div');
        modalBox.style.cssText = `
            background: white;
            border-radius: 16px;
            max-width: 700px;
            width: 90%;
            max-height: 85vh;
            overflow: hidden;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease;
        `;

        modalBox.innerHTML = content;
        modal.appendChild(modalBox);
        document.body.appendChild(modal);

        // Close on background click
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeConnectionModal();
            }
        });
    }

    // Close connection modal
    window.closeConnectionModal = function() {
        const modal = document.getElementById('connectionStatusModal');
        if (modal) {
            modal.remove();
        }
    };

    // Notification helper
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
            max-width: 350px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateX(400px);
            transition: transform 0.3s ease;
        `;
        
        // Set color based on type
        const colors = {
            success: '#2ecc71',
            error: '#e74c3c',
            info: '#3498db',
            warning: '#f39c12'
        };
        notification.style.background = colors[type] || '#95a5a6';
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.style.transform = 'translateX(0)', 100);
        
        // Animate out and remove
        setTimeout(() => {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }
    
    // Make functions globally available
    window.toggleDarkMode = function() {
        // Use the button's click event to ensure consistent behavior
        const btn = document.getElementById('darkModeToggle');
        if (btn) {
            btn.click();
        } else {
            // Fallback if button not found
            const isDark = document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', isDark);
            if (typeof showNotification === 'function') {
                showNotification(isDark ? 'Dark mode enabled' : 'Light mode enabled', 'success');
            }
        }
    };
    
    window.resetSession = function() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.textContent.includes('Reset')) btn.click();
        });
    };
    
    window.testS3Connection = function() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.textContent.includes('Test S3')) btn.click();
        });
    };

    window.testClaudeConnection = function() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.textContent.includes('Test Claude')) btn.click();
        });
    };
})();
