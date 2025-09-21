@echo off
echo Starting 24-Hour Power Outage Forecasting System...
echo.

echo [1/2] Starting Backend Server...
start "Backend Server" cmd /k "cd /d "C:\Users\Admin\IET_BalfourBeatty\24-Hour Power Outage Forecasting System" && python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8002"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo [2/2] Starting Frontend Dashboard...
start "Frontend Dashboard" cmd /k "cd /d "C:\Users\Admin\IET_BalfourBeatty\24-Hour Power Outage Forecasting System\frontend" && npm start"

echo.
echo System started successfully!
echo.
echo Access URLs:
echo - Frontend Dashboard: http://localhost:3000
echo - Backend API: http://localhost:8002
echo - API Documentation: http://localhost:8002/docs
echo.
echo Press any key to exit...
pause >nul