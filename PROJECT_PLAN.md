# CaRMS Residency Program Data Platform - Project Plan

## Context
This is a technical skills demonstration for the CaRMS Junior Data Scientist position. The goal is to showcase data engineering skills using their exact tech stack: PostgreSQL, SQLAlchemy/SQLModel, Dagster, FastAPI, and LangChain.

## Job Requirements Focus
1. **Data Engineering** (primary) - ETL, data warehouse design, data quality
2. **Their exact tech stack** - PostgreSQL, SQLAlchemy/SQLModel, Dagster, FastAPI
3. **Business-relevant problems** - matching, preferences, data contracts, reporting
4. **Production-ready practices** - Docker, testing, Git, AWS-ready architecture

## Available Data
- **1503_markdown_program_descriptions_v2.json**: 386+ residency program descriptions with rich text content
- **1503_program_descriptions_x_section.csv**: Cross-sectional program data (386K+ rows) with structured sections
- **1503_program_master.xlsx**: Master program information (metadata)
- **1503_discipline.xlsx**: Discipline categorization data

Data represents Canadian Residency Matching Service (CaRMS) 2025 R-1 Main Residency Match programs across Canadian universities.

---

## Project Goal
Build a production-ready data platform that ingests, transforms, and serves CaRMS residency program data through a modern data stack. This directly mirrors the work required for the matching platform modernization role.

---

## Core Components

### 1. Data Warehouse Design (PostgreSQL + SQLModel)
**Purpose**: Demonstrate "Deep understanding of data management concepts associated with designing, building, maintaining, and extending an Enterprise Data Warehouse"

**Design**:
- **Fact Tables**:
  - `programs` - Core program information
  - `applications` (simulated) - Application records
  - `match_outcomes` (simulated) - Match results
  
- **Dimension Tables**:
  - `universities` - University information
  - `specialties` - Medical specialties
  - `requirements` - Program requirements
  - `training_sites` - Clinical training locations
  - `selection_criteria` - How programs evaluate candidates
  - `interview_dates` - Interview scheduling information

- **Design Pattern**: Star/Snowflake schema with proper normalization
- **Key Features**:
  - Surrogate keys
  - Audit columns (created_at, updated_at)
  - Soft deletes where appropriate
  - Proper foreign key constraints

### 2. ETL Pipeline (Dagster)
**Purpose**: Demonstrate "Designing, implementing, and operating critical data infrastructure" and "Migrating ETL"

**Dagster Assets**:

**Raw Layer** (`assets/raw_data.py`):
- `raw_program_descriptions_json` - Load JSON file
- `raw_program_descriptions_csv` - Load CSV file
- `raw_program_master` - Load Excel file
- `raw_discipline` - Load Excel file

**Staging Layer** (`assets/staging.py`):
- `staging_programs` - Parse and clean program data
- `staging_universities` - Extract university information
- `staging_requirements` - Parse requirements from text
- `staging_selection_criteria` - Extract selection criteria
- `staging_training_sites` - Parse training site information
- Data quality checks at this layer

**Serving Layer** (`assets/serving.py`):
- `dim_universities` - Final university dimension
- `dim_specialties` - Final specialty dimension
- `dim_requirements` - Final requirements dimension
- `fact_programs` - Final program fact table

**Analytics Layer** (`assets/analytics.py`):
- `analytics_program_summary` - Aggregated program statistics
- `analytics_requirements_by_specialty` - Requirements analysis
- `analytics_selection_criteria_trends` - Selection criteria patterns

**Data Quality Checks**:
- Missing required fields validation
- Duplicate detection
- Invalid dates/quotas
- Referential integrity checks
- Data type validation
- Business rule validation (e.g., quota > 0)

**Orchestration**:
- Schedules for daily refresh
- Sensors for new file detection
- Job definitions for manual runs
- Resource definitions for database and external services

### 3. API Layer (FastAPI)
**Purpose**: Demonstrate "Developing internal matching platform API (using FastAPI)"

**Endpoints** (`api/routes/`):

**Programs** (`programs.py`):
- `GET /programs` - List programs with filters (specialty, university, location)
- `GET /programs/{id}` - Program details
- `GET /programs/{id}/requirements` - Program requirements
- `GET /programs/{id}/selection-criteria` - Selection criteria
- `POST /programs/compare` - Compare multiple programs

**Search** (`search.py`):
- `POST /search/semantic` - Semantic search using LangChain
- `POST /search/qa` - Q&A on program descriptions
- `GET /search/similar/{program_id}` - Find similar programs

**Analytics** (`analytics.py`):
- `GET /analytics/specialties` - Specialty statistics
- `GET /analytics/requirements/summary` - Requirements by specialty
- `GET /analytics/selection-criteria` - Selection criteria patterns
- `GET /analytics/geographic-distribution` - Programs by location

**Simulation** (`simulation.py`):
- `POST /simulate/match` - Run match simulation
- `POST /simulate/what-if` - What-if scenario analysis
- `GET /simulate/results/{simulation_id}` - Get simulation results

**Reports** (`reports.py`):
- `GET /reports/data-contract` - Data contract report
- `GET /reports/operational` - Operational reporting
- `POST /reports/custom` - Custom data request

**Features**:
- Auto-generated OpenAPI documentation
- Input validation with Pydantic models
- Async database queries
- Proper error handling and logging
- Response models for type safety
- Query parameter validation

### 4. Match Simulation Module
**Purpose**: Demonstrate "Maintaining and extending match simulation software and conducting 'what-if' scenario analysis"

**Implementation** (`matching/`):
- Stable matching algorithm (Gale-Shapley variant)
- Applicant preference modeling
- Program capacity constraints
- What-if scenario analysis
- Simulation result analytics

**Features**:
- Generate synthetic applicant data
- Rank programs based on criteria
- Run matching algorithm
- Analyze match outcomes
- Support "what-if" scenarios (e.g., "What if program X increases quota by 2?")

### 5. Semantic Search & Q&A (LangChain)
**Purpose**: Demonstrate "Implementing semantic search and Q&A on documents"

**Implementation** (`utils/embeddings.py`):
- Embed program descriptions using OpenAI/Anthropic
- Store vectors in PostgreSQL using pgvector extension
- RAG (Retrieval Augmented Generation) pipeline
- Semantic search functionality
- Q&A system for program descriptions

**Use Cases**:
- "Find programs that emphasize research and offer strong mentorship"
- "Which programs have the best work-life balance?"
- "Compare the selection criteria of programs X and Y"

### 6. Modular Reporting Framework
**Purpose**: Demonstrate "Developing modular Python-based reporting framework"

**Reports** (`reporting/`):
- Base report class with common functionality
- Data contract report (requirements by specialty)
- Operational report (programs by status, capacity, interview rates)
- Custom request handler (parameterized queries)

**Features**:
- Export to CSV, JSON, or Markdown
- Templated output
- Configurable parameters
- Scheduled generation via Dagster

### 7. Containerization & AWS-Ready Architecture
**Purpose**: Demonstrate "Experience using cloud data storage (AWS S3), PostgreSQL-compatible database services (RDS/Aurora), and compute (EC2, ECS, Fargate)"

**Docker Setup** (`docker/`):
- `Dockerfile.api` - FastAPI application
- `Dockerfile.dagster` - Dagster daemon and web UI
- `docker-compose.yml` - Local development setup
  - PostgreSQL with pgvector
  - FastAPI service
  - Dagster daemon
  - Dagster web UI

**AWS Deployment Documentation** (`docs/aws_deployment.md`):
- RDS PostgreSQL setup
- ECS/Fargate deployment
- S3 for data storage
- Environment configuration
- CI/CD with GitHub Actions

### 8. Testing & Quality
**Purpose**: Demonstrate "Use of version control (Git) and test-based development practices"

**Test Coverage** (`tests/`):
- Unit tests for models and utilities
- Integration tests for API endpoints
- Data quality tests in Dagster
- Match algorithm tests

**Quality Practices**:
- Type hints throughout
- Pre-commit hooks (black, ruff, mypy)
- GitHub Actions CI/CD
- Code coverage tracking
- Professional commit messages

---

## Project Structure

```
carms-demo/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD
├── data/                          # Raw data files (existing)
│   ├── 1503_markdown_program_descriptions_v2.json
│   ├── 1503_program_descriptions_x_section.csv
│   ├── 1503_program_master.xlsx
│   ├── 1503_discipline.xlsx
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── models/                    # SQLModel schemas
│   │   ├── __init__.py
│   │   ├── program.py             # Program fact table
│   │   ├── university.py          # University dimension
│   │   ├── specialty.py           # Specialty dimension
│   │   ├── requirement.py         # Requirements dimension
│   │   ├── training_site.py       # Training sites dimension
│   │   ├── selection_criteria.py  # Selection criteria
│   │   └── base.py                # Base model with audit fields
│   ├── dagster_project/           # Dagster ETL pipeline
│   │   ├── __init__.py
│   │   ├── assets/
│   │   │   ├── __init__.py
│   │   │   ├── raw_data.py        # Raw data ingestion
│   │   │   ├── staging.py         # Staging transformations
│   │   │   ├── serving.py         # Serving layer
│   │   │   └── analytics.py       # Analytics layer
│   │   ├── resources/
│   │   │   ├── __init__.py
│   │   │   ├── database.py        # Database resource
│   │   │   └── langchain.py       # LangChain resource
│   │   ├── sensors.py             # File sensors
│   │   ├── schedules.py           # Scheduled jobs
│   │   ├── jobs.py                # Job definitions
│   │   └── repository.py          # Dagster repository
│   ├── api/                       # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app initialization
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── programs.py        # Program endpoints
│   │   │   ├── search.py          # Search endpoints
│   │   │   ├── analytics.py       # Analytics endpoints
│   │   │   ├── simulation.py      # Simulation endpoints
│   │   │   └── reports.py         # Reporting endpoints
│   │   ├── dependencies.py        # Shared dependencies
│   │   └── schemas.py             # Pydantic request/response models
│   ├── matching/                  # Match simulation
│   │   ├── __init__.py
│   │   ├── algorithm.py           # Matching algorithm
│   │   ├── simulation.py          # Simulation runner
│   │   └── preferences.py         # Preference modeling
│   ├── reporting/                 # Modular reporting
│   │   ├── __init__.py
│   │   ├── base.py                # Base report class
│   │   ├── data_contract.py       # Data contract report
│   │   ├── operational.py         # Operational report
│   │   └── custom.py              # Custom request handler
│   └── utils/
│       ├── __init__.py
│       ├── database.py            # Database utilities
│       ├── embeddings.py          # LangChain embeddings
│       └── config.py              # Configuration management
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_models.py             # Model tests
│   ├── test_etl.py                # ETL pipeline tests
│   ├── test_api.py                # API endpoint tests
│   ├── test_matching.py           # Matching algorithm tests
│   └── test_reporting.py          # Reporting tests
├── docker/
│   ├── Dockerfile.api             # FastAPI Docker image
│   ├── Dockerfile.dagster         # Dagster Docker image
│   └── docker-compose.yml         # Local development setup
├── docs/
│   ├── architecture.md            # System architecture
│   ├── data_warehouse_design.md   # Data model documentation
│   ├── api_documentation.md       # API usage guide
│   ├── aws_deployment.md          # AWS deployment guide
│   └── etl_pipeline.md            # ETL pipeline documentation
├── .gitignore
├── .pre-commit-config.yaml        # Pre-commit hooks
├── pyproject.toml                 # Project dependencies
├── uv.lock                        # Lock file
├── README.md                      # Project overview and setup
└── PROJECT_PLAN.md                # This file
```

---

## Implementation Phases

### Phase 1: Foundation (Days 1-3)
**Goal**: Set up project structure and core data models

1. **Project Setup**
   - Initialize project structure
   - Set up pyproject.toml with all dependencies
   - Configure pre-commit hooks
   - Create .gitignore

2. **SQLModel Schemas**
   - Design data warehouse schema
   - Implement all model classes
   - Add proper relationships and constraints
   - Create database initialization scripts

3. **Basic Dagster Pipeline**
   - Set up Dagster project structure
   - Implement raw data ingestion assets
   - Create database resource
   - Basic staging transformations

4. **Docker Setup**
   - Create Dockerfiles
   - Set up docker-compose.yml
   - Test local development environment

**Deliverables**: Working project structure, models defined, basic ETL running

### Phase 2: Core ETL & API (Days 4-6)
**Goal**: Complete ETL pipeline and build core API

1. **Complete Dagster Pipeline**
   - All staging layer assets
   - All serving layer assets
   - Analytics layer assets
   - Data quality checks
   - Schedules and sensors

2. **FastAPI Application**
   - Set up FastAPI app structure
   - Implement program endpoints
   - Implement analytics endpoints
   - Add proper error handling
   - Create OpenAPI documentation

3. **Testing**
   - Unit tests for models
   - Integration tests for ETL
   - API endpoint tests
   - Data quality tests

**Deliverables**: Complete ETL pipeline, working API, test coverage

### Phase 3: Advanced Features (Days 7-9)
**Goal**: Add differentiating features

1. **LangChain Integration**
   - Set up pgvector extension
   - Implement embedding generation
   - Create semantic search
   - Build RAG Q&A system

2. **Match Simulation**
   - Implement matching algorithm
   - Create preference modeling
   - Build what-if scenario analysis
   - Add simulation API endpoints

3. **Reporting Framework**
   - Build base report class
   - Implement data contract report
   - Create operational report
   - Add custom request handler
   - Integrate with Dagster

4. **Documentation**
   - Architecture documentation
   - Data model documentation
   - API usage guide
   - AWS deployment guide
   - Comprehensive README

**Deliverables**: Semantic search working, match simulation functional, reports generated, full documentation

### Phase 4: Polish & Deployment Prep (Days 10-11)
**Goal**: Production-ready code and presentation materials

1. **Code Quality**
   - Code review and refactoring
   - Type hint coverage
   - Error handling improvements
   - Logging implementation
   - Performance optimization

2. **AWS Deployment Documentation**
   - RDS setup instructions
   - ECS deployment guide
   - S3 integration
   - Environment configuration
   - CI/CD pipeline

3. **GitHub Repository**
   - Clean commit history
   - Professional README
   - Architecture diagrams
   - Setup instructions
   - Demo queries and use cases

4. **Presentation Preparation**
   - Demo script
   - Key talking points
   - Technical deep dive topics
   - Business value discussion

**Deliverables**: Production-quality code, deployment-ready, presentation materials

---

## Presentation Strategy for Interview

### Live Demo Flow (15-20 minutes)

**1. Introduction (2 min)**
- Project overview
- Technology stack alignment
- Business problem context

**2. Data Warehouse Design (3 min)**
- Show ERD diagram
- Explain dimensional model
- Discuss normalization decisions
- Highlight data quality considerations

**3. ETL Pipeline Demo (5 min)**
- Open Dagster UI
- Show asset lineage graph
- Materialize assets live
- Demonstrate data quality checks catching issues
- Show how failed checks are handled

**4. API Demonstration (5 min)**
- Open FastAPI Swagger docs
- Execute sample queries:
  - Filter programs by specialty and location
  - Get program requirements
  - Semantic search: "Find programs that emphasize wellness and mentorship"
  - Run match simulation
  - Generate data contract report

**5. Code Walkthrough (3 min)**
- SQLModel schema design
- Dagster asset with data quality checks
- FastAPI route with proper error handling
- Match algorithm implementation

**6. Production Readiness (2 min)**
- Show Docker setup
- Discuss AWS deployment architecture
- Highlight testing coverage
- Mention CI/CD pipeline

### Technical Deep Dive Topics to Prepare

**Data Engineering**:
- Why star schema over normalized OLTP design?
- How you handled data quality issues in source data
- ETL orchestration patterns in Dagster
- Incremental vs full refresh strategies
- Data lineage tracking

**API Design**:
- REST API best practices
- Input validation strategy
- Error handling patterns
- Async vs sync endpoints
- API versioning considerations

**Matching & Algorithms**:
- Stable matching algorithm explanation
- Preference modeling approach
- What-if scenario implementation
- Performance considerations

**Machine Learning/AI**:
- Semantic search architecture
- Embedding strategy and model choice
- RAG pipeline design
- Vector similarity search optimization

**Cloud & DevOps**:
- AWS service selection rationale (RDS vs Aurora, ECS vs Lambda)
- Container orchestration approach
- Secrets management
- Monitoring and observability strategy

**Data Science**:
- Insights extracted from the data
- Statistical approaches to preference modeling
- Simulation methodology
- Reporting framework design

### Business Understanding Discussion

**CaRMS Matching Process**:
- Demonstrate understanding of residency matching
- Discuss applicant and program preferences
- Explain constraints and optimization

**Preference Modeling Challenges**:
- How to infer preferences from historical data
- Dealing with incomplete information
- Balancing multiple stakeholder needs

**Platform Value Proposition**:
- How this platform supports match operations
- Analytics that help applicants make informed decisions
- Insights that help programs optimize selection
- Data contracts for external stakeholders

**Future Enhancements**:
- Real-time data updates
- Advanced analytics dashboards
- Preference prediction models
- Automated reporting schedule
- Integration with external systems

---

## Key Differentiators

### What Will Make This Project Stand Out

**1. Production-Quality Code**
- Comprehensive type hints
- Proper error handling
- Structured logging
- Clean architecture
- SOLID principles

**2. Proper Data Warehouse Design**
- Star/snowflake schema, not flat tables
- Proper normalization
- Audit columns
- Surrogate keys
- SCD Type 2 where appropriate

**3. Real Data Quality Checks**
- Not just "load and hope"
- Validate business rules
- Handle missing data gracefully
- Document data quality issues found
- Show how you'd alert on failures

**4. Business Relevance**
- Match simulation shows domain understanding
- Reports align with stakeholder needs
- API endpoints solve real problems
- Semantic search provides user value

**5. Deployment Ready**
- Docker setup that actually works
- Real AWS deployment documentation
- Environment-based configuration
- Security considerations
- Scalability discussion

**6. Testing**
- Actual tests with good coverage
- Integration tests, not just unit tests
- Data quality tests in pipeline
- API contract tests

**7. Documentation**
- Architecture decisions explained
- Trade-offs discussed
- Future improvements outlined
- Setup instructions that work
- Code comments where needed

---

## Technical Stack Details

### Dependencies (pyproject.toml)

**Core**:
- Python 3.11+
- PostgreSQL 15+
- pgvector extension

**Data Engineering**:
- sqlalchemy >= 2.0
- sqlmodel >= 0.0.14
- dagster >= 1.6
- dagster-webserver
- dagster-postgres
- pandas >= 2.0
- openpyxl (for Excel reading)

**API**:
- fastapi >= 0.110
- uvicorn[standard]
- pydantic >= 2.0

**ML/AI**:
- langchain >= 0.1
- langchain-openai
- openai
- tiktoken

**Testing**:
- pytest >= 8.0
- pytest-asyncio
- pytest-cov
- httpx (for API testing)

**Code Quality**:
- black
- ruff
- mypy
- pre-commit

**Utilities**:
- python-dotenv
- loguru

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/carms

# OpenAI (for embeddings)
OPENAI_API_KEY=sk-...

# Application
ENVIRONMENT=development  # development, staging, production
LOG_LEVEL=INFO

# Dagster
DAGSTER_HOME=/opt/dagster/dagster_home
```

---

## Success Metrics

### Technical Excellence
- [ ] 80%+ test coverage
- [ ] Type hints on all functions
- [ ] Zero linter warnings
- [ ] All data quality checks passing
- [ ] Docker compose runs cleanly
- [ ] API documentation auto-generated

### Functionality
- [ ] ETL pipeline processes all data sources
- [ ] API returns correct results
- [ ] Semantic search produces relevant results
- [ ] Match simulation runs successfully
- [ ] Reports generate correctly

### Production Readiness
- [ ] Error handling throughout
- [ ] Logging implemented
- [ ] Configuration externalized
- [ ] Docker containerized
- [ ] AWS deployment documented
- [ ] CI/CD pipeline defined

### Documentation
- [ ] Comprehensive README
- [ ] Architecture documentation
- [ ] API usage examples
- [ ] Setup instructions tested
- [ ] Code comments where needed

---

## Risk Mitigation

### Potential Challenges

**1. Time Constraints**
- **Mitigation**: Focus on core features first (ETL, API), advanced features second (LangChain, simulation)
- **Backup Plan**: Have a working minimal version by day 7, then add features

**2. Data Quality Issues**
- **Mitigation**: Build robust error handling and validation from the start
- **Document**: Keep a log of data quality issues found

**3. OpenAI API Costs**
- **Mitigation**: Use caching, batch processing, small models
- **Alternative**: Can use open-source embeddings (sentence-transformers)

**4. PostgreSQL pgvector Setup**
- **Mitigation**: Include setup scripts and Docker image with pgvector
- **Alternative**: Use separate vector store if needed

**5. Scope Creep**
- **Mitigation**: Stick to the plan, mark future enhancements as "TODO"
- **Focus**: Core data engineering over fancy visualizations

---

## Post-Interview Follow-Up

### Additional Materials to Prepare

1. **Extended documentation** on advanced topics
2. **Performance benchmarks** for key operations
3. **Scalability analysis** for production deployment
4. **Cost estimation** for AWS deployment
5. **Roadmap** for additional features

### Questions to Ask Them

1. Current pain points in the matching platform?
2. Data quality challenges they face?
3. Preferred AWS services and infrastructure?
4. Team's testing and deployment practices?
5. Most important features for the modernization project?

---

## Notes

- This plan is aggressive but achievable in 10-11 days
- Focus on demonstrating data engineering skills first
- Use their exact tech stack - don't substitute
- Show production-ready practices throughout
- Document decisions and trade-offs
- Be prepared to discuss scaling and performance
- Emphasize how this mirrors their actual work

---

## Next Steps

1. Review and confirm plan alignment
2. Set up project structure
3. Begin Phase 1 implementation
4. Daily progress check-ins
5. Adjust as needed based on progress
