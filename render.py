#!/usr/bin/env python3
"""Render v11 entry.png for make.fun news-image-20261120. Written from scratch.
Mechanics like v10 (big masthead date, editor note, UTC timeline, 2x2 big-scene
leads, illustrated cards, SOURCE label per story, DATE CHECK footer) plus a
compact 2-column list of all 32 also-on stories, so all 48 verified Friday
20 November 2026 stories are used. No external images, no network, no reading
of any previous build's files. Deterministic output.

Run: python3 render.py  -> writes entry.png next to this file.
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
NAVY = (20, 33, 61)
GOLD = (224, 169, 46)
PAPER = (247, 243, 234)
CARD_BG = (255, 255, 255)
INK = (26, 26, 26)
GRAY = (102, 102, 102)
LINE = (203, 196, 180)
TL_BG = (238, 234, 224)
PINK_BG = (250, 232, 232)
PINK_BD = (178, 58, 58)
PINK_TX = (122, 30, 30)

FDIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


F_TITLE = font("DejaVuSerif-Bold.ttf", 44)
F_DATE = font("DejaVuSans-Bold.ttf", 30)
F_RIGHT = font("DejaVuSans-Bold.ttf", 20)
F_RIGHT2 = font("DejaVuSans-Bold.ttf", 14)
F_NOTE = font("DejaVuSans.ttf", 13)
F_TL = font("DejaVuSans-Bold.ttf", 12)
F_LH = font("DejaVuSans-Bold.ttf", 20)
F_LD = font("DejaVuSans.ttf", 12)
F_LS = font("DejaVuSans-Bold.ttf", 10)
F_CH = font("DejaVuSans-Bold.ttf", 12)
F_CD = font("DejaVuSans.ttf", 10)
F_CS = font("DejaVuSans-Bold.ttf", 9)
F_AH = font("DejaVuSans-Bold.ttf", 12)
F_AO = font("DejaVuSans.ttf", 10)
F_DC = font("DejaVuSans.ttf", 10)
F_CHIP = font("DejaVuSans-Bold.ttf", 22)


def wrap(text, f, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(text, f, maxw, maxlines, what):
    lines = wrap(text, f, maxw)
    if len(lines) > maxlines:
        raise AssertionError(
            "%s: %d lines > %d: %r -> %r" % (what, len(lines), maxlines, text, lines)
        )
    return lines


# ---------------------------------------------------------------- scenes: leads (160x164)
def sc_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(13, 20, 44))
    for sx, sy in [(20, 18), (60, 10), (110, 22), (140, 12), (35, 40), (95, 30)]:
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(255, 255, 255))
    d.ellipse([x + w - 42, y + 8, x + w - 12, y + 38], fill=(240, 230, 180))
    d.ellipse([x + w - 34, y + 4, x + w - 4, y + 34], fill=(13, 20, 44))
    for bx, tx, ty in [(30, 70, 55), (80, 120, 40), (125, 95, 60)]:
        d.line([x + bx, y + h - 45, x + tx, y + ty], fill=GOLD, width=3)
        cx, cy = x + tx, y + ty
        for ang in range(0, 360, 45):
            ex = cx + 9 * math.cos(math.radians(ang))
            ey = cy + 9 * math.sin(math.radians(ang))
            d.line([cx, cy, ex, ey], fill=(255, 180, 60), width=2)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 200, 90))
    d.rectangle([x + 8, y + h - 52, x + 52, y + h], fill=(8, 12, 26))
    d.rectangle([x + 60, y + h - 40, x + 104, y + h], fill=(10, 14, 30))
    d.rectangle([x + 112, y + h - 58, x + w - 8, y + h], fill=(8, 12, 26))
    for wx, wy in [(16, h - 44), (30, h - 36), (70, h - 32), (86, h - 24),
                   (120, h - 48), (136, h - 38)]:
        d.rectangle([x + wx, y + wy, x + wx + 5, y + wy + 6], fill=(255, 210, 90))
    d.ellipse([x + w - 52, y + h - 38, x + w - 16, y + h - 2], fill=(255, 120, 30))


def sc_sanctions(d, x, y, w, h):
    # Treasury sanctions: oil barrel + official document with seal + ban sign.
    # Honest scene: paperwork and prohibition, NOT an attack.
    d.rectangle([x, y, x + w, y + h], fill=(38, 48, 58))
    # white document, right side
    d.rectangle([x + 102, y + 26, x + 150, y + 118], fill=(245, 243, 235))
    d.polygon([(x + 150, y + 26), (x + 150, y + 44), (x + 132, y + 26)],
              fill=(210, 206, 196))
    for ly in (40, 52, 64, 76):
        d.line([x + 110, y + ly, x + 142, y + ly], fill=(140, 140, 140), width=2)
    d.ellipse([x + 112, y + 88, x + 140, y + 116], fill=(178, 40, 40))
    d.ellipse([x + 120, y + 96, x + 132, y + 108], fill=(224, 169, 46))
    # black oil barrel, left side
    d.rectangle([x + 16, y + 58, x + 76, y + 140], fill=(16, 16, 16))
    d.ellipse([x + 16, y + 50, x + 76, y + 66], fill=(40, 40, 40))
    d.line([x + 16, y + 82, x + 76, y + 82], fill=(70, 70, 70), width=3)
    d.line([x + 16, y + 112, x + 76, y + 112], fill=(70, 70, 70), width=3)
    # red ban circle + slash over the barrel only
    cx, cy, r = x + 46, y + 100, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(214, 48, 48), width=8)
    d.line([cx - 30, cy + 30, cx + 30, cy - 30], fill=(214, 48, 48), width=8)


def sc_nasdaq(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 16, 22))
    # 1 green candle then 5 red candles falling
    candles = [(14, 62, 22, True), (38, 78, 26, False), (62, 92, 30, False),
               (86, 108, 26, False), (110, 122, 30, False), (134, 138, 26, False)]
    for cx, top, ch, green in candles:
        col = (60, 180, 90) if green else (224, 60, 50)
        d.rectangle([x + cx, y + top, x + cx + 14, y + top + ch], fill=col)
        d.line([x + cx + 7, y + top - 8, x + cx + 7, y + top + ch + 8],
               fill=col, width=2)
    # big red down arrow
    d.polygon([(x + 118, y + 34), (x + 152, y + 34), (x + 152, y + 96),
               (x + 160, y + 96), (x + 135, y + 128), (x + 110, y + 96),
               (x + 118, y + 96)], fill=(224, 60, 50))
    # trading-floor silhouette
    d.rectangle([x + 8, y + h - 16, x + w - 8, y + h], fill=(40, 40, 52))
    for bx in (16, 48, 84):
        d.rectangle([x + bx, y + h - 30, x + bx + 18, y + h - 16],
                    fill=(60, 60, 76))


def sc_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 58, 110))
    flag_cols = [(214, 48, 48), (240, 240, 240), (40, 140, 70),
                 (240, 200, 40), (40, 80, 200), (214, 48, 48)]
    for i, col in enumerate(flag_cols):
        d.rectangle([x + 12 + i * 24, y + 10, x + 30 + i * 24, y + 26], fill=col)
    # globe
    d.ellipse([x + 52, y + 38, x + 108, y + 94], fill=(70, 160, 220))
    d.ellipse([x + 62, y + 48, x + 78, y + 62], fill=(80, 180, 100))
    d.ellipse([x + 84, y + 66, x + 100, y + 82], fill=(80, 180, 100))
    # delegates: rows of tables + heads
    for ty in (108, 128):
        d.rectangle([x + 10, y + ty, x + w - 10, y + ty + 10], fill=(150, 110, 60))
        for hx in (24, 52, 80, 108, 136):
            d.ellipse([x + hx, y + ty - 12, x + hx + 12, y + ty], fill=(235, 210, 170))


# ---------------------------------------------------------------- scenes: cards (76x94)
def sc_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(28, 90, 160))
    d.arc([x + 8, y + 6, x + 68, y + 66], 0, 270, fill=(255, 255, 255), width=4)
    d.arc([x + 18, y + 16, x + 58, y + 56], 90, 360, fill=(255, 255, 255), width=4)
    d.arc([x + 28, y + 26, x + 48, y + 46], 180, 450, fill=(255, 255, 255), width=4)
    d.ellipse([x + 34, y + 32, x + 42, y + 40], fill=(220, 235, 255))
    d.polygon([(x, y + 78), (x + w, y + 68), (x + w, y + h), (x, y + h)],
              fill=(60, 140, 80))
    for rx, ry in [(56, 10), (64, 20), (50, 24)]:
        d.line([x + rx, y + ry, x + rx - 4, y + ry + 8], fill=(200, 220, 255),
               width=2)


def sc_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 18, 18))
    d.ellipse([x + 12, y + 12, x + 64, y + 64], fill=(224, 169, 46))
    d.ellipse([x + 18, y + 18, x + 58, y + 58], outline=(180, 130, 20), width=2)
    f = font("DejaVuSans-Bold.ttf", 32)
    d.text((x + 27, y + 20), "B", font=f, fill=(120, 70, 0))
    d.polygon([(x + 56, y + 58), (x + 68, y + 58), (x + 68, y + 66),
               (x + 64, y + 66), (x + 64, y + 82), (x + 58, y + 82),
               (x + 58, y + 66), (x + 52, y + 66)], fill=(224, 60, 50))


def sc_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(120, 170, 210))
    d.rectangle([x, y + 58, x + w, y + h], fill=(20, 60, 110))
    for cx, cy, r in [(30, 26, 9), (42, 20, 11), (54, 28, 8)]:
        d.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                  fill=(110, 110, 110))
    d.ellipse([x + 34, y + 30, x + 50, y + 46], fill=(255, 140, 40))
    d.rectangle([x + 14, y + 44, x + 26, y + 56], fill=(214, 48, 48))
    d.rectangle([x + 28, y + 44, x + 40, y + 56], fill=(40, 80, 200))
    d.rectangle([x + 42, y + 44, x + 54, y + 56], fill=(240, 200, 40))
    d.polygon([(x + 8, y + 56), (x + 68, y + 56), (x + 62, y + 74),
               (x + 14, y + 74)], fill=(12, 12, 12))


def sc_houthi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 170, 120))
    d.rectangle([x + 12, y + 20, x + 18, y + 86], fill=(60, 50, 40))
    d.line([x + 14, y + 22, x + 66, y + 44], fill=(60, 50, 40), width=4)
    d.line([x + 66, y + 44, x + 66, y + 54], fill=(60, 50, 40), width=2)
    d.polygon([(x + 20, y + 66), (x + 58, y + 34), (x + 64, y + 40),
               (x + 26, y + 72)], fill=(245, 245, 245))
    d.polygon([(x + 58, y + 34), (x + 68, y + 30), (x + 64, y + 40)],
              fill=(200, 40, 40))
    d.ellipse([x + 8, y + 78, x + 16, y + 86], fill=(255, 180, 60))


def sc_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 50, 140))
    cx, cy, r = x + 38, y + 44, 26
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        sx = cx + r * math.cos(ang)
        sy = cy + r * math.sin(ang)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)
    f = font("DejaVuSans-Bold.ttf", 34)
    d.text((x + 26, y + 26), "€", font=f, fill=GOLD)


def sc_candle(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 20, 40))
    d.rectangle([x + 26, y + 42, x + 38, y + 84], fill=(245, 243, 235))
    d.line([x + 32, y + 36, x + 32, y + 42], fill=(120, 120, 120), width=2)
    d.ellipse([x + 26, y + 22, x + 38, y + 38], fill=(255, 200, 60))
    d.ellipse([x + 29, y + 28, x + 35, y + 38], fill=(255, 120, 30))
    for px, py in [(56, 62), (66, 70), (56, 78), (46, 70)]:
        d.ellipse([x + px - 5, y + py - 5, x + px + 5, y + py + 5],
                  fill=(230, 120, 160))
    d.ellipse([x + 51, y + 65, x + 61, y + 75], fill=(255, 200, 60))


def sc_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 210, 190))
    d.polygon([(x + 8, y + 22), (x + 68, y + 22), (x + 38, y + 8)],
              fill=(245, 243, 235))
    for cx in (16, 32, 48):
        d.rectangle([x + cx, y + 26, x + cx + 8, y + 70], fill=(245, 243, 235))
    d.rectangle([x + 8, y + 70, x + 68, y + 78], fill=(200, 185, 160))
    d.rectangle([x + 48, y + 80, x + 68, y + 86], fill=(120, 80, 40))
    d.line([x + 58, y + 80, x + 66, y + 66], fill=(120, 80, 40), width=3)


def sc_tesla(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 200, 205))
    d.polygon([(x + 38, y + 6), (x + 48, y + 26), (x + 42, y + 26),
               (x + 52, y + 46), (x + 34, y + 24), (x + 40, y + 24)],
              fill=(240, 200, 40))
    d.rectangle([x + 10, y + 56, x + 66, y + 72], fill=(200, 40, 40))
    d.polygon([(x + 22, y + 56), (x + 28, y + 44), (x + 48, y + 44),
               (x + 54, y + 56)], fill=(200, 40, 40))
    for wx in (18, 52):
        d.ellipse([x + wx, y + 70, x + wx + 12, y + 82], fill=(20, 20, 20))
    d.rectangle([x, y + 84, x + w, y + h], fill=(90, 90, 95))


def sc_ronaldo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 140, 70))
    d.rectangle([x + 44, y + 12, x + 70, y + 46], outline=(255, 255, 255),
                width=3)
    for gx in (52, 60):
        d.line([x + gx, y + 12, x + gx, y + 46], fill=(255, 255, 255), width=1)
    d.line([x + 44, y + 29, x + 70, y + 29], fill=(255, 255, 255), width=1)
    d.ellipse([x + 14, y + 48, x + 22, y + 56], fill=(20, 20, 20))
    d.line([x + 18, y + 56, x + 18, y + 70], fill=(20, 20, 20), width=3)
    d.line([x + 18, y + 62, x + 30, y + 56], fill=(20, 20, 20), width=3)
    d.line([x + 18, y + 70, x + 10, y + 80], fill=(20, 20, 20), width=3)
    d.line([x + 18, y + 70, x + 28, y + 78], fill=(20, 20, 20), width=3)
    d.ellipse([x + 30, y + 76, x + 38, y + 84], fill=(255, 255, 255))


def sc_peru(d, x, y, w, h):
    # HONEST scene: building stands STRAIGHT, one small crack on the wall only,
    # flat ground, NO ground cracks, NO leaning, NO collapse.
    d.rectangle([x, y, x + w, y + h], fill=(225, 215, 195))
    d.rectangle([x + 16, y + 16, x + 60, y + 88], fill=(150, 140, 125))
    d.rectangle([x + 16, y + 16, x + 60, y + 24], fill=(120, 110, 95))
    for wy in (30, 44, 58, 72):
        for wx in (22, 34, 46):
            d.rectangle([x + wx, y + wy, x + wx + 7, y + wy + 8],
                        fill=(60, 60, 70))
    # one small thin crack on the wall face only (light damage)
    d.line([x + 40, y + 34, x + 44, y + 42, x + 40, y + 50],
           fill=(80, 70, 60), width=1)
    # flat ground line, no cracks
    d.line([x, y + 88, x + w, y + 88], fill=(90, 80, 65), width=3)
    d.rectangle([x + 62, y + 84, x + 68, y + 88], fill=(120, 110, 95))


def sc_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 230))
    d.rectangle([x + 6, y + 20, x + 36, y + 44], fill=(20, 50, 140))
    for sx, sy in [(12, 26), (21, 24), (30, 26), (12, 38), (21, 40), (30, 38)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=GOLD)
    d.rectangle([x + 40, y + 20, x + 70, y + 44], fill=(30, 60, 140))
    d.line([x + 40, y + 32, x + 70, y + 32], fill=(255, 255, 255), width=4)
    d.line([x + 55, y + 20, x + 55, y + 44], fill=(255, 255, 255), width=4)
    d.line([x + 40, y + 32, x + 70, y + 32], fill=(200, 40, 40), width=2)
    d.line([x + 55, y + 20, x + 55, y + 44], fill=(200, 40, 40), width=2)
    d.arc([x + 12, y + 56, x + 64, y + 84], 200, 340, fill=(40, 140, 70),
          width=4)


def sc_un(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(180, 210, 235))
    d.ellipse([x + 8, y + 14, x + 40, y + 46], fill=(50, 130, 210))
    d.ellipse([x + 16, y + 20, x + 26, y + 30], fill=(80, 180, 100))
    d.ellipse([x + 26, y + 32, x + 36, y + 42], fill=(80, 180, 100))
    d.rectangle([x + 44, y + 52, x + 68, y + 82], fill=(30, 50, 110))
    d.line([x + 50, y + 52, x + 62, y + 52], fill=(240, 240, 240), width=3)
    d.rectangle([x + 52, y + 38, x + 60, y + 52], fill=(245, 245, 245))


# ---------------------------------------------------------------- content
LEADS = [
    dict(scene=sc_kyiv, chip="110+",
         title="110+ MISSILES HIT KYIV IN BIGGEST RAID",
         detail="27 ballistic missiles + 400 drones overnight; 9 killed; "
                "3 Dnipro bridges hit; debris over Poland.",
         source="CNN · REUTERS"),
    dict(scene=sc_sanctions, chip="4",
         title="US SANCTIONS IRAN 'OIL TRUSTEES'",
         detail="Treasury's Operation Economic Outcast sanctions 4 'oil "
                "trustees': Bavand, Taj, Servati, Arabnejad.",
         source="TREASURY"),
    dict(scene=sc_nasdaq, chip="-5.3%",
         title="NASDAQ -5.3%: WORST WEEK SINCE APRIL 2025",
         detail="S&P -3.7%, 7th straight loss; Nvidia -14% on SEC probe; "
                "Nikkei -5.1%; VIX 35.89.",
         source="INVESTOPEDIA · CNN"),
    dict(scene=sc_cop31, chip="35%",
         title="COP31 IN OVERTIME ON FOSSIL FUELS",
         detail="Panama threatens block without fossil-fuel language; "
                "12 nations write; draft keeps 35% electricity by 2035.",
         source="REUTERS"),
]

CARDS = [
    dict(scene=sc_akvan, title="CYCLONE AKVAN SLAMS INDIA",
         detail="300,000+ evacuated; 1,300+ babies born in shelters.",
         source="IMD · THE HINDU"),
    dict(scene=sc_bitcoin, title="BITCOIN BELOW $60,000",
         detail="First since July; low $57,778; close ~$58,317.",
         source="REUTERS"),
    dict(scene=sc_tanker, title="TANKER HIT OFF OMAN",
         detail="Off Khasab: fire, no casualties; mine claim disputed.",
         source="UKMTO · REUTERS"),
    dict(scene=sc_houthi, title="HOUTHI THREAT TO SAUDI PORTS",
         detail="Threat if coalition hits Hodeidah; strikes Yemen.",
         source="REUTERS"),
    dict(scene=sc_eu, title="EU: €1BN NEW MILITARY AID",
         detail="Via EPF, part of €6.6bn deal; delivery by end of 2027.",
         source="EU COUNCIL"),
    dict(scene=sc_candle, title="MLAMBO-NGCUKA DIES, 71",
         detail="Ex-deputy president dies Friday; announced late Friday.",
         source="PRESIDENCY ZA"),
    dict(scene=sc_court, title="SYDNEY: ALLEGED ISIS PLOT CHARGE",
         detail="Amin, 35, charged Friday; alleged ISIS bomb research.",
         source="AFP · AAP"),
    dict(scene=sc_tesla, title="ITALY: FIRST MAJOR EU TESLA APPROVAL",
         detail="Temporary approval for Tesla driving system.",
         source="REUTERS"),
    dict(scene=sc_ronaldo, title="RONALDO'S 986TH GOAL",
         detail="Minute 14, Al-Ahli 3-1 Al-Nassr. (SPL tally.)",
         source="ESPN"),
    dict(scene=sc_peru, title="PERU SHAKEN BY M6.7 QUAKE",
         detail="19:09 local near Junín, 108 km deep; no casualties.",
         source="AP"),
    dict(scene=sc_flags, title="EU-UK TRADE DEAL STRUCK",
         detail="Trade barriers fall; youth mobility 100,000 each side.",
         source="AP"),
    dict(scene=sc_un, title="UN CHIEF RACE: 2 VETOES",
         detail="Grynspan leads 10-4 in 9th poll; vetoes undisclosed.",
         source="REUTERS"),
]

# 32 also-on, one short line each (source included). A28 framed as a CLAIM.
ALSO_ON = [
    ("A1", "Estonia closes Russia road crossings from Dec 1 — Reuters / AP"),
    ("A2", "US–China: humans must decide military AI — Reuters"),
    ("A3", "Japan: 93% say Japan–China ties bad, worst since 1986 — Cabinet Office / Kyodo"),
    ("A4", "SCO forum opens in Delhi; first Pakistan minister visit in 3 years — PTI"),
    ("A5", "Canada, Australia, NZ: joint call for unconditional ceasefire — Global Affairs Canada"),
    ("A6", "Iraq retakes Kataeb Hezbollah base without resistance — AFP / Reuters"),
    ("A7", "Nvidia −14%, ~$491bn wiped; SEC probes its accounting — Reuters"),
    ("A8", "Xi meets Albanese in Shenzhen; ties in “full turnaround” — Xinhua / People's Daily"),
    ("A9", "ECB: Boone & Brunnermeier picked for top jobs — Eurogroup"),
    ("A10", "BYD Ti7 banned in EU over Defender design — Reuters"),
    ("A11", "Tesla opens first Argentina store in Buenos Aires — Reuters"),
    ("A12", "Las Vegas GP: Russell fastest in FP3 — Reuters / formula1.com"),
    ("A13", "Gold −2.4% to $3,538, lowest since September — Reuters"),
    ("A14", "Michigan sentiment 51.5; Bessent warns the Fed — Univ. of Michigan / CNBC"),
    ("A15", "Tesla plans $3.1bn polysilicon plant in Texas — Reuters"),
    ("A16", "Russian missiles enter Polish airspace — Reuters / CNN"),
    ("A17", "Kyiv hits 3 Russian launchers and Smolensk plant — ISW"),
    ("A18", "South Africa crime stats: 5,590 murders in a quarter — BBC / SAPS"),
    ("A19", "Venezuela rejects ICJ ruling on Esequibo — CANA News"),
    ("A20", "KOSPI −5.2% to 4,869.96, lowest since January — AJP"),
    ("A21", "Brent +0.6% to $92.57, third weekly loss — Morningstar"),
    ("A22", "SpaceX launches secret USSF-317 mission — Spaceflight Now"),
    ("A23", "OpenAI: new usage policy takes effect today — OpenAI"),
    ("A24", "Island nations: COP31 “a failure” if 1.5°C ignored — finwire / Guardian"),
    ("A25", "Tech rout: Broadcom −12%, AMD −13%, Meta −6% — Motley Fool"),
    ("A26", "Anthropic −8.5% a day after record IPO — Reuters"),
    ("A27", "“Chapo Isidro” arrested in Mexico after shootout — CNN / NY Post"),
    ("A28", "Iran claims 14 tankers at Kharg; trackers dispute it — Hamshahri / Fars / ISW"),
    ("A29", "Bolsonaro, 71, taken to hospital in Brazil — Reuters / CNN"),
    ("A30", "Brazil storm kills 3, wrecks ~5,000 homes — EIN Presswire"),
    ("A31", "Samsung names Hwang Sang-joon memory chief — Reuters / Samsung"),
    ("A32", "Sensex +1.1%, defying global rout — Moneycontrol"),
]

TIMELINE = ("02:00 AKVAN · 06:10 SYDNEY · 14:50 EU €1BN · 15:00 KHASAB · "
            "15:42 BTC <$60K · 16:35 ECB · 19:09 PERU · 21:00 NASDAQ")
DATE_CHECK = ("DATE CHECK — Every story above happened or was first reported "
              "Friday 20 Nov 2026. Deliberately dropped (wrong day): Shenzhen "
              "summit, ICJ Myanmar, US Senate 51-48, PIF Tower, Egypt-IMF, "
              "Argentina disability law, Colombia strike.")


# ---------------------------------------------------------------- layout
def draw_lead(d, x, y, w, h, item):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=CARD_BG, outline=LINE, width=1)
    item["scene"](d, x + 1, y + 1, 160, h - 2)
    chip = item["chip"]
    cw = F_CHIP.getlength(chip) + 16
    d.rectangle([x + 1, y + h - 32, x + 1 + cw, y + h - 2], fill=GOLD)
    d.text((x + 9, y + h - 30), chip, font=F_CHIP, fill=NAVY)
    tx = x + 160 + 12
    twd = x + w - 12 - tx
    lines = fit(item["title"], F_LH, twd, 2, "lead title")
    yy = y + 10
    for ln in lines:
        d.text((tx, yy), ln, font=F_LH, fill=INK)
        yy += 24
    dlines = fit(item["detail"], F_LD, twd, 3, "lead detail")
    yy += 2
    for ln in dlines:
        d.text((tx, yy), ln, font=F_LD, fill=INK)
        yy += 15
    d.text((tx, y + h - 20), "SOURCE: " + item["source"], font=F_LS, fill=GRAY)


def draw_card(d, x, y, w, h, item):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=CARD_BG, outline=LINE, width=1)
    item["scene"](d, x + 1, y + 1, 76, h - 2)
    tx = x + 76 + 8
    twd = x + w - 8 - tx
    lines = fit(item["title"], F_CH, twd, 2, "card title")
    yy = y + 6
    for ln in lines:
        d.text((tx, yy), ln, font=F_CH, fill=INK)
        yy += 15
    dlines = fit(item["detail"], F_CD, twd, 2, "card detail")
    for ln in dlines:
        d.text((tx, yy), ln, font=F_CD, fill=INK)
        yy += 13
    d.text((tx, y + h - 14), "SOURCE: " + item["source"], font=F_CS, fill=GRAY)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # masthead
    d.rectangle([0, 0, W, 86], fill=NAVY)
    d.text((16, 6), "THE FRIDAY PAPER", font=F_TITLE, fill=(255, 255, 255))
    d.text((16, 52), "FRIDAY 20 NOVEMBER 2026", font=F_DATE, fill=GOLD)
    r1 = "48 STORIES · ONE DAY"
    r2 = "OF WORLD NEWS"
    d.text((1006 - F_RIGHT.getlength(r1), 12), r1, font=F_RIGHT,
           fill=(255, 255, 255))
    d.text((1006 - F_RIGHT2.getlength(r2), 44), r2, font=F_RIGHT2,
           fill=(255, 255, 255))
    # editor note
    d.text((16, 90), "Every story below happened or was first reported on "
                     "Friday 20 November 2026.", font=F_NOTE, fill=GRAY)
    # timeline
    d.rectangle([0, 106, W, 126], fill=TL_BG)
    if F_TL.getlength(TIMELINE) > 1000:
        raise AssertionError("timeline too wide: %d" % F_TL.getlength(TIMELINE))
    d.text((16, 110), TIMELINE, font=F_TL, fill=INK)
    # leads 2x2: rows y=126 and y=298, height 164, gap 8
    lw = 500
    for i, item in enumerate(LEADS):
        lx = 8 + (i % 2) * (lw + 8)
        ly = 126 + (i // 2) * (164 + 8)
        draw_lead(d, lx, ly, lw, 164, item)
    # cards 4x3: rows y=470, 572, 674, height 94, gap 8
    cw = 246
    for i, item in enumerate(CARDS):
        cx = 8 + (i % 4) * (cw + 8)
        cy = 470 + (i // 4) * (94 + 8)
        draw_card(d, cx, cy, cw, 94, item)
    # also-on: header y=776, 16 rows of 11px from y=798
    d.text((16, 778), "ALSO ON FRIDAY — 32 MORE VERIFIED STORIES",
           font=F_AH, fill=INK)
    for i, (label, text) in enumerate(ALSO_ON):
        col = i // 16
        row = i % 16
        ax = 16 + col * 500
        ay = 800 + row * 11
        line = "%s. %s" % (label, text)
        if F_AO.getlength(line) > 488:
            raise AssertionError("also-on too wide: %r" % line)
        d.text((ax, ay), line, font=F_AO, fill=INK)
    # DATE CHECK footer
    d.rectangle([8, 980, W - 8, 1010], fill=PINK_BG, outline=PINK_BD, width=1)
    dclines = fit(DATE_CHECK, F_DC, 992, 2, "date check")
    yy = 984
    for ln in dclines:
        d.text((16, yy), ln, font=F_DC, fill=PINK_TX)
        yy += 12
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    pal = img.convert("P", palette=Image.ADAPTIVE, colors=256)
    pal.save(out, optimize=True)
    data = open(out, "rb").read()
    print("wrote %s (%dx%d, %d bytes, sha256 %s)"
          % (out, W, H, len(data), hashlib.sha256(data).hexdigest()))
    return out


if __name__ == "__main__":
    render()
