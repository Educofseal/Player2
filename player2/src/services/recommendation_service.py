
from collections import Counter
from dataclasses import dataclass
from typing import Collection, Dict, List, Optional, Tuple

from src.core.graph import Graph
from src.core.user import User
from src.algorithms.dijkstra import dijkstra, reconstruir_caminho
from src.algorithms.bfs import bfs, agrupar_por_nivel
from src.algorithms.dfs import ordem_dfs, encontrar_componentes


@dataclass
class Recomendacao:

    usuario:        User
    custo:          float           # menor custo no grafo (Dijkstra); inf = sem conexão
    caminho:        List[int]       # ids da origem até o usuário
    em_comum:       List[str]
    exclusivos:     List[str]       # interesses que só o outro tem
    afinidade_pct:  int
    grau:           Optional[int]   # grau de separação (BFS); None = sem conexão

    @property
    def conectado(self) -> bool:
        return self.custo != float("inf")


@dataclass
class InsightsGrafo:

    total_usuarios:      int
    total_arestas:       int
    total_comunidades:   int
    tamanho_comunidade:  int                     # outras pessoas alcançáveis a partir de você (DFS)
    por_grau:            Dict[int, int]          # grau de separação -> quantidade de pessoas (BFS)
    interesses_em_alta:  List[Tuple[str, int]]   # mais comuns na sua comunidade


class RecommendationService:


    def __init__(self, grafo: Graph):
        self.grafo = grafo

    # Recomendações (Dijkstra + BFS)

    def recomendar(self, origem_id: int, excluir: Collection[int] = ()) -> List[Recomendacao]:

        eu = self.grafo.get_usuario(origem_id)
        distancias, predecessores = dijkstra(self.grafo, origem_id)
        niveis = bfs(self.grafo, origem_id)

        conectados = []
        desconectados = []

        for uid, custo in distancias.items():
            if uid == origem_id or uid in excluir:
                continue
            outro = self.grafo.get_usuario(uid)
            conectado = custo != float("inf")
            rec = Recomendacao(
                usuario       = outro,
                custo         = custo,
                caminho       = reconstruir_caminho(predecessores, uid) if conectado else [],
                em_comum      = eu.interesses_em_comum(outro),
                exclusivos    = eu.interesses_exclusivos_de(outro),
                afinidade_pct = eu.afinidade_percentual(outro),
                grau          = niveis.get(uid),
            )
            (conectados if conectado else desconectados).append(rec)

        # empate no custo: mais afinidade primeiro, depois ordem alfabética
        conectados.sort(key=lambda r: (r.custo, -r.afinidade_pct, r.usuario.nome.lower()))
        desconectados.sort(key=lambda r: r.usuario.nome.lower())
        return conectados + desconectados

    def insights(self, origem_id: int) -> InsightsGrafo:

        comunidade = ordem_dfs(self.grafo, origem_id)
        niveis = bfs(self.grafo, origem_id)

        por_grau = Counter(nivel for uid, nivel in niveis.items() if uid != origem_id)
        interesses = Counter(
            interesse
            for uid in comunidade
            for interesse in self.grafo.get_usuario(uid).interesses
        )

        return InsightsGrafo(
            total_usuarios     = self.grafo.total_usuarios(),
            total_arestas      = self.grafo.total_arestas(),
            total_comunidades  = len(encontrar_componentes(self.grafo)),
            tamanho_comunidade = len(comunidade) - 1,
            por_grau           = dict(sorted(por_grau.items())),
            interesses_em_alta = interesses.most_common(5),
        )

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
