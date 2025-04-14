from services.mongo_service import buscar_todos_documentos
from services.embedding_service import gerar_embedding
from services.faiss_service import (
    reset_index,
    adicionar_embedding,
    reset_index_blocos,
    adicionar_bloco_embedding
)

def reindexar_todos():
    print("🔁 Iniciando reindexação do FAISS...")
    reset_index()

    documentos = buscar_todos_documentos()
    if not documentos:
        print("⚠️ Nenhum dado encontrado no MongoDB para reindexar.")
        return

    for doc in documentos:
        entrada = f"{doc.get('tipo', '')}: {doc.get('codigoOriginal', '')}"
        embedding = gerar_embedding(entrada)
        adicionar_embedding(embedding, doc["codigoOriginal"])

    print(f"✅ Reindexação concluída: {len(documentos)} casos carregados.")

def reindexar_blocos():
    from services.mongo_service import buscar_todos_blocos  # <- Importação local ok também
    print("🧠 Reindexando todos os blocos de código corrigidos...")
    reset_index_blocos()

    blocos = buscar_todos_blocos()
    if not blocos:
        print("⚠️ Nenhum bloco encontrado para reindexar.")
        return

    for bloco in blocos:
        embedding = gerar_embedding(bloco["blocoAntes"])
        adicionar_bloco_embedding(embedding, str(bloco["_id"]))

    print(f"✅ Blocos reindexados: {len(blocos)}")
