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
            const data = await response.json();
            
            document.getElementById('total-documents').textContent = data.documents || 0;
            document.getElementById('total-ontology-classes').textContent = data.ontology_classes || 0;
            document.getElementById('total-observations').textContent = data.observations || 0;
            document.getElementById('total-datasets').textContent = data.datasets || 0;

            // Load charts
            this.loadRevenueChart();
            this.loadExpenseChart();
            this.loadRecentObservations();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
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
            const data = await response.json();
            
            const tbody = document.getElementById('ontology-classes');
            tbody.innerHTML = '';

            if (data.classes && data.classes.length > 0) {
                data.classes.forEach(cls => {
                    const row = document.createElement('tr');
                    const statusBadge = cls.status === 'pending_review' ? 'warning' : 'success';
                    row.innerHTML = `
                        <td><code>${cls.class_id}</code></td>
                        <td>${cls.label}</td>
                        <td>${cls.class_type}</td>
                        <td><span class="badge badge-${statusBadge}">${cls.status}</span></td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="dashboard.approveOntologyClass('${cls.id}')">
                                <i class="fas fa-check"></i>
                            </button>
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

            const response = await fetch('/api/v1/crew/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: 'demo_user'
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
            formData.append('user_id', 'demo_user');

            try {
                this.addMessageToChat('user', `Uploading ${file.name}...`, true);
                
                const response = await fetch('/api/v1/documents/ingest-rootfi', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (response.ok) {
                    this.addMessageToChat('ai', `✅ Successfully processed ${file.name}. The document has been analyzed and added to your knowledge base.`);
                } else {
                    this.addMessageToChat('ai', `❌ Error processing ${file.name}: ${result.detail || 'Unknown error'}`);
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
            const response = await fetch('/api/v1/admin/wipe-database', {
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
            const response = await fetch(`/api/v1/dashboard/ontology/classes/${classId}/approve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                this.loadOntologyData();
                // Also refresh approvals if we're on that page
                if (this.currentSection === 'approvals') {
                    this.loadApprovals();
                }
            } else {
                alert('Error approving ontology class. Please try again.');
            }
        } catch (error) {
            console.error('Error approving ontology class:', error);
            alert('Error approving ontology class. Please try again.');
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
            const data = await response.json();

            const tbody = document.getElementById('documents-list');
            tbody.innerHTML = '';

            if (!data.documents || data.documents.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No documents found</td></tr>';
                return;
            }

            data.documents.forEach(doc => {
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
            const response = await fetch('/api/v1/dashboard/approvals');
            const data = await response.json();

            const container = document.getElementById('approval-items');
            if (!container) {
                console.error('Approval items container not found');
                return;
            }

            if (!data.approvals || data.approvals.length === 0) {
                container.innerHTML = '<p class="text-center text-secondary">No pending approvals</p>';
                return;
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
                        ${approval.details ? `<details><summary>Details</summary><pre>${JSON.stringify(approval.details, null, 2)}</pre></details>` : ''}
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

            // Update count
            const countEl = document.getElementById('pending-count');
            if (countEl) {
                countEl.textContent = `${data.approvals.length} pending`;
            }

        } catch (error) {
            console.error('Error loading approvals:', error);
            const container = document.getElementById('approval-items');
            if (container) {
                container.innerHTML = '<p class="text-center text-danger">Error loading approvals</p>';
            }
        }
    }

    async loadKnowledgeGraph() {
        try {
            console.log('Loading knowledge graph...');
            const response = await fetch('/api/v1/dashboard/knowledge-graph');
            const data = await response.json();

            console.log('Knowledge graph data received:', {
                elements: data.elements?.length || 0,
                stats: data.stats
            });

            if (!data.elements || data.elements.length === 0) {
                console.warn('Knowledge graph returned no elements', data);
                // Show a message in the graph container
                const container = document.getElementById('knowledge-graph');
                container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">No graph data available. Upload documents to see relationships.</div>';
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

        console.log('Rendering knowledge graph with', data.elements?.length, 'elements');

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
        this.cy.add(data.elements || []);

        console.log('Added elements to graph:', {
            nodes: this.cy.nodes().length,
            edges: this.cy.edges().length
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

// Initialize dashboard
const dashboard = new KudwaDashboard();
window.dashboard = dashboard; // Make it globally accessible
