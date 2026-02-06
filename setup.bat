@echo off
REM Setup script for Windows
REM Use with existing projectvenv

echo.
echo ============================================
echo Multi-Agent Data Analyzer - Setup
echo ============================================
echo.

echo Step 1: Activating projectvenv...
call projectvenv\Scripts\activate.bat

if errorlevel 1 (
    echo Error: Could not activate projectvenv
    echo Make sure projectvenv folder exists in the current directory
    exit /b 1
)

echo Step 2: Installing dependencies...
pip install -r requirements.txt --upgrade

if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo.
echo Step 3: Verifying setup...

python -c "import streamlit; import pandas; import langchain; import langgraph; print('✓ All dependencies verified!')" 

if errorlevel 1 (
    echo ✗ Some dependencies are missing
    exit /b 1
)

echo.
echo Step 4: Creating .env file...
if not exist .env (
    copy .env.example .env
    echo ✓ .env file created from template
    echo.
    echo IMPORTANT: Edit .env and add your OpenRouter API key
) else (
    echo ✓ .env file already exists
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env and add your OpenRouter API key
echo 2. Run: run.bat
echo    OR
echo 3. Manually: projectvenv\Scripts\activate.bat
echo           streamlit run app.py
echo.
pause
