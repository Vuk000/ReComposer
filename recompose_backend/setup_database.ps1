# PostgreSQL Database Setup Script for ReCompose AI
# This script helps set up the PostgreSQL database

Write-Host "ReCompose AI - Database Setup Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is installed
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlPath) {
    Write-Host "ERROR: PostgreSQL is not installed or not in PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install PostgreSQL from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    Write-Host "Or use Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:latest" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "PostgreSQL found at: $($psqlPath.Source)" -ForegroundColor Green
Write-Host ""

# Prompt for database credentials
Write-Host "Please provide PostgreSQL connection details:" -ForegroundColor Yellow
$dbHost = Read-Host "Database host (default: localhost)"
if ([string]::IsNullOrWhiteSpace($dbHost)) { $dbHost = "localhost" }

$dbPort = Read-Host "Database port (default: 5432)"
if ([string]::IsNullOrWhiteSpace($dbPort)) { $dbPort = "5432" }

$dbUser = Read-Host "Database user (default: postgres)"
if ([string]::IsNullOrWhiteSpace($dbUser)) { $dbUser = "postgres" }

$dbPassword = Read-Host "Database password" -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword))

$dbName = Read-Host "Database name (default: recompose)"
if ([string]::IsNullOrWhiteSpace($dbName)) { $dbName = "recompose" }

Write-Host ""
Write-Host "Creating database '$dbName'..." -ForegroundColor Cyan

# Set PGPASSWORD environment variable for psql
$env:PGPASSWORD = $dbPasswordPlain

# Create database
$createDbQuery = "CREATE DATABASE $dbName;"
try {
    $result = & psql -h $dbHost -p $dbPort -U $dbUser -d postgres -c $createDbQuery 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database '$dbName' created successfully!" -ForegroundColor Green
    } else {
        if ($result -match "already exists") {
            Write-Host "Database '$dbName' already exists. Continuing..." -ForegroundColor Yellow
        } else {
            Write-Host "Error creating database: $result" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
} finally {
    # Clear password from environment
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Database setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Update your .env file with:" -ForegroundColor Yellow
Write-Host "DATABASE_URL=postgresql+asyncpg://$dbUser`:$dbPasswordPlain@$dbHost`:$dbPort/$dbName" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then run: alembic upgrade head" -ForegroundColor Yellow

