import os
import pathlib
import subprocess

MODEL_DIR = "codet5-finetuned-vulnerabilities-trainer"
MODEL_FILES = ["pytorch_model.bin", "config.json", "tokenizer_config.json"]

def modelo_ja_treinado():
    path = pathlib.Path(MODEL_DIR)
    if not path.exists():
        return False
    for fname in MODEL_FILES:
        if not (path / fname).exists():
            return False
    return True

if modelo_ja_treinado():
    print("✅ Modelo já está treinado. Pulando treinamento.")
else:
    print("🚀 Modelo não encontrado ou incompleto. Iniciando treinamento...")
    subprocess.run(["python", "treinar_codet5.py"], check=True)

# ✅ Agora sim, iniciar a API
print("🌐 Subindo API FastAPI...")
subprocess.run(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])
