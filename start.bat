@echo off
cd /d "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
    echo Primeira execucao: criando ambiente e instalando dependencias...
    python -m venv .venv
    .venv\Scripts\python -m pip install --upgrade pip
    .venv\Scripts\python -m pip install -r requirements.txt
)

.venv\Scripts\python desktop.py
