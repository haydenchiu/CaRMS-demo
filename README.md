# CaRMS Residency Program Data Platform

A production-ready data engineering platform demonstrating best practices for data warehousing, ETL orchestration, and API development using the modern Python data stack.

## 🎯 Project Overview

This platform ingests, transforms, and serves Canadian Residency Matching Service (CaRMS) program data through:

- **PostgreSQL Data Warehouse** with dimensional modeling (star schema)
- **Dagster ETL Pipeline** for orchestrated data processing
- **FastAPI REST API** for data access and analytics
- **LangChain Integration** for semantic search and Q&A
- **Match Simulation** for scenario analysis
- **Docker Containerization** for consistent deployment

## 🏗️ Architecture

```
┌─────────────────┐
│   Data Sources  │
│  (JSON/CSV/XLS) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Dagster     │
│  ETL Pipeline   │
│  - Raw Layer    │
│  - Staging      │
│  - Serving      │
│  - Analytics    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│  Data Warehouse │
│   (+ pgvector)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    FastAPI      │
│   REST API      │
│  - Programs     │
│  - Search       │
│  - Analytics    │
│  - Simulation   │
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (or use Docker)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd carms-demo
```

2. **Set up Python environment**
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Or using pip
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings (DATABASE_URL, OPENAI_API_KEY, etc.)
```

4. **Start services with Docker**
```bash
cd docker
docker-compose up -d
```

This starts:
- PostgreSQL with pgvector (port 5432)
- Dagster Web UI (http://localhost:3000)
- FastAPI (http://localhost:8000)

5. **Initialize database**
```bash
python scripts/init_db.py
```

### Verify Installation

**Check API health:**
```bash
curl http://localhost:8000/health
```

**Access Dagster UI:**
Open http://localhost:3000 in your browser

**View API docs:**
Open http://localhost:8000/docs in your browser

## 📊 Data Model

The platform uses a **star schema** data warehouse design:

### Dimension Tables
- `dim_universities` - Canadian universities offering residency programs
- `dim_specialties` - Medical specialties and disciplines
- `dim_requirements` - Program eligibility and document requirements
- `dim_training_sites` - Clinical training locations
- `dim_selection_criteria` - How programs evaluate candidates

### Fact Tables
- `fact_programs` - Core residency program information (main fact table)

### Key Features
- Surrogate keys for all dimensions
- Audit columns (created_at, updated_at)
- Soft delete support
- Proper foreign key constraints
- Optimized indexes for common queries

## 🔄 ETL Pipeline

The Dagster pipeline processes data through multiple layers:

### 1. Raw Layer
- `raw_program_descriptions_json` - Load JSON program descriptions
- `raw_program_descriptions_csv` - Load CSV cross-sectional data
- `raw_program_master` - Load Excel master file
- `raw_discipline` - Load discipline categorization

### 2. Staging Layer (Phase 2)
- Data cleaning and validation
- Parsing and normalization
- Data quality checks

### 3. Serving Layer (Phase 2)
- Populate dimension tables
- Populate fact tables
- Apply business rules

### 4. Analytics Layer (Phase 2)
- Aggregated metrics
- Derived analytics
- Reporting datasets

## 🛠️ Development

### Project Structure

```
carms-demo/
├── src/
│   ├── models/              # SQLModel schemas
│   ├── dagster_project/     # ETL pipeline
│   ├── api/                 # FastAPI application
│   ├── matching/            # Match simulation (Phase 3)
│   ├── reporting/           # Report generation (Phase 3)
│   └── utils/               # Shared utilities
├── tests/                   # Test suite
├── docker/                  # Docker configuration
├── docs/                    # Documentation
├── data/                    # Source data files
└── scripts/                 # Utility scripts
```

### Running Tests

```bash
pytest tests/ -v --cov=src
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff src/ tests/

# Type checking
mypy src/
```

### Running Dagster Locally (without Docker)

```bash
dagster dev -m src.dagster_project
```

### Running FastAPI Locally (without Docker)

```bash
uvicorn src.api.main:app --reload
```

## 📚 API Documentation

Once the API is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Available Endpoints (Phase 1)

- `GET /` - Root endpoint with API info
- `GET /health` - Health check

### Coming in Phase 2

- `GET /api/v1/programs` - List programs with filters
- `GET /api/v1/programs/{id}` - Program details
- `GET /api/v1/analytics/specialties` - Specialty statistics
- And more...

## 🐳 Docker Deployment

### Build and Run

```bash
cd docker
docker-compose up --build
```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f [service_name]
```

### Reset Database

```bash
docker-compose down -v  # Remove volumes
docker-compose up -d
```

## 🔧 Configuration

Configuration is managed through environment variables (see `.env.example`):

### Database
- `DATABASE_URL` - PostgreSQL connection string

### OpenAI (for embeddings)
- `OPENAI_API_KEY` - API key for embeddings and semantic search

### Application
- `ENVIRONMENT` - development/staging/production
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)
- `DEBUG` - Enable debug mode

### API
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)
- `API_RELOAD` - Enable auto-reload in development

## 📈 Implementation Phases

### ✅ Phase 1: Foundation (Current)
- [x] Project setup and structure
- [x] SQLModel schemas with proper relationships
- [x] Basic Dagster pipeline (raw data ingestion)
- [x] Docker containerization
- [x] Database utilities
- [x] Basic FastAPI application

### 🚧 Phase 2: Core ETL & API (Next)
- [ ] Complete staging and serving layers
- [ ] Data quality checks
- [ ] Program and analytics API endpoints
- [ ] Integration tests

### 📅 Phase 3: Advanced Features
- [ ] LangChain semantic search
- [ ] Match simulation algorithm
- [ ] Reporting framework
- [ ] Full documentation

### 📅 Phase 4: Production Ready
- [ ] Performance optimization
- [ ] AWS deployment guide
- [ ] CI/CD pipeline
- [ ] Comprehensive testing

## 🎓 Tech Stack

- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+ with pgvector
- **ETL**: Dagster 1.6+
- **API**: FastAPI, Uvicorn
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Data Processing**: Pandas
- **ML/AI**: LangChain, OpenAI
- **Testing**: Pytest
- **Code Quality**: Black, Ruff, MyPy
- **Containerization**: Docker, Docker Compose

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a demonstration project for a job application. Feedback and suggestions are welcome!

## 📧 Contact

For questions about this project, please reach out via the contact information in the repository.

---

**Built with ❤️ for CaRMS Junior Data Scientist position**
