#!/bin/bash

echo "🚦 Road Segment Traffic Analysis Dashboard"
echo "=========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not available"
    echo "Please ensure pip is installed with Python"
    exit 1
fi

echo "✅ pip found: $(pip3 --version)"
echo

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo

# Check if data file exists
if [ ! -f "data/road_segment_traffic_clusters.csv" ]; then
    echo "❌ Data file not found: data/road_segment_traffic_clusters.csv"
    echo "Please ensure the data file exists"
    exit 1
fi

echo "✅ Data file found"
echo

# Start the dashboard
echo "🚀 Starting Traffic Analysis Dashboard..."
echo
echo "The dashboard will open in your browser at:"
echo "http://localhost:8501"
echo
echo "To stop the server, press Ctrl+C"
echo

streamlit run app.py
