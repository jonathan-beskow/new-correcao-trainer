import logging
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger("codet5_model")

model_path = "./codet5p-220m-finetuned"
tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.model_max_length = 4096
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
MAX_TOKENS = model.config.n_positions or 4096

__all__ = ["model", "tokenizer", "device", "MAX_TOKENS"]