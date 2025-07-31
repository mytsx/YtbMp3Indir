@echo off
echo Cleaning build artifacts...

REM Remove build directories
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Remove spec file artifacts
if exist *.spec del *.spec

echo.
echo Clean complete!
pause
