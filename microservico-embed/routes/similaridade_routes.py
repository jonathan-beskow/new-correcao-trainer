from fastapi import APIRouter, Request, Body
from models.schemas import SimilaridadeRequest
from services.embedding_service import gerar_embedding
from services.faiss_service import buscar_similaridade, buscar_bloco_similaridade
from services.mongo_service import buscar_documento_por_codigo, buscar_bloco_por_id
import logging

router = APIRouter()
logger = logging.getLogger("similaridade_router")


@router.post("/buscar_similar")
async def buscar_similar(req: SimilaridadeRequest = Body(...), raw: Request = None):
    logger.info(
        f"🚀 Nova requisição buscar_similar recebida: tipo={req.tipo}, k={req.k}"
    )
    logger.info(f"📝 Código recebido (até 300 caracteres): {req.codigo[:300]}...")

    entrada = f"{req.tipo}: {req.codigo}"
    embedding = gerar_embedding(entrada)

    # 🔍 Buscar similaridade por classe completa
    resultados_classe = buscar_similaridade(embedding, k=req.k)
    similares = []

    if resultados_classe:
        logger.info(f"🔎 {len(resultados_classe)} documentos similares encontrados.")
    else:
        logger.warning("⚠️ Nenhum documento similar encontrado.")

    for codigo_similar, similaridade in resultados_classe:
        doc = buscar_documento_por_codigo(codigo_similar)
        if doc:
            similares.append(
                {
                    "codigoOriginal": req.codigo,
                    "codigoCorrigido": doc.get("codigoCorrigido"),
                    "similaridade": similaridade,
                    "origemId": str(doc.get("_id")),
                }
            )

    # 🔎 Buscar bloco mais similar
    resultado_bloco = buscar_bloco_similaridade(embedding, k=1)
    bloco_similar = None

    if resultado_bloco:
        bloco_id, score = resultado_bloco[0]
        bloco_doc = buscar_bloco_por_id(bloco_id)
        if bloco_doc:
            logger.info(f"🧩 Bloco mais similar encontrado com score={score:.4f}")
            bloco_similar = {
                "blocoOriginal": bloco_doc.get("blocoAntes"),
                "blocoCorrigido": bloco_doc.get("blocoDepois"),
                "nomeMetodo": bloco_doc.get("nomeMetodo"),
                "similaridade": score,
                "origemId": bloco_doc.get("origemId"),
            }
        else:
            logger.warning("⚠️ Nenhum bloco correspondente encontrado no MongoDB.")
    else:
        logger.warning("⚠️ Nenhum bloco similar encontrado.")

    resposta = {
        "tipo": req.tipo,
        "codigoOriginal": req.codigo,
        "similares": similares,
        "blocoMaisSimilar": bloco_similar,
    }

    logger.info(
        f"📤 Retornando resposta: {len(similares)} similares e {'1 bloco' if bloco_similar else 'nenhum bloco'} encontrado(s)."
    )
    return resposta
