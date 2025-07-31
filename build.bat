@echo off
echo Building MP3Yap for Windows...
echo.

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
pip install -r requirements-dev.txt

REM Run build script
echo.
echo Running build script...
python build_windows.py

echo.
echo Build complete!
pause
