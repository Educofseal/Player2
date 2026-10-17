from typing import Dict, List, Optional, Tuple
from src.core.user import User
from src.core.edge import Edge


class Graph:

    def __init__(self):
        self._usuarios:   Dict[int, User]                  = {}
        self._adjacencia: Dict[int, List[Tuple[int, float]]] = {}
        self._arestas:    List[Edge]                        = []

    def adicionar_usuario(self, usuario: User) -> None:
        self._usuarios[usuario.id] = usuario
        if usuario.id not in self._adjacencia:
            self._adjacencia[usuario.id] = []

    def conectar_usuario(self, usuario: User) -> None:
        """Adiciona um usuário novo criando só as arestas dele: O(n) em vez de reconstruir tudo."""
        if usuario.id in self._usuarios:
            raise ValueError(f"Usuário {usuario.id} já está no grafo.")
        outros = list(self._usuarios.values())
        self.adicionar_usuario(usuario)
        for outro in outros:
            self._ligar(outro, usuario)

    def construir_arestas(self) -> None:
        self._arestas.clear()
        for adj in self._adjacencia.values():
            adj.clear()

        usuarios = list(self._usuarios.values())
        for i, u_a in enumerate(usuarios):
            for u_b in usuarios[i + 1:]:
                self._ligar(u_a, u_b)

    def _ligar(self, u_a: User, u_b: User) -> None:
        em_comum = u_a.calcular_afinidade(u_b)
        if em_comum == 0:
            return

        peso_final = Edge.calcular_peso(em_comum)

        self._arestas.append(Edge(u_a.id, u_b.id, em_comum, peso_final))
        self._adjacencia[u_a.id].append((u_b.id, peso_final))
        self._adjacencia[u_b.id].append((u_a.id, peso_final))

    def contem(self, uid: int) -> bool:
        return uid in self._usuarios

    def get_usuario(self, uid: int) -> User:
        try:
            return self._usuarios[uid]
        except KeyError:
            raise KeyError(f"Usuário {uid} não está no grafo.") from None

    def buscar_por_nome(self, nome: str) -> Optional[User]:
        alvo = (nome or "").strip().lower()
        return next((u for u in self._usuarios.values() if u.nome.lower() == alvo), None)

    def get_todos_usuarios(self) -> List[User]:
        return list(self._usuarios.values())

    def get_vizinhos(self, uid: int) -> List[Tuple[int, float]]:
        return self._adjacencia.get(uid, [])

    def get_todos_ids(self) -> List[int]:
        return list(self._usuarios.keys())

    def get_arestas(self) -> List[Edge]:
        return self._arestas

    def total_usuarios(self) -> int:
        return len(self._usuarios)

    def total_arestas(self) -> int:
        return len(self._arestas)

    def __repr__(self) -> str:
        return (
            f"Graph(usuários={self.total_usuarios()}, "
            f"arestas={self.total_arestas()})"
        )
