@echo off
cd /d %~dp0

echo ========================================
echo 🧹 Limpando cache do HuggingFace...
echo ========================================

REM Limpa cache do HuggingFace Transformers
rmdir /S /Q %USERPROFILE%\.cache\huggingface\transformers 2>nul

REM Limpa cache do HuggingFace Hub
rmdir /S /Q %USERPROFILE%\.cache\huggingface\hub 2>nul

echo ✅ Cache limpo!

echo.
echo ========================================
echo Iniciando microserviço com Uvicorn...
echo ========================================
echo.

REM Ativando ambiente virtual (.venv)
call .venv\Scripts\activate

REM Executando Uvicorn com reload (modo dev)
uvicorn main:app --reload

echo.
echo ========================================
echo Servidor finalizado. Pressione qualquer tecla para sair.
pause >nul
