import flet as ft

BG           = "#0a0a0f"     
SURFACE      = "#12121a"    
SURFACE2     = "#1a1a26"   
SURFACE3     = "#22223a"    

ACCENT       = "#7c3aed"     
ACCENT2      = "#a855f7"   
NEON         = "#c084fc"     

LIKE_COLOR   = "#22c55e"     
NOPE_COLOR   = "#ef4444"    
GOLD_COLOR   = "#f59e0b"  
INFO_COLOR   = "#60a5fa"    

TEXT         = "#f0eeff"    
MUTED        = "#6b7280"    
BORDER       = "#2a1f4a"     

FONT_TITLE   = "Rajdhani"    
FONT_MONO    = "Space Mono"
FONT_BODY    = "Inter"    

RADIUS       = 16
RADIUS_LG    = 24
PADDING      = 20
GAP          = 12

EMOJIS = {
    1: "🧙", 2: "🦊", 3: "🐉", 4: "🌸",  5: "💻",
    6: "🎵", 7: "♟️", 8: "🎬", 9: "🔐", 10: "✨",
}

def emoji_para(uid: int) -> str:
    return EMOJIS.get(uid, "👾")


def tag_chip(texto: str, cor_bg: str = "#1e1040", cor_borda: str = ACCENT,
             cor_texto: str = NEON) -> ft.Container:
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