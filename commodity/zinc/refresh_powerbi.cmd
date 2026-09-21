@echo off
cd /d "%~dp0"
if exist "..\..\.venv\Scripts\python.exe" (
  "..\..\.venv\Scripts\python.exe" refresh_powerbi.py
) else (
  py refresh_powerbi.py
)
if errorlevel 1 pause
