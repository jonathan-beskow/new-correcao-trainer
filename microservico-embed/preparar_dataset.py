# preparar_dataset.py
import os
import json
import random
from pymongo import MongoClient
from difflib import SequenceMatcher

def extrair_diferencas(origem: str, destino: str) -> str:
    matcher = SequenceMatcher(None, origem.splitlines(), destino.splitlines())
    linhas_modificadas = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            linhas_modificadas.extend(destino.splitlines()[j1:j2])
    return '\n'.join(linhas_modificadas).strip()

def carregar_dados_do_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["corretor_db"]
    collection = db["casosCorrigidos"]
    collection_blocos = db["casosCorrigidosBlocos"]
    
    dados = []

    for doc in collection.find():
        entrada = doc.get("codigoOriginal", "").strip()
        saida = doc.get("codigoCorrigido", "").strip()
        tipo = doc.get("tipo", "").strip()
        if entrada and saida:
            dados.append({
                "input": f"Corrija este código vulnerável do tipo {tipo}:\n{entrada}",
                "output": saida
            })

    for bloco in collection_blocos.find():
        entrada = bloco.get("blocoAntes", "").strip()
        saida = bloco.get("blocoDepois", "").strip()
        tipo = bloco.get("tipo", "").strip()
        if entrada and saida:
            refinado = extrair_diferencas(entrada, saida)
            dados.append({
                "input": f"Corrija este bloco vulnerável do tipo {tipo}:\n{entrada}",
                "output": refinado if refinado else saida
            })
    return dados

def salvar_datasets(dados, output_dir="dataset_codet5"):
    os.makedirs(output_dir, exist_ok=True)
    random.shuffle(dados)

    n = len(dados)
    splits = {
        "train": dados[:int(0.8 * n)],
        "val": dados[int(0.8 * n):int(0.9 * n)],
        "test": dados[int(0.9 * n):]
    }

    for split_name, split_data in splits.items():
        with open(os.path.join(output_dir, f"{split_name}.json"), "w", encoding="utf-8") as f:
            json.dump(split_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Dataset salvo em '{output_dir}' com {n} exemplos.")
    for k, v in splits.items():
        print(f"🔹 {k.capitalize()}: {len(v)} exemplos")

if __name__ == "__main__":
    print("📦 Preparando dataset para treinamento do CodeT5...")
    dados = carregar_dados_do_mongo()
    salvar_datasets(dados)
