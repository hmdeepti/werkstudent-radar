@echo off
cd /d "%~dp0"
if not exist "reports" mkdir "reports"
py -m radar.main >> "reports\run.log" 2>&1
