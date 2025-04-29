# preparar_dataset.py
import os
import json
import random
from pymongo import MongoClient
from difflib import SequenceMatcher

# Mapeamento manual dos tipos
mapeamento_tipos = {
    "Cross-Site Request Forgery": "Cross-Site Request Forgery",
    "Cross-site request forgery": "Cross-Site Request Forgery",
    "Cross-Site Scripting (DOM)": "Cross-Site Scripting: DOM",
    "Cross-site scripting: dom": "Cross-Site Scripting: DOM",
    "cross-site scripting: dom": "Cross-Site Scripting: DOM",
    "SQL Injection": "SQL Injection",
}


def normalizar_tipo(tipo: str) -> str:
    """Normaliza o tipo de vulnerabilidade baseado no mapeamento."""
    tipo = tipo.strip() if isinstance(tipo, str) else ""
    return mapeamento_tipos.get(tipo, tipo)


def extrair_diferencas(origem: str, destino: str) -> str:
    """Extrai as diferenças entre duas versões de código."""
    matcher = SequenceMatcher(None, origem.splitlines(), destino.splitlines())
    linhas_modificadas = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            linhas_modificadas.extend(destino.splitlines()[j1:j2])
    return "\n".join(linhas_modificadas).strip()


def carregar_dados_do_mongo(
    uri="mongodb://localhost:27017/",
    db_name="corretor_db",
    collection_name="casosCorrigidos",
):
    """Carrega e prepara os dados do MongoDB."""
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    dados = []
    for doc in collection.find():
        entrada = doc.get("codigoOriginal", "").strip()
        saida = doc.get("codigoCorrigido", "").strip()
        tipo = doc.get("tipo", "").strip()

        if entrada and saida and tipo:
            tipo_normalizado = normalizar_tipo(tipo)
            refinado = extrair_diferencas(entrada, saida)
            dados.append(
                {
                    "input": f"Corrija este código vulnerável do tipo {tipo_normalizado}:\n{entrada}",
                    "output": refinado if refinado else saida,
                }
            )

    return dados


def extrair_diferencas_com_contexto(origem: str, destino: str) -> list:
    """Extrai diferenças com contexto onde foi aplicado."""
    matcher = SequenceMatcher(None, origem.splitlines(), destino.splitlines())
    origem_linhas = origem.splitlines()
    destino_linhas = destino.splitlines()

    modificacoes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            trecho_antigo = "\n".join(origem_linhas[i1:i2]).strip()
            trecho_novo = "\n".join(destino_linhas[j1:j2]).strip()

            # Tenta identificar contexto: buscar o <form> mais próximo acima
            contexto = ""
            if i1 > 0:
                for k in range(i1 - 1, -1, -1):
                    if "<form:form" in origem_linhas[k] or "<form" in origem_linhas[k]:
                        contexto = origem_linhas[k].strip()
                        break

            modificacoes.append(
                {
                    "contexto": contexto,
                    "codigoCorrigido": trecho_novo,
                }
            )

    return modificacoes


def salvar_datasets(dados, output_dir="dataset_codet5"):
    """Divide os dados em train/val/test e salva os arquivos."""
    os.makedirs(output_dir, exist_ok=True)
    random.shuffle(dados)

    n = len(dados)
    splits = {
        "train": dados[: int(0.8 * n)],
        "val": dados[int(0.8 * n) : int(0.9 * n)],
        "test": dados[int(0.9 * n) :],
    }

    for split_name, split_data in splits.items():
        with open(
            os.path.join(output_dir, f"{split_name}.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(split_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Dataset salvo em '{output_dir}' com {n} exemplos.")
    for k, v in splits.items():
        print(f"🔹 {k.capitalize()}: {len(v)} exemplos")


def mostrar_exemplo_por_tipo(
    dados, tipo_desejado="Cross-Site Request Forgery", output_dir="dataset_codet5"
):
    """Mostra e salva um exemplo de um tipo específico de vulnerabilidade para análise."""
    exemplos_filtrados = [
        exemplo
        for exemplo in dados
        if tipo_desejado.lower() in exemplo["input"].lower()
    ]

    if not exemplos_filtrados:
        print(f"\n⚠️ Nenhum exemplo encontrado para o tipo: {tipo_desejado}")
        return

    exemplo = random.choice(exemplos_filtrados)

    # Recupera o código original e corrigido
    input_linhas = exemplo["input"].split(":\n", 1)
    tipo = (
        input_linhas[0].replace("Corrija este código vulnerável do tipo ", "").strip()
    )
    codigo_original = input_linhas[1]
    codigo_corrigido = exemplo["output"]

    print("\n🔍 Exemplo Selecionado")
    print("📌 Tipo:", tipo)
    print("\n🔴 Código Original:\n", codigo_original)
    print("\n🟢 Código Corrigido ou Diferenças:\n", codigo_corrigido)

    # Salvar como JSON para facilitar inspeção manual
    caminho_exemplo = os.path.join(
        output_dir, f"exemplo_debug_{tipo_desejado.replace(' ', '_')}.json"
    )
    with open(caminho_exemplo, "w", encoding="utf-8") as f:
        json.dump(
            {
                "tipo": tipo,
                "codigoOriginal": codigo_original,
                "codigoCorrigidoOuDiferencas": codigo_corrigido,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n💾 Exemplo salvo em: {caminho_exemplo}")

    def mostrar_exemplo_por_tipo_com_contexto(
        dados, tipo_desejado="Cross-Site Request Forgery", output_dir="dataset_codet5"
    ):
        """Mostra e salva um exemplo de um tipo específico de vulnerabilidade, agora com contexto."""
        exemplos_filtrados = [
            exemplo
            for exemplo in dados
            if tipo_desejado.lower() in exemplo["input"].lower()
        ]

        if not exemplos_filtrados:
            print(f"\n⚠️ Nenhum exemplo encontrado para o tipo: {tipo_desejado}")
            return

        exemplo = random.choice(exemplos_filtrados)

        input_linhas = exemplo["input"].split(":\n", 1)
        tipo = (
            input_linhas[0]
            .replace("Corrija este código vulnerável do tipo ", "")
            .strip()
        )
        codigo_original = input_linhas[1]
        codigo_corrigido = exemplo["output"]

        # Agora extrai com contexto
        modificacoes = extrair_diferencas_com_contexto(
            codigo_original, codigo_corrigido
        )

        print("\n🔍 Exemplo Selecionado com Contexto")
        print("📌 Tipo:", tipo)
        for mod in modificacoes:
            print("\n🔸 Contexto Detectado:\n", mod["contexto"])
            print("🟢 Correção Aplicada:\n", mod["codigoCorrigido"])

        caminho_exemplo = os.path.join(
            output_dir,
            f"exemplo_debug_{tipo_desejado.replace(' ', '_')}_com_contexto.json",
        )
        with open(caminho_exemplo, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "tipo": tipo,
                    "modificacoes": modificacoes,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\n💾 Exemplo com contexto salvo em: {caminho_exemplo}")


if __name__ == "__main__":
    print("📦 Preparando dataset para treinamento do CodeT5...")

    dados = carregar_dados_do_mongo()
    salvar_datasets(dados)

    mostrar_exemplo_por_tipo(dados, tipo_desejado="Cross-Site Request Forgery")
