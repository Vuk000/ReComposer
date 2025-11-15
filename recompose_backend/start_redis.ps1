# ReCompose AI - Start Redis Server
# Starts Redis server if installed locally

Write-Host "ReCompose AI - Starting Redis Server" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$redisDir = "$PSScriptRoot\redis"
$redisExe = "$redisDir\redis-server.exe"

# Check if Redis is already running
$redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
if ($redisRunning) {
    Write-Host "[OK] Redis is already running on port 6379" -ForegroundColor Green
    exit 0
}

# Check if Redis is installed locally
if (Test-Path $redisExe) {
    Write-Host "[OK] Found Redis installation at: $redisDir" -ForegroundColor Green
    Write-Host "Starting Redis server..." -ForegroundColor Yellow
    
    # Start Redis server
    Start-Process -FilePath $redisExe -WindowStyle Minimized
    
    # Wait for Redis to start
    Write-Host "Waiting for Redis to start..." -ForegroundColor Yellow
    $maxAttempts = 10
    $attempt = 0
    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 1
        $redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        if ($redisRunning) {
            Write-Host "[OK] Redis is now running on port 6379!" -ForegroundColor Green
            exit 0
        }
        $attempt++
    }
    
    Write-Host "[FAIL] Redis did not start within $maxAttempts seconds" -ForegroundColor Red
    exit 1
} else {
    Write-Host "[FAIL] Redis not found at: $redisExe" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Redis first:" -ForegroundColor Yellow
    Write-Host "  Run: .\install_redis_windows.ps1" -ForegroundColor White
    Write-Host "  Or download from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor White
    exit 1
}

