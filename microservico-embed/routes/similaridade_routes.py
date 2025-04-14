from fastapi import APIRouter, Request, Body
from models.schemas import SimilaridadeRequest
from services.embedding_service import gerar_embedding
from services.faiss_service import buscar_similaridade, buscar_bloco_similaridade
from services.mongo_service import buscar_documento_por_codigo, buscar_bloco_por_id

router = APIRouter()

@router.post("/buscar_similar")
async def buscar_similar(req: SimilaridadeRequest = Body(...), raw: Request = None):
    entrada = f"{req.tipo}: {req.codigo}"
    embedding = gerar_embedding(entrada)

    # 🔍 Buscar similaridade por classe completa
    resultados_classe = buscar_similaridade(embedding, k=req.k)
    similares = []

    for codigo_similar, similaridade in resultados_classe:
        doc = buscar_documento_por_codigo(codigo_similar)
        if doc:
            similares.append({
                "codigoOriginal": req.codigo,
                "codigoCorrigido": doc.get("codigoCorrigido"),
                "similaridade": similaridade,
                "origemId": str(doc.get("_id"))
            })

    # 🔎 Buscar bloco mais similar
    resultado_bloco = buscar_bloco_similaridade(embedding, k=1)
    bloco_similar = None

    if resultado_bloco:
        bloco_id, score = resultado_bloco[0]
        bloco_doc = buscar_bloco_por_id(bloco_id)
        if bloco_doc:
            bloco_similar = {
                "blocoOriginal": bloco_doc.get("blocoAntes"),
                "blocoCorrigido": bloco_doc.get("blocoDepois"),
                "nomeMetodo": bloco_doc.get("nomeMetodo"),
                "similaridade": score,
                "origemId": bloco_doc.get("origemId")
            }

    return {
        "tipo": req.tipo,
        "codigoOriginal": req.codigo,
        "similares": similares,
        "blocoMaisSimilar": bloco_similar
    }
