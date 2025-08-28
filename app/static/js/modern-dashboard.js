// Modern Dashboard JavaScript
class KudwaDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.chatMessages = [];
        this.pendingFiles = [];
        this.cy = null; // Cytoscape instance
        this.graphLibsReady = false; // Cytoscape + layouts readiness
        this.currentNodeData = null; // For record-specific chat
        this.widgets = []; // Widget instances
        this.widgetCounter = 0; // For unique widget IDs
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.setupChat();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.currentTarget.dataset.section;
                this.switchSection(section);
            });
        });

        // Database wipe
        document.getElementById('wipe-database-btn').addEventListener('click', () => {
            this.showWipeConfirmation();
        });

        document.getElementById('execute-wipe-btn').addEventListener('click', () => {
            this.wipeDatabase();
        });

        document.getElementById('cancel-wipe-btn').addEventListener('click', () => {
            this.hideWipeConfirmation();
        });

        // Refresh data
        document.getElementById('refresh-data-btn').addEventListener('click', () => {
            this.loadDashboardData();
        });

        // Chat functionality
        document.getElementById('send-message-btn').addEventListener('click', () => {
            this.sendMessage();
        });

        // Modal functionality
        this.setupModalEventListeners();

        // Widget functionality
        this.setupWidgetEventListeners();

        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // File upload
        document.getElementById('file-upload-input').addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });

        document.getElementById('file-upload-btn').addEventListener('click', () => {
            document.getElementById('file-upload-input').click();
        });

        // Graph controls
        document.getElementById('refresh-graph-btn').addEventListener('click', () => {
            this.loadKnowledgeGraph();
        });

        document.getElementById('fit-graph-btn').addEventListener('click', () => {
            if (this.cy) {
                this.cy.fit();
            }
        });

        document.getElementById('graph-layout-select').addEventListener('change', (e) => {
            this.changeGraphLayout(e.target.value);
        });

        // Mark graph libs ready when Cytoscape is present
        if (window.cytoscape && typeof window.cytoscape === 'function') {
            this.graphLibsReady = true;
        }

    }

    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.classList.add('hidden');
        });
        document.getElementById(`${section}-section`).classList.remove('hidden');

        // Update page title
        const titles = {
            dashboard: 'Financial Dashboard',
            chat: 'AI Chat Assistant',
            ontology: 'Ontology Management',
            graph: 'Knowledge Graph',
            documents: 'Document Management',
            approvals: 'Pending Approvals',
            settings: 'System Settings'
        };
        document.getElementById('page-title').textContent = titles[section];

        this.currentSection = section;

        // Load section-specific data
        switch(section) {
            case 'ontology':
                this.loadOntologyData();
                break;
            case 'graph':
                this.loadKnowledgeGraph();
                break;
            case 'documents':
                this.loadDocuments();
                break;
            case 'approvals':
                this.loadApprovals();
                break;
        }
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/v1/dashboard/stats');
            const result = await response.json();
            const data = result.data || result; // Handle both formats

            document.getElementById('total-documents').textContent = data.total_documents || data.documents || 0;
            document.getElementById('total-ontology-classes').textContent = data.total_ontology_classes || data.ontology_classes || 0;
            document.getElementById('total-observations').textContent = data.total_observations || data.observations || 0;
            document.getElementById('total-datasets').textContent = data.pending_approvals || data.datasets || 0;

            // Load charts
            this.loadRevenueChart();
            this.loadExpenseChart();
            this.loadRecentObservations();

            // Load approval count for sidebar
            this.loadApprovalCount();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadApprovalCount() {
        try {
            // Use the global approvals endpoint
            const response = await fetch('/api/v1/approvals/pending');
            const result = await response.json();
            const data = result.data || result;

            // Update sidebar badge
            const sidebarCountEl = document.getElementById('approval-count');
            if (sidebarCountEl) {
                sidebarCountEl.textContent = data.total_pending || (data.approvals ? data.approvals.length : 0);
            }
        } catch (error) {
            console.error('Error loading approval count:', error);
        }
    }

    async loadRevenueChart() {
        try {
            const response = await fetch('/api/v1/dashboard/revenue-trends');
            const data = await response.json();
            
            const trace = {
                x: data.periods || [],
                y: data.amounts || [],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Revenue',
                line: { color: '#2563eb' }
            };

            const layout = {
                title: '',
                xaxis: { title: 'Period' },
                yaxis: { title: 'Amount (USD)' },
                margin: { t: 20, r: 20, b: 40, l: 60 }
            };

            Plotly.newPlot('revenue-chart', [trace], layout, {responsive: true});
        } catch (error) {
            console.error('Error loading revenue chart:', error);
        }
    }

    async loadExpenseChart() {
        try {
            const response = await fetch('/api/v1/dashboard/expense-breakdown');
            const data = await response.json();
            
            const trace = {
                labels: data.categories || [],
                values: data.amounts || [],
                type: 'pie',
                marker: {
                    colors: ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                }
            };

            const layout = {
                title: '',
                margin: { t: 20, r: 20, b: 20, l: 20 }
            };

            Plotly.newPlot('expense-chart', [trace], layout, {responsive: true});
        } catch (error) {
            console.error('Error loading expense chart:', error);
        }
    }

    async loadRecentObservations() {
        try {
            const response = await fetch('/api/v1/dashboard/recent-observations');
            const data = await response.json();
            
            const tbody = document.getElementById('recent-observations');
            tbody.innerHTML = '';

            if (data.observations && data.observations.length > 0) {
                data.observations.forEach(obs => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><span class="badge">${obs.observation_type}</span></td>
                        <td>${obs.account_name}</td>
                        <td>$${parseFloat(obs.amount).toLocaleString()}</td>
                        <td>${obs.currency}</td>
                        <td>${obs.period_start} to ${obs.period_end}</td>
                        <td>
                            <button class="btn btn-sm btn-secondary">
                                <i class="fas fa-eye"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No observations found</td></tr>';
            }
        } catch (error) {
            console.error('Error loading recent observations:', error);
        }
    }

    async loadOntologyData() {
        try {
            const response = await fetch('/api/v1/dashboard/ontology/classes');
            const result = await response.json();
            const data = result.data || result;

            const tbody = document.getElementById('ontology-classes');
            tbody.innerHTML = '';

            // Combine approved and pending classes
            const allClasses = [
                ...(data.approved_classes || []),
                ...(data.pending_classes || [])
            ];

            if (allClasses && allClasses.length > 0) {
                allClasses.forEach(cls => {
                    const row = document.createElement('tr');
                    const statusBadge = cls.status === 'pending_review' ? 'warning' : 'success';
                    const isPending = cls.status === 'pending_review';
                    const buttonId = isPending ? cls.approval_id : cls.id;

                    row.innerHTML = `
                        <td><code>${cls.class_id}</code></td>
                        <td>${cls.label}</td>
                        <td>${cls.class_type}</td>
                        <td><span class="badge badge-${statusBadge}">${cls.status}</span></td>
                        <td>
                            ${isPending ?
                                `<button class="btn btn-sm btn-primary" onclick="dashboard.approveOntologyClass('${buttonId}')">
                                    <i class="fas fa-check"></i>
                                </button>` :
                                '<span class="text-success">Approved</span>'
                            }
                            <button class="btn btn-sm btn-secondary">
                                <i class="fas fa-edit"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No ontology classes found</td></tr>';
            }
        } catch (error) {
            console.error('Error loading ontology data:', error);
        }
    }

    setupChat() {
        // Auto-resize chat input
        const chatInput = document.getElementById('chat-input');
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 128) + 'px';
        });
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message && this.pendingFiles.length === 0) return;

        // Add user message to chat
        if (message) {
            this.addMessageToChat('user', message);
        }

        // Handle file uploads
        if (this.pendingFiles.length > 0) {
            await this.uploadFiles();
        }

        // Clear input
        input.value = '';
        input.style.height = 'auto';

        // Send to AI
        if (message) {
            await this.sendToAI(message);
        }
    }

    addMessageToChat(sender, content, isFile = false) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = sender === 'user' ? 'U' : 'AI';
        const avatarClass = sender === 'user' ? 'user' : 'ai';
        
        messageDiv.innerHTML = `
            <div class="message-avatar ${avatarClass}">${avatar}</div>
            <div class="message-content">
                ${isFile ? `<i class="fas fa-file"></i> ` : ''}${content}
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async sendToAI(message) {
        const startTime = Date.now();
        let debugInfo = {
            message: message,
            timestamp: new Date().toISOString(),
            user_id: 'demo_user'
        };

        try {
            console.log('🤖 Sending message to AI:', debugInfo);

            // Show typing indicator with debug info
            this.addMessageToChat('ai', `
                <div class="loading">
                    <div class="spinner"></div>
                    <span>Thinking...</span>
                    <small style="display: block; color: #666; margin-top: 4px;">
                        Debug: Sent at ${new Date().toLocaleTimeString()}
                    </small>
                </div>
            `);

            // Check for special Agno commands
            if (message.startsWith('/')) {
                await this.handleAgnoCommand(message);
                return;
            }

            // Determine if we should use Agno or CrewAI
            const useAgno = this.shouldUseAgno(message);
            const endpoint = useAgno ? '/api/v1/agno/unified-chat' : '/api/v1/crew/chat';

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: 'demo_user',
                    context: {
                        current_section: this.currentSection,
                        timestamp: new Date().toISOString(),
                        use_reasoning: true
                    },
                    use_reasoning: true,
                    create_interface: message.toLowerCase().includes('create') || message.toLowerCase().includes('interface')
                })
            });

            const responseTime = Date.now() - startTime;
            debugInfo.response_time_ms = responseTime;
            debugInfo.status = response.status;
            debugInfo.ok = response.ok;

            console.log('📡 API Response received:', debugInfo);

            const data = await response.json();
            debugInfo.response_data = data;

            // Remove typing indicator
            const messages = document.getElementById('chat-messages');
            messages.removeChild(messages.lastChild);

            if (!response.ok) {
                console.error('❌ API Error:', data);
                this.addMessageToChat('ai', `
                    <div class="error-response">
                        <strong>API Error (${response.status}):</strong><br>
                        ${data.detail || data.message || 'Unknown error'}<br>
                        <small style="color: #666;">Response time: ${responseTime}ms</small>
                    </div>
                `);
                return;
            }

            // Add AI response with debug info and optional visualization
            const aiResponse = data.response || 'Sorry, I encountered an error processing your request.';
            let responseHtml = `<div class="ai-response">${aiResponse}`;

            // Add visualization if present
            if (data.graph_data) {
                responseHtml += `
                    <div style="margin-top: 12px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; background: #f9f9f9;">
                        <strong>📊 Visualization:</strong>
                        <pre style="background: #fff; padding: 8px; border-radius: 4px; margin-top: 4px; overflow-x: auto; font-size: 0.85em;">${JSON.stringify(data.graph_data, null, 2)}</pre>
                    </div>
                `;
            }

            // Add debug info
            responseHtml += `
                <details style="margin-top: 8px; font-size: 0.8em; color: #666;">
                    <summary style="cursor: pointer;">Debug Info</summary>
                    <pre style="background: #f5f5f5; padding: 8px; border-radius: 4px; margin-top: 4px; overflow-x: auto;">${JSON.stringify(debugInfo, null, 2)}</pre>
                </details>
            </div>`;

            this.addMessageToChat('ai', responseHtml);

            console.log('✅ Chat interaction completed:', debugInfo);

        } catch (error) {
            const errorTime = Date.now() - startTime;
            console.error('💥 Chat error:', error);

            // Remove typing indicator if it exists
            try {
                const messages = document.getElementById('chat-messages');
                if (messages.lastChild && messages.lastChild.querySelector('.loading')) {
                    messages.removeChild(messages.lastChild);
                }
            } catch (e) {
                // Ignore cleanup errors
            }

            this.addMessageToChat('ai', `
                <div class="error-response">
                    <strong>Connection Error:</strong><br>
                    ${error.message}<br>
                    <small style="color: #666;">
                        Time: ${errorTime}ms | Check console for details
                    </small>
                </div>
            `);
        }
    }

    handleFileUpload(files) {
        this.pendingFiles = Array.from(files);
        
        // Show file preview
        const preview = document.getElementById('file-preview');
        preview.innerHTML = '';
        preview.classList.remove('hidden');
        
        this.pendingFiles.forEach(file => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-preview-item';
            fileDiv.innerHTML = `
                <i class="fas fa-file"></i>
                <span>${file.name}</span>
                <span class="file-size">(${this.formatFileSize(file.size)})</span>
            `;
            preview.appendChild(fileDiv);
        });
    }

    async uploadFiles() {
        for (const file of this.pendingFiles) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('request_data', JSON.stringify({
                user_id: 'demo_user',
                context: {
                    timestamp: new Date().toISOString(),
                    use_agno: true
                }
            }));

            try {
                this.addMessageToChat('user', `📄 Uploading ${file.name} for Agno analysis...`, true);

                // Try Agno unified document processing first
                let response = await fetch('/api/v1/agno/upload-document', {
                    method: 'POST',
                    body: formData
                });

                let result = await response.json();

                if (response.ok && result.success) {
                    // Agno processing successful
                    const analysis = result.analysis || {};
                    const reasoningSteps = analysis.reasoning_steps || [];
                    const entities = analysis.entities_found || [];
                    const recommendations = analysis.recommendations || [];

                    this.addMessageToChat('ai', `
                        <div class="agno-upload-response">
                            <div class="framework-badge agno-badge">🧠 ${result.agent_type} (${result.processing_time_ms}ms)</div>

                            <div class="upload-success">
                                ✅ <strong>Successfully processed ${file.name}</strong>
                            </div>

                            <div class="analysis-results">
                                <h4>📊 Document Analysis:</h4>
                                <div class="agno-analysis">
                                    ${analysis.document_analysis}<br>
                                    <strong>Confidence Score:</strong> ${(analysis.confidence_score * 100).toFixed(1)}%
                                </div>

                                <h4>🧠 Reasoning Steps:</h4>
                                <div class="reasoning-steps">
                                    ${reasoningSteps.map(step => `<div class="reasoning-step">• ${step}</div>`).join('')}
                                </div>

                                <h4>🏷️ Entities Found:</h4>
                                <div class="entities-found">
                                    ${entities.map(entity => `<span class="entity-tag">${entity}</span>`).join(' ')}
                                </div>

                                <h4>💡 Recommendations:</h4>
                                <div class="recommendations">
                                    ${recommendations.map(rec => `<div class="recommendation">• ${rec}</div>`).join('')}
                                </div>
                            </div>

                            <div class="processing-info">
                                <small>Framework: ${result.framework} | File: ${result.file_processed?.size} bytes</small>
                            </div>
                        </div>
                    `);
                } else {
                    // Fallback to original endpoint
                    console.log('Agno processing failed, falling back to original endpoint');

                    const fallbackFormData = new FormData();
                    fallbackFormData.append('file', file);
                    fallbackFormData.append('user_id', 'demo_user');

                    response = await fetch('/api/v1/documents/ingest-rootfi', {
                        method: 'POST',
                        body: fallbackFormData
                    });

                    result = await response.json();

                    if (response.ok && result.success) {
                        const entities = result.ontology_classes_extracted || 0;
                        const processingTime = result.processing_results?.processing_time || 0;
                        this.addMessageToChat('ai', `
                            <div class="fallback-upload-response">
                                <div class="framework-badge">⚙️ CrewAI Fallback</div>

                                ✅ <strong>Successfully processed ${file.name}</strong>

                                <div class="results-summary">
                                    📊 <strong>Results:</strong><br>
                                    • <strong>${entities} entities</strong> extracted with LangExtract AI<br>
                                    • <strong>Processing time:</strong> ${processingTime.toFixed(2)} seconds<br>
                                    • <strong>Document ID:</strong> ${result.document_id}
                                </div>

                                <div class="next-steps">
                                    The document has been analyzed and ${entities} entities are pending approval.
                                    Check the <strong>Approvals</strong> section to review and approve them!
                                </div>
                            </div>
                        `);
                    } else {
                        this.addMessageToChat('ai', `❌ Error processing ${file.name}: ${result.error || result.detail || 'Unknown error'}`);
                    }
                }
            } catch (error) {
                console.error('Error uploading file:', error);
                this.addMessageToChat('ai', `❌ Error uploading ${file.name}: ${error.message}`);
            }
        }

        // Clear pending files
        this.pendingFiles = [];
        document.getElementById('file-preview').classList.add('hidden');
        
        // Refresh dashboard data
        this.loadDashboardData();
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showWipeConfirmation() {
        document.getElementById('wipe-confirmation-modal').classList.remove('hidden');
    }

    hideWipeConfirmation() {
        document.getElementById('wipe-confirmation-modal').classList.add('hidden');
    }

    async wipeDatabase() {
        try {
            const response = await fetch('/api/v1/database/wipe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                alert('Database wiped successfully!');
                this.hideWipeConfirmation();
                this.loadDashboardData();
            } else {
                alert('Error wiping database. Please try again.');
            }
        } catch (error) {
            console.error('Error wiping database:', error);
            alert('Error wiping database. Please try again.');
        }
    }

    async approveOntologyClass(classId) {
        try {
            const response = await fetch(`/api/v1/approvals/${classId}/approve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const result = await response.json();
                console.log('✅ Approval successful:', result);

                // Show success message
                alert(`✅ Successfully approved: ${result.message || 'Ontology class approved'}`);

                this.loadOntologyData();
                // Also refresh approvals if we're on that page
                if (this.currentSection === 'approvals') {
                    this.loadApprovals();
                }
            } else {
                // Get detailed error message
                const errorData = await response.json();
                const errorMsg = errorData.detail || errorData.message || 'Unknown error';

                console.error('❌ Approval failed:', errorData);

                // Check if it's a duplicate error
                if (errorMsg.includes('duplicate key') || errorMsg.includes('already exists')) {
                    alert('⚠️ This item already exists and cannot be approved again. Try approving a different item.');
                } else {
                    alert(`❌ Error approving: ${errorMsg}`);
                }
            }
        } catch (error) {
            console.error('Error approving ontology class:', error);
            alert('❌ Network error. Please check your connection and try again.');
        }
    }

    async approveItem(itemId) {
        // Generic approval function for different item types
        try {
            // For now, assume it's an ontology class
            await this.approveOntologyClass(itemId);
        } catch (error) {
            console.error('Error approving item:', error);
            alert('Error approving item. Please try again.');
        }
    }

    async rejectItem(itemId) {
        // Generic rejection function for different item types
        try {
            if (confirm('Are you sure you want to reject this item?')) {
                // TODO: Implement rejection endpoint
                console.log('Rejecting item:', itemId);
                alert('Rejection functionality not yet implemented');
            }
        } catch (error) {
            console.error('Error rejecting item:', error);
            alert('Error rejecting item. Please try again.');
        }
    }

    async loadDocuments() {
        try {
            const response = await fetch('/api/v1/dashboard/documents');
            const result = await response.json();
            const documents = result.data || result.documents || [];

            const tbody = document.getElementById('documents-list');
            tbody.innerHTML = '';

            if (!documents || documents.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No documents found</td></tr>';
                return;
            }

            documents.forEach(doc => {
                const uploaded = new Date(doc.created_at).toLocaleString();
                const sizeInMB = (doc.file_size / 1024 / 1024).toFixed(2);
                const statusBadge = doc.processing_status === 'completed' ? 'success' : 'secondary';

                tbody.insertAdjacentHTML('beforeend', `
                    <tr>
                        <td>${doc.filename}</td>
                        <td>${doc.content_type || '-'}</td>
                        <td>${sizeInMB} MB</td>
                        <td><span class="badge badge-${statusBadge}">${doc.processing_status}</span></td>
                        <td>${uploaded}</td>
                        <td>
                            <button class="btn btn-sm btn-secondary" title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                        </td>
                    </tr>
                `);
            });
        } catch (error) {
            console.error('Error loading documents:', error);
            const tbody = document.getElementById('documents-list');
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading documents</td></tr>';
        }
    }

    async loadApprovals() {
        try {
            // Use the global approvals endpoint
            const response = await fetch('/api/v1/approvals/pending');
            const result = await response.json();
            const data = result.data || result;

            const container = document.getElementById('approval-items');
            if (!container) {
                console.error('Approval items container not found');
                return;
            }

            // Show/hide bulk approve button
            const bulkBtn = document.getElementById('bulk-approve-btn');
            if (bulkBtn) {
                if (!data.approvals || data.approvals.length === 0) {
                    bulkBtn.style.display = 'none';
                    container.innerHTML = '<p class="text-center text-secondary">No pending approvals</p>';
                    return;
                } else {
                    bulkBtn.style.display = 'inline-flex';
                }
            }

            // Create approval cards
            container.innerHTML = '';
            data.approvals.forEach(approval => {
                const approvalCard = document.createElement('div');
                approvalCard.className = 'approval-card';
                approvalCard.innerHTML = `
                    <div class="approval-header">
                        <h4>${approval.title || approval.type}</h4>
                        <span class="badge badge-warning">Pending</span>
                    </div>
                    <div class="approval-content">
                        <p><strong>Type:</strong> ${approval.type}</p>
                        <p><strong>Description:</strong> ${approval.description || 'No description available'}</p>
                        ${approval.data ? `<details><summary>Details</summary><pre>${JSON.stringify(approval.data, null, 2)}</pre></details>` : ''}
                    </div>
                    <div class="approval-actions">
                        <button class="btn btn-success" onclick="dashboard.approveItem('${approval.id}')">
                            <i class="fas fa-check"></i> Approve
                        </button>
                        <button class="btn btn-danger" onclick="dashboard.rejectItem('${approval.id}')">
                            <i class="fas fa-times"></i> Reject
                        </button>
                    </div>
                `;
                container.appendChild(approvalCard);
            });

            // Update count in both places
            const countEl = document.getElementById('pending-count');
            if (countEl) {
                countEl.textContent = `${data.approvals.length} pending`;
            }

            // Update sidebar badge
            const sidebarCountEl = document.getElementById('approval-count');
            if (sidebarCountEl) {
                sidebarCountEl.textContent = data.approvals.length;
            }

        } catch (error) {
            console.error('Error loading approvals:', error);
            const container = document.getElementById('approval-items');
            if (container) {
                container.innerHTML = '<p class="text-center text-danger">Error loading approvals</p>';
            }
        }
    }

    async bulkApproveAll() {
        try {
            // Get all pending approvals first
            const response = await fetch('/api/v1/approvals/pending');
            const result = await response.json();
            const data = result.data || result;

            if (!data.approvals || data.approvals.length === 0) {
                alert('No pending approvals to process.');
                return;
            }

            const totalCount = data.approvals.length;
            if (!confirm(`Are you sure you want to approve all ${totalCount} pending items? This action cannot be undone.`)) {
                return;
            }

            // Show progress
            const bulkBtn = document.getElementById('bulk-approve-btn');
            const originalText = bulkBtn.innerHTML;
            bulkBtn.disabled = true;
            bulkBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Approving...';

            // Use the bulk approve API endpoint
            try {
                const approvalIds = data.approvals.map(approval => approval.id);
                const bulkResponse = await fetch('/api/v1/approvals/bulk-approve', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        approval_ids: approvalIds
                    })
                });

                if (bulkResponse.ok) {
                    const bulkResult = await bulkResponse.json();

                    // Restore button
                    bulkBtn.disabled = false;
                    bulkBtn.innerHTML = originalText;

                    // Show results
                    const successCount = bulkResult.approved_count || 0;
                    const errorCount = bulkResult.failed_count || 0;

                    let message = `✅ Bulk approval completed!\n\n`;
                    message += `✅ Successfully approved: ${successCount}\n`;
                    if (errorCount > 0) {
                        message += `❌ Failed: ${errorCount}\n`;
                        if (bulkResult.errors && bulkResult.errors.length > 0) {
                            message += `\nErrors:\n${bulkResult.errors.slice(0, 5).join('\n')}`;
                            if (bulkResult.errors.length > 5) {
                                message += `\n... and ${bulkResult.errors.length - 5} more`;
                            }
                        }
                    }

                    alert(message);

                    // Refresh the approvals view
                    this.loadApprovals();
                    this.loadDashboardData(); // Refresh dashboard stats

                } else {
                    throw new Error(`Bulk approve failed: ${bulkResponse.status}`);
                }

            } catch (bulkError) {
                console.warn('Bulk approve failed, falling back to individual approvals:', bulkError);

                // Fallback to individual approvals
                let successCount = 0;
                let errorCount = 0;
                const errors = [];

                // Process each approval individually
                for (const approval of data.approvals) {
                    try {
                        const approveResponse = await fetch(`/api/v1/approvals/${approval.id}/approve`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            }
                        });

                        if (approveResponse.ok) {
                            successCount++;
                        } else {
                            const errorData = await approveResponse.json();
                            errorCount++;
                            errors.push(`${approval.title || approval.id}: ${errorData.detail || 'Unknown error'}`);
                        }
                    } catch (error) {
                        errorCount++;
                        errors.push(`${approval.title || approval.id}: ${error.message}`);
                    }

                    // Update progress
                    bulkBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${successCount + errorCount}/${totalCount}`;
                }

                // Restore button
                bulkBtn.disabled = false;
                bulkBtn.innerHTML = originalText;

                // Show results
                let message = `✅ Bulk approval completed!\n\n`;
                message += `✅ Successfully approved: ${successCount}\n`;
                if (errorCount > 0) {
                    message += `❌ Failed: ${errorCount}\n\n`;
                    if (errors.length > 0) {
                        message += `Errors:\n${errors.slice(0, 5).join('\n')}`;
                        if (errors.length > 5) {
                            message += `\n... and ${errors.length - 5} more`;
                        }
                    }
                }

                alert(message);

                // Refresh the approvals view
                this.loadApprovals();
                this.loadDashboardData(); // Refresh dashboard stats
            }

        } catch (error) {
            console.error('Error in bulk approval:', error);
            alert('❌ Error during bulk approval. Please try again.');

            // Restore button
            const bulkBtn = document.getElementById('bulk-approve-btn');
            bulkBtn.disabled = false;
            bulkBtn.innerHTML = '<i class="fas fa-check-double"></i> Approve All';
        }
    }

    async loadKnowledgeGraph() {
        try {
            console.log('Loading knowledge graph...');
            const response = await fetch('/api/v1/dashboard/knowledge-graph');
            const result = await response.json();
            const data = result.data || result;

            console.log('Knowledge graph data received:', {
                nodes: data.nodes?.length || 0,
                edges: data.edges?.length || 0,
                stats: data.stats
            });

            if (!data.nodes || data.nodes.length === 0) {
                console.warn('Knowledge graph returned no nodes', data);
                // Show a message in the graph container
                const container = document.getElementById('knowledge-graph');
                container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">No graph data available. Upload documents and approve entities to see relationships.</div>';
                return;
            }

            this.renderKnowledgeGraph(data);
        } catch (error) {
            console.error('Error loading knowledge graph:', error);
            const container = document.getElementById('knowledge-graph');
            container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #dc3545;">Error loading knowledge graph</div>';
        }
    }

    renderKnowledgeGraph(data) {
        const container = document.getElementById('knowledge-graph');

        // Convert nodes/edges format to Cytoscape elements format
        const elements = [];

        // Add nodes
        if (data.nodes) {
            data.nodes.forEach(node => {
                elements.push({
                    data: {
                        id: node.id,
                        label: node.label || node.id,
                        type: node.type || 'unknown',
                        size: node.size || 5,
                        ...node
                    }
                });
            });
        }

        // Add edges
        if (data.edges) {
            data.edges.forEach(edge => {
                elements.push({
                    data: {
                        id: `${edge.source}-${edge.target}`,
                        source: edge.source,
                        target: edge.target,
                        relationship: edge.label || edge.type || 'related',
                        ...edge
                    }
                });
            });
        }

        console.log('Rendering knowledge graph with', elements.length, 'elements:', {
            nodes: data.nodes?.length || 0,
            edges: data.edges?.length || 0
        });

        // Initialize Cytoscape if not already done
        if (!this.graphLibsReady) {
            container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#666;">Graph libraries not loaded yet. Please wait or refresh.</div>';
            console.warn('Cytoscape not yet ready');
            return;
        }

        if (!this.cy) {
            this.cy = cytoscape({
                container: container,
                style: [
                    {
                        selector: 'node',
                        style: {
                            'background-color': '#2563eb',
                            'label': 'data(label)',
                            'color': 'white',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'font-size': '12px',
                            'font-weight': 'bold',
                            'width': 'mapData(size, 1, 10, 30, 80)',
                            'height': 'mapData(size, 1, 10, 30, 80)',
                            'text-outline-width': 2,
                            'text-outline-color': '#000'
                        }
                    },
                    {
                        selector: 'node[type="ontology_class"]',
                        style: {
                            'background-color': '#2563eb',
                            'shape': 'round-rectangle'
                        }
                    },
                    {
                        selector: 'node[type="financial_entity"]',
                        style: {
                            'background-color': '#10b981',
                            'shape': 'ellipse'
                        }
                    },
                    {
                        selector: 'node[type="document"]',
                        style: {
                            'background-color': '#f59e0b',
                            'shape': 'diamond'
                        }
                    },
                    {
                        selector: 'edge',
                        style: {
                            'width': 2,
                            'line-color': '#64748b',
                            'target-arrow-color': '#64748b',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'label': 'data(relationship)',
                            'font-size': '10px',
                            'color': '#64748b',
                            'text-rotation': 'autorotate'
                        }
                    },
                    {
                        selector: 'node:selected',
                        style: {
                            'border-width': 3,
                            'border-color': '#ef4444'
                        }
                    }
                ],
                // Use a safe default layout at init; apply advanced layout after data load
                layout: { name: 'grid' }
            });

            // Add click handlers
            this.cy.on('tap', 'node', (evt) => {
                const node = evt.target;
                this.showNodeDetails(node.data());
            });
        }

        // Update graph data
        this.cy.elements().remove();
        this.cy.add(elements);

        console.log('Added elements to graph:', {
            nodes: this.cy.nodes().length,
            edges: this.cy.edges().length,
            totalElements: elements.length
        });

        // Choose layout from selector; robust fallback chain
        const tryRun = (name) => {
            try {
                const layout = this.cy.layout({ name });
                layout.run();
                console.log('Layout applied:', name);
                return true;
            } catch (e) {
                console.warn('Failed to apply layout', name, e);
                return false;
            }
        };

        const layoutSelect = document.getElementById('graph-layout-select');
        const preferred = layoutSelect ? layoutSelect.value : 'cose-bilkent';
        if (!tryRun(preferred)) {
            if (!tryRun('cose-bilkent')) {
                if (!tryRun('circle')) {
                    tryRun('grid');
                }
            }
        }

        // Update stats
        const nodeCount = this.cy.nodes().length;
        const edgeCount = this.cy.edges().length;

        // Update stats display if elements exist
        const nodeCountEl = document.getElementById('graph-node-count');
        const edgeCountEl = document.getElementById('graph-edge-count');

        if (nodeCountEl) nodeCountEl.textContent = `${nodeCount} nodes`;
        if (edgeCountEl) edgeCountEl.textContent = `${edgeCount} edges`;

        console.log('Knowledge graph rendered successfully:', { nodeCount, edgeCount });
    }

    changeGraphLayout(layoutName) {
        if (this.cy) {
            const layout = this.cy.layout({ name: layoutName });
            layout.run();
        }
    }

    setupModalEventListeners() {
        // Modal close functionality
        const modal = document.getElementById('nodeModal');
        const closeBtn = modal.querySelector('.modal-close');

        closeBtn.addEventListener('click', () => {
            this.closeNodeModal();
        });

        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeNodeModal();
            }
        });

        // Record-specific chat
        const recordChatSend = document.getElementById('recordChatSend');
        const recordChatInput = document.getElementById('recordChatInput');

        recordChatSend.addEventListener('click', () => {
            this.sendRecordSpecificMessage();
        });

        recordChatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendRecordSpecificMessage();
            }
        });
    }

    async showNodeDetails(nodeData) {
        this.currentNodeData = nodeData;

        // Fetch detailed information about the node
        const details = await this.fetchNodeDetails(nodeData);

        // Update modal content
        document.getElementById('modalTitle').textContent = `${nodeData.label || nodeData.id}`;

        const nodeDetailsContainer = document.getElementById('nodeDetails');
        nodeDetailsContainer.innerHTML = this.renderNodeDetails(details);

        // Clear previous chat messages
        document.getElementById('recordChatMessages').innerHTML = '';
        document.getElementById('recordChatInput').value = '';

        // Show modal
        document.getElementById('nodeModal').style.display = 'block';
    }

    async fetchNodeDetails(nodeData) {
        try {
            // Determine the correct ID based on node type
            let nodeId;
            switch (nodeData.type) {
                case 'ontology_class':
                    nodeId = nodeData.class_id || nodeData.id;
                    break;
                case 'financial_entity':
                    nodeId = nodeData.source_id || nodeData.id;
                    break;
                case 'document':
                    nodeId = nodeData.document_id || nodeData.id;
                    break;
                default:
                    nodeId = nodeData.id;
            }

            console.log('Fetching details for:', { type: nodeData.type, nodeId, originalData: nodeData });

            const endpoint = `/api/v1/dashboard/node-details/${nodeData.type}/${nodeId}`;
            const response = await fetch(endpoint);
            const data = await response.json();

            if (data.error) {
                console.warn('Node details not found:', data.error);
                return nodeData;
            }

            console.log('Fetched node details:', data);
            return data;
        } catch (error) {
            console.error('Error fetching node details:', error);
            return nodeData;
        }
    }

    renderNodeDetails(details) {
        const items = [];

        // Common fields
        if (details.id) items.push({ label: 'ID', value: details.id });
        if (details.label) items.push({ label: 'Label', value: details.label });
        if (details.class_id) items.push({ label: 'Class ID', value: details.class_id });

        // Type-specific fields based on actual data structure
        if (details.class_type) items.push({ label: 'Class Type', value: details.class_type });
        if (details.status) items.push({ label: 'Status', value: details.status });

        // Financial observation fields
        if (details.account_name) items.push({ label: 'Account', value: details.account_name });
        if (details.amount !== undefined) items.push({ label: 'Amount', value: `${details.amount} ${details.currency || 'USD'}` });
        if (details.observation_type) items.push({ label: 'Observation Type', value: details.observation_type });
        if (details.period_start) items.push({ label: 'Period Start', value: details.period_start });
        if (details.period_end) items.push({ label: 'Period End', value: details.period_end });

        // Document fields
        if (details.filename) items.push({ label: 'Filename', value: details.filename });
        if (details.content_type) items.push({ label: 'Content Type', value: details.content_type });
        if (details.processing_status) items.push({ label: 'Processing Status', value: details.processing_status });
        if (details.file_size) items.push({ label: 'File Size', value: this.formatFileSize(details.file_size) });
        if (details.uploaded_by) items.push({ label: 'Uploaded By', value: details.uploaded_by });

        // Properties (for ontology classes)
        if (details.properties && typeof details.properties === 'object') {
            const propsStr = JSON.stringify(details.properties, null, 2);
            if (propsStr.length < 300) {
                items.push({ label: 'Properties', value: `<pre style="font-size: 0.8em; margin: 0;">${propsStr}</pre>` });
            }
        }

        // Metadata
        if (details.metadata && typeof details.metadata === 'object') {
            const metadataStr = JSON.stringify(details.metadata, null, 2);
            if (metadataStr.length < 300) {
                items.push({ label: 'Metadata', value: `<pre style="font-size: 0.8em; margin: 0;">${metadataStr}</pre>` });
            }
        }

        // Timestamps
        if (details.created_at) items.push({ label: 'Created', value: new Date(details.created_at).toLocaleString() });
        if (details.updated_at) items.push({ label: 'Updated', value: new Date(details.updated_at).toLocaleString() });

        return `
            <h4>Record Details</h4>
            ${items.map(item => `
                <div class="detail-item">
                    <span class="detail-label">${item.label}:</span>
                    <span class="detail-value">${item.value}</span>
                </div>
            `).join('')}
        `;
    }

    async sendRecordSpecificMessage() {
        const input = document.getElementById('recordChatInput');
        const message = input.value.trim();

        if (!message || !this.currentNodeData) return;

        const messagesContainer = document.getElementById('recordChatMessages');
        const sendButton = document.getElementById('recordChatSend');

        // Disable input while processing
        input.disabled = true;
        sendButton.disabled = true;

        // Add user message
        this.addRecordChatMessage('user', message);
        input.value = '';

        // Add loading message
        const loadingId = this.addRecordChatMessage('loading', 'Analyzing this record...');

        try {
            // Create context-aware message
            const contextMessage = `About ${this.currentNodeData.type} "${this.currentNodeData.label || this.currentNodeData.id}": ${message}`;

            const response = await fetch('/api/v1/crew/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: contextMessage,
                    user_id: 'dashboard_user',
                    context: {
                        node_data: this.currentNodeData,
                        record_specific: true
                    }
                })
            });

            const data = await response.json();

            // Remove loading message
            document.getElementById(loadingId).remove();

            if (data.success) {
                this.addRecordChatMessage('assistant', data.response);
            } else {
                this.addRecordChatMessage('assistant', 'Sorry, I encountered an error processing your question.');
            }

        } catch (error) {
            console.error('Error sending record-specific message:', error);
            document.getElementById(loadingId).remove();
            this.addRecordChatMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        } finally {
            input.disabled = false;
            sendButton.disabled = false;
            input.focus();
        }
    }

    addRecordChatMessage(type, content) {
        const messagesContainer = document.getElementById('recordChatMessages');
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = `chat-message ${type}`;
        messageDiv.textContent = content;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        return messageId;
    }

    closeNodeModal() {
        document.getElementById('nodeModal').style.display = 'none';
        this.currentNodeData = null;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(amount || 0);
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch {
            return dateString;
        }
    }

    exportTableData() {
        // Simple CSV export functionality
        alert('Export functionality would be implemented here');
    }

    // Widget System Methods
    setupWidgetEventListeners() {
        // Add widget button
        document.getElementById('add-widget-btn').addEventListener('click', () => {
            this.showWidgetModal();
        });

        // Widget modal close
        const widgetModal = document.getElementById('widgetModal');
        const widgetCloseBtn = widgetModal.querySelector('.modal-close');

        widgetCloseBtn.addEventListener('click', () => {
            this.closeWidgetModal();
        });

        widgetModal.addEventListener('click', (e) => {
            if (e.target === widgetModal) {
                this.closeWidgetModal();
            }
        });

        // Create widget button
        document.getElementById('createWidgetBtn').addEventListener('click', () => {
            this.createWidget();
        });
    }

    showWidgetModal() {
        document.getElementById('widgetModal').style.display = 'block';
        document.getElementById('widgetPrompt').focus();
    }

    closeWidgetModal() {
        document.getElementById('widgetModal').style.display = 'none';
        document.getElementById('widgetPrompt').value = '';
        document.getElementById('widgetSize').value = 'half';

        // Reset button state
        const createBtn = document.getElementById('createWidgetBtn');
        createBtn.innerHTML = '<i class="fas fa-magic"></i> Create Widget';
        createBtn.disabled = false;
    }

    async createWidget() {
        const prompt = document.getElementById('widgetPrompt').value.trim();
        const size = document.getElementById('widgetSize').value;
        const createBtn = document.getElementById('createWidgetBtn');
        const editId = createBtn.getAttribute('data-edit-id');

        if (!prompt) {
            alert('Please describe what you want to visualize.');
            return;
        }

        const originalText = createBtn.innerHTML;
        const isEditing = !!editId;
        createBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${isEditing ? 'Updating...' : 'Creating...'}`;
        createBtn.disabled = true;

        try {
            // Call the widget generation endpoint
            const response = await fetch('/api/v1/dashboard/widgets/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    size: size
                })
            });

            const data = await response.json();

            if (isEditing) {
                // Remove the old widget
                const oldWidget = this.widgets.find(w => w.id === editId);
                if (oldWidget) {
                    oldWidget.element.remove();
                    this.widgets = this.widgets.filter(w => w.id !== editId);
                }
            }

            // Add the new/updated widget with generated HTML
            const widgetHtml = data.success ? data.html : prompt;
            this.addWidgetToCanvas(prompt, size, widgetHtml);
            this.closeWidgetModal();

            // Reset modal state
            document.querySelector('#widgetModal .modal-header h3').textContent = 'Create Custom Widget';
            createBtn.removeAttribute('data-edit-id');

        } catch (error) {
            console.error('Error creating/updating widget:', error);
            alert(`Failed to ${isEditing ? 'update' : 'create'} widget. Please try again.`);
        } finally {
            createBtn.innerHTML = originalText;
            createBtn.disabled = false;
        }
    }

    addWidgetToCanvas(title, size, content) {
        const widgetId = `widget-${++this.widgetCounter}`;
        const canvas = document.getElementById('widget-canvas');

        // Hide placeholder if it exists and this is the first widget
        const placeholder = document.getElementById('widget-placeholder');
        if (placeholder && this.widgets.length === 0) {
            placeholder.style.display = 'none';
        }

        // Create widget element
        const widget = document.createElement('div');
        widget.className = `widget size-${size}`;
        widget.id = widgetId;
        widget.innerHTML = `
            <div class="widget-header">
                <h3 class="widget-title">${this.truncateTitle(title)}</h3>
                <div class="widget-actions">
                    <button class="widget-action" onclick="dashboard.refreshWidget('${widgetId}')" title="Refresh">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                    <button class="widget-action" onclick="dashboard.editWidget('${widgetId}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="widget-action" onclick="dashboard.removeWidget('${widgetId}')" title="Remove">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="widget-content" id="${widgetId}-content">
                <div class="widget-loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Generating widget...</span>
                </div>
            </div>
        `;

        canvas.appendChild(widget);

        // Store widget info
        this.widgets.push({
            id: widgetId,
            title: title,
            size: size,
            prompt: content,
            element: widget
        });

        // Process the AI response and render the widget
        setTimeout(() => {
            this.renderWidgetContent(widgetId, content);
        }, 1000);
    }

    truncateTitle(title) {
        return title.length > 50 ? title.substring(0, 47) + '...' : title;
    }

    async renderWidgetContent(widgetId, widgetHtml) {
        const contentContainer = document.getElementById(`${widgetId}-content`);

        try {
            // Check if we have generated HTML code
            if (this.containsCode(widgetHtml)) {
                await this.renderCustomWidget(contentContainer, widgetHtml, widgetId);
            } else {
                // Fallback to predefined widget types
                const widgetType = this.detectWidgetType(widgetHtml);

                switch (widgetType) {
                    case 'table':
                        await this.createTableWidget(contentContainer, widgetHtml);
                        break;
                    case 'chart':
                        await this.createChartWidget(contentContainer, widgetHtml);
                        break;
                    case 'kpi':
                        await this.createKPIWidget(contentContainer, widgetHtml);
                        break;
                    case 'spotlight':
                        await this.createSpotlightWidget(contentContainer, widgetHtml);
                        break;
                    default:
                        await this.createTextWidget(contentContainer, widgetHtml);
                }
            }
        } catch (error) {
            console.error('Error rendering widget:', error);
            contentContainer.innerHTML = `
                <div class="widget-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error rendering widget</p>
                    <button class="btn btn-sm btn-secondary" onclick="dashboard.refreshWidget('${widgetId}')">
                        Try Again
                    </button>
                </div>
            `;
        }
    }

    detectWidgetType(response) {
        const text = response.toLowerCase();

        if (text.includes('spotlight') || text.includes('biggest') || text.includes('highest') || text.includes('largest')) {
            return 'spotlight';
        } else if (text.includes('table') || text.includes('list') || text.includes('rows')) {
            return 'table';
        } else if (text.includes('chart') || text.includes('graph') || text.includes('plot')) {
            return 'chart';
        } else if (text.includes('kpi') || text.includes('metric') || text.includes('dashboard')) {
            return 'kpi';
        }

        return 'text';
    }

    containsCode(response) {
        return response.includes('<div') || response.includes('<script') || response.includes('function') || response.includes('fetch(') || response.includes('custom-');
    }

    async renderCustomWidget(container, code, widgetId) {
        // Render custom widget code from backend
        try {
            // Set the HTML content
            container.innerHTML = code;

            // Extract and execute JavaScript if present
            const scripts = container.querySelectorAll('script');
            scripts.forEach(script => {
                try {
                    // Create a new script element and execute it
                    const newScript = document.createElement('script');
                    newScript.textContent = script.textContent;
                    document.head.appendChild(newScript);
                    document.head.removeChild(newScript);
                } catch (jsError) {
                    console.error('Error executing widget script:', jsError);
                }
            });

            // Extract and apply CSS if present
            const styles = container.querySelectorAll('style');
            styles.forEach(style => {
                if (!document.head.querySelector(`style[data-widget="${widgetId}"]`)) {
                    const newStyle = document.createElement('style');
                    newStyle.textContent = style.textContent;
                    newStyle.setAttribute('data-widget', widgetId);
                    document.head.appendChild(newStyle);
                }
            });

        } catch (error) {
            console.error('Error executing custom widget code:', error);
            container.innerHTML = '<div class="widget-error"><i class="fas fa-exclamation-triangle"></i><p>Error executing custom widget</p></div>';
        }
    }

    async createTableWidget(container, aiResponse) {
        // Fetch recent financial observations for table
        try {
            const response = await fetch('/api/v1/dashboard/recent-observations');
            const data = await response.json();

            container.innerHTML = `
                <div class="widget-table-container">
                    <div class="table-header">
                        <span class="table-count">${data.observations.length} records</span>
                        <button class="btn btn-sm btn-outline" onclick="dashboard.exportTableData()">
                            <i class="fas fa-download"></i> Export
                        </button>
                    </div>
                    <div class="table-wrapper">
                        <table class="widget-table">
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Account</th>
                                    <th>Amount</th>
                                    <th>Currency</th>
                                    <th>Period</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.observations.map(obs => `
                                    <tr>
                                        <td><span class="type-badge type-${(obs.observation_type || 'unknown').replace(/[^a-z]/gi, '')}">${obs.observation_type || 'N/A'}</span></td>
                                        <td>${obs.account_name || 'N/A'}</td>
                                        <td class="amount-cell">${this.formatCurrency(obs.amount || 0, obs.currency)}</td>
                                        <td>${obs.currency || 'USD'}</td>
                                        <td>${this.formatDate(obs.period_start)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            container.innerHTML = '<div class="widget-error"><i class="fas fa-exclamation-triangle"></i><p>Error loading table data</p></div>';
        }
    }

    async createChartWidget(container, aiResponse) {
        try {
            const response = await fetch('/api/v1/dashboard/revenue-trends');
            const data = await response.json();

            const chartId = `chart-${Date.now()}`;
            container.innerHTML = `<div id="${chartId}" style="height: 300px;"></div>`;

            // Create a simple Plotly chart
            const trace = {
                x: data.periods,
                y: data.amounts,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Revenue',
                line: { color: '#2563eb' }
            };

            const layout = {
                title: 'Revenue Trends',
                xaxis: { title: 'Period' },
                yaxis: { title: 'Amount' },
                margin: { t: 40, r: 20, b: 40, l: 60 }
            };

            Plotly.newPlot(chartId, [trace], layout, { responsive: true });
        } catch (error) {
            container.innerHTML = '<p class="text-center text-danger">Error loading chart data</p>';
        }
    }

    async createKPIWidget(container, aiResponse) {
        try {
            const [statsResponse, revenueResponse] = await Promise.all([
                fetch('/api/v1/dashboard/stats'),
                fetch('/api/v1/dashboard/revenue-trends')
            ]);

            const stats = await statsResponse.json();
            const revenue = await revenueResponse.json();

            const totalRevenue = revenue.amounts.reduce((sum, amount) => sum + amount, 0);

            container.innerHTML = `
                <div class="kpi-grid">
                    <div class="kpi-card primary">
                        <div class="kpi-icon"><i class="fas fa-dollar-sign"></i></div>
                        <div class="kpi-content">
                            <div class="kpi-value">${this.formatCurrency(totalRevenue)}</div>
                            <div class="kpi-label">Total Revenue</div>
                            <div class="kpi-change positive">+12.5%</div>
                        </div>
                    </div>
                    <div class="kpi-card success">
                        <div class="kpi-icon"><i class="fas fa-file-alt"></i></div>
                        <div class="kpi-content">
                            <div class="kpi-value">${stats.documents}</div>
                            <div class="kpi-label">Documents</div>
                            <div class="kpi-change positive">+${stats.documents}</div>
                        </div>
                    </div>
                    <div class="kpi-card info">
                        <div class="kpi-icon"><i class="fas fa-chart-line"></i></div>
                        <div class="kpi-content">
                            <div class="kpi-value">${stats.observations}</div>
                            <div class="kpi-label">Observations</div>
                            <div class="kpi-change positive">+${stats.observations}</div>
                        </div>
                    </div>
                    <div class="kpi-card warning">
                        <div class="kpi-icon"><i class="fas fa-project-diagram"></i></div>
                        <div class="kpi-content">
                            <div class="kpi-value">${stats.ontology_classes}</div>
                            <div class="kpi-label">Ontology Classes</div>
                            <div class="kpi-change positive">+${stats.ontology_classes}</div>
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            container.innerHTML = '<div class="widget-error"><i class="fas fa-exclamation-triangle"></i><p>Error loading KPI data</p></div>';
        }
    }

    async createSpotlightWidget(container, aiResponse) {
        try {
            // Fetch financial observations and find the biggest value
            const response = await fetch('/api/v1/dashboard/recent-observations');
            const data = await response.json();

            // Find the observation with the highest amount
            const biggestObservation = data.observations.reduce((max, obs) => {
                const amount = parseFloat(obs.amount) || 0;
                const maxAmount = parseFloat(max.amount) || 0;
                return amount > maxAmount ? obs : max;
            }, data.observations[0] || {});

            container.innerHTML = `
                <div class="spotlight-widget">
                    <div class="spotlight-header">
                        <i class="fas fa-search-dollar"></i>
                        <h4>Biggest Value Spotlight</h4>
                    </div>
                    <div class="spotlight-content">
                        <div class="spotlight-main">
                            <div class="spotlight-amount">${this.formatCurrency(biggestObservation.amount, biggestObservation.currency)}</div>
                            <div class="spotlight-type">${biggestObservation.observation_type || 'Financial Observation'}</div>
                        </div>
                        <div class="spotlight-details">
                            <div class="detail-item">
                                <span class="detail-label">Account:</span>
                                <span class="detail-value">${biggestObservation.account_name || 'N/A'}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Period:</span>
                                <span class="detail-value">${this.formatDate(biggestObservation.period_start)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Currency:</span>
                                <span class="detail-value">${biggestObservation.currency || 'USD'}</span>
                            </div>
                        </div>
                        <div class="spotlight-insight">
                            <i class="fas fa-lightbulb"></i>
                            <p>This represents the highest single financial observation in your database.</p>
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            container.innerHTML = '<div class="widget-error"><i class="fas fa-exclamation-triangle"></i><p>Error loading spotlight data</p></div>';
        }
    }

    createTextWidget(container, aiResponse) {
        container.innerHTML = `
            <div class="text-widget">
                <div class="ai-response">
                    <i class="fas fa-robot"></i>
                    <h4>AI Response</h4>
                    <p>${aiResponse}</p>
                </div>
                <div class="widget-actions-bottom">
                    <button class="btn btn-sm btn-primary" onclick="dashboard.enhanceTextWidget('${container.id}', '${aiResponse.replace(/'/g, "\\'")}')">
                        <i class="fas fa-magic"></i> Enhance with Data
                    </button>
                </div>
            </div>
        `;
    }

    async enhanceTextWidget(containerId, originalPrompt) {
        const container = document.getElementById(containerId);
        container.innerHTML = '<div class="widget-loading"><i class="fas fa-spinner fa-spin"></i><span>Enhancing with data...</span></div>';

        try {
            // Call the AI agent to generate a proper data visualization
            const response = await fetch('/api/v1/crew/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: `Create a data visualization widget for: "${originalPrompt}". Generate HTML/CSS/JS code that fetches data from our financial database and creates an interactive visualization. Include proper error handling and responsive design. Use our existing API endpoints like /api/v1/dashboard/recent-observations, /api/v1/dashboard/stats, /api/v1/dashboard/revenue-trends.`,
                    user_id: 'dashboard_user',
                    context: {
                        widget_enhancement: true,
                        original_prompt: originalPrompt,
                        request_type: 'data_visualization',
                        available_endpoints: [
                            '/api/v1/dashboard/recent-observations',
                            '/api/v1/dashboard/stats',
                            '/api/v1/dashboard/revenue-trends'
                        ]
                    }
                })
            });

            const data = await response.json();

            if (data.success) {
                await this.renderCustomWidget(container, data.response, containerId);
            } else {
                throw new Error(data.error || 'Failed to enhance widget');
            }

        } catch (error) {
            console.error('Error enhancing widget:', error);
            container.innerHTML = `
                <div class="widget-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to enhance widget</p>
                    <button class="btn btn-sm btn-secondary" onclick="dashboard.createTextWidget(document.getElementById('${containerId}'), '${originalPrompt.replace(/'/g, "\\'")}')">
                        Revert
                    </button>
                </div>
            `;
        }
    }

    refreshWidget(widgetId) {
        const widget = this.widgets.find(w => w.id === widgetId);
        if (widget) {
            const contentContainer = document.getElementById(`${widgetId}-content`);
            contentContainer.innerHTML = '<div class="widget-loading"><i class="fas fa-spinner fa-spin"></i> Refreshing...</div>';

            setTimeout(() => {
                this.renderWidgetContent(widgetId, widget.prompt);
            }, 500);
        }
    }

    editWidget(widgetId) {
        const widget = this.widgets.find(w => w.id === widgetId);
        if (widget) {
            // Pre-fill the modal with current widget data
            document.getElementById('widgetPrompt').value = widget.title;
            document.getElementById('widgetSize').value = widget.size;

            // Change the modal title and button
            document.querySelector('#widgetModal .modal-header h3').textContent = 'Edit Widget';
            document.getElementById('createWidgetBtn').innerHTML = '<i class="fas fa-save"></i> Update Widget';
            document.getElementById('createWidgetBtn').setAttribute('data-edit-id', widgetId);

            this.showWidgetModal();
        }
    }

    removeWidget(widgetId) {
        const widget = this.widgets.find(w => w.id === widgetId);
        if (widget && confirm('Remove this widget?')) {
            widget.element.remove();
            this.widgets = this.widgets.filter(w => w.id !== widgetId);

            // Show placeholder if no widgets left
            if (this.widgets.length === 0) {
                const placeholder = document.getElementById('widget-placeholder');
                if (placeholder) {
                    placeholder.style.display = 'flex';
                }
            }
        }
    }
}

// Global functions for widget examples
function setWidgetExample(type) {
    const examples = {
        'revenue-chart': 'Create a line chart showing revenue trends over time',
        'expense-table': 'Show me a table of all expense categories with amounts',
        'kpi-cards': 'Display key performance indicators as cards (total documents, observations, classes)',
        'live-feed': 'Create a live feed of the most recent financial observations',
        'ontology-explorer': 'Show me a table of all ontology classes with their status and properties',
        'document-tracker': 'Create a widget showing document upload status and processing progress'
    };

    document.getElementById('widgetPrompt').value = examples[type] || '';

    // Auto-select appropriate size for different widget types
    const sizeMap = {
        'revenue-chart': 'half',
        'expense-table': 'full',
        'kpi-cards': 'full',
        'live-feed': 'half',
        'ontology-explorer': 'half',
        'document-tracker': 'quarter'
    };

    document.getElementById('widgetSize').value = sizeMap[type] || 'half';
}

function closeWidgetModal() {
    if (window.dashboard) {
        window.dashboard.closeWidgetModal();
    }
}

// Dedicated File Upload Functionality
class FileUploadManager {
    constructor() {
        this.uploadHistory = [];
        this.setupEventListeners();
    }

    setupEventListeners() {
        // File input change
        const fileInput = document.getElementById('dedicated-file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e.target.files);
            });
        }

        // Drag and drop
        const uploadZone = document.getElementById('upload-zone');
        if (uploadZone) {
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('dragover');
            });

            uploadZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
            });

            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
                this.handleFileSelection(e.dataTransfer.files);
            });
        }

        // Clear history button
        const clearBtn = document.getElementById('clear-upload-history-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearUploadHistory();
            });
        }
    }

    async handleFileSelection(files) {
        if (!files || files.length === 0) return;

        const fileArray = Array.from(files);
        console.log('📁 Files selected for upload:', fileArray.map(f => f.name));

        for (const file of fileArray) {
            await this.uploadFile(file);
        }
    }

    async uploadFile(file) {
        const uploadId = Date.now() + Math.random();

        // Get selected pipeline
        const selectedPipeline = document.querySelector('input[name="pipeline"]:checked')?.value || 'langextract';

        // Show progress
        this.showUploadProgress(file.name);

        // Create processing pipeline container in upload section
        const pipelineId = `pipeline-${Date.now()}`;
        this.createProcessingPipelineInUpload(pipelineId, file.name, selectedPipeline);

        // Add to history immediately
        const historyItem = {
            id: uploadId,
            filename: file.name,
            size: file.size,
            status: 'processing',
            timestamp: new Date(),
            entities: 0,
            pipeline: selectedPipeline
        };
        this.uploadHistory.unshift(historyItem);
        this.updateUploadHistory();

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('user_id', 'demo_user');
            formData.append('pipeline_type', selectedPipeline);

            console.log('🚀 Uploading file:', file.name, 'with pipeline:', selectedPipeline);

            // Choose endpoint based on selected pipeline
            const endpoints = {
                'langextract': '/api/v1/documents/process-langextract',
                'rag-anything': '/api/v1/documents/process-rag-anything',
                'agno': '/api/v1/documents/process-agno',
                'hybrid': '/api/v1/documents/process-hybrid'
            };

            const endpoint = endpoints[selectedPipeline] || '/api/v1/documents/ingest-rootfi';

            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            console.log('📊 Upload result:', result);

            if (response.ok && result.success) {
                // Update history item
                historyItem.status = 'success';
                historyItem.entities = result.ontology_classes_extracted || 0;
                historyItem.documentId = result.document_id;
                historyItem.processingTime = result.processing_results?.processing_time || 0;

                this.hideUploadProgress();
                this.updateUploadHistory();

                // Refresh dashboard data
                if (window.dashboard) {
                    window.dashboard.loadDashboardData();
                }

                console.log('✅ File uploaded successfully:', file.name);
            } else {
                throw new Error(result.error || result.message || 'Upload failed');
            }
        } catch (error) {
            console.error('❌ Upload error:', error);

            // Update history item
            historyItem.status = 'error';
            historyItem.error = error.message;

            this.hideUploadProgress();
            this.updateUploadHistory();
        }
    }

    showUploadProgress(filename) {
        const progressSection = document.getElementById('upload-progress-section');
        const statusElement = document.getElementById('upload-status');
        const progressBar = document.getElementById('upload-progress-bar');

        if (progressSection && statusElement && progressBar) {
            progressSection.classList.remove('hidden');
            statusElement.textContent = `Processing ${filename} with LangExtract AI...`;
            progressBar.style.width = '100%';
        }
    }

    hideUploadProgress() {
        const progressSection = document.getElementById('upload-progress-section');
        if (progressSection) {
            progressSection.classList.add('hidden');
        }
    }

    updateUploadHistory() {
        const resultsList = document.getElementById('upload-results-list');
        if (!resultsList) return;

        if (this.uploadHistory.length === 0) {
            resultsList.innerHTML = '<p class="text-muted">No files uploaded yet</p>';
            return;
        }

        resultsList.innerHTML = this.uploadHistory.map(item => `
            <div class="upload-result-item">
                <div class="upload-result-info">
                    <div class="upload-result-filename">${item.filename}</div>
                    <div class="upload-result-details">
                        ${this.formatFileSize(item.size)} •
                        ${item.entities} entities extracted •
                        ${item.timestamp.toLocaleTimeString()}
                        ${item.processingTime ? ` • ${item.processingTime.toFixed(2)}s` : ''}
                    </div>
                </div>
                <div class="upload-result-status ${item.status}">
                    ${item.status === 'success' ? '✅ Success' :
                      item.status === 'error' ? '❌ Error' :
                      '⏳ Processing'}
                </div>
            </div>
        `).join('');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    clearUploadHistory() {
        this.uploadHistory = [];
        this.updateUploadHistory();
    }

    // Agno Integration Methods
    shouldUseAgno(message) {
        const agnoKeywords = [
            'reasoning', 'analyze', 'step by step', 'explain', 'why', 'how',
            'reasoning tools', 'multi-modal', 'interface', 'visualization',
            'ontology', 'document analysis', 'confidence', 'score'
        ];

        const messageLower = message.toLowerCase();
        return agnoKeywords.some(keyword => messageLower.includes(keyword));
    }

    async handleAgnoCommand(command) {
        const cmd = command.toLowerCase();

        if (cmd === '/reasoning on') {
            this.agnoReasoningEnabled = true;
            this.addMessageToChat('ai', `
                <div class="system-message">
                    ✅ <strong>Agno reasoning mode enabled.</strong><br>
                    I will show step-by-step analysis for complex queries.
                </div>
            `);
        } else if (cmd === '/reasoning off') {
            this.agnoReasoningEnabled = false;
            this.addMessageToChat('ai', `
                <div class="system-message">
                    ⚡ <strong>Reasoning mode disabled.</strong><br>
                    Responses will be faster but less detailed.
                </div>
            `);
        } else if (cmd === '/demo') {
            await this.runAgnoDemo();
        } else if (cmd === '/interface') {
            this.addMessageToChat('ai', `
                <div class="system-message">
                    🎨 <strong>Interface creation mode enabled.</strong><br>
                    Describe what you want to build and I'll generate the code.
                </div>
            `);
        } else if (cmd === '/upload') {
            document.getElementById('file-upload-input').click();
        } else if (cmd === '/agno-status') {
            await this.checkAgnoStatus();
        } else {
            this.addMessageToChat('ai', `
                <div class="system-message">
                    <strong>Unknown command:</strong> ${command}<br><br>
                    <strong>Available Agno commands:</strong><br>
                    • <code>/reasoning on/off</code> - Toggle reasoning mode<br>
                    • <code>/demo</code> - Run Agno reasoning demonstration<br>
                    • <code>/interface</code> - Enable interface creation<br>
                    • <code>/upload</code> - Upload documents<br>
                    • <code>/agno-status</code> - Check Agno system status
                </div>
            `);
        }
    }

    async runAgnoDemo() {
        this.addMessageToChat('ai', `
            <div class="system-message">
                🧠 <strong>Running Agno reasoning demonstration...</strong>
            </div>
        `);

        try {
            const response = await fetch('/api/v1/agno/reasoning-demo');
            const result = await response.json();

            if (result.success) {
                this.addMessageToChat('ai', `
                    <div class="agno-demo-response">
                        <div class="framework-badge agno-badge">🧠 Agno Reasoning Demo</div>
                        <div class="demo-content">${result.demo_response}</div>
                        <div class="demo-capabilities">
                            <strong>Capabilities demonstrated:</strong>
                            <ul>
                                ${result.capabilities_shown?.map(cap => `<li>${cap}</li>`).join('') || ''}
                            </ul>
                        </div>
                    </div>
                `);
            } else {
                this.addMessageToChat('ai', `
                    <div class="error-response">
                        Demo failed to run. Please check system status.
                    </div>
                `);
            }
        } catch (error) {
            this.addMessageToChat('ai', `
                <div class="error-response">
                    Demo connection error: ${error.message}
                </div>
            `);
            console.error('Demo error:', error);
        }
    }

    async checkAgnoStatus() {
        try {
            const response = await fetch('/api/v1/agno/health');
            const result = await response.json();

            if (result.success) {
                const components = result.components || {};
                const status = `
                    <div class="agno-status-response">
                        <div class="framework-badge agno-badge">🧠 Agno System Status</div>

                        <div class="status-grid">
                            <div class="status-item">
                                <strong>Framework:</strong> ${components.agno_system?.agno_version || 'Unknown'}
                            </div>
                            <div class="status-item">
                                <strong>Status:</strong> ${result.status}
                            </div>
                            <div class="status-item">
                                <strong>Reasoning:</strong> ${result.reasoning_available ? '✅ Available' : '❌ Unavailable'}
                            </div>
                            <div class="status-item">
                                <strong>Ontology Specialist:</strong> ${result.ontology_specialist_ready ? '✅ Ready' : '❌ Not Ready'}
                            </div>
                            <div class="status-item">
                                <strong>Reasoning Engine:</strong> ${result.reasoning_engine_ready ? '✅ Ready' : '❌ Not Ready'}
                            </div>
                        </div>

                        <div class="capabilities-list">
                            <strong>Available Capabilities:</strong>
                            <ul>
                                ${result.capabilities?.map(cap => `<li>${cap}</li>`).join('') || '<li>None listed</li>'}
                            </ul>
                        </div>
                    </div>
                `;

                this.addMessageToChat('ai', status);
            } else {
                this.addMessageToChat('ai', `
                    <div class="error-response">
                        ❌ Agno system unhealthy: ${result.error}
                    </div>
                `);
            }
        } catch (error) {
            this.addMessageToChat('ai', `
                <div class="error-response">
                    ❌ Could not check Agno status: ${error.message}
                </div>
            `);
        }
    }

    createProcessingPipelineInUpload(pipelineId, filename, selectedPipeline = 'langextract') {
        const uploadResultsList = document.getElementById('upload-results-list');

        // Clear "No files uploaded yet" message
        if (uploadResultsList.querySelector('.text-muted')) {
            uploadResultsList.innerHTML = '';
        }

        // Get pipeline configuration
        const pipelineConfig = this.getPipelineConfig(selectedPipeline);

        const pipelineHtml = `
            <div id="${pipelineId}" class="pipeline-container">
                <div class="pipeline-header">
                    <h4>${pipelineConfig.icon} Processing: ${filename}</h4>
                    <div class="pipeline-info">
                        <span class="pipeline-name">${pipelineConfig.name}</span>
                        <span class="pipeline-status">⏳ Initializing...</span>
                    </div>
                </div>

                <div class="pipeline-steps">
                    ${pipelineConfig.steps.map((step, index) => `
                        <div id="${pipelineId}-step-${index + 1}" class="step">
                            <div class="step-icon">⏳</div>
                            <div class="step-content">
                                <div class="step-title">${step.title}</div>
                                <div class="step-details">${index === 0 ? 'Preparing for processing...' : 'Waiting for previous step...'}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <div class="pipeline-logs">
                    <div class="logs-header">📋 Processing Logs</div>
                    <div class="logs-content" id="${pipelineId}-logs">
                        <div class="log-entry">🚀 Pipeline initialized for ${filename}</div>
                    </div>
                </div>
            </div>
        `;

        uploadResultsList.insertAdjacentHTML('afterbegin', pipelineHtml);

        // Start the simulation
        setTimeout(() => {
            this.simulateProcessingStepsInUpload(pipelineId, selectedPipeline);
        }, 500);
    }

    async simulateProcessingStepsInUpload(pipelineId, selectedPipeline = 'langextract') {
        const pipelineConfig = this.getPipelineConfig(selectedPipeline);
        const steps = this.generatePipelineSteps(selectedPipeline, pipelineConfig);

        for (const step of steps) {
            await this.processStepInUpload(pipelineId, step);
        }

        // Complete the pipeline
        this.updatePipelineCompleteInUpload(pipelineId, {
            confidence_score: 0.94,
            processing_time: '3.2s',
            response: 'Document processed successfully! Extracted 23 financial entities with 89% average confidence. Ready for analysis and insights generation.'
        });
    }

    async processStepInUpload(pipelineId, step) {
        // Update step status to processing
        const stepElement = document.getElementById(`${pipelineId}-step-${step.id}`);
        const logsElement = document.getElementById(`${pipelineId}-logs`);

        stepElement.querySelector('.step-icon').textContent = '🔄';
        stepElement.classList.add('processing');

        // Add logs progressively
        for (const log of step.logs) {
            await new Promise(resolve => setTimeout(resolve, step.duration / step.logs.length));
            logsElement.insertAdjacentHTML('beforeend', `<div class="log-entry">${log}</div>`);
            logsElement.scrollTop = logsElement.scrollHeight;
        }

        // Complete step
        await new Promise(resolve => setTimeout(resolve, 200));
        stepElement.querySelector('.step-icon').textContent = step.success ? '✅' : '❌';
        stepElement.querySelector('.step-details').textContent = step.details;
        stepElement.classList.remove('processing');
        stepElement.classList.add(step.success ? 'completed' : 'failed');
    }

    updatePipelineCompleteInUpload(pipelineId, result) {
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
                    <button class="btn-secondary" onclick="dashboard.reviewPipeline('${pipelineId}')">🔍 Review Pipeline</button>
                    <button class="btn-secondary" onclick="dashboard.improvePipeline('${pipelineId}')">⚡ Improve Pipeline</button>
                    <button class="btn-primary" onclick="dashboard.acceptResults('${pipelineId}')">✅ Accept Results</button>
                </div>
            </div>
        `;

        pipelineElement.insertAdjacentHTML('beforeend', resultsHtml);
        logsElement.scrollTop = logsElement.scrollHeight;
    }

    // Pipeline action methods
    reviewPipeline(pipelineId) {
        alert('🔍 Pipeline Review: Analyzing performance and identifying optimization opportunities...');
    }

    improvePipeline(pipelineId) {
        alert('⚡ Pipeline Improvement: Suggested improvements include increasing confidence threshold and adding custom financial domain rules.');
    }

    acceptResults(pipelineId) {
        alert('✅ Results Accepted: Pipeline results have been accepted and saved to the knowledge base.');
    }

    getPipelineConfig(pipelineType) {
        const configs = {
            'langextract': {
                name: 'LangExtract',
                icon: '🧠',
                description: 'Google\'s advanced entity extraction',
                steps: [
                    {
                        title: 'Document Upload & Validation',
                        description: 'Validating file format and preparing for LangExtract processing'
                    },
                    {
                        title: 'LangExtract Entity Recognition',
                        description: 'Using Google\'s LangExtract for advanced entity detection'
                    },
                    {
                        title: 'Ontology Mapping & Classification',
                        description: 'Mapping entities to financial ontology classes'
                    },
                    {
                        title: 'Confidence Scoring & Validation',
                        description: 'Calculating confidence scores and validating results'
                    },
                    {
                        title: 'Knowledge Base Integration',
                        description: 'Storing results in the financial knowledge base'
                    }
                ]
            },
            'rag-anything': {
                name: 'RAG-Anything',
                icon: '🔍',
                description: 'Advanced RAG system for any data type',
                steps: [
                    {
                        title: 'Multi-Modal Data Analysis',
                        description: 'Analyzing document structure and content patterns'
                    },
                    {
                        title: 'RAG Vector Embedding',
                        description: 'Creating high-dimensional embeddings for retrieval'
                    },
                    {
                        title: 'Context Retrieval & Matching',
                        description: 'Finding relevant context and similar patterns'
                    },
                    {
                        title: 'Pattern Recognition & Classification',
                        description: 'Identifying financial patterns and data structures'
                    },
                    {
                        title: 'Insight Generation & Recommendations',
                        description: 'Generating actionable insights from RAG analysis'
                    }
                ]
            },
            'agno': {
                name: 'Agno AGI',
                icon: '⚡',
                description: 'Reasoning-based document analysis',
                steps: [
                    {
                        title: 'Reasoning Engine Initialization',
                        description: 'Starting Agno\'s multi-step reasoning process'
                    },
                    {
                        title: 'Step-by-Step Document Analysis',
                        description: 'Breaking down document into logical components'
                    },
                    {
                        title: 'Financial Domain Reasoning',
                        description: 'Applying financial domain knowledge and rules'
                    },
                    {
                        title: 'Insight Synthesis & Validation',
                        description: 'Synthesizing insights and validating reasoning chains'
                    },
                    {
                        title: 'Strategic Recommendations',
                        description: 'Generating strategic recommendations based on analysis'
                    }
                ]
            },
            'hybrid': {
                name: 'Hybrid Pipeline',
                icon: '🚀',
                description: 'Combines multiple tools for best results',
                steps: [
                    {
                        title: 'Multi-Tool Initialization',
                        description: 'Preparing LangExtract, RAG-Anything, and Agno pipelines'
                    },
                    {
                        title: 'Parallel Processing',
                        description: 'Running multiple analysis tools simultaneously'
                    },
                    {
                        title: 'Cross-Validation & Comparison',
                        description: 'Comparing results across different tools'
                    },
                    {
                        title: 'Consensus Building & Scoring',
                        description: 'Building consensus and calculating aggregate scores'
                    },
                    {
                        title: 'Best Results Synthesis',
                        description: 'Synthesizing the best insights from all tools'
                    }
                ]
            }
        };

        return configs[pipelineType] || configs['langextract'];
    }

    generatePipelineSteps(pipelineType, config) {
        const baseSteps = {
            'langextract': [
                {
                    id: 1,
                    duration: 1000,
                    success: true,
                    details: "✅ File validated and prepared for LangExtract processing.",
                    logs: ["📤 File upload initiated", "🔍 Format validation: JSON detected", "✅ File size within limits", "🧠 LangExtract engine ready"]
                },
                {
                    id: 2,
                    duration: 2000,
                    success: true,
                    details: "✅ LangExtract identified 23 entities with 94% confidence.",
                    logs: ["🧠 LangExtract engine started", "🔍 Advanced entity recognition", "🏢 Company entities: 5 found", "💵 Financial metrics: 12 identified", "📈 Performance indicators: 6 detected"]
                },
                {
                    id: 3,
                    duration: 1500,
                    success: true,
                    details: "✅ Entities mapped to financial ontology classes.",
                    logs: ["🗂️ Ontology mapping initiated", "🔗 Class relationships established", "📊 Confidence scoring calculated", "✅ 18/23 entities mapped successfully"]
                },
                {
                    id: 4,
                    duration: 1200,
                    success: true,
                    details: "✅ Confidence scores validated and results verified.",
                    logs: ["📊 Confidence validation started", "🎯 Score normalization", "✅ Quality assurance passed", "📋 Results verified"]
                },
                {
                    id: 5,
                    duration: 800,
                    success: true,
                    details: "✅ Results integrated into knowledge base.",
                    logs: ["💾 Knowledge base integration", "🔗 Entity linking", "📊 Index updating", "✅ Integration complete"]
                }
            ],
            'rag-anything': [
                {
                    id: 1,
                    duration: 1200,
                    success: true,
                    details: "✅ Multi-modal analysis completed for document structure.",
                    logs: ["🔍 Multi-modal analysis started", "📊 Document structure analysis", "🏗️ Content pattern recognition", "✅ Structure mapping complete"]
                },
                {
                    id: 2,
                    duration: 2500,
                    success: true,
                    details: "✅ High-dimensional embeddings created for RAG retrieval.",
                    logs: ["🧮 Vector embedding started", "📐 High-dimensional space mapping", "🔗 Semantic relationships", "✅ Embeddings generated"]
                },
                {
                    id: 3,
                    duration: 2000,
                    success: true,
                    details: "✅ Context retrieval found 47 relevant patterns.",
                    logs: ["🔍 Context retrieval initiated", "📊 Pattern matching", "🎯 Relevance scoring", "✅ 47 patterns identified"]
                },
                {
                    id: 4,
                    duration: 1800,
                    success: true,
                    details: "✅ Financial patterns classified with 91% accuracy.",
                    logs: ["🏷️ Pattern classification", "💰 Financial pattern recognition", "📈 Accuracy validation", "✅ Classification complete"]
                },
                {
                    id: 5,
                    duration: 1500,
                    success: true,
                    details: "✅ RAG-based insights and recommendations generated.",
                    logs: ["💡 Insight generation", "🎯 Recommendation synthesis", "📋 Report compilation", "✅ RAG analysis complete"]
                }
            ],
            'agno': [
                {
                    id: 1,
                    duration: 1500,
                    success: true,
                    details: "✅ Agno reasoning engine initialized and ready.",
                    logs: ["⚡ Agno engine startup", "🧠 Reasoning modules loaded", "🔧 Domain knowledge activated", "✅ Engine ready"]
                },
                {
                    id: 2,
                    duration: 3000,
                    success: true,
                    details: "✅ Step-by-step analysis completed with reasoning chains.",
                    logs: ["🔍 Document decomposition", "🧠 Logical reasoning chains", "📊 Component analysis", "🔗 Relationship mapping", "✅ Analysis complete"]
                },
                {
                    id: 3,
                    duration: 2200,
                    success: true,
                    details: "✅ Financial domain reasoning applied successfully.",
                    logs: ["💰 Financial domain rules", "📈 Market context analysis", "🏢 Business logic application", "✅ Domain reasoning complete"]
                },
                {
                    id: 4,
                    duration: 1800,
                    success: true,
                    details: "✅ Insights synthesized and reasoning validated.",
                    logs: ["💡 Insight synthesis", "🔍 Reasoning validation", "📊 Logic verification", "✅ Synthesis complete"]
                },
                {
                    id: 5,
                    duration: 1400,
                    success: true,
                    details: "✅ Strategic recommendations generated with reasoning.",
                    logs: ["🎯 Strategic analysis", "📋 Recommendation formulation", "🧠 Reasoning documentation", "✅ Recommendations ready"]
                }
            ],
            'hybrid': [
                {
                    id: 1,
                    duration: 2000,
                    success: true,
                    details: "✅ All processing tools initialized successfully.",
                    logs: ["🧠 LangExtract ready", "🔍 RAG-Anything ready", "⚡ Agno ready", "🚀 Hybrid mode activated"]
                },
                {
                    id: 2,
                    duration: 4000,
                    success: true,
                    details: "✅ Parallel processing completed across all tools.",
                    logs: ["🔄 Parallel processing started", "🧠 LangExtract processing...", "🔍 RAG-Anything processing...", "⚡ Agno processing...", "✅ All tools completed"]
                },
                {
                    id: 3,
                    duration: 2500,
                    success: true,
                    details: "✅ Cross-validation shows 96% consensus across tools.",
                    logs: ["📊 Result comparison", "🔍 Cross-validation", "📈 Consensus calculation", "✅ 96% agreement achieved"]
                },
                {
                    id: 4,
                    duration: 1800,
                    success: true,
                    details: "✅ Consensus built with weighted scoring system.",
                    logs: ["⚖️ Weighted scoring", "📊 Consensus building", "🎯 Score aggregation", "✅ Final scores calculated"]
                },
                {
                    id: 5,
                    duration: 1200,
                    success: true,
                    details: "✅ Best insights synthesized from all processing tools.",
                    logs: ["🏆 Best results selection", "💡 Insight synthesis", "📋 Final report", "✅ Hybrid processing complete"]
                }
            ]
        };

        return baseSteps[pipelineType] || baseSteps['langextract'];
    }
}

// Initialize dashboard
const dashboard = new KudwaDashboard();
window.dashboard = dashboard; // Make it globally accessible

// Make bulk approve function globally accessible
window.bulkApproveAll = function() {
    dashboard.bulkApproveAll();
};

// Initialize file upload manager
const fileUploadManager = new FileUploadManager();
window.fileUploadManager = fileUploadManager;
