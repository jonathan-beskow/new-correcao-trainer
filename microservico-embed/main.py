from fastapi import FastAPI
from routes.codet5_routes import router as codet5_router
from routes.similaridade_routes import router as similaridade_router
from routes.adicionar_routes import router as adicionar_routes
from services.processar_embeddings import processar_embeddings
from services.reindex_service import reindexar_todos, reindexar_blocos
from services.faiss_io import (
    carregar_index,
    salvar_index,
    carregar_codigo_id_map,
    salvar_codigo_id_map,
)
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

    try:
        model_dir = "./codet5p-220m-finetuned"
        model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
        tokenizer = AutoTokenizer.from_pretrained(model_dir)

        app.state.model = model
        app.state.tokenizer = tokenizer

        app.state.index = carregar_index(dimension=768)
        app.state.codigo_id_map = carregar_codigo_id_map()

        logger.info(
            f"🔍 Índice FAISS contém {app.state.index.ntotal} vetores carregados."
        )
        logger.info(
            f"🔍 codigo_id_map contém {len(app.state.codigo_id_map)} elementos carregados."
        )

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
        import sys

        sys.exit("Erro crítico: Falha ao carregar modelo/tokenizer.")

    # 🔁 Verificar se precisa reindexar — sempre fora do try
    precisa_reindexar = verificar_se_precisa_reindexar()
    if app.state.index.ntotal == 0 or len(app.state.codigo_id_map) == 0:
        logger.warning("⚠️ Índice FAISS ou código-ID MAP vazio! Forçando reindexação...")
        precisa_reindexar = True

    if precisa_reindexar:
        logger.info("🔎 Iniciando processamento de embeddings e reindexação...")
        processar_embeddings()
        reindexar_todos(app)
        reindexar_blocos(app)

        logger.info("💾 Salvando índice FAISS e mapa de códigos...")
        salvar_index(app.state.index)
        salvar_codigo_id_map(app.state.codigo_id_map)
        marcar_reindexacao_feita()

        logger.info("✅ Reindexação finalizada, tudo salvo e marcado.")

    if app.state.index.ntotal == 0 or len(app.state.codigo_id_map) == 0:
        logger.error(
            "❌ Reindexação concluída, mas índice FAISS ou código-ID MAP continuam vazios!"
        )
        import sys

        sys.exit("Erro crítico: Falha na reindexação. Encerrando aplicação.")
    else:
        logger.info(
            f"✅ Verificação pós-reindexação: índice contém {app.state.index.ntotal} vetores e {len(app.state.codigo_id_map)} códigos."
        )
