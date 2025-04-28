# avaliador.py
import difflib
from typing import Optional


def calcular_similaridade(a: str, b: str) -> float:
    """Calcula similaridade entre duas strings usando difflib."""
    return difflib.SequenceMatcher(None, a.strip(), b.strip()).ratio()


# def avaliar_sugestao(
#     alvo: str,
#     correcao_esperada: Optional[str],
#     sugestao: str,
#     limite_correcao_esperada: float = 0.95,
#     limite_minima_alteracao: float = 0.99
# ) -> dict:
#     """
#     Avalia uma sugestão gerada pelo modelo com base em:
#     - Similaridade com o alvo original
#     - Similaridade com a correção esperada (se fornecida)
#     - Indicador se a sugestão foi modificada
#     - Indicador se a sugestão está correta (opcionalmente comparando com a esperada)
#     """
#     sim_com_alvo = calcular_similaridade(alvo, sugestao)
#     sim_com_esperado = calcular_similaridade(correcao_esperada, sugestao) if correcao_esperada else None
#     alterou_algo = sim_com_alvo < limite_minima_alteracao
#     correto_esperado = sim_com_esperado is not None and sim_com_esperado >= limite_correcao_esperada


#     return {
#         "similaridade_com_alvo": round(sim_com_alvo, 4),
#         "similaridade_com_esperado": round(sim_com_esperado, 4) if sim_com_esperado is not None else None,
#         "alterou_algo": alterou_algo,
#         "correto_esperado": correto_esperado if correcao_esperada else None
#     }
def avaliar_sugestao(
    alvo: str,
    correcao_esperada: Optional[str],
    sugestao: str,
    limite_correcao_esperada: float = 0.95,
    limite_minima_alteracao: float = 0.99,
    tipo: Optional[str] = None,
    mudanca_pequena: bool = False,
) -> dict:
    """
    Avalia uma sugestão gerada pelo modelo.

    Agora também detecta correções específicas obrigatórias para mudanças pequenas.
    """
    sim_com_alvo = calcular_similaridade(alvo, sugestao)
    sim_com_esperado = (
        calcular_similaridade(correcao_esperada, sugestao)
        if correcao_esperada
        else None
    )
    alterou_algo = sim_com_alvo < limite_minima_alteracao
    correto_esperado = (
        sim_com_esperado is not None and sim_com_esperado >= limite_correcao_esperada
    )

    # 🔥 Se for mudança pequena, validar a presença de padrões importantes
    if mudanca_pequena and tipo:
        padroes_criticos = {
            "Cross-Site Scripting (Dom)": ["DOMPurify.sanitize"],
            "SQL Injection": ["prepareStatement", "?"],
            "Csrf": ["csrf_token", "csrfmiddlewaretoken"],
        }
        requisitos = padroes_criticos.get(tipo.title(), [])

        if requisitos:
            encontrou_requisito = any(
                req.lower() in sugestao.lower() for req in requisitos
            )
            correto_esperado = correto_esperado and encontrou_requisito

    return {
        "similaridade_com_alvo": round(sim_com_alvo, 4),
        "similaridade_com_esperado": (
            round(sim_com_esperado, 4) if sim_com_esperado is not None else None
        ),
        "alterou_algo": alterou_algo,
        "correto_esperado": correto_esperado if correcao_esperada else None,
    }
