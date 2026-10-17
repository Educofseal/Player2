import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, List, Optional

import flet as ft

from src.core.graph import Graph
from src.services.recommendation_service import Recomendacao
from src.services.swipe_session import CURTIR, Match, SwipeSession
from src.ui import theme as T


_DESLOCAMENTO_DECK  = 12      # quanto cada card de trás aparece abaixo do da frente
_LIMIAR_ARRASTO     = 0.28    # fração da largura do card que decide o swipe ao soltar
_LIMIAR_VELOCIDADE  = 900     # px/s: um "peteleco" rápido também conta
_SAIDA_MS           = 240

_ANIM_ARRASTO = ft.Animation(60, ft.AnimationCurve.LINEAR)
_ANIM_SOLTAR  = ft.Animation(260, ft.AnimationCurve.EASE_OUT_BACK)
_ANIM_SAIDA   = ft.Animation(_SAIDA_MS, ft.AnimationCurve.EASE_IN)
_ANIM_ENTRADA = ft.Animation(200, ft.AnimationCurve.EASE_OUT)


def _plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


def _limitar(valor: float) -> float:
    return max(0.0, min(1.0, valor))


def _caminho_dijkstra(rec: Recomendacao, grafo: Graph) -> ft.Control:
    if not rec.conectado:
        return T.texto_secundario(
            "Nenhum caminho de afinidade liga vocês dois no grafo.", 11, italic=True,
        )

    passos: List[ft.Control] = []
    for i, uid in enumerate(rec.caminho):
        if i:
            passos.append(ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, size=14, color=T.MUTED))
        ultimo = i == len(rec.caminho) - 1
        passos.append(ft.Text(
            "Você" if i == 0 else grafo.get_usuario(uid).nome,
            size=11, font_family=T.FONT_MONO,
            color=T.GOLD_COLOR if ultimo else T.TEXT,
        ))

    saltos = len(rec.caminho) - 1
    return ft.Column([
        ft.Row(passos, wrap=True, spacing=2, run_spacing=2,
               vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Text(f"custo {rec.custo:.4f} · {_plural(saltos, 'salto', 'saltos')}",
                size=10, color=T.MUTED, font_family=T.FONT_MONO),
    ], spacing=4)


def _legenda(cor: str, texto: str) -> ft.Row:
    return ft.Row([
        ft.Container(width=8, height=8, border_radius=4, bgcolor=cor),
        ft.Text(texto, size=10, color=T.MUTED),
    ], spacing=4, tight=True)


def _conteudo_card(rec: Recomendacao, grafo: Graph) -> ft.Column:
    u = rec.usuario

    tags = ft.Row(
        controls=[
            *[T.tag_em_comum(i) for i in rec.em_comum],
            *[T.tag_chip(i) for i in rec.exclusivos],
        ],
        wrap=True,
        spacing=6,
        run_spacing=6,
    )

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    T.avatar(u.id, 88),
                    ft.Column(
                        controls=[
                            ft.Text(u.nome, size=28, weight=ft.FontWeight.W_700,
                                    color=T.TEXT, font_family=T.FONT_TITLE,
                                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Row([
                                ft.Text(f"#{u.id:03d}", size=11, color=T.MUTED,
                                        font_family=T.FONT_MONO),
                                T.selo(T.descrever_grau(rec.grau), T.cor_do_grau(rec.grau),
                                       ft.Icons.HUB_ROUNDED),
                            ], spacing=8),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            *([ft.Text(u.bio, size=13, color=T.MUTED, italic=True)] if u.bio else []),
            ft.Column([
                ft.Row([
                    T.rotulo("Afinidade"),
                    ft.Text(f"{rec.afinidade_pct}%", size=12, color=T.NEON,
                            font_family=T.FONT_MONO),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([T.barra_afinidade(rec.afinidade_pct)]),
            ], spacing=6),
            T.divider(),
            ft.Row([
                T.rotulo("Interesses"),
                ft.Row([_legenda(T.LIKE_COLOR, "em comum"), _legenda(T.ACCENT2, "novos p/ você")],
                       spacing=10, tight=True),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            tags,
            T.divider(),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ROUTE_ROUNDED, size=14, color=T.MUTED),
                        T.rotulo("Caminho Dijkstra até você"),
                    ], spacing=6),
                    _caminho_dijkstra(rec, grafo),
                ], spacing=6),
                bgcolor=T.SURFACE2,
                border=ft.Border.all(1, T.BORDER),
                border_radius=12,
                padding=ft.Padding(12, 10, 12, 10),
            ),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
    )


def _superficie(conteudo: Optional[ft.Control] = None, **kwargs) -> ft.Container:
    return ft.Container(
        content=conteudo,
        bgcolor=T.SURFACE,
        border=ft.Border.all(1.5, T.BORDER),
        border_radius=T.RADIUS_LG,
        padding=T.PADDING,
        shadow=ft.BoxShadow(
            blur_radius=32,
            color=ft.Colors.with_opacity(0.5, "#000000"),
            offset=ft.Offset(0, 8),
        ),
        **kwargs,
    )


def _carimbo(texto: str, cor: str, angulo: float, opacity: float = 0, **posicao) -> ft.Container:
    return ft.Container(
        content=ft.Text(texto, size=26, weight=ft.FontWeight.W_700,
                        color=cor, font_family=T.FONT_TITLE),
        border=ft.Border.all(3, cor),
        border_radius=10,
        bgcolor=ft.Colors.with_opacity(0.92, T.SURFACE),   # fundo sólido: legível sobre o avatar
        padding=ft.Padding(12, 0, 12, 0),
        rotate=ft.Rotate(angulo),
        opacity=opacity,
        **posicao,
    )


@dataclass
class _CardTopo:
    """Controles do card da frente, mexidos durante o arrasto e as animações."""
    caixa:          ft.Container
    carimbo_curtir: ft.Container
    carimbo_passar: ft.Container
    carimbo_super:  ft.Container


def build_swipe_view(
    page: ft.Page,
    sessao: SwipeSession,
    grafo: Graph,
    on_ver_matches: Callable[[], None],
    on_sair: Callable[[], None],
    registrar_atalhos: Callable[[Callable[[ft.KeyboardEvent], Awaitable[None]]], None],
) -> ft.View:

    eu = sessao.usuario

    card: Optional[_CardTopo] = None
    arrasto_x = 0.0
    ocupado = False              # True enquanto um card está animando para fora
    dialogo_aberto = False

    deck = ft.Stack(expand=True, clip_behavior=ft.ClipBehavior.NONE)

    stat_matches  = ft.Text("0", size=18, color=T.NEON, font_family=T.FONT_MONO,
                            weight=ft.FontWeight.W_700)
    stat_fila     = ft.Text("0", size=18, color=T.NEON, font_family=T.FONT_MONO,
                            weight=ft.FontWeight.W_700)
    stat_afinidade = ft.Text("—", size=18, color=T.NEON, font_family=T.FONT_MONO,
                             weight=ft.FontWeight.W_700)

    def _largura_card() -> float:
        return max(min(page.width or 430, T.LARGURA_MAX) - 40, 200)

    # Deck

    def _fantasma(nivel: int) -> ft.Container:
        d = nivel * _DESLOCAMENTO_DECK
        return _superficie(
            left=d * 0.85, right=d * 0.85, top=d, bottom=2 * _DESLOCAMENTO_DECK - d,
            opacity=1 - 0.3 * nivel,
        )

    def _montar_topo(rec: Recomendacao, entrada: Optional[int], animar: bool) -> ft.GestureDetector:
        """`entrada` (-1/+1) faz o card surgir daquele lado; `animar` dá um leve zoom de entrada."""
        nonlocal card

        caixa = ft.Container(
            content=ft.Stack([
                _superficie(_conteudo_card(rec, grafo), left=0, top=0, right=0, bottom=0),
                carimbo_curtir := _carimbo("CURTIR", T.LIKE_COLOR, -0.25, top=28, left=24),
                carimbo_passar := _carimbo("PASSAR", T.NOPE_COLOR, 0.25, top=28, right=24),
                carimbo_super := ft.Container(
                    content=ft.Row([_carimbo("SUPER", T.GOLD_COLOR, 0, opacity=1)],
                                   alignment=ft.MainAxisAlignment.CENTER),
                    left=0, right=0, bottom=48, opacity=0,
                ),
            ]),
            offset=ft.Offset(1.4 * entrada, 0) if entrada else ft.Offset(0, 0),
            rotate=ft.Rotate(0.3 * entrada if entrada else 0, alignment=ft.Alignment.BOTTOM_CENTER),
            scale=0.96 if animar and not entrada else 1,
            animate_offset=_ANIM_SOLTAR,
            animate_rotation=_ANIM_SOLTAR,
            animate_scale=_ANIM_ENTRADA,
        )
        card = _CardTopo(caixa, carimbo_curtir, carimbo_passar, carimbo_super)

        return ft.GestureDetector(
            content=caixa,
            left=0, top=0, right=0, bottom=2 * _DESLOCAMENTO_DECK,
            mouse_cursor=ft.MouseCursor.GRAB,
            drag_interval=10,
            on_horizontal_drag_update=_arrastar,
            on_horizontal_drag_end=_soltar,
        )

    def _estado_vazio() -> ft.Container:
        pulados = sessao.pulados
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("🎲", size=56),
                    T.titulo_tela("Você viu todo mundo!", 24),
                    T.texto_secundario(
                        f"{_plural(len(sessao.matches), 'match', 'matches')} até agora.",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Row([T.botao_primario("Ver meus matches", lambda: on_ver_matches(),
                                             icone=ft.Icons.FAVORITE_ROUNDED)]),
                    *([T.botao_secundario(
                        f"Rever {_plural(pulados, 'perfil pulado', 'perfis pulados')}",
                        _rever_pulados, icone=ft.Icons.REPLAY_ROUNDED,
                    )] if pulados else []),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                tight=True,
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding(24, 0, 24, 0),
            left=0, top=0, right=0, bottom=0,
        )

    def _montar_deck(entrada: Optional[int] = None, animar: bool = False) -> None:
        nonlocal card
        card = None
        proximos = sessao.proximos(3)
        if not proximos:
            deck.controls = [_estado_vazio()]
        else:
            fantasmas = [_fantasma(n) for n in range(len(proximos) - 1, 0, -1)]
            deck.controls = [*fantasmas, _montar_topo(proximos[0], entrada, animar)]
        _atualizar_stats()

    async def _renderizar(entrada: Optional[int] = None) -> None:
        """Remonta o deck. `entrada` (-1/+1) faz o card voltar deslizando daquele lado."""
        _montar_deck(entrada, animar=True)
        page.update()
        if card:
            await asyncio.sleep(0.03)
            card.caixa.offset = ft.Offset(0, 0)
            card.caixa.rotate = ft.Rotate(0, alignment=ft.Alignment.BOTTOM_CENTER)
            card.caixa.scale  = 1
            card.caixa.update()

    def _atualizar_stats() -> None:
        stat_matches.value   = str(len(sessao.matches))
        stat_fila.value      = str(sessao.restantes)
        stat_afinidade.value = f"{sessao.atual.afinidade_pct}%" if sessao.atual else "—"
        matches_btn.badge = (
            ft.Badge(label=str(len(sessao.matches)), bgcolor=T.ACCENT, text_color=T.TEXT)
            if sessao.matches else None
        )
        desfazer_btn.opacity = 1 if sessao.pode_desfazer else 0.4
        for botao in botoes_swipe:
            botao.opacity = 1 if sessao.atual else 0.4

    # Arrasto

    def _posicionar(fracao: float, animacao: ft.Animation) -> None:
        caixa = card.caixa
        caixa.animate_offset   = animacao
        caixa.animate_rotation = animacao
        caixa.offset = ft.Offset(fracao, 0)
        caixa.rotate = ft.Rotate(fracao * 0.35, alignment=ft.Alignment.BOTTOM_CENTER)
        card.carimbo_curtir.opacity = _limitar(fracao * 3)
        card.carimbo_passar.opacity = _limitar(-fracao * 3)
        caixa.update()

    def _arrastar(e: ft.DragUpdateEvent) -> None:
        nonlocal arrasto_x
        if ocupado or card is None:
            return
        delta = e.primary_delta if e.primary_delta is not None else e.local_delta.x
        arrasto_x += delta
        _posicionar(arrasto_x / _largura_card(), _ANIM_ARRASTO)

    async def _soltar(e: ft.DragEndEvent) -> None:
        nonlocal arrasto_x
        if ocupado or card is None:
            return
        fracao = arrasto_x / _largura_card()
        velocidade = e.primary_velocity or 0
        arrasto_x = 0
        if fracao > _LIMIAR_ARRASTO or velocidade > _LIMIAR_VELOCIDADE:
            await _curtir()
        elif fracao < -_LIMIAR_ARRASTO or velocidade < -_LIMIAR_VELOCIDADE:
            await _passar()
        else:
            _posicionar(0, _ANIM_SOLTAR)

    async def _animar_saida(direcao: str) -> None:
        caixa = card.caixa
        caixa.animate_offset   = _ANIM_SAIDA
        caixa.animate_rotation = _ANIM_SAIDA
        if direcao == "super":
            caixa.offset = ft.Offset(0, -1.3)
            card.carimbo_super.opacity = 1
        else:
            lado = 1 if direcao == "curtir" else -1
            caixa.offset = ft.Offset(1.5 * lado, 0.05)
            caixa.rotate = ft.Rotate(0.4 * lado, alignment=ft.Alignment.BOTTOM_CENTER)
            (card.carimbo_curtir if lado > 0 else card.carimbo_passar).opacity = 1
        caixa.update()
        await asyncio.sleep(_SAIDA_MS / 1000)

    # Ações

    async def _curtir(super_like: bool = False) -> None:
        nonlocal ocupado
        if ocupado or card is None:
            return
        ocupado = True
        match = None
        try:
            await _animar_saida("super" if super_like else "curtir")
            try:
                match = sessao.curtir(super_like)
            except OSError as erro:
                _avisar(f"Não foi possível salvar a curtida ({erro}).")
            await _renderizar()
        finally:
            ocupado = False
        if match:
            _mostrar_match(match)

    # O Flet passa o evento a handlers com parâmetro e não aguarda corrotinas devolvidas
    # por lambdas; por isso os botões usam estas versões sem argumentos.
    async def _curtir_normal() -> None:
        await _curtir()

    async def _super_like() -> None:
        await _curtir(super_like=True)

    async def _passar() -> None:
        nonlocal ocupado
        if ocupado or card is None:
            return
        ocupado = True
        try:
            await _animar_saida("passar")
            sessao.passar()
            await _renderizar()
        finally:
            ocupado = False

    async def _desfazer() -> None:
        nonlocal ocupado
        if ocupado:
            return
        try:
            resultado = sessao.desfazer()
        except OSError as erro:
            _avisar(f"Não foi possível desfazer ({erro}).")
            return
        if resultado is None:
            _avisar("Nada para desfazer.")
            return

        acao, rec = resultado
        ocupado = True
        try:
            await _renderizar(entrada=1 if acao == CURTIR else -1)
        finally:
            ocupado = False
        _avisar(f"{rec.usuario.nome} voltou para o topo da fila.")

    async def _rever_pulados() -> None:
        sessao.rever_pulados()
        await _renderizar()

    def _avisar(msg: str) -> None:
        page.show_dialog(ft.SnackBar(
            content=ft.Text(msg, color=T.TEXT),
            bgcolor=T.SURFACE2,
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=1800,
        ))

    def _mostrar_match(match: Match) -> None:
        nonlocal dialogo_aberto
        usuario    = match.usuario
        rec        = match.recomendacao
        # ícone em vez de emoji no título: emoji em fonte customizada pode virar "☐" sem fallback
        titulo     = "SUPER MATCH!" if match.super_like else "É UM MATCH!"
        icone      = ft.Icons.STAR_ROUNDED if match.super_like else ft.Icons.FAVORITE_ROUNDED
        cor_titulo = T.GOLD_COLOR if match.super_like else T.LIKE_COLOR

        def _fechou() -> None:
            nonlocal dialogo_aberto
            dialogo_aberto = False

        def _fechar() -> None:
            _fechou()
            page.pop_dialog()

        def _ver_matches() -> None:
            _fechar()
            on_ver_matches()

        dlg = ft.AlertDialog(
            bgcolor=T.SURFACE,
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_LG),
            title=ft.Row(
                [
                    ft.Icon(icone, color=cor_titulo, size=28),
                    ft.Text(titulo, size=28, color=cor_titulo,
                            font_family=T.FONT_TITLE, weight=ft.FontWeight.W_700),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            T.avatar(eu.id, 72),
                            ft.Icon(ft.Icons.FAVORITE_ROUNDED, color=cor_titulo, size=28),
                            T.avatar(usuario.id, 72, cor_borda=cor_titulo),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    T.texto_secundario(
                        f"Você e {usuario.nome} têm "
                        f"{_plural(len(rec.em_comum), 'interesse', 'interesses')} em comum.",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    *([ft.Row([T.tag_em_comum(i) for i in rec.em_comum], wrap=True,
                              spacing=6, run_spacing=6,
                              alignment=ft.MainAxisAlignment.CENTER)] if rec.em_comum else []),
                    ft.Container(
                        content=_caminho_dijkstra(rec, grafo),
                        bgcolor=T.SURFACE2,
                        border=ft.Border.all(1, T.BORDER),
                        border_radius=T.RADIUS,
                        padding=ft.Padding(12, 10, 12, 10),
                    ),
                ],
                spacing=12,
                tight=True,
                width=340,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            actions=[
                ft.Row([T.botao_primario("Continuar explorando", lambda: _fechar())]),
                ft.Row([T.botao_texto("Ver todos os matches", lambda: _ver_matches())],
                       alignment=ft.MainAxisAlignment.CENTER),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            on_dismiss=lambda: _fechou(),
        )
        dialogo_aberto = True
        page.show_dialog(dlg)

    async def _atalho(e: ft.KeyboardEvent) -> None:
        if dialogo_aberto:
            return
        tecla = e.key
        if tecla == "Arrow Right":
            await _curtir_normal()
        elif tecla == "Arrow Left":
            await _passar()
        elif tecla == "Arrow Up":
            await _super_like()
        elif tecla == "Backspace" or (tecla == "Z" and (e.ctrl or e.meta)):
            await _desfazer()

    registrar_atalhos(_atalho)

    # Layout

    def _stat_pill(label: str, valor: ft.Text) -> ft.Container:
        valor.text_align = ft.TextAlign.CENTER
        return ft.Container(
            content=ft.Column(
                controls=[valor, ft.Text(label, size=10, color=T.MUTED,
                                         text_align=ft.TextAlign.CENTER)],
                spacing=1,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=T.SURFACE2,
            border=ft.Border.all(1, T.BORDER),
            border_radius=30,
            padding=ft.Padding(16, 8, 16, 8),
            expand=True,
        )

    def _botao_acao(icone: ft.IconData, cor: str, handler, tamanho: int,
                    dica: str, preenchido: bool = False) -> ft.Container:
        return ft.Container(
            content=ft.Icon(icone, color=T.TEXT if preenchido else cor, size=tamanho * 0.45),
            width=tamanho, height=tamanho,
            border_radius=tamanho / 2,
            bgcolor=cor if preenchido else T.SURFACE2,
            border=ft.Border.all(2, T.ACCENT2 if preenchido else cor),
            alignment=ft.Alignment.CENTER,
            on_click=handler,
            ink=True,
            tooltip=dica,
            animate_opacity=150,
        )

    desfazer_btn = _botao_acao(ft.Icons.UNDO_ROUNDED, T.GOLD_COLOR, _desfazer, 46,
                               "Desfazer (Backspace)")
    botoes_swipe = [
        _botao_acao(ft.Icons.CLOSE_ROUNDED, T.NOPE_COLOR, _passar, 58, "Passar (←)"),
        _botao_acao(ft.Icons.FAVORITE_ROUNDED, T.ACCENT, _curtir_normal, 66, "Curtir (→)",
                    preenchido=True),
        _botao_acao(ft.Icons.STAR_ROUNDED, T.INFO_COLOR, _super_like, 46, "Super like (↑)"),
    ]
    action_row = ft.Row(
        controls=[desfazer_btn, *botoes_swipe],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=14,
    )

    em_celular = page.platform in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS)
    dica_teclado = ft.Text(
        "← passar   ↑ super   → curtir   ⌫ desfazer",
        size=10, color=T.MUTED, font_family=T.FONT_MONO,
        text_align=ft.TextAlign.CENTER, visible=not em_celular,
    )

    matches_btn = ft.IconButton(
        icon=ft.Icons.FAVORITE_ROUNDED,
        icon_color=T.NEON,
        tooltip="Ver matches",
        on_click=lambda: on_ver_matches(),
        icon_size=22,
    )
    menu = ft.PopupMenuButton(
        content=T.avatar(eu.id, 36),
        tooltip=f"{eu.nome} · menu",
        bgcolor=T.SURFACE2,
        items=[
            ft.PopupMenuItem(
                content=ft.Column([
                    ft.Text(eu.nome, size=14, color=T.TEXT, font_family=T.FONT_BODY_SEMI),
                    ft.Text(", ".join(eu.interesses), size=11, color=T.MUTED,
                            max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, width=200),
                ], spacing=2, tight=True),
                disabled=True,
            ),
            ft.PopupMenuItem(icon=ft.Icons.FAVORITE_ROUNDED, content=ft.Text("Meus matches"),
                             on_click=lambda: on_ver_matches()),
            ft.PopupMenuItem(icon=ft.Icons.LOGOUT_ROUNDED, content=ft.Text("Sair"),
                             on_click=lambda: on_sair()),
        ],
    )

    header = ft.Row(
        controls=[T.logo(26), ft.Row([matches_btn, menu], spacing=4)],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    stats_row = ft.Row(
        controls=[
            _stat_pill("Matches", stat_matches),
            _stat_pill("Na fila", stat_fila),
            _stat_pill("Afinidade", stat_afinidade),
        ],
        spacing=8,
    )

    _montar_deck()

    return ft.View(
        route="/swipe",
        bgcolor=T.BG,
        padding=ft.Padding(20, 16, 20, 12),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            T.coluna_central(ft.Column(
                controls=[
                    header,
                    stats_row,
                    ft.Container(content=deck, expand=True, padding=ft.Padding(0, 6, 0, 0)),
                    ft.Container(height=4),
                    action_row,
                    ft.Row([dica_teclado], alignment=ft.MainAxisAlignment.CENTER),
                ],
                spacing=10,
                expand=True,
            )),
        ],
    )
