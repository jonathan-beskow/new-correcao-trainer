from pydantic import BaseModel, Field
from typing import Optional


class SimilaridadeRequest(BaseModel):
    codigo: str
    tipo: str
    k: int = 1


class SugestaoResponse(BaseModel):
    sugestao: str


class CodeT5Request(BaseModel):
    tipo: str
    exemplo: str
    correcao: str
    alvo: str
    origem_id: Optional[str] = None
    linguagem: Optional[str] = None
    nome_metodo: Optional[str] = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class NovoCasoRequest(BaseModel):
    tipo: str
    codigoOriginal: str
    codigoCorrigido: str
    justificativa: str = "Cadastro manual"
