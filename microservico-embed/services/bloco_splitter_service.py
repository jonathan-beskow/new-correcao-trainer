# services/bloco_splitter_service.py

import re, hashlib
from datetime import datetime
from pymongo import MongoClient, errors
from bson import ObjectId

class BlocoSplitterService:
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="corretor_db"):
        try:
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            self.client.server_info()  # força teste de conexão
            print(f"✅ Conectado ao MongoDB com sucesso: {mongo_uri}")
        except errors.ServerSelectionTimeoutError as err:
            print(f"❌ Falha ao conectar no MongoDB: {err}")
            raise

        self.db = self.client[db_name]
        self.casos = self.db["casosCorrigidos"]
        self.blocos = self.db["casosCorrigidosBlocos"]
        print(f"📂 Coleções disponíveis: {self.db.list_collection_names()}")

    def detectar_linguagem(self, texto):
        if "<%@ page" in texto or "<jsp:" in texto or "form:" in texto:
            return "jsp"
        if "<html" in texto or "<form" in texto:
            return "html"
        if "function(" in texto or "$(" in texto:
            return "javascript"
        if "class " in texto and "public" in texto:
            return "java"
        return "plain"

    def quebrar_blocos(self, codigo, linguagem):
        if linguagem in ("html", "jsp", "jstl"):
            blocos = re.split(r"(?=<form|<div|<table|<script)", codigo, flags=re.IGNORECASE)
        elif linguagem == "javascript":
            blocos = re.split(r"\n(?=function\s|\$\(document|\w+\s?=\s?function)", codigo)
        elif linguagem == "java":
            blocos = re.split(r"\n(?=(public|private|protected)\s)", codigo)
        else:
            blocos = [codigo]
        return [b.strip() for b in blocos if b.strip()]

    def processar_todos(self):
        print("🔄 Forçando reprocessamento completo (sem duplicar)...")
        total = 0
        casos = list(self.casos.find({
            "codigoOriginal": {"$exists": True, "$ne": ""},
            "codigoCorrigido": {"$exists": True, "$ne": ""}
        }))
        for caso in casos:
            origem_id = str(caso["_id"])
            print(f"⚙️ Reprocessando caso _id={origem_id}...")
            self.processar_um_caso(caso)
            total += 1
        print(f"✅ Casos reprocessados: {total}")

    def processar_um_caso(self, caso):
        linguagem = caso.get("linguagem") or self.detectar_linguagem(caso["codigoOriginal"])
        blocos_antes = self.quebrar_blocos(caso["codigoOriginal"], linguagem)
        blocos_depois = self.quebrar_blocos(caso["codigoCorrigido"], linguagem)

        for i, blocoAntes in enumerate(blocos_antes):
            blocoDepois = blocos_depois[i] if i < len(blocos_depois) else ""
            hash_bloco = hashlib.md5((blocoAntes + blocoDepois).encode()).hexdigest()

            if not self.blocos.find_one({"hash": hash_bloco}):
                self.blocos.insert_one({
                    "origemId": str(caso["_id"]),
                    "tipo": caso["tipo"],
                    "linguagem": linguagem,
                    "nomeMetodo": f"bloco_{i+1}",
                    "blocoAntes": blocoAntes,
                    "blocoDepois": blocoDepois,
                    "hash": hash_bloco,
                    "criadoEm": datetime.utcnow()
                })
                print(f"📌 Inserido bloco {i+1} para caso {caso['_id']}, linguagem: {linguagem}")

    def processar_novos(self):
        print("🔎 Buscando casos sem blocos fragmentados...")
        ids_fragmentados = set(self.blocos.distinct("origemId"))
        casos = self.casos.find({
            "_id": {"$nin": [ObjectId(id_) for id_ in ids_fragmentados]},
            "codigoOriginal": {"$exists": True, "$ne": ""},
            "codigoCorrigido": {"$exists": True, "$ne": ""}
        })

        total = 0
        for caso in casos:
            self.processar_um_caso(caso)
            total += 1

        print(f"✅ Casos novos processados: {total}")
