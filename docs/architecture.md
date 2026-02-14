# CaRMS Data Platform - Architecture

## System Architecture

The CaRMS Data Platform follows a modern data engineering architecture with clear separation of concerns across layers.

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Data Sources                            │
│  • JSON (Program Descriptions)                              │
│  • CSV (Cross-sectional Data)                               │
│  • Excel (Master Data & Disciplines)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Dagster ETL Pipeline                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Raw Layer:    Load files as-is                       │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Staging Layer: Clean, parse, validate                │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Serving Layer: Populate warehouse tables             │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Analytics Layer: Derived metrics & aggregations      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Data Warehouse                       │
│  • Star Schema Design                                        │
│  • Dimension Tables (Universities, Specialties, etc.)       │
│  • Fact Tables (Programs)                                   │
│  • pgvector for semantic search                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI REST API                           │
│  • Programs Endpoints                                        │
│  • Search & Analytics                                        │
│  • Match Simulation                                          │
│  • Reporting                                                 │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Warehouse (PostgreSQL + SQLModel)

**Design Pattern**: Star/Snowflake Schema

**Dimension Tables**:
- `dim_universities`: University information
- `dim_specialties`: Medical specialties with hierarchy
- `dim_requirements`: Program requirements
- `dim_training_sites`: Clinical training locations
- `dim_selection_criteria`: Selection criteria

**Fact Tables**:
- `fact_programs`: Core program information (main fact table)

**Key Features**:
- Surrogate keys for all tables
- Audit columns (created_at, updated_at)
- Soft delete support
- Proper foreign key constraints
- Optimized indexes

### 2. ETL Pipeline (Dagster)

**Asset Lineage**:
```
raw_program_descriptions_json ─┐
raw_program_descriptions_csv ──┼─> staging_programs ─> fact_programs
raw_program_master ────────────┤
raw_discipline ─────────────────┘
```

**Data Quality Checks**:
- Missing required fields validation
- Duplicate detection
- Data type validation
- Business rule validation
- Referential integrity checks

### 3. API Layer (FastAPI)

**API Design**:
- RESTful principles
- Auto-generated OpenAPI documentation
- Input validation with Pydantic
- Async database queries
- Proper error handling

**Endpoint Structure**:
- `/api/v1/programs` - Program CRUD and search
- `/api/v1/search` - Semantic search
- `/api/v1/analytics` - Analytics and reporting
- `/api/v1/simulation` - Match simulation
- `/api/v1/reports` - Report generation

## Technology Decisions

### Why SQLModel?

- Combines SQLAlchemy ORM with Pydantic validation
- Type-safe database models
- Automatic API schema generation
- Better developer experience

### Why Dagster?

- Asset-based data lineage
- Built-in data quality testing
- Web UI for monitoring
- Easy incremental updates
- Strong typing support

### Why FastAPI?

- High performance (ASGI)
- Auto-generated documentation
- Type hints throughout
- Easy async support
- Modern Python features

### Why PostgreSQL?

- ACID compliance
- Rich data types
- pgvector for semantic search
- Mature ecosystem
- CaRMS uses PostgreSQL-compatible databases

## Deployment Architecture (AWS)

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Cloud                             │
│                                                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │  S3 Bucket   │      │    RDS       │                │
│  │  (Raw Data)  │      │ PostgreSQL   │                │
│  └──────┬───────┘      └──────┬───────┘                │
│         │                     │                         │
│         ▼                     ▼                         │
│  ┌─────────────────────────────────────┐               │
│  │         ECS/Fargate Cluster         │               │
│  │  ┌──────────┐      ┌──────────┐    │               │
│  │  │ Dagster  │      │ FastAPI  │    │               │
│  │  │  Tasks   │      │ Service  │    │               │
│  │  └──────────┘      └──────────┘    │               │
│  └─────────────────────────────────────┘               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Ingestion**: Raw data loaded from files into Dagster assets
2. **Staging**: Data cleaned, parsed, and validated
3. **Loading**: Data inserted into warehouse dimensions and facts
4. **Serving**: API queries warehouse for real-time data access
5. **Analytics**: Derived metrics computed and cached

## Security Considerations

- Environment-based configuration
- Secrets stored in environment variables
- Database connection pooling
- Input validation on all API endpoints
- CORS configured appropriately
- SQL injection prevention via ORM

## Scalability

- Horizontal scaling via container orchestration
- Database connection pooling
- Async API endpoints
- Incremental ETL processing
- Caching strategies for analytics

---

This architecture is designed to be:
- **Maintainable**: Clear separation of concerns
- **Testable**: Unit and integration tests
- **Scalable**: Container-based deployment
- **Observable**: Logging and monitoring built-in
- **Production-ready**: Following industry best practices
