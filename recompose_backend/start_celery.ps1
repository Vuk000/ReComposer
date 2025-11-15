# ReCompose AI - Start Celery Worker and Beat
# Starts Celery worker and beat scheduler for background tasks

Write-Host "ReCompose AI - Starting Celery Services" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Redis is running
Write-Host "Checking Redis connection..." -ForegroundColor Yellow
$redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue

if (-not $redisRunning) {
    Write-Host "[FAIL] Redis is not running on port 6379" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install and start Redis first:" -ForegroundColor Yellow
    Write-Host "  1. Run: .\install_redis.ps1" -ForegroundColor White
    Write-Host "  2. Or install Redis manually from:" -ForegroundColor White
    Write-Host "     https://github.com/microsoftarchive/redis/releases" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "For development without Redis, Celery tasks will be disabled." -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Redis is running" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[FAIL] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting Celery Worker..." -ForegroundColor Yellow
Write-Host "  (This will run in a separate window)" -ForegroundColor Gray

# Start Celery worker in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; celery -A app.celery_app worker --loglevel=info --pool=solo" -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host "Starting Celery Beat..." -ForegroundColor Yellow
Write-Host "  (This will run in a separate window)" -ForegroundColor Gray

# Start Celery beat in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; celery -A app.celery_app beat --loglevel=info" -WindowStyle Normal

Write-Host ""
Write-Host "[OK] Celery services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Note: Two PowerShell windows have been opened:" -ForegroundColor Cyan
Write-Host "  - Celery Worker (processes background tasks)" -ForegroundColor White
Write-Host "  - Celery Beat (schedules periodic tasks)" -ForegroundColor White
Write-Host ""
Write-Host "To stop Celery services, close the PowerShell windows." -ForegroundColor Yellow

