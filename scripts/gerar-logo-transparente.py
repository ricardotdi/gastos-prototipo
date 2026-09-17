#!/usr/bin/env python3
"""Gera o lockup "emblema + Bruma Finance" como PNG com fundo transparente,
em duas variantes de cor de texto (branco, para fundos escuros; e tinta
escura, para fundos claros)."""
from PIL import Image, ImageDraw, ImageFont
import os

RAIZ = "/home/user/gastos-prototipo"
EMBLEMA = os.path.join(RAIZ, "bruma-emblem.png")
FONTE = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

ALTURA_EMBLEMA = 200
GAP = 36
TAMANHO_FONTE = 84
MARGEM = 24

emblema = Image.open(EMBLEMA).convert("RGBA")
escala = ALTURA_EMBLEMA / emblema.size[1]
emblema = emblema.resize((round(emblema.size[0] * escala), ALTURA_EMBLEMA), Image.LANCZOS)

fonte = ImageFont.truetype(FONTE, TAMANHO_FONTE)
texto = "Bruma Finance"

# Mede o texto num canvas temporario
tmp = Image.new("RGBA", (10, 10))
d = ImageDraw.Draw(tmp)
bbox = d.textbbox((0, 0), texto, font=fonte)
largura_texto = bbox[2] - bbox[0]
altura_texto = bbox[3] - bbox[1]

largura_total = MARGEM * 2 + emblema.size[0] + GAP + largura_texto
altura_total = MARGEM * 2 + max(emblema.size[1], altura_texto)


def gerar(cor_texto, nome_ficheiro):
    canvas = Image.new("RGBA", (largura_total, altura_total), (0, 0, 0, 0))
    y_emblema = (altura_total - emblema.size[1]) // 2
    canvas.alpha_composite(emblema, (MARGEM, y_emblema))

    d = ImageDraw.Draw(canvas)
    x_texto = MARGEM + emblema.size[0] + GAP
    y_texto = (altura_total - altura_texto) // 2 - bbox[1]
    d.text((x_texto, y_texto), texto, font=fonte, fill=cor_texto)

    destino = os.path.join(RAIZ, nome_ficheiro)
    canvas.save(destino, "PNG")
    print(f"Gerado {destino} ({canvas.size[0]}x{canvas.size[1]})")


gerar((255, 255, 255, 255), "bruma-logo-texto-branco.png")
gerar((21, 21, 21, 255), "bruma-logo-texto-escuro.png")
