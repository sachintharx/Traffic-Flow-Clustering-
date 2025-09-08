#!/usr/bin/env python3
"""
Environment and Requirements Checker for Traffic Dashboard
"""
import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_pip():
    """Check if pip is available"""
    print("📦 Checking pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("   ✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("   ❌ pip is not available")
        return False

def check_requirements():
    """Check if required packages are installed"""
    print("📋 Checking required packages...")
    
    requirements = [
        "streamlit", "pandas", "plotly", "numpy", 
        "requests", "fastapi", "uvicorn", "pydantic"
    ]
    
    missing = []
    for package in requirements:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Missing")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_data_files():
    """Check if required data files exist"""
    print("📊 Checking data files...")
    
    data_file = Path("data/road_segment_traffic_clusters.csv")
    if data_file.exists():
        print(f"   ✅ {data_file}")
        return True
    else:
        print(f"   ❌ {data_file} - Missing")
        return False

def check_ports():
    """Check if required ports are available"""
    print("🔌 Checking ports...")
    
    import socket
    
    ports = [8501, 8000]  # Streamlit and FastAPI default ports
    available_ports = []
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result != 0:
            print(f"   ✅ Port {port} - Available")
            available_ports.append(port)
        else:
            print(f"   ⚠️  Port {port} - In use")
    
    return len(available_ports) > 0

def install_missing_packages(missing_packages):
    """Install missing packages"""
    if not missing_packages:
        return True
    
    print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install"
        ] + missing_packages, check=True)
        print("   ✅ Installation completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Installation failed: {e}")
        return False

def main():
    """Main check function"""
    print("🚦 Traffic Dashboard Environment Checker")
    print("=" * 45)
    print()
    
    checks_passed = 0
    total_checks = 5
    
    # Check Python version
    if check_python_version():
        checks_passed += 1
    print()
    
    # Check pip
    if check_pip():
        checks_passed += 1
    print()
    
    # Check requirements
    packages_ok, missing = check_requirements()
    if packages_ok:
        checks_passed += 1
    elif missing:
        print(f"\n🔧 Attempting to install missing packages...")
        if install_missing_packages(missing):
            checks_passed += 1
            print("   ✅ All packages now installed")
        else:
            print("   ❌ Failed to install some packages")
    print()
    
    # Check data files
    if check_data_files():
        checks_passed += 1
    print()
    
    # Check ports
    if check_ports():
        checks_passed += 1
    print()
    
    # Summary
    print("=" * 45)
    print(f"📊 Summary: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 Environment is ready!")
        print("\nTo start the dashboard:")
        print("  • Run: streamlit run app.py")
        print("  • Or double-click run.bat (Windows)")
        print("  • Then open: http://localhost:8501")
    else:
        print("⚠️  Some issues need to be resolved")
        print("\nNext steps:")
        if checks_passed < 2:
            print("  1. Install Python 3.8+ and pip")
        if not packages_ok and missing:
            print("  2. Install missing packages: pip install " + " ".join(missing))
        print("  3. Ensure data files are in the correct location")
        print("  4. Close any applications using ports 8501 or 8000")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
