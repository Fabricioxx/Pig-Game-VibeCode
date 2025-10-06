@echo off
REM Script para executar o Jogo do Porquinho
REM Criado automaticamente

echo.
echo ====================================
echo    JOGO DO PORQUINHO
echo ====================================
echo.

REM Mostrar recorde se existir
if exist highscore.json (
    echo Carregando seu recorde salvo...
) else (
    echo Primeira vez? Boa sorte!
)

echo.
echo Iniciando o jogo...
echo.

C:\Users\fabri\AppData\Local\Programs\Python\Python312\python.exe game.py

echo.
echo ====================================
echo Jogo encerrado!
echo Seu recorde foi salvo automaticamente.
echo ====================================
echo.
pause
