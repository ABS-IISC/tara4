// Custom Feedback Help and Tutorial Functions

/**
 * Show help for custom feedback on AI suggestions
 */
function showCustomFeedbackHelp() {
    const modalContent = `
        <div style="max-height: 80vh; overflow-y: auto; padding: 20px;">
            <h3 style="color: #4f46e5; margin-bottom: 25px; text-align: center;">✨ Custom Feedback on AI Suggestions</h3>
            
            <div style="background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); padding: 25px; border-radius: 15px; margin-bottom: 25px; border: 3px solid #4f46e5;">
                <h4 style="color: #4f46e5; margin-bottom: 20px;">🎯 What's New?</h4>
                <p style="margin-bottom: 15px; line-height: 1.6;">
                    You can now add your own custom feedback directly to each AI suggestion! This allows you to:
                </p>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Enhance AI suggestions</strong> with your expertise</li>
                    <li><strong>Add missing context</strong> that AI might have overlooked</li>
                    <li><strong>Provide alternative approaches</strong> to the AI's recommendations</li>
                    <li><strong>Clarify or disagree</strong> with specific AI points</li>
                    <li><strong>Build a comprehensive review</strong> combining AI and human insights</li>
                </ul>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 12px; border-left: 5px solid #10b981; margin-bottom: 20px;">
                <h4 style="color: #10b981; margin-bottom: 15px;">📝 How to Use:</h4>
                <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
                    <div style="display: flex; align-items: center; padding: 10px; background: #f0fff4; border-radius: 8px;">
                        <span style="font-size: 1.5em; margin-right: 12px;">1️⃣</span>
                        <div><strong>Find an AI suggestion</strong> you want to add feedback to</div>
                    </div>
                    <div style="display: flex; align-items: center; padding: 10px; background: #f0fff4; border-radius: 8px;">
                        <span style="font-size: 1.5em; margin-right: 12px;">2️⃣</span>
                        <div><strong>Click "✨ Add Custom"</strong> button on that AI feedback item</div>
                    </div>
                    <div style="display: flex; align-items: center; padding: 10px; background: #f0fff4; border-radius: 8px;">
                        <span style="font-size: 1.5em; margin-right: 12px;">3️⃣</span>
                        <div><strong>Choose feedback type</strong> (Addition, Clarification, etc.)</div>
                    </div>
                    <div style="display: flex; align-items: center; padding: 10px; background: #f0fff4; border-radius: 8px;">
                        <span style="font-size: 1.5em; margin-right: 12px;">4️⃣</span>
                        <div><strong>Write your feedback</strong> in the text area</div>
                    </div>
                    <div style="display: flex; align-items: center; padding: 10px; background: #f0fff4; border-radius: 8px;">
                        <span style="font-size: 1.5em; margin-right: 12px;">5️⃣</span>
                        <div><strong>Click "Save My Feedback"</strong> to add it to the review</div>
                    </div>
                </div>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 12px; border-left: 5px solid #f59e0b; margin-bottom: 20px;">
                <h4 style="color: #f59e0b; margin-bottom: 15px;">🔧 Button Functions:</h4>
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="padding: 8px; background: #fffbf0; border-radius: 6px;">
                        <strong>✨ Add Custom:</strong> Opens form to add your feedback to this AI suggestion
                    </div>
                    <div style="padding: 8px; background: #fffbf0; border-radius: 6px;">
                        <strong>✨ Custom (2):</strong> Shows you already have 2 custom feedback items for this AI suggestion
                    </div>
                    <div style="padding: 8px; background: #fffbf0; border-radius: 6px;">
                        <strong>🧹 Clear:</strong> Removes all your custom feedback for this specific AI suggestion
                    </div>
                    <div style="padding: 8px; background: #fffbf0; border-radius: 6px;">
                        <strong>🧹 Clear Section Feedback:</strong> Removes all custom feedback from current section
                    </div>
                </div>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 12px; border-left: 5px solid #ec4899; margin-bottom: 20px;">
                <h4 style="color: #ec4899; margin-bottom: 15px;">💡 Feedback Types:</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div style="padding: 10px; background: #fdf2f8; border-radius: 6px; text-align: center;">
                        <strong>Addition</strong><br>
                        <small>Add more information</small>
                    </div>
                    <div style="padding: 10px; background: #fdf2f8; border-radius: 6px; text-align: center;">
                        <strong>Clarification</strong><br>
                        <small>Explain better</small>
                    </div>
                    <div style="padding: 10px; background: #fdf2f8; border-radius: 6px; text-align: center;">
                        <strong>Disagreement</strong><br>
                        <small>I disagree with AI</small>
                    </div>
                    <div style="padding: 10px; background: #fdf2f8; border-radius: 6px; text-align: center;">
                        <strong>Enhancement</strong><br>
                        <small>Improve this suggestion</small>
                    </div>
                    <div style="padding: 10px; background: #fdf2f8; border-radius: 6px; text-align: center;">
                        <strong>Alternative</strong><br>
                        <small>Different approach</small>
                    </div>
                    <div style="padding: 10px; background: #fdf2f8; border-radius: 6px; text-align: center;">
                        <strong>Context</strong><br>
                        <small>Missing context</small>
                    </div>
                </div>
            </div>
            
            <div style="background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%); padding: 20px; border-radius: 12px; border: 2px solid #28a745; text-align: center;">
                <h4 style="color: #28a745; margin-bottom: 15px;">🎉 Benefits</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                    <div>
                        <div style="font-size: 2em; margin-bottom: 5px;">🤝</div>
                        <strong>AI + Human</strong><br>
                        <small>Best of both worlds</small>
                    </div>
                    <div>
                        <div style="font-size: 2em; margin-bottom: 5px;">📋</div>
                        <strong>Complete Review</strong><br>
                        <small>Nothing missed</small>
                    </div>
                    <div>
                        <div style="font-size: 2em; margin-bottom: 5px;">🎯</div>
                        <strong>Targeted Feedback</strong><br>
                        <small>Specific to each point</small>
                    </div>
                    <div>
                        <div style="font-size: 2em; margin-bottom: 5px;">📄</div>
                        <strong>Export Ready</strong><br>
                        <small>Included in final document</small>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 25px;">
                <button class="btn btn-primary" onclick="closeModal('genericModal')" style="padding: 12px 25px; border-radius: 20px; font-weight: 600;">
                    ✨ Start Adding Custom Feedback
                </button>
            </div>
        </div>
    `;
    
    if (typeof showModal === 'function') {
        showModal('genericModal', 'Custom Feedback Help', modalContent);
    } else {
        alert('Custom Feedback Help: You can now add custom feedback to each AI suggestion using the "Add Custom" button!');
    }
}

/**
 * Show quick tips for custom feedback
 */
function showCustomFeedbackTips() {
    const tips = [
        "💡 Tip: Use 'Addition' type to add information AI missed",
        "💡 Tip: Use 'Clarification' to explain complex points better", 
        "💡 Tip: Use 'Alternative' to suggest different approaches",
        "💡 Tip: Your custom feedback appears in the final document",
        "💡 Tip: Click the counter to see all your section feedback",
        "💡 Tip: Use 'Clear' button to remove specific AI feedback comments"
    ];
    
    const randomTip = tips[Math.floor(Math.random() * tips.length)];
    
    if (typeof showNotification === 'function') {
        showNotification(randomTip, 'info');
    }
}

// Auto-show tips occasionally
let tipCounter = 0;
function maybeShowTip() {
    tipCounter++;
    if (tipCounter % 10 === 0) { // Show tip every 10 actions
        setTimeout(showCustomFeedbackTips, 1000);
    }
}

// Hook into existing functions to show tips
if (typeof addCustomToAI !== 'undefined') {
    const originalAddCustomToAI = addCustomToAI;
    addCustomToAI = function() {
        maybeShowTip();
        return originalAddCustomToAI.apply(this, arguments);
    };
}