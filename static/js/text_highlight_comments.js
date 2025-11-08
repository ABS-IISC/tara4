// Text Highlighting with Comments Functionality
let selectedColor = 'yellow';
let highlightComments = [];
let highlightCounter = 0;

/**
 * Set the highlight color
 */
function setHighlightColor(color) {
    selectedColor = color;
    // Update button states
    document.querySelectorAll('.color-btn').forEach(btn => {
        btn.style.border = '2px solid #ddd';
    });
    event.target.style.border = '3px solid #333';
    showNotification(`Highlight color set to ${color}`, 'info');
}

/**
 * Handle text selection and highlighting
 */
function handleTextHighlight() {
    const selection = window.getSelection();
    if (selection.rangeCount === 0 || selection.toString().trim() === '') return;
    
    const selectedText = selection.toString().trim();
    if (selectedText.length < 3) {
        showNotification('Please select at least 3 characters', 'error');
        return;
    }
    
    const range = selection.getRangeAt(0);
    const highlightId = `highlight_${++highlightCounter}_${Date.now()}`;
    
    try {
        const span = document.createElement('span');
        span.className = 'text-highlight';
        span.id = highlightId;
        span.style.backgroundColor = selectedColor;
        span.style.padding = '2px 4px';
        span.style.borderRadius = '3px';
        span.style.cursor = 'pointer';
        span.title = 'Click to view/edit comments';
        
        range.surroundContents(span);
        
        // Store highlight data
        const highlightData = {
            id: highlightId,
            text: selectedText,
            color: selectedColor,
            section: sections[currentSectionIndex],
            comments: [],
            timestamp: new Date().toISOString()
        };
        
        highlightComments.push(highlightData);
        selection.removeAllRanges();
        
        // Show add comment dialog
        showAddCommentDialog(highlightId, selectedText);
        
    } catch (error) {
        showNotification('Could not highlight this text. Try selecting simpler text.', 'error');
    }
}

/**
 * Show add comment dialog
 */
function showAddCommentDialog(highlightId, selectedText) {
    // If no highlight ID provided, check for current selection
    if (!highlightId) {
        const selection = window.getSelection();
        if (selection.rangeCount === 0 || selection.toString().trim() === '') {
            showNotification('Please select text first to add a comment', 'error');
            return;
        }
        // Create highlight first
        handleTextHighlight();
        return;
    }
    const modalContent = `
        <div style="padding: 20px;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">💬 Add Comment to Highlighted Text</h3>
            
            <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid ${selectedColor};">
                <strong>Selected Text:</strong><br>
                <em>"${selectedText.length > 100 ? selectedText.substring(0, 100) + '...' : selectedText}"</em>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="font-weight: 600; margin-bottom: 5px; display: block;">Comment Type:</label>
                <select id="commentType" style="width: 100%; padding: 8px; border: 2px solid #4f46e5; border-radius: 5px;">
                    <option value="suggestion">Suggestion</option>
                    <option value="important">Important</option>
                    <option value="critical">Critical</option>
                    <option value="question">Question</option>
                    <option value="clarification">Clarification</option>
                </select>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="font-weight: 600; margin-bottom: 5px; display: block;">Your Comment:</label>
                <textarea id="commentText" placeholder="Add your comment about this highlighted text..." 
                    style="width: 100%; height: 100px; padding: 10px; border: 2px solid #4f46e5; border-radius: 5px; resize: vertical;"></textarea>
            </div>
            
            <div style="text-align: center;">
                <button class="btn btn-success" onclick="saveHighlightComment('${highlightId}')" style="margin: 5px;">💾 Save Comment</button>
                <button class="btn btn-secondary" onclick="closeModal('genericModal')" style="margin: 5px;">❌ Cancel</button>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Add Comment', modalContent);
}

/**
 * Save highlight comment
 */
function saveHighlightComment(highlightId) {
    const type = document.getElementById('commentType').value;
    const text = document.getElementById('commentText').value.trim();
    
    if (!text) {
        showNotification('Please enter a comment', 'error');
        return;
    }
    
    const highlight = highlightComments.find(h => h.id === highlightId);
    if (!highlight) return;
    
    const comment = {
        id: `comment_${Date.now()}`,
        type: type,
        text: text,
        timestamp: new Date().toISOString()
    };
    
    highlight.comments.push(comment);
    
    // Add to user feedback history
    const feedbackItem = {
        id: `highlight_${Date.now()}`,
        type: type,
        category: 'Text Highlighting',
        description: `Highlighted text: "${highlight.text.substring(0, 50)}..." - Comment: ${text}`,
        section: sections[currentSectionIndex],
        timestamp: new Date().toISOString(),
        user_created: true,
        highlight_id: highlightId,
        highlighted_text: highlight.text
    };
    
    userFeedbackHistory.push(feedbackItem);
    displayUserFeedback(feedbackItem);
    refreshUserFeedbackList();
    
    closeModal('genericModal');
    showNotification('Comment added to highlighted text!', 'success');
}

/**
 * Show update comments dialog
 */
function showUpdateCommentsDialog() {
    const currentSectionName = sections[currentSectionIndex];
    const sectionHighlights = highlightComments.filter(h => h.section === currentSectionName && h.comments.length > 0);
    
    if (sectionHighlights.length === 0) {
        showNotification('No highlighted comments in this section', 'info');
        return;
    }
    
    const modalContent = `
        <div style="padding: 20px; max-height: 70vh; overflow-y: auto;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">✏️ Update Highlighted Comments</h3>
            
            ${sectionHighlights.map(highlight => `
                <div style="background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid ${highlight.color};">
                    <div style="font-weight: 600; margin-bottom: 10px;">
                        📝 "${highlight.text.substring(0, 50)}${highlight.text.length > 50 ? '...' : ''}"
                    </div>
                    ${highlight.comments.map(comment => `
                        <div style="background: #f8f9ff; padding: 10px; margin: 5px 0; border-radius: 5px; cursor: pointer;" 
                             onclick="editHighlightComment('${highlight.id}', '${comment.id}')">
                            <div style="font-size: 0.9em; color: #666; margin-bottom: 5px;">
                                <strong>${comment.type.toUpperCase()}</strong> - ${new Date(comment.timestamp).toLocaleString()}
                            </div>
                            <div>${comment.text}</div>
                        </div>
                    `).join('')}
                </div>
            `).join('')}
            
            <div style="text-align: center; margin-top: 20px;">
                <button class="btn btn-secondary" onclick="closeModal('genericModal')">❌ Close</button>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Update Comments', modalContent);
}

/**
 * Edit highlight comment
 */
function editHighlightComment(highlightId, commentId) {
    const highlight = highlightComments.find(h => h.id === highlightId);
    const comment = highlight?.comments.find(c => c.id === commentId);
    
    if (!highlight || !comment) return;
    
    const modalContent = `
        <div style="padding: 20px;">
            <h3 style="color: #4f46e5; margin-bottom: 20px;">✏️ Edit Comment</h3>
            
            <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid ${highlight.color};">
                <strong>Highlighted Text:</strong><br>
                <em>"${highlight.text.length > 100 ? highlight.text.substring(0, 100) + '...' : highlight.text}"</em>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="font-weight: 600; margin-bottom: 5px; display: block;">Comment Type:</label>
                <select id="editCommentType" style="width: 100%; padding: 8px; border: 2px solid #4f46e5; border-radius: 5px;">
                    <option value="suggestion" ${comment.type === 'suggestion' ? 'selected' : ''}>Suggestion</option>
                    <option value="important" ${comment.type === 'important' ? 'selected' : ''}>Important</option>
                    <option value="critical" ${comment.type === 'critical' ? 'selected' : ''}>Critical</option>
                    <option value="question" ${comment.type === 'question' ? 'selected' : ''}>Question</option>
                    <option value="clarification" ${comment.type === 'clarification' ? 'selected' : ''}>Clarification</option>
                </select>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="font-weight: 600; margin-bottom: 5px; display: block;">Your Comment:</label>
                <textarea id="editCommentText" style="width: 100%; height: 100px; padding: 10px; border: 2px solid #4f46e5; border-radius: 5px; resize: vertical;">${comment.text}</textarea>
            </div>
            
            <div style="text-align: center;">
                <button class="btn btn-success" onclick="updateHighlightComment('${highlightId}', '${commentId}')" style="margin: 5px;">💾 Save Changes</button>
                <button class="btn btn-danger" onclick="deleteHighlightComment('${highlightId}', '${commentId}')" style="margin: 5px;">🗑️ Delete</button>
                <button class="btn btn-secondary" onclick="showUpdateCommentsDialog()" style="margin: 5px;">← Back</button>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Edit Comment', modalContent);
}

/**
 * Update highlight comment
 */
function updateHighlightComment(highlightId, commentId) {
    const type = document.getElementById('editCommentType').value;
    const text = document.getElementById('editCommentText').value.trim();
    
    if (!text) {
        showNotification('Please enter a comment', 'error');
        return;
    }
    
    const highlight = highlightComments.find(h => h.id === highlightId);
    const comment = highlight?.comments.find(c => c.id === commentId);
    
    if (!highlight || !comment) return;
    
    comment.type = type;
    comment.text = text;
    comment.edited = true;
    comment.editedAt = new Date().toISOString();
    
    // Update in user feedback history
    const feedbackIndex = userFeedbackHistory.findIndex(item => 
        item.highlight_id === highlightId && item.description.includes(comment.id)
    );
    
    if (feedbackIndex !== -1) {
        userFeedbackHistory[feedbackIndex].type = type;
        userFeedbackHistory[feedbackIndex].description = `Highlighted text: "${highlight.text.substring(0, 50)}..." - Comment: ${text}`;
        userFeedbackHistory[feedbackIndex].edited = true;
        userFeedbackHistory[feedbackIndex].edited_at = new Date().toISOString();
    }
    
    refreshUserFeedbackList();
    showUpdateCommentsDialog();
    showNotification('Comment updated successfully!', 'success');
}

/**
 * Delete highlight comment
 */
function deleteHighlightComment(highlightId, commentId) {
    if (!confirm('Are you sure you want to delete this comment?')) return;
    
    const highlight = highlightComments.find(h => h.id === highlightId);
    if (!highlight) return;
    
    highlight.comments = highlight.comments.filter(c => c.id !== commentId);
    
    // Remove from user feedback history
    userFeedbackHistory = userFeedbackHistory.filter(item => 
        !(item.highlight_id === highlightId && item.description.includes(commentId))
    );
    
    // If no comments left, remove highlight
    if (highlight.comments.length === 0) {
        const highlightElement = document.getElementById(highlightId);
        if (highlightElement) {
            const parent = highlightElement.parentNode;
            parent.replaceChild(document.createTextNode(highlightElement.textContent), highlightElement);
            parent.normalize();
        }
        highlightComments = highlightComments.filter(h => h.id !== highlightId);
    }
    
    refreshUserFeedbackList();
    showUpdateCommentsDialog();
    showNotification('Comment deleted successfully!', 'success');
}

/**
 * Clear all highlights
 */
function clearAllHighlights() {
    if (!confirm('Are you sure you want to clear all highlights and comments?')) return;
    
    highlightComments.forEach(highlight => {
        const element = document.getElementById(highlight.id);
        if (element) {
            const parent = element.parentNode;
            parent.replaceChild(document.createTextNode(element.textContent), element);
            parent.normalize();
        }
    });
    
    // Remove from user feedback history
    userFeedbackHistory = userFeedbackHistory.filter(item => !item.highlight_id);
    
    highlightComments = [];
    refreshUserFeedbackList();
    showNotification('All highlights cleared!', 'success');
}

/**
 * Initialize text highlighting
 */
function initializeTextHighlighting() {
    const docContent = document.getElementById('documentContent');
    if (!docContent) return;
    
    docContent.addEventListener('mouseup', handleTextHighlight);
    
    // Add click handler for existing highlights
    docContent.addEventListener('click', function(e) {
        if (e.target.classList.contains('text-highlight')) {
            const highlightId = e.target.id;
            const highlight = highlightComments.find(h => h.id === highlightId);
            if (highlight && highlight.comments.length > 0) {
                showUpdateCommentsDialog();
            }
        }
    });
}