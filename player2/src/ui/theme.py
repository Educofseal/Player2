from typing import Callable, Optional

import flet as ft

BG           = "#0a0a0f"
SURFACE      = "#12121a"
SURFACE2     = "#1a1a26"
SURFACE3     = "#22223a"

ACCENT       = "#7c3aed"
ACCENT2      = "#a855f7"
ACCENT_DARK  = "#5b21b6"
NEON         = "#c084fc"

LIKE_COLOR   = "#22c55e"
LIKE_BG      = "#0d2e1a"
LIKE_TEXT    = "#86efac"
NOPE_COLOR   = "#ef4444"
GOLD_COLOR   = "#f59e0b"
INFO_COLOR   = "#60a5fa"
CHIP_BG      = "#1e1040"

TEXT         = "#f0eeff"
MUTED        = "#9ca3af"     # contraste AA sobre BG e SURFACE
BORDER       = "#2a1f4a"

FONT_TITLE   = "Rajdhani"
FONT_MONO    = "Space Mono"
FONT_BODY    = "Inter"
FONT_BODY_SEMI = "Inter SemiBold"

# arquivos em assets/fonts, empacotados para não depender de URL externa
FONTES = {
    FONT_TITLE:     "fonts/Rajdhani-Bold.ttf",
    FONT_MONO:      "fonts/SpaceMono-Regular.ttf",
    FONT_BODY:      "fonts/Inter-Regular.ttf",
    FONT_BODY_SEMI: "fonts/Inter-SemiBold.ttf",
}

RADIUS       = 16
RADIUS_LG    = 24
PADDING      = 20
GAP          = 12
LARGURA_MAX  = 460           # o layout é mobile-first; em telas largas fica centralizado

# os 10 primeiros mantêm o avatar que cada usuário da base já tinha
EMOJIS = [
    "🧙", "🦊", "🐉", "🌸", "💻", "🎵", "♟️", "🎬", "🔐", "✨",
    "🎨", "🚀", "🎧", "🛡️", "🪡", "🤖", "🌙", "🎲", "🦄", "🧩",
    "👾", "🐙", "🍄", "⚡",
]

GRADIENTES = [
    ("#7c3aed", "#c084fc"), ("#db2777", "#f472b6"), ("#0891b2", "#22d3ee"),
    ("#16a34a", "#4ade80"), ("#ea580c", "#fbbf24"), ("#4f46e5", "#818cf8"),
]


def aplicar_tema(page: ft.Page) -> None:
    page.title      = "Player2"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor    = BG
    page.padding    = 0
    page.fonts      = FONTES

    tema = ft.Theme(
        font_family=FONT_BODY,
        color_scheme=ft.ColorScheme(
            primary=ACCENT,
            secondary=ACCENT2,
            surface=SURFACE,
            on_surface=TEXT,
            on_primary=TEXT,
            error=NOPE_COLOR,
        ),
    )
    page.theme      = tema
    page.dark_theme = tema


def emoji_para(uid: int) -> str:
    return EMOJIS[(uid - 1) % len(EMOJIS)]


def avatar(uid: int, tamanho: int = 48, cor_borda: Optional[str] = None) -> ft.Container:
    inicio, fim = GRADIENTES[(uid - 1) % len(GRADIENTES)]
    return ft.Container(
        content=ft.Text(emoji_para(uid), size=tamanho * 0.5, text_align=ft.TextAlign.CENTER),
        width=tamanho,
        height=tamanho,
        border_radius=tamanho / 2,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[ft.Colors.with_opacity(0.55, inicio), ft.Colors.with_opacity(0.25, fim)],
        ),
        border=ft.Border.all(2, cor_borda or fim),
        alignment=ft.Alignment.CENTER,
    )


def logo(tamanho: int = 24) -> ft.Row:
    return ft.Row(
        controls=[
            ft.Text("PLAYER", size=tamanho, weight=ft.FontWeight.W_700,
                    color=NEON, font_family=FONT_TITLE),
            ft.Text("2", size=tamanho, weight=ft.FontWeight.W_700,
                    color=ACCENT2, font_family=FONT_TITLE),
        ],
        spacing=0,
    )


def titulo_tela(texto: str, tamanho: int = 28) -> ft.Text:
    return ft.Text(
        texto,
        size=tamanho,
        weight=ft.FontWeight.W_700,
        color=TEXT,
        font_family=FONT_TITLE,
    )


def texto_secundario(texto: str, tamanho: int = 13, **kwargs) -> ft.Text:
    return ft.Text(texto, size=tamanho, color=MUTED, **kwargs)


def rotulo(texto: str) -> ft.Text:
    return ft.Text(texto.upper(), size=10, color=MUTED, font_family=FONT_BODY_SEMI,
                   style=ft.TextStyle(letter_spacing=1.2))


def botao_primario(
    texto: str,
    on_click: Callable,
    icone: Optional[ft.IconData] = None,
    expand: bool = True,
    disabled: bool = False,
) -> ft.Button:
    return ft.Button(
        content=ft.Text(texto, size=16, font_family=FONT_TITLE, weight=ft.FontWeight.W_700),
        icon=icone,
        on_click=on_click,
        disabled=disabled,
        expand=expand,
        height=52,
        style=ft.ButtonStyle(
            bgcolor={ft.ControlState.DEFAULT:  ACCENT,
                     ft.ControlState.HOVERED:  ACCENT2,
                     ft.ControlState.PRESSED:  ACCENT_DARK,
                     ft.ControlState.DISABLED: SURFACE3},
            color={ft.ControlState.DEFAULT:  TEXT,
                   ft.ControlState.DISABLED: MUTED},
            icon_color={ft.ControlState.DEFAULT:  TEXT,
                        ft.ControlState.DISABLED: MUTED},
            shape=ft.RoundedRectangleBorder(radius=RADIUS),
            elevation=0,
        ),
    )


def botao_secundario(
    texto: str,
    on_click: Callable,
    icone: Optional[ft.IconData] = None,
    cor: str = NEON,
) -> ft.OutlinedButton:
    return ft.OutlinedButton(
        content=ft.Text(texto, size=14, font_family=FONT_BODY_SEMI),
        icon=icone,
        on_click=on_click,
        height=44,
        style=ft.ButtonStyle(
            color=cor,
            icon_color=cor,
            side=ft.BorderSide(1, BORDER),
            shape=ft.RoundedRectangleBorder(radius=RADIUS),
            overlay_color=ft.Colors.with_opacity(0.08, cor),
        ),
    )


def botao_texto(texto: str, on_click: Callable, cor: str = MUTED) -> ft.TextButton:
    return ft.TextButton(
        content=ft.Text(texto, size=13, color=cor),
        on_click=on_click,
        style=ft.ButtonStyle(overlay_color=ft.Colors.with_opacity(0.08, cor)),
    )


def tag_chip(texto: str, cor_bg: str = CHIP_BG, cor_borda: str = ACCENT,
             cor_texto: str = NEON) -> ft.Container:
    return ft.Container(
        content=ft.Text(texto, size=11, color=cor_texto,
                        font_family=FONT_MONO, weight=ft.FontWeight.W_400),
        bgcolor=cor_bg,
        border=ft.Border.all(1, cor_borda),
        border_radius=20,
        padding=ft.Padding(10, 4, 10, 4),
    )


def tag_em_comum(texto: str) -> ft.Container:
    return tag_chip(texto, LIKE_BG, LIKE_COLOR, LIKE_TEXT)


def selo(texto: str, cor: str, icone: Optional[ft.IconData] = None) -> ft.Container:
    """Etiqueta pequena e arredondada (grau de separação, super like...)."""
    controles = [ft.Text(texto, size=10, color=cor, font_family=FONT_MONO)]
    if icone:
        controles.insert(0, ft.Icon(icone, size=12, color=cor))
    return ft.Container(
        content=ft.Row(controles, spacing=4, tight=True),
        bgcolor=ft.Colors.with_opacity(0.12, cor),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.4, cor)),
        border_radius=20,
        padding=ft.Padding(8, 3, 8, 3),
    )


def barra_afinidade(pct: int, cor: str = ACCENT2) -> ft.ProgressBar:
    return ft.ProgressBar(
        value=pct / 100,
        bgcolor=SURFACE3,
        color=cor,
        bar_height=5,
        border_radius=3,
        expand=True,
    )


def cartao(content: ft.Control, padding: int = PADDING, **kwargs) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=SURFACE,
        border=ft.Border.all(1.5, BORDER),
        border_radius=RADIUS_LG,
        padding=padding,
        **kwargs,
    )


def divider() -> ft.Divider:
    return ft.Divider(height=1, color=BORDER)


def descrever_grau(grau: Optional[int]) -> str:
    return "fora da sua rede" if grau is None else f"{grau}º grau"


def cor_do_grau(grau: Optional[int]) -> str:
    if grau is None:
        return MUTED
    return LIKE_COLOR if grau == 1 else GOLD_COLOR if grau == 2 else INFO_COLOR


def coluna_central(content: ft.Control, expand: bool = True) -> ft.SafeArea:
    """Limita a largura e centraliza em janelas largas; a SafeArea evita o notch do iPhone."""
    return ft.SafeArea(
        content=ft.Container(content=content, width=LARGURA_MAX, expand=expand),
        expand=expand,
    )
