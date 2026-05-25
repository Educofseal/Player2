"""
risk_service.py
---------------
Triagem silenciosa de segurança baseada no Short Dark Tetrad (SD4 — Paulhus et al., 2021).

As perguntas são apresentadas ao usuário como "Seu Estilo de Jogo" — uma curadoria
de preferências geek — sem revelar o propósito clínico. O score resultante é usado
apenas internamente pelo algoritmo de recomendação para evitar matches entre perfis
de alto risco e perfis mais vulneráveis/abertos.

Dimensões avaliadas (subclinical):
  • Maquiavelismo  — manipulação planejada para ganho próprio
  • Narcisismo      — senso de superioridade e merecimento
  • Psicopatia      — frieza emocional, falta de empatia
  • Sadismo         — prazer com o sofrimento ou humilhação alheia

Referência: Paulhus, D. L., Buckels, E. E., Trapnell, P. D., & Jones, D. N. (2021).
Screening for dark personalities: The Short Dark Tetrad (SD4).
European Journal of Psychological Assessment.
"""

from typing import Dict, List

# ── Banco de perguntas ──────────────────────────────────────────────────────
#
# Cada item tem:
#   id        → índice único (0–11)
#   dimensao  → qual dos 4 traços ele avalia
#   texto     → pergunta exibida ao usuário (linguagem geek/neutra)
#   opcoes    → lista de (texto_opcao, score_1_a_5)
#               score 1 = traço ausente / score 5 = traço muito presente
#
# A ordem das opções foi embaralhada propositalmente para que a opção
# de menor risco não seja sempre a primeira (reduz viés de resposta).

PERGUNTAS: List[dict] = [

    # ── Maquiavelismo ───────────────────────────────────────────────────────
    {
        "id": 0,
        "dimensao": "maquiavelismo",
        "texto": "Num servidor ou guild, quando quer entrar num grupo já formado, você...",
        "opcoes": [
            ("Identifico quem tem influência e me aproximo primeiro",       4),
            ("Espero ser convidado naturalmente",                           1),
            ("Articulo estrategicamente minha entrada no grupo",            5),
            ("Participo das atividades e me apresento ao pessoal",          2),
        ],
    },
    {
        "id": 1,
        "dimensao": "maquiavelismo",
        "texto": "Se souber de uma informação sobre outro usuário da comunidade, você...",
        "opcoes": [
            ("Só menciono se for relevante para o grupo todo",              2),
            ("Guardo para usar quando for mais conveniente pra mim",        5),
            ("Compartilho seletivamente com quem pode me beneficiar",       4),
            ("Não uso informação sobre outras pessoas dessa forma",          1),
        ],
    },
    {
        "id": 2,
        "dimensao": "maquiavelismo",
        "texto": "Em jogos de negociação ou troca (TCG, MMO, board game), sua abordagem é...",
        "opcoes": [
            ("Maximizar meu ganho — é o objetivo do jogo",                  5),
            ("Buscar acordos onde os dois saem ganhando",                   1),
            ("Identificar o que o outro quer mais e usar isso a meu favor", 4),
            ("Ser justo, mesmo que não seja o melhor negócio pra mim",      2),
        ],
    },

    # ── Narcisismo ──────────────────────────────────────────────────────────
    {
        "id": 3,
        "dimensao": "narcisismo",
        "texto": "Quando alguém questiona seu conhecimento sobre um tema geek que você domina...",
        "opcoes": [
            ("Explico meu raciocínio com calma e abertura",                 2),
            ("Ignoro ou rebato forte — só quem entende tanto pode me questionar", 5),
            ("Considero o ponto deles — podem saber algo que eu não sei",   1),
            ("Fico irritado — claramente não sabem com quem estão falando", 4),
        ],
    },
    {
        "id": 4,
        "dimensao": "narcisismo",
        "texto": "Num grupo de RPG ou jogo colaborativo, qual papel você naturalmente espera ter?",
        "opcoes": [
            ("Líder — tenho mais visão estratégica que a maioria",          5),
            ("O que o grupo precisar — me adapto bem",                      2),
            ("Qualquer um — o importante é jogarmos bem juntos",            1),
            ("Um papel central — sou um dos mais habilidosos do grupo",     4),
        ],
    },
    {
        "id": 5,
        "dimensao": "narcisismo",
        "texto": "Quando você posta algo bacana (build, cosplay, análise), espera...",
        "opcoes": [
            ("As pessoas curtam se gostarem — não fico esperando nada",     1),
            ("Ser tratado como referência no assunto pela comunidade",       5),
            ("Reconhecimento da galera mais próxima",                       2),
            ("Muito engajamento — o conteúdo merece atenção ampla",         4),
        ],
    },

    # ── Psicopatia ──────────────────────────────────────────────────────────
    {
        "id": 6,
        "dimensao": "psicopatia",
        "texto": "Um colega de grupo errou feio numa campanha de RPG e prejudicou a sessão. Você...",
        "opcoes": [
            ("Converso em particular depois, com calma e sem julgamento",   1),
            ("Aponto sem rodeios na hora — a pessoa precisa entender o impacto", 5),
            ("Falo na hora com jeito — erros acontecem e fazem parte",      2),
            ("Deixo bem claro na frente de todos que foi um erro grave",    4),
        ],
    },
    {
        "id": 7,
        "dimensao": "psicopatia",
        "texto": "Se perceber que alguém do servidor está passando por algo difícil...",
        "opcoes": [
            ("Provavelmente está exagerando para chamar atenção",           5),
            ("Ofereço apoio — faz parte de uma boa comunidade",             1),
            ("Não é meu problema — cada um cuida da própria vida",          4),
            ("Noto, mas só me envolvo se a pessoa me pedir diretamente",    2),
        ],
    },
    {
        "id": 8,
        "dimensao": "psicopatia",
        "texto": "Regras de convivência em comunidades online, você acha...",
        "opcoes": [
            ("Necessárias e importantes para o espaço funcionar bem",       1),
            ("Irrelevantes — cada um faz o que quer e quem não aguentar sai", 5),
            ("Chatas — limitam demais quem pensa diferente da maioria",     4),
            ("Úteis na maioria dos casos, mesmo que algumas sejam exageradas", 2),
        ],
    },

    # ── Sadismo ─────────────────────────────────────────────────────────────
    {
        "id": 9,
        "dimensao": "sadismo",
        "texto": "Ver um debate acalorado onde alguém é 'destruído' pelos argumentos adversários...",
        "opcoes": [
            ("Divertido — adoro acompanhar esse tipo de confronto",         5),
            ("Me deixa desconfortável — mesmo que o argumento seja ruim",   1),
            ("Neutro — faz parte de qualquer debate público",               2),
            ("Satisfatório quando a pessoa estava claramente errada e arrogante", 4),
        ],
    },
    {
        "id": 10,
        "dimensao": "sadismo",
        "texto": "Sobre trollar pessoas com opiniões 'erradas' na internet...",
        "opcoes": [
            ("É um passatempo legítimo — quem não sabe debater merece",     5),
            ("Não faço isso — prefiro conversar sério ou simplesmente ignorar", 1),
            ("É justo quando a pessoa claramente pede com suas opiniões",   4),
            ("Raramente, só quando é algo muito absurdo mesmo",             2),
        ],
    },
    {
        "id": 11,
        "dimensao": "sadismo",
        "texto": "Quando um rival ou alguém que te irritou passa por algo ruim...",
        "opcoes": [
            ("Sinto empatia — independente do que aconteceu entre nós",     1),
            ("Sinto satisfação real — é uma pequena justiça poética",       5),
            ("Uma parte de mim acha que foi um pouco merecido",             4),
            ("Fico neutro — já deixei isso para trás há muito tempo",       2),
        ],
    },
]


# ── Scoring ─────────────────────────────────────────────────────────────────

def calcular_score_risco(respostas: Dict[int, int]) -> Dict:
    """
    Calcula o perfil de risco a partir das respostas ao quiz.

    Parâmetros
    ----------
    respostas : dict {pergunta_id: score (1–5)}

    Retorna
    -------
    dict com:
        "dimensoes" → {"maquiavelismo": 0.0–1.0, "narcisismo": ..., ...}
        "geral"     → float 0.0–1.0  (média das 4 dimensões)
    """
    acumulado: Dict[str, List[int]] = {
        "maquiavelismo": [],
        "narcisismo":    [],
        "psicopatia":    [],
        "sadismo":       [],
    }

    for pergunta in PERGUNTAS:
        pid = pergunta["id"]
        if pid in respostas:
            acumulado[pergunta["dimensao"]].append(respostas[pid])

    scores_dim: Dict[str, float] = {}
    for dim, valores in acumulado.items():
        if valores:
            media = sum(valores) / len(valores)
            # Normaliza escala 1–5 para 0.0–1.0
            scores_dim[dim] = round((media - 1) / 4, 3)
        else:
            scores_dim[dim] = 0.25  # default conservador (neutro-baixo)

    geral = round(sum(scores_dim.values()) / len(scores_dim), 3)

    return {"dimensoes": scores_dim, "geral": geral}


def classificar_risco(score: float) -> str:
    """Rótulo interno para logs e debug. Nunca exibido ao usuário."""
    if score < 0.30:
        return "baixo"
    if score < 0.55:
        return "moderado"
    if score < 0.75:
        return "elevado"
    return "alto"
