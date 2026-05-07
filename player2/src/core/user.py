
from dataclasses import dataclass, field
from typing import List


@dataclass
class User:

    id: int
    nome: str
    interesses: List[str] = field(default_factory=list)

    def calcular_afinidade(self, outro: "User") -> int:

        conjunto_a = set(i.lower() for i in self.interesses)
        conjunto_b = set(i.lower() for i in outro.interesses)
        return len(conjunto_a & conjunto_b)

    def __repr__(self) -> str:
        return f"User(id={self.id}, nome='{self.nome}', interesses={self.interesses})"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, User) and self.id == other.id
