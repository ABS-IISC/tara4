@echo off
echo ========================================
echo TARA GitHub Deployment Script
echo ========================================

echo Step 1: Initialize Git repository...
git init

echo Step 2: Add all files...
git add .

echo Step 3: Create initial commit...
git commit -m "Initial commit - TARA Document Analysis Tool"

echo Step 4: Add GitHub remote...
echo Please create a new repository on GitHub and paste the URL below:
set /p GITHUB_URL="Enter GitHub repository URL: "

git remote add origin %GITHUB_URL%

echo Step 5: Push to GitHub...
git branch -M main
git push -u origin main

echo ========================================
echo SUCCESS: Code pushed to GitHub!
echo Repository: %GITHUB_URL%
echo ========================================
echo.
echo Next steps for AWS App Runner:
echo 1. Go to AWS App Runner console
echo 2. Create service from source code
echo 3. Connect to GitHub repository: %GITHUB_URL%
echo 4. Use apprunner.yaml configuration
echo 5. Set IAM role with Bedrock permissions
echo ========================================
pause