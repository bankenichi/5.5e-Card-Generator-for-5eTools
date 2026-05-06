@echo off
echo ==============================================
echo Launching 5.5e Card Generator
echo ==============================================

:: Check for virtual environment
IF NOT EXIST ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run install.bat first!
    pause
    exit /b 1
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

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
    pip install -r requirements.txt >nul 2>&1
)

echo.
echo Starting Card Generator Server...
python card_controller.py

pause
