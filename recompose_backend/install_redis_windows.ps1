# ReCompose AI - Redis Installation for Windows
# Downloads and sets up Redis for Windows

Write-Host "ReCompose AI - Redis Installation (Windows)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$redisDir = "$PSScriptRoot\redis"
$redisUrl = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"

Write-Host "This script will help you install Redis for Windows." -ForegroundColor Yellow
Write-Host ""

# Check if Redis is already installed
if (Test-Path "$redisDir\redis-server.exe") {
    Write-Host "[INFO] Redis appears to be installed at: $redisDir" -ForegroundColor Yellow
    $useExisting = Read-Host "Use existing installation? (y/n)"
    if ($useExisting -eq "y" -or $useExisting -eq "Y") {
        Write-Host "Starting Redis server..." -ForegroundColor Yellow
        Start-Process -FilePath "$redisDir\redis-server.exe" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        
        $redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        if ($redisRunning) {
            Write-Host "[OK] Redis is running!" -ForegroundColor Green
            exit 0
        }
    }
}

Write-Host "Installation Options:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1: Download Redis for Windows (Recommended)" -ForegroundColor Yellow
Write-Host "  Download from: $redisUrl" -ForegroundColor White
Write-Host "  Extract to: $redisDir" -ForegroundColor White
Write-Host "  Run: .\redis\redis-server.exe" -ForegroundColor White
Write-Host ""

Write-Host "Option 2: Use Memurai (Redis-compatible, easier install)" -ForegroundColor Yellow
Write-Host "  Download from: https://www.memurai.com/get-memurai" -ForegroundColor White
Write-Host "  Memurai is a Redis-compatible server for Windows with installer" -ForegroundColor Gray
Write-Host ""

Write-Host "Option 3: Use WSL2 (if available)" -ForegroundColor Yellow
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    Write-Host "  WSL2 is available!" -ForegroundColor Green
    Write-Host "  Run in WSL: sudo apt-get update && sudo apt-get install redis-server" -ForegroundColor White
    Write-Host "  Then start: sudo service redis-server start" -ForegroundColor White
} else {
    Write-Host "  WSL2 not available" -ForegroundColor Gray
}
Write-Host ""

$choice = Read-Host "Would you like to open the Redis download page? (y/n)"
if ($choice -eq "y" -or $choice -eq "Y") {
    Start-Process "https://github.com/microsoftarchive/redis/releases"
    Write-Host ""
    Write-Host "After downloading:" -ForegroundColor Cyan
    Write-Host "  1. Extract the ZIP file" -ForegroundColor White
    Write-Host "  2. Copy redis-server.exe to: $redisDir" -ForegroundColor White
    Write-Host "  3. Run: .\start_redis.ps1" -ForegroundColor White
}

Write-Host ""
Write-Host "For quick testing, you can also use fakeredis (Python mock):" -ForegroundColor Yellow
Write-Host "  pip install fakeredis" -ForegroundColor White
Write-Host "  (Note: This is for testing only, not production)" -ForegroundColor Gray

