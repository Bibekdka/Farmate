@echo off
REM Daily Backup Script for FarmApp
REM This script runs the multi-location backup system

cd /d "%~dp0"

echo ==========================================
echo   FarmApp Daily Backup System
echo ==========================================
echo Starting backup at %date% %time%
echo.

python backup_db.py

echo.
echo ==========================================
echo   Backup Complete
echo ==========================================
pause
