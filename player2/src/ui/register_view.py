import flet as ft
from typing import Callable, Dict, List

from src.services.registration_service import RegistrationService, INTERESSES_DISPONIVEIS
from src.services.risk_service import PERGUNTAS
from src.core.user import User
from src.ui import theme as T

_TOTAL_PERGUNTAS = len(PERGUNTAS)  
_PASSOS_INICIAIS = 3               
_TOTAL_PASSOS    = _PASSOS_INICIAIS + _TOTAL_PERGUNTAS 


def build_register_view(
    page: ft.Page,
    registration_service: RegistrationService,
    on_cadastro_ok: Callable[[User], None],
) -> ft.View:

    passo:      List[int] = [0]
    nome_val:   List[str] = [""]
    bio_val:    List[str] = [""]
    interesses_selecionados: List[str] = []
    quiz_respostas: Dict[int, int]     = {}

    progresso_bar = ft.Ref[ft.ProgressBar]()
    progresso_txt = ft.Ref[ft.Text]()
    conteudo_ref  = ft.Ref[ft.Container]()
    erro_ref      = ft.Ref[ft.Text]()

    def _erro(msg: str) -> None:
        erro_ref.current.value = msg
        page.update()

    def _avancar() -> None:
        passo[0] += 1
        _renderizar()

    def _renderizar() -> None:
        p = passo[0]
        val = (p + 1) / _TOTAL_PASSOS
        progresso_bar.current.value = min(val, 1.0)
        progresso_txt.current.value = f"{min(p + 1, _TOTAL_PASSOS)}/{_TOTAL_PASSOS}"
        erro_ref.current.value      = ""
        conteudo_ref.current.content = _build_passo(p)
        page.update()

    def _passo_nome() -> ft.Column:
        campo = ft.TextField(
            value=nome_val[0],
            hint_text="Digite seu nome...",
            hint_style=ft.TextStyle(color=T.MUTED, size=18),
            text_style=ft.TextStyle(color=T.TEXT, size=20, font_family=T.FONT_TITLE),
            bgcolor="transparent",
            border_color="transparent",
            focused_border_color="transparent",
            content_padding=ft.Padding(0, 8, 0, 8),
            max_length=40,
            cursor_color=T.ACCENT2,
            autofocus=True,
        )

        def _next(e: ft.ControlEvent) -> None:
            v = (campo.value or "").strip()
            if len(v) < 2:
                _erro("Nome deve ter ao menos 2 caracteres.")
                return
            if len(v) > 40:
                _erro("Nome deve ter no máximo 40 caracteres.")
                return
            nomes = [u.nome.lower() for u in registration_service.grafo.get_todos_usuarios()]
            if v.lower() in nomes:
                _erro(f"'{v}' já está em uso. Escolha outro nome.")
                return
            nome_val[0] = v
            _avancar()

        return ft.Column([
            ft.Text("Qual é o seu nome?", size=28, color=T.TEXT,
                    weight=ft.FontWeight.W_700, font_family=T.FONT_TITLE),
            ft.Text("Como você quer ser chamado na comunidade",
                    size=13, color=T.MUTED),
            ft.Container(height=32),
            ft.Container(
                content=campo,
                bgcolor=T.SURFACE2,
                border=ft.Border(bottom=ft.BorderSide(2, T.ACCENT)),
                border_radius=ft.BorderRadius(T.RADIUS, T.RADIUS, 0, 0),
                padding=ft.Padding(20, 16, 20, 16),
            ),
            ft.Container(height=32),
            ft.Row([
                ft.ElevatedButton(
                    content=ft.Text("Próximo →", size=16, weight=ft.FontWeight.W_600,
                                    font_family=T.FONT_TITLE, color=T.TEXT),
                    on_click=_next,
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: T.ACCENT,
                                 ft.ControlState.HOVERED: T.ACCENT2,
                                 ft.ControlState.PRESSED: "#5b21b6"},
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS),
                        padding=ft.Padding(0, 18, 0, 18),
                    ),
                    expand=True, height=52,
                ),
            ]),
        ], spacing=8)

    def _passo_bio() -> ft.Column:
        campo = ft.TextField(
            value=bio_val[0],
            hint_text="Uma frase sobre você...",
            hint_style=ft.TextStyle(color=T.MUTED, size=16),
            text_style=ft.TextStyle(color=T.TEXT, size=16),
            bgcolor="transparent",
            border_color="transparent",
            focused_border_color="transparent",
            content_padding=ft.Padding(0, 8, 0, 8),
            multiline=True, min_lines=2, max_lines=4,
            max_length=160,
            cursor_color=T.ACCENT2,
            autofocus=True,
        )

        def _next(e: ft.ControlEvent) -> None:
            v = (campo.value or "").strip()
            if len(v) > 160:
                _erro("Bio deve ter no máximo 160 caracteres.")
                return
            bio_val[0] = v
            _avancar()

        def _pular(e: ft.ControlEvent) -> None:
            bio_val[0] = ""
            _avancar()

        return ft.Column([
            ft.Text("Sua bio", size=28, color=T.TEXT,
                    weight=ft.FontWeight.W_700, font_family=T.FONT_TITLE),
            ft.Text("Uma frase que te define — totalmente opcional",
                    size=13, color=T.MUTED),
            ft.Container(height=32),
            ft.Container(
                content=campo,
                bgcolor=T.SURFACE2,
                border=ft.Border(bottom=ft.BorderSide(2, T.ACCENT)),
                border_radius=ft.BorderRadius(T.RADIUS, T.RADIUS, 0, 0),
                padding=ft.Padding(20, 16, 20, 16),
            ),
            ft.Container(height=32),
            ft.Row([
                ft.ElevatedButton(
                    content=ft.Text("Próximo →", size=16, weight=ft.FontWeight.W_600,
                                    font_family=T.FONT_TITLE, color=T.TEXT),
                    on_click=_next,
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: T.ACCENT,
                                 ft.ControlState.HOVERED: T.ACCENT2,
                                 ft.ControlState.PRESSED: "#5b21b6"},
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS),
                        padding=ft.Padding(0, 18, 0, 18),
                    ),
                    expand=True, height=52,
                ),
            ]),
            ft.TextButton(
                "Pular esta etapa",
                on_click=_pular,
                style=ft.ButtonStyle(color=T.MUTED),
            ),
        ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _passo_interesses() -> ft.Column:
        contador = ft.Text(
            f"{len(interesses_selecionados)} selecionado(s)",
            size=12, color=T.ACCENT2,
        )

        grid = ft.GridView(
            expand=False,
            runs_count=3,
            max_extent=130,
            child_aspect_ratio=2.8,
            spacing=8, run_spacing=8,
        )

        def _on_cb(e: ft.ControlEvent) -> None:
            cb = e.control
            if cb.value:
                if cb.data not in interesses_selecionados:
                    interesses_selecionados.append(cb.data)
            else:
                if cb.data in interesses_selecionados:
                    interesses_selecionados.remove(cb.data)
            contador.value = f"{len(interesses_selecionados)} selecionado(s)"
            page.update()

        for interesse in INTERESSES_DISPONIVEIS:
            cb = ft.Checkbox(
                label=interesse, data=interesse,
                value=interesse in interesses_selecionados,
                on_change=_on_cb,
                fill_color={ft.ControlState.SELECTED: T.ACCENT,
                            ft.ControlState.DEFAULT:  T.SURFACE3},
                check_color=T.TEXT,
                label_style=ft.TextStyle(size=12, color=T.TEXT, font_family=T.FONT_MONO),
            )
            grid.controls.append(cb)

        def _next(e: ft.ControlEvent) -> None:
            if len(interesses_selecionados) < 1:
                _erro("Selecione ao menos 1 interesse.")
                return
            if len(interesses_selecionados) > 10:
                _erro("Selecione no máximo 10 interesses.")
                return
            _avancar()

        return ft.Column([
            ft.Text("O que você curte?", size=28, color=T.TEXT,
                    weight=ft.FontWeight.W_700, font_family=T.FONT_TITLE),
            ft.Row([
                ft.Text("Escolha seus interesses", size=13, color=T.MUTED),
                contador,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=12),
            ft.Container(
                content=grid,
                bgcolor=T.SURFACE2,
                border=ft.Border.all(1, T.BORDER),
                border_radius=T.RADIUS,
                padding=T.PADDING,
                height=270,
            ),
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    content=ft.Text("Próximo →", size=16, weight=ft.FontWeight.W_600,
                                    font_family=T.FONT_TITLE, color=T.TEXT),
                    on_click=_next,
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: T.ACCENT,
                                 ft.ControlState.HOVERED: T.ACCENT2,
                                 ft.ControlState.PRESSED: "#5b21b6"},
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS),
                        padding=ft.Padding(0, 18, 0, 18),
                    ),
                    expand=True, height=52,
                ),
            ]),
        ], spacing=8)

    def _passo_quiz(idx: int) -> ft.Column:
        pergunta = PERGUNTAS[idx]
        pid      = pergunta["id"]
        eh_ultima = idx == _TOTAL_PERGUNTAS - 1
        opcao_controls: List[ft.Container] = []

        def _selecionar(e: ft.ControlEvent, score: int, idx_opcao: int) -> None:
            quiz_respostas[pid] = score

            for i, c in enumerate(opcao_controls):
                sel = (i == idx_opcao)
                c.bgcolor = "#1e1040" if sel else T.SURFACE2
                c.border  = ft.Border.all(1, T.ACCENT if sel else T.BORDER)
                c.content.color = T.NEON if sel else T.TEXT
            page.update()

            if eh_ultima:
                _finalizar()
            else:
                _avancar()

        for i, (texto_opcao, score) in enumerate(pergunta["opcoes"]):
            def _handler(e, s=score, io=i):
                _selecionar(e, s, io)

            cont = ft.Container(
                content=ft.Text(texto_opcao, size=13, color=T.TEXT,
                                font_family=T.FONT_MONO),
                bgcolor=T.SURFACE2,
                border=ft.Border.all(1, T.BORDER),
                border_radius=T.RADIUS,
                padding=ft.Padding(18, 14, 18, 14),
                on_click=_handler,
            )
            opcao_controls.append(cont)

        num_label = ft.Container(
            content=ft.Text(f"{idx + 1}/{_TOTAL_PERGUNTAS}", size=11,
                            color=T.ACCENT2, font_family=T.FONT_MONO,
                            weight=ft.FontWeight.W_600),
            bgcolor=T.SURFACE3,
            border_radius=20,
            padding=ft.Padding(12, 5, 12, 5),
        )

        return ft.Column([
            ft.Row([num_label]),
            ft.Container(height=20),
            ft.Text(
                pergunta["texto"],
                size=20,
                color=T.TEXT,
                weight=ft.FontWeight.W_600,
                font_family=T.FONT_TITLE,
            ),
            ft.Container(height=28),
            ft.Column(opcao_controls, spacing=10),
        ], spacing=0)

    def _finalizar() -> None:
        try:
            novo = registration_service.cadastrar(
                nome           = nome_val[0],
                interesses     = interesses_selecionados,
                bio            = bio_val[0],
                respostas_quiz = quiz_respostas,
            )
            on_cadastro_ok(novo)
        except ValueError as ex:
            _erro(str(ex))

    def _build_passo(p: int) -> ft.Column:
        if p == 0:   return _passo_nome()
        if p == 1:   return _passo_bio()
        if p == 2:   return _passo_interesses()
        return _passo_quiz(p - _PASSOS_INICIAIS)

    header = ft.Column([
        ft.Row([
            ft.Text("PLAYER", size=22, weight=ft.FontWeight.W_700,
                    color=T.NEON, font_family=T.FONT_TITLE),
            ft.Text("2", size=22, weight=ft.FontWeight.W_700,
                    color=T.ACCENT2, font_family=T.FONT_TITLE),
            ft.Container(expand=True),
            ft.Text(ref=progresso_txt, value=f"1/{_TOTAL_PASSOS}",
                    size=11, color=T.MUTED, font_family=T.FONT_MONO),
        ], spacing=0),
        ft.Container(height=10),
        ft.ProgressBar(
            ref=progresso_bar,
            value=1 / _TOTAL_PASSOS,
            color=T.ACCENT,
            bgcolor=T.SURFACE3,
            height=4,
            border_radius=4,
        ),
    ], spacing=0)

    return ft.View(
        route="/register",
        bgcolor=T.BG,
        padding=ft.Padding(24, 36, 24, 24),
        controls=[
            ft.Column([
                header,
                ft.Container(height=36),
                ft.Container(
                    ref=conteudo_ref,
                    content=_build_passo(0),
                    expand=True,
                ),
                ft.Container(height=8),
                ft.Text(ref=erro_ref, value="", size=12,
                        color=T.NOPE_COLOR, italic=True),
            ], expand=True, spacing=0),
        ],
    )
