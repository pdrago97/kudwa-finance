# Kudwa Next.js Financial Platform

A modern, commercial-grade financial data platform built with Next.js 14, TypeScript, and Supabase.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Supabase account and project

### Environment Setup

1. **Copy environment files:**
   ```bash
   cp .env.example .env
   cp frontend/.env.example frontend/.env
   ```

2. **Configure Supabase:**
   - Update `.env` with your Supabase credentials
   - Update `frontend/.env` with your Supabase URL and anon key

3. **Start the platform:**
   ```bash
   ./start-nextjs.sh
   ```

### Access Points
- **Next.js Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Streamlit (Legacy)**: http://localhost:8501

## 🏗️ Architecture

### Frontend Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand + React Query
- **Authentication**: Supabase Auth
- **Charts**: Recharts + D3.js
- **Real-time**: Supabase Realtime

### Backend Stack
- **API**: FastAPI (existing)
- **Database**: Supabase PostgreSQL
- **Vector Store**: Supabase Vector
- **Authentication**: Supabase Auth

## 📁 Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Authentication pages
│   ├── (dashboard)/              # Dashboard pages
│   ├── admin/                    # Admin pages
│   ├── api/                      # API routes
│   ├── globals.css               # Global styles
│   └── layout.tsx                # Root layout
├── components/                   # React components
│   ├── ui/                       # shadcn/ui components
│   ├── dashboard/                # Dashboard components
│   ├── charts/                   # Chart components
│   ├── graph/                    # Graph visualization
│   ├── chat/                     # Chat interface
│   └── canvas/                   # Widget canvas
├── lib/                          # Utilities
│   ├── supabase.ts              # Supabase client
│   ├── utils.ts                 # Utility functions
│   └── api.ts                   # API client
├── hooks/                        # Custom React hooks
├── stores/                       # Zustand stores
├── types/                        # TypeScript definitions
└── public/                       # Static assets
```

## 🎨 Features

### ✅ Implemented
- **Authentication System**: Login/register with Supabase Auth
- **Modern Dashboard**: Responsive layout with metrics and charts
- **Component Library**: shadcn/ui based components
- **Theme Support**: Dark/light mode toggle
- **Real-time Updates**: Live data with React Query
- **Navigation**: Sidebar navigation with quick actions
- **User Management**: Profile and session management

### 🚧 In Progress
- **Chat Interface**: AI assistant with streaming responses
- **Graph Visualization**: Interactive knowledge graph
- **Canvas Widgets**: Drag-and-drop dashboard builder
- **File Upload**: Advanced document processing
- **Analytics**: Advanced insights and reporting

### 📋 Planned
- **GraphRAG Integration**: Advanced graph-based RAG
- **Backoffice Features**: Admin panel and user management
- **Advanced Charts**: Custom visualization components
- **Mobile App**: React Native companion app
- **API Extensions**: GraphQL endpoint

## 🔧 Development

### Local Development

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Run tests:**
   ```bash
   npm test
   ```

4. **Type checking:**
   ```bash
   npm run type-check
   ```

### Docker Development

```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f frontend

# Stop services
docker-compose down
```

## 🎯 Migration from Streamlit

### What's Different
- **Performance**: Significantly faster than Streamlit
- **Customization**: Full control over UI/UX
- **Scalability**: Better performance at scale
- **Mobile Support**: Responsive design
- **Real-time**: WebSocket support for live updates

### Migration Strategy
1. **Phase 1**: Basic dashboard and authentication ✅
2. **Phase 2**: Chat and graph visualization 🚧
3. **Phase 3**: Canvas widgets and advanced features 📋
4. **Phase 4**: Admin panel and deployment 📋

### Feature Comparison

| Feature | Streamlit | Next.js | Status |
|---------|-----------|---------|--------|
| Dashboard | Basic | Advanced | ✅ |
| Authentication | None | Full | ✅ |
| Chat | Simple | Advanced | 🚧 |
| Graphs | Basic | Interactive | 🚧 |
| Mobile | Poor | Excellent | ✅ |
| Performance | Slow | Fast | ✅ |
| Customization | Limited | Full | ✅ |

## 🔐 Security

- **Authentication**: Supabase Auth with JWT tokens
- **Authorization**: Row Level Security (RLS) policies
- **API Security**: CORS and rate limiting
- **Data Validation**: Zod schemas for type safety
- **Environment**: Secure environment variable handling

## 📊 Monitoring

### Health Checks
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000/api/health`

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
```

## 🚀 Deployment

### Production Build
```bash
cd frontend
npm run build
npm start
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**Next Steps**: 
1. Complete chat interface implementation
2. Add graph visualization with React Flow
3. Implement canvas widget system
4. Build admin panel
5. Add comprehensive testing
