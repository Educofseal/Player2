from dataclasses import dataclass, field
from typing import Dict, Iterable, List


def normalizar_interesses(interesses: Iterable[str]) -> List[str]:
    """Minúsculas, sem espaços nas pontas, sem vazios e sem repetição (mantém a ordem)."""
    vistos: Dict[str, None] = {}
    for item in interesses:
        valor = str(item).strip().lower()
        if valor:
            vistos.setdefault(valor, None)
    return list(vistos)


@dataclass
class User:

    id: int
    nome: str
    interesses: List[str] = field(default_factory=list)
    bio: str = ""
    # id do perfil curtido -> True se foi super like
    curtidas: Dict[int, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.nome       = self.nome.strip()
        self.bio        = self.bio.strip()
        self.interesses = normalizar_interesses(self.interesses)

    def interesses_em_comum(self, outro: "User") -> List[str]:
        deles = set(outro.interesses)
        return [i for i in self.interesses if i in deles]

    def interesses_exclusivos_de(self, outro: "User") -> List[str]:
        meus = set(self.interesses)
        return [i for i in outro.interesses if i not in meus]

    def calcular_afinidade(self, outro: "User") -> int:
        return len(self.interesses_em_comum(outro))

    def afinidade_percentual(self, outro: "User") -> int:
        total = max(len(self.interesses), len(outro.interesses), 1)
        return round(self.calcular_afinidade(outro) / total * 100)

    def __repr__(self) -> str:
        return f"User(id={self.id}, nome='{self.nome}')"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, User) and self.id == other.id
