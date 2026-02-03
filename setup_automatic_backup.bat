@echo off
REM Setup automatic daily backup using Windows Task Scheduler
REM This script creates a scheduled task to run backups at 11 PM every day

echo ==========================================
echo   FarmApp Automatic Backup Setup
echo ==========================================
echo.

REM Get the current directory
set SCRIPT_DIR=%~dp0

echo Setting up daily backup task...
echo.

REM Create the scheduled task
schtasks /Create /SC DAILY /TN "FarmApp_DailyBackup" /TR "%SCRIPT_DIR%run_daily_backup.bat" /ST 23:00 /F /RU "%USERNAME%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo   SUCCESS!
    echo ==========================================
    echo.
    echo Automatic daily backup is now configured!
    echo.
    echo Details:
    echo - Task Name: FarmApp_DailyBackup
    echo - Schedule: Every day at 11:00 PM
    echo - Action: Run full backup to 3 locations
    echo.
    echo You can verify this in Task Scheduler or run:
    echo   schtasks /Query /TN "FarmApp_DailyBackup"
    echo.
    echo To remove the scheduled task, run:
    echo   schtasks /Delete /TN "FarmApp_DailyBackup" /F
    echo.
) else (
    echo.
    echo ==========================================
    echo   ERROR
    echo ==========================================
    echo.
    echo Failed to create scheduled task.
    echo Please run this script as Administrator.
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
)

pause
