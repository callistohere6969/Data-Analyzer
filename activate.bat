@echo off
REM Quick manual activation script for Windows
REM Just activates projectvenv and opens interactive shell

echo Activating projectvenv...
echo Type 'streamlit run app.py' to start the app
echo Type 'python quick_test.py' to run tests
echo Type 'deactivate' to exit the environment
echo.

call projectvenv\Scripts\activate.bat
cmd /k
