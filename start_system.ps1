# 24-Hour Power Outage Forecasting System Startup Script
# This script starts both the backend FastAPI server and frontend React app

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "24-Hour Power Outage Forecasting System" -ForegroundColor Green
Write-Host "Balfour Beatty Demo System" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$projectPath = "C:\Users\Admin\IET_BalfourBeatty\24-Hour Power Outage Forecasting System"
$frontendPath = "$projectPath\frontend"

# Check if project directory exists
if (-not (Test-Path $projectPath)) {
    Write-Host "ERROR: Project directory not found!" -ForegroundColor Red
    Write-Host "Expected: $projectPath" -ForegroundColor Red
    exit 1
}

Write-Host "[1/3] Checking system requirements..." -ForegroundColor Blue

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] Starting Backend Server (FastAPI)..." -ForegroundColor Blue

# Start backend in new PowerShell window
$backendScript = @"
Set-Location '$projectPath'
Write-Host 'Starting FastAPI Backend Server...' -ForegroundColor Green
Write-Host 'Real-time weather data integration enabled' -ForegroundColor Yellow
Write-Host 'Server will run on: http://127.0.0.1:8002' -ForegroundColor Cyan
Write-Host ''
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8002 --reload
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Write-Host "✓ Backend server starting on port 8002..." -ForegroundColor Green
Write-Host "  Waiting for initialization..." -ForegroundColor Yellow

# Wait for backend to start
Start-Sleep -Seconds 8

Write-Host ""
Write-Host "[3/3] Starting Frontend Dashboard (React)..." -ForegroundColor Blue

# Start frontend in new PowerShell window  
$frontendScript = @"
Set-Location '$frontendPath'
Write-Host 'Starting React Frontend Dashboard...' -ForegroundColor Green
Write-Host 'Industry-ready power outage forecasting interface' -ForegroundColor Yellow
Write-Host 'Dashboard will run on: http://localhost:3000' -ForegroundColor Cyan
Write-Host ''
npm start
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host "✓ Frontend dashboard starting on port 3000..." -ForegroundColor Green

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "SYSTEM STARTUP COMPLETE!" -ForegroundColor Green -BackgroundColor Black
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Yellow
Write-Host "   Frontend Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API:        http://localhost:8002" -ForegroundColor White
Write-Host "   API Documentation:  http://localhost:8002/docs" -ForegroundColor White
Write-Host ""
Write-Host "📊 Features Available:" -ForegroundColor Yellow
Write-Host "   ✓ Real-time weather data integration" -ForegroundColor Green
Write-Host "   ✓ 24-hour power outage forecasting" -ForegroundColor Green
Write-Host "   ✓ Interactive charts and visualizations" -ForegroundColor Green
Write-Host "   ✓ Professional dashboard interface" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Ready for Balfour Beatty presentation!" -ForegroundColor Green -BackgroundColor DarkBlue
Write-Host ""

# Test connectivity
Write-Host "Testing system connectivity..." -ForegroundColor Blue
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8002/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Backend health check: PASSED" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Backend health check: PENDING (still starting up)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit this startup script..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")