@echo off
echo ==============================================
echo Launching 5.5e Card Generator
echo ==============================================

set "PYTHON_DIR=%CD%\python-env"

:: Check for standalone python
IF NOT EXIST "%PYTHON_DIR%\python.exe" (
    echo Standalone Python environment not found. Please run install.bat first!
    pause
    exit /b 1
)

:: Update 5etools repository
echo Checking for 5etools dataset updates...
IF EXIST "generators\5etools\.git" (
    cd generators\5etools
    git pull
    cd ..\..
) ELSE (
    echo Warning: 5etools repository not found in generators\5etools.
    echo Running install.bat is highly recommended.
)

:: Update python dependencies if necessary
echo Updating dependencies...
IF EXIST "requirements.txt" (
    "%PYTHON_DIR%\python.exe" -m pip install -r requirements.txt >nul 2>&1
)

echo.
echo Starting Card Generator Server...
"%PYTHON_DIR%\python.exe" card_controller.py

pause
