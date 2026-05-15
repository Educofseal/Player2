import json
import os
from typing import List, Optional

from src.core.user import User
from src.core.graph import Graph


INTERESSES_DISPONIVEIS = [
    "anime", "jogos", "mangá", "rpg", "cosplay", "filmes",
    "k-pop", "board games", "programação", "hacking", "séries", "xadrez",
    "música", "quadrinhos", "fantasia", "sci-fi", "streaming", "arte",
]


class RegistrationService:

    def __init__(self, grafo: Graph, caminho_json: Optional[str] = None):
        self.grafo = grafo
        self.caminho_json = caminho_json 

    def proximo_id(self) -> int:
        ids = self.grafo.get_todos_ids()
        return max(ids) + 1 if ids else 1

    def validar(self, nome: str, interesses: List[str]) -> List[str]:
      
        erros = []
        if not nome or not nome.strip():
            erros.append("O nome não pode ser vazio.")
        elif len(nome.strip()) < 2:
            erros.append("O nome deve ter ao menos 2 caracteres.")
        elif len(nome.strip()) > 40:
            erros.append("O nome deve ter no máximo 40 caracteres.")

        nomes_existentes = [u.nome.lower() for u in self.grafo.get_todos_usuarios()]
        if nome.strip().lower() in nomes_existentes:
            erros.append(f"Já existe um usuário com o nome '{nome.strip()}'.")

        if len(interesses) < 1:
            erros.append("Selecione ao menos 1 interesse.")
        elif len(interesses) > 10:
            erros.append("Selecione no máximo 10 interesses.")

        return erros

    def cadastrar(self, nome: str, interesses: List[str]) -> User:

        erros = self.validar(nome, interesses)
        if erros:
            raise ValueError(" | ".join(erros))

        novo_id = self.proximo_id()
        novo_usuario = User(
            id=novo_id,
            nome=nome.strip(),
            interesses=[i.lower() for i in interesses],
        )

        self.grafo.adicionar_usuario(novo_usuario)
        self.grafo.construir_arestas() 

        if self.caminho_json:
            self._persistir(novo_usuario)

        return novo_usuario

    def _persistir(self, usuario: User) -> None:
        try:
            if os.path.exists(self.caminho_json):
                with open(self.caminho_json, "r", encoding="utf-8") as f:
                    dados = json.load(f)
            else:
                dados = {"usuarios": []}

            dados["usuarios"].append({
                "id": usuario.id,
                "nome": usuario.nome,
                "interesses": usuario.interesses,
            })

            with open(self.caminho_json, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
        except Exception:
            pass  
