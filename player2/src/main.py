import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft

from src.core.graph import Graph
from src.core.user import User
from src.io.file_reader import carregar_usuarios_json, carregar_usuarios_dict
from src.services.recommendation_service import RecommendationService
from src.services.registration_service import RegistrationService
from src.ui.register_view import build_register_view
from src.ui.swipe_view import build_swipe_view
from src.ui.matches_view import build_matches_view
from src.ui import theme as T

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


def main(page: ft.Page) -> None:
    page.title         = "Player2"
    page.theme_mode    = ft.ThemeMode.DARK
    page.bgcolor       = T.BG
    page.padding       = 0
    page.window.width  = 430
    page.window.height = 820
    page.window.resizable = True
    page.fonts = {
        T.FONT_TITLE: "https://fonts.gstatic.com/s/rajdhani/v15/LDI2apCSOBg7S-QT7p4HM-e1ig.woff2",
        T.FONT_MONO:  "https://fonts.gstatic.com/s/spacemono/v13/i7dPIFZifjKcF5UAWdDRUEZ2RFq7AwU.woff2",
    }
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=T.ACCENT,
            secondary=T.ACCENT2,
            surface=T.SURFACE,
            on_surface=T.TEXT,
            on_primary=T.TEXT,
        ),
    )

    grafo = Graph()
    json_path = os.path.join(os.path.dirname(__file__), "usuarios.json")

    if os.path.exists(json_path):
        usuarios = carregar_usuarios_json(json_path)
    else:
        usuarios = carregar_usuarios_dict(DADOS_EXEMPLO)

    for u in usuarios:
        grafo.adicionar_usuario(u)
    grafo.construir_arestas()

    reg_service = RegistrationService(grafo, caminho_json=json_path if os.path.exists(json_path) else None)

    estado = {
        "usuario_atual": None,  
        "matches": [],          
    }


    def ir_para_swipe(novo_usuario: User) -> None:
        estado["usuario_atual"] = novo_usuario
        estado["matches"] = []
        page.go("/swipe")

    def ir_para_matches() -> None:
        page.go("/matches")

    def voltar_para_swipe() -> None:
        page.go("/swipe")

    def voltar_para_registro() -> None:
        estado["usuario_atual"] = None
        estado["matches"] = []
        page.go("/register")


    def route_change(e: ft.RouteChangeEvent) -> None:
        page.views.clear()
        route = page.route

        if route == "/swipe":
            usuario = estado["usuario_atual"]
            if usuario is None:
                page.go("/register")
                return

            def salvar_matches(lista: list) -> None:
                estado["matches"] = lista

            view = build_swipe_view(
                page=page,
                eu=usuario,
                grafo=grafo,
                on_ver_matches=ir_para_matches,
                on_voltar=voltar_para_registro,
                matches_sink=salvar_matches,
            )
            page.views.append(view)

        elif route == "/matches":
            usuario = estado["usuario_atual"]
            if usuario is None:
                page.go("/register")
                return
            view = build_matches_view(
                page=page,
                eu=usuario,
                matches=estado["matches"],
                grafo=grafo,
                on_voltar=voltar_para_swipe,
            )
            page.views.append(view)

        else:
            view = build_register_view(
                page=page,
                registration_service=reg_service,
                on_cadastro_ok=ir_para_swipe,
            )
            page.views.append(view)

        page.update()

    def view_pop(e: ft.ViewPopEvent) -> None:
        page.views.pop()
        top = page.views[-1] if page.views else None
        if top:
            page.go(top.route)
        else:
            page.go("/register")

    page.on_route_change = route_change
    page.on_view_pop     = view_pop
    page.go("/register")


if __name__ == "__main__":
    ft.app(target=main)