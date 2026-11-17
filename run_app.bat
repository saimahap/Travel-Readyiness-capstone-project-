@echo off
title TravelReady AI - Flask Server
cd /d "%~dp0"
echo ======================================================================
echo   TravelReady AI - Pre-Travel Readiness Prediction System
echo ======================================================================
echo.
echo Starting Flask web server on http://localhost:5000 ...
echo.
start "" "http://localhost:5000"
"C:\Users\sai maha\AppData\Local\Programs\Python\Python314\python.exe" app.py
pause
