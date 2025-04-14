from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import ObjectId

load_dotenv()

# MongoDB connection
#client = MongoClient("mongodb://host.docker.internal:27017/")
client = MongoClient("mongodb://localhost:27017/")
#mongodb://localhost:27017/
db = client["corretor_db"]
collection = db["casosCorrigidos"]
collection_blocos = db["casosCorrigidosBlocos"]

documentos = list(collection.find({"origemId": "67f44b7faaffd76837eebb00"}))
print(f"Encontrados: {len(documentos)} documentos.")
for doc in documentos:
    print(doc)


def buscar_todos_documentos():
    return list(collection.find({
        "codigoOriginal": {"$exists": True, "$ne": ""},
        "codigoCorrigido": {"$exists": True, "$ne": ""}
    }))

def buscar_documento_por_codigo(codigo_original: str):
    doc = collection.find_one({"codigoOriginal": codigo_original})
    if doc:
        return {
            "codigoCorrigido": doc.get("codigoCorrigido"),
            "origemId": str(doc.get("_id"))  # <-- Adicione isso
        }
    return None


def buscar_blocos_por_origem_id(origem_id: str):
    return list(collection_blocos.find({"origemId": origem_id}))

def buscar_bloco_por_id(bloco_id: str):
    try:
        return db["casosCorrigidosBlocos"].find_one({"_id": ObjectId(bloco_id)})
    except Exception as e:
        print(f"❌ Erro ao buscar bloco por ID '{bloco_id}': {e}")
        return None
    
def buscar_todos_blocos():
    return list(db["casosCorrigidosBlocos"].find({
        "blocoAntes": {"$exists": True, "$ne": ""},
        "blocoDepois": {"$exists": True, "$ne": ""}
    }))
