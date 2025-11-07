@echo off
echo.
echo ========================================
echo   AI-Prism Document Analysis Tool
echo ========================================
echo.
echo Choose your version:
echo.
echo 1. Standalone App (Recommended)
echo 2. Enhanced UI Version
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Opening Standalone App...
    start "" "standalone_app.html"
) else if "%choice%"=="2" (
    echo.
    echo Opening Enhanced UI Version...
    start "" "templates\enhanced_index.html"
) else if "%choice%"=="3" (
    echo.
    echo Goodbye!
    exit
) else (
    echo.
    echo Invalid choice. Please try again.
    pause
    goto :eof
)

echo.
echo Application launched in your default browser.
echo.
pause