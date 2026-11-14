@echo off
echo =============================================
echo  AI Research Assistant - Starting Server
echo =============================================
echo.

cd /d "%~dp0backend"
set OPENBLAS_NUM_THREADS=1
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=
set http_proxy=
set https_proxy=
set all_proxy=
call venv\Scripts\activate.bat

echo Backend running at: http://localhost:8000
echo API Docs at:        http://localhost:8000/docs
echo.
echo Open frontend\index.html in your browser to use the app.
echo Press Ctrl+C to stop.
echo.

netstat -ano -p tcp | findstr /R /C:":8000 .*LISTENING" >nul
if not errorlevel 1 (
    echo Backend is already listening on port 8000.
    echo Open http://localhost:8000/health to check it.
    exit /b 0
)

"%~dp0backend\venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
