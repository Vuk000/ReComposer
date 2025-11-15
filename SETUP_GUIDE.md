# ReCompose AI - Setup Guide

This guide will help you set up the ReCompose AI application from scratch.

## Prerequisites

Before starting, ensure you have:
- Python 3.11 or higher
- PostgreSQL database server
- Redis server (for Celery background tasks)
- Node.js and npm (for frontend development server)
- OpenAI API key

## Step 1: Environment Configuration

1. Navigate to the `recompose_backend` directory
2. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Edit `.env` and configure the following **required** variables:
   - `DATABASE_URL`: PostgreSQL connection string
     - Format: `postgresql+asyncpg://username:password@localhost:5432/recompose`
     - Example: `postgresql+asyncpg://postgres:mypassword@localhost:5432/recompose`
   - `OPENAI_API_KEY`: Your OpenAI API key
     - Get it from: https://platform.openai.com/api-keys
   - `JWT_SECRET`: A strong random string (minimum 32 characters)
     - Generate with: `openssl rand -hex 32`
     - Or use: `python -c "import secrets; print(secrets.token_hex(32))"`

## Step 2: Database Setup

### Install PostgreSQL (if not installed)

**Windows:**
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the postgres user password you set during installation

**Create Database:**
```powershell
# Connect to PostgreSQL (replace 'postgres' with your username)
psql -U postgres

# Create database
CREATE DATABASE recompose;

# Create user (optional, or use existing postgres user)
CREATE USER recompose_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE recompose TO recompose_user;

# Exit psql
\q
```

### Update .env with Database Credentials

Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/recompose
```

## Step 3: Redis Setup (for Celery)

### Install Redis (if not installed)

**Windows:**
1. Download Redis for Windows from: https://github.com/microsoftarchive/redis/releases
2. Or use WSL2 with Redis
3. Or use Docker: `docker run -d -p 6379:6379 redis:latest`

**Start Redis:**
- If installed as service, it should start automatically
- If using Docker, the container should be running
- Verify Redis is running:
  ```powershell
  redis-cli ping
  # Should return: PONG
  ```

## Step 4: Backend Setup

1. Navigate to `recompose_backend` directory:
   ```powershell
   cd recompose_backend
   ```

2. Create Python virtual environment:
   ```powershell
   python -m venv venv
   ```

3. Activate virtual environment:
   ```powershell
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   
   # Windows CMD
   venv\Scripts\activate.bat
   ```

4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

5. Run database migrations:
   ```powershell
   alembic upgrade head
   ```

6. Start the backend server:
   ```powershell
   # Option 1: Use the startup script
   .\start_app.ps1
   
   # Option 2: Manual start
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. Verify backend is running:
   - Open browser: http://localhost:8000/docs
   - Check health endpoint: http://localhost:8000/health

## Step 5: Celery Setup (for Background Tasks)

Open a **new terminal** window and activate the virtual environment:

1. Start Celery worker:
   ```powershell
   cd recompose_backend
   .\venv\Scripts\Activate.ps1
   celery -A app.celery_app worker --loglevel=info
   ```

2. Start Celery beat (in another terminal):
   ```powershell
   cd recompose_backend
   .\venv\Scripts\Activate.ps1
   celery -A app.celery_app beat --loglevel=info
   ```

## Step 6: Frontend Setup

1. Navigate to `frontend` directory:
   ```powershell
   cd frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Start frontend server:
   ```powershell
   npm run dev
   ```

4. Frontend will be available at: http://localhost:3000

## Step 7: Verify Installation

1. **Backend Health Check:**
   - Visit: http://localhost:8000/health
   - Should return: `{"status":"healthy","version":"1.0.0","database":"connected"}`

2. **API Documentation:**
   - Visit: http://localhost:8000/docs
   - Should show Swagger UI

3. **Frontend:**
   - Visit: http://localhost:3000
   - Should show landing page

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running:
  ```powershell
  # Check if PostgreSQL service is running
  Get-Service postgresql*
  ```
- Verify database exists:
  ```powershell
  psql -U postgres -l
  ```
- Check connection string format in `.env`

### Redis Connection Issues

- Verify Redis is running:
  ```powershell
  redis-cli ping
  ```
- Check Redis URL in `.env` matches your Redis setup

### Port Already in Use

- Backend (port 8000): Change port in startup command or kill process using port
- Frontend (port 3000): Change port in `package.json` or kill process
- Redis (port 6379): Check if Redis is already running

### Migration Errors

- Ensure database exists and user has proper permissions
- Check `DATABASE_URL` in `.env` is correct
- Try: `alembic downgrade -1` then `alembic upgrade head`

## Next Steps

After setup is complete:
1. Test user signup/login
2. Test email rewriting functionality
3. Create contacts and campaigns
4. Review API documentation at `/docs`

## Support

For issues or questions, check:
- Backend README: `recompose_backend/README.md`
- Frontend README: `frontend/README.md`
- API Documentation: http://localhost:8000/docs

