import pytest

from src.core.graph import Graph
from src.core.user import User


def montar_grafo(*usuarios: User) -> Graph:
    grafo = Graph()
    for u in usuarios:
        grafo.adicionar_usuario(u)
    grafo.construir_arestas()
    return grafo


@pytest.fixture
def grafo_exemplo() -> Graph:
    """
    1 —— 2 —— 3      4 —— 5      6 (isolado)

    1 e 2 dividem dois interesses; 2 e 3 dividem um; 1 e 3 nenhum.
    """
    return montar_grafo(
        User(1, "Ana",    ["anime", "rpg"]),
        User(2, "Bruno",  ["anime", "rpg", "xadrez"]),
        User(3, "Carla",  ["xadrez", "arte"]),
        User(4, "Davi",   ["k-pop", "música"]),
        User(5, "Elisa",  ["k-pop"]),
        User(6, "Fábio",  ["sci-fi"]),
    )
