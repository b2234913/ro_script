@echo off
mode con: cols=50 lines=40


:: Change to the directory where the script is located
cd /d %~dp0


@echo off
set "source_dir=%~dp0lib"
set "source_file=libomp140.x86_64.dll"
set "destination_dir=C:\Windows\System32"
set "destination_file=%destination_dir%\%source_file%"

:: Check if the source file exists in the destination directory
if exist "%destination_file%" (
    echo %source_file% already exists in %destination_dir%.
) else (
    echo %source_file% not found in %destination_dir%. Copying...
    copy "%source_dir%\%source_file%" "%destination_dir%"
    if errorlevel 1 (
        echo Failed to copy %source_file%.
    ) else (
        echo %source_file% copied successfully.
    )
)


:: Clean the directory before running the script
cmd /c clean.bat

:: Check for administrator privileges
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo This script requires administrator privileges.
    pause
    exit /B
)

:: Display task options
echo Select the task to execute:
echo 1. make_money
echo 2. make_fire_lake
echo 3. make_soul
echo 4. enter_fire_lake
echo 5. enter_king_gym
echo 6. enter_bad_gym
echo 7. enter_bad_dark

:: Get task input
set /p task_choice="Enter the number of the task: "

:: Set task variable based on input
if "%task_choice%"=="1" (
    set task=make_money
) else if "%task_choice%"=="2" (
    set task=make_fire_lake
) else if "%task_choice%"=="3" (
    set task=make_life_palce
) else if "%task_choice%"=="4" (
    set task=make_soul
) else if "%task_choice%"=="5" (
    set task=enter_fire_lake
) else if "%task_choice%"=="6" (
    set task=enter_king_gym
) else if "%task_choice%"=="7" (
    set task=enter_bad_gym
) else if "%task_choice%"=="8" (
    set task=enter_bad_dark
) else (
    echo Invalid choice.
    pause
    exit /B
)

:: Ask for delay time
@REM set /p delay="Enter the delay time in milliseconds (default is 350ms): "

:: Use default delay if input is empty
if "%delay%"=="" (
    set delay=350
)

:: Run the Python script with the selected parameters
echo Running task %task% with a delay of %delay% milliseconds...
main.exe --task %task% --delay %delay% -l DEBUG

:: Pause to keep the window open
pause
