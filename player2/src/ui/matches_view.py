"""
Módulo: matches_view.py
Responsabilidade: Tela que exibe todos os usuários que o novo
                  usuário curtiu (matches), com detalhes de afinidade.
"""

import flet as ft
from typing import Callable, List, Tuple

from src.core.user import User
from src.core.graph import Graph
from src.ui import theme as T


def build_matches_view(
    page: ft.Page,
    eu: User,
    matches: List[Tuple[User, List[str], float]],
    grafo: Graph,
    on_voltar: Callable[[], None],
) -> ft.View:

    def _match_card(usuario: User, em_comum: List[str], custo: float) -> ft.Container:
        emoji = T.emoji_para(usuario.id)
        pct   = round((len(em_comum) / max(len(eu.interesses), len(usuario.interesses), 1)) * 100)

        tags = ft.Row(
            controls=[T.tag_chip(i, "#0d2e1a", T.LIKE_COLOR, "#86efac")
                      for i in em_comum],
            wrap=True,
            spacing=6,
            run_spacing=4,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    # Avatar
                    ft.Container(
                        content=ft.Text(emoji, size=30),
                        width=54, height=54,
                        border_radius=27,
                        bgcolor=T.SURFACE2,
                        border=ft.Border.all(2, T.LIKE_COLOR),
                        alignment=ft.Alignment(0, 0),
                    ),
                    # Info
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        usuario.nome,
                                        size=17, weight=ft.FontWeight.W_600,
                                        color=T.TEXT, font_family=T.FONT_TITLE,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            f"{len(em_comum)} em comum",
                                            size=10, color=T.NEON,
                                            font_family=T.FONT_MONO,
                                        ),
                                        bgcolor=ft.Colors.with_opacity(0.15, T.ACCENT),
                                        border=ft.Border.all(1, T.BORDER),
                                        border_radius=20,
                                        padding=ft.Padding(8, 3, 8, 3),
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.ProgressBar(
                                            value=pct / 100,
                                            bgcolor=T.SURFACE3,
                                            color=T.LIKE_COLOR,
                                            border_radius=2,
                                        ),
                                        height=4, expand=True,
                                    ),
                                    ft.Text(
                                        f"{pct}%", size=10,
                                        color=T.LIKE_COLOR, font_family=T.FONT_MONO,
                                    ),
                                ],
                                spacing=8,
                            ),
                            tags,
                            ft.Text(
                                f"Custo Dijkstra: {custo:.4f}",
                                size=10, color=T.GOLD_COLOR,
                                font_family=T.FONT_MONO,
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            bgcolor=T.SURFACE,
            border=ft.Border.all(1.5, T.BORDER),
            border_radius=T.RADIUS,
            padding=ft.Padding(14, 14, 14, 14),
        )

    # ── Estado vazio ─────────────────────────────────────────
    if not matches:
        corpo = ft.Column(
            controls=[
                ft.Container(height=40),
                ft.Text("💜", size=56, text_align=ft.TextAlign.CENTER),
                ft.Text(
                    "Nenhum match ainda",
                    size=20, color=T.TEXT, font_family=T.FONT_TITLE,
                    text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_600,
                ),
                ft.Text(
                    "Volte ao feed e dê likes nos perfis que você curtir.",
                    size=13, color=T.MUTED, text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        )
    else:
        cards = [_match_card(u, em, c) for (u, em, c) in matches]
        corpo = ft.Column(
            controls=cards,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )

    # ── Header ───────────────────────────────────────────────
    header = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW,
                icon_color=T.MUTED,
                tooltip="Voltar",
                on_click=lambda _: on_voltar(),
                icon_size=18,
            ),
            ft.Text(
                f"💜  Seus matches ({len(matches)})",
                size=20, weight=ft.FontWeight.W_700,
                color=T.TEXT, font_family=T.FONT_TITLE,
            ),
            ft.Container(width=36),  # espaçador
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.View(
        route="/matches",
        bgcolor=T.BG,
        padding=ft.Padding(20, 16, 20, 16),
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Column(
                controls=[
                    header,
                    ft.Container(height=8),
                    corpo,
                ],
                spacing=0,
                expand=True,
            )
        ],
    )