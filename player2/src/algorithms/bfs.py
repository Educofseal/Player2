
from collections import deque
from typing import Dict, List

from src.core.graph import Graph


def bfs(grafo: Graph, origem_id: int) -> Dict[int, int]:

    niveis: Dict[int, int] = {origem_id: 0}
    fila = deque([origem_id])

    while fila:
        uid_atual = fila.popleft()
        nivel_atual = niveis[uid_atual]

        for vizinho_id, _ in grafo.get_vizinhos(uid_atual):
            if vizinho_id not in niveis:
                niveis[vizinho_id] = nivel_atual + 1
                fila.append(vizinho_id)

    return niveis

def agrupar_por_nivel(niveis: Dict[int, int]) -> Dict[int, List[int]]:

    grupos: Dict[int, List[int]] = {}
    for uid, nivel in niveis.items():
        grupos.setdefault(nivel, []).append(uid)
    return grupos
