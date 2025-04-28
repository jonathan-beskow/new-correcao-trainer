import logging
import torch
from services.codet5_service.model_handler import model, tokenizer, device, MAX_TOKENS
from services.codet5_service.fallback_service import (
    fallback_para_java,
    diferenca_percentual,
)
from services.mongo_service import (
    buscar_blocos_por_origem_id,
    buscar_blocos_por_tipo,
    buscar_todos_blocos,
)
from services.embedding_service import gerar_embedding
from services.avaliador import avaliar_sugestao

logger = logging.getLogger("codet5_suggestion")


def construir_prompt(tipo, alvo, blocos_exemplo, blocos_correcao):
    prompt_partes = []
    scores = []

    for idx, (b_ex, b_corr) in enumerate(zip(blocos_exemplo, blocos_correcao)):
        bloco_info = f"Exemplo: {b_ex}\nCorreção: {b_corr}"
        prompt_tokens = sum(
            len(tokenizer.encode(p, truncation=False)) for p in prompt_partes
        )
        token_margin = 200
        bloco_tokens = len(tokenizer.encode(bloco_info, truncation=False))

        if prompt_tokens + bloco_tokens + token_margin > MAX_TOKENS:
            logger.warning(f"⚠️ Prompt truncado após {idx} blocos.")
            break

        prompt_partes.append(bloco_info)

    prompt_partes.append(f"Corrija o seguinte código vulnerável do tipo {tipo}:")
    prompt_partes.append(alvo)
    prompt = "\n".join(prompt_partes)

    return prompt


def gerar_resposta(prompt):
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_TOKENS,
        padding="max_length",
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=512,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3,
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def sugerir_codet5(
    tipo,
    exemplo,
    correcao,
    alvo,
    linguagem="desconhecida",
    nome_metodo="",
    origem_id=None,
    blocos_exemplo=None,
    blocos_correcao=None,
    permitir_fallback=True,
):
    blocos_exemplo = blocos_exemplo or []
    blocos_correcao = blocos_correcao or []

    # 🔵 Carrega blocos via origem_id, se fornecido
    if origem_id and not blocos_exemplo:
        blocos = buscar_blocos_por_origem_id(origem_id)
        for b in blocos:
            blocos_exemplo.append(b.get("blocoAntes", ""))
            blocos_correcao.append(b.get("blocoDepois", ""))
        logger.info(f"🔄 Blocos carregados via origem_id ({origem_id}): {len(blocos)}")

    # 🔵 Busca blocos similares via embeddings
    if not blocos_exemplo and tipo and alvo:
        logger.info(
            f"🔎 Buscando blocos do tipo '{tipo}' para comparação por similaridade..."
        )
        entrada_embedding = gerar_embedding(f"{tipo}: {alvo}")

        blocos_filtrados = [
            b
            for b in buscar_todos_blocos()
            if b.get("tipo", "").lower().strip() == tipo.lower().strip()
            and b.get("blocoAntes")
            and b.get("blocoDepois")
        ]

        if blocos_filtrados:
            scored_blocos = []
            for b in blocos_filtrados:
                texto_bloco = f"{tipo}: {b['blocoAntes']}"
                emb_bloco = gerar_embedding(texto_bloco)
                score = torch.nn.functional.cosine_similarity(
                    torch.tensor(entrada_embedding), torch.tensor(emb_bloco), dim=0
                ).item()
                scored_blocos.append((b, score))

            scored_blocos = [(b, s) for b, s in scored_blocos if s >= 0.8]

            scored_blocos.sort(key=lambda x: x[1], reverse=True)
            for b, score in scored_blocos[:3]:
                blocos_exemplo.append(b.get("blocoAntes", ""))
                blocos_correcao.append(b.get("blocoDepois", ""))
                logger.info(
                    f"🧠 Bloco similar (score={score:.4f}): {b.get('blocoAntes')[:100]}..."
                )

            if scored_blocos:
                score_medio = sum(s for _, s in scored_blocos) / len(scored_blocos)
                logger.info(f"🧠 Score médio dos blocos usados: {score_medio:.4f}")
        else:
            logger.warning(f"⚠️ Nenhum bloco encontrado com tipo '{tipo}'.")

    # 🔵 Fallback para blocos genéricos
    if not blocos_exemplo and tipo:
        blocos_genericos = buscar_blocos_por_tipo(tipo, limite=5)
        for b in blocos_genericos:
            blocos_exemplo.append(b.get("blocoAntes", ""))
            blocos_correcao.append(b.get("blocoDepois", ""))
        logger.info(
            f"🔄 Blocos genéricos carregados para tipo '{tipo}': {len(blocos_exemplo)}"
        )

    # 🚀 Construir o prompt
    prompt = construir_prompt(tipo, alvo, blocos_exemplo, blocos_correcao)

    logger.info(f"🧮 Tokens no prompt: {len(tokenizer.encode(prompt))}")
    logger.info(f"📝 Prompt:\n{prompt}")

    if len(tokenizer.encode(prompt)) < 100:
        logger.warning("⚠️ Prompt pequeno demais. Ativando fallback imediatamente...")
        return fallback_para_java(tipo, exemplo, correcao, alvo)

    # 🚀 Gerar resposta
    resposta = gerar_resposta(prompt)
    logger.info("✅ Sugestão gerada com sucesso.")
    logger.info("🧠 Resposta:\n" + resposta)

    # ✅ Avaliar resposta (AQUI!)
    avaliacao = avaliar_sugestao(alvo, correcao, resposta)
    logger.info(f"📊 Avaliação automática: {avaliacao}")

    # 🚨 Se muito similar ao alvo e incorreto, ativar fallback
    if (diferenca_percentual(alvo, resposta) < 0.05) and not avaliacao.get(
        "correto_esperado", False
    ):
        if permitir_fallback:
            logger.warning(
                "⚠️ Resposta muito similar à entrada e incorreta. Ativando fallback via Java..."
            )
            resposta = fallback_para_java(tipo, exemplo, correcao, alvo)
            logger.info("✅ Fallback via Java concluído.")
        else:
            logger.warning(
                "⚠️ Resposta muito similar, mas fallback desativado (permitir_fallback=False). Retornando sugestão como está."
            )

    return resposta
