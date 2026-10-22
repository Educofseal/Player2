import pytest

from src.algorithms.bfs import bfs, agrupar_por_nivel
from src.algorithms.dfs import dfs, ordem_dfs, encontrar_componentes
from src.algorithms.dijkstra import dijkstra, reconstruir_caminho
from src.core.edge import Edge
from src.core.user import User

from conftest import montar_grafo


INF = float("inf")


def test_dijkstra_custos_e_caminho(grafo_exemplo):
    dist, pred = dijkstra(grafo_exemplo, 1)

    assert dist[1] == 0
    assert dist[2] == Edge.calcular_peso(2)
    assert dist[3] == pytest.approx(Edge.calcular_peso(2) + Edge.calcular_peso(1))
    assert dist[4] == dist[6] == INF
    assert reconstruir_caminho(pred, 3) == [1, 2, 3]


def test_dijkstra_prefere_caminho_mais_barato_ao_direto():
    # 1-3 dividem só um interesse (peso 0.5); passando por 2 o custo é 0.2 + 0.2
    grafo = montar_grafo(
        User(1, "A", ["a", "b", "c", "d", "x"]),
        User(2, "B", ["a", "b", "c", "d", "e", "f", "g", "h"]),
        User(3, "C", ["e", "f", "g", "h", "x"]),
    )
    dist, pred = dijkstra(grafo, 1)
    assert dist[3] == pytest.approx(0.4)
    assert reconstruir_caminho(pred, 3) == [1, 2, 3]


def test_dijkstra_origem_inexistente(grafo_exemplo):
    with pytest.raises(KeyError):
        dijkstra(grafo_exemplo, 42)


def test_bfs_niveis(grafo_exemplo):
    assert bfs(grafo_exemplo, 1) == {1: 0, 2: 1, 3: 2}
    assert agrupar_por_nivel({1: 0, 2: 1, 3: 1}) == {0: [1], 1: [2, 3]}


def test_dfs_registra_predecessor_na_visita_e_nao_na_descoberta():
    # triângulo 1-2-3: a busca em profundidade vai 1 -> 2 -> 3, então o pai de 3 é 2
    grafo = montar_grafo(
        User(1, "A", ["x", "y"]),
        User(2, "B", ["x", "z"]),
        User(3, "C", ["y", "z"]),
    )
    assert dfs(grafo, 1) == {1: None, 2: 1, 3: 2}
    assert ordem_dfs(grafo, 1) == [1, 2, 3]


def test_dfs_e_ordem_sao_coerentes(grafo_exemplo):
    arvore = dfs(grafo_exemplo, 2)
    assert list(arvore) == ordem_dfs(grafo_exemplo, 2) == [2, 1, 3]
    assert arvore[2] is None


def test_componentes(grafo_exemplo):
    assert encontrar_componentes(grafo_exemplo) == [[1, 2, 3], [4, 5], [6]]
