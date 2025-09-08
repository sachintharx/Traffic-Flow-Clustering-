# Traffic Dashboard Cleanup Script
Write-Host "🧹 Cleaning up Traffic Dashboard..." -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Stop any running Streamlit processes
Write-Host "🛑 Stopping Streamlit processes..." -ForegroundColor Yellow
Get-Process -Name "streamlit*" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*streamlit*" } | Stop-Process -Force

# Stop any running FastAPI processes
Write-Host "🛑 Stopping FastAPI processes..." -ForegroundColor Yellow
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*chatbot_server*" } | Stop-Process -Force

# Clean Streamlit cache
Write-Host "🗂️  Clearing Streamlit cache..." -ForegroundColor Yellow
if (Test-Path "$env:USERPROFILE\.streamlit") {
    Remove-Item -Path "$env:USERPROFILE\.streamlit\cache" -Recurse -Force -ErrorAction SilentlyContinue
}

# Clean Python cache
Write-Host "🗂️  Clearing Python cache..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Recurse -Name "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path "." -Recurse -Name "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force

# Clean temporary files
Write-Host "🗂️  Clearing temporary files..." -ForegroundColor Yellow
Remove-Item -Path "*.tmp" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "*.log" -Force -ErrorAction SilentlyContinue

# Clean pip cache
Write-Host "🗂️  Clearing pip cache..." -ForegroundColor Yellow
pip cache purge 2>$null

Write-Host "✅ Cleanup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run the dashboard with:" -ForegroundColor White
Write-Host "  • Double-click run.bat (Windows)" -ForegroundColor Gray
Write-Host "  • Or: streamlit run app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
