
import heapq
from typing import Dict, List, Optional, Tuple

from src.core.graph import Graph


def dijkstra(grafo: Graph, origem_id: int) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:

    distancias: Dict[int, float] = {uid: float("inf") for uid in grafo.get_todos_ids()}
    distancias[origem_id] = 0.0

    predecessores: Dict[int, Optional[int]] = {uid: None for uid in grafo.get_todos_ids()}

    heap = [(0.0, origem_id)]

    visitados = set()

    while heap:
        custo_atual, uid_atual = heapq.heappop(heap)

        if uid_atual in visitados:
            continue
        visitados.add(uid_atual)

        for vizinho_id, peso in grafo.get_vizinhos(uid_atual):
            novo_custo = custo_atual + peso

            if novo_custo < distancias[vizinho_id]:
                distancias[vizinho_id] = novo_custo
                predecessores[vizinho_id] = uid_atual
                heapq.heappush(heap, (novo_custo, vizinho_id))

    return distancias, predecessores


def reconstruir_caminho(predecessores: Dict[int, Optional[int]], destino_id: int) -> List[int]:

    caminho = []
    atual = destino_id

    while atual is not None:
        caminho.append(atual)
        atual = predecessores[atual]

    caminho.reverse()

    return caminho
