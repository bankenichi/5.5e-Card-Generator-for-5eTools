@echo off
setlocal enabledelayedexpansion

echo ==============================================
echo TTRPG Card Generator Installer
echo ==============================================

:: Updated to target Python 3.14.1
set "PYTHON_DIR=%CD%\python-env"
set "PYTHON_ZIP=python-3.14.1-embed-amd64.zip"
set "PYTHON_URL=https://www.python.org/ftp/python/3.14.1/python-3.14.1-embed-amd64.zip"
set "GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py"

:: Portable Git settings
set "GIT_DIR=%CD%\git-portable"
set "GIT_ZIP=PortableGit.7z.exe"
set "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/PortableGit-2.45.2-64-bit.7z.exe"
set "GIT_EXE=%GIT_DIR%\bin\git.exe"

echo.
echo [0/4] Checking for Git...
git --version >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo Git is already installed on this system.
    set "GIT_CMD=git"
) ELSE (
    if EXIST "%GIT_EXE%" (
        echo Portable Git already set up.
        set "GIT_CMD=%GIT_EXE%"
    ) ELSE (
        echo Git not found. Downloading portable Git...
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GIT_URL%', '%GIT_ZIP%')"
        IF !ERRORLEVEL! NEQ 0 (
            echo Failed to download portable Git. Please check your internet connection.
            pause
            exit /b 1
        )

        echo Extracting portable Git ^(this may take a moment^)...
        mkdir "%GIT_DIR%"
        :: PortableGit self-extracts as a 7z SFX archive with a -o flag
        "%GIT_ZIP%" -o"%GIT_DIR%" -y >nul 2>&1
        IF !ERRORLEVEL! NEQ 0 (
            echo Failed to extract portable Git.
            pause
            exit /b 1
        )

        echo Cleaning up Git archive...
        del "%GIT_ZIP%"

        IF NOT EXIST "%GIT_EXE%" (
            echo Could not locate git.exe after extraction. Setup cannot continue.
            pause
            exit /b 1
        )

        echo Portable Git installed successfully.
        set "GIT_CMD=%GIT_EXE%"
    )
)

echo.
echo [1/4] Setting up standalone Python environment...
IF NOT EXIST "%PYTHON_DIR%\python.exe" (
    echo Downloading Portable Python 3.14...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%PYTHON_URL%', '%PYTHON_ZIP%')"
    
    echo Extracting Python...
    mkdir "%PYTHON_DIR%"
    powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
    
    echo Cleaning up zip file...
    del "%PYTHON_ZIP%"

    echo Enabling site-packages and local imports...
    :: Uncomment import site in python314._pth to allow pip and external modules
    powershell -Command "(Get-Content '%PYTHON_DIR%\python314._pth') -replace '#import site', 'import site' | Set-Content '%PYTHON_DIR%\python314._pth'"
    
    :: Allow embedded python to read modules from the parent directory
    echo .. >> "%PYTHON_DIR%\python314._pth"

    echo Downloading get-pip.py...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GET_PIP_URL%', 'get-pip.py')"

    echo Installing pip...
    "%PYTHON_DIR%\python.exe" get-pip.py
    
    echo Cleaning up get-pip.py...
    del get-pip.py
) ELSE (
    echo Standalone Python environment already exists.
    :: Ensure the path fix exists even if Python was already installed
    findstr /c:".." "%PYTHON_DIR%\python314._pth" >nul
    if errorlevel 1 (
        echo Adding local import path to existing Python environment...
        echo .. >> "%PYTHON_DIR%\python314._pth"
    )
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
echo [3/3] Setting up Data Environment...
IF NOT EXIST "generators" mkdir generators

:: Write sentinel file so launcher knows install completed successfully
echo %DATE% %TIME% > install.lock

echo.
echo ==============================================
echo Setup Complete!
echo You can now use "launch.bat" to start the generator.
echo ==============================================
pause
start launch.bat
