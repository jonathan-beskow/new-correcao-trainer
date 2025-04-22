from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

from pydantic import BaseModel

class EmbeddingRequest(BaseModel):
    tipo: str
    codigo: str


# def gerar_embedding(texto: str):
#     tokens = tokenizer(texto, return_tensors="pt", truncation=True, max_length=512)
#     with torch.no_grad():
#         outputs = model(**tokens)
#     return outputs.last_hidden_state.mean(dim=1).squeeze().numpy().tolist()
def gerar_embedding(texto: str):
    tokens = tokenizer(texto, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**tokens)

    token_embeddings = outputs.last_hidden_state[0][1:-1] 
    if len(token_embeddings) == 0:
        # fallback seguro
        token_embeddings = outputs.last_hidden_state[0]

    pooled = token_embeddings.mean(dim=0)
    normalized = pooled / pooled.norm()
    return normalized.numpy().tolist()
