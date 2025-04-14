import faiss
import numpy as np

# Índice para classes completas
index = faiss.IndexFlatL2(768)
codigo_id_map = []

# 🔄 Novo índice para blocos
index_blocos = faiss.IndexFlatL2(768)
bloco_id_map = []  # Salva o _id (str) ou qualquer identificador único

# 🧹 Reset para ambos
def reset_index():
    global index, codigo_id_map
    index = faiss.IndexFlatL2(768)
    codigo_id_map = []

def reset_index_blocos():
    global index_blocos, bloco_id_map
    index_blocos = faiss.IndexFlatL2(768)
    bloco_id_map = []

# Adicionar classe
def adicionar_embedding(embedding, codigo_original):
    vetor = np.array([embedding], dtype=np.float32)
    index.add(vetor)
    codigo_id_map.append(codigo_original)

# Adicionar bloco
def adicionar_bloco_embedding(embedding, bloco_id):
    vetor = np.array([embedding], dtype=np.float32)
    index_blocos.add(vetor)
    bloco_id_map.append(bloco_id)

# Buscar similaridade de classe
def buscar_similaridade(embedding, k=1):
    if len(codigo_id_map) == 0:
        return []

    embedding_array = np.array([embedding], dtype=np.float32)
    D, I = index.search(embedding_array, k=k)

    similares = []
    for j, i in enumerate(I[0]):
        if i < len(codigo_id_map):
            similares.append((codigo_id_map[i], float(1.0 / (1.0 + D[0][j]))))

    return similares

# ✅ Buscar similaridade de blocos
def buscar_bloco_similaridade(embedding, k=1):
    if len(bloco_id_map) == 0:
        return []

    embedding_array = np.array([embedding], dtype=np.float32)
    D, I = index_blocos.search(embedding_array, k=k)

    similares = []
    for j, i in enumerate(I[0]):
        if i < len(bloco_id_map):
            similares.append((bloco_id_map[i], float(1.0 / (1.0 + D[0][j]))))

    return similares
