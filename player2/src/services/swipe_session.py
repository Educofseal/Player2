from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from src.core.user import User
from src.services.recommendation_service import Recomendacao


CURTIR = "curtir"
PASSAR = "passar"


@dataclass
class Match:

    recomendacao:  Recomendacao
    super_like:    bool = False

    @property
    def usuario(self) -> User:
        return self.recomendacao.usuario


class SwipeSession:
    """Estado do feed de um usuário: fila de perfis, histórico para desfazer e matches.

    As curtidas ficam em `usuario.curtidas`; `salvar` é chamado sempre que elas mudam.
    Perfis já curtidos em sessões anteriores não voltam para a fila e aparecem como matches.
    """

    def __init__(
        self,
        usuario: User,
        recomendacoes: List[Recomendacao],
        salvar: Optional[Callable[[], None]] = None,
    ):
        self.usuario = usuario
        self._salvar = salvar or (lambda: None)

        por_id = {r.usuario.id: r for r in recomendacoes}
        self.matches: List[Match] = [
            Match(por_id[uid], super_like)
            for uid, super_like in usuario.curtidas.items()
            if uid in por_id
        ]
        self.fila: List[Recomendacao] = [
            r for r in recomendacoes if r.usuario.id not in usuario.curtidas
        ]
        self.indice = 0
        self._historico: List[Tuple[str, Recomendacao]] = []

    @property
    def atual(self) -> Optional[Recomendacao]:
        return self.fila[self.indice] if self.indice < len(self.fila) else None

    def proximos(self, quantidade: int) -> List[Recomendacao]:
        return self.fila[self.indice:self.indice + quantidade]

    @property
    def restantes(self) -> int:
        return len(self.fila) - self.indice

    @property
    def pulados(self) -> int:
        return sum(1 for r in self.fila[:self.indice] if r.usuario.id not in self.usuario.curtidas)

    @property
    def pode_desfazer(self) -> bool:
        return bool(self._historico)

    def curtir(self, super_like: bool = False) -> Optional[Match]:
        rec = self.atual
        if rec is None:
            return None

        self.usuario.curtidas[rec.usuario.id] = super_like
        try:
            self._salvar()
        except Exception:
            del self.usuario.curtidas[rec.usuario.id]
            raise

        match = Match(rec, super_like)
        self.matches.append(match)
        self._historico.append((CURTIR, rec))
        self.indice += 1
        return match

    def passar(self) -> Optional[Recomendacao]:
        rec = self.atual
        if rec is None:
            return None
        self._historico.append((PASSAR, rec))
        self.indice += 1
        return rec

    def desfazer(self) -> Optional[Tuple[str, Recomendacao]]:
        """Volta o último swipe. Retorna (ação, perfil) ou None se não houver o que desfazer."""
        if not self._historico:
            return None

        acao, rec = self._historico[-1]
        if acao == CURTIR:
            super_like = self.usuario.curtidas.pop(rec.usuario.id)
            try:
                self._salvar()
            except Exception:
                self.usuario.curtidas[rec.usuario.id] = super_like
                raise
            self.matches = [m for m in self.matches if m.usuario.id != rec.usuario.id]

        self._historico.pop()
        self.indice -= 1
        return acao, rec

    def rever_pulados(self) -> int:
        """Devolve ao fim da fila os perfis que você passou. Retorna quantos voltaram."""
        vistos, restantes = self.fila[:self.indice], self.fila[self.indice:]
        pulados = [r for r in vistos if r.usuario.id not in self.usuario.curtidas]
        self.fila = restantes + pulados
        self.indice = 0
        self._historico.clear()
        return len(pulados)

    def matches_ordenados(self) -> List[Match]:
        """Super likes primeiro; depois quem tem menor custo no grafo."""
        return sorted(self.matches, key=lambda m: (not m.super_like, m.recomendacao.custo))
