from services.mongo_service import buscar_todos_documentos, buscar_todos_blocos
from services.embedding_service import gerar_embedding
import numpy as np  # <- adicionar no topo


def reindexar_todos(app):
    print("🔁 Iniciando reindexação do FAISS...")

    documentos = buscar_todos_documentos()
    if not documentos:
        print("⚠️ Nenhum dado encontrado no MongoDB para reindexar.")
        return

    app.state.index.reset()
    app.state.codigo_id_map.clear()

    for doc in documentos:
        entrada = f"{doc.get('tipo', '')}: {doc.get('codigoOriginal', '')}"
        embedding = gerar_embedding(entrada)

        if embedding is not None:
            embedding_np = np.array(embedding, dtype=np.float32)  # 👈 CONVERSÃO CERTA
            app.state.index.add(embedding_np.reshape(1, -1))
            app.state.codigo_id_map.append(doc["codigoOriginal"])

    print(f"✅ Reindexação concluída: {len(documentos)} casos carregados.")


def reindexar_blocos(app):
    print("🧠 Reindexando todos os blocos de código corrigidos...")

    blocos = buscar_todos_blocos()
    if not blocos:
        print("⚠️ Nenhum bloco encontrado para reindexar.")
        return

    for bloco in blocos:
        embedding = gerar_embedding(bloco["blocoAntes"])

        if embedding is not None:
            embedding_np = np.array(embedding, dtype=np.float32)  # 👈 CONVERSÃO CERTA
            app.state.index.add(embedding_np.reshape(1, -1))
            app.state.codigo_id_map.append(str(bloco["_id"]))

    print(f"✅ Blocos reindexados: {len(blocos)}")
