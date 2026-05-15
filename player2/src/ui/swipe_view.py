import flet as ft
from typing import Callable, List, Tuple, Optional

from src.core.user import User
from src.core.graph import Graph
from src.services.recommendation_service import RecommendationService
from src.ui import theme as T


# ── Helpers internos ──────────────────────────────────────────

def _afinidade_pct(usuario: User, outro: User) -> int:
    em_comum = usuario.calcular_afinidade(outro)
    total = max(len(usuario.interesses), len(outro.interesses), 1)
    return round((em_comum / total) * 100)


def _build_card(
    item_usuario: User,
    eu: User,
    custo: float,
    caminho_ids: List[int],
    grafo: Graph,
) -> ft.Container:

    em_comum    = [i for i in eu.interesses if i in item_usuario.interesses]
    so_dele     = [i for i in item_usuario.interesses if i not in eu.interesses]
    pct         = _afinidade_pct(eu, item_usuario)
    emoji       = T.emoji_para(item_usuario.id)

    # Tags interesses em comum (verde) e únicos dele (roxo)
    tags_row = ft.Row(
        controls=[
            *[T.tag_chip(i, "#0d2e1a", T.LIKE_COLOR, "#86efac") for i in em_comum],
            *[T.tag_chip(i) for i in so_dele],
        ],
        wrap=True,
        spacing=6,
        run_spacing=6,
    )

    # Caminho Dijkstra
    nos_caminho = [grafo.get_usuario(uid).nome for uid in caminho_ids]
    caminho_str = " → ".join(nos_caminho) if nos_caminho else "—"

    path_row = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("🗺  Caminho Dijkstra", size=10, color=T.MUTED,
                        weight=ft.FontWeight.W_600),
                ft.Text(caminho_str, size=11, color=T.GOLD_COLOR,
                        font_family=T.FONT_MONO, no_wrap=False),
                ft.Text(f"custo: {custo:.4f}", size=10, color=T.MUTED,
                        font_family=T.FONT_MONO),
            ],
            spacing=3,
        ),
        bgcolor=T.SURFACE2,
        border=ft.Border.all(1, T.BORDER),
        border_radius=10,
        padding=ft.Padding(12, 10, 12, 10),
    )

    # Barra de afinidade
    bar_fill = ft.Container(
        width=0,   # será animada pelo AnimatedSwitcher via expand
        height=4,
        bgcolor=T.ACCENT2,
        border_radius=2,
        expand=pct,  # usa expand como proporção
    )
    bar_bg = ft.Container(
        content=ft.Row(
            controls=[bar_fill],
            expand=True,
        ),
        height=4,
        bgcolor=T.SURFACE3,
        border_radius=2,
        expand=True,
    )

    # Avatar circular
    avatar = ft.Container(
        content=ft.Text(emoji, size=56, text_align=ft.TextAlign.CENTER),
        width=100,
        height=100,
        border_radius=50,
        bgcolor=T.SURFACE2,
        border=ft.Border.all(2, T.ACCENT),
        alignment=ft.Alignment(0, 0),
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                # Topo — avatar + nome
                ft.Row(
                    controls=[
                        avatar,
                        ft.Column(
                            controls=[
                                ft.Text(
                                    item_usuario.nome,
                                    size=26, weight=ft.FontWeight.W_700,
                                    color=T.TEXT, font_family=T.FONT_TITLE,
                                ),
                                ft.Text(
                                    f"#{str(item_usuario.id).zfill(3)}",
                                    size=11, color=T.MUTED,
                                    font_family=T.FONT_MONO,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text("Afinidade", size=11, color=T.MUTED),
                                        ft.Text(f"{pct}%", size=11, color=T.NEON,
                                                font_family=T.FONT_MONO),
                                    ],
                                    spacing=6,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=ft.ProgressBar(
                                                value=pct / 100,
                                                bgcolor=T.SURFACE3,
                                                color=T.ACCENT2,
                                                border_radius=2,
                                            ),
                                            height=4,
                                            expand=True,
                                        ),
                                    ],
                                    expand=True,
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                    ],
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),

                T.divider(),

                # Interesses
                ft.Text("Interesses", size=10, color=T.MUTED,
                        weight=ft.FontWeight.W_500),
                tags_row,

                T.divider(),

                # Dijkstra path
                path_row,
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor=T.SURFACE,
        border=ft.Border.all(1.5, T.BORDER),
        border_radius=T.RADIUS_LG,
        padding=T.PADDING,
        shadow=ft.BoxShadow(
            blur_radius=32,
            spread_radius=0,
            color=ft.Colors.with_opacity(0.5, "#000000"),
            offset=ft.Offset(0, 8),
        ),
        expand=True,
    )


# ── View principal ────────────────────────────────────────────

def build_swipe_view(
    page: ft.Page,
    eu: User,
    grafo: Graph,
    on_ver_matches: Callable[[], None],
    on_voltar: Callable[[], None],
    matches_sink: Optional[Callable[[list], None]] = None,
) -> ft.View:

    servico = RecommendationService(grafo)

    # Gera fila ordenada por Dijkstra
    recomendacoes: List[Tuple[User, float, List[int]]] = servico.recomendar(eu.id)

    # Estado
    fila        = list(recomendacoes)   # [(User, custo, caminho)]
    idx         = [0]                   # índice atual (mutável em closure)
    historico   = []                    # para undo
    matches     = []                    # (User, em_comum, custo)

    # Refs para atualização dinâmica
    card_area       = ft.Ref[ft.Column]()
    stats_matches   = ft.Ref[ft.Text]()
    stats_restantes = ft.Ref[ft.Text]()
    stats_compat    = ft.Ref[ft.Text]()
    snack_ref       = ft.Ref[ft.SnackBar]()

    # ── Helpers ───────────────────────────────────────────────

    def item_atual() -> Optional[Tuple]:
        if idx[0] < len(fila):
            return fila[idx[0]]
        return None

    def atualizar_stats():
        stats_matches.current.value   = str(len(matches))
        stats_restantes.current.value = str(len(fila) - idx[0])
        item = item_atual()
        if item:
            em = eu.calcular_afinidade(item[0])
            total = max(len(eu.interesses), len(item[0].interesses), 1)
            stats_compat.current.value = f"{round(em/total*100)}%"
        else:
            stats_compat.current.value = "—"

    def renderizar_cards():
        card_area.current.controls.clear()

        remaining = fila[idx[0]:]
        if not remaining:
            # Estado vazio
            card_area.current.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("🎲", size=56, text_align=ft.TextAlign.CENTER),
                            ft.Text("Acabou por aqui!", size=20,
                                    color=T.TEXT, font_family=T.FONT_TITLE,
                                    text_align=ft.TextAlign.CENTER,
                                    weight=ft.FontWeight.W_600),
                            ft.Text("Você viu todos os perfis disponíveis.",
                                    size=13, color=T.MUTED,
                                    text_align=ft.TextAlign.CENTER),
                            ft.ElevatedButton(
                                content=ft.Text("Ver meus matches", color=T.TEXT,
                                                font_family=T.FONT_TITLE, size=14,
                                                weight=ft.FontWeight.W_600),
                                on_click=lambda _: on_ver_matches(),
                                style=ft.ButtonStyle(
                                    bgcolor={ft.ControlState.DEFAULT: T.ACCENT},
                                    color=T.TEXT,
                                    shape=ft.RoundedRectangleBorder(radius=T.RADIUS),
                                ),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                )
            )
        else:
            # Mostra até 3 cards no stack (visual de profundidade)
            for i, (usuario, custo, caminho) in enumerate(remaining[:3]):
                card = _build_card(usuario, eu, custo, caminho, grafo)
                # Cards de trás ficam levemente menores
                scale = 1.0 - (i * 0.03)
                offset_y = i * 10
                card_area.current.controls.append(
                    ft.Container(
                        content=card,
                        margin=ft.Margin(0, offset_y, 0, 0),
                        scale=ft.Scale(scale=scale),
                        opacity=1.0 - (i * 0.15),
                    )
                )

        atualizar_stats()
        page.update()

    # ── Ações de swipe ────────────────────────────────────────

    def acao_like(e=None, super_like=False):
        item = item_atual()
        if not item:
            return
        usuario, custo, caminho = item
        em_comum = [i for i in eu.interesses if i in usuario.interesses]
        historico.append(("like", item))
        matches.append((usuario, em_comum, custo))
        idx[0] += 1
        if matches_sink:
            matches_sink(list(matches))  # sincroniza com estado global
        renderizar_cards()
        _mostrar_match(usuario, em_comum, custo, super_like)

    def acao_pass(e=None):
        item = item_atual()
        if not item:
            return
        historico.append(("pass", item))
        idx[0] += 1
        renderizar_cards()

    def acao_undo(e=None):
        if not historico:
            snack_ref.current.content = ft.Text("Nada para desfazer.", color=T.TEXT)
            snack_ref.current.open = True
            page.update()
            return
        acao, item = historico.pop()
        if acao == "like":
            usuario = item[0]
            matches[:] = [m for m in matches if m[0].id != usuario.id]
        idx[0] -= 1
        renderizar_cards()

    def acao_super(e=None):
        acao_like(super_like=True)

    # ── Match dialog ──────────────────────────────────────────

    def _mostrar_match(usuario: User, em_comum: List[str], custo: float,
                       super_like: bool = False):
        emoji_eu   = T.emoji_para(eu.id)
        emoji_dele = T.emoji_para(usuario.id)
        titulo     = "⭐ SUPER MATCH!" if super_like else "💜 É UM MATCH!"
        cor_titulo = T.GOLD_COLOR if super_like else T.LIKE_COLOR

        tags_comuns = ft.Row(
            controls=[T.tag_chip(i, "#0d2e1a", T.LIKE_COLOR, "#86efac")
                      for i in em_comum],
            wrap=True,
            spacing=6,
        )

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=T.SURFACE,
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_LG),
            title=ft.Text(
                titulo, size=28, color=cor_titulo,
                font_family=T.FONT_TITLE, weight=ft.FontWeight.W_700,
                text_align=ft.TextAlign.CENTER,
            ),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(emoji_eu, size=44),
                                width=70, height=70, border_radius=35,
                                bgcolor=T.SURFACE2,
                                border=ft.Border.all(2, T.ACCENT),
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Text("💜", size=28),
                            ft.Container(
                                content=ft.Text(emoji_dele, size=44),
                                width=70, height=70, border_radius=35,
                                bgcolor=T.SURFACE2,
                                border=ft.Border.all(2, T.LIKE_COLOR),
                                alignment=ft.Alignment(0, 0),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    ft.Text(
                        f"Você e {usuario.nome} têm muito em comum!",
                        size=13, color=T.MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(f"{len(em_comum)} interesses em comum",
                                        size=13, color=T.NEON,
                                        font_family=T.FONT_MONO),
                                ft.Text(f"Custo Dijkstra: {custo:.4f}",
                                        size=11, color=T.GOLD_COLOR,
                                        font_family=T.FONT_MONO),
                                ft.Container(height=4),
                                tags_comuns,
                            ],
                            spacing=4,
                        ),
                        bgcolor=T.SURFACE2,
                        border=ft.Border.all(1, T.BORDER),
                        border_radius=T.RADIUS,
                        padding=ft.Padding(12, 12, 12, 12),
                    ),
                ],
                spacing=12,
                tight=True,
            ),
            actions=[
                ft.ElevatedButton(
                    content=ft.Text("Continuar explorando", color=T.TEXT,
                                    font_family=T.FONT_TITLE, size=14,
                                    weight=ft.FontWeight.W_600),
                    on_click=lambda _: _fechar_dlg(dlg),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: T.ACCENT},
                        color=T.TEXT,
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS),
                    ),
                    expand=True,
                ),
                ft.TextButton(
                    content=ft.Text("Ver todos os matches", color=T.MUTED, size=13),
                    on_click=lambda _: (_fechar_dlg(dlg), on_ver_matches()),
                    style=ft.ButtonStyle(color=T.MUTED),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def _fechar_dlg(dlg: ft.AlertDialog):
        dlg.open = False
        page.update()

    # ── Layout ────────────────────────────────────────────────

    # Barra de stats
    def _stat_pill(label: str, ref) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(ref=ref, value="—", size=18,
                            color=T.NEON, font_family=T.FONT_MONO,
                            weight=ft.FontWeight.W_700,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(label, size=10, color=T.MUTED,
                            text_align=ft.TextAlign.CENTER),
                ],
                spacing=1,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=T.SURFACE2,
            border=ft.Border.all(1, T.BORDER),
            border_radius=30,
            padding=ft.Padding(16, 8, 16, 8),
            expand=True,
        )

    stats_row = ft.Row(
        controls=[
            _stat_pill("Matches", stats_matches),
            _stat_pill("Restantes", stats_restantes),
            _stat_pill("Afinidade", stats_compat),
        ],
        spacing=8,
    )

    # Botões de ação
    def _action_btn(emoji: str, cor_bg: str, cor_borda: str,
                    handler, size=58, font_size=22) -> ft.Container:
        return ft.Container(
            content=ft.Text(emoji, size=font_size, text_align=ft.TextAlign.CENTER),
            width=size, height=size,
            border_radius=size // 2,
            bgcolor=cor_bg,
            border=ft.Border.all(2, cor_borda),
            alignment=ft.Alignment(0, 0),
            on_click=handler,
            ink=True,
        )

    action_row = ft.Row(
        controls=[
            _action_btn("↩", T.SURFACE2, T.GOLD_COLOR,  acao_undo,  size=46, font_size=18),
            _action_btn("✕", T.SURFACE2, T.NOPE_COLOR,  acao_pass,  size=58, font_size=22),
            _action_btn("💜", T.ACCENT,   T.ACCENT2,     acao_like,  size=66, font_size=24),
            _action_btn("⭐", T.SURFACE2, T.INFO_COLOR,  acao_super, size=46, font_size=18),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=14,
    )

    # Header
    header = ft.Row(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("PLAYER", size=26, weight=ft.FontWeight.W_700,
                            color=T.NEON, font_family=T.FONT_TITLE),
                    ft.Text("2", size=26, weight=ft.FontWeight.W_700,
                            color=T.ACCENT2, font_family=T.FONT_TITLE),
                ],
                spacing=0,
            ),
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(T.emoji_para(eu.id), size=16),
                        width=36, height=36, border_radius=18,
                        bgcolor=T.SURFACE2,
                        border=ft.Border.all(1.5, T.ACCENT),
                        alignment=ft.Alignment(0, 0),
                        tooltip=eu.nome,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.FAVORITE,
                        icon_color=T.NEON,
                        tooltip="Ver matches",
                        on_click=lambda _: on_ver_matches(),
                        icon_size=20,
                    ),
                ],
                spacing=4,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    snack = ft.SnackBar(
        ref=snack_ref,
        content=ft.Text("", color=T.TEXT),
        bgcolor=T.SURFACE2,
    )
    page.overlay.append(snack)

    view_content = ft.Column(
        controls=[
            header,
            ft.Container(height=4),
            stats_row,
            ft.Container(height=4),
            # Área de cards — Column empilhada (stack visual)
            ft.Container(
                content=ft.Column(
                    ref=card_area,
                    controls=[],
                    spacing=0,
                ),
                expand=True,
            ),
            action_row,
            ft.Container(height=4),
        ],
        spacing=8,
        expand=True,
    )

    # Renderiza os cards ao construir
    renderizar_cards()

    return ft.View(
        route="/swipe",
        bgcolor=T.BG,
        padding=ft.Padding(20, 16, 20, 16),
        controls=[view_content],
    )