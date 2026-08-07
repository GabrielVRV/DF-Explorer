@echo off
cd /d "%~dp0"

echo === Compilando o frontend ===
cd frontend
call npm install
call npm run build
cd ..

echo === Preparando ambiente Python ===
cd backend
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
)
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt

echo === Gerando o executavel ===
.venv\Scripts\python -m PyInstaller "DF Explorer.spec"

echo.
echo Pronto! Executavel em: backend\dist\DF Explorer.exe
pause
