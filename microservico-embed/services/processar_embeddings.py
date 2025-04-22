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
    documentos = buscar_todos_documentos()
    if not documentos:
        print("⚠️ Nenhum dado encontrado para adicionar embeddings.")
        return

    for doc in documentos:
        # Verifica se 'codigoOriginal' existe e não está vazio
        if "codigoOriginal" in doc and doc["codigoOriginal"]:
            entrada = f"{doc.get('tipo', '')}: {doc['codigoOriginal']}"
            embedding = gerar_embedding(entrada)
            
            if embedding is not None:
                adicionar_embedding(embedding, doc["codigoOriginal"])
                print(f"✅ Embedding adicionado para o código: {doc['codigoOriginal']}")
            else:
                print(f"⚠️ Falha ao gerar embedding para o código: {doc['codigoOriginal']}")
        else:
            print(f"⚠️ Documento {doc['_id']} não possui o campo 'codigoOriginal'. Ignorando.")


def buscar_todos_documentos():
    return list(collection.find({
        "codigoOriginal": {"$exists": True, "$ne": ""},
        "codigoCorrigido": {"$exists": True, "$ne": ""}
    }))


# Função para verificar e criar embeddings para blocos
def adicionar_embeddings_para_blocos():
    print("🔁 Verificando e criando embeddings para os blocos...")

    blocos = collection_blocos.find({"embedding": {"$exists": False}})  # Verifica blocos sem embedding
    total_adicionados = 0

    for bloco in blocos:
        entrada = bloco["blocoAntes"]
        embedding = gerar_embedding(entrada)
        
        # Adiciona o embedding no FAISS
        adicionar_bloco_embedding(embedding, str(bloco["_id"]))

        # Atualiza o banco de dados com o novo campo de embedding
        collection_blocos.update_one(
            {"_id": bloco["_id"]},
            {"$set": {"embedding": embedding}}
        )
        total_adicionados += 1

    print(f"✅ Embeddings adicionados para {total_adicionados} blocos.")

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
