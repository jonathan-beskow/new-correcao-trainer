@echo off
chcp 65001 > nul
title 🚀 Treinar modelo CodeT5p-220m - Fine Tuning

echo ========================================
echo  Iniciando treinamento do modelo CodeT5p-220m
echo ========================================
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

:: Verifica se huggingface-cli está disponível
where huggingface-cli > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ huggingface-cli não encontrado. Instalando...
    pip install huggingface_hub
)

:: 🔁 Verifica autenticação no Hugging Face
echo Verificando autenticação no Hugging Face...
huggingface-cli whoami > nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 Você ainda não está autenticado no Hugging Face.
    echo Abrindo login...
    huggingface-cli login
)

:: 💡 Para forçar limpeza de modelo anterior, descomente abaixo
:: echo Limpando cache antigo do modelo...
:: rmdir /s /q .\codet5p-220m-finetuned

:: Executa o script Python
echo.
echo 🧠 Iniciando script Python de treinamento...
python treinar_codet5.py

:: Verifica retorno
if %errorlevel% neq 0 (
    echo.
    echo ❌ Erro durante o treinamento!
    echo ❗ Verifique os logs em "logs/treinamento.log" para detalhes.
) else (
    echo.
    echo ✅ Treinamento finalizado com sucesso!
)

echo.
pause
