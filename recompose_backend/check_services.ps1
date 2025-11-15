# Service Health Check Script for ReCompose AI
# Checks if all required services are running

Write-Host "ReCompose AI - Service Health Check" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

$allServicesOk = $true

# Check PostgreSQL
Write-Host "Checking PostgreSQL..." -ForegroundColor Yellow
$pgRunning = Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
if ($pgRunning) {
    Write-Host "  [OK] PostgreSQL is running on port 5432" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] PostgreSQL is NOT running on port 5432" -ForegroundColor Red
    $allServicesOk = $false
}

# Check Redis
Write-Host "Checking Redis..." -ForegroundColor Yellow
$redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
if ($redisRunning) {
    Write-Host "  [OK] Redis is running on port 6379" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Redis is NOT running on port 6379" -ForegroundColor Red
    Write-Host "    Note: Redis is required for Celery background tasks" -ForegroundColor Yellow
    $allServicesOk = $false
}

# Check if .env file exists
Write-Host "Checking .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  [OK] .env file exists" -ForegroundColor Green
    
    # Check for required variables
    $envContent = Get-Content ".env" -Raw
    $requiredVars = @("DATABASE_URL", "OPENAI_API_KEY", "JWT_SECRET")
    $missingVars = @()
    
    foreach ($var in $requiredVars) {
        if ($envContent -notmatch "$var\s*=") {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -eq 0) {
        Write-Host "  [OK] All required environment variables are set" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Missing required variables: $($missingVars -join ', ')" -ForegroundColor Red
        $allServicesOk = $false
    }
} else {
    Write-Host "  [FAIL] .env file does not exist" -ForegroundColor Red
    Write-Host "    Create it from .env.example: Copy-Item .env.example .env" -ForegroundColor Yellow
    $allServicesOk = $false
}

Write-Host ""
if ($allServicesOk) {
    Write-Host "All services are ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run migrations: alembic upgrade head" -ForegroundColor Yellow
    Write-Host "2. Start backend: uvicorn app.main:app --reload" -ForegroundColor Yellow
    Write-Host "3. Start Celery worker: celery -A app.celery_app worker --loglevel=info" -ForegroundColor Yellow
    Write-Host "4. Start Celery beat: celery -A app.celery_app beat --loglevel=info" -ForegroundColor Yellow
} else {
    Write-Host "Some services are not ready. Please fix the issues above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Setup guides:" -ForegroundColor Cyan
    Write-Host "- Database: .\setup_database.ps1" -ForegroundColor Yellow
    Write-Host "- See SETUP_GUIDE.md for detailed instructions" -ForegroundColor Yellow
    exit 1
}
