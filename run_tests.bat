@echo off
echo ===============================================
echo DataOps Foundation Jenkins - Run Tests
echo ===============================================

echo.
echo [Step 1] Installing missing dependencies...
pip install pymssql
if %errorlevel% neq 0 (
    echo ERROR: Failed to install pymssql
    pause
    exit /b 1
)

echo.
echo [Step 2] Running quick tests...
python tests\quick_test.py

echo.
echo [Step 3] Running full ETL pipeline test...
python etl_main.py

echo.
echo [Step 4] Running unit tests...
python tests\test_etl_pipeline.py

echo.
echo ===============================================
echo All tests completed!
echo ===============================================
pause
