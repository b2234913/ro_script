@echo off
REM Save the current directory
set "INITIAL_DIR=%CD%"

REM Set the TEMP directory path
set "TEMP_DIR=%TEMP%"

REM Change to the TEMP directory
cd /d "%TEMP_DIR%"

REM Loop through all directories starting with _MEI
for /d %%i in (_MEI*) do (
    REM Check if it's a directory
    if exist "%%i\" (
        echo Deleting folder: %%i
        REM Remove the directory and its contents
        rmdir /s /q "%%i"
    )
)

REM Change back to the initial directory
cd /d "%INITIAL_DIR%"

echo Done.
