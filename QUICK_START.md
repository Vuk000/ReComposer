# ReCompose AI - Quick Start Guide

## Prerequisites Check

Run this command to check what's needed:
```powershell
cd recompose_backend
.\check_services.ps1
```

## Installation Steps

### Step 1: Install PostgreSQL and Redis

**Option A: Using Chocolatey (Fastest)**
```powershell
# Install Chocolatey if not installed: https://chocolatey.org/install
choco install postgresql
choco install redis-64
```

**Option B: Manual Installation**
```powershell
# Run helper script
.\install_services.ps1

# Or download manually:
# PostgreSQL: https://www.postgresql.org/download/windows/
# Redis: https://github.com/microsoftarchive/redis/releases
```

**Option C: Using Docker**
```powershell
# PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres --name recompose-postgres postgres:latest

# Redis
docker run -d -p 6379:6379 --name recompose-redis redis:latest
```

### Step 2: Create Database

```powershell
# Run database setup script
.\setup_database.ps1

# Or manually:
psql -U postgres
CREATE DATABASE recompose;
\q
```

### Step 3: Configure Environment

```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env and set:
# - DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/recompose
# - OPENAI_API_KEY=sk-your-key-here
# - JWT_SECRET=(generate with: openssl rand -hex 32)
```

### Step 4: Run Migrations

```powershell
.\venv\Scripts\Activate.ps1
alembic upgrade head
```

### Step 5: Start Services

**Terminal 1 - Backend:**
```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Terminal 2 - Celery Worker:**
```powershell
.\venv\Scripts\Activate.ps1
celery -A app.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat:**
```powershell
.\venv\Scripts\Activate.ps1
celery -A app.celery_app beat --loglevel=info
```

**Terminal 4 - Frontend:**
```powershell
cd ..\frontend
npm run dev
```

### Step 6: Verify

1. Backend: http://localhost:8000/docs
2. Frontend: http://localhost:3000
3. Health Check: http://localhost:8000/health

## Troubleshooting

Run health check:
```powershell
.\check_services.ps1
```

See SETUP_GUIDE.md for detailed troubleshooting.

