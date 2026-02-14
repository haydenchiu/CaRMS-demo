# Phase 1 Foundation - Quick Start Guide

## 🎉 What's Been Built

Phase 1 of the CaRMS Residency Program Data Platform is complete! This provides a solid foundation with:

- **Production-ready project structure** following best practices
- **Data warehouse schema** with 6 SQLModel tables (star schema design)
- **Basic Dagster ETL pipeline** with 4 raw data ingestion assets
- **FastAPI REST API** with health checks and auto-documentation
- **Docker containerization** for PostgreSQL, Dagster, and FastAPI
- **Testing infrastructure** with 5 passing tests
- **Comprehensive documentation** and setup scripts

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Start all services:**
   ```bash
   cd docker
   docker-compose up -d
   ```

2. **Access the services:**
   - Dagster UI: http://localhost:3000
   - FastAPI Docs: http://localhost:8000/docs
   - PostgreSQL: localhost:5432

3. **Initialize the database:**
   ```bash
   # Wait for PostgreSQL to be ready (about 10 seconds)
   source .venv/bin/activate
   python scripts/init_db.py
   ```

### Option 2: Local Development

1. **Set up Python environment:**
   ```bash
   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -e ".[dev]"
   ```

2. **Start PostgreSQL** (via Docker or local installation)

3. **Run services locally:**
   ```bash
   # Terminal 1: Dagster
   dagster dev -m src.dagster_project
   
   # Terminal 2: FastAPI
   uvicorn src.api.main:app --reload
   ```

## 📂 Project Structure

```
szw/
├── src/                        # Main source code
│   ├── models/                 # SQLModel database schemas
│   │   ├── base.py            # Base models with timestamps
│   │   ├── university.py      # University dimension
│   │   ├── specialty.py       # Specialty dimension
│   │   ├── program.py         # Program fact table
│   │   ├── requirement.py     # Requirements dimension
│   │   ├── training_site.py   # Training sites dimension
│   │   └── selection_criteria.py
│   ├── dagster_project/       # ETL pipeline
│   │   ├── assets/
│   │   │   └── raw_data.py    # Raw data ingestion
│   │   └── resources/
│   │       └── __init__.py    # Database resource
│   ├── api/                   # FastAPI application
│   │   ├── main.py           # App with health endpoints
│   │   └── routes/           # Route modules (Phase 2)
│   ├── utils/                # Shared utilities
│   │   ├── config.py         # Configuration management
│   │   └── database.py       # Database utilities
│   ├── matching/             # Match simulation (Phase 3)
│   └── reporting/            # Reporting framework (Phase 3)
├── tests/                    # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── test_models.py       # Model tests (5 passing)
│   └── test_api.py          # API tests
├── docker/                   # Docker configuration
│   ├── Dockerfile.api
│   ├── Dockerfile.dagster
│   ├── docker-compose.yml
│   └── init-db.sql
├── scripts/                  # Utility scripts
│   ├── init_db.py           # Database initialization
│   ├── verify.py            # Installation verification
│   └── setup.sh             # Quick setup script
├── docs/
│   └── architecture.md      # System architecture
├── pyproject.toml           # Project configuration
├── README.md                # Main documentation
└── PHASE1_COMPLETE.md       # This file
```

## 🧪 Verify Installation

```bash
source .venv/bin/activate
python scripts/verify.py
```

This checks:
- ✅ All Python packages installed
- ✅ Models can be imported
- ✅ Configuration loads correctly
- ✅ Dagster definitions valid
- ✅ FastAPI app loads
- ⚠️  Database connection (needs Docker)
- ⚠️  Data files (not in repo)

## 🔧 Key Files

### Configuration
- `.env` - Environment variables (create from `.env.example`)
- `pyproject.toml` - Dependencies and project metadata

### Database Models (Star Schema)
All models in `src/models/`:
- **Dimensions**: Universities, Specialties, Requirements, Training Sites, Selection Criteria
- **Facts**: Programs (main fact table)
- **Features**: Audit columns, soft deletes, proper relationships

### ETL Assets
Current raw data assets in `src/dagster_project/assets/raw_data.py`:
- Load JSON program descriptions
- Load CSV cross-sectional data
- Load Excel master data
- Load discipline data

### API Endpoints
Current endpoints in `src/api/main.py`:
- `GET /` - API information
- `GET /health` - Health check

## 📊 Database Schema

### Dimension Tables
```
dim_universities       - University information
dim_specialties       - Medical specialties with hierarchy
dim_requirements      - Program eligibility requirements
dim_training_sites    - Clinical training locations
dim_selection_criteria - How programs evaluate candidates
```

### Fact Table
```
fact_programs         - Core residency program information
  ├─> university_id   (FK to dim_universities)
  └─> specialty_id    (FK to dim_specialties)
```

All tables include:
- `id` (primary key)
- `created_at`, `updated_at` (audit columns)
- `is_deleted`, `deleted_at` (soft delete support)

## 🧪 Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_models.py -v

# With coverage
pytest --cov=src tests/

# Current status: 5/5 tests passing ✅
```

## 🛠️ Development Commands

### Database
```bash
# Initialize database
python scripts/init_db.py

# Connect to PostgreSQL
docker exec -it carms-postgres psql -U carms -d carms
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

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up --build
```

## 📚 Next: Phase 2

Phase 2 will implement:

1. **Complete ETL Pipeline**
   - Staging layer with data cleaning and validation
   - Serving layer to populate warehouse tables
   - Analytics layer for derived metrics
   - Comprehensive data quality checks

2. **Full API Implementation**
   - Program CRUD endpoints with filters
   - Analytics endpoints for insights
   - Proper request/response models
   - Pagination and sorting

3. **Expanded Testing**
   - Integration tests for ETL pipeline
   - API endpoint tests with test database
   - Data quality test cases

## 🎯 Success Metrics - Phase 1

### Completed ✅
- [x] Clean project structure
- [x] 6 SQLModel tables with relationships
- [x] 4 Dagster raw data assets
- [x] Basic FastAPI with 2 endpoints
- [x] Docker setup with 3 services
- [x] 5 passing tests
- [x] Comprehensive documentation
- [x] Type hints throughout
- [x] Configuration management
- [x] Database utilities

### Phase 2 Goals
- [ ] 10+ Dagster assets (staging + serving)
- [ ] 10+ API endpoints
- [ ] 20+ tests with 80% coverage
- [ ] Data quality checks
- [ ] Full ETL pipeline functional

## 💡 Tips

1. **Use Docker for simplicity** - Everything just works
2. **Check logs** if something fails - `docker-compose logs -f`
3. **Verify installation** - Run `python scripts/verify.py`
4. **Read the docs** - Check `docs/architecture.md` for design details
5. **Run tests** - Ensure everything works after changes

## 🐛 Troubleshooting

### Database connection failed
```bash
# Make sure PostgreSQL is running
docker-compose ps

# Restart if needed
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Import errors
```bash
# Reinstall dependencies
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Port already in use
```bash
# Check what's using the port
lsof -i :5432  # PostgreSQL
lsof -i :3000  # Dagster
lsof -i :8000  # FastAPI

# Change port in docker-compose.yml if needed
```

## 📞 Support

- Check `README.md` for detailed setup instructions
- Review `docs/architecture.md` for design decisions
- Run `python scripts/verify.py` to diagnose issues
- Check Docker logs: `docker-compose logs -f [service]`

---

**Phase 1 is complete and ready for Phase 2 development!** 🎉

The foundation is solid, well-tested, and follows production best practices.
