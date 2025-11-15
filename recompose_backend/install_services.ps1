# ReCompose AI - Service Installation Helper Script
# This script helps install PostgreSQL and Redis for Windows

Write-Host "ReCompose AI - Service Installation Helper" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

$installPostgres = $false
$installRedis = $false

# Check what's needed
Write-Host "Checking current service status..." -ForegroundColor Yellow
$pgRunning = Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
$redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue

if (-not $pgRunning) {
    Write-Host "[INFO] PostgreSQL is not running" -ForegroundColor Yellow
    $installPostgres = $true
} else {
    Write-Host "[OK] PostgreSQL is already running" -ForegroundColor Green
}

if (-not $redisRunning) {
    Write-Host "[INFO] Redis is not running" -ForegroundColor Yellow
    $installRedis = $true
} else {
    Write-Host "[OK] Redis is already running" -ForegroundColor Green
}

Write-Host ""

if (-not $installPostgres -and -not $installRedis) {
    Write-Host "All services are already running!" -ForegroundColor Green
    exit 0
}

Write-Host "Installation Options:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1: Manual Installation (Recommended)" -ForegroundColor Yellow
Write-Host "  - PostgreSQL: Download from https://www.postgresql.org/download/windows/" -ForegroundColor White
Write-Host "  - Redis: Download from https://github.com/microsoftarchive/redis/releases" -ForegroundColor White
Write-Host ""
Write-Host "Option 2: Using Chocolatey (if installed)" -ForegroundColor Yellow
if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "  Chocolatey is available!" -ForegroundColor Green
    if ($installPostgres) {
        Write-Host "  To install PostgreSQL: choco install postgresql" -ForegroundColor White
    }
    if ($installRedis) {
        Write-Host "  To install Redis: choco install redis-64" -ForegroundColor White
    }
} else {
    Write-Host "  Chocolatey not found. Install from: https://chocolatey.org/install" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Option 3: Using Docker (if installed)" -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "  Docker is available!" -ForegroundColor Green
    if ($installPostgres) {
        Write-Host "  To install PostgreSQL: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres --name recompose-postgres postgres:latest" -ForegroundColor White
    }
    if ($installRedis) {
        Write-Host "  To install Redis: docker run -d -p 6379:6379 --name recompose-redis redis:latest" -ForegroundColor White
    }
} else {
    Write-Host "  Docker not found. Install from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Option 4: Using WSL2 (Windows Subsystem for Linux)" -ForegroundColor Yellow
Write-Host "  If you have WSL2 installed, you can install PostgreSQL and Redis there" -ForegroundColor White
Write-Host "  See SETUP_GUIDE.md for WSL2 instructions" -ForegroundColor White
Write-Host ""

# Offer to open download pages
$response = Read-Host "Would you like to open download pages? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    if ($installPostgres) {
        Start-Process "https://www.postgresql.org/download/windows/"
    }
    if ($installRedis) {
        Start-Process "https://github.com/microsoftarchive/redis/releases"
    }
}

Write-Host ""
Write-Host "After installation, run: .\check_services.ps1" -ForegroundColor Cyan

