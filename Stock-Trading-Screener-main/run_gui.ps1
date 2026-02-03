# Stock Trading Screener - GUI Launcher (PowerShell)
# Run this script to launch the professional GUI dashboard

# Get the directory where this script is located
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Run the GUI
& .\.venv\Scripts\python.exe gui_trades.py

# Keep window open if there are errors
Read-Host "Press Enter to close"
