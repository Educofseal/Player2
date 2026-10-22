import sys

import flet as ft
from typing import Callable, List

from src.services.registration_service import (
    BIO_MAX, INTERESSES_DISPONIVEIS, INTERESSES_MAX, INTERESSES_MIN, NOME_MAX,
    RegistrationService,
)
from src.core.user import User
from src.ui import theme as T

_TOTAL_PASSOS = 3

# Na demo web (flet publish) o Python roda no navegador e o disco é só da aba aberta.
_DEMO_NO_NAVEGADOR = sys.platform == "emscripten"


def build_register_view(
    page: ft.Page,
    registration_service: RegistrationService,
    on_cadastro_ok: Callable[[User], None],
    on_entrar: Callable[[User], None],
) -> ft.View:

    passo = 0
    nome_val = ""
    bio_val = ""
    interesses_selecionados: List[str] = []

    progresso_bar = ft.ProgressBar(value=1 / _TOTAL_PASSOS, color=T.ACCENT, bgcolor=T.SURFACE3,
                                   bar_height=4, border_radius=4)
    progresso_txt = ft.Text(f"1/{_TOTAL_PASSOS}", size=11, color=T.MUTED, font_family=T.FONT_MONO)
    erro_txt      = ft.Text()   # recriado a cada passo, logo abaixo do campo principal
    voltar_btn    = ft.IconButton(
        icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=T.MUTED, icon_size=20,
        tooltip="Voltar", visible=False, on_click=lambda: _ir_para(passo - 1),
    )
    conteudo = ft.AnimatedSwitcher(
        content=ft.Container(),
        duration=250,
        reverse_duration=150,
        transition=ft.AnimatedSwitcherTransition.FADE,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        expand=True,
    )

    def _erro(msg: str) -> None:
        erro_txt.value   = msg
        erro_txt.visible = True
        page.update()

    def _limpar_erro(atualizar: bool = True) -> None:
        if erro_txt.visible:
            erro_txt.visible = False
            if atualizar:
                page.update()

    def _ir_para(p: int, atualizar: bool = True) -> None:
        nonlocal passo
        passo = max(0, min(p, _TOTAL_PASSOS - 1))
        progresso_bar.value  = (passo + 1) / _TOTAL_PASSOS
        progresso_txt.value  = f"{passo + 1}/{_TOTAL_PASSOS}"
        voltar_btn.visible   = passo > 0
        conteudo.content     = _build_passo(passo)
        if atualizar:
            page.update()

    def _borda(largura: float, cor: str) -> ft.UnderlineInputBorder:
        return ft.UnderlineInputBorder(
            side=ft.BorderSide(largura, cor),
            border_radius=ft.BorderRadius(T.RADIUS, T.RADIUS, 0, 0),
        )

    def _campo(**kwargs) -> ft.TextField:
        return ft.TextField(
            bgcolor=T.SURFACE2,
            filled=True,
            border={
                ft.ControlState.DEFAULT: _borda(1, T.ACCENT),
                ft.ControlState.FOCUSED: _borda(2, T.ACCENT2),
            },
            cursor_color=T.ACCENT2,
            content_padding=ft.Padding(20, 18, 20, 18),
            counter_style=ft.TextStyle(color=T.MUTED, size=11),
            autofocus=True,
            on_change=lambda: _limpar_erro(),
            **kwargs,
        )

    def _layout_passo(titulo: str, subtitulo: ft.Control, principal: ft.Control,
                      *resto: ft.Control) -> ft.Container:
        nonlocal erro_txt
        erro_txt = ft.Text("", size=12, color=T.NOPE_COLOR, visible=False)
        return ft.Container(
            content=ft.Column(
                [T.titulo_tela(titulo), subtitulo, ft.Container(height=24),
                 principal, erro_txt, *resto],
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            alignment=ft.Alignment.TOP_CENTER,
        )

    def _passo_nome() -> ft.Container:
        entrar_box = ft.Container(visible=False, padding=ft.Padding(0, 4, 0, 0))

        def _next() -> None:
            nonlocal nome_val
            v = (campo.value or "").strip()

            existente = registration_service.buscar_por_nome(v)
            if existente:
                entrar_box.content = T.botao_secundario(
                    f"Entrar como {existente.nome}",
                    lambda: on_entrar(existente),
                    icone=ft.Icons.LOGIN_ROUNDED,
                )
                entrar_box.visible = True
                _erro(f"'{existente.nome}' já tem um perfil por aqui.")
                return

            erros = registration_service.validar_nome(v)
            if erros:
                _erro(erros[0])
                return
            nome_val = v
            _ir_para(1)

        def _ao_digitar() -> None:
            if entrar_box.visible or erro_txt.visible:
                entrar_box.visible = False
                _limpar_erro()

        campo = _campo(
            value=nome_val,
            hint_text="Digite seu nome...",
            hint_style=ft.TextStyle(color=T.MUTED, size=18),
            text_style=ft.TextStyle(color=T.TEXT, size=20, font_family=T.FONT_TITLE),
            max_length=NOME_MAX,
            on_submit=lambda: _next(),
        )
        campo.on_change = lambda: _ao_digitar()

        return _layout_passo(
            "Qual é o seu nome?",
            T.texto_secundario("Como você quer ser chamado na comunidade"),
            campo,
            ft.Container(height=16),
            ft.Row([T.botao_primario("Próximo", lambda: _next(), icone=ft.Icons.ARROW_FORWARD_ROUNDED)]),
            entrar_box,
            ft.Container(height=8),
            T.texto_secundario("Já tem perfil? Digite o mesmo nome para entrar.", 12,
                               text_align=ft.TextAlign.CENTER),
            *([T.texto_secundario(
                "Demo no navegador: experimente entrar como João, Ana ou Pedro. "
                "O que você cadastrar fica só nesta aba.",
                11, text_align=ft.TextAlign.CENTER, italic=True,
            )] if _DEMO_NO_NAVEGADOR else []),
        )

    def _passo_bio() -> ft.Container:

        def _next() -> None:
            nonlocal bio_val
            v = (campo.value or "").strip()
            erros = registration_service.validar_bio(v)
            if erros:
                _erro(erros[0])
                return
            bio_val = v
            _ir_para(2)

        def _pular() -> None:
            nonlocal bio_val
            bio_val = ""
            _ir_para(2)

        campo = _campo(
            value=bio_val,
            hint_text="Uma frase sobre você...",
            hint_style=ft.TextStyle(color=T.MUTED, size=16),
            text_style=ft.TextStyle(color=T.TEXT, size=16),
            multiline=True, min_lines=2, max_lines=4,
            max_length=BIO_MAX,
            shift_enter=True,
            on_submit=lambda: _next(),
        )

        return _layout_passo(
            "Sua bio",
            T.texto_secundario("Uma frase que te define. Totalmente opcional."),
            campo,
            ft.Container(height=16),
            ft.Row([T.botao_primario("Próximo", lambda: _next(), icone=ft.Icons.ARROW_FORWARD_ROUNDED)]),
            ft.Row([T.botao_texto("Pular esta etapa", lambda: _pular())],
                   alignment=ft.MainAxisAlignment.CENTER),
        )

    def _passo_interesses() -> ft.Container:
        contador = ft.Text("", size=12, color=T.ACCENT2, font_family=T.FONT_MONO)
        criar_btn = T.botao_primario("Criar perfil", lambda: _finalizar(), icone=ft.Icons.CHECK_ROUNDED)
        chips: List[ft.Chip] = []

        def _atualizar(atualizar: bool = True) -> None:
            cheio = len(interesses_selecionados) >= INTERESSES_MAX
            for chip in chips:
                chip.selected = chip.data in interesses_selecionados
                chip.disabled = cheio and not chip.selected
                # ícone de largura fixa: marcar não muda o tamanho do chip nem reflui a grade
                chip.leading  = ft.Icon(
                    ft.Icons.CHECK_ROUNDED if chip.selected else ft.Icons.ADD_ROUNDED,
                    size=14, color=T.TEXT if chip.selected else T.MUTED,
                )
            contador.value = f"{len(interesses_selecionados)}/{INTERESSES_MAX}"
            criar_btn.disabled = len(interesses_selecionados) < INTERESSES_MIN
            _limpar_erro(atualizar=False)
            if atualizar:
                page.update()

        def _alternar(e: ft.ControlEvent) -> None:
            interesse = e.control.data
            if interesse in interesses_selecionados:
                interesses_selecionados.remove(interesse)
            elif len(interesses_selecionados) < INTERESSES_MAX:
                interesses_selecionados.append(interesse)
            _atualizar()

        for interesse in INTERESSES_DISPONIVEIS:
            chips.append(ft.Chip(
                label=ft.Text(interesse, size=12, font_family=T.FONT_MONO),
                data=interesse,
                on_select=_alternar,
                show_checkmark=False,
                bgcolor=T.SURFACE2,
                selected_color=T.ACCENT,
                disabled_color=ft.Colors.with_opacity(0.4, T.SURFACE2),
                label_text_style=ft.TextStyle(color=T.TEXT),
                border_side=ft.BorderSide(1, T.BORDER),
                shape=ft.StadiumBorder(),
            ))
        _atualizar(atualizar=False)

        return _layout_passo(
            "O que você curte?",
            ft.Row([
                T.texto_secundario(f"Escolha de {INTERESSES_MIN} a {INTERESSES_MAX} interesses"),
                contador,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row(chips, wrap=True, spacing=8, run_spacing=8),
            ft.Container(height=16),
            ft.Row([criar_btn]),
        )

    def _finalizar() -> None:
        try:
            novo = registration_service.cadastrar(
                nome           = nome_val,
                interesses     = interesses_selecionados,
                bio            = bio_val,
            )
        except ValueError as ex:
            _erro(str(ex))
            return
        except OSError as ex:
            _erro(f"Não foi possível salvar seu perfil: {ex}")
            return
        on_cadastro_ok(novo)

    def _build_passo(p: int) -> ft.Container:
        if p == 0:   return _passo_nome()
        if p == 1:   return _passo_bio()
        return _passo_interesses()

    header = ft.Column([
        ft.Row([
            voltar_btn,
            T.logo(22),
            ft.Container(expand=True),
            progresso_txt,
        ], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER, height=40),
        ft.Container(height=6),
        progresso_bar,
    ], spacing=0)

    _ir_para(0, atualizar=False)

    return ft.View(
        route="/register",
        bgcolor=T.BG,
        padding=ft.Padding(24, 28, 24, 24),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            T.coluna_central(ft.Column([
                header,
                ft.Container(height=32),
                conteudo,
            ], expand=True, spacing=0)),
        ],
    )
