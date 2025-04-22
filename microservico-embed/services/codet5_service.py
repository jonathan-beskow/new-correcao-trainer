# import logging
# import torch
# import requests
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# from services.mongo_service import (
#     buscar_blocos_por_origem_id,
#     buscar_blocos_por_tipo,
#     buscar_bloco_por_id,
#     buscar_todos_blocos,
# )
# from services.embedding_service import gerar_embedding
# from services.avaliador import avaliar_sugestao

# # Logger
# logger = logging.getLogger("codet5")
# logging.basicConfig(level=logging.INFO)

# model_path = "./codet5p-220m-finetuned"
# tokenizer = AutoTokenizer.from_pretrained(model_path)
# tokenizer.model_max_length = 4096
# model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model.to(device)
# MAX_TOKENS = model.config.n_positions or 4096

# def diferenca_percentual(a, b):
#     if not a: return 1.0
#     return abs(len(a) - len(b)) / len(a)

# def fallback_para_java(tipo, exemplo, correcao, alvo):
#     try:
#         payload = {
#             "tipo": tipo,
#             "exemplo": exemplo,
#             "correcao": correcao,
#             "codigo": alvo
#         }
#         resposta = requests.post("http://localhost:8080/corrigir/fallback", json=payload)
#         if resposta.ok:
#             return resposta.json().get("codigoCorrigido", "")
#         else:
#             logger.error(f"Erro no fallback Java: {resposta.status_code}")
#     except Exception as e:
#         logger.error(f"Erro na requisição fallback: {e}")
#     return "Erro: fallback falhou."

# def sugerir_codet5(
#     tipo: str,
#     exemplo: str,
#     correcao: str,
#     alvo: str,
#     linguagem: str = "desconhecida",
#     nome_metodo: str = "",
#     origem_id: str = None,
#     blocos_exemplo: list[str] = None,
#     blocos_correcao: list[str] = None
# ) -> str:
#     blocos_exemplo = blocos_exemplo or []
#     blocos_correcao = blocos_correcao or []

#     if origem_id and not blocos_exemplo:
#         blocos = buscar_blocos_por_origem_id(origem_id)
#         for b in blocos:
#             blocos_exemplo.append(b.get("blocoAntes", ""))
#             blocos_correcao.append(b.get("blocoDepois", ""))
#         logger.info(f"🔄 Blocos carregados via origem_id ({origem_id}): {len(blocos)}")

#     if not blocos_exemplo and tipo and alvo:
#         logger.warning("⚠️ Nenhum bloco passado. Filtrando por tipo antes da busca FAISS...")
#         entrada_embedding = gerar_embedding(f"{tipo}: {alvo}")
#         blocos_filtrados = [
#             b for b in buscar_todos_blocos()
#             if b.get("tipo", "").lower().strip() == tipo.lower().strip()
#         ]
#         if not blocos_filtrados:
#             logger.warning(f"⚠️ Nenhum bloco do tipo '{tipo}' encontrado.")
#         else:
#             scored_blocos = []
#             for b in blocos_filtrados:
#                 entrada_bloco = f"{tipo}: {b.get('blocoAntes', '')}"
#                 embedding_bloco = gerar_embedding(entrada_bloco)
#                 score = torch.nn.functional.cosine_similarity(
#                     torch.tensor(entrada_embedding), torch.tensor(embedding_bloco), dim=0
#                 ).item()
#                 scored_blocos.append((b, score))

#             scored_blocos.sort(key=lambda x: x[1], reverse=True)
#             for b, score in scored_blocos[:3]:
#                 blocos_exemplo.append(b.get("blocoAntes", ""))
#                 blocos_correcao.append(b.get("blocoDepois", ""))
#                 logger.info(f"🧠 Bloco similar (score={score:.2f}): {b.get('blocoAntes')[:100]}...")

#     if not blocos_exemplo and tipo:
#         blocos_genericos = buscar_blocos_por_tipo(tipo, limite=5)
#         for b in blocos_genericos:
#             blocos_exemplo.append(b.get("blocoAntes", ""))
#             blocos_correcao.append(b.get("blocoDepois", ""))
#         logger.info(f"🔄 Blocos genéricos carregados do tipo '{tipo}': {len(blocos_exemplo)}")

#     prompt_partes = []
#     for idx, (b_ex, b_corr) in enumerate(zip(blocos_exemplo, blocos_correcao)):
#         bloco_info = f"Exemplo: {b_ex}\nCorreção: {b_corr}"
#         prompt_tokens = sum(len(tokenizer.encode(p, truncation=False)) for p in prompt_partes)
#         token_margin = 200
#         bloco_tokens = len(tokenizer.encode(bloco_info, truncation=False))
#         if prompt_tokens + bloco_tokens + token_margin > MAX_TOKENS:
#             logger.warning(f"⚠️ Prompt truncado após {idx} blocos.")
#             break
#         prompt_partes.append(bloco_info)

#     prompt_partes.append(f"Corrija o seguinte código vulnerável do tipo {tipo}:")
#     prompt_partes.append(alvo)

#     prompt = "\n".join(prompt_partes)
#     logger.info(f"🧮 Tokens no prompt: {len(tokenizer.encode(prompt))}")
#     logger.info(f"📝 Prompt:\n{prompt}")

#     inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_TOKENS, padding="max_length")
#     inputs = {k: v.to(device) for k, v in inputs.items()}

#     with torch.no_grad():
#         outputs = model.generate(
#             **inputs,
#             max_length=512,
#             num_beams=4,
#             early_stopping=True,
#             no_repeat_ngram_size=3
#         )

#     resposta = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     logger.info("✅ Sugestão gerada com sucesso.")
#     logger.info("🧠 Resposta:\n" + resposta)

#     avaliacao = avaliar_sugestao(alvo, correcao, resposta)
#     logger.info(f"📊 Avaliação automática: {avaliacao}")

#     # Novo fallback com base em diferença de texto
#     if diferenca_percentual(alvo, resposta) < 0.05:
#         logger.warning("⚠️ Resposta muito similar ao código de entrada. Ativando fallback...")
#         resposta = fallback_para_java(tipo, exemplo, correcao, alvo)
#         logger.info("✅ Fallback via Java finalizado.")

#     return resposta
