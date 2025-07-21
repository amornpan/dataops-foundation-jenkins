@echo off
echo ===============================================
echo DataOps Foundation Jenkins Project Setup
echo ===============================================

echo.
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)
echo ✅ Python found

echo.
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, removing...
    rmdir /s /q venv
)
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created

echo.
echo [3/5] Activating virtual environment and installing packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo ✅ Packages installed

echo.
echo [4/5] Checking data file...
if not exist "data\LoanStats_web_small.csv" (
    echo ⚠️  WARNING: Data file not found!
    echo Please copy LoanStats_web_small.csv to the data\ folder
    echo.
    echo Expected location: data\LoanStats_web_small.csv
    echo.
    echo You can copy from the original project:
    echo copy "C:\Users\Asus\dataops-foundation\LoanStats_web_small.csv" "data\"
) else (
    echo ✅ Data file found
)

echo.
echo [5/5] Testing installation...
python -c "import pandas, numpy, sqlalchemy; print('✅ Core packages working')"
if %errorlevel% neq 0 (
    echo ERROR: Package import test failed
    pause
    exit /b 1
)

echo.
echo ===============================================
echo 🎉 Setup completed successfully!
echo ===============================================
echo.
echo Next steps:
echo 1. Copy data file to data\ folder (if not done)
echo 2. Test ETL pipeline: python ETL-dev.py
echo 3. Run unit tests: python tests\test_etl_pipeline.py
echo 4. Setup Jenkins pipeline using Jenkinsfile
echo.
echo For more information, see README.md
echo.
pause
