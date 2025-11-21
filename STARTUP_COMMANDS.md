# Complete Startup Commands for ReCompose AI

## ✅ Your Environment is Ready

All services are configured to use:
- **Neon PostgreSQL** with asyncpg
- **OpenAI** for AI rewriting
- **Brevo** for email sending
- **Stripe** for payments
- **Redis Cloud** for Celery background tasks

## 📝 Important Note about DATABASE_URL

Your Neon connection string should use `ssl=require` (not `sslmode=require`) for asyncpg:

```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:***@ep-***.aws.neon.tech/neondb?ssl=require
```

If your current DATABASE_URL has `sslmode=require`, change it to `ssl=require`.

## 🚀 Commands to Run

### Step 1: Apply Database Migrations

```powershell
cd C:\Business\ReCompose\recompose_backend
.\venv\Scripts\Activate.ps1
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial migration
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add content fields
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, Add subscription fields
INFO  [alembic.runtime.migration] Running upgrade 003 -> 004, Add campaign tables
INFO  [alembic.runtime.migration] Running upgrade 004 -> 005 (head), Add CLICK event type
```

### Step 2: Start Backend Server (Terminal 1)

```powershell
cd C:\Business\ReCompose\recompose_backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify:** Open http://localhost:8000/health

### Step 3: Start Celery Worker (Terminal 2)

```powershell
cd C:\Business\ReCompose\recompose_backend
.\venv\Scripts\Activate.ps1
celery -A app.celery_app worker --loglevel=info --pool=solo
```

**Note:** `--pool=solo` is required on Windows.

### Step 4: Start Celery Beat (Terminal 3)

```powershell
cd C:\Business\ReCompose\recompose_backend
.\venv\Scripts\Activate.ps1
celery -A app.celery_app beat --loglevel=info
```

### Step 5: Start Frontend (Terminal 4)

```powershell
cd C:\Business\ReCompose\frontend-react
npm run dev
```

**Access:** http://localhost:5173

## 🔧 Troubleshooting

### If migrations fail with SSL error:

Your DATABASE_URL might have `sslmode=require`. Change it to:
```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:***@ep-***.aws.neon.tech/neondb?ssl=require
```

### If Celery can't connect to Redis:

Verify your Redis Cloud URL format:
```env
CELERY_BROKER_URL=redis://default:password@host:port
CELERY_RESULT_BACKEND=redis://default:password@host:port
```

### If frontend can't connect to backend:

Check CORS_ORIGINS in your .env:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## ✅ Testing Checklist

Once all services are running:

1. **Health Check**: http://localhost:8000/health
2. **API Docs**: http://localhost:8000/docs
3. **Frontend**: http://localhost:5173
4. **Signup**: Create a test account
5. **Login**: Test authentication
6. **AI Rewrite**: Test email rewriting
7. **Campaign**: Create and launch a test campaign

## 📊 All Features Wired

- ✅ **Database**: Neon PostgreSQL via `settings.DATABASE_URL`
- ✅ **AI**: OpenAI GPT-4o via `settings.OPENAI_API_KEY`
- ✅ **Email**: Brevo via `settings.BREVO_API_KEY`
- ✅ **Payments**: Stripe via `settings.STRIPE_SECRET_KEY`
- ✅ **Background Tasks**: Redis via `settings.CELERY_BROKER_URL`
- ✅ **Tracking**: Via `settings.BACKEND_URL`

Everything is ready to run!

