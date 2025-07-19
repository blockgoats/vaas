# BI Platform - Open Source Preset.io Alternative

A comprehensive, multi-tenant SaaS business intelligence platform built with modern technologies, featuring AI-powered chart generation and enterprise-grade security.

## 🚀 Features

### Core Platform
- **Multi-tenant Workspaces**: Isolated environments for teams and organizations
- **Role-Based Access Control**: Admin, Editor, and Viewer roles with granular permissions
- **Data Source Management**: Connect to PostgreSQL, MySQL, Snowflake, BigQuery, and more
- **Interactive Dashboards**: Create and share beautiful data visualizations
- **Embedded Analytics**: Secure dashboard embedding with token authentication

### AI-Powered Analytics
- **Natural Language to Chart**: Generate visualizations from plain English descriptions
- **Smart Chart Recommendations**: AI suggests optimal chart types for your data
- **Automated Insights**: Discover patterns and anomalies in your data
- **Prompt-to-Dashboard**: Create entire dashboards from conversational prompts

### Enterprise Features
- **SSO Integration**: SAML, OAuth2, and JWT authentication
- **Audit Logging**: Complete activity tracking for compliance
- **API Access**: RESTful APIs for programmatic dashboard management
- **Multi-format Export**: PDF, PNG, CSV exports for dashboards and charts
- **Data Quality Monitoring**: Automated data validation and quality reports

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React 18, TypeScript, Tailwind CSS, Framer Motion
- **Backend**: FastAPI (Python), SQLAlchemy, PostgreSQL
- **Async Processing**: Celery with Redis
- **AI Integration**: OpenAI GPT-4, Groq Mixtral, Claude APIs
- **Containerization**: Docker, Docker Compose
- **Charts**: Apache Superset integration

### Project Structure
```
├── src/                    # React frontend
│   ├── components/         # Reusable UI components
│   ├── pages/             # Page components
│   ├── stores/            # Zustand state management
│   └── ...
├── backend/               # FastAPI backend
│   ├── main.py           # API routes and app configuration
│   ├── database.py       # SQLAlchemy models and DB config
│   ├── tasks/            # Celery async tasks
│   └── ...
├── docker-compose.yml    # Multi-service orchestration
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (for local development)

### 1. Clone and Install
```bash
git clone <repository-url>
cd bi-platform
npm install
```

### 2. Environment Setup
Create a `.env` file:
```env
# Database
DATABASE_URL=postgresql://bi_user:bi_password@localhost:5432/bi_platform

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# AI APIs (optional)
OPENAI_API_KEY=your-openai-key
GROQ_API_KEY=your-groq-key
CLAUDE_API_KEY=your-claude-key
```

### 3. Development Setup

#### Option A: Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Option B: Local Development
```bash
# Start frontend
npm run dev

# Start backend (in another terminal)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Start Celery worker (in another terminal)
cd backend
celery -A celery_app.celery worker --loglevel=info
```

### 4. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 5. Default Login
- Email: `admin@example.com`
- Password: `admin`

## 🤖 AI Chart Generation

The platform includes sophisticated AI-powered chart generation:

### Natural Language Examples
```
"Show me sales by region for the last 6 months"
"Create a line chart of user growth over time"
"Display revenue breakdown by product category"
"Generate a funnel chart for our conversion process"
```

### API Usage
```python
import requests

response = requests.post('http://localhost:8000/api/charts/ai-generate', 
  json={
    "prompt": "Show quarterly revenue trends",
    "workspace_id": "ws-1",
    "data_source_id": "ds-1"
  },
  headers={"Authorization": "Bearer <token>"}
)
```

## 📊 Data Source Integration

### Supported Databases
- PostgreSQL
- MySQL
- Snowflake
- Google BigQuery
- Amazon Redshift
- Microsoft SQL Server
- SQLite

### Connection Example
```python
data_source = {
  "name": "Production DB",
  "type": "PostgreSQL",
  "host": "db.company.com",
  "port": 5432,
  "database": "analytics",
  "username": "readonly_user",
  "password": "secure_password"
}
```

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Workspace-level isolation
- API key management

### Data Security
- Encrypted database connections
- Password encryption with bcrypt
- Audit logging for all actions
- IP whitelisting support

### Compliance
- SOC 2 ready architecture
- GDPR compliance features
- Activity audit trails
- Data retention policies

## 🔧 API Reference

### Authentication
```bash
# Login
POST /api/auth/login
{
  "email": "user@company.com",
  "password": "password"
}

# Get current user
GET /api/users/me
Authorization: Bearer <token>
```

### Workspaces
```bash
# List workspaces
GET /api/workspaces

# Create workspace
POST /api/workspaces
{
  "name": "Analytics Team",
  "description": "Main analytics workspace"
}
```

### Charts & Dashboards
```bash
# Generate AI chart
POST /api/charts/ai-generate
{
  "prompt": "Show sales trends",
  "workspace_id": "ws-1"
}

# List charts
GET /api/charts

# List dashboards
GET /api/dashboards
```

## 🚀 Deployment

### Production Deployment

#### Docker Compose
```bash
# Production configuration
docker-compose -f docker-compose.prod.yml up -d
```

#### Kubernetes
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
```

#### Cloud Providers
- **AWS**: ECS, EKS, or EC2
- **Google Cloud**: GKE or Compute Engine
- **Azure**: AKS or Container Instances

### Environment Variables (Production)
```env
# Database
DATABASE_URL=postgresql://user:pass@prod-db:5432/bi_platform

# Security
SECRET_KEY=<generate-strong-key>
JWT_ALGORITHM=HS256

# AI APIs
OPENAI_API_KEY=<production-key>
GROQ_API_KEY=<production-key>

# Monitoring
SENTRY_DSN=<sentry-url>
LOG_LEVEL=INFO
```

## 🧪 Testing

### Unit Tests
```bash
# Frontend tests
npm run test

# Backend tests
cd backend
pytest
```

### Integration Tests
```bash
# API integration tests
cd backend
pytest tests/integration/

# End-to-end tests
npm run test:e2e
```

## 📈 Performance & Scaling

### Optimization Features
- Redis caching for frequently accessed data
- Async processing with Celery
- Database query optimization
- CDN support for static assets

### Scaling Considerations
- Horizontal scaling with load balancers
- Database read replicas
- Separate Celery workers by task type
- Microservices architecture ready

## 🛠️ Development

### Code Quality
- TypeScript for type safety
- ESLint and Prettier for code formatting
- Pre-commit hooks with Husky
- Automated testing in CI/CD

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: [docs.bi-platform.com](https://docs.bi-platform.com)
- **Community**: [Discord](https://discord.gg/bi-platform)
- **Issues**: [GitHub Issues](https://github.com/your-org/bi-platform/issues)
- **Email**: support@bi-platform.com

## 🗺️ Roadmap

### Q1 2024
- [ ] Advanced AI features (auto-insights, anomaly detection)
- [ ] Real-time collaboration
- [ ] Advanced embedding options

### Q2 2024
- [ ] Mobile app
- [ ] Advanced data transformations
- [ ] Machine learning integrations

### Q3 2024
- [ ] Marketplace for community charts
- [ ] Advanced governance features
- [ ] Multi-cloud deployment options

---

Built with ❤️ by the BI Platform team. Star ⭐ this repo if you find it useful!