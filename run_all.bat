@echo off
REM Batch Script to Automate Minecraft Server Synchronization and Execution

SETLOCAL

REM Define paths
SET ROOT_DIR=%~dp0
SET SYNC_SCRIPTS_DIR=%ROOT_DIR%sync_scripts
SET SERVER_FILES_DIR=%ROOT_DIR%server_files
SET BACKUP_DIR=%ROOT_DIR%backup
SET PYTHON_CMD=python

REM Check for Python
%PYTHON_CMD% --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed or not added to PATH.
    pause
    EXIT /B 1
)

REM Check for Java
java -version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Java is not installed or not added to PATH.
    pause
    EXIT /B 1
)

REM Install required Python packages
echo Checking for required Python packages...
cd "%SYNC_SCRIPTS_DIR%"
IF EXIST requirements.txt (
    %PYTHON_CMD% -m pip install --upgrade pip >nul
    %PYTHON_CMD% -m pip install -r requirements.txt >nul
    echo Required Python packages installed.
) ELSE (
    echo requirements.txt not found. Skipping package installation.
)

REM Run setup_config.py if config.json does not exist
IF NOT EXIST "%SYNC_SCRIPTS_DIR%\config.json" (
    echo Running initial configuration...
    cd "%SYNC_SCRIPTS_DIR%"
    %PYTHON_CMD% setup_config.py
    cd "%ROOT_DIR%"
)

REM Run authenticate_gdrive.py
echo Authenticating with Google Drive...
cd "%SYNC_SCRIPTS_DIR%"
%PYTHON_CMD% authenticate_gdrive.py
cd "%ROOT_DIR%"

REM Run download_server_files.py
echo Downloading server files...
cd "%SYNC_SCRIPTS_DIR%"
%PYTHON_CMD% download_server_files.py
cd "%ROOT_DIR%"

REM Run the server
IF EXIST "%SERVER_FILES_DIR%\run.bat" (
    echo Starting Minecraft server...
    cd "%SERVER_FILES_DIR%"
    call run.bat
    cd "%ROOT_DIR%"
) ELSE (
    echo run.bat not found in server_files directory.
    pause
    EXIT /B 1
)

REM Run authenticate_gdrive.py
echo Authenticating with Google Drive...
cd "%SYNC_SCRIPTS_DIR%"
%PYTHON_CMD% authenticate_gdrive.py
cd "%ROOT_DIR%"

REM Run upload_server_files.py
echo Uploading server files...
cd "%SYNC_SCRIPTS_DIR%"
%PYTHON_CMD% upload_server_files.py
cd "%ROOT_DIR%"

echo Synchronization complete.
pause
ENDLOCAL
