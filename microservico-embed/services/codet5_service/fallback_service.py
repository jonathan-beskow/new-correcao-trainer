import logging
import requests

logger = logging.getLogger("codet5_fallback")


def fallback_para_java(tipo, exemplo, correcao, alvo):
    try:
        payload = {
            "tipo": tipo,
            "exemplo": exemplo,
            "correcao": correcao,
            "codigo": alvo
        }
        resposta = requests.post("http://localhost:8080/corrigir/fallback", json=payload)
        if resposta.ok:
            return resposta.json().get("codigoCorrigido", "")
        else:
            logger.error(f"Erro no fallback Java: {resposta.status_code}")
    except Exception as e:
        logger.error(f"Erro na requisição fallback: {e}")
    return "Erro: fallback falhou."


def diferenca_percentual(a, b):
    if not a:
        return 1.0
    return abs(len(a) - len(b)) / len(a)