@echo off
chcp 65001 > nul
title 🔍 Verificar blocos cross-site scripting: dom no MongoDB

echo ==========================================
echo  Analisando blocos do tipo CSSDOM
echo ==========================================
echo.

:: Verifica se o ambiente virtual existe
if not exist ".venv\Scripts\activate" (
    echo ❌ Ambiente virtual não encontrado!
    echo 🔧 Por favor, crie com: python -m venv .venv
    pause
    exit /b
)

:: Ativa o ambiente virtual
call .venv\Scripts\activate

:: Garante que pymongo está instalado
pip show pymongo > nul 2>&1
if %errorlevel% neq 0 (
    echo ⬇️ Instalando pymongo...
    pip install pymongo
)

:: Executa o script de verificação
echo 🧠 Executando script: verificar_blocos_cssdom.py
python verificar_blocos_cssdom.py

echo.
echo 📄 Logs salvos em: logs\analise_codet5.log
echo.
pause
