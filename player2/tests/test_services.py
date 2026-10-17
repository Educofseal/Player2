import pytest

from src.core.user import User
from src.io.user_store import UserStore, carregar_usuarios_json
from src.services.recommendation_service import RecommendationService
from src.services.registration_service import RegistrationService
from src.services.swipe_session import CURTIR, PASSAR, SwipeSession


INF = float("inf")


# Cadastro

@pytest.fixture
def cadastro(grafo_exemplo, tmp_path):
    return RegistrationService(grafo_exemplo, UserStore(str(tmp_path / "u.json")))


@pytest.mark.parametrize("nome, erro", [
    (None, "vazio"),
    ("   ", "vazio"),
    ("A", "ao menos 2"),
    ("x" * 41, "no máximo 40"),
    (" ana ", "Já existe"),
])
def test_validar_nome(cadastro, nome, erro):
    (mensagem,) = cadastro.validar_nome(nome)
    assert erro in mensagem


def test_validar_interesses(cadastro):
    assert cadastro.validar_interesses([]) == ["Selecione ao menos 1 interesse."]
    assert cadastro.validar_interesses(["anime", "Anime"]) == []        # repetido conta uma vez
    assert "desconhecido" in cadastro.validar_interesses(["anime", "culinária"])[0]
    todos = ["anime", "jogos", "mangá", "rpg", "cosplay", "filmes",
             "k-pop", "board games", "programação", "hacking", "séries"]
    assert "no máximo 10" in cadastro.validar_interesses(todos)[0]


def test_validar_bio(cadastro):
    assert cadastro.validar_bio(None) == []
    assert cadastro.validar_bio("x" * 161) == ["A bio deve ter no máximo 160 caracteres."]


def test_cadastrar_grava_e_conecta(cadastro, grafo_exemplo):
    novo = cadastro.cadastrar("  Gabi ", ["Anime", "k-pop"], "  oi ")

    assert (novo.id, novo.nome, novo.interesses, novo.bio) == (7, "Gabi", ["anime", "k-pop"], "oi")
    assert sorted(v for v, _ in grafo_exemplo.get_vizinhos(7)) == [1, 2, 4, 5]
    assert [u.id for u in carregar_usuarios_json(cadastro.store.caminho)] == [1, 2, 3, 4, 5, 6, 7]


def test_cadastrar_invalido_nao_altera_nada(cadastro, grafo_exemplo):
    with pytest.raises(ValueError, match="Já existe"):
        cadastro.cadastrar("Ana", ["anime"])
    assert grafo_exemplo.total_usuarios() == 6


def test_falha_ao_gravar_nao_deixa_usuario_no_grafo(grafo_exemplo):
    class DiscoQuebrado(UserStore):
        def salvar(self, usuarios):
            raise OSError("disco cheio")

    servico = RegistrationService(grafo_exemplo, DiscoQuebrado("x.json"))
    with pytest.raises(OSError):
        servico.cadastrar("Gabi", ["anime"])
    assert not grafo_exemplo.contem(7)


def test_proximo_id_considera_o_disco(cadastro, grafo_exemplo):
    cadastro.store.salvar([User(50, "De outra sessão")])
    assert cadastro.proximo_id() == 51


# Recomendação

def test_recomendar_ordena_por_custo_e_preenche_detalhes(grafo_exemplo):
    recs = RecommendationService(grafo_exemplo).recomendar(1)

    assert [r.usuario.id for r in recs] == [2, 3, 4, 5, 6]
    bruno, carla, davi = recs[0], recs[1], recs[2]

    assert bruno.caminho == [1, 2] and bruno.grau == 1
    assert bruno.em_comum == ["anime", "rpg"] and bruno.exclusivos == ["xadrez"]
    assert bruno.afinidade_pct == 67

    assert carla.caminho == [1, 2, 3] and carla.grau == 2 and carla.conectado
    assert davi.custo == INF and davi.caminho == [] and davi.grau is None and not davi.conectado


def test_recomendar_pode_excluir_ids(grafo_exemplo):
    recs = RecommendationService(grafo_exemplo).recomendar(1, excluir={2, 6})
    assert [r.usuario.id for r in recs] == [3, 4, 5]


def test_insights(grafo_exemplo):
    info = RecommendationService(grafo_exemplo).insights(1)
    assert info.total_usuarios == 6
    assert info.total_arestas == 3
    assert info.total_comunidades == 3
    assert info.tamanho_comunidade == 2
    assert info.por_grau == {1: 1, 2: 1}
    assert info.interesses_em_alta[:3] == [("anime", 2), ("rpg", 2), ("xadrez", 2)]


# Sessão de swipe

@pytest.fixture
def sessao(grafo_exemplo):
    eu = grafo_exemplo.get_usuario(1)
    salvamentos = []
    s = SwipeSession(eu, RecommendationService(grafo_exemplo).recomendar(1),
                     salvar=lambda: salvamentos.append(dict(eu.curtidas)))
    s.salvamentos = salvamentos
    return s


def test_curtir_passar_e_desfazer(sessao):
    assert sessao.atual.usuario.id == 2 and sessao.restantes == 5

    match = sessao.curtir(super_like=True)
    assert match.usuario.id == 2 and match.super_like
    assert sessao.usuario.curtidas == {2: True}
    assert sessao.salvamentos == [{2: True}]

    assert sessao.passar().usuario.id == 3
    assert sessao.atual.usuario.id == 4 and sessao.restantes == 3

    assert sessao.desfazer()[0] == PASSAR
    assert sessao.atual.usuario.id == 3

    assert sessao.desfazer()[0] == CURTIR
    assert sessao.matches == [] and sessao.usuario.curtidas == {}
    assert sessao.salvamentos[-1] == {}

    assert sessao.desfazer() is None and not sessao.pode_desfazer


def test_fim_da_fila(sessao):
    for _ in range(5):
        sessao.passar()
    assert sessao.atual is None and sessao.restantes == 0
    assert sessao.curtir() is None and sessao.passar() is None


def test_rever_pulados(sessao):
    sessao.passar()           # Bruno
    sessao.curtir()           # Carla
    sessao.passar()           # Davi

    assert sessao.pulados == 2
    assert sessao.rever_pulados() == 2
    assert [r.usuario.id for r in sessao.fila] == [5, 6, 2, 4]
    assert sessao.indice == 0 and not sessao.pode_desfazer


def test_curtidas_salvas_viram_matches_na_proxima_sessao(grafo_exemplo):
    eu = grafo_exemplo.get_usuario(1)
    eu.curtidas = {3: True, 2: False}
    s = SwipeSession(eu, RecommendationService(grafo_exemplo).recomendar(1))

    assert [r.usuario.id for r in s.fila] == [4, 5, 6]
    assert [m.usuario.id for m in s.matches_ordenados()] == [3, 2]   # super like primeiro


def test_falha_ao_salvar_curtida_desfaz_o_estado(grafo_exemplo):
    def quebrar():
        raise OSError("sem disco")

    eu = grafo_exemplo.get_usuario(1)
    s = SwipeSession(eu, RecommendationService(grafo_exemplo).recomendar(1), salvar=quebrar)
    with pytest.raises(OSError):
        s.curtir()
    assert eu.curtidas == {} and s.matches == [] and s.atual.usuario.id == 2
