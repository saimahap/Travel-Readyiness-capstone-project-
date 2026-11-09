@echo off
title TravelReady AI - Flask Server
cd /d "%~dp0"
echo ======================================================================
echo   TravelReady AI - Pre-Travel Readiness Prediction System
echo ======================================================================
echo.
echo Starting Flask application on http://localhost:5000 ...
echo Press Ctrl+C in this window to stop the server.
echo.
python app.py
pause

