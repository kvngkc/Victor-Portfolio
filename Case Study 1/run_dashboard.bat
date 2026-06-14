@echo off
setlocal

:: ── Configuration ────────────────────────────────────────────────────────────
set VENV_DIR=venv
set APP_FILE=app.py

:: ── Step 1: Create venv if it doesn't exist ──────────────────────────────────
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [1/3] Creating virtual environment...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        echo Make sure Python 3.9+ is installed and on your PATH.
        pause
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo [1/3] Virtual environment already exists, skipping creation.
)

:: ── Step 2: Activate venv ────────────────────────────────────────────────────
echo [2/3] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

:: ── Step 3: Install / update dependencies ────────────────────────────────────
echo [3/3] Installing dependencies from requirements.txt...
pip install -r requirements.txt --timeout 120 --quiet
if errorlevel 1 (
    echo ERROR: Dependency installation failed.
    pause
    exit /b 1
)

:: ── Launch ───────────────────────────────────────────────────────────────────
echo.
echo Starting Cyclistic Dashboard...
echo Open your browser at http://localhost:8501
echo Press Ctrl+C to stop the server.
echo.
streamlit run %APP_FILE%

endlocal
