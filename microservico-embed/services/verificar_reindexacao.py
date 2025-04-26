from pymongo import MongoClient


def verificar_se_precisa_reindexar():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["corretor_db"]
    collection_controle = db["controleSistema"]

    controle = collection_controle.find_one({"tipo": "reindexacao"})

    if controle and controle.get("ja_reindexado", False):
        print("✅ Sistema já reindexado anteriormente. Pulando reindexação.")
        return False
    else:
        print("🔁 Sistema nunca reindexado. Será necessário reindexar.")
        return True


def marcar_reindexacao_feita():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["corretor_db"]
    collection_controle = db["controleSistema"]

    collection_controle.update_one(
        {"tipo": "reindexacao"}, {"$set": {"ja_reindexado": True}}, upsert=True
    )
