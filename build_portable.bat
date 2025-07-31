@echo off
echo MP3Yap Portable Build Script
echo ============================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.11 from python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
pip install -r requirements-dev.txt

REM Build executable
echo.
echo Building executable...
python -m PyInstaller --clean mp3yap.spec

echo.
if exist dist\MP3Yap.exe (
    echo SUCCESS: Executable created at dist\MP3Yap.exe
) else (
    echo ERROR: Build failed!
)

echo.
pause
