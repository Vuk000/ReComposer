# API Testing Script for ReCompose AI
# Tests all API endpoints

$baseUrl = "http://localhost:8000"
$testEmail = "test$(Get-Random)@example.com"
$testPassword = "TestPassword123"

Write-Host "ReCompose AI - API Testing" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -ErrorAction Stop
    Write-Host "   [OK] Health check passed: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "   [FAIL] Health check failed: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Root Endpoint
Write-Host "2. Testing Root Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get -ErrorAction Stop
    Write-Host "   [OK] Root endpoint works" -ForegroundColor Green
} catch {
    Write-Host "   [FAIL] Root endpoint failed: $_" -ForegroundColor Red
}

# Test 3: Signup
Write-Host "3. Testing User Signup..." -ForegroundColor Yellow
$signupSuccess = $false
try {
    $signupData = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/signup" -Method Post -Body $signupData -ContentType "application/json" -ErrorAction Stop
    Write-Host "   [OK] User signup successful: $($response.email)" -ForegroundColor Green
    $signupSuccess = $true
} catch {
    Write-Host "   [FAIL] User signup failed: $_" -ForegroundColor Red
}

# Test 4: Login
Write-Host "4. Testing User Login..." -ForegroundColor Yellow
$loginSuccess = $false
$token = $null
if ($signupSuccess) {
    try {
        $loginData = @{
            email = $testEmail
            password = $testPassword
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginData -ContentType "application/json" -ErrorAction Stop
        $token = $response.access_token
        Write-Host "   [OK] User login successful" -ForegroundColor Green
        $loginSuccess = $true
    } catch {
        Write-Host "   [FAIL] User login failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   [SKIP] Skipped (signup failed)" -ForegroundColor Yellow
}

# Test 5: Get Current User
Write-Host "5. Testing Get Current User..." -ForegroundColor Yellow
if ($loginSuccess -and $token) {
    try {
        $headers = @{
            "Authorization" = "Bearer $token"
        }
        $response = Invoke-RestMethod -Uri "$baseUrl/auth/me" -Method Get -Headers $headers -ErrorAction Stop
        Write-Host "   [OK] Get current user successful: $($response.email)" -ForegroundColor Green
    } catch {
        Write-Host "   [FAIL] Get current user failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   [SKIP] Skipped (login failed)" -ForegroundColor Yellow
}

# Test 6: API Documentation
Write-Host "6. Testing API Documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/docs" -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   [OK] API docs available at /docs" -ForegroundColor Green
    }
} catch {
    Write-Host "   [FAIL] API docs check failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "API Testing Complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Credentials Used:" -ForegroundColor Yellow
Write-Host "  Email: $testEmail" -ForegroundColor White
Write-Host "  Password: $testPassword" -ForegroundColor White
