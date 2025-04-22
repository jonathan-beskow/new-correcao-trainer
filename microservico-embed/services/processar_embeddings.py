from pymongo import MongoClient
from services.embedding_service import gerar_embedding
from services.faiss_service import adicionar_embedding, adicionar_bloco_embedding

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["corretor_db"]
collection = db["casosCorrigidos"]
collection_blocos = db["casosCorrigidosBlocos"]

# Função para verificar e criar embeddings para documentos
def adicionar_embeddings_para_documentos():
    print("🔍 Buscando documentos sem embeddings...")

    documentos_sem_embedding = list(collection.find({
        "$or": [
            {"embedding": {"$exists": False}},
            {"embedding": {"$size": 0}},
            {"embedding": None}
        ],
        "codigoOriginal": {"$exists": True, "$ne": ""},
        "codigoCorrigido": {"$exists": True, "$ne": ""},
        "tipo": {"$exists": True, "$ne": ""}
    }))

    print(f"📄 Total de documentos a processar: {len(documentos_sem_embedding)}")

    for doc in documentos_sem_embedding:
        try:
            entrada = f"{doc.get('tipo', '')}: {doc.get('codigoOriginal', '')}"
            embedding = gerar_embedding(entrada)

            if embedding:
                # Salva no MongoDB
                collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"embedding": embedding}}
                )
                # Adiciona no índice FAISS
                adicionar_embedding(embedding, doc["codigoOriginal"])
                print(f"✅ Embedding salvo para ID {doc['_id']}")
            else:
                print(f"⚠️ Embedding nulo para ID {doc['_id']}")

        except Exception as e:
            print(f"❌ Erro ao processar documento {doc['_id']}: {e}")



def buscar_todos_documentos():
    return list(collection.find({
        "codigoOriginal": {"$exists": True, "$ne": ""},
        "codigoCorrigido": {"$exists": True, "$ne": ""}
    }))


# Função para verificar e criar embeddings para blocos
def adicionar_embeddings_para_blocos():
    print("🔁 Buscando blocos sem embeddings...")

    blocos_sem_embedding = list(collection_blocos.find({
        "$or": [
            {"embedding": {"$exists": False}},
            {"embedding": {"$size": 0}},
            {"embedding": None}
        ],
        "blocoAntes": {"$exists": True, "$ne": ""},
        "blocoDepois": {"$exists": True, "$ne": ""}
    }))

    print(f"📄 Blocos a processar: {len(blocos_sem_embedding)}")

    for bloco in blocos_sem_embedding:
        try:
            entrada = bloco["blocoAntes"]
            embedding = gerar_embedding(entrada)

            if embedding:
                collection_blocos.update_one(
                    {"_id": bloco["_id"]},
                    {"$set": {"embedding": embedding}}
                )
                adicionar_bloco_embedding(embedding, str(bloco["_id"]))
                print(f"✅ Embedding salvo para bloco {bloco['_id']}")
            else:
                print(f"⚠️ Embedding vazio para bloco {bloco['_id']}")
        except Exception as e:
            print(f"❌ Erro ao processar bloco {bloco['_id']}: {e}")


# Função principal que chama as verificações e a criação de embeddings
def processar_embeddings():
    print("📦 Iniciando a verificação e criação de embeddings...")

    # Adiciona embeddings para documentos
    adicionar_embeddings_para_documentos()

    # Adiciona embeddings para blocos
    adicionar_embeddings_para_blocos()

# Chama a função principal
if __name__ == "__main__":
    processar_embeddings()
