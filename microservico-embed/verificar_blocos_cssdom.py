import logging
from pymongo import MongoClient

# Configura o logger
logger = logging.getLogger("codet5-analyze")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("logs/analise_codet5.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["corretor_db"]
collection_blocos = db["casosCorrigidosBlocos"]

# Contadores
total_blocos = 0
exemplos_validos = 0
exemplos_invalidos = 0

# Verificação dos blocos
for doc in collection_blocos.find({"tipo": "cross-site scripting: dom"}):
    total_blocos += 1
    blocoAntes = doc.get("blocoAntes", "").strip()
    blocoDepois = doc.get("blocoDepois", "").strip()
    if blocoAntes and blocoDepois:
        exemplos_validos += 1
        logger.info(f"✅ Bloco válido:\n🟥 Antes: {blocoAntes[:80]}...\n🟩 Depois: {blocoDepois[:80]}...\n")
    else:
        exemplos_invalidos += 1
        logger.warning(f"⚠️ Bloco inválido encontrado: {doc}")

# Resumo
logger.info(f"📊 Total de blocos com tipo 'cross-site scripting: dom': {total_blocos}")
logger.info(f"✔️ Blocos válidos com entrada e saída: {exemplos_validos}")
logger.info(f"❌ Blocos incompletos ou inválidos: {exemplos_invalidos}")
