@echo off
echo Parando DF Explorer...

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /F /PID %%p >nul 2>&1

echo Pronto. Pode fechar esta janela.
pause
