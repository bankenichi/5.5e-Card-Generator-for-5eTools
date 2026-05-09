@echo off
setlocal enabledelayedexpansion

echo ==============================================
echo Launching 5.5e Card Generator
echo ==============================================

set "PYTHON_DIR=%CD%\python-env"
set "GIT_DIR=%CD%\git-portable"
set "GIT_EXE=%GIT_DIR%\bin\git.exe"

:: Check for standalone Python
IF NOT EXIST "%PYTHON_DIR%\python.exe" (
    echo Standalone Python environment not found. Please run install.bat first!
    pause
    exit /b 1
)

:: Resolve Git (system or portable)
git --version >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    set "GIT_CMD=git"
) else if EXIST "%GIT_EXE%" (
    set "GIT_CMD=%GIT_EXE%"
) else (
    echo Warning: Git not found. Skipping update checks.
    echo Run install.bat to set up the portable Git environment.
    set "GIT_CMD="
)

:: Update Card Generator repository
echo Checking for Card Generator updates...
IF DEFINED GIT_CMD (
    IF EXIST ".git" (
        "%GIT_CMD%" pull
    ) ELSE (
        echo Warning: Card Generator repository not found. Please run install.bat first!
    )
) ELSE (
    echo Skipping Card Generator update ^(no Git available^).
)

:: Update 5etools repository
echo Checking for 5etools dataset updates...
IF DEFINED GIT_CMD (
    IF EXIST "generators\5etools\.git" (
        cd generators\5etools
        "%GIT_CMD%" pull
        cd ..\..
    ) ELSE (
        echo Warning: 5etools repository not found in generators\5etools.
        echo Running install.bat is highly recommended.
    )
) ELSE (
    echo Skipping 5etools update ^(no Git available^).
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