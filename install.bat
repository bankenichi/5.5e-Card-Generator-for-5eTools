@echo off
setlocal enabledelayedexpansion

echo ==============================================
echo 5.5e Card Generator Installer
echo ==============================================

:: Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Create Virtual Environment
echo.
echo [1/3] Creating virtual environment (.venv)...
IF NOT EXIST ".venv" (
    python -m venv .venv
    IF !ERRORLEVEL! NEQ 0 (
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
) ELSE (
    echo Virtual environment already exists.
)

:: Install Dependencies
echo.
echo [2/3] Installing dependencies...
call .venv\Scripts\activate.bat
:: Upgrade pip first
python -m pip install --upgrade pip >nul 2>&1
IF EXIST "requirements.txt" (
    pip install -r requirements.txt
) ELSE (
    echo No requirements.txt found, checking standard libraries.
)

:: Clone 5etools Repository
echo.
echo [3/3] Setting up 5etools dataset...
IF NOT EXIST "generators" mkdir generators
IF NOT EXIST "generators\5etools" (
    echo Cloning 5etools repository...
    git clone https://github.com/5etools-mirror-1/5etools-src.git generators\5etools
    IF !ERRORLEVEL! NEQ 0 (
        echo Failed to clone 5etools! Please ensure git is installed and accessible.
        pause
        exit /b 1
    )
) ELSE (
    echo 5etools repository already exists.
)

echo.
echo ==============================================
echo Setup Complete! 
echo You can now use "launch.bat" to start the generator.
echo ==============================================
pause
