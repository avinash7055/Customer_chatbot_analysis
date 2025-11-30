@echo off
echo ================================================================================
echo  SkyRocket Netomi Submission - Automated Setup
echo ================================================================================
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.9+ first.
    pause
    exit /b 1
@echo off
echo ================================================================================
echo  SkyRocket Netomi Submission - Automated Setup
echo ================================================================================
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.9+ first.
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo [2/6] Creating virtual environment...
if not exist "..\venv" (
    python -m venv ..\venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate venv
echo [3/6] Activating virtual environment...
call ..\venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/6] Installing Python packages...
pip install -r ..\requirements.txt --quiet
pip install -e .. --quiet
echo Packages installed.
echo.

REM Download spaCy model
echo [5/6] Downloading spaCy model...
python -m spacy download en_core_web_sm --quiet
echo spaCy model installed.
echo.

REM Create .env if not exists
echo [6/6] Setting up configuration...
if not exist "..\.env" (
    if exist "..\.env.example" (
        copy ..\.env.example ..\.env
        echo .env file created. PLEASE EDIT IT TO ADD YOUR GROQ_API_KEY!
        notepad ..\.env
    ) else (
        echo Please create .env file with your GROQ_API_KEY in the project root.
    )
) else (
    echo .env file already exists.
)
echo.

echo ================================================================================
echo  Setup Complete!
echo ================================================================================
echo.
echo Next Steps:
echo 1. Make sure you added your GROQ_API_KEY to .env file
echo 2. Run: scripts\start_webapp.bat
echo.
echo ================================================================================
pause
