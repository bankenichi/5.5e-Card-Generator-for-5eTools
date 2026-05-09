@echo off
setlocal enabledelayedexpansion

echo ==============================================
echo Launching 5.5e Card Generator
echo ==============================================

set "PYTHON_DIR=%CD%\python-env"
set "GIT_EXE=%CD%\git-portable\bin\git.exe"

:: Check install.lock — authoritative signal that install completed successfully
IF NOT EXIST "install.lock" (
    echo Install has not been completed. Please run install.bat first!
    pause
    exit /b 1
)

:: Check for standalone Python
IF NOT EXIST "%PYTHON_DIR%\python.exe" (
    echo Python environment is missing or broken. Please run install.bat again to repair.
    pause
    exit /b 1
)

:: Resolve Git (system or portable) — capture absolute path before any cd
git --version >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    for /f "delims=" %%i in ('where git') do (
        set "GIT_CMD=%%i"
        goto :git_found
    )
)
if not defined GIT_CMD (
    if EXIST "%GIT_EXE%" (
        set "GIT_CMD=%GIT_EXE%"
    ) else (
        echo Warning: Git not found. Skipping update checks.
        echo Run install.bat to set up the portable Git environment.
    )
)

:git_found
:: Update Card Generator repository
echo Checking for Card Generator updates...
IF DEFINED GIT_CMD (
    IF EXIST ".git" (
        "%GIT_CMD%" pull
    ) ELSE (
        echo Generator repo missing .git — attempting repair...
        "%GIT_CMD%" clone https://github.com/bankenichi/5.5e-Card-Generator-for-5eTools temp_repair
        IF !ERRORLEVEL! NEQ 0 (
            echo Repair failed. Please run install.bat manually.
        ) ELSE (
            robocopy "temp_repair" "%CD%" /e /move /xd "%CD%\python-env" "%CD%\git-portable" "%CD%\generators" >nul
            rmdir /s /q "temp_repair" 2>nul
            echo Repair complete.
        )
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