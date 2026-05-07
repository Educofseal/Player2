
from typing import Dict, List, Tuple
from src.core.user import User
from src.core.edge import Edge


class Graph:

    def __init__(self):
        self._usuarios: Dict[int, User] = {}
        self._adjacencia: Dict[int, List[Tuple[int, float]]] = {}
        self._arestas: List[Edge] = []

    def adicionar_usuario(self, usuario: User) -> None:
        """Adiciona um usuário (nó) ao grafo."""
        self._usuarios[usuario.id] = usuario
        if usuario.id not in self._adjacencia:
            self._adjacencia[usuario.id] = []

    def construir_arestas(self) -> None:

        self._arestas.clear()
        for uid, adj in self._adjacencia.items():
            adj.clear()

        ids = list(self._usuarios.keys())

        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                u_a = self._usuarios[ids[i]]
                u_b = self._usuarios[ids[j]]

                em_comum = u_a.calcular_afinidade(u_b)
                if em_comum == 0:
                    continue

                peso = Edge.calcular_peso(em_comum)
                aresta = Edge(u_a.id, u_b.id, em_comum, peso)
                self._arestas.append(aresta)

                self._adjacencia[u_a.id].append((u_b.id, peso))
                self._adjacencia[u_b.id].append((u_a.id, peso))

    def get_usuario(self, uid: int) -> User:
        return self._usuarios[uid]

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
