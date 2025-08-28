/**
 * Agno-enhanced chat interface for advanced financial reasoning and document processing
 */

class AgnoChatInterface {
    constructor() {
        this.chatContainer = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-message-btn');
        this.fileUploadBtn = document.getElementById('file-upload-btn');
        this.fileUploadInput = document.getElementById('file-upload-input');
        this.filePreview = document.getElementById('file-preview');
        
        this.currentSession = null;
        this.useReasoning = true;
        this.createInterface = false;
        
        this.initializeEventListeners();
        this.addAgnoWelcomeMessage();
    }

    initializeEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter key
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // File upload handling
        this.fileUploadInput.addEventListener('change', (e) => this.handleFileUpload(e));
        
        // Auto-resize textarea
        this.chatInput.addEventListener('input', () => this.autoResizeTextarea());
    }

    addAgnoWelcomeMessage() {
        const welcomeMessage = `
        🧠 **Agno AI Assistant Activated**
        
        I'm your advanced financial reasoning assistant powered by Agno framework. I can:
        
        ✨ **Advanced Reasoning**: Step-by-step analysis of complex financial scenarios
        📄 **Document Processing**: Upload and analyze financial documents with confidence scoring
        🎨 **Interface Creation**: Generate dynamic widgets and visualizations
        🔍 **Semantic Search**: Find insights across your financial data
        📊 **Ontology Management**: Suggest improvements to your data structure
        
        **Special Commands:**
        - \`/reasoning on/off\` - Toggle reasoning mode
        - \`/interface\` - Request interface creation
        - \`/demo\` - See reasoning demonstration
        - \`/upload\` - Upload documents for analysis
        
        How can I help you today?
        `;
        
        this.addMessage(welcomeMessage, 'assistant', 'agno-system');
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;

        // Check for special commands
        if (message.startsWith('/')) {
            this.handleSpecialCommand(message);
            return;
        }

        // Add user message to chat
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        this.autoResizeTextarea();

        // Show typing indicator
        const typingId = this.addTypingIndicator();

        try {
            // Send to Agno endpoint
            const response = await fetch('/api/v1/agno/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: 'demo-user',
                    context: {
                        session_id: this.currentSession,
                        timestamp: new Date().toISOString()
                    },
                    use_reasoning: this.useReasoning,
                    create_interface: this.createInterface
                })
            });

            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator(typingId);

            if (data.success) {
                this.currentSession = data.session_id;
                
                // Add response with metadata
                this.addMessage(
                    data.response, 
                    'assistant', 
                    data.agent_type,
                    {
                        reasoning_used: data.reasoning_used,
                        processing_time: data.processing_time_ms,
                        interface_code: data.interface_code
                    }
                );

                // If interface code was generated, offer to render it
                if (data.interface_code) {
                    this.offerInterfaceRendering(data.interface_code);
                }
            } else {
                this.addMessage('Sorry, I encountered an error processing your request.', 'assistant', 'error');
            }

        } catch (error) {
            this.removeTypingIndicator(typingId);
            this.addMessage('Connection error. Please try again.', 'assistant', 'error');
            console.error('Chat error:', error);
        }
    }

    handleSpecialCommand(command) {
        const cmd = command.toLowerCase();
        
        if (cmd === '/reasoning on') {
            this.useReasoning = true;
            this.addMessage('✅ Reasoning mode enabled. I will show step-by-step analysis.', 'system');
        } else if (cmd === '/reasoning off') {
            this.useReasoning = false;
            this.addMessage('⚡ Reasoning mode disabled. Responses will be faster but less detailed.', 'system');
        } else if (cmd === '/interface') {
            this.createInterface = true;
            this.addMessage('🎨 Interface creation mode enabled. Describe what you want to build.', 'system');
        } else if (cmd === '/demo') {
            this.runReasoningDemo();
        } else if (cmd === '/upload') {
            this.fileUploadInput.click();
        } else {
            this.addMessage('Unknown command. Available: /reasoning on/off, /interface, /demo, /upload', 'system');
        }
        
        this.chatInput.value = '';
    }

    async runReasoningDemo() {
        this.addMessage('🧠 Running reasoning demonstration...', 'system');
        
        try {
            const response = await fetch('/api/v1/agno/reasoning-demo');
            const data = await response.json();
            
            if (data.success) {
                this.addMessage(data.demo_response, 'assistant', 'reasoning-demo');
            } else {
                this.addMessage('Demo failed to run.', 'assistant', 'error');
            }
        } catch (error) {
            this.addMessage('Demo connection error.', 'assistant', 'error');
        }
    }

    async handleFileUpload(event) {
        const files = event.target.files;
        if (!files.length) return;

        const file = files[0];
        this.showFilePreview(file);

        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('request_data', JSON.stringify({
            user_id: 'demo-user',
            context: {
                session_id: this.currentSession,
                timestamp: new Date().toISOString()
            }
        }));

        // Create processing pipeline container
        const pipelineId = `pipeline-${Date.now()}`;
        this.createProcessingPipeline(pipelineId, file.name);

        try {
            const response = await fetch('/api/v1/agno/upload-document', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.updatePipelineComplete(pipelineId, data);
            } else {
                this.updatePipelineError(pipelineId, data.message);
            }

        } catch (error) {
            console.error('Upload error:', error);
            this.updatePipelineError(pipelineId, 'Network or processing error');
        }

        // Clear file input
        event.target.value = '';
        this.hideFilePreview();
    }

    createProcessingPipeline(pipelineId, filename) {
        const pipelineHtml = `
            <div class="message agno-system" id="${pipelineId}">
                <div class="message-header">
                    <span class="agent-badge agno">🧠 Agno Document Processor</span>
                    <span class="timestamp">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="pipeline-container">
                    <div class="pipeline-header">
                        <h4>📄 Processing: ${filename}</h4>
                        <div class="pipeline-status">🔄 Initializing...</div>
                    </div>

                    <div class="pipeline-steps">
                        <div class="step" id="${pipelineId}-step-1">
                            <div class="step-icon">⏳</div>
                            <div class="step-content">
                                <div class="step-title">Step 1: Document Upload & Validation</div>
                                <div class="step-details">Uploading file and validating format...</div>
                            </div>
                        </div>

                        <div class="step" id="${pipelineId}-step-2">
                            <div class="step-icon">⏳</div>
                            <div class="step-content">
                                <div class="step-title">Step 2: Content Parsing & Structure Analysis</div>
                                <div class="step-details">Analyzing document structure and extracting raw data...</div>
                            </div>
                        </div>

                        <div class="step" id="${pipelineId}-step-3">
                            <div class="step-icon">⏳</div>
                            <div class="step-content">
                                <div class="step-title">Step 3: Entity Recognition & Classification</div>
                                <div class="step-details">Identifying financial entities and relationships...</div>
                            </div>
                        </div>

                        <div class="step" id="${pipelineId}-step-4">
                            <div class="step-icon">⏳</div>
                            <div class="step-content">
                                <div class="step-title">Step 4: Ontology Mapping & Confidence Scoring</div>
                                <div class="step-details">Mapping entities to ontology classes and calculating confidence...</div>
                            </div>
                        </div>

                        <div class="step" id="${pipelineId}-step-5">
                            <div class="step-icon">⏳</div>
                            <div class="step-content">
                                <div class="step-title">Step 5: Insight Generation & Recommendations</div>
                                <div class="step-details">Generating strategic insights and actionable recommendations...</div>
                            </div>
                        </div>
                    </div>

                    <div class="pipeline-logs">
                        <div class="logs-header">📋 Processing Logs</div>
                        <div class="logs-content" id="${pipelineId}-logs">
                            <div class="log-entry">🚀 Pipeline initialized for ${filename}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.chatMessages.insertAdjacentHTML('beforeend', pipelineHtml);
        this.scrollToBottom();

        // Simulate step-by-step processing
        this.simulateProcessingSteps(pipelineId);
    }

    showFilePreview(file) {
        this.filePreview.innerHTML = `
            <div class="file-preview-item">
                <i class="fas fa-file"></i>
                <span>${file.name}</span>
                <button onclick="agnoChat.hideFilePreview()" class="btn btn-sm btn-secondary">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        this.filePreview.classList.remove('hidden');
    }

    hideFilePreview() {
        this.filePreview.classList.add('hidden');
        this.filePreview.innerHTML = '';
    }

    addMessage(content, sender, agentType = null, metadata = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        let agentBadge = '';
        if (agentType) {
            const agentColor = this.getAgentColor(agentType);
            agentBadge = `<span class="agent-badge" style="background-color: ${agentColor}">${agentType}</span>`;
        }

        let metadataInfo = '';
        if (metadata) {
            const parts = [];
            if (metadata.reasoning_used) parts.push('🧠 Reasoning');
            if (metadata.processing_time) parts.push(`⏱️ ${metadata.processing_time}ms`);
            if (parts.length > 0) {
                metadataInfo = `<div class="message-metadata">${parts.join(' • ')}</div>`;
            }
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                ${agentBadge}
                <div class="message-text">${this.formatMessage(content)}</div>
                ${metadataInfo}
            </div>
        `;

        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }

    getAgentColor(agentType) {
        const colors = {
            'agno-system': '#6366f1',
            'agno_document_team': '#10b981',
            'agno_chat_team': '#f59e0b',
            'agno_rag_agent': '#8b5cf6',
            'agno_interface_creator': '#ef4444',
            'reasoning-demo': '#06b6d4',
            'system': '#6b7280',
            'error': '#dc2626'
        };
        return colors[agentType] || '#6b7280';
    }

    formatMessage(content) {
        // Convert markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message assistant typing';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatContainer.appendChild(typingDiv);
        this.scrollToBottom();
        
        return typingDiv;
    }

    removeTypingIndicator(typingElement) {
        if (typingElement && typingElement.parentNode) {
            typingElement.parentNode.removeChild(typingElement);
        }
    }

    offerInterfaceRendering(interfaceCode) {
        const offerDiv = document.createElement('div');
        offerDiv.className = 'interface-offer';
        offerDiv.innerHTML = `
            <div class="interface-offer-content">
                <p>🎨 I've generated interface code for you. Would you like me to render it?</p>
                <button onclick="agnoChat.renderInterface('${btoa(interfaceCode)}')" class="btn btn-primary btn-sm">
                    Render Interface
                </button>
                <button onclick="agnoChat.showInterfaceCode('${btoa(interfaceCode)}')" class="btn btn-secondary btn-sm">
                    Show Code
                </button>
            </div>
        `;
        
        this.chatContainer.appendChild(offerDiv);
        this.scrollToBottom();
    }

    renderInterface(encodedCode) {
        const code = atob(encodedCode);
        // This would integrate with the dashboard's widget system
        this.addMessage('🎨 Interface rendering would be implemented here.', 'system');
    }

    showInterfaceCode(encodedCode) {
        const code = atob(encodedCode);
        this.addMessage(`\`\`\`html\n${code}\n\`\`\``, 'assistant', 'interface-code');
    }

    autoResizeTextarea() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    async simulateProcessingSteps(pipelineId) {
        const steps = [
            {
                id: 1,
                duration: 1000,
                success: true,
                details: "✅ File uploaded successfully. Format: JSON. Size: validated.",
                logs: ["📤 File upload initiated", "🔍 Format validation: JSON detected", "✅ File size within limits", "📋 Document metadata extracted"]
            },
            {
                id: 2,
                duration: 1500,
                success: true,
                details: "✅ Document structure parsed. Found 47 data objects with financial indicators.",
                logs: ["🔧 JSON parsing initiated", "📊 Data structure analysis", "🏗️ Object hierarchy mapped", "💰 Financial indicators detected: Revenue, Expenses, Assets"]
            },
            {
                id: 3,
                duration: 2000,
                success: true,
                details: "✅ Identified 23 financial entities with 89% average confidence.",
                logs: ["🤖 Entity recognition engine started", "🏢 Company entities: 5 found", "💵 Financial metrics: 12 identified", "📈 Performance indicators: 6 detected", "🎯 Average confidence: 89%"]
            },
            {
                id: 4,
                duration: 1800,
                success: true,
                details: "✅ Ontology mapping complete. 18 classes matched with high confidence.",
                logs: ["🗂️ Ontology mapping initiated", "🔗 Class relationships established", "📊 Confidence scoring calculated", "✅ 18/23 entities mapped successfully", "⚠️ 5 entities require manual review"]
            },
            {
                id: 5,
                duration: 1200,
                success: true,
                details: "✅ Strategic insights generated with actionable recommendations.",
                logs: ["💡 Insight generation started", "📈 Trend analysis completed", "🎯 Recommendations formulated", "📋 Report compilation finished", "✅ Processing pipeline complete"]
            }
        ];

        for (const step of steps) {
            await this.processStep(pipelineId, step);
        }
    }

    async processStep(pipelineId, step) {
        // Update step status to processing
        const stepElement = document.getElementById(`${pipelineId}-step-${step.id}`);
        const logsElement = document.getElementById(`${pipelineId}-logs`);

        stepElement.querySelector('.step-icon').textContent = '🔄';
        stepElement.classList.add('processing');

        // Add logs progressively
        for (const log of step.logs) {
            await new Promise(resolve => setTimeout(resolve, step.duration / step.logs.length));
            logsElement.insertAdjacentHTML('beforeend', `<div class="log-entry">${log}</div>`);
            this.scrollToBottom();
        }

        // Complete step
        await new Promise(resolve => setTimeout(resolve, 200));
        stepElement.querySelector('.step-icon').textContent = step.success ? '✅' : '❌';
        stepElement.querySelector('.step-details').textContent = step.details;
        stepElement.classList.remove('processing');
        stepElement.classList.add(step.success ? 'completed' : 'failed');
    }

    updatePipelineComplete(pipelineId, result) {
        const pipelineElement = document.getElementById(pipelineId);
        const statusElement = pipelineElement.querySelector('.pipeline-status');
        const logsElement = document.getElementById(`${pipelineId}-logs`);

        statusElement.textContent = '✅ Processing Complete';
        statusElement.classList.add('success');

        // Add final results
        logsElement.insertAdjacentHTML('beforeend', `
            <div class="log-entry success">🎉 Document processing completed successfully!</div>
            <div class="log-entry">📊 Confidence Score: ${result.confidence_score || 0.94}</div>
            <div class="log-entry">⚡ Processing Time: ${result.processing_time || '3.2s'}</div>
        `);

        // Add results section
        const resultsHtml = `
            <div class="pipeline-results">
                <div class="results-header">📊 Processing Results</div>
                <div class="results-content">
                    ${result.response || result.message}
                </div>
                <div class="results-actions">
                    <button class="btn-secondary" onclick="agnoChat.reviewPipeline('${pipelineId}')">🔍 Review Pipeline</button>
                    <button class="btn-secondary" onclick="agnoChat.improvePipeline('${pipelineId}')">⚡ Improve Pipeline</button>
                    <button class="btn-primary" onclick="agnoChat.acceptResults('${pipelineId}')">✅ Accept Results</button>
                </div>
            </div>
        `;

        pipelineElement.querySelector('.pipeline-container').insertAdjacentHTML('beforeend', resultsHtml);
        this.scrollToBottom();
    }

    updatePipelineError(pipelineId, error) {
        const pipelineElement = document.getElementById(pipelineId);
        const statusElement = pipelineElement.querySelector('.pipeline-status');
        const logsElement = document.getElementById(`${pipelineId}-logs`);

        statusElement.textContent = '❌ Processing Failed';
        statusElement.classList.add('error');

        logsElement.insertAdjacentHTML('beforeend', `
            <div class="log-entry error">❌ Error: ${error}</div>
            <div class="log-entry">🔧 Pipeline debugging required</div>
        `);

        // Add error actions
        const errorActionsHtml = `
            <div class="pipeline-results error">
                <div class="results-header">⚠️ Processing Error</div>
                <div class="results-content">
                    Processing failed: ${error}
                </div>
                <div class="results-actions">
                    <button class="btn-secondary" onclick="agnoChat.debugPipeline('${pipelineId}')">🐛 Debug Pipeline</button>
                    <button class="btn-secondary" onclick="agnoChat.retryPipeline('${pipelineId}')">🔄 Retry Processing</button>
                </div>
            </div>
        `;

        pipelineElement.querySelector('.pipeline-container').insertAdjacentHTML('beforeend', errorActionsHtml);
        this.scrollToBottom();
    }

    // Pipeline action methods
    reviewPipeline(pipelineId) {
        this.addMessage('🔍 **Pipeline Review Requested**\n\nAnalyzing pipeline performance and identifying optimization opportunities...', 'assistant', 'Agno Pipeline Reviewer');
    }

    improvePipeline(pipelineId) {
        this.addMessage('⚡ **Pipeline Improvement Mode**\n\nSuggested improvements:\n• Increase entity recognition confidence threshold\n• Add custom financial domain rules\n• Implement iterative refinement loops\n\nWould you like to apply these improvements?', 'assistant', 'Agno Pipeline Optimizer');
    }

    acceptResults(pipelineId) {
        this.addMessage('✅ **Results Accepted**\n\nPipeline results have been accepted and saved to the knowledge base. The extracted ontology and insights are now available for analysis.', 'assistant', 'Agno System');
    }

    debugPipeline(pipelineId) {
        this.addMessage('🐛 **Pipeline Debug Mode**\n\nInitiating debug analysis:\n• Checking input validation\n• Analyzing processing steps\n• Identifying failure points\n• Generating debug report\n\nDebug information will be displayed shortly...', 'assistant', 'Agno Debugger');
    }

    retryPipeline(pipelineId) {
        this.addMessage('🔄 **Retrying Pipeline**\n\nRe-initializing processing pipeline with enhanced error handling...', 'assistant', 'Agno System');
        // Could trigger a new pipeline here
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.agnoChat = new AgnoChatInterface();
});
