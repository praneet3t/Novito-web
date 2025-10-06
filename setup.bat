@echo off
echo ========================================
echo   Meeting Agent - Setup Script
echo ========================================
echo.

echo [1/4] Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Backend installation failed!
    pause
    exit /b 1
)

echo.
echo [2/4] Installing Frontend Dependencies...
cd ..\frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Frontend installation failed!
    pause
    exit /b 1
)

echo.
echo [3/4] Initializing Database...
cd ..\backend
python -c "from database import init_db; init_db()"
if %errorlevel% neq 0 (
    echo ERROR: Database initialization failed!
    pause
    exit /b 1
)

echo.
echo [4/4] Seeding Example Data...
python -c "from seed_data import seed_example_data; seed_example_data()"
if %errorlevel% neq 0 (
    echo ERROR: Data seeding failed!
    pause
    exit /b 1
)

cd ..
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Demo Accounts:
echo   Admin:  Admin / admin123
echo   User 1: Priya / priya123
echo   User 2: Arjun / arjun456
echo   User 3: Raghav / raghav789
echo.
echo Run 'start.bat' to launch the application
echo ========================================
echo.
pause
