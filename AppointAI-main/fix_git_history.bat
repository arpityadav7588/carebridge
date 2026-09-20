@echo off
echo ========================================
echo GIT HISTORY CLEANUP SCRIPT
echo ========================================
echo.
echo WARNING: This will remove all git history and start fresh!
echo Make sure you have:
echo   1. Rotated your API key in Google Cloud Console
echo   2. Updated .env with new API key
echo   3. Backed up any important data
echo.
pause

echo.
echo Step 1: Backing up current branch name...
git branch --show-current > current_branch.txt
set /p BRANCH=<current_branch.txt
del current_branch.txt
echo Current branch: %BRANCH%

echo.
echo Step 2: Removing .git directory...
rmdir /s /q .git

echo.
echo Step 3: Reinitializing git repository...
git init

echo.
echo Step 4: Adding all files...
git add .

echo.
echo Step 5: Creating clean commit...
git commit -m "Complete Member 1 (AI + Automation) implementation - Gemini Live Agent Challenge 2026"

echo.
echo Step 6: Ready to push!
echo.
echo To push to GitHub, run:
echo   git remote add origin YOUR-REPO-URL
echo   git branch -M main
echo   git push -f origin main
echo.
echo ========================================
echo CLEANUP COMPLETE!
echo ========================================
pause
