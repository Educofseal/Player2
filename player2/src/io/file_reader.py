
import json
import os
from typing import List

from src.core.user import User


def carregar_usuarios_json(caminho: str) -> List[User]:

    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    if "usuarios" not in dados:
        raise ValueError("JSON deve conter a chave 'usuarios'.")

    usuarios = []
    for item in dados["usuarios"]:
        try:
            usuario = User(
                id=int(item["id"]),
                nome=str(item["nome"]),
                interesses=[str(i).lower() for i in item.get("interesses", [])],
            )
            usuarios.append(usuario)
        except KeyError as e:
            raise ValueError(f"Campo obrigatório ausente no usuário: {e}")

    return usuarios


def carregar_usuarios_dict(dados: dict) -> List[User]:

    usuarios = []
    for item in dados.get("usuarios", []):
        usuario = User(
            id=int(item["id"]),
            nome=str(item["nome"]),
            interesses=[str(i).lower() for i in item.get("interesses", [])],
        )
        usuarios.append(usuario)
    return usuarios
