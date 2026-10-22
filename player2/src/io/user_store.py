import json
import os
import tempfile
import threading
from typing import Iterable, List, Optional

from src.core.user import User


# Usado quando o arquivo de dados ainda não existe; ele é criado no primeiro salvamento.
DADOS_EXEMPLO = {
    "usuarios": [
        {"id": 1,  "nome": "João",   "interesses": ["anime", "jogos", "mangá", "rpg"]},
        {"id": 2,  "nome": "Maria",  "interesses": ["jogos", "filmes", "anime", "cosplay"]},
        {"id": 3,  "nome": "Lucas",  "interesses": ["rpg", "mangá", "jogos", "board games"]},
        {"id": 4,  "nome": "Ana",    "interesses": ["cosplay", "anime", "filmes", "k-pop"]},
        {"id": 5,  "nome": "Pedro",  "interesses": ["programação", "jogos", "hacking", "rpg"]},
        {"id": 6,  "nome": "Julia",  "interesses": ["k-pop", "anime", "cosplay", "mangá"]},
        {"id": 7,  "nome": "Carlos", "interesses": ["board games", "rpg", "xadrez"]},
        {"id": 8,  "nome": "Bruna",  "interesses": ["filmes", "séries", "k-pop"]},
        {"id": 9,  "nome": "Rafael", "interesses": ["hacking", "programação", "jogos", "anime"]},
        {"id": 10, "nome": "Camila", "interesses": ["mangá", "anime", "cosplay", "filmes"]},
    ]
}

# Serializa as escritas: no modo web várias sessões rodam no mesmo processo.
_TRAVA_ESCRITA = threading.Lock()


def usuario_de_dict(item: dict) -> User:
    try:
        uid  = int(item["id"])
        nome = str(item["nome"])
    except KeyError as e:
        raise ValueError(f"Campo obrigatório ausente no usuário: {e}") from None
    except (TypeError, ValueError):
        raise ValueError(f"ID inválido no usuário: {item.get('id')!r}") from None

    if not nome.strip():
        raise ValueError(f"Usuário {uid} está sem nome.")

    curtidas = {}
    for curtida in item.get("curtidas", []):
        try:
            curtidas[int(curtida["id"])] = bool(curtida.get("super", False))
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"Curtida inválida no usuário {uid}: {curtida!r}") from None

    return User(
        id          = uid,
        nome        = nome,
        interesses  = [str(i) for i in item.get("interesses", [])],
        bio         = str(item.get("bio", "")),
        curtidas    = curtidas,
    )


def usuario_para_dict(usuario: User) -> dict:
    dados = {
        "id":          usuario.id,
        "nome":        usuario.nome,
        "interesses":  usuario.interesses,
        "bio":         usuario.bio,
    }
    if usuario.curtidas:
        dados["curtidas"] = [
            {"id": uid, "super": super_like} for uid, super_like in usuario.curtidas.items()
        ]
    return dados


def carregar_usuarios_dict(dados: dict) -> List[User]:

    if not isinstance(dados, dict) or "usuarios" not in dados:
        raise ValueError("JSON deve conter a chave 'usuarios'.")

    usuarios = [usuario_de_dict(item) for item in dados["usuarios"]]

    vistos, duplicados = set(), set()
    for u in usuarios:
        (duplicados if u.id in vistos else vistos).add(u.id)
    if duplicados:
        raise ValueError(f"IDs de usuário duplicados: {sorted(duplicados)}")

    return usuarios


def carregar_usuarios_json(caminho: str) -> List[User]:

    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    with open(caminho, "r", encoding="utf-8") as f:
        try:
            dados = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido em {caminho}: {e}") from None

    return carregar_usuarios_dict(dados)


def salvar_usuarios_json(caminho: str, usuarios: Iterable[User]) -> None:
    """Grava num arquivo temporário e troca de uma vez, para nunca deixar o JSON pela metade.

    Mantém o formato da base original: um usuário por linha.
    """
    linhas = ",\n".join(
        "        " + json.dumps(usuario_para_dict(u), ensure_ascii=False)
        for u in sorted(usuarios, key=lambda u: u.id)
    )
    texto = '{\n    "usuarios": [\n' + linhas + '\n    ]\n}\n'

    pasta = os.path.dirname(os.path.abspath(caminho))
    fd, temporario = tempfile.mkstemp(dir=pasta, prefix=".usuarios-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(texto)
        os.replace(temporario, caminho)
    except BaseException:
        if os.path.exists(temporario):
            os.remove(temporario)
        raise


class UserStore:
    """Base de usuários em JSON. Sem caminho, funciona só em memória."""

    def __init__(self, caminho: Optional[str]):
        self.caminho = caminho

    def carregar(self) -> List[User]:
        if self.caminho and os.path.exists(self.caminho):
            return carregar_usuarios_json(self.caminho)
        return carregar_usuarios_dict(DADOS_EXEMPLO)

    def maior_id(self) -> int:
        """Maior id gravado no disco (0 se não houver arquivo)."""
        if not self.caminho or not os.path.exists(self.caminho):
            return 0
        return max((u.id for u in carregar_usuarios_json(self.caminho)), default=0)

    def salvar(self, usuarios: Iterable[User]) -> None:
        """Mescla por id com o que já está no disco (a versão em memória vence) e grava."""
        if not self.caminho:
            return
        with _TRAVA_ESCRITA:
            por_id = {}
            if os.path.exists(self.caminho):
                por_id = {u.id: u for u in carregar_usuarios_json(self.caminho)}
            por_id.update({u.id: u for u in usuarios})
            salvar_usuarios_json(self.caminho, por_id.values())
