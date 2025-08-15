# 🤖 Kudwa CrewAI System

A robust, AI-powered financial data processing system built with CrewAI agents and advanced RAG capabilities.

## 🌟 Features

### 🚀 CrewAI-Powered Agent Framework
- **Document Processing Agent**: Intelligent parsing and entity extraction from financial documents
- **Ontology Management Agent**: Dynamic ontology extension and validation with human-in-the-loop
- **RAG Specialist Agent**: Advanced semantic search and knowledge retrieval
- **Financial Analysis Agent**: Specialized financial data analysis and insights generation

### 🕸️ Advanced Knowledge Graph
- **Dynamic Graph Generation**: Real-time knowledge graph construction from your data
- **Semantic Relationships**: AI-powered relationship discovery between entities
- **Interactive Visualizations**: Beautiful, interactive graph visualizations using pyvis
- **Multi-layered Architecture**: Ontology schema + actual data instances + semantic connections

### 🔍 Intelligent RAG System
- **Semantic Search**: Natural language queries across all your financial data
- **Vector Embeddings**: High-quality embeddings using sentence-transformers
- **FAISS Integration**: Fast similarity search with optimized indexing
- **Context-Aware Responses**: Agents provide responses with full context and confidence scores

### 💬 Smart Chat Interface
- **Multi-Agent Collaboration**: Different agents handle different types of queries
- **Financial Domain Expertise**: Specialized understanding of financial concepts and relationships
- **Human-in-the-Loop**: Approval workflows for ontology extensions and critical operations
- **Real-time Processing**: Live document processing and graph updates

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kudwa CrewAI System                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend: CrewAI Dashboard (Dash + Plotly)                │
├─────────────────────────────────────────────────────────────┤
│  API Layer: FastAPI with CrewAI Endpoints                  │
├─────────────────────────────────────────────────────────────┤
│  Agent Layer: CrewAI Agents                                │
│  ├── Document Processing Agent                             │
│  ├── Ontology Management Agent                             │
│  ├── RAG Specialist Agent                                  │
│  └── Financial Analysis Agent                              │
├─────────────────────────────────────────────────────────────┤
│  Knowledge Layer: RAG + Graph Management                   │
│  ├── Vector Embeddings (FAISS)                            │
│  ├── Knowledge Graph (NetworkX)                           │
│  └── Semantic Search Engine                               │
├─────────────────────────────────────────────────────────────┤
│  Data Layer: Supabase                                      │
│  ├── Ontology Classes & Relations                         │
│  ├── Financial Data & Observations                        │
│  ├── Document Storage                                      │
│  └── Vector Embeddings                                     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Supabase Account and API Keys

### 1. Clone and Setup
```bash
git clone <your-repo>
cd Kudwa
```

### 2. Start the System
```bash
./start_crew_ai.sh
```

This script will:
- Create virtual environment if needed
- Install all dependencies
- Check environment variables
- Start FastAPI server
- Launch CrewAI dashboard
- Initialize vector index

### 3. Access the System
- **Dashboard**: http://localhost:8051
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **CrewAI Chat**: http://localhost:8000/api/v1/crew/chat

## 📊 Usage Examples

### Document Upload and Processing
```python
# Upload a financial document
files = {'file': open('financial_data.json', 'rb')}
data = {'user_id': 'your_user_id'}
response = requests.post('http://localhost:8000/api/v1/documents/upload-crew', 
                        files=files, data=data)
```

### Chat with AI Agents
```python
# Chat with CrewAI agents
payload = {
    "message": "What are the main revenue sources in our latest financial data?",
    "user_id": "your_user_id",
    "context": {}
}
response = requests.post('http://localhost:8000/api/v1/crew/chat', json=payload)
```

### Semantic Search
```python
# Perform semantic search
payload = {
    "query": "quarterly revenue trends",
    "top_k": 10,
    "user_id": "your_user_id"
}
response = requests.post('http://localhost:8000/api/v1/crew/semantic-search', json=payload)
```

### Knowledge Graph Analysis
```python
# Analyze knowledge graph
payload = {
    "analysis_type": "overview",
    "user_id": "your_user_id"
}
response = requests.post('http://localhost:8000/api/v1/crew/graph-analysis', json=payload)
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# Optional: Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Agent Configuration
Agents can be customized in `agents/crew_base.py`:
- Adjust agent roles and backstories
- Modify tool configurations
- Change LLM parameters

### RAG Configuration
RAG settings in `agents/rag_graph_manager.py`:
- Embedding model selection
- Vector index parameters
- Graph visualization settings

## 📈 Key Improvements Over N8N

### 1. **Robust Agent Framework**
- **Before**: Simple webhook-based processing
- **After**: Sophisticated multi-agent collaboration with specialized roles

### 2. **Advanced RAG Capabilities**
- **Before**: Basic text search
- **After**: Semantic search with vector embeddings and knowledge graphs

### 3. **Dynamic Ontology Management**
- **Before**: Static ontology structure
- **After**: AI-powered ontology extension with human validation

### 4. **Better Error Handling**
- **Before**: Limited error recovery
- **After**: Robust error handling with fallback mechanisms

### 5. **Scalable Architecture**
- **Before**: Workflow-based processing
- **After**: Microservices architecture with independent agents

## 🛠️ Development

### Adding New Agents
1. Create agent class in `agents/`
2. Define tools and capabilities
3. Add to CrewAI manager
4. Update API endpoints

### Extending RAG Capabilities
1. Modify `RAGGraphManager` class
2. Add new embedding strategies
3. Implement custom similarity metrics
4. Update graph visualization

### Custom Tools
1. Inherit from `KudwaBaseTool`
2. Implement `_run` method
3. Add to agent tool list
4. Test with crew execution

## 🔍 Monitoring and Debugging

### Logs
- FastAPI logs: `logs/fastapi.log`
- Dashboard logs: `logs/dashboard.log`
- Agent execution logs: Console output

### Health Checks
- System health: `GET /api/v1/crew/health`
- Individual agent status: Available in dashboard
- Vector index status: Included in health check

### Performance Metrics
- Agent execution times
- Vector search performance
- Graph generation statistics
- API response times

## 🚨 Troubleshooting

### Common Issues

1. **Vector Index Not Initialized**
   - Check Supabase connection
   - Verify embeddings table has data
   - Restart system to reinitialize

2. **Agent Execution Failures**
   - Check OpenAI API key
   - Verify tool configurations
   - Review agent logs

3. **Graph Visualization Issues**
   - Ensure static directory exists
   - Check file permissions
   - Verify pyvis installation

4. **Memory Issues**
   - Reduce vector index size
   - Limit graph node count
   - Optimize embedding dimensions

## 🔮 Future Enhancements

- **Multi-modal Support**: Image and PDF processing
- **Real-time Collaboration**: Multi-user ontology editing
- **Advanced Analytics**: Predictive financial modeling
- **Integration APIs**: Connect with external financial systems
- **Mobile Interface**: React Native dashboard

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Test individual components
4. Create detailed issue reports

---

**Built with ❤️ using CrewAI, FastAPI, and Supabase**
