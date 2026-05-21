
from typing import Dict, List, Optional, Set

from src.core.graph import Graph


def dfs(grafo: Graph, origem_id: int) -> Dict[int, Optional[int]]:

    visitados: Set[int] = set()
    predecessores: Dict[int, Optional[int]] = {origem_id: None}

    pilha = [origem_id]

    while pilha:
        uid_atual = pilha.pop()

        if uid_atual in visitados:
            continue
        visitados.add(uid_atual)

        for vizinho_id, _ in grafo.get_vizinhos(uid_atual):
            if vizinho_id not in visitados:
                pilha.append(vizinho_id)
                if vizinho_id not in predecessores:
                    predecessores[vizinho_id] = uid_atual

    return predecessores


def ordem_dfs(grafo: Graph, origem_id: int) -> List[int]:

    visitados: Set[int] = set()
    ordem: List[int] = []
    pilha = [origem_id]

    while pilha:
        uid_atual = pilha.pop()
        if uid_atual in visitados:
            continue
        visitados.add(uid_atual)
        ordem.append(uid_atual)

        vizinhos = sorted(
            [v for v, _ in grafo.get_vizinhos(uid_atual) if v not in visitados],
            reverse=True,
        )
        pilha.extend(vizinhos)

    return ordem


def encontrar_componentes(grafo: Graph) -> List[List[int]]:

    visitados: Set[int] = set()
    componentes: List[List[int]] = []

    for uid in grafo.get_todos_ids():
        if uid not in visitados:
            componente: List[int] = []
            pilha = [uid]

            while pilha:
                atual = pilha.pop()
                if atual in visitados:
                    continue
                visitados.add(atual)
                componente.append(atual)
                for vizinho_id, _ in grafo.get_vizinhos(atual):
                    if vizinho_id not in visitados:
                        pilha.append(vizinho_id)

            componentes.append(componente)

    return componentes
