@echo off
echo ========================================
echo TARA ECR Push Script
echo ========================================

set ECR_URI=758897368787.dkr.ecr.us-east-1.amazonaws.com/tara
set AWS_REGION=us-east-1

echo Step 1: Getting ECR login token...
for /f "tokens=*" %%i in ('aws ecr get-login-password --region %AWS_REGION%') do set ECR_TOKEN=%%i

if "%ECR_TOKEN%"=="" (
    echo ERROR: Failed to get ECR token. Check AWS permissions.
    pause
    exit /b 1
)

echo Step 2: Logging into ECR...
echo %ECR_TOKEN% | docker login --username AWS --password-stdin %ECR_URI%

if %ERRORLEVEL% neq 0 (
    echo ERROR: ECR login failed
    pause
    exit /b 1
)

echo Step 3: Pushing image to ECR...
docker push %ECR_URI%:latest

if %ERRORLEVEL% neq 0 (
    echo ERROR: Push failed
    pause
    exit /b 1
)

echo ========================================
echo SUCCESS: Image pushed to ECR!
echo ECR URI: %ECR_URI%:latest
echo ========================================
echo.
echo Next steps:
echo 1. Go to AWS App Runner console
echo 2. Create service with ECR image: %ECR_URI%:latest
echo 3. Set port to 8000
echo 4. Add environment variables for Bedrock access
echo ========================================
pause