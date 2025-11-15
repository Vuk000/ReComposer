# Redis Setup for ReCompose AI

Redis is required for Celery background tasks. This guide provides multiple installation options for Windows.

## Quick Installation Options

### Option 1: Memurai (Easiest - Recommended)
Memurai is a Redis-compatible server for Windows with a simple installer.

1. Download from: https://www.memurai.com/get-memurai
2. Run the installer
3. Memurai will start automatically as a Windows service
4. Verify: `Test-NetConnection -ComputerName localhost -Port 6379`

### Option 2: Redis for Windows (Manual)
1. Download Redis for Windows from: https://github.com/microsoftarchive/redis/releases
2. Download: `Redis-x64-3.0.504.zip` (or latest version)
3. Extract to: `C:\Business\ReCompose\recompose_backend\redis\`
4. Run: `.\redis\redis-server.exe`
5. Or use: `.\start_redis.ps1`

### Option 3: Docker (If Available)
```powershell
docker run -d -p 6379:6379 --name recompose-redis redis:latest
```

### Option 4: Chocolatey (If Installed)
```powershell
choco install redis-64 -y
```

### Option 5: WSL2 (If Available)
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo service redis-server start
```

## Verification

After installation, verify Redis is running:

```powershell
# Check if Redis is listening on port 6379
Test-NetConnection -ComputerName localhost -Port 6379

# Or use the check script
.\check_services.ps1
```

## Starting Celery

Once Redis is running, start Celery services:

```powershell
.\start_celery.ps1
```

This will start:
- Celery Worker (processes background tasks)
- Celery Beat (schedules periodic tasks)

## Troubleshooting

### Redis Not Starting
- Check if port 6379 is already in use
- Ensure Redis executable has proper permissions
- Check Windows Firewall settings

### Celery Connection Errors
- Verify Redis is running: `Test-NetConnection -ComputerName localhost -Port 6379`
- Check `.env` file has correct `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`
- Default: `redis://localhost:6379/0`

## Development Without Redis

For development/testing without Redis:
- The main API will work fine
- Celery background tasks will be disabled
- Email sending and campaign processing won't work
- All other features remain functional

