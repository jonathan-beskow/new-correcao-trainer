from fastapi import FastAPI
from routes.codet5_routes import router as codet5_router
from routes.similaridade_routes import router as similaridade_router
from routes.adicionar_routes import router as adicionar_routes
from services.processar_embeddings import processar_embeddings
from services.reindex_service import reindexar_todos, reindexar_blocos
from services.verificar_reindexacao import (
    verificar_se_precisa_reindexar,
    marcar_reindexacao_feita,
)
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import faiss
import os
import logging

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(title="Microserviço de Correção com IA")

# 📦 Inclusão das rotas
app.include_router(codet5_router, prefix="/codet5")
app.include_router(similaridade_router, prefix="/similaridade")
app.include_router(adicionar_routes)


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Inicializando microserviço...")

    # 🧠 Carregando modelo e tokenizer primeiro
    try:
        model_dir = "./codet5p-220m-finetuned"
        model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
        tokenizer = AutoTokenizer.from_pretrained(model_dir)

        index = faiss.IndexFlatL2(768)
        codigo_id_map = []

        app.state.model = model
        app.state.tokenizer = tokenizer
        app.state.index = index
        app.state.codigo_id_map = codigo_id_map

        max_tokens = getattr(model.config, "n_positions", None)
        if max_tokens:
            logger.info(
                f"Modelo carregado com sucesso. Tokens máximos suportados: {max_tokens}"
            )
        else:
            logger.warning(
                "Modelo carregado, mas número de tokens máximos não encontrado."
            )
    except Exception as e:
        logger.error("❌ Erro ao carregar o modelo/tokenizer:")
        logger.exception(e)

    # 🔍 Verificando se precisa processar embeddings e reindexar
    if verificar_se_precisa_reindexar():
        logger.info(
            "🔎 Reindexação necessária. Iniciando processamento de embeddings e reindexação..."
        )

        processar_embeddings()
        reindexar_todos()
        reindexar_blocos()

        marcar_reindexacao_feita()
        logger.info("✅ Reindexação realizada e marcada com sucesso.")
    else:
        logger.info("✅ Reindexação já realizada anteriormente. Pulando processamento.")
