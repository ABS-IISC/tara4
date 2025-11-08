// Custom Feedback Functions for AI-Prism
// Handles individual AI feedback custom comments and management

/**
 * Add custom feedback to a specific AI suggestion
 * @param {string} aiId - The AI feedback item ID
 * @param {Event} event - The click event
 */
function addCustomToAI(aiId, event) {
    if (event) event.stopPropagation();
    
    const customDiv = document.getElementById(`custom-${aiId}`);
    if (customDiv.style.display === 'none') {
        // Hide all other custom forms
        document.querySelectorAll('.ai-custom-feedback').forEach(div => {
            div.style.display = 'none';
        });
        customDiv.style.display = 'block';
        
        // Focus on the description textarea
        const descTextarea = document.getElementById(`aiCustomDesc-${aiId}`);
        if (descTextarea) {
            setTimeout(() => descTextarea.focus(), 100);
        }
    } else {
        customDiv.style.display = 'none';
    }
}

/**
 * Cancel adding custom feedback to AI suggestion
 * @param {string} aiId - The AI feedback item ID
 */
function cancelAICustom(aiId) {
    const customDiv = document.getElementById(`custom-${aiId}`);
    const descTextarea = document.getElementById(`aiCustomDesc-${aiId}`);
    
    if (customDiv) customDiv.style.display = 'none';
    if (descTextarea) descTextarea.value = '';
}

/**
 * Save custom feedback for a specific AI suggestion
 * @param {string} aiId - The AI feedback item ID
 */
function saveAICustomFeedback(aiId) {
    const type = document.getElementById(`aiCustomType-${aiId}`).value;
    const category = document.getElementById(`aiCustomCategory-${aiId}`).value;
    const description = document.getElementById(`aiCustomDesc-${aiId}`).value.trim();
    
    if (!description) {
        showNotification('Please enter your custom feedback', 'error');
        return;
    }
    
    // Find the AI feedback item for reference
    const aiItem = window.sectionData?.[sections[currentSectionIndex]]?.feedback?.find(item => item.id === aiId);
    const aiReference = aiItem ? `${aiItem.type}: ${aiItem.description.substring(0, 50)}...` : 'AI Suggestion';
    
    fetch('/add_custom_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: currentSession,
            section_name: sections[currentSectionIndex],
            type: type,
            category: category,
            description: description,
            ai_reference: aiReference,
            ai_id: aiId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Custom feedback added to AI suggestion!', 'success');
            
            // Add to local history
            const feedbackItem = data.feedback_item;
            feedbackItem.section = sections[currentSectionIndex];
            userFeedbackHistory.push(feedbackItem);
            
            displayUserFeedback(feedbackItem);
            cancelAICustom(aiId);
            updateStatistics();
            updateAllCustomFeedbackList();
            
            // Immediately refresh the custom feedback section logs
            refreshUserFeedbackList();
        } else {
            showNotification(data.error || 'Add feedback failed', 'error');
        }
    })
    .catch(error => {
        showNotification('Add feedback failed: ' + error.message, 'error');
    });
}

/**
 * Clear all custom feedback for a specific AI suggestion
 * @param {string} aiId - The AI feedback item ID
 * @param {Event} event - The click event
 */
function clearAICustomFeedback(aiId, event) {
    if (event) event.stopPropagation();
    
    if (confirm('Are you sure you want to clear all custom feedback for this AI suggestion?')) {
        // Hide the custom feedback form
        const customDiv = document.getElementById(`custom-${aiId}`);
        if (customDiv) {
            customDiv.style.display = 'none';
        }
        
        // Clear the form fields
        const typeSelect = document.getElementById(`aiCustomType-${aiId}`);
        const categorySelect = document.getElementById(`aiCustomCategory-${aiId}`);
        const descTextarea = document.getElementById(`aiCustomDesc-${aiId}`);
        
        if (typeSelect) typeSelect.selectedIndex = 0;
        if (categorySelect) categorySelect.selectedIndex = 0;
        if (descTextarea) descTextarea.value = '';
        
        // Remove any related user feedback from the current section
        const currentSectionName = sections[currentSectionIndex];
        if (userFeedbackHistory && currentSectionName) {
            // Count items to be removed
            const itemsToRemove = userFeedbackHistory.filter(item => 
                item.section === currentSectionName && item.ai_id === aiId
            );
            
            // Filter out feedback related to this AI item
            userFeedbackHistory = userFeedbackHistory.filter(item => 
                !(item.section === currentSectionName && item.ai_id === aiId)
            );
            
            // Remove from display
            const userFeedbackDisplay = document.getElementById('userFeedbackDisplay');
            if (userFeedbackDisplay) {
                const relatedFeedback = userFeedbackDisplay.querySelectorAll(`[data-ai-id="${aiId}"]`);
                relatedFeedback.forEach(element => element.remove());
            }
            
            // Update the custom feedback list
            updateAllCustomFeedbackList();
            updateStatistics();
            
            // Refresh the custom feedback section logs
            if (typeof refreshUserFeedbackList === 'function') {
                refreshUserFeedbackList();
            }
            
            showNotification(`Cleared ${itemsToRemove.length} custom feedback item(s) for this AI suggestion!`, 'success');
        } else {
            showNotification('Custom feedback cleared for this AI suggestion!', 'success');
        }
    }
}

/**
 * Clear all custom feedback for the current section
 */
function clearAllSectionCustomFeedback() {
    if (!currentSession || currentSectionIndex < 0) {
        showNotification('No active section', 'error');
        return;
    }
    
    const currentSectionName = sections[currentSectionIndex];
    const sectionFeedback = userFeedbackHistory.filter(item => item.section === currentSectionName);
    
    if (sectionFeedback.length === 0) {
        showNotification('No custom feedback to clear in this section', 'info');
        return;
    }
    
    if (confirm(`Are you sure you want to clear all ${sectionFeedback.length} custom feedback items from "${currentSectionName}"?`)) {
        // Remove from history
        userFeedbackHistory = userFeedbackHistory.filter(item => item.section !== currentSectionName);
        
        // Clear display
        const userFeedbackDisplay = document.getElementById('userFeedbackDisplay');
        if (userFeedbackDisplay) {
            userFeedbackDisplay.innerHTML = '';
        }
        
        // Hide all custom forms
        document.querySelectorAll('.ai-custom-feedback').forEach(div => {
            div.style.display = 'none';
            // Clear form fields
            const form = div.closest('.feedback-item');
            if (form) {
                const aiId = form.getAttribute('data-feedback-id');
                if (aiId) {
                    const typeSelect = document.getElementById(`aiCustomType-${aiId}`);
                    const categorySelect = document.getElementById(`aiCustomCategory-${aiId}`);
                    const descTextarea = document.getElementById(`aiCustomDesc-${aiId}`);
                    
                    if (typeSelect) typeSelect.selectedIndex = 0;
                    if (categorySelect) categorySelect.selectedIndex = 0;
                    if (descTextarea) descTextarea.value = '';
                }
            }
        });
        
        updateAllCustomFeedbackList();
        updateStatistics();
        
        // Refresh the custom feedback section logs
        refreshUserFeedbackList();
        
        showNotification(`Cleared ${sectionFeedback.length} custom feedback items from this section!`, 'success');
    }
}

/**
 * Toggle all custom feedback forms for AI suggestions
 * @param {boolean} show - Whether to show or hide all forms
 */
function toggleAllAICustomForms(show = false) {
    document.querySelectorAll('.ai-custom-feedback').forEach(div => {
        div.style.display = show ? 'block' : 'none';
    });
    
    if (show) {
        showNotification('All custom feedback forms opened', 'info');
    } else {
        showNotification('All custom feedback forms closed', 'info');
    }
}

/**
 * Get count of custom feedback for a specific AI suggestion
 * @param {string} aiId - The AI feedback item ID
 * @returns {number} Count of custom feedback items
 */
function getAICustomFeedbackCount(aiId) {
    if (!userFeedbackHistory || !sections[currentSectionIndex]) return 0;
    
    const currentSectionName = sections[currentSectionIndex];
    return userFeedbackHistory.filter(item => 
        item.section === currentSectionName && item.ai_id === aiId
    ).length;
}

/**
 * Update button states based on custom feedback count
 */
function updateAICustomButtonStates() {
    document.querySelectorAll('.feedback-item').forEach(item => {
        const aiId = item.getAttribute('data-feedback-id');
        if (aiId) {
            const count = getAICustomFeedbackCount(aiId);
            const addButton = item.querySelector(`button[onclick*="addCustomToAI('${aiId}'"]`);
            const clearButton = item.querySelector(`button[onclick*="clearAICustomFeedback('${aiId}'"]`);
            
            if (addButton) {
                if (count > 0) {
                    addButton.innerHTML = `✨ Custom (${count})`;
                    addButton.className = 'btn btn-success';
                } else {
                    addButton.innerHTML = '✨ Add Custom';
                    addButton.className = 'btn btn-info';
                }
            }
            
            if (clearButton) {
                clearButton.style.display = count > 0 ? 'inline-block' : 'none';
            }
        }
    });
    
    // Update section custom feedback counter
    updateSectionCustomFeedbackCounter();
}

/**
 * Update the section custom feedback counter
 */
function updateSectionCustomFeedbackCounter() {
    if (typeof sections === 'undefined' || typeof currentSectionIndex === 'undefined' || currentSectionIndex < 0) {
        return;
    }
    
    const currentSectionName = sections[currentSectionIndex];
    const sectionFeedbackCount = userFeedbackHistory ? 
        userFeedbackHistory.filter(item => item.section === currentSectionName).length : 0;
    
    const counter = document.getElementById('customFeedbackCounter');
    const countSpan = document.getElementById('customCount');
    
    if (counter && countSpan) {
        countSpan.textContent = sectionFeedbackCount;
        counter.style.display = sectionFeedbackCount > 0 ? 'block' : 'none';
    }
}

// Auto-update button states when feedback changes
if (typeof updateStatistics === 'function') {
    const originalUpdateStatistics = updateStatistics;
    updateStatistics = function() {
        originalUpdateStatistics.apply(this, arguments);
        updateAICustomButtonStates();
    };
}