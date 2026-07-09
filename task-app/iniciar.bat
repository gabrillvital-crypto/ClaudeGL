@echo off
SET NODE_DIR=C:\Users\gabriel.evangelista\AppData\Local\nodejs-portable\node-v20.16.0-win-x64
SET PATH=%NODE_DIR%;%NODE_DIR%\node_modules\.bin;%PATH%

cd /d "%~dp0"
echo Iniciando Gestao Efcaz (Task App)...
echo Acesse: http://localhost:5173
npm run dev
