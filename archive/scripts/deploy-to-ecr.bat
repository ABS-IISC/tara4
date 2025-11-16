@echo off
echo ========================================
echo TARA ECR Deployment Script
echo ========================================

set ECR_URI=758897368787.dkr.ecr.us-east-1.amazonaws.com/tara
set AWS_REGION=us-east-1
set IMAGE_TAG=latest

echo Step 1: Building Docker image...
docker build -t tara-app:%IMAGE_TAG% .

if %ERRORLEVEL% neq 0 (
    echo ERROR: Docker build failed
    pause
    exit /b 1
)

echo Step 2: Getting ECR login token...
for /f "tokens=*" %%i in ('aws ecr get-login-password --region %AWS_REGION%') do set ECR_TOKEN=%%i

if "%ECR_TOKEN%"=="" (
    echo ERROR: Failed to get ECR token. Check AWS credentials.
    pause
    exit /b 1
)

echo Step 3: Logging into ECR...
echo %ECR_TOKEN% | docker login --username AWS --password-stdin %ECR_URI%

if %ERRORLEVEL% neq 0 (
    echo ERROR: ECR login failed
    pause
    exit /b 1
)

echo Step 4: Tagging image for ECR...
docker tag tara-app:%IMAGE_TAG% %ECR_URI%:%IMAGE_TAG%

if %ERRORLEVEL% neq 0 (
    echo ERROR: Image tagging failed
    pause
    exit /b 1
)

echo Step 5: Pushing image to ECR...
docker push %ECR_URI%:%IMAGE_TAG%

if %ERRORLEVEL% neq 0 (
    echo ERROR: Push failed
    pause
    exit /b 1
)

echo ========================================
echo SUCCESS: TARA deployed to ECR!
echo ECR URI: %ECR_URI%:%IMAGE_TAG%
echo ========================================
echo.
echo Next steps for AWS App Runner:
echo 1. Go to AWS App Runner console
echo 2. Create service with ECR image: %ECR_URI%:%IMAGE_TAG%
echo 3. Set port to 8000
echo 4. Add environment variables:
echo    - AWS_DEFAULT_REGION=us-east-1
echo    - PORT=8000
echo ========================================
pause