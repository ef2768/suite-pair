@echo off
REM Run this in the project folder after creating the repo at:
REM https://github.com/new  (name: suite-pair, leave README unchecked)

cd /d "c:\Users\ethan\OneDrive\Documents\room selection"

git init
git add .
git commit -m "Initial commit: suite survey and grouping algorithm"
git branch -M main
git remote add origin https://github.com/ef2768/suite-pair.git
git push -u origin main

pause
