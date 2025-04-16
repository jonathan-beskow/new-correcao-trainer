@echo off
chcp 65001 > nul
cd /d %~dp0

echo ========================================
echo 🧹 Limpando cache do HuggingFace...
echo ========================================

rmdir /S /Q %USERPROFILE%\.cache\huggingface\transformers 2>nul
rmdir /S /Q %USERPROFILE%\.cache\huggingface\hub 2>nul

echo ✅ Cache limpo!

echo.
echo ========================================
echo 🔍 Verificando ambiente virtual...
echo ========================================

IF NOT EXIST ".venv" (
    echo ⚠️ Ambiente virtual não encontrado.
    echo 🔧 Criando ambiente virtual...
    python -m venv .venv
)

echo ✅ Ambiente virtual pronto.

REM Ativa o ambiente virtual
call .venv\Scripts\activate

echo 📦 Verificando se pip está disponível...
where .venv\Scripts\pip.exe >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❗ pip não encontrado. Instalando pip manualmente...
    python -m ensurepip --upgrade
)

echo 📦 Instalando dependências...
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Dependências instaladas com sucesso!

echo.
echo ========================================
echo 🚀 Iniciando microserviço com Uvicorn...
echo ========================================
echo.

uvicorn main:app --reload

echo.
echo ========================================
echo 🛑 Servidor finalizado. Pressione qualquer tecla para sair.
pause >nul
