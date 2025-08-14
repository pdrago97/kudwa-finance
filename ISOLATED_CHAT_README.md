# 🧠 Kudwa - Isolated Chat Dashboard

A clean, modern interface with separate chat workflows that connect directly to your N8N automation workflows.

## 🎯 Overview

This dashboard provides a single, minimal chat interface focused on Ontology Extension. Uploads are optional; you can also just start chatting. It connects directly to your N8N webhook for processing.

## 🚀 Quick Start

1. **Start the dashboard:**
   ```bash
   python start_isolated_dashboard.py
   ```

2. **Open in browser:**
   ```
   http://localhost:8051
   ```

## ⚙️ N8N Webhook Configuration

### Step 1: Set Environment Variables

Create a `.env` file or set environment variables:

```bash
# Ontology Extension Webhook
export N8N_ONTOLOGY_WEBHOOK="https://your-n8n-instance.com/webhook/ontology-extension-id"

# Data Registration Webhook  
export N8N_REGISTRATION_WEBHOOK="https://your-n8n-instance.com/webhook/data-registration-id"

# Optional: N8N instance configuration
export N8N_BASE_URL="https://your-n8n-instance.com"
export N8N_API_KEY="your-api-key-if-needed"
export N8N_TIMEOUT="30"
```

### Step 2: Configure N8N Workflows

Each N8N workflow should expect this payload structure:

```json
{
  "workflow_type": "ontology_extension",
  "filename": "document.json",
  "file_content": "base64_encoded_content",
  "message": "user_chat_message",
  "timestamp": "2024-01-15T10:30:00Z",
  "session_id": "uuid-string"
}
```

## 🎨 Features

### 🧠 Ontology Extension Chat
- **Purpose**: Extend and adapt ontology based on new documents
- **Use Cases**:
  - Upload financial reports to extend ontology
  - Chat about ontology structure requirements
  - Request new entity types or relationships
- **N8N Integration**: Sends data to `N8N_ONTOLOGY_WEBHOOK`

### 📝 Data Registration Chat  
- **Purpose**: Create new records from documents + RAG + instructions
- **Use Cases**:
  - Upload invoices to create transaction records
  - Process contracts to extract key data
  - Convert unstructured data to structured records
- **N8N Integration**: Sends data to `N8N_REGISTRATION_WEBHOOK`

### 🔄 Workflow Features
- **File Upload**: Drag & drop or click to upload documents
- **Chat Context**: Persistent chat history per workflow
- **Real-time Status**: Visual feedback on N8N webhook responses
- **Error Handling**: Retry logic and error display
- **Session Management**: Unique session IDs for tracking

## 🛠️ Technical Details

### File Structure
```
├── isolated_chat_dashboard.py    # Main dashboard application
├── n8n_config.py                # N8N webhook configuration
├── start_isolated_dashboard.py  # Startup script
└── ISOLATED_CHAT_README.md      # This file
```

### Dependencies
```bash
pip install dash dash-bootstrap-components requests python-dotenv
```

### Webhook Response Format
N8N webhooks should return:
```json
{
  "success": true,
  "message": "Workflow triggered successfully",
  "workflow_id": "workflow-execution-id",
  "data": {
    // Any additional response data
  }
}
```

## 🎯 Example N8N Workflows

### Ontology Extension Workflow
1. **Webhook Trigger** - Receives file + chat context
2. **File Analysis** - Extract entities, relationships, patterns
3. **Ontology Comparison** - Compare with existing ontology
4. **Proposal Generation** - Generate extension proposals
5. **Human Validation** - Send proposals for approval
6. **Ontology Update** - Apply approved changes

### Data Registration Workflow  
1. **Webhook Trigger** - Receives document + instructions
2. **Document Processing** - Extract structured data
3. **RAG Analysis** - Enhance with context from knowledge base
4. **Record Creation** - Generate structured records
5. **Validation** - Quality checks and validation
6. **Database Storage** - Store in Supabase/database

## 🔧 Customization

### Adding New Workflow Types (future)
Currently we keep a single chat. To add more later: extend `n8n_config.py` and add a new chat block + callbacks.

### Styling
The dashboard uses Bootstrap components with custom colors:
- **Ontology Extension**: Purple (`#6f42c1`)

## 🐛 Troubleshooting

### Common Issues

1. **Webhook not configured**
   - Check environment variables are set
   - Verify N8N webhook URLs are correct

2. **Connection timeout**
   - Increase `N8N_TIMEOUT` environment variable
   - Check N8N instance is accessible

3. **File upload errors**
   - Check file size limits
   - Verify file format is supported

### Debug Mode
Run with debug logging:
```bash
DEBUG=1 python start_isolated_dashboard.py
```

## 📊 Monitoring

The dashboard provides real-time status indicators:
- **Connection Status**: Shows N8N connectivity
- **Workflow Status**: Success/error feedback
- **Processing Stats**: Records processed, validation rates

## 🔐 Security

- File uploads are base64 encoded for safe transmission
- Session IDs provide request tracking
- Environment variables keep webhook URLs secure
- No sensitive data stored in browser

## 🚀 Next Steps

1. Configure your N8N webhooks
2. Test with sample documents
3. Build custom workflows for your use cases
4. Monitor and optimize performance

---

**Need help?** Check the configuration with:
```bash
python n8n_config.py
```
