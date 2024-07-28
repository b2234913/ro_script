@echo off
:: Change to the directory where the script is located
cd /d %~dp0

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
echo 2. enter_fire_lake
echo 3. make_fire_lake_mission

:: Get task input
set /p task_choice="Enter the number of the task: "

:: Set task variable based on input
if "%task_choice%"=="1" (
    set task=make_money
) else if "%task_choice%"=="2" (
    set task=enter_fire_lake
) else if "%task_choice%"=="3" (
    set task=make_fire_lake_mission
) else (
    echo Invalid choice.
    pause
    exit /B
)

:: Ask for delay time
set /p delay="Enter the delay time in milliseconds (default is 350ms): "

:: Use default delay if input is empty
if "%delay%"=="" (
    set delay=350
)

:: Run the Python script with the selected parameters
echo Running task %task% with a delay of %delay% milliseconds...
main.exe --task %task% --delay %delay%

:: Pause to keep the window open
pause
