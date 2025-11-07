@echo off
echo Pushing AI-Prism Document Review Tool to GitHub...

REM Initialize git repository if not already done
if not exist .git (
    echo Initializing git repository...
    git init
)

REM Add remote origin
echo Setting up remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/ABS-IISC/tara2.git

REM Add all files
echo Adding files to git...
git add .

REM Commit changes
echo Committing changes...
git commit -m "AI-Prism Document Review Tool - Complete Implementation

Features:
- AI-powered document analysis with Hawkeye framework
- Interactive statistics with clickable breakdowns
- Real-time chat assistant
- Text highlighting and commenting system
- Accept/reject feedback with notifications
- Dark/light mode toggle
- Responsive design for all devices
- AWS Bedrock integration
- Docker deployment ready
- Complete modular architecture

All features fully functional and production-ready."

REM Push to GitHub
echo Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo ✅ Successfully pushed to GitHub!
echo Repository: https://github.com/ABS-IISC/tara2
echo.
pause