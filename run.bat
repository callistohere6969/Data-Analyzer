@echo off
REM Run the Multi-Agent Data Analyzer in projectvenv
REM Windows batch script

echo Activating projectvenv...
call projectvenv\Scripts\activate.bat

if errorlevel 1 (
    echo Error: Could not activate projectvenv
    exit /b 1
)

echo Installing/updating dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo.
echo ============================================
echo Running quick test...
echo ============================================
python quick_test.py

echo.
echo ============================================
echo Test complete! Starting Streamlit app...
echo ============================================
echo.
streamlit run app.py

pause
