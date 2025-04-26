from fastapi import FastAPI, Body
from services.embedding_service import EmbeddingRequest
import torch
import numpy as np

app = FastAPI(title="Microserviço de Correção com IA")


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
        "total_codigos": len(codigo_id_map),
    }
