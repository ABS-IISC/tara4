// Text Highlighting and Commenting Functions
window.currentHighlightColor = window.currentHighlightColor || 'yellow';
window.highlightedTexts = window.highlightedTexts || [];
window.highlightCounter = window.highlightCounter || 0;
window.currentSelectedText = window.currentSelectedText || '';
window.currentSelectedRange = window.currentSelectedRange || null;

// Set highlight color and enable selection mode
function setHighlightColor(color) {
    currentHighlightColor = color;
    
    // Update button states
    document.querySelectorAll('.highlight-tools button').forEach(btn => {
        btn.style.border = '1px solid #ddd';
    });
    
    event.target.style.border = '3px solid #333';
    
    showNotification(`Highlight color set to ${color}. Select text to highlight.`, 'info');
    enableTextSelection();
}

// Save highlighted text and show comment dialog
function saveHighlightedText() {
    if (!currentSelectedText || !currentSelectedRange) {
        showNotification('No text selected. Please select text first.', 'error');
        return;
    }
    
    const highlightId = `highlight_${++highlightCounter}_${Date.now()}`;
    
    try {
        // Create highlight span
        const highlightSpan = document.createElement('span');
        highlightSpan.className = 'text-highlight';
        highlightSpan.id = highlightId;
        highlightSpan.style.backgroundColor = currentHighlightColor;
        highlightSpan.style.padding = '2px 4px';
        highlightSpan.style.borderRadius = '3px';
        highlightSpan.style.cursor = 'pointer';
        highlightSpan.style.border = '1px solid rgba(0,0,0,0.2)';
        highlightSpan.title = 'Click to add comment or view existing comments';
        
        // Wrap the selected text
        currentSelectedRange.surroundContents(highlightSpan);
        
        // Store highlight data
        const highlightData = {
            id: highlightId,
            text: currentSelectedText,
            color: currentHighlightColor,
            section: window.sections && window.currentSectionIndex >= 0 ? window.sections[window.currentSectionIndex] : 'Unknown',
            timestamp: new Date().toISOString(),
            comments: []
        };
        
        highlightedTexts.push(highlightData);
        
        // Clear selection
        window.getSelection().removeAllRanges();
        currentSelectedText = '';
        currentSelectedRange = null;
        
        // Hide save button
        document.getElementById('saveHighlightBtn').style.display = 'none';
        
        // Show comment dialog immediately
        showHighlightCommentDialog(highlightId, highlightData.text);
        
        showNotification(`Text highlighted with ${currentHighlightColor}! Add your comment.`, 'success');
        
    } catch (error) {
        console.error('Highlighting error:', error);
        showNotification('Could not highlight this text. Try selecting simpler text.', 'error');
    }
}

// Clear all highlights in current section
function clearHighlights() {
    if (confirm('Are you sure you want to clear all highlights and their comments? This will also remove the associated feedback from your custom feedback list.')) {
        const docContent = document.getElementById('documentContent');
        const highlights = docContent.querySelectorAll('.text-highlight');
        
        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
            parent.normalize();
        });
        
        // Clear highlight data
        const currentSectionName = window.sections && window.currentSectionIndex >= 0 ?
            window.sections[window.currentSectionIndex] : null;
        if (!currentSectionName) return;
        const highlightIds = highlightedTexts.filter(h => h.section === currentSectionName).map(h => h.id);
        
        // Remove highlights for current section
        highlightedTexts = highlightedTexts.filter(h => h.section !== currentSectionName);
        
        // Remove highlight-related user feedback from display
        highlightIds.forEach(highlightId => {
            const feedbackElements = document.querySelectorAll(`[id*="${highlightId}"]`);
            feedbackElements.forEach(el => el.remove());
        });
        
        // Remove from user feedback history
        if (window.userFeedbackHistory) {
            window.userFeedbackHistory = window.userFeedbackHistory.filter(item =>
                !(item.section === currentSectionName && item.highlight_id)
            );
        }
        
        // Clear from session storage
        sessionStorage.removeItem(`highlights_${currentSectionName}`);
        
        updateAllCustomFeedbackList();
        updateStatistics();
        showNotification('All highlights and associated comments cleared!', 'success');
    }
}

// Enable text selection for highlighting
function enableTextSelection() {
    const docContent = document.getElementById('documentContent');
    
    // Remove existing event listeners
    docContent.removeEventListener('mouseup', handleTextSelection);
    docContent.removeEventListener('click', handleHighlightClick);
    
    // Add new event listeners
    docContent.addEventListener('mouseup', handleTextSelection);
    docContent.addEventListener('click', handleHighlightClick);
}

// Handle text selection
function handleTextSelection(event) {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    
    if (selection.rangeCount === 0 || selectedText === '') {
        // Hide save button if no selection
        document.getElementById('saveHighlightBtn').style.display = 'none';
        currentSelectedText = '';
        currentSelectedRange = null;
        return;
    }
    
    if (selectedText.length < 3) {
        showNotification('Please select at least 3 characters to highlight.', 'error');
        return;
    }
    
    // Check if selection is within document content
    const docContent = document.getElementById('documentContent');
    const range = selection.getRangeAt(0);
    
    if (!docContent.contains(range.commonAncestorContainer)) {
        showNotification('Please select text within the document content.', 'error');
        return;
    }
    
    // Store current selection
    currentSelectedText = selectedText;
    currentSelectedRange = range.cloneRange();
    
    // Show save button
    const saveBtn = document.getElementById('saveHighlightBtn');
    saveBtn.style.display = 'inline-block';
    
    showNotification(`Text selected: "${selectedText.substring(0, 30)}${selectedText.length > 30 ? '...' : ''}". Click "Save & Comment" to add feedback.`, 'info');
}

// Handle clicking on existing highlights
function handleHighlightClick(event) {
    if (!event.target.classList.contains('text-highlight')) return;
    
    event.preventDefault();
    event.stopPropagation();
    
    const highlightId = event.target.id;
    const highlightData = highlightedTexts.find(h => h.id === highlightId);
    
    // Show options dialog for existing highlight
    showHighlightOptionsDialog(highlightId, highlightData ? highlightData.text : event.target.textContent);
}

// Show highlight options dialog
function showHighlightOptionsDialog(highlightId, selectedText) {
    const highlightData = highlightedTexts.find(h => h.id === highlightId);
    const existingComments = highlightData ? highlightData.comments : [];
    
    const modalContent = `
        <div style="max-height: 70vh; overflow-y: auto; padding: 20px;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">📝 Highlighted Text Options</h3>
            
            <div style="background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid ${highlightData ? highlightData.color : 'yellow'};">
                <h4 style="color: #4f46e5; margin-bottom: 10px;">📝 Highlighted Text:</h4>
                <div style="background: white; padding: 10px; border-radius: 5px; font-style: italic; color: #333; border: 1px solid #ddd;">
                    "${selectedText.length > 200 ? selectedText.substring(0, 200) + '...' : selectedText}"
                </div>
            </div>
            
            ${existingComments.length > 0 ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #2ecc71; margin-bottom: 10px;">💬 Existing Comments (${existingComments.length}):</h4>
                    ${existingComments.map((comment, index) => `
                        <div style="background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #2ecc71;">
                            <div style="font-size: 0.9em; color: #27ae60; margin-bottom: 5px;">
                                <strong>${comment.type.toUpperCase()}</strong> - ${comment.category}
                            </div>
                            <div>${comment.description}</div>
                            <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                                ${new Date(comment.timestamp).toLocaleString()}
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            <div style="text-align: center; margin-bottom: 20px;">
                <button class="btn btn-primary" onclick="closeModal('genericModal'); showHighlightCommentDialog('${highlightId}', \`${selectedText.replace(/`/g, '\\`').replace(/'/g, "\\'")}\`)">➕ Add New Comment</button>
                <button class="btn btn-info" onclick="editHighlightColor('${highlightId}'); closeModal('genericModal');">🎨 Change Color</button>
                <button class="btn btn-warning" onclick="removeHighlight('${highlightId}'); closeModal('genericModal');">🗑️ Remove Highlight</button>
                <button class="btn btn-secondary" onclick="closeModal('genericModal')">❌ Close</button>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Highlight Options', modalContent);
}

// Remove individual highlight
function removeHighlight(highlightId) {
    const highlightElement = document.getElementById(highlightId);
    if (highlightElement) {
        const parent = highlightElement.parentNode;
        parent.replaceChild(document.createTextNode(highlightElement.textContent), highlightElement);
        parent.normalize();
        
        // Remove from data
        highlightedTexts = highlightedTexts.filter(h => h.id !== highlightId);
        
        // Remove related feedback
        if (window.userFeedbackHistory) {
            window.userFeedbackHistory = window.userFeedbackHistory.filter(item => item.highlight_id !== highlightId);
        }
        
        updateAllCustomFeedbackList();
        showNotification('Highlight removed!', 'success');
    }
}

// Show comment dialog for highlight
function showHighlightCommentDialog(highlightId, selectedText) {
    const highlightData = highlightedTexts.find(h => h.id === highlightId);
    const existingComments = highlightData ? highlightData.comments : [];
    
    const modalContent = `
        <div style="max-height: 70vh; overflow-y: auto; padding: 20px;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">💬 Add Comment to Highlighted Text</h3>
            
            <div style="background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid ${currentHighlightColor};">
                <h4 style="color: #4f46e5; margin-bottom: 10px;">📝 Selected Text:</h4>
                <div style="background: white; padding: 10px; border-radius: 5px; font-style: italic; color: #333; border: 1px solid #ddd;">
                    "${selectedText.length > 200 ? selectedText.substring(0, 200) + '...' : selectedText}"
                </div>
            </div>
            
            ${existingComments.length > 0 ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #2ecc71; margin-bottom: 10px;">💭 Existing Comments:</h4>
                    ${existingComments.map((comment, index) => `
                        <div style="background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #2ecc71;">
                            <div style="font-size: 0.9em; color: #27ae60; margin-bottom: 5px;">
                                <strong>${comment.type.toUpperCase()}</strong> - ${comment.category}
                            </div>
                            <div>${comment.description}</div>
                            <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                                ${new Date(comment.timestamp).toLocaleString()}
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            <div style="background: white; padding: 20px; border-radius: 10px; border: 2px solid #4f46e5;">
                <h4 style="color: #4f46e5; margin-bottom: 15px;">✨ Add New Comment</h4>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <div>
                        <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">🏷️ Type:</label>
                        <select id="highlightCommentType" style="width: 100%; padding: 10px; border: 2px solid #4f46e5; border-radius: 8px;">
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
                        <select id="highlightCommentCategory" style="width: 100%; padding: 10px; border: 2px solid #4f46e5; border-radius: 8px;">
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
                    <label style="font-weight: 600; color: #555; margin-bottom: 5px; display: block;">📝 Your Comment:</label>
                    <textarea id="highlightCommentText" placeholder="Add your comment about this highlighted text..." style="width: 100%; height: 100px; padding: 12px; border: 2px solid #4f46e5; border-radius: 8px; resize: vertical;"></textarea>
                </div>
                
                <div style="text-align: center;">
                    <button class="btn btn-success" onclick="saveHighlightComment('${highlightId}')" style="padding: 12px 25px; margin: 5px; border-radius: 20px; font-weight: 600;">💾 Save Comment</button>
                    <button class="btn btn-warning" onclick="removeHighlight('${highlightId}'); closeModal('genericModal');" style="padding: 12px 25px; margin: 5px; border-radius: 20px;">🗑️ Remove Highlight</button>
                    <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="padding: 12px 25px; margin: 5px; border-radius: 20px;">❌ Cancel</button>
                </div>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Highlight Comment', modalContent);
}

// Save highlight comment
function saveHighlightComment(highlightId) {
    const type = document.getElementById('highlightCommentType').value;
    const category = document.getElementById('highlightCommentCategory').value;
    const description = document.getElementById('highlightCommentText').value.trim();
    
    if (!description) {
        showNotification('Please enter a comment description.', 'error');
        return;
    }
    
    const highlightData = highlightedTexts.find(h => h.id === highlightId);
    if (!highlightData) {
        showNotification('Highlight data not found.', 'error');
        return;
    }
    
    // Create comment data
    const commentData = {
        type: type,
        category: category,
        description: description,
        timestamp: new Date().toISOString(),
        highlight_id: highlightId,
        highlighted_text: highlightData.text
    };
    
    // Add to highlight data
    highlightData.comments.push(commentData);
    
    // Send to backend to save with session
    fetch('/add_custom_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: window.currentSession,
            section_name: window.sections && window.currentSectionIndex >= 0 ? window.sections[window.currentSectionIndex] : 'Unknown',
            type: type,
            category: category,
            description: `[Highlighted: "${highlightData.text.substring(0, 50)}${highlightData.text.length > 50 ? '...' : ''}"] ${description}`,
            highlight_id: highlightId,
            highlighted_text: highlightData.text
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Create feedback item for display
            const feedbackItem = {
                id: data.feedback_item.id,
                type: type,
                category: category,
                description: `[Highlighted: "${highlightData.text.substring(0, 50)}${highlightData.text.length > 50 ? '...' : ''}"] ${description}`,
                section: window.sections && window.currentSectionIndex >= 0 ? window.sections[window.currentSectionIndex] : 'Unknown',
                timestamp: new Date().toISOString(),
                user_created: true,
                highlight_id: highlightId,
                highlighted_text: highlightData.text,
                risk_level: type === 'critical' ? 'High' : type === 'important' ? 'Medium' : 'Low'
            };
            
            // Add to user feedback history
            if (!window.userFeedbackHistory) {
                window.userFeedbackHistory = [];
            }
            window.userFeedbackHistory.push(feedbackItem);
            
            // Display the feedback
            displayUserFeedback(feedbackItem);
            
            // Update statistics
            updateStatistics();
            
            // Update all custom feedback list
            updateAllCustomFeedbackList();
            
            // Close modal
            closeModal('genericModal');
            
            showNotification('Highlight comment saved successfully!', 'success');
        } else {
            showNotification('Failed to save highlight comment: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error saving highlight comment:', error);
        showNotification('Failed to save highlight comment: ' + error.message, 'error');
    });
}

// Edit highlight color
function editHighlightColor(highlightId) {
    const highlightElement = document.getElementById(highlightId);
    const highlightData = highlightedTexts.find(h => h.id === highlightId);
    
    if (!highlightElement || !highlightData) {
        showNotification('Highlight not found.', 'error');
        return;
    }
    
    const modalContent = `
        <div style="text-align: center; padding: 20px;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">🎨 Change Highlight Color</h3>
            
            <div style="background: #f8f9ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h4 style="color: #4f46e5; margin-bottom: 15px;">Current Highlight:</h4>
                <div style="background: ${highlightData.color}; padding: 10px; border-radius: 5px; color: #333; font-weight: bold; margin-bottom: 15px;">
                    "${highlightData.text.substring(0, 100)}${highlightData.text.length > 100 ? '...' : ''}"
                </div>
                
                <h4 style="color: #4f46e5; margin-bottom: 15px;">Choose New Color:</h4>
                <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                    <button onclick="changeHighlightColor('${highlightId}', 'yellow')" style="background: #ffd700; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">🟡 Yellow</button>
                    <button onclick="changeHighlightColor('${highlightId}', 'lightgreen')" style="background: #90ee90; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">🟢 Green</button>
                    <button onclick="changeHighlightColor('${highlightId}', 'lightblue')" style="background: #add8e6; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">🔵 Blue</button>
                    <button onclick="changeHighlightColor('${highlightId}', 'lightcoral')" style="background: #f08080; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">🔴 Red</button>
                    <button onclick="changeHighlightColor('${highlightId}', 'lightgray')" style="background: #d3d3d3; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">⚪ Gray</button>
                </div>
            </div>
            
            <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="padding: 12px 25px; border-radius: 20px;">
                ❌ Cancel
            </button>
        </div>
    `;
    
    showModal('genericModal', 'Change Highlight Color', modalContent);
}

// Change highlight color
function changeHighlightColor(highlightId, newColor) {
    const highlightElement = document.getElementById(highlightId);
    const highlightData = highlightedTexts.find(h => h.id === highlightId);
    
    if (highlightElement && highlightData) {
        // Update element style
        highlightElement.style.backgroundColor = newColor;
        
        // Update data
        highlightData.color = newColor;
        
        // Save to session storage
        const currentSectionName = window.sections && window.currentSectionIndex >= 0 ?
            window.sections[window.currentSectionIndex] : null;
        if (!currentSectionName) return;
        const sectionHighlights = highlightedTexts.filter(h => h.section === currentSectionName);
        sessionStorage.setItem(`highlights_${currentSectionName}`, JSON.stringify(sectionHighlights));
        
        closeModal('genericModal');
        showNotification(`Highlight color changed to ${newColor}!`, 'success');
    }
}

// Save current section highlights to session storage
function saveCurrentSectionHighlights() {
    if (window.currentSectionIndex >= 0 && window.sections && window.sections[window.currentSectionIndex]) {
        const currentSectionName = window.sections[window.currentSectionIndex];
        const sectionHighlights = highlightedTexts.filter(h => h.section === currentSectionName);
        
        // Store highlights in session storage
        sessionStorage.setItem(`highlights_${currentSectionName}`, JSON.stringify(sectionHighlights));
    }
}

// Restore highlights for a section
function restoreSectionHighlights(sectionName) {
    try {
        const storedHighlights = sessionStorage.getItem(`highlights_${sectionName}`);
        if (storedHighlights) {
            const sectionHighlights = JSON.parse(storedHighlights);
            
            // Clear current highlights for this section
            highlightedTexts = highlightedTexts.filter(h => h.section !== sectionName);
            
            // Restore highlights
            sectionHighlights.forEach(highlight => {
                restoreHighlight(highlight);
                highlightedTexts.push(highlight);
            });
        }
    } catch (error) {
        console.error('Error restoring highlights:', error);
    }
}

// Restore individual highlight
function restoreHighlight(highlightData) {
    const docContent = document.getElementById('documentContent');
    if (!docContent) return;
    
    // Find text nodes that contain the highlighted text
    const walker = document.createTreeWalker(
        docContent,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    let node;
    while (node = walker.nextNode()) {
        const text = node.textContent;
        const highlightIndex = text.indexOf(highlightData.text);
        
        if (highlightIndex !== -1) {
            try {
                const range = document.createRange();
                range.setStart(node, highlightIndex);
                range.setEnd(node, highlightIndex + highlightData.text.length);
                
                const highlightSpan = document.createElement('span');
                highlightSpan.className = 'text-highlight';
                highlightSpan.id = highlightData.id;
                highlightSpan.style.backgroundColor = highlightData.color;
                highlightSpan.style.padding = '2px 4px';
                highlightSpan.style.borderRadius = '3px';
                highlightSpan.style.cursor = 'pointer';
                highlightSpan.style.border = '1px solid rgba(0,0,0,0.2)';
                highlightSpan.title = 'Click to add comment or remove highlight';
                
                range.surroundContents(highlightSpan);
                break;
            } catch (error) {
                console.error('Error restoring individual highlight:', error);
            }
        }
    }
}