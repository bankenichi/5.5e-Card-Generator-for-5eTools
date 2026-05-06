@echo off
setlocal enabledelayedexpansion

echo ==============================================
echo 5.5e Card Generator Installer
echo ==============================================

set "PYTHON_DIR=%CD%\python-env"
set "PYTHON_ZIP=python-3.11.9-embed-amd64.zip"
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py"

echo.
echo [1/3] Setting up standalone Python environment...
IF NOT EXIST "%PYTHON_DIR%\python.exe" (
    echo Downloading Portable Python 3.11...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%PYTHON_URL%', '%PYTHON_ZIP%')"
    
    echo Extracting Python...
    mkdir "%PYTHON_DIR%"
    powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
    
    echo Cleaning up zip file...
    del "%PYTHON_ZIP%"

    echo Enabling site-packages...
    :: Uncomment import site in python311._pth to allow pip and external modules
    powershell -Command "(Get-Content '%PYTHON_DIR%\python311._pth') -replace '#import site', 'import site' | Set-Content '%PYTHON_DIR%\python311._pth'"

    echo Downloading get-pip.py...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GET_PIP_URL%', 'get-pip.py')"

    echo Installing pip...
    "%PYTHON_DIR%\python.exe" get-pip.py
    
    echo Cleaning up get-pip.py...
    del get-pip.py
) ELSE (
    echo Standalone Python environment already exists.
)

echo.
echo [2/3] Installing dependencies...
IF EXIST "requirements.txt" (
    "%PYTHON_DIR%\python.exe" -m pip install --upgrade pip >nul 2>&1
    "%PYTHON_DIR%\python.exe" -m pip install -r requirements.txt
) ELSE (
    echo No requirements.txt found, checking standard libraries.
)

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
