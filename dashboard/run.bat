@echo off
echo 🚦 Road Segment Traffic Analysis Dashboard
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

:: Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo ✅ pip found
echo.

:: Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.

:: Check if data file exists
if not exist "data\road_segment_traffic_clusters.csv" (
    echo ❌ Data file not found: data\road_segment_traffic_clusters.csv
    echo Please ensure the data file exists
    pause
    exit /b 1
)

echo ✅ Data file found
echo.

:: Start the dashboard
echo 🚀 Starting Traffic Analysis Dashboard...
echo.
echo The dashboard will open in your browser at:
echo http://localhost:8501
echo.
echo To stop the server, press Ctrl+C
echo.

streamlit run app.py
pause
