"""Gera os ícones do Player2 (app nativo, PWA/iPhone, favicon e tela de carregamento web).

Uso (na pasta player2/):  python scripts/gerar_icones.py      (requer Pillow)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ   = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"
FONTE  = ASSETS / "fonts" / "Rajdhani-Bold.ttf"

BG, SURFACE3, ACCENT, ACCENT2, TEXT = "#0a0a0f", "#22223a", "#7c3aed", "#a855f7", "#f0eeff"
LADO = 1024


def _card(cor_topo: str, cor_base: str, contorno: str = None) -> Image.Image:
    """Card arredondado com degradê vertical, num canvas transparente."""
    w, h = 500, 620
    degrade = Image.new("RGBA", (w, h))
    topo, base = Image.new("RGBA", (w, h), cor_topo), Image.new("RGBA", (w, h), cor_base)
    mascara_degrade = Image.linear_gradient("L").resize((w, h))
    degrade = Image.composite(base, topo, mascara_degrade)

    forma = Image.new("L", (w, h), 0)
    ImageDraw.Draw(forma).rounded_rectangle((0, 0, w - 1, h - 1), radius=72, fill=255)
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    card.paste(degrade, (0, 0), forma)
    if contorno:
        ImageDraw.Draw(card).rounded_rectangle((4, 4, w - 5, h - 5), radius=70,
                                               outline=contorno, width=10)
    return card


def _logo(fundo: bool) -> Image.Image:
    img = Image.new("RGBA", (LADO, LADO), BG if fundo else (0, 0, 0, 0))

    if fundo:   # brilho roxo atrás dos cards
        brilho = Image.new("RGBA", (LADO, LADO), (0, 0, 0, 0))
        ImageDraw.Draw(brilho).ellipse((212, 212, 812, 812), fill=(124, 58, 237, 110))
        img.alpha_composite(brilho.filter(ImageFilter.GaussianBlur(120)))

    for card, angulo, dx in (
        (_card(SURFACE3, SURFACE3, contorno=ACCENT), 12, -40),
        (_card(ACCENT2, ACCENT), -6, 30),
    ):
        girado = card.rotate(angulo, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(girado, ((LADO - girado.width) // 2 + dx,
                                     (LADO - girado.height) // 2))

    texto = ImageDraw.Draw(img)
    fonte = ImageFont.truetype(str(FONTE), 330)
    texto.text((LADO // 2 + 30, LADO // 2 + 10), "P2", font=fonte, fill=TEXT, anchor="mm")
    return img


def _cantos_arredondados(img: Image.Image, raio: int) -> Image.Image:
    mascara = Image.new("L", img.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, *img.size), radius=raio, fill=255)
    saida = Image.new("RGBA", img.size, (0, 0, 0, 0))
    saida.paste(img, (0, 0), mascara)
    return saida


def _salvar(img: Image.Image, caminho: Path, lado: int, rgb: bool = False) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    final = img.resize((lado, lado), Image.LANCZOS)
    if rgb:
        final = final.convert("RGB")
    final.save(caminho, optimize=True)
    print("gerado:", caminho.relative_to(RAIZ), f"{lado}x{lado}")


def main() -> None:
    com_fundo = _logo(fundo=True)          # sangra até a borda: iOS e Android aplicam a máscara
    arredondado = _cantos_arredondados(com_fundo, 220)
    sem_fundo = _logo(fundo=False)

    _salvar(com_fundo, ASSETS / "icon.png", 1024, rgb=True)                  # flet build
    _salvar(com_fundo, ASSETS / "icons" / "apple-touch-icon-192.png", 192, rgb=True)
    _salvar(com_fundo, ASSETS / "icons" / "icon-maskable-192.png", 192, rgb=True)
    _salvar(com_fundo, ASSETS / "icons" / "icon-maskable-512.png", 512, rgb=True)
    _salvar(arredondado, ASSETS / "icons" / "icon-192.png", 192)
    _salvar(arredondado, ASSETS / "icons" / "icon-512.png", 512)
    _salvar(arredondado, ASSETS / "favicon.png", 32)
    _salvar(sem_fundo, ASSETS / "icons" / "loading-animation.png", 512)


if __name__ == "__main__":
    main()
