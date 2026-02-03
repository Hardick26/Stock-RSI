@echo off
REM Stock Trading Screener - GUI Launcher
REM Run this batch file to launch the professional GUI dashboard

cd /d "%~dp0"

REM Activate virtual environment and run GUI
call .venv\Scripts\activate.bat
.venv\Scripts\python.exe gui_trades.py

REM If GUI closes, keep window open to see any errors
pause
