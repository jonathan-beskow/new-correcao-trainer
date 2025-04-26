import faiss
import pickle
import os
import logging

INDEX_PATH = "./faiss_index.idx"
CODIGO_ID_MAP_PATH = "./codigo_id_map.pkl"

logger = logging.getLogger("faiss_io")


def salvar_index(index):
    """Salva o índice FAISS em disco."""
    faiss.write_index(index, INDEX_PATH)
    logger.info(f"✅ Índice FAISS salvo em {INDEX_PATH}.")


def carregar_index(dimension=768):
    """Carrega o índice FAISS do disco, ou cria um novo vazio se não existir."""
    if os.path.exists(INDEX_PATH):
        logger.info(f"✅ Carregando índice FAISS salvo: {INDEX_PATH}")
        return faiss.read_index(INDEX_PATH)
    else:
        logger.warning("⚠️ Índice FAISS não encontrado. Criando novo índice vazio.")
        return faiss.IndexFlatL2(dimension)


def salvar_codigo_id_map(codigo_id_map):
    """Salva a lista de mapeamento de IDs."""
    with open(CODIGO_ID_MAP_PATH, "wb") as f:
        pickle.dump(codigo_id_map, f)
    logger.info(f"✅ Mapa de código-ID salvo em {CODIGO_ID_MAP_PATH}.")


def carregar_codigo_id_map():
    """Carrega a lista de mapeamento de IDs."""
    if os.path.exists(CODIGO_ID_MAP_PATH):
        with open(CODIGO_ID_MAP_PATH, "rb") as f:
            logger.info(f"✅ Carregando mapa de código-ID salvo: {CODIGO_ID_MAP_PATH}")
            return pickle.load(f)
    else:
        logger.warning("⚠️ Mapa de código-ID não encontrado. Iniciando lista vazia.")
        return []
