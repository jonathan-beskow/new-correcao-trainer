import os
import json
import hashlib
from pymongo import MongoClient

def calcular_hash_dados():
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
            dados.append({
                "input": f"Corrija este bloco vulnerável do tipo {tipo}:\n{entrada}",
                "output": saida
            })

    dados_ordenados = sorted(dados, key=lambda x: x["input"])
    dados_json = json.dumps(dados_ordenados, sort_keys=True)
    return hashlib.sha256(dados_json.encode("utf-8")).hexdigest()

def verifica_necessidade_treinamento():
    hash_atual = calcular_hash_dados()
    hash_file_path = "hash_treinamento.json"

    if os.path.exists(hash_file_path):
        with open(hash_file_path, "r", encoding="utf-8") as f:
            hash_anterior = json.load(f).get("hash")
        if hash_atual == hash_anterior:
            print("✅ Nenhuma mudança detectada. Não é necessário treinar novamente.")
            return False
        else:
            print("🔁 Mudança detectada. Treinamento necessário.")
    else:
        print("📁 Nenhum hash anterior encontrado. Treinamento necessário.")

    with open(hash_file_path, "w", encoding="utf-8") as f:
        json.dump({"hash": hash_atual}, f, ensure_ascii=False, indent=4)

    return True

if __name__ == "__main__":
    precisa_treinar = verifica_necessidade_treinamento()
    if precisa_treinar:
        print("\n🚀 Execute agora seu script de treino normalmente.")
