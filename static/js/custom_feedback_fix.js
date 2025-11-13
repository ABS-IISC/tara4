// Custom Feedback Fix - Consolidated functionality
console.log('Loading custom feedback fix...');

// Ensure global variables exist
window.currentSession = window.currentSession || null;
window.sections = window.sections || [];
window.currentSectionIndex = window.currentSectionIndex || 0;
window.userFeedbackHistory = window.userFeedbackHistory || [];

// Main custom feedback function
function addCustomFeedback() {
    console.log('addCustomFeedback called');
    
    const typeElement = document.getElementById('customType');
    const categoryElement = document.getElementById('customCategory');
    const descriptionElement = document.getElementById('customDescription');
    
    if (!typeElement || !categoryElement || !descriptionElement) {
        showNotification('Custom feedback form elements not found', 'error');
        return;
    }
    
    const type = typeElement.value;
    const category = categoryElement.value;
    const description = descriptionElement.value.trim();
    
    if (!description) {
        showNotification('Please enter feedback description', 'error');
        return;
    }
    
    if (!window.currentSession) {
        showNotification('No active session. Please upload a document first.', 'error');
        return;
    }
    
    if (!window.sections || window.currentSectionIndex < 0 || !window.sections[window.currentSectionIndex]) {
        showNotification('No section selected. Please select a section first.', 'error');
        return;
    }
    
    const currentSectionName = window.sections[window.currentSectionIndex];
    
    console.log('Sending custom feedback:', {
        session_id: window.currentSession,
        section_name: currentSectionName,
        type: type,
        category: category,
        description: description
    });
    
    // Show loading state
    const submitButton = document.querySelector('button[onclick="addCustomFeedback()"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Adding...';
    }
    
    fetch('/add_custom_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: window.currentSession,
            section_name: currentSectionName,
            type: type,
            category: category,
            description: description
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);\n        }\n        return response.json();\n    })\n    .then(data => {\n        console.log('Response data:', data);\n        \n        if (data.success) {\n            showNotification('Custom feedback added successfully!', 'success');\n            \n            // Clear the form\n            descriptionElement.value = '';\n            \n            // Add to local history\n            const feedbackItem = data.feedback_item || {\n                id: `custom_${Date.now()}`,\n                type: type,\n                category: category,\n                description: description,\n                section: currentSectionName,\n                timestamp: new Date().toISOString(),\n                user_created: true\n            };\n            \n            window.userFeedbackHistory.push(feedbackItem);\n            \n            // Display the feedback immediately\n            displayUserFeedback(feedbackItem);\n            \n            // Update statistics if function exists\n            if (typeof updateStatistics === 'function') {\n                updateStatistics();\n            }\n            \n            // Update custom feedback list if function exists\n            if (typeof updateAllCustomFeedbackList === 'function') {\n                updateAllCustomFeedbackList();\n            }\n            \n            // Refresh user feedback list if function exists\n            if (typeof refreshUserFeedbackList === 'function') {\n                refreshUserFeedbackList();\n            }\n        } else {\n            showNotification(data.error || 'Failed to add custom feedback', 'error');\n        }\n    })\n    .catch(error => {\n        console.error('Custom feedback error:', error);\n        showNotification('Failed to add custom feedback: ' + error.message, 'error');\n    })\n    .finally(() => {\n        // Reset button state\n        if (submitButton) {\n            submitButton.disabled = false;\n            submitButton.textContent = '🌟 Add My Feedback';\n        }\n    });\n}\n\n// Display user feedback function\nfunction displayUserFeedback(feedbackItem) {\n    const container = document.getElementById('userFeedbackDisplay');\n    if (!container) {\n        console.warn('userFeedbackDisplay container not found');\n        return;\n    }\n    \n    const feedbackDiv = document.createElement('div');\n    feedbackDiv.className = 'feedback-item user-feedback';\n    feedbackDiv.style.background = '#e8f5e8';\n    feedbackDiv.style.borderLeft = '4px solid #2ecc71';\n    feedbackDiv.style.padding = '15px';\n    feedbackDiv.style.margin = '10px 0';\n    feedbackDiv.style.borderRadius = '8px';\n    feedbackDiv.id = `user-feedback-${feedbackItem.id}`;\n    \n    const typeClass = `type-${feedbackItem.type}`;\n    const timestamp = new Date(feedbackItem.timestamp).toLocaleTimeString();\n    \n    feedbackDiv.innerHTML = `\n        <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;\">\n            <div>\n                <span class=\"feedback-type ${typeClass}\" style=\"background: #2ecc71; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600; text-transform: uppercase;\">${feedbackItem.type}</span>\n                <span style=\"color: #2ecc71; font-weight: bold; margin-left: 10px;\">👤 Your Feedback</span>\n                <span style=\"color: #7f8c8d; font-size: 0.9em; margin-left: 10px;\">${feedbackItem.category}</span>\n                <span style=\"color: #7f8c8d; font-size: 0.8em; margin-left: 10px;\">${timestamp}</span>\n            </div>\n        </div>\n        <p style=\"margin: 10px 0;\"><strong>Your Input:</strong> ${feedbackItem.description}</p>\n        <div style=\"margin-top: 10px; padding: 8px; background: rgba(46, 204, 113, 0.1); border-radius: 5px; font-size: 0.9em; color: #27ae60;\">\n            ✅ This feedback has been recorded and will be included in the final document.\n        </div>\n    `;\n    \n    container.appendChild(feedbackDiv);\n    \n    // Scroll to show the new feedback\n    feedbackDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });\n}\n\n// Update all custom feedback list function\nfunction updateAllCustomFeedbackList() {\n    const container = document.getElementById('customFeedbackList');\n    if (!container) return;\n    \n    const currentSectionName = window.sections[window.currentSectionIndex];\n    if (!currentSectionName) {\n        container.innerHTML = '<div style=\"text-align: center; padding: 20px; color: #666;\">No section selected</div>';\n        return;\n    }\n    \n    const allFeedback = window.userFeedbackHistory.filter(item => item.section === currentSectionName);\n    \n    if (allFeedback.length === 0) {\n        container.innerHTML = '<div style=\"text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; color: #666; border: 2px dashed #ddd;\"><p style=\"margin: 0; font-style: italic;\">No custom feedback for this section yet.</p><p style=\"margin: 5px 0 0 0; font-size: 0.9em;\">Add your first feedback above!</p></div>';\n        return;\n    }\n    \n    // Sort by timestamp (newest first)\n    allFeedback.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));\n    \n    container.innerHTML = allFeedback.map((item, index) => {\n        const timestamp = new Date(item.timestamp).toLocaleTimeString();\n        const typeColors = {\n            'addition': '#3498db',\n            'clarification': '#f39c12', \n            'disagreement': '#e74c3c',\n            'enhancement': '#9b59b6',\n            'alternative': '#1abc9c',\n            'context': '#34495e',\n            'suggestion': '#2ecc71',\n            'important': '#f39c12',\n            'critical': '#e74c3c',\n            'positive': '#27ae60'\n        };\n        const typeColor = typeColors[item.type] || '#95a5a6';\n        \n        return `\n            <div style=\"background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 4px solid ${typeColor}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);\">\n                <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;\">\n                    <div>\n                        <span style=\"background: ${typeColor}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600; text-transform: uppercase;\">${item.type}</span>\n                        <span style=\"color: #7f8c8d; font-size: 0.8em; margin-left: 8px;\">🕰️ ${timestamp}</span>\n                    </div>\n                </div>\n                <div style=\"color: #555; font-size: 0.9em; line-height: 1.4;\">\n                    <strong>${item.category}:</strong> ${item.description}\n                </div>\n            </div>\n        `;\n    }).join('');\n}\n\n// Refresh user feedback list function\nfunction refreshUserFeedbackList() {\n    console.log('Refreshing user feedback list...');\n    updateAllCustomFeedbackList();\n    \n    // Update counter if it exists\n    const currentSectionName = window.sections[window.currentSectionIndex];\n    if (currentSectionName) {\n        const sectionFeedbackCount = window.userFeedbackHistory.filter(item => item.section === currentSectionName).length;\n        \n        const counter = document.getElementById('customFeedbackCounter');\n        const countSpan = document.getElementById('customCount');\n        \n        if (counter && countSpan) {\n            countSpan.textContent = sectionFeedbackCount;\n            counter.style.display = sectionFeedbackCount > 0 ? 'block' : 'none';\n        }\n    }\n}\n\n// Clear section custom feedback function\nfunction clearAllSectionCustomFeedback() {\n    if (!window.currentSession || window.currentSectionIndex < 0) {\n        showNotification('No active section', 'error');\n        return;\n    }\n    \n    const currentSectionName = window.sections[window.currentSectionIndex];\n    const sectionFeedback = window.userFeedbackHistory.filter(item => item.section === currentSectionName);\n    \n    if (sectionFeedback.length === 0) {\n        showNotification('No custom feedback to clear in this section', 'info');\n        return;\n    }\n    \n    if (confirm(`Are you sure you want to clear all ${sectionFeedback.length} custom feedback items from \"${currentSectionName}\"?`)) {\n        // Remove from history\n        window.userFeedbackHistory = window.userFeedbackHistory.filter(item => item.section !== currentSectionName);\n        \n        // Clear display\n        const userFeedbackDisplay = document.getElementById('userFeedbackDisplay');\n        if (userFeedbackDisplay) {\n            userFeedbackDisplay.innerHTML = '';\n        }\n        \n        // Update lists\n        updateAllCustomFeedbackList();\n        refreshUserFeedbackList();\n        \n        if (typeof updateStatistics === 'function') {\n            updateStatistics();\n        }\n        \n        showNotification(`Cleared ${sectionFeedback.length} custom feedback items from this section!`, 'success');\n    }\n}\n\n// Show notification function (ensure it exists)\nif (typeof showNotification !== 'function') {\n    window.showNotification = function(message, type = 'info') {\n        console.log(`${type.toUpperCase()}: ${message}`);\n        \n        // Create a simple notification\n        const notification = document.createElement('div');\n        notification.style.cssText = `\n            position: fixed;\n            top: 20px;\n            right: 20px;\n            padding: 15px 20px;\n            border-radius: 8px;\n            color: white;\n            font-weight: 500;\n            z-index: 1001;\n            max-width: 300px;\n            word-wrap: break-word;\n        `;\n        \n        const colors = {\n            'success': '#2ecc71',\n            'error': '#e74c3c',\n            'info': '#3498db',\n            'warning': '#f39c12'\n        };\n        \n        notification.style.background = colors[type] || colors.info;\n        notification.textContent = message;\n        \n        document.body.appendChild(notification);\n        \n        setTimeout(() => {\n            if (notification.parentNode) {\n                notification.parentNode.removeChild(notification);\n            }\n        }, 4000);\n    };\n}\n\nconsole.log('Custom feedback fix loaded successfully');\n