# 🗺️ GBP Audit Bot - Local Ranking Monitoring System

**GBP Audit Bot** is a comprehensive geogrid-based local ranking monitoring system designed to track Google Business Profile (GBP) visibility across geographic areas. The system generates coordinate grids, performs SERP searches at each point, and provides detailed analytics with AI-powered insights.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)

## ✨ Features

### Core Functionality
- **🔍 Grid Generation** - Generate coordinate grids (3x3, 5x5, 7x7) around a central location
- **📊 SERP Search** - Search business rankings at each grid point using ScaleSERP API
- **📈 Metrics Calculation**
  - **ARP (Average Rank Position)** - Mean ranking across all grid points
  - **Top 3 Count** - Number of grid points where business ranks in top 3
  - **Top 10 Count** - Number of grid points where business ranks in top 10
  - **Visibility Score** - Weighted score based on ranking distribution

### Advanced Features
- **🤖 AI Analysis** - OpenAI-powered weekly comparison reports with actionable insights
- **📄 PDF Reports** - Automated PDF generation with heatmaps and metrics
- **📱 WhatsApp Integration** - Scheduled weekly reports sent to client WhatsApp groups
- **⏰ Automated Scheduling** - APScheduler-based cron jobs for weekly scans and reports
- **👥 Multi-User Support** - User authentication with JWT and credit-based system
- **🎨 Interactive Dashboard** - Next.js frontend with Leaflet maps and Recharts visualizations

## 🏗️ Architecture

### Technology Stack

#### Backend
- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (python-jose)
- **Task Scheduling**: APScheduler
- **PDF Generation**: ReportLab + StaticMap
- **AI Integration**: OpenAI API
- **SERP API**: ScaleSERP

#### Frontend
- **Framework**: Next.js 16.1.6 (React 19)
- **Styling**: TailwindCSS 4
- **Maps**: Leaflet + React-Leaflet
- **Charts**: Recharts
- **Icons**: Lucide React
- **Screenshots**: html2canvas

### Project Structure

```
gbp/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── routers/         # FastAPI route handlers
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   ├── projects.py  # Project CRUD
│   │   │   ├── grid.py      # Grid generation
│   │   │   ├── search.py    # SERP search execution
│   │   │   └── reports.py   # Weekly reports & PDF
│   │   ├── services/        # Business logic
│   │   │   ├── geogrid.py   # Coordinate grid generation
│   │   │   ├── serp.py      # ScaleSERP API integration
│   │   │   ├── heatmap.py   # Heatmap generation
│   │   │   ├── ai_analysis.py  # OpenAI integration
│   │   │   ├── pdf_report.py   # PDF generation
│   │   │   ├── whatsapp.py     # WhatsApp API integration
│   │   │   └── scheduler.py    # Cron job scheduler
│   │   ├── auth.py          # JWT authentication utilities
│   │   ├── config.py        # Settings management
│   │   ├── database.py      # Database connection
│   │   ├── schemas.py       # Pydantic models
│   │   └── main.py          # Application entry point
│   ├── tests/               # Pytest test suite
│   ├── requirements.txt     # Python dependencies
│   └── init_db.py          # Database initialization
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js app router
│   │   │   ├── page.tsx     # Dashboard
│   │   │   ├── login/       # Login page
│   │   │   ├── register/    # Registration page
│   │   │   ├── search/      # Search execution
│   │   │   ├── scan/        # Scan results
│   │   │   └── settings/    # Project settings
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts (Auth)
│   │   └── lib/             # Utilities
│   └── package.json         # Node dependencies
├── README.md                # This file
├── CONTRIBUTING.md          # Contribution guidelines
└── SECURITY.md              # Security policy
```

## 📦 Prerequisites

### Backend Requirements
- **Python**: 3.10 or higher
- **PostgreSQL**: 14 or higher
- **API Keys**:
  - ScaleSERP API key ([Get one here](https://www.scaleserp.com/))
  - OpenAI API key ([Get one here](https://platform.openai.com/))
  - WhatsApp API URL (optional, for automated reports)

### Frontend Requirements
- **Node.js**: 18 or higher
- **npm**: 9 or higher

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd gbp
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Edit .env with your configuration
# (See Configuration section below)

# Initialize database
python init_db.py

# Run migrations (if using Alembic)
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## ⚙️ Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/gbp_check

# API Keys
SCALE_SERP_API_KEY=your_scale_serp_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# WhatsApp Integration (Optional)
WHATSAPP_API_URL=https://your-whatsapp-api.com/send
WHATSAPP_API_TOKEN=your_whatsapp_token

# Security
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Scheduler (Optional)
WEEKLY_REPORT_CRON=0 9 * * 1  # Every Monday at 9 AM
```

### Database Setup

1. **Install PostgreSQL** if not already installed
2. **Create database**:
   ```sql
   CREATE DATABASE gbp_check;
   ```
3. **Run initialization script**:
   ```bash
   python init_db.py
   ```

## 📖 Usage

### 1. User Registration

```bash
# Via API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword"
  }'
```

Or use the frontend at `http://localhost:3000/register`

### 2. Login

```bash
# Via API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

Or use the frontend at `http://localhost:3000/login`

### 3. Create a Project

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "My Coffee Shop",
    "target_keyword": "coffee shop near me",
    "central_lat": 40.7128,
    "central_lng": -74.0060,
    "default_radius_km": 5.0,
    "default_grid_size": 5
  }'
```

### 4. Execute a Grid Search

```bash
curl -X POST http://localhost:8000/api/search/execute \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "PROJECT_UUID",
    "grid_size": 5,
    "radius_km": 5.0
  }'
```

### 5. Generate Weekly Report

```bash
curl -X POST http://localhost:8000/api/reports/weekly/PROJECT_UUID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 6. Download PDF Report

```bash
curl -X GET http://localhost:8000/api/reports/pdf/SCAN_UUID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  --output report.pdf
```

## 📚 API Documentation

### Interactive Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Main Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

#### Projects
- `POST /api/projects` - Create new project
- `GET /api/projects` - List user's projects
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

#### Grid Generation
- `POST /api/grid/generate` - Generate coordinate grid

#### Search/Scans
- `POST /api/search/execute` - Execute grid search
- `GET /api/search/scans/{project_id}` - List project scans
- `GET /api/search/scan/{scan_id}` - Get scan details
- `POST /api/search/estimate` - Estimate credit cost

#### Reports
- `POST /api/reports/weekly/{project_id}` - Generate weekly comparison
- `GET /api/reports/pdf/{scan_id}` - Download PDF report
- `POST /api/reports/whatsapp/{scan_id}` - Send report via WhatsApp

## 🗄️ Database Schema

### Users
- `id` (UUID, PK)
- `email` (String, Unique)
- `name` (String)
- `hashed_password` (String)
- `credits_balance` (Integer)
- `is_active` (Boolean)
- `created_at` (DateTime)

### Projects
- `id` (UUID, PK)
- `user_id` (UUID, FK → Users)
- `business_name` (String)
- `target_keyword` (String)
- `place_id` (String, Optional)
- `central_lat` (Decimal)
- `central_lng` (Decimal)
- `default_radius_km` (Decimal)
- `default_grid_size` (Integer)
- `weekly_actions` (Text, Optional)
- `whatsapp_group_id` (String, Optional)
- `whatsapp_enabled` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Scans
- `id` (UUID, PK)
- `project_id` (UUID, FK → Projects)
- `keyword` (String)
- `grid_size` (Integer)
- `radius_km` (Decimal)
- `credits_used` (Integer)
- `average_rank` (Decimal, Optional)
- `top3_count` (Integer)
- `top10_count` (Integer)
- `visibility_score` (Decimal, Optional)
- `status` (String)
- `executed_at` (DateTime)

### ScanPoints
- `id` (UUID, PK)
- `scan_id` (UUID, FK → Scans)
- `grid_x` (Integer)
- `grid_y` (Integer)
- `latitude` (Decimal)
- `longitude` (Decimal)
- `rank_position` (Integer, Optional)
- `serp_data` (JSON, Optional)

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 🔒 Security

Please read [SECURITY.md](SECURITY.md) for information about reporting security vulnerabilities.

## 📄 License

This project is proprietary software. All rights reserved.

## 🙏 Acknowledgments

- **ScaleSERP** - SERP API provider
- **OpenAI** - AI analysis capabilities
- **Leaflet** - Interactive mapping
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework

## 📞 Support

For support, please contact the development team or open an issue in the repository.

---

**Made with ❤️ by Juan Silva**
