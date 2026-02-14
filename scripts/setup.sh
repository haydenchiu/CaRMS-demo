#!/usr/bin/env bash
# Quick setup script for local development

set -e

echo "🚀 CaRMS Platform - Quick Setup"
echo "================================"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. You'll need Docker to run the full stack."
    echo "   Install from: https://www.docker.com/get-started"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -e ".[dev]"

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://carms:carms@localhost:5432/carms

# OpenAI (optional for Phase 3)
OPENAI_API_KEY=

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=false

# Dagster
DAGSTER_HOME=/opt/dagster/dagster_home

# Data paths
DATA_DIR=data

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
EOF
    echo "✅ .env file created. Update with your settings."
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start Docker services: cd docker && docker-compose up -d"
echo "2. Initialize database: python scripts/init_db.py"
echo "3. Access Dagster UI: http://localhost:3000"
echo "4. Access API docs: http://localhost:8000/docs"
echo ""
echo "Or run services locally:"
echo "- Dagster: dagster dev -m src.dagster_project"
echo "- API: uvicorn src.api.main:app --reload"
