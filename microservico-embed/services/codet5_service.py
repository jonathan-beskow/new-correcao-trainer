# services/codet5_service.py
import logging
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from services.mongo_service import buscar_blocos_por_origem_id, buscar_blocos_por_tipo, buscar_bloco_por_id
from services.embedding_service import gerar_embedding
from services.faiss_service import buscar_bloco_similaridade
from services.avaliador import avaliar_sugestao

# Logger
logger = logging.getLogger("codet5")
logging.basicConfig(level=logging.INFO)

# Caminho do modelo treinado
model_path = "./codet5p-220m-finetuned"

# Carrega tokenizer e modelo
tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.model_max_length = 4096

model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Tokens máximos permitidos
MAX_TOKENS = model.config.n_positions or 4096

def sugerir_codet5(
    tipo: str,
    exemplo: str,
    correcao: str,
    alvo: str,
    linguagem: str = "desconhecida",
    nome_metodo: str = "",
    origem_id: str = None,
    blocos_exemplo: list[str] = None,
    blocos_correcao: list[str] = None
) -> str:
    blocos_exemplo = blocos_exemplo or []
    blocos_correcao = blocos_correcao or []

    if origem_id and not blocos_exemplo:
        blocos = buscar_blocos_por_origem_id(origem_id)
        for b in blocos:
            blocos_exemplo.append(b.get("blocoAntes", ""))
            blocos_correcao.append(b.get("blocoDepois", ""))
        logger.info(f"🔄 Blocos carregados via origem_id ({origem_id}): {len(blocos)}")

    if not blocos_exemplo and tipo and alvo:
        logger.warning("⚠️ Nenhum bloco passado ou carregado. Buscando exemplos mais similares via FAISS...")
        entrada = f"{tipo}: {alvo}"
        embedding = gerar_embedding(entrada)
        resultado_blocos = buscar_bloco_similaridade(embedding, k=3)
        for bloco_id, score in resultado_blocos:
            bloco_doc = buscar_bloco_por_id(bloco_id)
            if bloco_doc:
                blocos_exemplo.append(bloco_doc.get("blocoAntes", ""))
                blocos_correcao.append(bloco_doc.get("blocoDepois", ""))
                logger.info(f"🧠 Bloco similar encontrado (score={score:.2f}): {bloco_doc.get('blocoAntes')[:100]}...")

    if not blocos_exemplo and tipo:
        logger.warning("⚠️ Nenhum bloco similar encontrado. Usando blocos genéricos do tipo: %s", tipo)
        blocos_genericos = buscar_blocos_por_tipo(tipo, limite=5)
        for b in blocos_genericos:
            blocos_exemplo.append(b.get("blocoAntes", ""))
            blocos_correcao.append(b.get("blocoDepois", ""))
        logger.info(f"🔄 Blocos genéricos carregados do tipo '{tipo}': {len(blocos_exemplo)}")

    prompt_partes = []

    for idx, (b_ex, b_corr) in enumerate(zip(blocos_exemplo, blocos_correcao)):
        bloco_info = f"Exemplo: {b_ex}\nCorreção: {b_corr}"
        prompt_tokens = sum(len(tokenizer.encode(p, truncation=False)) for p in prompt_partes)
        token_margin = 200
        bloco_tokens = len(tokenizer.encode(bloco_info, truncation=False))
        if prompt_tokens + bloco_tokens + token_margin > MAX_TOKENS:
            logger.warning(f"⚠️ Prompt truncado em {idx} blocos por limite de tokens.")
            break
        prompt_partes.append(bloco_info)
        logger.info(f"📦 Bloco {idx+1} incluído no prompt:\n🟥 {b_ex[:150]}...\n🟩 {b_corr[:150]}...")

    prompt_partes.append(f"Corrija o seguinte código vulnerável do tipo {tipo}:")
    prompt_partes.append(alvo)

    prompt = "\n".join(prompt_partes)
    total_tokens = len(tokenizer.encode(prompt, truncation=False))
    logger.info(f"🧮 Tokens no prompt final: {total_tokens}")
    logger.info(f"📝 Prompt enviado ao modelo:\n{prompt}")

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_TOKENS, padding="max_length")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=512,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3
        )

    resposta = tokenizer.decode(outputs[0], skip_special_tokens=True)
    logger.info("✅ Sugestão gerada com sucesso.")
    logger.info("🧠 Sugestão bruta do modelo:\n" + resposta)

    avaliacao = avaliar_sugestao(alvo, correcao, resposta)
    logger.info(f"📊 Avaliação automática: {avaliacao}")

    if resposta.strip() in [c.strip() for c in blocos_correcao]:
        logger.warning("⚠️ A sugestão gerada é idêntica a uma das correções de exemplo. Pode indicar cópia literal.")

    return resposta
