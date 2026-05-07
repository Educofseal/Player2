
from typing import List, Tuple

from src.core.graph import Graph
from src.core.user import User
from src.algorithms.dijkstra import dijkstra, reconstruir_caminho
from src.algorithms.bfs import bfs, agrupar_por_nivel
from src.algorithms.dfs import ordem_dfs, encontrar_componentes


class RecommendationService:


    def __init__(self, grafo: Graph):
        self.grafo = grafo

    # Recomendações (Dijkstra)                                            

    def recomendar(self, origem_id: int) -> List[Tuple[User, float, List[int]]]:

        distancias, predecessores = dijkstra(self.grafo, origem_id)

        recomendacoes = []
        for uid, custo in distancias.items():
            if uid == origem_id:
                continue
            if custo == float("inf"):
                continue

            usuario = self.grafo.get_usuario(uid)
            caminho = reconstruir_caminho(predecessores, uid)
            recomendacoes.append((usuario, custo, caminho))

        recomendacoes.sort(key=lambda x: x[1])
        return recomendacoes

    #  BFS                                             

    def proximos_por_nivel(self, origem_id: int) -> dict:

        niveis = bfs(self.grafo, origem_id)
        grupos = agrupar_por_nivel(niveis)

        resultado = {}
        for nivel, ids in grupos.items():
            resultado[nivel] = [self.grafo.get_usuario(uid) for uid in ids]

        return resultado

    #  DFS                                        

    def explorar_dfs(self, origem_id: int) -> List[User]:

        ids = ordem_dfs(self.grafo, origem_id)
        return [self.grafo.get_usuario(uid) for uid in ids]

    def componentes_conectados(self) -> List[List[User]]:

        componentes = encontrar_componentes(self.grafo)
        return [
            [self.grafo.get_usuario(uid) for uid in comp]
            for comp in componentes
        ]

    def afinidade_entre(self, id_a: int, id_b: int) -> int:

        u_a = self.grafo.get_usuario(id_a)
        u_b = self.grafo.get_usuario(id_b)
        return u_a.calcular_afinidade(u_b)
