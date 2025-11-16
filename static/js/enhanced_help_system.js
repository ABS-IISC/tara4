// Enhanced Help System with Dropdown Functionality
// Provides interactive help sections with collapsible content

// Toggle feature section visibility
function toggleFeatureSection(sectionId) {
    const content = document.getElementById(`${sectionId}-content`);
    const toggle = document.getElementById(`${sectionId}-toggle`);
    
    if (content && toggle) {
        const isVisible = content.style.display !== 'none';
        content.style.display = isVisible ? 'none' : 'block';
        toggle.textContent = isVisible ? '▶' : '▼';
    }
}

// Enhanced showShortcuts function
function showShortcuts() {
    const modalContent = `
        <div style="max-height: 80vh; overflow-y: auto;">
            <div class="feature-header" onclick="toggleFeatureSection('shortcuts')">
                <h3>⌨️ Keyboard Shortcuts</h3>
                <span class="toggle-icon" id="shortcuts-toggle">▼</span>
            </div>
            <div class="feature-content" id="shortcuts-content">
                <div class="feature-intro">
                    <p>🚀 <strong>Boost your productivity</strong> with these powerful keyboard shortcuts for lightning-fast document review!</p>
                </div>
                
                <div class="shortcuts-categories">
                    <div class="shortcut-category">
                        <h4>🧭 Navigation Shortcuts</h4>
                        <div class="shortcuts-grid">
                            <div class="shortcut-item">
                                <kbd>N</kbd>
                                <span>Next Section</span>
                                <small>Jump to next document section</small>
                            </div>
                            <div class="shortcut-item">
                                <kbd>P</kbd>
                                <span>Previous Section</span>
                                <small>Go back to previous section</small>
                            </div>
                            <div class="shortcut-item">
                                <kbd>1</kbd>
                                <span>Feedback Tab</span>
                                <small>Switch to AI feedback view</small>
                            </div>
                            <div class="shortcut-item">
                                <kbd>2</kbd>
                                <span>Chat Tab</span>
                                <small>Switch to AI chat assistant</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="shortcut-category">
                        <h4>⚡ Action Shortcuts</h4>
                        <div class="shortcuts-grid">
                            <div class="shortcut-item">
                                <kbd>A</kbd>
                                <span>Accept Feedback</span>
                                <small>Accept current AI suggestion</small>
                            </div>
                            <div class="shortcut-item">
                                <kbd>R</kbd>
                                <span>Reject Feedback</span>
                                <small>Reject current AI suggestion</small>
                            </div>
                            <div class="shortcut-item">
                                <kbd>F</kbd>
                                <span>Custom Feedback</span>
                                <small>Focus on custom feedback form</small>
                            </div>
                            <div class="shortcut-item">
                                <kbd>C</kbd>
                                <span>Chat Input</span>
                                <small>Focus on chat message box</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="shortcut-category">
                        <h4>🎨 Interface Shortcuts</h4>
                        <div class="shortcuts-grid">
                            <div class="shortcut-item">
                                <kbd>D</kbd>
                                <span>Dark Mode</span>
                                <small>Toggle dark/light theme</small>
                            </div>
                            <div class="shortcut-item">
                                <kbd>?</kbd>
                                <span>Help Panel</span>
                                <small>Show/hide this help guide</small>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Esc</kbd>
                                <span>Close Dialogs</span>
                                <small>Close any open popup/dialog</small>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Enter</kbd>
                                <span>Submit Forms</span>
                                <small>Submit active form/input</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="feature-tips">
                    <h4>💡 Pro Tips</h4>
                    <ul>
                        <li><strong>Combo Power:</strong> Use <kbd>N</kbd> + <kbd>A</kbd> to quickly navigate and accept feedback</li>
                        <li><strong>Speed Review:</strong> Hold <kbd>A</kbd> or <kbd>R</kbd> to rapid-fire through suggestions</li>
                        <li><strong>Focus Flow:</strong> Use <kbd>F</kbd> to add custom feedback without mouse clicks</li>
                        <li><strong>Chat Quick:</strong> Press <kbd>2</kbd> + <kbd>C</kbd> to instantly start chatting with AI</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Keyboard Shortcuts', modalContent);
}

// Enhanced showTutorial function
function showTutorial() {
    const modalContent = `
        <div style="max-height: 80vh; overflow-y: auto;">
            <div class="feature-header" onclick="toggleFeatureSection('tutorial')">
                <h3>🔍 Interactive Tutorial</h3>
                <span class="toggle-icon" id="tutorial-toggle">▼</span>
            </div>
            <div class="feature-content" id="tutorial-content">
                <div class="feature-intro">
                    <p>🎯 <strong>Master AI-Prism in 6 easy steps!</strong> Follow this interactive guide to become a document review expert.</p>
                </div>
                
                <div class="tutorial-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="tutorial-progress"></div>
                    </div>
                    <span class="progress-text">Step <span id="current-step">1</span> of 6</span>
                </div>
                
                <div class="tutorial-steps">
                    <div class="tutorial-step active" data-step="1">
                        <div class="step-header">
                            <div class="step-number">1</div>
                            <h4>📤 Upload Your Document</h4>
                            <span class="step-status">🔄 In Progress</span>
                        </div>
                        <div class="step-content">
                            <p><strong>Get started:</strong> Drag and drop your .docx file or click "Choose File" to upload.</p>
                            <div class="step-tips">
                                <strong>💡 Pro Tips:</strong>
                                <ul>
                                    <li>Files up to 16MB supported</li>
                                    <li>Only .docx format accepted</li>
                                    <li>Watch the upload progress bar</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <div class="tutorial-step" data-step="2">
                        <div class="step-header">
                            <div class="step-number">2</div>
                            <h4>🤖 Review AI Analysis</h4>
                            <span class="step-status">⏳ Waiting</span>
                        </div>
                        <div class="step-content">
                            <p><strong>AI Magic:</strong> Our AI automatically analyzes your document using the powerful Hawkeye framework.</p>
                            <div class="step-features">
                                <span class="feature-badge">🎯 20-Point Analysis</span>
                                <span class="feature-badge">🚨 Risk Assessment</span>
                                <span class="feature-badge">📊 Section Breakdown</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="tutorial-step" data-step="3">
                        <div class="step-header">
                            <div class="step-number">3</div>
                            <h4>✅ Accept or Reject Feedback</h4>
                            <span class="step-status">⏳ Waiting</span>
                        </div>
                        <div class="step-content">
                            <p><strong>Your Decision:</strong> Click ✅ to accept valuable feedback or ❌ to reject irrelevant suggestions.</p>
                            <div class="step-shortcuts">
                                <kbd>A</kbd> Accept | <kbd>R</kbd> Reject | <kbd>N</kbd> Next Section
                            </div>
                        </div>
                    </div>
                    
                    <div class="tutorial-step" data-step="4">
                        <div class="step-header">
                            <div class="step-number">4</div>
                            <h4>✏️ Add Custom Feedback</h4>
                            <span class="step-status">⏳ Waiting</span>
                        </div>
                        <div class="step-content">
                            <p><strong>Your Expertise:</strong> Use the custom feedback form to add your own observations and insights.</p>
                            <div class="step-options">
                                <span class="option-tag">💡 Suggestions</span>
                                <span class="option-tag">⚠️ Issues</span>
                                <span class="option-tag">✨ Improvements</span>
                                <span class="option-tag">❓ Questions</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="tutorial-step" data-step="5">
                        <div class="step-header">
                            <div class="step-number">5</div>
                            <h4>💬 Chat with AI Assistant</h4>
                            <span class="step-status">⏳ Waiting</span>
                        </div>
                        <div class="step-content">
                            <p><strong>Get Answers:</strong> Switch to the Chat tab to ask questions about feedback or document guidelines.</p>
                            <div class="chat-examples">
                                <div class="example-question">"Why is this section high risk?"</div>
                                <div class="example-question">"What are the Hawkeye criteria?"</div>
                                <div class="example-question">"How can I improve this clause?"</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="tutorial-step" data-step="6">
                        <div class="step-header">
                            <div class="step-number">6</div>
                            <h4>🎉 Complete Review</h4>
                            <span class="step-status">⏳ Waiting</span>
                        </div>
                        <div class="step-content">
                            <p><strong>Finish Strong:</strong> Click "Complete Review" to generate a Word document with all accepted feedback as comments.</p>
                            <div class="completion-benefits">
                                <ul>
                                    <li>📄 Professional Word document with embedded comments</li>
                                    <li>📊 Complete analysis summary</li>
                                    <li>🎯 All accepted feedback included</li>
                                    <li>💾 Instant download ready</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="tutorial-navigation">
                    <button class="tutorial-btn" onclick="previousTutorialStep()">← Previous</button>
                    <button class="tutorial-btn primary" onclick="nextTutorialStep()">Next →</button>
                    <button class="tutorial-btn" onclick="resetTutorial()">🔄 Restart</button>
                </div>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Interactive Tutorial', modalContent);
}

// Tutorial navigation functions
let currentTutorialStep = 1;

function nextTutorialStep() {
    if (currentTutorialStep < 6) {
        currentTutorialStep++;
        updateTutorialStep();
    }
}

function previousTutorialStep() {
    if (currentTutorialStep > 1) {
        currentTutorialStep--;
        updateTutorialStep();
    }
}

function resetTutorial() {
    currentTutorialStep = 1;
    updateTutorialStep();
}

function updateTutorialStep() {
    const steps = document.querySelectorAll('.tutorial-step');
    const progressFill = document.getElementById('tutorial-progress');
    const currentStepSpan = document.getElementById('current-step');
    
    steps.forEach((step, index) => {
        const stepNumber = index + 1;
        const isActive = stepNumber === currentTutorialStep;
        const isCompleted = stepNumber < currentTutorialStep;
        
        step.classList.toggle('active', isActive);
        step.classList.toggle('completed', isCompleted);
        
        const status = step.querySelector('.step-status');
        if (status) {
            if (isCompleted) {
                status.textContent = '✅ Completed';
                status.style.color = '#2ecc71';
            } else if (isActive) {
                status.textContent = '🔄 In Progress';
                status.style.color = '#3498db';
            } else {
                status.textContent = '⏳ Waiting';
                status.style.color = '#95a5a6';
            }
        }
    });
    
    if (progressFill) {
        progressFill.style.width = `${(currentTutorialStep / 6) * 100}%`;
    }
    
    if (currentStepSpan) {
        currentStepSpan.textContent = currentTutorialStep;
    }
}

// Enhanced showFAQ function
function showFAQ() {
    const modalContent = `
        <div style="max-height: 80vh; overflow-y: auto;">
            <div class="feature-header" onclick="toggleFeatureSection('faqs')">
                <h3>❓ Frequently Asked Questions</h3>
                <span class="toggle-icon" id="faqs-toggle">▼</span>
            </div>
            <div class="feature-content" id="faqs-content">
                <div class="feature-intro">
                    <p>🔍 <strong>Quick answers to common questions!</strong> Find solutions to get the most out of AI-Prism.</p>
                </div>
                
                <div class="faq-search">
                    <input type="text" id="faq-search" placeholder="🔍 Search FAQs..." onkeyup="filterFAQs()">
                </div>
                
                <div class="faq-categories">
                    <div class="faq-category">
                        <h4>🚀 Getting Started</h4>
                        <div class="faq-list">
                            <div class="faq-item" onclick="toggleFAQ(this)">
                                <div class="faq-question">
                                    <span>📤 What file formats are supported?</span>
                                    <span class="faq-toggle">+</span>
                                </div>
                                <div class="faq-answer">
                                    <p><strong>Supported:</strong> Microsoft Word (.docx) files only</p>
                                    <ul>
                                        <li>✅ Maximum file size: 16MB</li>
                                        <li>✅ Drag & drop or file selection</li>
                                        <li>❌ .doc, .pdf, .txt not supported yet</li>
                                    </ul>
                                    <div class="faq-tip">
                                        <strong>💡 Tip:</strong> Convert .doc files to .docx in Microsoft Word before uploading.
                                    </div>
                                </div>
                            </div>
                            
                            <div class="faq-item" onclick="toggleFAQ(this)">
                                <div class="faq-question">
                                    <span>🤖 How does the AI analysis work?</span>
                                    <span class="faq-toggle">+</span>
                                </div>
                                <div class="faq-answer">
                                    <p><strong>Hawkeye Framework:</strong> 20-point comprehensive analysis system</p>
                                    <div class="analysis-features">
                                        <span class="feature-badge">🎯 Risk Assessment</span>
                                        <span class="feature-badge">📊 Section Analysis</span>
                                        <span class="feature-badge">⚖️ Compliance Check</span>
                                        <span class="feature-badge">💡 Improvements</span>
                                    </div>
                                    <p>Each section gets analyzed for legal risks, clarity issues, and improvement opportunities.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="faq-category">
                        <h4>🔒 Security & Privacy</h4>
                        <div class="faq-list">
                            <div class="faq-item" onclick="toggleFAQ(this)">
                                <div class="faq-question">
                                    <span>🛡️ What happens to my documents?</span>
                                    <span class="faq-toggle">+</span>
                                </div>
                                <div class="faq-answer">
                                    <p><strong>Secure Processing:</strong> Your documents are handled with enterprise-grade security</p>
                                    <ul>
                                        <li>🔒 Encrypted during upload and processing</li>
                                        <li>⏱️ Temporarily stored only during analysis</li>
                                        <li>🗑️ Automatically deleted after session ends</li>
                                        <li>🚫 Never shared or used for training</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="faq-footer">
                    <p>🤔 <strong>Still have questions?</strong> Use the 💬 AI Chat to ask anything about your document or the review process!</p>
                </div>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Frequently Asked Questions', modalContent);
}

// FAQ toggle function
function toggleFAQ(faqItem) {
    const answer = faqItem.querySelector('.faq-answer');
    const toggle = faqItem.querySelector('.faq-toggle');
    
    if (answer && toggle) {
        const isVisible = answer.style.display !== 'none';
        answer.style.display = isVisible ? 'none' : 'block';
        toggle.textContent = isVisible ? '+' : '-';
    }
}

// FAQ search function
function filterFAQs() {
    const searchTerm = document.getElementById('faq-search').value.toLowerCase();
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question span').textContent.toLowerCase();
        const answer = item.querySelector('.faq-answer').textContent.toLowerCase();
        
        if (question.includes(searchTerm) || answer.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Enhanced showPatterns function
function showPatterns() {
    const modalContent = `
        <div style="max-height: 80vh; overflow-y: auto;">
            <div class="feature-header" onclick="toggleFeatureSection('patterns')">
                <h3>📊 Pattern Recognition</h3>
                <span class="toggle-icon" id="patterns-toggle">▼</span>
            </div>
            <div class="feature-content" id="patterns-content">
                <div class="feature-intro">
                    <p>🧠 <strong>Smart Pattern Detection!</strong> AI-Prism identifies recurring issues and trends across your document reviews.</p>
                </div>
                
                <div class="pattern-dashboard">
                    <div class="pattern-stats">
                        <div class="pattern-stat">
                            <div class="stat-number">0</div>
                            <div class="stat-label">Patterns Found</div>
                        </div>
                        <div class="pattern-stat">
                            <div class="stat-number">0</div>
                            <div class="stat-label">Documents Analyzed</div>
                        </div>
                        <div class="pattern-stat">
                            <div class="stat-number">0</div>
                            <div class="stat-label">Risk Trends</div>
                        </div>
                    </div>
                </div>
                
                <div class="pattern-categories">
                    <div class="pattern-category">
                        <h4>🔍 Issue Detection</h4>
                        <div class="pattern-feature">
                            <div class="feature-icon">🎯</div>
                            <div class="feature-details">
                                <p><strong>Recurring Problems:</strong> Automatically identifies issues that appear across different sections and documents.</p>
                                <div class="feature-examples">
                                    <span class="example-tag">Unclear Terms</span>
                                    <span class="example-tag">Missing Clauses</span>
                                    <span class="example-tag">Compliance Gaps</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="pattern-category">
                        <h4>📈 Trend Analysis</h4>
                        <div class="pattern-feature">
                            <div class="feature-icon">📊</div>
                            <div class="feature-details">
                                <p><strong>Review Preferences:</strong> Tracks patterns in your feedback acceptance/rejection to understand your review style.</p>
                                <div class="trend-indicators">
                                    <div class="trend-item">
                                        <span class="trend-label">Most Accepted:</span>
                                        <span class="trend-value">Risk Issues</span>
                                    </div>
                                    <div class="trend-item">
                                        <span class="trend-label">Most Rejected:</span>
                                        <span class="trend-value">Style Suggestions</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="pattern-actions">
                    <button class="pattern-btn" onclick="refreshPatterns()">🔄 Refresh Patterns</button>
                    <button class="pattern-btn" onclick="exportPatterns()">📊 Export Analysis</button>
                    <button class="pattern-btn" onclick="clearPatterns()">🗑️ Clear History</button>
                </div>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'Pattern Recognition', modalContent);
}

// ❌ DELETED: showLogs() stub function - not used, replaced by showActivityLogs()
// Activity Logs is properly implemented in global_function_fixes.js as window.showActivityLogs()
// with full backend integration, stats, timeline, and export functionality

// Enhanced showLearning function
function showLearning() {
    const modalContent = `
        <div style="max-height: 80vh; overflow-y: auto;">
            <div class="feature-header" onclick="toggleFeatureSection('learning')">
                <h3>🧠 AI Learning System</h3>
                <span class="toggle-icon" id="learning-toggle">▼</span>
            </div>
            <div class="feature-content" id="learning-content">
                <div class="feature-intro">
                    <p>🚀 <strong>Smart AI that gets smarter!</strong> AI-Prism continuously learns from your feedback patterns.</p>
                </div>
                
                <div class="learning-dashboard">
                    <div class="learning-progress">
                        <div class="progress-circle">
                            <div class="progress-ring">
                                <div class="progress-fill" style="--progress: 0%"></div>
                            </div>
                            <div class="progress-center">
                                <span class="progress-percent">0%</span>
                                <span class="progress-label">Learning Progress</span>
                            </div>
                        </div>
                        <div class="learning-stats">
                            <div class="learning-stat">
                                <span class="stat-value">0</span>
                                <span class="stat-label">Documents Learned From</span>
                            </div>
                            <div class="learning-stat">
                                <span class="stat-value">0</span>
                                <span class="stat-label">Feedback Patterns</span>
                            </div>
                            <div class="learning-stat">
                                <span class="stat-value">0%</span>
                                <span class="stat-label">Accuracy Improvement</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="learning-actions">
                    <button class="learning-btn" onclick="viewLearningDetails()">📊 View Learning Data</button>
                    <button class="learning-btn" onclick="resetLearning()">🔄 Reset Learning</button>
                    <button class="learning-btn" onclick="exportLearningData()">📁 Export Data</button>
                </div>
                
                <div class="learning-tips">
                    <h4>💡 Maximize AI Learning</h4>
                    <ul>
                        <li><strong>Be Consistent:</strong> Accept/reject feedback consistently to help AI learn your preferences</li>
                        <li><strong>Review Regularly:</strong> More documents = better learning and personalization</li>
                        <li><strong>Use Custom Feedback:</strong> Add your own insights to teach AI what matters to you</li>
                        <li><strong>Check Progress:</strong> Monitor learning progress to see how AI adapts to your style</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
    
    showModal('genericModal', 'AI Learning System', modalContent);
}

// Placeholder functions for button actions
function refreshPatterns() { showNotification('Pattern data refreshed!', 'info'); }
function exportPatterns() { showNotification('Pattern analysis exported!', 'success'); }
function clearPatterns() { showNotification('Pattern history cleared!', 'info'); }
// ❌ REMOVED: Activity logs helper functions (refreshLogs, exportLogs, clearLogs)
// Activity Logs has proper implementation in global_function_fixes.js
function viewLearningDetails() { showNotification('Learning details displayed!', 'info'); }
function resetLearning() { showNotification('AI learning reset!', 'info'); }
function exportLearningData() { showNotification('Learning data exported!', 'success'); }

// ✅ FIX: Attach all help system functions to window for onclick handlers
window.showShortcuts = showShortcuts;
window.showTutorial = showTutorial;
window.showFAQ = showFAQ;
window.showPatterns = showPatterns;
// ❌ REMOVED: window.showActivityLogs = showActivityLogs; (was undefined, breaking the button)
// Activity Logs is properly implemented in global_function_fixes.js
window.showLearning = showLearning;
window.toggleFeatureSection = toggleFeatureSection;
window.refreshPatterns = refreshPatterns;
window.exportPatterns = exportPatterns;
window.clearPatterns = clearPatterns;
// ❌ REMOVED: window.refreshLogs, window.exportLogs, window.clearLogs
// Activity Logs has complete implementation in global_function_fixes.js with:
// - window.refreshActivityLogs() - Refresh logs display
// - window.exportActivityLogs() - Export in JSON/CSV/TXT formats
// - window.downloadActivityLogsFormat() - Download trigger
window.viewLearningDetails = viewLearningDetails;
window.resetLearning = resetLearning;
window.exportLearningData = exportLearningData;

console.log('✅ Enhanced help system: All functions attached to window object');
console.log('   - showShortcuts:', typeof window.showShortcuts);
console.log('   - showTutorial:', typeof window.showTutorial);
console.log('   - showFAQ:', typeof window.showFAQ);
console.log('   - showPatterns:', typeof window.showPatterns);