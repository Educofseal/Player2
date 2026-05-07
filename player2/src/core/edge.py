from dataclasses import dataclass


@dataclass
class Edge:

    usuario_id_a: int
    usuario_id_b: int
    interesses_em_comum: int
    peso: float

    @staticmethod
    def calcular_peso(interesses_em_comum: int) -> float:

        return round(1 / (1 + interesses_em_comum), 4)

    def __repr__(self) -> str:
        return (
            f"Edge({self.usuario_id_a} <-> {self.usuario_id_b} | "
            f"em_comum={self.interesses_em_comum}, peso={self.peso:.4f})"
        )
