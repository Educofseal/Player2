
from typing import Dict, List, Optional, Set

from src.core.graph import Graph


def dfs(grafo: Graph, origem_id: int) -> Dict[int, Optional[int]]:
    """Árvore de busca em profundidade a partir da origem.

    Retorna o predecessor de cada nó alcançado, na ordem de visita. O predecessor é
    registrado quando o nó é visitado (e não quando é descoberto), senão a árvore
    resultante seria a de uma busca em largura.
    """

    visitados: Set[int] = set()
    predecessores: Dict[int, Optional[int]] = {}

    pilha = [(origem_id, None)]

    while pilha:
        uid_atual, pai = pilha.pop()

        if uid_atual in visitados:
            continue
        visitados.add(uid_atual)
        predecessores[uid_atual] = pai

        # empilha em ordem decrescente para visitar primeiro o menor id
        vizinhos = sorted(
            (v for v, _ in grafo.get_vizinhos(uid_atual) if v not in visitados),
            reverse=True,
        )
        pilha.extend((v, uid_atual) for v in vizinhos)

    return predecessores


def ordem_dfs(grafo: Graph, origem_id: int) -> List[int]:

    return list(dfs(grafo, origem_id))


def encontrar_componentes(grafo: Graph) -> List[List[int]]:

    visitados: Set[int] = set()
    componentes: List[List[int]] = []

    for uid in grafo.get_todos_ids():
        if uid not in visitados:
            componente = ordem_dfs(grafo, uid)
            visitados.update(componente)
            componentes.append(componente)

    return componentes
