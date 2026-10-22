from typing import List, Optional

from src.core.user import User, normalizar_interesses
from src.core.graph import Graph
from src.io.user_store import UserStore


INTERESSES_DISPONIVEIS = [
    "anime", "jogos", "mangá", "rpg", "cosplay", "filmes",
    "k-pop", "board games", "programação", "hacking", "séries", "xadrez",
    "música", "quadrinhos", "fantasia", "sci-fi", "streaming", "arte",
]

NOME_MIN        = 2
NOME_MAX        = 40
BIO_MAX         = 160
INTERESSES_MIN  = 1
INTERESSES_MAX  = 10


class RegistrationService:

    def __init__(self, grafo: Graph, store: Optional[UserStore] = None):
        self.grafo = grafo
        self.store = store or UserStore(None)

    def proximo_id(self) -> int:
        # olha também o disco: outra sessão (modo web) pode ter cadastrado alguém
        return max([*self.grafo.get_todos_ids(), self.store.maior_id()], default=0) + 1

    def buscar_por_nome(self, nome: str) -> Optional[User]:
        return self.grafo.buscar_por_nome(nome)

    def validar_nome(self, nome: Optional[str]) -> List[str]:
        nome = (nome or "").strip()
        if not nome:
            return ["O nome não pode ser vazio."]
        if len(nome) < NOME_MIN:
            return [f"O nome deve ter ao menos {NOME_MIN} caracteres."]
        if len(nome) > NOME_MAX:
            return [f"O nome deve ter no máximo {NOME_MAX} caracteres."]
        if self.buscar_por_nome(nome):
            return [f"Já existe um usuário com o nome '{nome}'."]
        return []

    def validar_bio(self, bio: Optional[str]) -> List[str]:
        if len((bio or "").strip()) > BIO_MAX:
            return [f"A bio deve ter no máximo {BIO_MAX} caracteres."]
        return []

    def validar_interesses(self, interesses: Optional[List[str]]) -> List[str]:
        escolhidos = normalizar_interesses(interesses or [])
        if len(escolhidos) < INTERESSES_MIN:
            return [f"Selecione ao menos {INTERESSES_MIN} interesse."]
        if len(escolhidos) > INTERESSES_MAX:
            return [f"Selecione no máximo {INTERESSES_MAX} interesses."]
        desconhecidos = [i for i in escolhidos if i not in INTERESSES_DISPONIVEIS]
        if desconhecidos:
            return [f"Interesse(s) desconhecido(s): {', '.join(desconhecidos)}."]
        return []

    def validar(self, nome: Optional[str], interesses: Optional[List[str]], bio: Optional[str] = "") -> List[str]:
        return [
            *self.validar_nome(nome),
            *self.validar_interesses(interesses),
            *self.validar_bio(bio),
        ]

    def cadastrar(
        self,
        nome: str,
        interesses: List[str],
        bio: str = "",
    ) -> User:

        erros = self.validar(nome, interesses, bio)
        if erros:
            raise ValueError(" | ".join(erros))

        novo_usuario = User(
            id          = self.proximo_id(),
            nome        = nome,
            interesses  = interesses,
            bio         = bio or "",
        )

        # grava antes de mexer no grafo: se o disco falhar, nada fica pela metade
        self.store.salvar([*self.grafo.get_todos_usuarios(), novo_usuario])
        self.grafo.conectar_usuario(novo_usuario)

        return novo_usuario
