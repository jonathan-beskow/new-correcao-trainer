from fastapi import APIRouter, Body
from models.schemas import CodeT5Request
from services.codet5_service.suggestion_service import sugerir_codet5
from services.mongo_service import buscar_blocos_por_origem_id
from bson import ObjectId

router = APIRouter()


@router.post("/codet5_sugerir")
async def codet5_sugerir(req: CodeT5Request = Body(...)):
    blocos_exemplo = []
    blocos_correcao = []

    if req.origem_id:
        blocos = buscar_blocos_por_origem_id(req.origem_id)
        for b in blocos:
            blocos_exemplo.append(b.get("blocoAntes", ""))
            blocos_correcao.append(b.get("blocoDepois", ""))

    return {
        "sugestao": sugerir_codet5(
            tipo=req.tipo,
            exemplo=req.exemplo,
            correcao=req.correcao,
            alvo=req.alvo,
            linguagem=req.linguagem if hasattr(req, "linguagem") else "desconhecida",
            nome_metodo=req.nome_metodo if hasattr(req, "nome_metodo") else "",
            blocos_exemplo=blocos_exemplo,
            blocos_correcao=blocos_correcao,
        )
    }


@router.get("/blocos/{origem_id}")
async def get_blocos(origem_id: str):
    origem_id = origem_id.strip()

    blocos = buscar_blocos_por_origem_id(origem_id)

    # 🔁 Converte ObjectId para string antes de retornar
    for bloco in blocos:
        if "_id" in bloco:
            bloco["_id"] = str(bloco["_id"])
        if "origemId" in bloco and isinstance(bloco["origemId"], ObjectId):
            bloco["origemId"] = str(bloco["origemId"])

    return {"blocos": blocos}
