#!/usr/bin/env python3
"""Gera os icones da app (icons/icon-192.png, icons/icon-512.png) a partir do
emblema bruma-emblem.png: centra o emblema a 80% do canvas (zona segura para
icones "maskable" do Android, que cortam as margens conforme a forma do
lançador) sobre um fundo solido --brand-dark (icones maskable nao podem ter
transparencia). Correr a partir da raiz do repo: python3 scripts/generate-icons.py
"""
from PIL import Image
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBLEMA = os.path.join(RAIZ, "bruma-emblem.png")
FUNDO = (26, 26, 26, 255)  # --brand-dark #1A1A1A
ZONA_SEGURA = 0.8  # 80% do canvas, margem de 10% de cada lado

TAMANHOS = [192, 512]


def gerar(tamanho):
    canvas = Image.new("RGBA", (tamanho, tamanho), FUNDO)
    emblema = Image.open(EMBLEMA).convert("RGBA")

    lado_alvo = int(tamanho * ZONA_SEGURA)
    escala = lado_alvo / max(emblema.size)
    novo_tamanho = (round(emblema.size[0] * escala), round(emblema.size[1] * escala))
    emblema_redim = emblema.resize(novo_tamanho, Image.LANCZOS)

    pos_x = (tamanho - novo_tamanho[0]) // 2
    pos_y = (tamanho - novo_tamanho[1]) // 2
    canvas.alpha_composite(emblema_redim, (pos_x, pos_y))

    destino = os.path.join(RAIZ, "icons", f"icon-{tamanho}.png")
    canvas.convert("RGB").save(destino, "PNG")
    print(f"Gerado {destino} ({tamanho}x{tamanho})")


if __name__ == "__main__":
    for t in TAMANHOS:
        gerar(t)
