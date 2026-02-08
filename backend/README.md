# GBP Audit Bot MVP - Backend

Sistema de monitoramento de rankings locais via Geogrid.

## Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Run server
uvicorn app.main:app --reload
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/gbp_check
SCALE_SERP_API_KEY=your_api_key
SECRET_KEY=your_jwt_secret
```
