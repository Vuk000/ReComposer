# --- Startup Script (Windows PowerShell) ---
# Run Alembic migrations
Write-Host "Running database migrations..."
alembic upgrade head

# Start the FastAPI application
Write-Host "Starting FastAPI application..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

