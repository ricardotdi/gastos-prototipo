#!/usr/bin/env python3
"""Gera o lockup "emblema + BRUMA / FINANCE" (texto em duas linhas, BRUMA
maior por cima, FINANCE mais pequeno por baixo) como PNG com fundo
transparente, em duas variantes de cor de texto (branco, para fundos
escuros; e tinta escura, para fundos claros)."""
from PIL import Image, ImageDraw, ImageFont
import os

RAIZ = "/home/user/gastos-prototipo"
EMBLEMA = os.path.join(RAIZ, "bruma-emblem.png")
FONTE = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

ALTURA_EMBLEMA = 200
GAP = 32
MARGEM = 24

TAMANHO_BRUMA = 84
TAMANHO_FINANCE = 42
TRACKING_FINANCE = 6  # espaçamento extra entre letras, em pixels

fonte_bruma = ImageFont.truetype(FONTE, TAMANHO_BRUMA)
fonte_finance = ImageFont.truetype(FONTE, TAMANHO_FINANCE)

emblema = Image.open(EMBLEMA).convert("RGBA")
escala = ALTURA_EMBLEMA / emblema.size[1]
emblema = emblema.resize((round(emblema.size[0] * escala), ALTURA_EMBLEMA), Image.LANCZOS)


def largura_com_tracking(texto, fonte, tracking):
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    largura = 0
    for ch in texto:
        largura += d.textlength(ch, font=fonte) + tracking
    return largura - tracking


def desenhar_com_tracking(draw, pos, texto, fonte, tracking, fill):
    x, y = pos
    for ch in texto:
        draw.text((x, y), ch, font=fonte, fill=fill)
        x += draw.textlength(ch, font=fonte) + tracking


tmp = Image.new("RGBA", (10, 10))
d_tmp = ImageDraw.Draw(tmp)
bbox_bruma = d_tmp.textbbox((0, 0), "BRUMA", font=fonte_bruma)
largura_bruma = bbox_bruma[2] - bbox_bruma[0]
altura_bruma = bbox_bruma[3] - bbox_bruma[1]
largura_finance = largura_com_tracking("FINANCE", fonte_finance, TRACKING_FINANCE)
bbox_finance = d_tmp.textbbox((0, 0), "FINANCE", font=fonte_finance)
altura_finance = bbox_finance[3] - bbox_finance[1]

largura_texto = max(largura_bruma, largura_finance)
gap_linhas = 6
altura_texto = altura_bruma + gap_linhas + altura_finance

largura_total = MARGEM * 2 + emblema.size[0] + GAP + round(largura_texto)
altura_total = MARGEM * 2 + max(emblema.size[1], round(altura_texto))


def gerar(cor_texto, cor_finance, nome_ficheiro):
    canvas = Image.new("RGBA", (largura_total, altura_total), (0, 0, 0, 0))
    y_emblema = (altura_total - emblema.size[1]) // 2
    canvas.alpha_composite(emblema, (MARGEM, y_emblema))

    d = ImageDraw.Draw(canvas)
    x_texto = MARGEM + emblema.size[0] + GAP
    y_bloco = (altura_total - altura_texto) // 2

    y_bruma = y_bloco - bbox_bruma[1]
    d.text((x_texto, y_bruma), "BRUMA", font=fonte_bruma, fill=cor_texto)

    y_finance = y_bloco + altura_bruma + gap_linhas - bbox_finance[1]
    desenhar_com_tracking(d, (x_texto, y_finance), "FINANCE", fonte_finance, TRACKING_FINANCE, cor_finance)

    destino = os.path.join(RAIZ, nome_ficheiro)
    canvas.save(destino, "PNG")
    print(f"Gerado {destino} ({canvas.size[0]}x{canvas.size[1]})")


gerar((255, 255, 255, 255), (255, 255, 255, 190), "bruma-logo-texto-branco.png")
gerar((21, 21, 21, 255), (21, 21, 21, 170), "bruma-logo-texto-escuro.png")
