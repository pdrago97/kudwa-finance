# Kudwa AI-Powered Financial Data Processing System

An intelligent financial data processing system that integrates diverse financial data sources with AI-powered insights and ontology-based data modeling.

## 🏗️ Architecture Overview

This system combines:
- **FastAPI** for high-performance REST API
- **Supabase** for scalable database with strong entity typification
- **LangExtract** for intelligent document processing and entity extraction
- **OpenAI/Anthropic LLMs** for natural language querying and insights
- **Ontology-based data modeling** for flexible financial entity management

## 🚀 Key Features

### Core Capabilities
- **Natural Language Querying**: Ask questions about financial data in plain English
- **Intelligent Document Processing**: Extract entities from financial documents using LangExtract
- **Dynamic Ontology Management**: Flexible schema that evolves with new data
- **AI-Powered Analytics**: Trend analysis, anomaly detection, and automated insights

### Financial Entity Support
- Customers and Companies
- Payments and Transactions
- Contracts and Agreements
- Roles and Permissions
- Financial Instruments
- Compliance and Regulatory Data

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL with real-time capabilities)
- **AI/ML**: OpenAI GPT-4, Google LangExtract
- **Data Processing**: Pandas, Pydantic
- **Deployment**: Docker, Render.com

## 📁 Project Structure

```
kudwa/
├── app/
│   ├── api/                 # FastAPI routes and endpoints
│   ├── core/                # Core configuration and settings
│   ├── models/              # Pydantic models and schemas
│   ├── services/            # Business logic and AI services
│   ├── ontology/            # Entity definitions and relationships
│   └── utils/               # Utility functions
├── data/                    # Sample data and datasets
├── docs/                    # Technical documentation
├── tests/                   # Test suites
├── docker/                  # Docker configuration
└── scripts/                 # Setup and utility scripts
```

## 🔧 Quick Start

### Prerequisites
- Python 3.11+
- Supabase account
- OpenAI API key
- Docker (optional)

### Installation

1. Clone and setup:
```bash
git clone <repository>
cd kudwa
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Environment setup:
```bash
cp .env.example .env
# Edit .env with your API keys and database URLs
```

3. Database setup:
```bash
python scripts/setup_database.py
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## 📊 API Endpoints

### Natural Language Queries
- `POST /api/v1/query/natural` - Ask questions in natural language
- `GET /api/v1/insights/summary` - Get AI-generated financial summaries

### Entity Management
- `GET /api/v1/entities/{entity_type}` - List entities by type
- `POST /api/v1/entities/extract` - Extract entities from documents

### Data Integration
- `POST /api/v1/data/ingest` - Ingest financial data
- `GET /api/v1/data/validate` - Validate data quality

## 🧠 AI Features

### Natural Language Processing
The system can understand and respond to queries like:
- "What was the total profit in Q1?"
- "Show me revenue trends for 2024"
- "Which expense category had the highest increase?"
- "Compare Q1 and Q2 performance"

### Document Intelligence
Using LangExtract to automatically identify and extract:
- Customer information
- Contract terms
- Payment details
- Compliance requirements

## 🔒 Security

- Row Level Security (RLS) with Supabase
- API key authentication
- Data encryption at rest and in transit
- Audit logging for all operations

## 📈 Deployment

### Local Development
```bash
make dev
```

### Production Deployment
```bash
make deploy
```

## 🧪 Testing

```bash
make test
```

## 📚 Documentation

- [Technical Architecture](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Ontology Design](docs/ontology.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

Please read our contributing guidelines and code of conduct.

## 📄 License

MIT License - see LICENSE file for details.
