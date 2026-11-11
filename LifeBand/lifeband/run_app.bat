@echo off
title LifeBand - Emergency Medical Identification System
echo ========================================================
echo  LifeBand: Smart Emergency Medical Identification System
echo  CSE Academic Prototype (IoT & Blockchain)
echo ========================================================
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Running test suite verification...
python -m unittest discover tests

if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some tests did not pass. Proceeding to launch app...
)

echo.
echo Starting Flask web server on http://127.0.0.1:5000 ...
echo Press Ctrl+C to terminate.
echo.
python app.py
pause
