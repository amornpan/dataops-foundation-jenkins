@echo off
echo ===============================================
echo Installing Missing Dependencies
echo ===============================================

echo.
echo Installing pymssql...
pip install pymssql

echo.
echo Testing pymssql installation...
python -c "import pymssql; print('✅ pymssql installed successfully')"

echo.
echo ===============================================
echo Installation completed!
echo ===============================================
pause
