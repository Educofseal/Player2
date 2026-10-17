import os
import sys
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

# Garante que `import src.*` funcione tanto com `python -m src.main` quanto com
# `flet run src/main.py` (a raiz do projeto é a pasta acima de src/).
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

import flet as ft

from src.core.graph import Graph
from src.core.user import User
from src.io.user_store import UserStore
from src.services.recommendation_service import RecommendationService
from src.services.registration_service import RegistrationService
from src.services.swipe_session import SwipeSession
from src.ui.register_view import build_register_view
from src.ui.swipe_view import build_swipe_view
from src.ui.matches_view import build_matches_view
from src.ui import theme as T

# PLAYER2_DATA permite usar outra base (útil para testes sem mexer na original)
CAMINHO_DADOS = os.environ.get("PLAYER2_DATA") or os.path.join(_RAIZ, "usuarios.json")
PASTA_ASSETS  = os.path.join(_RAIZ, "assets")


@dataclass
class EstadoApp:

    usuario:  Optional[User]          = None
    sessao:   Optional[SwipeSession]  = None
    atalhos:  Optional[Callable[[ft.KeyboardEvent], Awaitable[None]]] = None


def _tela_erro(page: ft.Page, mensagem: str) -> None:
    page.add(ft.SafeArea(ft.Container(
        content=ft.Column([
            T.logo(28),
            T.titulo_tela("Não foi possível abrir a base de usuários", 22),
            T.texto_secundario(mensagem, selectable=True),
            T.texto_secundario(f"Arquivo: {CAMINHO_DADOS}", 11, selectable=True),
        ], spacing=12),
        padding=24,
    )))


def main(page: ft.Page) -> None:
    T.aplicar_tema(page)
    page.window.width      = 430
    page.window.height     = 820
    page.window.min_width  = 360
    page.window.min_height = 640

    store = UserStore(CAMINHO_DADOS)
    try:
        usuarios = store.carregar()
    except (OSError, ValueError) as erro:
        _tela_erro(page, str(erro))
        return

    grafo = Graph()
    for u in usuarios:
        grafo.adicionar_usuario(u)
    grafo.construir_arestas()

    cadastro     = RegistrationService(grafo, store)
    recomendador = RecommendationService(grafo)
    estado       = EstadoApp()

    def salvar_curtidas() -> None:
        store.salvar(grafo.get_todos_usuarios())

    def navegar(rota: str) -> None:
        page.run_task(page.push_route, rota)

    def entrar(usuario: User) -> None:
        estado.usuario = usuario
        estado.sessao  = SwipeSession(usuario, recomendador.recomendar(usuario.id),
                                      salvar=salvar_curtidas)
        navegar("/swipe")

    def sair() -> None:
        estado.usuario = None
        estado.sessao  = None
        navegar("/register")

    def registrar_atalhos(handler: Callable[[ft.KeyboardEvent], Awaitable[None]]) -> None:
        estado.atalhos = handler

    def rotear() -> None:
        rota = page.route
        if rota in ("/swipe", "/matches") and estado.sessao is None:
            navegar("/register")
            return

        estado.atalhos = None
        page.views.clear()

        if rota == "/swipe":
            view = build_swipe_view(
                page=page,
                sessao=estado.sessao,
                grafo=grafo,
                on_ver_matches=lambda: navegar("/matches"),
                on_sair=sair,
                registrar_atalhos=registrar_atalhos,
            )
        elif rota == "/matches":
            view = build_matches_view(
                page=page,
                sessao=estado.sessao,
                insights=recomendador.insights(estado.usuario.id),
                grafo=grafo,
                on_voltar=lambda: navegar("/swipe"),
            )
        else:
            view = build_register_view(
                page=page,
                registration_service=cadastro,
                on_cadastro_ok=entrar,
                on_entrar=entrar,
            )

        page.views.append(view)
        page.update()

    async def teclado(e: ft.KeyboardEvent) -> None:
        if estado.atalhos:
            await estado.atalhos(e)

    def voltar_view() -> None:
        # botão "voltar" do sistema (Android / navegador)
        if page.route == "/matches":
            navegar("/swipe")

    page.on_route_change    = rotear
    page.on_view_pop        = voltar_view
    page.on_keyboard_event  = teclado
    rotear()


if __name__ == "__main__":
    ft.run(main, assets_dir=PASTA_ASSETS)
