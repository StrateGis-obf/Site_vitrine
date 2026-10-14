#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Affiche corporate StrateGis style professionnel
Format : A4 portrait (2480x3508 @ 300 DPI)

Dependances : pip install Pillow qrcode
"""

import sys
import math
import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("ERREUR : Pillow non installe. pip install Pillow")
    sys.exit(1)

# QR code (optionnel)
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


# ===== Config =====
PROJECT_DIR = Path(__file__).parent.resolve()
OUT_DIR = PROJECT_DIR / "affiches"
IMG_DIR = PROJECT_DIR / "img"
OUT_DIR.mkdir(exist_ok=True)

# ===== Couleurs (charte StrateGis) =====
NAVY_DARK = (10, 18, 40)      # Bleu très foncé (header)
NAVY = (15, 30, 77)           # Bleu marine
BLUE_LIGHT = (30, 100, 200)   # Bleu clair (accents)
CYAN = (60, 180, 220)         # Cyan (titres)
ORANGE = (245, 130, 32)       # Orange (CTA, numéros)
ORANGE_DARK = (200, 90, 20)   # Orange foncé
WHITE = (255, 255, 255)
GRAY_LIGHT = (245, 245, 245)  # Fond gris très clair
GRAY = (150, 150, 150)
GRAY_DARK = (60, 60, 60)
BLACK = (0, 0, 0)
GOLD = (200, 155, 60)


# ===== Polices =====
def find_font(bold=True):
    paths = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
         "C:/Windows/Fonts/calibrib.ttf"]
        if bold else
        ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
         "C:/Windows/Fonts/calibri.ttf"]
    )
    for p in paths:
        if os.path.exists(p):
            return p
    return "arial"


FONT_B = find_font(True)
FONT_R = find_font(False)
print(f"Police titre   : {FONT_B}")
print(f"Police normale : {FONT_R}")

_fc = {}
def F(size, bold=True):
    key = (size, bold)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(FONT_B if bold else FONT_R, size)
    return _fc[key]


# ===== Helpers =====
def draw_centered(draw, text, cx, y, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    draw.text((cx - w // 2, y), text, font=fnt, fill=fill)
    return w


def draw_left(draw, text, x, y, fnt, fill):
    draw.text((x, y), text, font=fnt, fill=fill)


# ===== Logo =====
def make_logo(S):
    """Charge le logo depuis img/logo.png ou dessine un fallback."""
    logo_path = IMG_DIR / "logo.png"
    if logo_path.exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            w, h = logo.size
            # Conserve les proportions
            ratio = S / max(w, h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            return logo.resize((new_w, new_h), Image.LANCZOS)
        except Exception as e:
            print(f"⚠️  Erreur logo : {e}")

    # Fallback : logo vectoriel SGS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S, S], radius=S // 6, fill=(240, 235, 220))
    fnt = F(int(S * 0.5), bold=True)
    letters = ["S", "G", "S"]
    pad = int(S * 0.09)
    lw = (S - 2 * pad) // 3
    for i, ch in enumerate(letters):
        bbox = d.textbbox((0, 0), ch, font=fnt)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = pad + i * lw + (lw - tw) // 2 - bbox[0]
        y = (S - th) // 2 - bbox[1]
        d.text((x, y), ch, font=fnt, fill=(15, 30, 77))
    return img


# ===== QR Code =====
def make_qr(url, size):
    """Genere un QR code."""
    if not HAS_QRCODE:
        # Fallback : carré noir avec texte
        img = Image.new("RGB", (size, size), WHITE)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, size - 1, size - 1], outline=BLACK, width=2)
        fnt = F(20, bold=False)
        draw_centered(d, "QR Code", size // 2, size // 2 - 10, fnt, GRAY)
        return img

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img.convert("RGB").resize((size, size), Image.LANCZOS)
    except Exception as e:
        print(f"⚠️  Erreur QR : {e}")
        img = Image.new("RGB", (size, size), WHITE)
        return img


# ============================================================
# AFFICHE PRINCIPALE
# ============================================================
def affiche_corporate():
    W, H = 2480, 3508  # A4 portrait @ 300 DPI

    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # ============================================================
    # 1. HEADER (bandeau bleu foncé avec titre)
    # ============================================================
    header_h = 700

    # Fond bleu foncé avec dégradé
    for y in range(header_h):
        ratio = y / header_h
        r = int(NAVY_DARK[0] + (NAVY[0] - NAVY_DARK[0]) * ratio)
        g = int(NAVY_DARK[1] + (NAVY[1] - NAVY_DARK[1]) * ratio)
        b = int(NAVY_DARK[2] + (NAVY[2] - NAVY_DARK[2]) * ratio)
        d.line([(0, y), (W, y)], fill=(r, g, b))

    # Bordure décorative cyan en bas du header
    d.rectangle([0, header_h - 8, W, header_h], fill=CYAN)

    # --- Logo à gauche ---
    logo_size = 240
    logo = make_logo(logo_size)
    logo_x = 120
    logo_y = 100
    # Cadre blanc autour du logo
    lw, lh = logo.size
    d.rectangle([logo_x - 20, logo_y - 20, logo_x + lw + 20, logo_y + lh + 20],
                fill=WHITE)
    img.paste(logo, (logo_x, logo_y), logo)

    # Sous le logo : "DATA · IA · LOGICIELS"
    fnt_tag = F(28, bold=True)
    draw_left(d, "DATA · IA · LOGICIELS", 120, logo_y + lh + 50, fnt_tag, WHITE)
    draw_left(d, "BURKINA FASO", 120, logo_y + lh + 90, fnt_tag, WHITE)

    # --- Trait vertical séparateur ---
    d.rectangle([700, 100, 704, header_h - 100], fill=(255, 255, 255, 50))

    # --- "ENTREPRISES D'AFRIQUE DE L'OUEST" en haut à droite ---
    fnt_overline = F(38, bold=True)
    d.text((780, 110), "ENTREPRISES D'AFRIQUE DE L'OUEST", font=fnt_overline, fill=ORANGE)

    # --- Titre principal ---
    fnt_title = F(120, bold=True)
    d.text((780, 200), "PASSEZ À L'ACTION", font=fnt_title, fill=WHITE)
    d.text((780, 340), "AVEC LA DATA !", font=fnt_title, fill=CYAN)

    # --- Sous-titre ---
    fnt_sub = F(42, bold=False)
    d.text((780, 510), "Votre partenaire stratégique pour valoriser vos données et", font=fnt_sub, fill=(200, 210, 230))
    d.text((780, 570), "booster votre croissance et vous faire gagner du temps.", font=fnt_sub, fill=(200, 210, 230))

    # ============================================================
    # 2. SECTION SERVICES (grille 2 colonnes)
    # ============================================================
    y_cur = header_h + 60

    # Titre "Nos Solutions & Services"
    fnt_sec = F(72, bold=True)
    d.text((120, y_cur), "Nos Solutions & Services", font=fnt_sec, fill=NAVY)

    # Sous-titre à droite
    fnt_sub2 = F(32, bold=False)
    txt_right = "Un accompagnement sur tout le cycle de vie de la donnée"
    bbox = d.textbbox((0, 0), txt_right, font=fnt_sub2)
    w_r = bbox[2] - bbox[0]
    d.text((W - 120 - w_r, y_cur + 30), txt_right, font=fnt_sub2, fill=GRAY_DARK)

    # Ligne décorative sous le titre
    d.rectangle([120, y_cur + 100, 700, y_cur + 108], fill=ORANGE)

    y_cur += 160

    # --- 6 services en grille ---
    services = [
        ("Collecte & Qualité des Données",
         "Structuration et fiabilisation de vos données."),
        ("Nettoyage & Préparation",
         "Données prêtes à l'analyse, suppression des doublons."),
        ("Analyse & Interprétation",
         "Transformez vos chiffres en décisions."),
        ("Formations Data & IA",
         "Data Analyst, Data Engineer, Data Scientist."),
        ("Formations IA",
         "Prompt Engineering, Agents IA, Marketing digital, génération vidéo."),
        ("Logiciels Personnalisés",
         "Dashboard et Cas d'usage IA. Suivi de vos KPI en temps réel."),
    ]

    # Dimensions de la grille
    col_gap = 40
    row_gap = 60
    card_w = (W - 240 - col_gap) // 2
    card_h = 220

    for i, (title, desc) in enumerate(services):
        col = i % 2
        row = i // 2

        x = 120 + col * (card_w + col_gap)
        y = y_cur + row * (card_h + row_gap)

        # --- Numéro orange (01, 02, ...) ---
        fnt_num = F(52, bold=True)
        d.text((x, y), f"0{i+1}", font=fnt_num, fill=ORANGE)

        # --- Mini-visuel à droite du numéro (rectangle coloré) ---
        vis_x = x + 120
        vis_y = y - 10
        vis_w = 200
        vis_h = 120
        # Rectangle stylisé avec dégradé
        for k in range(vis_h):
            ratio = k / vis_h
            r = int(NAVY[0] + (CYAN[0] - NAVY[0]) * ratio * 0.5)
            g = int(NAVY[1] + (CYAN[1] - NAVY[1]) * ratio * 0.5)
            b = int(NAVY[2] + (CYAN[2] - NAVY[2]) * ratio * 0.5)
            d.line([(vis_x, vis_y + k), (vis_x + vis_w, vis_y + k)], fill=(r, g, b))
        # Petites icônes stylisées dans le rectangle
        d.rectangle([vis_x + 20, vis_y + 20, vis_x + vis_w - 20, vis_y + 40], fill=CYAN)
        d.rectangle([vis_x + 20, vis_y + 55, vis_x + vis_w - 60, vis_y + 70], fill=ORANGE)
        d.rectangle([vis_x + 20, vis_y + 85, vis_x + vis_w - 40, vis_y + 100], fill=WHITE)

        # --- Titre du service ---
        fnt_title_svc = F(40, bold=True)
        d.text((x + 350, y), title, font=fnt_title_svc, fill=NAVY)

        # --- Description ---
        fnt_desc = F(30, bold=False)
        # Wrap manuel de la description
        words = desc.split()
        line = ""
        line_y = y + 55
        for word in words:
            test = line + " " + word if line else word
            bbox = d.textbbox((0, 0), test, font=fnt_desc)
            if bbox[2] - bbox[0] > card_w - 360 and line:
                d.text((x + 350, line_y), line, font=fnt_desc, fill=GRAY_DARK)
                line = word
                line_y += 40
            else:
                line = test
        if line:
            d.text((x + 350, line_y), line, font=fnt_desc, fill=GRAY_DARK)

    y_cur += 3 * (card_h + row_gap) + 40

    # ============================================================
    # 3. SECTION "ILS NOUS FONT CONFIANCE"
    # ============================================================
    d.text((120, y_cur), "Ils nous font confiance", font=F(60, bold=True), fill=NAVY)
    y_cur += 100

    # Grille de logos clients (placeholders)
    logos_count = 10
    logo_w = (W - 240 - 9 * 20) // 10
    logo_h = 120

    for i in range(logos_count):
        lx = 120 + i * (logo_w + 20)
        ly = y_cur

        # Cadre
        d.rectangle([lx, ly, lx + logo_w, ly + logo_h], fill=WHITE,
                    outline=(220, 220, 220), width=2)

        # Texte placeholder (le nom de votre client ou un carré coloré)
        colors = [ORANGE, CYAN, NAVY, (150, 200, 100), (200, 100, 150),
                  (100, 150, 200), (220, 180, 50), (180, 180, 180),
                  (100, 100, 200), (200, 120, 80)]
        # Cercle coloré stylisé
        ccx = lx + logo_w // 2
        ccy = ly + logo_h // 2
        d.ellipse([ccx - 30, ccy - 30, ccx + 30, ccy + 30], fill=colors[i % len(colors)])

    y_cur += logo_h + 60

    # ============================================================
    # 4. BANDEAU ÉVÉNEMENT / CTA (bleu clair + bouton orange)
    # ============================================================
    event_h = 320

    # Fond bleu clair
    d.rectangle([0, y_cur, W, y_cur + event_h], fill=(30, 130, 200))

    # Bloc blanc à gauche (logo événement)
    d.rectangle([80, y_cur + 40, 480, y_cur + event_h - 40], fill=WHITE)

    # Texte dans le bloc blanc : "Grand Salon de la Data"
    fnt_evt = F(40, bold=True)
    d.text((110, y_cur + 80), "Grand Salon", font=fnt_evt, fill=ORANGE)
    d.text((110, y_cur + 130), "de la Data", font=fnt_evt, fill=NAVY)
    fnt_evt_sub = F(24, bold=False)
    d.text((110, y_cur + 190), "ORGANISÉ PAR STRATEGIS", font=fnt_evt_sub, fill=GRAY_DARK)

    # --- Texte à droite ---
    d.text((540, y_cur + 60), "NOTRE ÉVÉNEMENT",
           font=F(28, bold=True), fill=WHITE)
    d.text((540, y_cur + 110), "Organisateur du Grand Salon de la Data",
           font=F(42, bold=True), fill=WHITE)
    d.text((540, y_cur + 165), "Le rendez-vous panafricain de la data et de l'IA",
           font=F(30, bold=False), fill=(220, 230, 245))

    # --- Bouton orange à droite ---
    btn_w = 500
    btn_h = 100
    btn_x = W - 120 - btn_w
    btn_y = y_cur + (event_h - btn_h) // 2
    d.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
                        radius=10, fill=ORANGE)
    # Texte bouton
    fnt_btn = F(36, bold=True)
    draw_centered(d, "EN SAVOIR PLUS", btn_x + btn_w // 2, btn_y + 15, fnt_btn, WHITE)
    fnt_btn_sub = F(28, bold=False)
    draw_centered(d, "strategis-of.netlify.app", btn_x + btn_w // 2, btn_y + 60,
                  fnt_btn_sub, WHITE)

    y_cur += event_h + 60

    # ============================================================
    # 5. BANDEAU "CONTACTEZ-NOUS" ORANGE
    # ============================================================
    cta_h = 140
    d.rectangle([80, y_cur, W - 80, y_cur + cta_h], fill=ORANGE)

    fnt_cta = F(60, bold=True)
    draw_centered(d, "Contactez-nous pour une consultation gratuite !",
                  W // 2, y_cur + 40, fnt_cta, WHITE)

    y_cur += cta_h + 50

    # ============================================================
    # 6. BLOC CONTACT (3 colonnes + QR code)
    # ============================================================
    contact_top = y_cur

    # --- Colonne 1 : Téléphone ---
    fnt_label = F(28, bold=True)
    fnt_value = F(32, bold=False)

    d.text((120, contact_top), "TÉLÉPHONE", font=fnt_label, fill=ORANGE)
    d.text((120, contact_top + 50), "+226 55 87 49 51", font=fnt_value, fill=NAVY)
    d.text((120, contact_top + 95), "+226 XX XX XX XX", font=fnt_value, fill=GRAY)

    # --- Colonne 2 : Email ---
    d.text((900, contact_top), "EMAIL", font=fnt_label, fill=ORANGE)
    d.text((900, contact_top + 50), "strategisobf@gmail.com", font=fnt_value, fill=NAVY)

    # --- Colonne 3 : Site web ---
    d.text((1650, contact_top), "SITE WEB", font=fnt_label, fill=ORANGE)
    d.text((1650, contact_top + 50), "strategis-of.netlify.app", font=fnt_value, fill=NAVY)

    # --- QR Code à droite ---
    qr_size = 260
    qr_x = W - 120 - qr_size
    qr_y = contact_top - 20
    qr_img = make_qr("https://strategis-of.netlify.app", qr_size)
    img.paste(qr_img, (qr_x, qr_y))

    # Texte sous le QR
    fnt_qr = F(24, bold=False)
    draw_centered(d, "Visiter notre site web", qr_x + qr_size // 2,
                  qr_y + qr_size + 15, fnt_qr, GRAY_DARK)

    y_cur = contact_top + 350

    # ============================================================
    # 7. FOOTER NOIR
    # ============================================================
    footer_top = H - 400
    d.rectangle([0, footer_top, W, H], fill=(15, 20, 35))

    # --- Logo + Nom ---
    logo_footer = make_logo(160)
    img.paste(logo_footer, (120, footer_top + 80), logo_footer)

    fnt_footer_name = F(52, bold=True)
    d.text((320, footer_top + 90), "StrateGis", font=fnt_footer_name, fill=WHITE)

    fnt_footer_sub = F(28, bold=False)
    d.text((320, footer_top + 155), "Développement Web, Mobile & IA", font=fnt_footer_sub, fill=CYAN)

    # --- Coordonnées au centre ---
    fnt_footer_label = F(26, bold=True)
    fnt_footer_val = F(28, bold=False)

    col2_x = 900
    d.text((col2_x, footer_top + 80), "COORDONNÉES", font=fnt_footer_label, fill=ORANGE)
    d.text((col2_x, footer_top + 130), "+226 55 87 49 51", font=fnt_footer_val, fill=WHITE)
    d.text((col2_x, footer_top + 175), "strategisobf@gmail.com", font=fnt_footer_val, fill=WHITE)
    d.text((col2_x, footer_top + 220), "Ouagadougou, Burkina Faso", font=fnt_footer_val, fill=(200, 200, 200))

    # --- Suivez-nous ---
    col3_x = 1750
    d.text((col3_x, footer_top + 80), "SUIVEZ-NOUS", font=fnt_footer_label, fill=ORANGE)

    # Icônes réseaux sociaux (cercles)
    socials = ["f", "in", "X", "◎", "◉"]
    for i, s in enumerate(socials):
        cx = col3_x + 30 + i * 70
        cy = footer_top + 160
        d.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], fill=CYAN)
        fnt_soc = F(36, bold=True)
        draw_centered(d, s, cx, cy - 22, fnt_soc, (15, 20, 35))

    # Site web en bas à droite
    fnt_url = F(28, bold=False)
    d.text((col3_x, footer_top + 220), "strategis-of.netlify.app", font=fnt_url, fill=CYAN)

    # ============================================================
    # Sauvegarde
    # ============================================================
    out = OUT_DIR / "affiche-corporate.png"
    img.save(out, "PNG", optimize=True)
    size_kb = out.stat().st_size // 1024
    print(f"   OK  {out.name} ({W}x{H}, {size_kb} Ko)")

    return out


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("STRATEGIS — Affiche corporate professionnelle")
    print("=" * 60)
    print(f"Format   : A4 portrait @ 300 DPI (2480x3508)")
    print(f"Logo     : {IMG_DIR / 'logo.png'}")
    print(f"Sortie   : {OUT_DIR}")
    print()

    if not (IMG_DIR / "logo.png").exists():
        print("⚠️  Logo non trouvé → un logo vectoriel sera utilisé")
    if not HAS_QRCODE:
        print("⚠️  Module 'qrcode' non installé → QR code simplifié")

    print()
    print("Génération de l'affiche...")
    out = affiche_corporate()

    print()
    print("=" * 60)
    print("SUCCÈS !")
    print("=" * 60)
    print()
    print(f"Affiche créée : {out.name}")
    print(f"Dimensions    : 2480x3508 pixels (A4 @ 300 DPI)")
    print(f"Taille        : {out.stat().st_size // 1024} Ko")
    print()
    print("💡 Imprimez en A4 ou partagez sur les réseaux")
    print(f"📁 Dossier : {OUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERREUR : {e}")
        import traceback
        traceback.print_exc()