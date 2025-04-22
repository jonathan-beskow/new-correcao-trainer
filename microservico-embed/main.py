from fastapi import FastAPI, Body
from routes.codet5_routes import router as codet5_router
from routes.similaridade_routes import router as similaridade_router
from services.reindex_service import reindexar_todos, reindexar_blocos
from services.bloco_splitter_service import BlocoSplitterService
from services.embedding_service import EmbeddingRequest
from services.processar_embeddings import processar_embeddings
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import numpy as np
import faiss
import os
import logging

# Evita erro de duplicação com bibliotecas que usam OpenMP
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Criação da aplicação FastAPI
app = FastAPI(title="Microserviço de Correção com IA")

# 🔁 Ações ao iniciar a API
@app.on_event("startup")
async def startup_event():
    logger.info("🔄 Reindexando todos os casos corrigidos ao iniciar a API...")
    reindexar_todos()
    processar_embeddings()
    logger.info("🧠 Reindexando todos os blocos de código corrigidos...")
    reindexar_blocos()

    logger.info("🔍 Processando blocos de código para treinamento e correção...")
    splitter = BlocoSplitterService()
    splitter.processar_todos()
    splitter.processar_novos()

    # Carregando modelo e tokenizer CodeT5
    try:
        model_dir = "./codet5p-220m-finetuned"
        model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
        tokenizer = AutoTokenizer.from_pretrained(model_dir)


        # Índice FAISS para embeddings + mapeamento dos códigos adicionados
        index = faiss.IndexFlatL2(768)  # confere se o tamanho 768 está correto para seu modelo
        codigo_id_map = []

        # Armazenando tudo no app.state
        app.state.model = model
        app.state.tokenizer = tokenizer
        app.state.index = index
        app.state.codigo_id_map = codigo_id_map

        max_tokens = getattr(model.config, "n_positions", None)
        if max_tokens:
            logger.info(f"Modelo carregado com sucesso. Token máximo suportado: {max_tokens}")
        else:
            logger.warning("Não foi possível determinar o número máximo de tokens do modelo.")
    except Exception as e:
        logger.error("Erro ao carregar o modelo/tokenizer:")
        logger.exception(e)

# 🔌 Endpoint para verificar se a API está no ar
@app.get("/check")
def check_connection():
    return {"status": "OK", "message": "Python server is up and running!"}

# 🔍 Endpoint para adicionar código ao índice FAISS
@app.post("/adicionar")
async def adicionar_codigo(req: EmbeddingRequest = Body(...)):
    tokenizer = app.state.tokenizer
    model = app.state.model
    index = app.state.index
    codigo_id_map = app.state.codigo_id_map

    entrada = f"{req.tipo}: {req.codigo}"
    tokens = tokenizer(entrada, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**tokens)

    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    index.add(np.array([embedding]))
    codigo_id_map.append(req.codigo)

    return {
        "message": "✅ Código adicionado com sucesso!",
        "total_codigos": len(codigo_id_map)
    }

# 📦 Inclusão das rotas
app.include_router(codet5_router, prefix="/codet5")
app.include_router(similaridade_router, prefix="/similaridade")
