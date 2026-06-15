@echo off
cd /d "%~dp0"
set PATH=%LOCALAPPDATA%\nodejs-portable\node-v20.16.0-win-x64;%PATH%
npm run dev
pause
