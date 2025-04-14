# services/codet5_service.py
import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from services.mongo_service import buscar_blocos_por_origem_id

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

    logger.info(f"🔍 {len(blocos_exemplo)} blocos encontrados para origemId={origem_id}")

    prompt_partes = [
        f"[tipo]: {tipo}",
        f"[linguagem]: {linguagem}",
        f"[metodo]: {nome_metodo}",
    ]

    prompt_tokens = sum(len(tokenizer.encode(p, truncation=False)) for p in prompt_partes)
    token_margin = 200  # espaço reservado pro alvo

    for idx, (b_ex, b_corr) in enumerate(zip(blocos_exemplo, blocos_correcao)):
        bloco_info = f"[exemplo_{idx+1}]: {b_ex}\n[correcao_{idx+1}]: {b_corr}"
        bloco_tokens = len(tokenizer.encode(bloco_info, truncation=False))
        if prompt_tokens + bloco_tokens + token_margin > MAX_TOKENS:
            logger.warning(f"⚠️ Prompt truncado em {idx} blocos por limite de tokens.")
            break
        prompt_partes.append(bloco_info)
        prompt_tokens += bloco_tokens
        logger.info(f"📦 Bloco {idx+1}:\n🟥 {b_ex[:150]}...\n🟩 {b_corr[:150]}...")

    prompt_partes.append(f"[alvo]: {alvo}")
    prompt = "\n".join(prompt_partes)
    total_tokens = len(tokenizer.encode(prompt, truncation=False))
    logger.info(f"🧮 Tokens no prompt final: {total_tokens}")

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
    return resposta
