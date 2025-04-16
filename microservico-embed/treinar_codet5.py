import os
import sys
import torch
import logging
from pymongo import MongoClient
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSeq2SeqLM,
    Trainer, TrainingArguments
)
from difflib import SequenceMatcher
from transformers.utils import logging as hf_logging

# ================================
# Logging configurado
# ================================
hf_logging.set_verbosity_info()
logger = logging.getLogger("codet5-train")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(message)s'))
console_handler.stream.reconfigure(encoding='utf-8')
logger.addHandler(console_handler)

os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/treinamento.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# ================================
# 1. Conectar ao MongoDB
# ================================
logger.info("🌐 Conectando ao MongoDB...")
client = MongoClient("mongodb://localhost:27017/")
db = client["corretor_db"]
collection = db["casosCorrigidos"]
collection_blocos = db["casosCorrigidosBlocos"]

# ================================
# 2. Carregar e refinar exemplos
# ================================
logger.info("🔍 Extraindo e refinando exemplos do MongoDB...")
dados = []

def extrair_diferencas(origem: str, destino: str) -> str:
    matcher = SequenceMatcher(None, origem.splitlines(), destino.splitlines())
    linhas_modificadas = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            linhas_modificadas.extend(destino.splitlines()[j1:j2])
    return '\n'.join(linhas_modificadas).strip()

# Casos completos
for doc in collection.find():
    entrada = doc.get("codigoOriginal", "").strip()
    saida = doc.get("codigoCorrigido", "").strip()
    tipo = doc.get("tipo", "").strip()
    if entrada and saida:
        dados.append({
            "input": f"Corrija este código vulnerável do tipo {tipo}:\n{entrada}",
            "output": saida
        })

# Blocos refinados
for bloco in collection_blocos.find():
    entrada = bloco.get("blocoAntes", "").strip()
    saida = bloco.get("blocoDepois", "").strip()
    tipo = bloco.get("tipo", "").strip()
    if entrada and saida:
        refinado = extrair_diferencas(entrada, saida)
        dados.append({
            "input": f"Corrija este bloco vulnerável do tipo {tipo}:\n{entrada}",
            "output": refinado if refinado else saida
        })

logger.info(f"✅ Total de exemplos coletados e refinados: {len(dados)}")
if not dados:
    logger.warning("⚠️ Nenhum exemplo encontrado. Encerrando.")
    exit(0)

# ================================
# 3. Dataset HuggingFace
# ================================
dataset = Dataset.from_list(dados)

# ================================
# 4. Carregar modelo e tokenizer
# ================================
model_name = "Salesforce/codet5p-220m"
logger.info(f"📦 Carregando modelo: {model_name}")
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.model_max_length = 4096

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
use_fp16 = torch.cuda.is_available()

model = AutoModelForSeq2SeqLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if use_fp16 else torch.float32
).to(device)

# ================================
# 5. Pré-processamento
# ================================
def preprocess(example):
    model_inputs = tokenizer(
        example["input"],
        max_length=1024,
        padding="max_length",
        truncation=True
    )
    labels = tokenizer(
        text_target=example["output"],
        max_length=512,
        padding="max_length",
        truncation=True
    )
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

logger.info("🔧 Tokenizando exemplos...")
tokenized_dataset = dataset.map(preprocess, remove_columns=dataset.column_names)

# ================================
# 6. Diretórios
# ================================
output_dir = "./codet5p-220m-finetuned"
log_dir = "./logs"
os.makedirs(output_dir, exist_ok=True)

# ================================
# 7. Argumentos de treino
# ================================
training_args = TrainingArguments(
    output_dir=output_dir,
    overwrite_output_dir=True,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    save_strategy="epoch",
    save_total_limit=2,
    logging_dir=log_dir,
    logging_steps=1,
    logging_first_step=True,
    fp16=use_fp16,
    dataloader_pin_memory=True,
    report_to="none"
)

# ================================
# 8. Trainer
# ================================
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer
)

# ================================
# 9. Executar treinamento
# ================================
logger.info("🚀 Iniciando treinamento do CodeT5p-220m...")
try:
    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    logger.info("✅ Modelo salvo em: %s", output_dir)
except Exception as e:
    logger.exception("❌ Erro durante o treinamento!")
    print("\n⚠️ Erro detectado:", str(e))
    import traceback
    traceback.print_exc()
    exit(1)
