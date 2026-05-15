import flet as ft
from typing import Callable, List

from src.services.registration_service import RegistrationService, INTERESSES_DISPONIVEIS
from src.core.user import User
from src.ui import theme as T


def build_register_view(
    page: ft.Page,
    registration_service: RegistrationService,
    on_cadastro_ok: Callable[[User], None],
) -> ft.View:

    # ── Estado local ──────────────────────────────────────────
    interesses_selecionados: List[str] = []
    checkboxes: List[ft.Checkbox] = []

    # ── Refs ──────────────────────────────────────────────────
    nome_field    = ft.Ref[ft.TextField]()
    erro_text     = ft.Ref[ft.Text]()
    btn_cadastrar = ft.Ref[ft.ElevatedButton]()
    contador_ref  = ft.Ref[ft.Text]()

    # ── Handlers ──────────────────────────────────────────────
    def on_interesse_change(e: ft.ControlEvent) -> None:
        cb: ft.Checkbox = e.control
        interesse = cb.data
        if cb.value:
            if interesse not in interesses_selecionados:
                interesses_selecionados.append(interesse)
        else:
            if interesse in interesses_selecionados:
                interesses_selecionados.remove(interesse)

        contador_ref.current.value = f"{len(interesses_selecionados)} selecionado(s)"
        erro_text.current.value = ""
        page.update()

    def on_cadastrar(e: ft.ControlEvent) -> None:
        nome = nome_field.current.value or ""
        erros = registration_service.validar(nome, interesses_selecionados)

        if erros:
            erro_text.current.value = erros[0]
            page.update()
            return

        try:
            novo_usuario = registration_service.cadastrar(nome, interesses_selecionados)
            on_cadastro_ok(novo_usuario)
        except ValueError as ex:
            erro_text.current.value = str(ex)
            page.update()

    def on_nome_change(e: ft.ControlEvent) -> None:
        erro_text.current.value = ""
        page.update()

    # ── Grid de interesses ────────────────────────────────────
    grid_interesses = ft.GridView(
        expand=False,
        runs_count=3,
        max_extent=130,
        child_aspect_ratio=2.8,
        spacing=8,
        run_spacing=8,
    )

    for interesse in INTERESSES_DISPONIVEIS:
        cb = ft.Checkbox(
            label=interesse,
            data=interesse,
            value=False,
            on_change=on_interesse_change,
            fill_color={
                ft.ControlState.SELECTED: T.ACCENT,
                ft.ControlState.DEFAULT:  T.SURFACE3,
            },
            check_color=T.TEXT,
            label_style=ft.TextStyle(
                size=12,
                color=T.TEXT,
                font_family=T.FONT_MONO,
            ),
        )
        checkboxes.append(cb)
        grid_interesses.controls.append(cb)

    # ── Layout da view ────────────────────────────────────────
    content = ft.Column(
        controls=[

            # Cabeçalho
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "PLAYER", size=32, weight=ft.FontWeight.W_700,
                                    color=T.NEON, font_family=T.FONT_TITLE,
                                ),
                                ft.Text(
                                    "2", size=32, weight=ft.FontWeight.W_700,
                                    color=T.ACCENT2, font_family=T.FONT_TITLE,
                                ),
                            ],
                            spacing=0,
                        ),
                        ft.Text(
                            "Crie seu perfil geek",
                            size=13, color=T.MUTED,
                        ),
                    ],
                    spacing=2,
                ),
                padding=ft.Padding(0, 0, 0, 20),
            ),

            # Campo nome
            ft.Text("Seu nome", size=12, color=T.MUTED, weight=ft.FontWeight.W_500),
            ft.TextField(
                ref=nome_field,
                hint_text="Como você quer ser chamado?",
                hint_style=ft.TextStyle(color=T.MUTED, size=14),
                text_style=ft.TextStyle(color=T.TEXT, size=14),
                bgcolor=T.SURFACE2,
                border_color=T.BORDER,
                focused_border_color=T.ACCENT,
                border_radius=T.RADIUS,
                content_padding=ft.Padding(16, 14, 16, 14),
                on_change=on_nome_change,
                max_length=40,
                cursor_color=T.ACCENT2,
            ),

            ft.Container(height=4),

            # Seção interesses
            ft.Row(
                controls=[
                    ft.Text("Seus interesses", size=12, color=T.MUTED,
                            weight=ft.FontWeight.W_500),
                    ft.Text(
                        ref=contador_ref,
                        value="0 selecionado(s)",
                        size=11, color=T.ACCENT2,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),

            ft.Container(
                content=grid_interesses,
                bgcolor=T.SURFACE2,
                border=ft.Border.all(1, T.BORDER),
                border_radius=T.RADIUS,
                padding=T.PADDING,
                height=260,
            ),

            ft.Container(height=4),

            # Mensagem de erro
            ft.Text(
                ref=erro_text,
                value="",
                size=12,
                color=T.NOPE_COLOR,
                italic=True,
            ),

            # Botão cadastrar
            ft.ElevatedButton(
                ref=btn_cadastrar,
                content=ft.Text(
                    "Criar meu perfil  →",
                    size=15, weight=ft.FontWeight.W_600,
                    font_family=T.FONT_TITLE, color=T.TEXT,
                ),
                on_click=on_cadastrar,
                style=ft.ButtonStyle(
                    bgcolor={
                        ft.ControlState.DEFAULT:  T.ACCENT,
                        ft.ControlState.HOVERED:  T.ACCENT2,
                        ft.ControlState.PRESSED:  "#5b21b6",
                    },
                    color=T.TEXT,
                    shape=ft.RoundedRectangleBorder(radius=T.RADIUS),
                    padding=ft.Padding(0, 16, 0, 16),
                ),
                expand=True,
                height=52,
            ),

        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.View(
        route="/register",
        bgcolor=T.BG,
        padding=ft.Padding(24, 20, 24, 20),
        controls=[content],
        scroll=ft.ScrollMode.AUTO,
    )