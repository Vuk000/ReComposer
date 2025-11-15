# Comprehensive API Testing Script
# Tests all endpoints including contacts, campaigns, and rewrite

$baseUrl = "http://localhost:8000"
$testEmail = "test$(Get-Random)@example.com"
$testPassword = "TestPassword123"
$token = $null

Write-Host "ReCompose AI - Comprehensive API Testing" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Signup
Write-Host "1. User Signup..." -ForegroundColor Yellow
try {
    $signupData = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/signup" -Method Post -Body $signupData -ContentType "application/json" -ErrorAction Stop
    Write-Host "   [OK] Signup successful: $($response.email)" -ForegroundColor Green
    $signupSuccess = $true
} catch {
    Write-Host "   [FAIL] Signup failed: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Login
Write-Host "2. User Login..." -ForegroundColor Yellow
try {
    $loginData = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginData -ContentType "application/json" -ErrorAction Stop
    $token = $response.access_token
    Write-Host "   [OK] Login successful" -ForegroundColor Green
} catch {
    Write-Host "   [FAIL] Login failed: $_" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
}

# Test 3: Get Current User
Write-Host "3. Get Current User..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/me" -Method Get -Headers $headers -ErrorAction Stop
    Write-Host "   [OK] Current user: $($response.email)" -ForegroundColor Green
    $userId = $response.id
} catch {
    Write-Host "   [FAIL] Get current user failed: $_" -ForegroundColor Red
}

# Test 4: Create Contact
Write-Host "4. Create Contact..." -ForegroundColor Yellow
try {
    $contactData = @{
        name = "John Doe"
        email = "john.doe@example.com"
        company = "Example Corp"
        notes = "Test contact"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/contacts" -Method Post -Body $contactData -ContentType "application/json" -Headers $headers -ErrorAction Stop
    Write-Host "   [OK] Contact created: $($response.name)" -ForegroundColor Green
    $contactId = $response.id
} catch {
    Write-Host "   [FAIL] Create contact failed: $_" -ForegroundColor Red
    $contactId = $null
}

# Test 5: List Contacts
Write-Host "5. List Contacts..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/contacts" -Method Get -Headers $headers -ErrorAction Stop
    Write-Host "   [OK] Found $($response.Count) contacts" -ForegroundColor Green
} catch {
    Write-Host "   [FAIL] List contacts failed: $_" -ForegroundColor Red
}

# Test 6: Create Campaign
Write-Host "6. Create Campaign..." -ForegroundColor Yellow
try {
    $campaignData = @{
        name = "Test Campaign"
        description = "Test campaign description"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/campaigns" -Method Post -Body $campaignData -ContentType "application/json" -Headers $headers -ErrorAction Stop
    Write-Host "   [OK] Campaign created: $($response.name)" -ForegroundColor Green
    $campaignId = $response.id
} catch {
    Write-Host "   [FAIL] Create campaign failed: $_" -ForegroundColor Red
    $campaignId = $null
}

# Test 7: List Campaigns
Write-Host "7. List Campaigns..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/campaigns" -Method Get -Headers $headers -ErrorAction Stop
    Write-Host "   [OK] Found $($response.Count) campaigns" -ForegroundColor Green
} catch {
    Write-Host "   [FAIL] List campaigns failed: $_" -ForegroundColor Red
}

# Test 8: Get Usage Stats
Write-Host "8. Get Usage Stats..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/rewrite/usage" -Method Get -Headers $headers -ErrorAction Stop
    Write-Host "   [OK] Usage: $($response.used)/$($response.limit)" -ForegroundColor Green
} catch {
    Write-Host "   [FAIL] Get usage stats failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Account:" -ForegroundColor Yellow
Write-Host "  Email: $testEmail" -ForegroundColor White
Write-Host "  Password: $testPassword" -ForegroundColor White

