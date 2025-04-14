@echo off
chcp 65001 > nul
title 🚀 Treinar modelo CodeT5p-220m - Fine Tuning

echo ========================================
echo  Iniciando treinamento do modelo CodeT5p-220m
echo ========================================
echo.

:: Ativa o ambiente virtual
call .venv\Scripts\activate

:: 🔁 Verifica se está autenticado no Hugging Face
echo Verificando autenticação no Hugging Face...
huggingface-cli whoami > nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 Você ainda não está autenticado no Hugging Face.
    echo Abrindo login...
    huggingface-cli login
)

:: 💡 Descomente abaixo para forçar limpeza de cache local
:: echo Limpando cache antigo do modelo...
:: rmdir /s /q .\codet5p-220m-finetuned

:: Executa o script Python de treinamento
python treinar_codet5.py

:: Verifica o código de retorno
if %errorlevel% neq 0 (
    echo.
    echo ❌ Erro durante o treinamento!
    echo ❗ Verifique os logs acima para identificar o problema.
) else (
    echo.
    echo ✅ Treinamento finalizado com sucesso!
)

echo.
pause
