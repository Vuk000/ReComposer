# Starting ReCompose AI Services

This guide shows how to start all services for end-to-end testing.

## Prerequisites

✅ All environment variables are set in `recompose_backend/.env`:
- DATABASE_URL (Neon PostgreSQL with `postgresql+asyncpg://` and `?ssl=require`)
- OPENAI_API_KEY or ANTHROPIC_API_KEY
- BREVO_API_KEY, BREVO_SMTP_USERNAME, BREVO_SMTP_PASSWORD
- STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
- JWT_SECRET (64+ characters)
- ENCRYPTION_KEY
- CELERY_BROKER_URL (Redis Cloud)
- CELERY_RESULT_BACKEND (Redis Cloud)
- BACKEND_URL (for tracking)
- FRONTEND_URL (for CORS)

## Step 1: Verify Environment

```powershell
cd recompose_backend
python verify_env.py
```

This will check all required environment variables are set.

## Step 2: Run Database Migrations

**IMPORTANT:** Ensure your `.env` file has the correct Neon PostgreSQL DATABASE_URL:

```env
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?ssl=require
```

Then run migrations:

```powershell
cd recompose_backend
.\venv\Scripts\Activate.ps1
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial migration...
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add content fields...
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, Add subscription fields...
INFO  [alembic.runtime.migration] Running upgrade 003 -> 004, Add campaign tables...
INFO  [alembic.runtime.migration] Running upgrade 004 -> 005, Add CLICK event type...
```

If you see `SQLiteImpl` instead of `PostgresqlImpl`, your DATABASE_URL is pointing to SQLite. Update your `.env` file.

## Step 3: Start Services

Open **4 separate PowerShell terminals**:

### Terminal 1: Backend API Server

```powershell
cd recompose_backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify:** Open http://localhost:8000/health in browser. Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "openai": "configured",
  "redis": "connected"
}
```

### Terminal 2: Celery Worker

```powershell
cd recompose_backend
.\venv\Scripts\Activate.ps1
celery -A app.celery_app worker --loglevel=info --pool=solo
```

**Expected Output:**
```
[2025-11-21 12:00:00,000: INFO/MainProcess] Connected to redis://...
[2025-11-21 12:00:00,000: INFO/MainProcess] celery@hostname ready.
```

**Note:** `--pool=solo` is required on Windows. On Linux/Mac, you can use `--pool=prefork` (default).

### Terminal 3: Celery Beat (Scheduled Tasks)

```powershell
cd recompose_backend
.\venv\Scripts\Activate.ps1
celery -A app.celery_app beat --loglevel=info
```

**Expected Output:**
```
[2025-11-21 12:00:00,000: INFO/MainProcess] Scheduler: Sending due task process-pending-emails
[2025-11-21 12:00:00,000: INFO/MainProcess] Scheduler: Sending due task check-replies
```

### Terminal 4: Frontend Development Server

```powershell
cd frontend-react
npm run dev
```

**Expected Output:**
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## Step 4: Verify All Services

1. **Backend Health:** http://localhost:8000/health
2. **API Docs:** http://localhost:8000/docs
3. **Frontend:** http://localhost:5173

## Troubleshooting

### Database Connection Issues

**Error:** `Context impl SQLiteImpl` instead of `PostgresqlImpl`

**Solution:** Check your `.env` file DATABASE_URL:
- Must start with `postgresql+asyncpg://`
- Must include `?ssl=require` for Neon
- Format: `postgresql+asyncpg://user:pass@host:port/dbname?ssl=require`

### Celery Can't Connect to Redis

**Error:** `Error connecting to Redis`

**Solution:**
1. Verify `CELERY_BROKER_URL` in `.env` is correct
2. Format: `redis://user:password@host:port/db` or `redis://:password@host:port/db`
3. Test Redis connection: `redis-cli -h host -p port -a password ping`

### Brevo Email Sending Fails

**Error:** `Brevo SMTP password not configured`

**Solution:**
1. Verify `BREVO_SMTP_PASSWORD` is set (SMTP key, not account password)
2. Verify `BREVO_SMTP_USERNAME` is your Brevo account email
3. Check Brevo dashboard for SMTP credentials

### Frontend Can't Connect to Backend

**Error:** CORS errors in browser console

**Solution:**
1. Verify `CORS_ORIGINS` in `.env` includes `http://localhost:5173`
2. Restart backend server after changing `.env`

## Next Steps

Once all services are running:

1. **Test Authentication:**
   - Navigate to http://localhost:5173/signup
   - Create an account
   - Verify login works

2. **Test AI Rewrite:**
   - Navigate to Rewrite page
   - Enter email text and select tone
   - Verify AI rewrite appears

3. **Test Campaign:**
   - Create a contact
   - Create a campaign with email steps
   - Launch campaign
   - Verify email is sent via Brevo

4. **Test Tracking:**
   - Open email and check tracking pixel loads
   - Click link and verify redirect works
   - Check campaign stats update

