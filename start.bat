@echo off
echo =============================================
echo  AI Research Assistant - Starting Server
echo =============================================
echo.

cd /d "%~dp0backend"
call venv\Scripts\activate.bat

echo Backend running at: http://localhost:8000
echo API Docs at:        http://localhost:8000/docs
echo.
echo Open frontend\index.html in your browser to use the app.
echo Press Ctrl+C to stop.
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000

