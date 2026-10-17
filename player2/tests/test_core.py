import pytest

from src.core.edge import Edge
from src.core.user import User, normalizar_interesses

from conftest import montar_grafo


def test_normaliza_interesses_sem_repetir_e_mantendo_ordem():
    assert normalizar_interesses([" Anime", "RPG", "anime", "", "  "]) == ["anime", "rpg"]


def test_user_normaliza_campos():
    u = User(1, "  Ana  ", ["Anime", "anime", "RPG"], "  oi  ")
    assert (u.nome, u.interesses, u.bio) == ("Ana", ["anime", "rpg"], "oi")


def test_afinidade_e_interesses():
    a = User(1, "Ana", ["anime", "rpg", "arte"])
    b = User(2, "Bia", ["rpg", "anime", "xadrez", "k-pop"])
    assert a.interesses_em_comum(b) == ["anime", "rpg"]
    assert a.interesses_exclusivos_de(b) == ["xadrez", "k-pop"]
    assert a.calcular_afinidade(b) == 2
    assert a.afinidade_percentual(b) == 50     # 2 de max(3, 4)


def test_afinidade_percentual_sem_interesses_nao_divide_por_zero():
    assert User(1, "A").afinidade_percentual(User(2, "B")) == 0


def test_users_iguais_pelo_id():
    assert User(1, "A") == User(1, "Outro nome")
    assert len({User(1, "A"), User(1, "B")}) == 1


def test_peso_da_aresta_cai_com_a_afinidade():
    assert Edge.calcular_peso(1) == 0.5
    assert Edge.calcular_peso(3) == 0.25
    assert Edge.calcular_peso(1) > Edge.calcular_peso(2)


def test_grafo_so_liga_quem_tem_interesse_em_comum(grafo_exemplo):
    assert grafo_exemplo.total_arestas() == 3     # 1-2, 2-3, 4-5
    assert dict(grafo_exemplo.get_vizinhos(2)) == {1: Edge.calcular_peso(2), 3: Edge.calcular_peso(1)}
    assert grafo_exemplo.get_vizinhos(6) == []


def test_conectar_usuario_equivale_a_reconstruir(grafo_exemplo):
    novo = User(7, "Gabi", ["anime", "k-pop"])

    grafo_exemplo.conectar_usuario(novo)
    incremental = sorted(grafo_exemplo.get_vizinhos(7))

    grafo_exemplo.construir_arestas()
    assert sorted(grafo_exemplo.get_vizinhos(7)) == incremental == [
        (1, 0.5), (2, 0.5), (4, 0.5), (5, 0.5),
    ]


def test_conectar_usuario_repetido_falha(grafo_exemplo):
    with pytest.raises(ValueError):
        grafo_exemplo.conectar_usuario(User(1, "Ana de novo", ["anime"]))


def test_buscar_por_nome_ignora_caixa_e_espacos(grafo_exemplo):
    assert grafo_exemplo.buscar_por_nome("  bRUno ").id == 2
    assert grafo_exemplo.buscar_por_nome("ninguém") is None


def test_get_usuario_inexistente_tem_mensagem_clara():
    with pytest.raises(KeyError, match="99"):
        montar_grafo().get_usuario(99)
