// Progress and Loading Functions for AI-Prism

function showDocumentProgress() {
    const progressPanel = document.getElementById('documentProgress');
    if (progressPanel) {
        progressPanel.style.display = 'block';
        
        // Rotate through loading GIFs
        rotateLoadingMedia();
    }
}

function hideDocumentProgress() {
    const progressPanel = document.getElementById('documentProgress');
    if (progressPanel) {
        progressPanel.style.display = 'none';
    }
    
    // Stop media rotation
    if (mediaRotationInterval) {
        clearInterval(mediaRotationInterval);
        mediaRotationInterval = null;
        isMediaRotating = false;
    }
}

function updateDocumentProgress(sectionName, current, total, percent) {
    const progressTitle = document.getElementById('progressTitle');
    const progressDesc = document.getElementById('progressDesc');
    
    if (progressTitle) {
        const messages = [
            `🔍 AI-Prism is investigating "${sectionName}"...`,
            `📚 Deep analysis of "${sectionName}" in progress...`,
            `🎯 Applying Hawkeye framework to "${sectionName}"...`,
            `🧠 AI-Prism is thinking about "${sectionName}"...`,
            `⚡ Processing "${sectionName}" with advanced AI...`
        ];
        progressTitle.textContent = messages[Math.floor(Math.random() * messages.length)];
    }
    
    if (progressDesc) {
        const subMessages = [
            `Section ${current} of ${total} - ${Math.round(percent)}% complete`,
            `Applying 20-point Hawkeye investigation checklist`,
            `Cross-referencing with quality standards and best practices`,
            `Analyzing for compliance gaps and improvement opportunities`,
            `Almost there! Quality analysis in progress...`
        ];
        progressDesc.textContent = subMessages[Math.floor(Math.random() * subMessages.length)];
    }
}

function updateDocumentProgressMessage(title, description) {
    const progressTitle = document.getElementById('progressTitle');
    const progressDesc = document.getElementById('progressDesc');
    
    if (progressTitle) progressTitle.textContent = title;
    if (progressDesc) progressDesc.textContent = description;
}

function rotateLoadingMedia() {
    if (isMediaRotating) return;
    
    isMediaRotating = true;
    currentMediaIndex = 0;
    usedMediaIndices = [];
    
    // Show first media immediately
    showNextLoadingMedia();
    
    // Set up rotation interval
    mediaRotationInterval = setInterval(() => {
        showNextLoadingMedia();
    }, 4000); // Change every 4 seconds
}

function showNextLoadingMedia() {
    if (loadingMediaWithContent.length === 0) return;
    
    // Reset if we've used all media
    if (usedMediaIndices.length >= loadingMediaWithContent.length) {
        usedMediaIndices = [];
    }
    
    // Find next unused media
    let nextIndex;
    do {
        nextIndex = Math.floor(Math.random() * loadingMediaWithContent.length);
    } while (usedMediaIndices.includes(nextIndex) && usedMediaIndices.length < loadingMediaWithContent.length);
    
    usedMediaIndices.push(nextIndex);
    const media = loadingMediaWithContent[nextIndex];
    
    // Update the progress GIF and content
    const progressGif = document.getElementById('progressGif');
    if (progressGif && media.gif) {
        progressGif.src = media.gif;
        progressGif.alt = 'AI-Prism is working...';
    }
    
    // Optionally show joke or math fact in description
    const progressDesc = document.getElementById('progressDesc');
    if (progressDesc && Math.random() > 0.5) {
        if (Math.random() > 0.5 && media.joke) {
            progressDesc.textContent = `😄 ${media.joke}`;
        } else if (media.math) {
            progressDesc.textContent = `🧮 ${media.math}`;
        }
    }
}

// Enhanced chat functions
function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    input.value = '';
    
    // Add enhanced thinking message
    addChatMessage('🤖 AI-Prism is analyzing your question and consulting the Hawkeye framework...', 'assistant', true);
    
    // Send to backend
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: currentSession,
            message: message,
            current_section: sections[currentSectionIndex],
            ai_model: currentAIModel
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove thinking message
        const thinkingMessages = document.querySelectorAll('.chat-message.thinking');
        thinkingMessages.forEach(msg => msg.remove());
        
        if (data.success) {
            let responseMessage = data.response;
            if (data.model_used && data.model_used !== currentAIModel) {
                responseMessage += `\n\n*[Response generated using ${data.model_used}]*`;
            }
            addChatMessage(responseMessage, 'assistant');
            
            // Show success notification
            showNotification('💬 AI-Prism responded successfully!', 'success');
        } else {
            addChatMessage('❌ Sorry, I encountered an error processing your request. Please try again or rephrase your question.', 'assistant');
            showNotification('Chat error: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        // Remove thinking message
        const thinkingMessages = document.querySelectorAll('.chat-message.thinking');
        thinkingMessages.forEach(msg => msg.remove());
        
        addChatMessage('❌ Sorry, I encountered a connection error. Please check your internet connection and try again.', 'assistant');
        showNotification('Connection error: ' + error.message, 'error');
        console.error('Chat error:', error);
    });
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendChatMessage();
    }
}

// Enhanced section loading with progress
function loadSectionWithProgress(index) {
    if (index < 0 || index >= sections.length) return;
    
    // Save current section highlights before switching
    saveCurrentSectionHighlights();
    
    currentSectionIndex = index;
    const sectionName = sections[index];
    
    // Update section select
    const sectionSelect = document.getElementById('sectionSelect');
    if (sectionSelect) sectionSelect.value = index;
    
    // Clear user feedback display
    const userFeedbackDisplay = document.getElementById('userFeedbackDisplay');
    if (userFeedbackDisplay) userFeedbackDisplay.innerHTML = '';
    
    // Load from stored data
    if (window.sectionData && window.sectionData[sectionName]) {
        const data = window.sectionData[sectionName];
        displaySectionContent(data.content, sectionName);
        displayFeedback(data.feedback, sectionName);
        updateRiskIndicator(data.feedback);
        
        // Load any existing user feedback for this section
        loadUserFeedbackForSection(sectionName);
        
        // Restore highlights for this section
        setTimeout(() => {
            restoreSectionHighlights(sectionName);
            // Update custom feedback button states
            if (typeof updateAICustomButtonStates === 'function') {
                updateAICustomButtonStates();
            }
        }, 200);
    } else {
        // Fallback to API call if data not stored - show enhanced loading
        showProgress('🔍 Loading section analysis...');
        showDocumentProgress();
        updateDocumentProgressMessage(`🤖 Loading "${sectionName}" analysis...`, 
                                    '⏳ Retrieving AI-generated feedback...');
        
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
            if (data.success) {
                displaySectionContent(data.section_content, sectionName);
                displayFeedback(data.feedback_items, sectionName);
                updateRiskIndicator(data.feedback_items);
                loadUserFeedbackForSection(sectionName);
                
                // Show success message
                const feedbackCount = data.feedback_items ? data.feedback_items.length : 0;
                updateDocumentProgressMessage(`✅ "${sectionName}" loaded successfully!`, 
                                            `📊 ${feedbackCount} feedback items ready for review`);
                
                // Restore highlights for this section
                setTimeout(() => {
                    restoreSectionHighlights(sectionName);
                    // Update custom feedback button states
                    if (typeof updateAICustomButtonStates === 'function') {
                        updateAICustomButtonStates();
                    }
                }, 200);
            } else {
                updateDocumentProgressMessage(`❌ Failed to load "${sectionName}"`, 
                                            '🔄 Please try again or contact support');
            }
            
            setTimeout(() => {
                hideProgress();
                hideDocumentProgress();
            }, 2000);
        })
        .catch(error => {
            console.error('Section load error:', error);
            updateDocumentProgressMessage(`❌ Error loading "${sectionName}"`, 
                                        `🔄 ${error.message}`);
            setTimeout(() => {
                hideProgress();
                hideDocumentProgress();
                showNotification('Failed to load section: ' + error.message, 'error');
            }, 2000);
        });
    }
}

// Override the original loadSection function
function loadSection(index) {
    loadSectionWithProgress(index);
}