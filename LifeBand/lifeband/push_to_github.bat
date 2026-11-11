@echo off
echo ========================================================
echo  LifeBand - GitHub Remote Setup and Push Assistant
echo ========================================================
echo.
echo Make sure you have created an empty repository on GitHub:
echo https://github.com/new
echo Suggested name: lifeband
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/aditi-web-creator/lifeband.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL entered. Aborting.
    pause
    exit /b 1
)

echo.
echo [1/3] Configuring git remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo [2/3] Setting branch to main...
git branch -M main

echo [3/3] Pushing code to %REPO_URL%...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo  SUCCESS! LifeBand has been pushed to your GitHub repository!
    echo ========================================================
) else (
    echo.
    echo [NOTE] If prompted for authentication, log in via your browser
    echo or paste your GitHub Personal Access Token (PAT).
)
echo.
pause
