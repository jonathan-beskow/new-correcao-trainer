from fastapi import FastAPI
from routes.codet5_routes import router as codet5_router
from routes.similaridade_routes import router as similaridade_router
from services.reindex_service import reindexar_todos, reindexar_blocos
from services.bloco_splitter_service import BlocoSplitterService
import os
import logging

# Para evitar erro de duplicação
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(title="Microserviço de Correção com IA")

# 🔁 Ações ao iniciar a API
@app.on_event("startup")
async def startup_event():
    logger.info("🔄 Reindexando todos os casos corrigidos ao iniciar a API...")
    reindexar_todos()

    logger.info("🧠 Reindexando todos os blocos de código corrigidos...")
    reindexar_blocos()

    logger.info("🔍 Verificando blocos de código para processamento...")
    splitter = BlocoSplitterService()
    splitter.processar_todos()
    splitter.processar_novos()

    # ✅ Verificação do modelo CodeT5
    from transformers import AutoModelForSeq2SeqLM

    model_dir = "./codet5-finetuned-vulnerabilities-trainer"
    try:
        model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
        max_tokens = getattr(model.config, "n_positions", None)
        if max_tokens:
            logger.info(f"✅ Modelo carregado com sucesso. Token máximo suportado: {max_tokens}")
        else:
            logger.warning("⚠️ Não foi possível determinar o número máximo de tokens do modelo.")
    except Exception as e:
        logger.error("❌ Erro ao carregar o modelo para verificar os tokens:")
        logger.exception(e)

# 🔌 Incluir rotas com prefixos
app.include_router(codet5_router, prefix="/codet5")
app.include_router(similaridade_router, prefix="/similaridade")
