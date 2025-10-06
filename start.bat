@echo off
echo ========================================
echo   Meeting Agent - AI Task Management
echo ========================================
echo.

echo [1/3] Starting Backend Server...
cd backend
start cmd /k "python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend Server...
cd ..\frontend
start cmd /k "npm run dev"
timeout /t 3 /nobreak >nul

echo [3/3] Opening Browser...
timeout /t 5 /nobreak >nul
start http://localhost:5173

echo.
echo ========================================
echo   Servers Started Successfully!
echo ========================================
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo   Docs:     http://127.0.0.1:8000/docs
echo ========================================
echo.
echo Press any key to exit...
pause >nul
