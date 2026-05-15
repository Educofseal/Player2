import flet as ft

# ── Cores ──────────────────────────────────────────────────────
BG           = "#0a0a0f"      # fundo principal
SURFACE      = "#12121a"      # cards / containers
SURFACE2     = "#1a1a26"      # inputs / containers secundários
SURFACE3     = "#22223a"      # hover / separadores

ACCENT       = "#7c3aed"      # roxo primário
ACCENT2      = "#a855f7"      # roxo claro
NEON         = "#c084fc"      # texto em destaque

LIKE_COLOR   = "#22c55e"      # verde — like / sucesso
NOPE_COLOR   = "#ef4444"      # vermelho — nope / erro
GOLD_COLOR   = "#f59e0b"      # âmbar — custo/Dijkstra
INFO_COLOR   = "#60a5fa"      # azul — informações

TEXT         = "#f0eeff"      # texto principal
MUTED        = "#6b7280"      # texto secundário
BORDER       = "#2a1f4a"      # bordas sutis

# ── Tipografia ────────────────────────────────────────────────
FONT_TITLE   = "Rajdhani"     # será importado via Google Fonts
FONT_MONO    = "Space Mono"
FONT_BODY    = "Inter"        # fallback do sistema

# ── Tamanhos ──────────────────────────────────────────────────
RADIUS       = 16
RADIUS_LG    = 24
PADDING      = 20
GAP          = 12

# ── Emojis por usuário (id → emoji) ───────────────────────────
EMOJIS = {
    1: "🧙", 2: "🦊", 3: "🐉", 4: "🌸",  5: "💻",
    6: "🎵", 7: "♟️", 8: "🎬", 9: "🔐", 10: "✨",
}

def emoji_para(uid: int) -> str:
    return EMOJIS.get(uid, "👾")


# ── Helpers de componentes comuns ─────────────────────────────

def tag_chip(texto: str, cor_bg: str = "#1e1040", cor_borda: str = ACCENT,
             cor_texto: str = NEON) -> ft.Container:
    """Chip de interesse (tag pill)."""
    return ft.Container(
        content=ft.Text(texto, size=11, color=cor_texto,
                        font_family=FONT_MONO, weight=ft.FontWeight.W_400),
        bgcolor=cor_bg,
        border=ft.Border.all(1, cor_borda),
        border_radius=20,
        padding=ft.Padding(10, 4, 10, 4),
    )


def divider() -> ft.Divider:
    return ft.Divider(height=1, color=BORDER)


def titulo_tela(texto: str) -> ft.Text:
    return ft.Text(
        texto,
        size=22,
        weight=ft.FontWeight.W_700,
        color=TEXT,
        font_family=FONT_TITLE,
    )