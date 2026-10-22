import json
import os

import pytest

from src.core.user import User
from src.io.user_store import (
    UserStore, carregar_usuarios_dict, carregar_usuarios_json, salvar_usuarios_json,
)


def test_ida_e_volta_preserva_curtidas(tmp_path):
    caminho = str(tmp_path / "usuarios.json")
    ana = User(1, "Ana", ["anime"], "oi", curtidas={2: False, 3: True})
    salvar_usuarios_json(caminho, [User(2, "Bia", ["rpg"]), ana])

    carregados = carregar_usuarios_json(caminho)
    assert [u.id for u in carregados] == [1, 2]                  # gravado em ordem de id
    assert carregados[0].curtidas == {2: False, 3: True}
    assert "curtidas" not in json.loads(open(caminho, encoding="utf-8").read())["usuarios"][1]


def test_formato_um_usuario_por_linha(tmp_path):
    caminho = str(tmp_path / "usuarios.json")
    salvar_usuarios_json(caminho, [User(1, "Ana"), User(2, "Bia")])
    linhas = open(caminho, encoding="utf-8").read().splitlines()
    assert len(linhas) == 6
    assert linhas[2].strip().startswith('{"id": 1')


def test_salvar_nao_deixa_temporarios(tmp_path):
    salvar_usuarios_json(str(tmp_path / "u.json"), [User(1, "Ana")])
    assert os.listdir(tmp_path) == ["u.json"]


@pytest.mark.parametrize("dados, mensagem", [
    ({}, "usuarios"),
    ({"usuarios": [{"nome": "Sem id"}]}, "ausente"),
    ({"usuarios": [{"id": "abc", "nome": "X"}]}, "ID inválido"),
    ({"usuarios": [{"id": 1, "nome": "  "}]}, "sem nome"),
    ({"usuarios": [{"id": 1, "nome": "A"}, {"id": 1, "nome": "B"}]}, "duplicados"),
    ({"usuarios": [{"id": 1, "nome": "A", "curtidas": [{"x": 1}]}]}, "Curtida inválida"),
])
def test_dados_invalidos_sao_rejeitados(dados, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        carregar_usuarios_dict(dados)


def test_json_corrompido_vira_value_error(tmp_path):
    caminho = tmp_path / "u.json"
    caminho.write_text("{ isso não é json", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON inválido"):
        carregar_usuarios_json(str(caminho))


def test_store_sem_arquivo_usa_dados_de_exemplo(tmp_path):
    store = UserStore(str(tmp_path / "nao_existe.json"))
    assert len(store.carregar()) == 10
    assert store.maior_id() == 0


def test_store_mescla_com_o_disco(tmp_path):
    caminho = str(tmp_path / "u.json")
    salvar_usuarios_json(caminho, [User(1, "Ana"), User(2, "Bia")])

    # outra sessão só conhece a Ana, mas atualiza ela e cria o Caio
    UserStore(caminho).salvar([User(1, "Ana", bio="nova bio"), User(3, "Caio")])

    por_id = {u.id: u for u in carregar_usuarios_json(caminho)}
    assert sorted(por_id) == [1, 2, 3]
    assert por_id[1].bio == "nova bio"
    assert UserStore(caminho).maior_id() == 3


def test_store_em_memoria_nao_grava(tmp_path):
    UserStore(None).salvar([User(1, "Ana")])
    assert os.listdir(tmp_path) == []
