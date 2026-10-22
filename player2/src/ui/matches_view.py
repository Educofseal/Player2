import flet as ft
from typing import Callable

from src.core.graph import Graph
from src.services.recommendation_service import InsightsGrafo
from src.services.swipe_session import Match, SwipeSession
from src.ui import theme as T


def _mini_stat(valor: int, titulo: str, legenda: str) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Text(str(valor), size=22, color=T.NEON, font_family=T.FONT_MONO,
                    weight=ft.FontWeight.W_700),
            ft.Text(titulo, size=12, color=T.TEXT, font_family=T.FONT_BODY_SEMI),
            ft.Text(legenda, size=10, color=T.MUTED, text_align=ft.TextAlign.CENTER),
        ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=T.SURFACE2,
        border=ft.Border.all(1, T.BORDER),
        border_radius=T.RADIUS,
        padding=ft.Padding(8, 10, 8, 10),
        expand=True,
    )


def _painel_rede(info: InsightsGrafo) -> ft.Container:
    diretos = info.por_grau.get(1, 0)
    indiretos = sum(n for grau, n in info.por_grau.items() if grau > 1)

    return T.cartao(ft.Column([
        ft.Row([
            ft.Icon(ft.Icons.HUB_ROUNDED, size=16, color=T.ACCENT2),
            T.rotulo("Sua rede no grafo"),
        ], spacing=6),
        ft.Row([
            _mini_stat(info.tamanho_comunidade, "Comunidade", "alcançáveis (DFS)"),
            _mini_stat(diretos, "1º grau", "conexões diretas (BFS)"),
            _mini_stat(indiretos, "2º grau +", "amigos de amigos (BFS)"),
        ], spacing=8, intrinsic_height=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH),
        *([
            T.rotulo("Em alta na sua comunidade"),
            ft.Row([T.tag_chip(f"{interesse} · {n}") for interesse, n in info.interesses_em_alta],
                   wrap=True, spacing=6, run_spacing=6),
        ] if info.interesses_em_alta else []),
        ft.Text(
            f"{info.total_usuarios} usuários · {info.total_arestas} arestas · "
            f"{info.total_comunidades} comunidade(s) no grafo",
            size=10, color=T.MUTED, font_family=T.FONT_MONO,
        ),
    ], spacing=10), padding=16)


def _caminho_texto(match: Match, grafo: Graph) -> str:
    rec = match.recomendacao
    if not rec.conectado:
        return "sem caminho no grafo"
    nomes = ["Você", *(grafo.get_usuario(uid).nome for uid in rec.caminho[1:])]
    return f"{' → '.join(nomes)}  ·  custo {rec.custo:.4f}"


def _match_card(match: Match, grafo: Graph) -> ft.Container:
    usuario = match.usuario
    rec     = match.recomendacao
    cor     = T.GOLD_COLOR if match.super_like else T.LIKE_COLOR

    nome_row = [
        ft.Text(usuario.nome, size=18, weight=ft.FontWeight.W_700,
                color=T.TEXT, font_family=T.FONT_TITLE),
        T.selo(T.descrever_grau(rec.grau), T.cor_do_grau(rec.grau)),
    ]
    if match.super_like:
        nome_row.append(T.selo("super", T.GOLD_COLOR, ft.Icons.STAR_ROUNDED))

    return T.cartao(
        ft.Row(
            controls=[
                T.avatar(usuario.id, 56, cor_borda=cor),
                ft.Column(
                    controls=[
                        ft.Row(nome_row, spacing=8, wrap=True, run_spacing=4),
                        *([ft.Text(usuario.bio, size=12, color=T.MUTED, italic=True)]
                          if usuario.bio else []),
                        ft.Row([
                            T.barra_afinidade(rec.afinidade_pct, cor=T.LIKE_COLOR),
                            ft.Text(f"{rec.afinidade_pct}%", size=11,
                                    color=T.LIKE_COLOR, font_family=T.FONT_MONO),
                        ], spacing=8),
                        ft.Row([T.tag_em_comum(i) for i in rec.em_comum],
                               wrap=True, spacing=6, run_spacing=4),
                        ft.Text(_caminho_texto(match, grafo), size=10,
                                color=T.GOLD_COLOR, font_family=T.FONT_MONO),
                    ],
                    spacing=6,
                    expand=True,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=14,
    )


def build_matches_view(
    page: ft.Page,
    sessao: SwipeSession,
    insights: InsightsGrafo,
    grafo: Graph,
    on_voltar: Callable[[], None],
) -> ft.View:

    matches = sessao.matches_ordenados()

    if not matches:
        corpo = ft.Column(
            controls=[
                ft.Container(height=24),
                ft.Text("💜", size=56),
                T.titulo_tela("Nenhum match ainda", 22),
                T.texto_secundario(
                    "Volte ao feed e curta os perfis que combinam com você.",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),
                T.botao_secundario("Voltar ao feed", lambda: on_voltar(),
                                   icone=ft.Icons.ARROW_BACK_ROUNDED),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    else:
        corpo = ft.Column([_match_card(m, grafo) for m in matches], spacing=10)

    header = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                icon_color=T.MUTED,
                tooltip="Voltar ao feed",
                on_click=lambda: on_voltar(),
                icon_size=20,
            ),
            T.titulo_tela("Seus matches", 22),
            ft.Container(expand=True),
            T.selo(str(len(matches)), T.NEON, ft.Icons.FAVORITE_ROUNDED),
        ],
        spacing=4,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.View(
        route="/matches",
        bgcolor=T.BG,
        padding=ft.Padding(20, 16, 20, 16),
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            T.coluna_central(ft.Column(
                controls=[
                    header,
                    _painel_rede(insights),
                    ft.Container(height=4),
                    corpo,
                ],
                spacing=12,
            ), expand=False),
        ],
    )
