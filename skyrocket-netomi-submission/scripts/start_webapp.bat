@echo off
echo ========================================
echo  SkyRocket Analytics - Web Application
echo ========================================
echo.

REM Check if virtual environment exists
REM Check if virtual environment exists
if not exist "..\venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first from the project root.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

REM Check if .env exists
if not exist "..\.env" (
    echo WARNING: .env file not found!
    echo Please create .env file with your GROQ_API_KEY
    echo.
)

REM Start backend server
echo.
echo Starting FastAPI backend server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
cd ..\webapp\backend
start "SkyRocket Backend" cmd /k "uvicorn app:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Open frontend in browser
echo.
echo Opening frontend in browser...
echo.
cd ..\frontend
start "" "index.html"

echo.
echo ========================================
echo  Application Started!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: Opening in default browser
echo.
echo Press any key to stop the backend server...
pause >nul

REM This will close the backend window when user presses a key
taskkill /FI "WindowTitle eq SkyRocket Backend*" /F >nul 2>&1

echo.
echo Application stopped.
pause
