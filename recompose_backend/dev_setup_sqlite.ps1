# Development Setup Script - Uses SQLite for testing without PostgreSQL
# This allows testing the application without installing PostgreSQL

Write-Host "ReCompose AI - Development Setup (SQLite Mode)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script sets up the application to use SQLite instead of PostgreSQL" -ForegroundColor Yellow
Write-Host "for development/testing purposes." -ForegroundColor Yellow
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env -ErrorAction SilentlyContinue
}

# Read .env file
$envContent = Get-Content ".env" -Raw -ErrorAction SilentlyContinue
if (-not $envContent) {
    Write-Host "ERROR: Could not read .env file" -ForegroundColor Red
    exit 1
}

# Generate JWT secret if not set
if ($envContent -notmatch "JWT_SECRET\s*=\s*[^\s]") {
    $jwtSecret = python -c "import secrets; print(secrets.token_hex(32))" 2>&1 | Select-Object -Last 1
    $envContent = $envContent -replace "(JWT_SECRET\s*=).*", "`$1$jwtSecret"
    Write-Host "Generated JWT_SECRET" -ForegroundColor Green
}

# Set SQLite database URL for development
$sqliteUrl = "sqlite+aiosqlite:///./dev_recompose.db"
if ($envContent -match "DATABASE_URL\s*=") {
    $envContent = $envContent -replace "(DATABASE_URL\s*=).*", "`$1$sqliteUrl"
    Write-Host "Set DATABASE_URL to SQLite: $sqliteUrl" -ForegroundColor Green
} else {
    $envContent += "`nDATABASE_URL=$sqliteUrl`n"
    Write-Host "Added DATABASE_URL to .env" -ForegroundColor Green
}

# Set debug mode
$envContent = $envContent -replace "(DEBUG\s*=).*", "`$1True"
Write-Host "Set DEBUG=True" -ForegroundColor Green

# Set test OpenAI key if not set
if ($envContent -notmatch "OPENAI_API_KEY\s*=\s*[^\s]") {
    $envContent = $envContent -replace "(OPENAI_API_KEY\s*=).*", "`$1test-key-for-development"
    Write-Host "Set test OPENAI_API_KEY (replace with real key for production)" -ForegroundColor Yellow
}

# Write back to .env
Set-Content -Path ".env" -Value $envContent -NoNewline

Write-Host ""
Write-Host "Development setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Note: This uses SQLite instead of PostgreSQL." -ForegroundColor Yellow
Write-Host "For production, use PostgreSQL and update DATABASE_URL in .env" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create tables: python -c 'from app.db import Base, engine; import asyncio; asyncio.run(engine.begin()).run_sync(Base.metadata.create_all)'" -ForegroundColor White
Write-Host "2. Start backend: uvicorn app.main:app --reload" -ForegroundColor White

