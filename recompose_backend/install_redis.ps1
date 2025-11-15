# ReCompose AI - Redis Installation Script
# Attempts to install Redis using available methods

Write-Host "ReCompose AI - Redis Installation" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

$redisInstalled = $false

# Method 1: Check if Chocolatey is available
Write-Host "Method 1: Checking for Chocolatey..." -ForegroundColor Yellow
if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "  [OK] Chocolatey found!" -ForegroundColor Green
    Write-Host "  Attempting to install Redis via Chocolatey..." -ForegroundColor Yellow
    
    try {
        # Install Redis using Chocolatey
        choco install redis-64 -y --accept-license
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Redis installed via Chocolatey!" -ForegroundColor Green
            $redisInstalled = $true
        } else {
            Write-Host "  [FAIL] Chocolatey installation failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "  [FAIL] Error: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  [SKIP] Chocolatey not available" -ForegroundColor Yellow
}

# Method 2: Check if Docker is available
if (-not $redisInstalled) {
    Write-Host ""
    Write-Host "Method 2: Checking for Docker..." -ForegroundColor Yellow
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Host "  [OK] Docker found!" -ForegroundColor Green
        Write-Host "  Attempting to start Redis container..." -ForegroundColor Yellow
        
        try {
            # Check if container already exists
            $existing = docker ps -a --filter "name=recompose-redis" --format "{{.Names}}"
            if ($existing -eq "recompose-redis") {
                Write-Host "  [INFO] Redis container exists, starting it..." -ForegroundColor Yellow
                docker start recompose-redis
            } else {
                Write-Host "  Creating new Redis container..." -ForegroundColor Yellow
                docker run -d -p 6379:6379 --name recompose-redis redis:latest
            }
            
            Start-Sleep -Seconds 3
            $redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
            if ($redisRunning) {
                Write-Host "  [OK] Redis is running via Docker!" -ForegroundColor Green
                $redisInstalled = $true
            } else {
                Write-Host "  [FAIL] Redis container started but not responding" -ForegroundColor Red
            }
        } catch {
            Write-Host "  [FAIL] Error: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  [SKIP] Docker not available" -ForegroundColor Yellow
    }
}

# Method 3: Try to download and run Redis directly
if (-not $redisInstalled) {
    Write-Host ""
    Write-Host "Method 3: Manual Redis Setup..." -ForegroundColor Yellow
    Write-Host "  Redis for Windows can be downloaded from:" -ForegroundColor White
    Write-Host "  https://github.com/microsoftarchive/redis/releases" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Or use Memurai (Redis-compatible for Windows):" -ForegroundColor White
    Write-Host "  https://www.memurai.com/get-memurai" -ForegroundColor Cyan
    Write-Host ""
    
    $response = Read-Host "Would you like to open the Redis download page? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Start-Process "https://github.com/microsoftarchive/redis/releases"
    }
}

# Final check
Write-Host ""
Write-Host "Checking Redis status..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
$redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue

if ($redisRunning) {
    Write-Host "[OK] Redis is running on port 6379!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now start Celery worker and beat." -ForegroundColor Cyan
} else {
    Write-Host "[FAIL] Redis is not running on port 6379" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Redis manually and try again." -ForegroundColor Yellow
    Write-Host "See SETUP_GUIDE.md for detailed instructions." -ForegroundColor Yellow
}

