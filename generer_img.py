#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Genere automatiquement les images SEO StrateGis :
- img/og-image.jpg (1200x630) - image de partage social
- apple-touch-icon.png (192x192) - icone iOS/mobile
- favicon.png (64x64) - icone de secours

Base sur le logo SGS (bleu marine #0F1E4D, dore #C89B3C, fond creme #F0EBDC)
"""

import sys
import math
from pathlib import Path

# Verifie que Pillow est installe
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERREUR : Pillow n'est pas installe.")
    print("Installez-le avec : pip install Pillow")
    sys.exit(1)

# ===== Configuration =====
PROJECT_DIR = Path(__file__).parent.resolve()
IMG_DIR = PROJECT_DIR / "img"
IMG_DIR.mkdir(exist_ok=True)

# Couleurs du logo SGS
NAVY = (15, 30, 77)       # #0F1E4D - bleu marine
GOLD = (200, 155, 60)     # #C89B3C - dore
CREAM = (240, 235, 220)   # #F0EBDC - fond creme
NAVY_LIGHT = (30, 50, 100)
GOLD_LIGHT = (220, 180, 90)


def find_font(size, bold=False):
    """Trouve une police systeme disponible."""
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def draw_sgs_logo(draw, x, y, size, with_bg=True):
    """
    Dessine le logo SGS (S-G-S avec fleche doree) aux coordonnees donnees.
    size = taille de la zone carree contenant le logo
    """
    # Fond arrondi creme
    if with_bg:
        radius = size // 5
        draw.rounded_rectangle(
            [x, y, x + size, y + size],
            radius=radius,
            fill=CREAM,
            outline=None
        )

    # Lettres S, G, S en bleu marine
    font_size = int(size * 0.55)
    font = find_font(font_size, bold=True)

    # Positionnement des 3 lettres
    padding = int(size * 0.12)
    letter_area = size - 2 * padding
    letter_width = letter_area // 3

    letters = ["S", "G", "S"]
    for i, letter in enumerate(letters):
        bbox = draw.textbbox((0, 0), letter, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        lx = x + padding + i * letter_width + (letter_width - w) // 2 - bbox[0]
        ly = y + (size - h) // 2 - bbox[1]

        draw.text((lx, ly), letter, font=font, fill=NAVY)

    # Fleche doree qui traverse de bas-gauche vers haut-droite
    arrow_start_x = x + int(size * 0.10)
    arrow_start_y = y + int(size * 0.80)
    arrow_end_x = x + int(size * 0.92)
    arrow_end_y = y + int(size * 0.28)

    # Cercle de depart (point dore)
    circle_r = int(size * 0.06)
    draw.ellipse(
        [arrow_start_x - circle_r, arrow_start_y - circle_r,
         arrow_start_x + circle_r, arrow_start_y + circle_r],
        fill=GOLD
    )

    # Ligne principale (courbe douce)
    points = []
    segments = 40
    for i in range(segments + 1):
        t = i / segments
        ctrl_x = (arrow_start_x + arrow_end_x) / 2
        ctrl_y = arrow_start_y - (arrow_start_y - arrow_end_y) * 1.3

        px = (1 - t) ** 2 * arrow_start_x + 2 * (1 - t) * t * ctrl_x + t ** 2 * arrow_end_x
        py = (1 - t) ** 2 * arrow_start_y + 2 * (1 - t) * t * ctrl_y + t ** 2 * arrow_end_y
        points.append((px, py))

    line_width = max(4, int(size * 0.035))

    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=GOLD, width=line_width)

    # Pointe de fleche (triangle a l'arrivee)
    dx = points[-1][0] - points[-2][0]
    dy = points[-1][1] - points[-2][1]
    angle = math.atan2(dy, dx)

    head_length = int(size * 0.12)
    head_width = int(size * 0.09)

    tip_x, tip_y = arrow_end_x, arrow_end_y

    left_x = tip_x - head_length * math.cos(angle) - head_width * math.sin(angle)
    left_y = tip_y - head_length * math.sin(angle) + head_width * math.cos(angle)

    right_x = tip_x - head_length * math.cos(angle) + head_width * math.sin(angle)
    right_y = tip_y - head_length * math.sin(angle) - head_width * math.cos(angle)

    draw.polygon(
        [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)],
        fill=GOLD
    )


def create_og_image():
    """Genere img/og-image.jpg (1200x630) pour les partages sociaux."""
    print("  Generation de og-image.jpg (1200x630)...")

    W, H = 1200, 630
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Degrade de fond (navy -> navy plus clair)
    for y in range(H):
        ratio = y / H
        r = int(NAVY[0] + (NAVY_LIGHT[0] - NAVY[0]) * ratio * 0.3)
        g = int(NAVY[1] + (NAVY_LIGHT[1] - NAVY[1]) * ratio * 0.3)
        b = int(NAVY[2] + (NAVY_LIGHT[2] - NAVY[2]) * ratio * 0.3)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Motif discret de grille (points dores tres legers)
    for gx in range(0, W, 60):
        for gy in range(0, H, 60):
            draw.ellipse(
                [gx - 1, gy - 1, gx + 1, gy + 1],
                fill=(30, 45, 90)
            )

    # --- LOGO SGS (cote gauche) ---
    logo_size = 280
    logo_x = 80
    logo_y = (H - logo_size) // 2
    draw_sgs_logo(draw, logo_x, logo_y, logo_size, with_bg=True)

    # --- TEXTE (cote droit) ---
    text_x = logo_x + logo_size + 60

    # Titre : StrateGis
    font_title = find_font(72, bold=True)
    draw.text((text_x, 175), "StrateGis", font=font_title, fill=(255, 255, 255))

    # Sous-titre : Developpement Web - Mobile - Desktop - IA
    font_sub = find_font(30, bold=False)
    draw.text(
        (text_x, 275),
        "Developpement Web - Mobile - Desktop - IA",
        font=font_sub,
        fill=GOLD
    )

    # Ligne decorative doree
    draw.rectangle(
        [text_x, 330, text_x + 80, 334],
        fill=GOLD
    )

    # Description
    font_desc = find_font(24, bold=False)
    draw.text(
        (text_x, 360),
        "Sites vitrines, applications mobiles, logiciels desktop",
        font=font_desc,
        fill=(200, 210, 230)
    )
    draw.text(
        (text_x, 395),
        "et agents IA conversationnels (RAG).",
        font=font_desc,
        fill=(200, 210, 230)
    )
    draw.text(
        (text_x, 445),
        "Solutions sur mesure a Ouagadougou, Burkina Faso.",
        font=font_desc,
        fill=(200, 210, 230)
    )

    # --- URL en bas a droite ---
    font_url = find_font(22, bold=False)
    url_text = "strategis-of.netlify.app"
    bbox = draw.textbbox((0, 0), url_text, font=font_url)
    url_w = bbox[2] - bbox[0]
    draw.text(
        (W - url_w - 60, H - 55),
        url_text,
        font=font_url,
        fill=GOLD
    )

    # Enregistre
    out = IMG_DIR / "og-image.jpg"
    img.save(out, "JPEG", quality=92, optimize=True)
    print(f"    OK  {out} ({out.stat().st_size // 1024} Ko)")


def create_apple_touch_icon():
    """Genere apple-touch-icon.png (192x192) pour iOS/mobile."""
    print("  Generation de apple-touch-icon.png (192x192)...")

    S = 192
    img = Image.new("RGB", (S, S), CREAM)
    draw = ImageDraw.Draw(img)

    draw_sgs_logo(draw, 0, 0, S, with_bg=True)

    out = PROJECT_DIR / "apple-touch-icon.png"
    img.save(out, "PNG", optimize=True)
    print(f"    OK  {out} ({out.stat().st_size // 1024} Ko)")


def create_favicon_png():
    """Genere favicon.png (64x64) en secours pour les navigateurs anciens."""
    print("  Generation de favicon.png (64x64)...")

    S = 64
    img = Image.new("RGB", (S, S), CREAM)
    draw = ImageDraw.Draw(img)
    draw_sgs_logo(draw, 0, 0, S, with_bg=True)

    out = PROJECT_DIR / "favicon.png"
    img.save(out, "PNG", optimize=True)
    print(f"    OK  {out} ({out.stat().st_size // 1024} Ko)")


def main():
    print("=" * 60)
    print("Generation des images SEO StrateGis")
    print("=" * 60)
    print(f"\nDossier projet : {PROJECT_DIR}\n")

    try:
        create_og_image()
        create_apple_touch_icon()
        create_favicon_png()

        print("\n" + "=" * 60)
        print("SUCCES !")
        print("=" * 60)
        print("\nImages generees :")
        print("  - img/og-image.jpg          (partages WhatsApp/Facebook/LinkedIn)")
        print("  - apple-touch-icon.png      (icone iOS/mobile)")
        print("  - favicon.png               (favicon de secours)")
        print("\nProchaines etapes :")
        print("  1. Verifiez visuellement les images dans img/og-image.jpg")
        print("  2. Deployez : git add . && git commit -m 'Images SEO' && git push")
        print("\nTest des partages sociaux :")
        print("  - Facebook : https://developers.facebook.com/tools/debug/")
        print("  - LinkedIn : https://www.linkedin.com/post-inspector/")

    except Exception as e:
        print(f"\nErreur : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()