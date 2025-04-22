import os
import sys
import json
import torch
import logging
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSeq2SeqLM,
    Trainer, TrainingArguments
)
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
# 1. Carregar datasets prontos
# ================================
logger.info("📂 Carregando datasets preparados...")
dataset_dir = "dataset_codet5"

def carregar_dataset(split):
    path = os.path.join(dataset_dir, f"{split}.json")
    if not os.path.exists(path):
        logger.error(f"❌ Arquivo não encontrado: {path}")
        exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return Dataset.from_list(json.load(f))

dataset_train = carregar_dataset("train")
dataset_val = carregar_dataset("val")

logger.info(f"✅ Dataset carregado: {len(dataset_train)} exemplos de treino, {len(dataset_val)} exemplos de validação.")

# ================================
# 2. Carregar modelo e tokenizer
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
# 3. Pré-processamento
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
train_tokenized = dataset_train.map(preprocess, remove_columns=dataset_train.column_names)
val_tokenized = dataset_val.map(preprocess, remove_columns=dataset_val.column_names)

# ================================
# 4. Diretórios
# ================================
output_dir = "./codet5p-220m-finetuned"
log_dir = "./logs"
os.makedirs(output_dir, exist_ok=True)

# ================================
# 5. Argumentos de treino
# ================================
training_args = TrainingArguments(
    output_dir=output_dir,
    overwrite_output_dir=True,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    save_strategy="epoch",
    eval_strategy="epoch",
    save_total_limit=2,
    logging_dir=log_dir,
    logging_steps=1,
    logging_first_step=True,
    fp16=use_fp16,
    dataloader_pin_memory=True,
    report_to="none"
)

# ================================
# 6. Trainer
# ================================
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_tokenized,
    eval_dataset=val_tokenized,
    tokenizer=tokenizer
)

# ================================
# 7. Executar treinamento
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
