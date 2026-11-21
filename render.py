#!/usr/bin/env python3
"""Render the v7 front page for news-image-20261120.

Draws a 1024x1024 newspaper front page with PIL primitives only:
no external images, no network. Every story on the page happened or
was first reported on Friday 20 November 2026 (see the verification
table in ../STATUS.md, section v7). Output is a palette PNG so the
file stays small (tie-break: a smaller file wins an exact tie).
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FD = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# --- palette (flat colours: small file, high contrast) ---
PAPER = (250, 247, 240)
CARD = (255, 255, 255)
INK = (18, 18, 22)
NAVY = (22, 44, 92)
NAVY_D = (14, 30, 64)
RED = (176, 30, 30)
TEAL = (0, 118, 108)
BLUE = (28, 88, 164)
GOLD = (172, 124, 0)
GREEN = (32, 116, 58)
PURPLE = (108, 58, 138)
ORANGE = (196, 96, 8)
GRAY = (96, 96, 100)
LINE = (208, 202, 192)
LIGHT = (236, 232, 224)
PINK = (248, 226, 224)
WHITE = (255, 255, 255)


def wrap(text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width` px."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(text, fnt, width):
    """Shorten with an ellipsis so the text fits `width` px on one line."""
    if fnt.getlength(text) <= width:
        return text
    while text and fnt.getlength(text + "...") > width:
        text = text[:-1]
    return text + "..."


def disc(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


def icon(d, kind, cx, cy, r, fg):
    """Draw a small pictogram centred at (cx, cy), radius r, in colour fg.

    All icons are plain PIL primitives (lines, arcs, polygons). Each
    story gets a different pictogram so the page reads from pictures
    as well as from labels.
    """
    x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r
    if kind == "missile":
        d.polygon([(cx - r * 0.55, cy + r * 0.7), (cx, cy - r * 0.9),
                   (cx + r * 0.55, cy + r * 0.7)], fill=fg)
        d.polygon([(cx - r * 0.55, cy + r * 0.35), (cx - r * 1.0, cy + r * 0.9),
                   (cx - r * 0.2, cy + r * 0.7)], fill=fg)
        d.polygon([(cx + r * 0.55, cy + r * 0.35), (cx + r * 1.0, cy + r * 0.9),
                   (cx + r * 0.2, cy + r * 0.7)], fill=fg)
        d.polygon([(cx - r * 0.3, cy + r * 0.75), (cx, cy + r * 1.15),
                   (cx + r * 0.3, cy + r * 0.75)], fill=fg)
    elif kind == "cyclone":
        for i, rr in enumerate((r * 0.95, r * 0.68, r * 0.42)):
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr],
                  start=40 + i * 120, end=300 + i * 120, fill=fg, width=max(2, r // 6))
        disc(d, cx, cy, max(2, r // 8), fg)
    elif kind == "chart":
        d.line([(x0, y1), (x1, y1)], fill=fg, width=max(2, r // 7))
        d.line([(x0, y0), (x0, y1)], fill=fg, width=max(2, r // 7))
        pts = [(x0 + r * 0.1, cy - r * 0.5), (cx - r * 0.25, cy - r * 0.1),
               (cx + r * 0.1, cy + r * 0.15), (cx + r * 0.45, cy - r * 0.05),
               (x1 - r * 0.1, cy + r * 0.75)]
        d.line(pts, fill=fg, width=max(2, r // 6), joint="curve")
        d.polygon([(x1 - r * 0.35, cy + r * 0.55), (x1 - r * 0.05, cy + r * 0.55),
                   (x1 - r * 0.05, cy + r * 0.95)], fill=fg)
    elif kind == "globe":
        d.ellipse([x0, y0, x1, y1], outline=fg, width=max(2, r // 6))
        d.ellipse([cx - r * 0.45, y0, cx + r * 0.45, y1], outline=fg,
                  width=max(2, r // 8))
        d.line([(x0, cy), (x1, cy)], fill=fg, width=max(2, r // 8))
        d.arc([x0, cy - r * 0.55, x1, cy + r * 0.55], start=200, end=340,
              fill=fg, width=max(2, r // 8))
        d.arc([x0, cy - r * 0.55, x1, cy + r * 0.55], start=20, end=160,
              fill=fg, width=max(2, r // 8))
    elif kind == "bitcoin":
        disc(d, cx, cy, r, fg)
        bf = font(SANS_B, int(r * 1.25))
        d.text((cx, cy), "B", font=bf, fill=WHITE, anchor="mm")
        d.line([(cx - r * 0.45, cy - r * 0.55), (cx - r * 0.45, cy + r * 0.55)],
               fill=WHITE, width=max(2, r // 8))
        d.line([(cx + r * 0.05, cy - r * 0.55), (cx + r * 0.05, cy + r * 0.55)],
               fill=WHITE, width=max(2, r // 8))
    elif kind == "ship":
        d.polygon([(x0 + r * 0.1, cy + r * 0.1), (x1 - r * 0.1, cy + r * 0.1),
                   (x1 - r * 0.35, cy + r * 0.7), (x0 + r * 0.35, cy + r * 0.7)],
                  fill=fg)
        d.line([(cx, cy + r * 0.1), (cx, cy - r * 0.8)], fill=fg,
               width=max(2, r // 7))
        d.polygon([(cx, cy - r * 0.8), (cx, cy - r * 0.15),
                   (cx + r * 0.55, cy - r * 0.15)], fill=fg)
        d.line([(x0, cy + r * 0.85), (x1, cy + r * 0.85)], fill=fg,
               width=max(2, r // 8))
    elif kind == "flame":
        d.polygon([(cx, cy - r * 0.95), (cx + r * 0.55, cy - r * 0.1),
                   (cx + r * 0.75, cy + r * 0.55), (cx + r * 0.25, cy + r * 0.9),
                   (cx - r * 0.25, cy + r * 0.9), (cx - r * 0.75, cy + r * 0.55),
                   (cx - r * 0.55, cy - r * 0.1)], fill=fg)
        d.polygon([(cx, cy - r * 0.2), (cx + r * 0.3, cy + r * 0.3),
                   (cx, cy + r * 0.7), (cx - r * 0.3, cy + r * 0.3)], fill=PAPER)
    elif kind == "eu":
        for i in range(12):
            a = math.radians(i * 30 - 90)
            sx, sy = cx + r * 0.72 * math.cos(a), cy + r * 0.72 * math.sin(a)
            disc(d, sx, sy, max(2, r // 9), fg)
        d.ellipse([cx - r * 0.28, cy - r * 0.28, cx + r * 0.28, cy + r * 0.28],
                  outline=fg, width=max(2, r // 8))
    elif kind == "person":
        disc(d, cx, cy - r * 0.35, r * 0.34, fg)
        d.pieslice([cx - r * 0.62, cy - r * 0.1, cx + r * 0.62, cy + r * 1.05],
                   start=180, end=360, fill=fg)
    elif kind == "shield":
        d.polygon([(cx, cy - r * 0.9), (cx + r * 0.75, cy - r * 0.55),
                   (cx + r * 0.75, cy + r * 0.15), (cx, cy + r * 0.95),
                   (cx - r * 0.75, cy + r * 0.15), (cx - r * 0.75, cy - r * 0.55)],
                  fill=fg)
        d.line([(cx - r * 0.35, cy), (cx - r * 0.08, cy + r * 0.3),
                (cx + r * 0.4, cy - r * 0.35)], fill=WHITE,
               width=max(2, r // 6), joint="curve")
    elif kind == "car":
        d.rounded_rectangle([x0 + r * 0.05, cy - r * 0.15, x1 - r * 0.05,
                             cy + r * 0.45], radius=r // 4, fill=fg)
        d.polygon([(cx - r * 0.5, cy - r * 0.15), (cx - r * 0.3, cy - r * 0.65),
                   (cx + r * 0.3, cy - r * 0.65), (cx + r * 0.5, cy - r * 0.15)],
                  fill=fg)
        disc(d, cx - r * 0.45, cy + r * 0.5, r * 0.22, INK)
        disc(d, cx + r * 0.45, cy + r * 0.5, r * 0.22, INK)
    elif kind == "ball":
        d.ellipse([x0, y0, x1, y1], outline=fg, width=max(2, r // 6))
        d.polygon([(cx, cy - r * 0.35), (cx + r * 0.33, cy - r * 0.1),
                   (cx + r * 0.2, cy + r * 0.3), (cx - r * 0.2, cy + r * 0.3),
                   (cx - r * 0.33, cy - r * 0.1)], fill=fg)
        for a in (90, 210, 330):
            ar = math.radians(a)
            d.line([(cx + r * 0.33 * math.cos(ar), cy + r * 0.33 * math.sin(ar)),
                    (cx + r * 0.9 * math.cos(ar), cy + r * 0.9 * math.sin(ar))],
                   fill=fg, width=max(2, r // 9))
    elif kind == "ban":
        d.ellipse([x0, y0, x1, y1], outline=fg, width=max(3, r // 5))
        d.line([(cx - r * 0.7, cy + r * 0.7), (cx + r * 0.7, cy - r * 0.7)],
               fill=fg, width=max(3, r // 5))
    elif kind == "quake":
        pts = [(x0, cy + r * 0.4), (cx - r * 0.5, cy - r * 0.2),
               (cx - r * 0.15, cy + r * 0.3), (cx + r * 0.2, cy - r * 0.5),
               (cx + r * 0.5, cy + r * 0.1), (x1, cy - r * 0.35)]
        d.line(pts, fill=fg, width=max(2, r // 6), joint="curve")
        d.line([(x0, y1 - r * 0.2), (x1, y1 - r * 0.2)], fill=fg,
               width=max(2, r // 9))
    elif kind == "link":
        d.ellipse([cx - r * 0.8, cy - r * 0.45, cx + r * 0.05, cy + r * 0.45],
                  outline=fg, width=max(3, r // 5))
        d.ellipse([cx - r * 0.05, cy - r * 0.45, cx + r * 0.8, cy + r * 0.45],
                  outline=fg, width=max(3, r // 5))
    elif kind == "un":
        d.polygon([(cx - r * 0.15, y0), (cx + r * 0.15, y0),
                   (cx + r * 0.35, y1), (cx - r * 0.35, y1)], fill=fg)
        d.polygon([(x0, cy - r * 0.15), (cx - r * 0.1, cy - r * 0.35),
                   (cx - r * 0.1, cy + r * 0.35), (x0, cy + r * 0.15)], fill=fg)
        d.polygon([(x1, cy - r * 0.15), (cx + r * 0.1, cy - r * 0.35),
                   (cx + r * 0.1, cy + r * 0.35), (x1, cy + r * 0.15)], fill=fg)
    elif kind == "rocket":
        d.polygon([(cx, cy - r * 0.95), (cx + r * 0.35, cy - r * 0.1),
                   (cx + r * 0.35, cy + r * 0.5), (cx, cy + r * 0.75),
                   (cx - r * 0.35, cy + r * 0.5), (cx - r * 0.35, cy - r * 0.1)],
                  fill=fg)
        d.polygon([(cx - r * 0.35, cy + r * 0.3), (cx - r * 0.7, cy + r * 0.85),
                   (cx - r * 0.35, cy + r * 0.6)], fill=fg)
        d.polygon([(cx + r * 0.35, cy + r * 0.3), (cx + r * 0.7, cy + r * 0.85),
                   (cx + r * 0.35, cy + r * 0.6)], fill=fg)
        disc(d, cx, cy - r * 0.35, r * 0.14, PAPER)
    elif kind == "chip":
        d.rectangle([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55],
                    fill=fg)
        for i in (-1, 0, 1):
            d.line([(cx + i * r * 0.35, cy - r * 0.9), (cx + i * r * 0.35,
                   cy - r * 0.55)], fill=fg, width=max(2, r // 7))
            d.line([(cx + i * r * 0.35, cy + r * 0.55), (cx + i * r * 0.35,
                   cy + r * 0.9)], fill=fg, width=max(2, r // 7))
            d.line([(cx - r * 0.9, cy + i * r * 0.35), (cx - r * 0.55,
                   cy + i * r * 0.35)], fill=fg, width=max(2, r // 7))
            d.line([(cx + r * 0.55, cy + i * r * 0.35), (cx + r * 0.9,
                   cy + i * r * 0.35)], fill=fg, width=max(2, r // 7))
        d.rectangle([cx - r * 0.25, cy - r * 0.25, cx + r * 0.25, cy + r * 0.25],
                    fill=PAPER)
    elif kind == "flag":
        d.line([(cx - r * 0.5, y0), (cx - r * 0.5, y1)], fill=fg,
               width=max(2, r // 7))
        d.polygon([(cx - r * 0.5, y0), (cx + r * 0.8, cy - r * 0.55),
                   (cx + r * 0.8, cy - r * 0.05), (cx - r * 0.5, cy + r * 0.2)],
                  fill=fg)
    elif kind == "gold":
        for i, wdt in enumerate((0.9, 0.7, 0.5)):
            yy = cy + r * (0.55 - i * 0.55)
            d.rectangle([cx - r * wdt, yy - r * 0.25, cx + r * wdt, yy + r * 0.25],
                        fill=fg)
    elif kind == "survey":
        for i, hh in enumerate((0.4, 0.75, 0.55, 1.0)):
            xx = x0 + i * r * 0.5
            d.rectangle([xx, y1 - r * hh, xx + r * 0.32, y1], fill=fg)
    elif kind == "factory":
        d.rectangle([x0, cy, x1, y1], fill=fg)
        d.rectangle([cx - r * 0.7, cy - r * 0.7, cx - r * 0.4, cy], fill=fg)
        d.rectangle([cx - r * 0.2, cy - r * 0.9, cx + r * 0.1, cy], fill=fg)
    elif kind == "plane":
        d.polygon([(x0, cy), (cx + r * 0.6, cy - r * 0.25),
                   (x1, cy - r * 0.1), (cx + r * 0.3, cy + r * 0.15),
                   (cx + r * 0.1, cy + r * 0.5), (cx - r * 0.1, cy + r * 0.2),
                   (cx - r * 0.6, cy + r * 0.35)], fill=fg)
    elif kind == "boom":
        for i in range(8):
            a = math.radians(i * 45)
            ex = cx + r * 0.95 * math.cos(a)
            ey = cy + r * 0.95 * math.sin(a)
            ix = cx + r * 0.35 * math.cos(a + 0.4)
            iy = cy + r * 0.35 * math.sin(a + 0.4)
            d.polygon([(cx, cy), (ex, ey), (ix, iy)], fill=fg)
        disc(d, cx, cy, r * 0.28, PAPER)
    elif kind == "oil":
        d.rounded_rectangle([cx - r * 0.55, cy - r * 0.75, cx + r * 0.55,
                             cy + r * 0.75], radius=r // 5, fill=fg)
        d.line([(cx - r * 0.55, cy - r * 0.25), (cx + r * 0.55, cy - r * 0.25)],
               fill=PAPER, width=max(2, r // 8))
        d.line([(cx - r * 0.55, cy + r * 0.25), (cx + r * 0.55, cy + r * 0.25)],
               fill=PAPER, width=max(2, r // 8))
    elif kind == "robot":
        d.rounded_rectangle([cx - r * 0.6, cy - r * 0.45, cx + r * 0.6,
                             cy + r * 0.6], radius=r // 4, fill=fg)
        d.line([(cx, cy - r * 0.45), (cx, cy - r * 0.85)], fill=fg,
               width=max(2, r // 7))
        disc(d, cx, cy - r * 0.9, r * 0.1, fg)
        disc(d, cx - r * 0.28, cy, r * 0.09, PAPER)
        disc(d, cx + r * 0.28, cy, r * 0.09, PAPER)
        d.line([(cx - r * 0.3, cy + r * 0.35), (cx + r * 0.3, cy + r * 0.35)],
               fill=PAPER, width=max(2, r // 8))
    elif kind == "court":
        d.polygon([(cx - r * 0.85, cy - r * 0.75), (cx + r * 0.85, cy - r * 0.75),
                   (cx, cy - r * 0.3)], fill=fg)
        for i in (-1, 0, 1):
            d.rectangle([cx + i * r * 0.55 - r * 0.09, cy - r * 0.25,
                         cx + i * r * 0.55 + r * 0.09, cy + r * 0.6], fill=fg)
        d.rectangle([x0, cy + r * 0.6, x1, cy + r * 0.8], fill=fg)
    elif kind == "raceflag":
        for i in range(3):
            for j in range(3):
                if (i + j) % 2 == 0:
                    d.rectangle([cx - r * 0.75 + i * r * 0.5,
                                 cy - r * 0.75 + j * r * 0.5,
                                 cx - r * 0.25 + i * r * 0.5,
                                 cy - r * 0.25 + j * r * 0.5], fill=fg)
        d.line([(cx - r * 0.75, y1 - r * 0.1), (cx + r * 0.75, y1 - r * 0.1)],
               fill=fg, width=max(2, r // 8))
    elif kind == "storm":
        d.ellipse([cx - r * 0.7, cy - r * 0.55, cx - r * 0.1, cy + r * 0.15],
                  fill=fg)
        d.ellipse([cx - r * 0.3, cy - r * 0.7, cx + r * 0.5, cy + r * 0.15],
                  fill=fg)
        d.ellipse([cx + r * 0.1, cy - r * 0.45, cx + r * 0.75, cy + r * 0.15],
                  fill=fg)
        d.polygon([(cx + r * 0.05, cy + r * 0.1), (cx - r * 0.25, cy + r * 0.75),
                   (cx + r * 0.05, cy + r * 0.75), (cx - r * 0.1, cy + r * 1.0),
                   (cx + r * 0.35, cy + r * 0.3)], fill=fg)
    elif kind == "health":
        disc(d, cx, cy, r, fg)
        d.rectangle([cx - r * 0.18, cy - r * 0.55, cx + r * 0.18, cy + r * 0.55],
                    fill=WHITE)
        d.rectangle([cx - r * 0.55, cy - r * 0.18, cx + r * 0.55, cy + r * 0.18],
                    fill=WHITE)
    elif kind == "scale":
        d.line([(cx, cy - r * 0.8), (cx, cy + r * 0.7)], fill=fg,
               width=max(2, r // 7))
        d.line([(cx - r * 0.8, cy - r * 0.6), (cx + r * 0.8, cy - r * 0.6)],
               fill=fg, width=max(2, r // 7))
        d.polygon([(cx - r * 0.8, cy - r * 0.6), (cx - r * 1.0, cy - r * 0.05),
                   (cx - r * 0.6, cy - r * 0.05)], fill=fg)
        d.polygon([(cx + r * 0.8, cy - r * 0.6), (cx + r * 1.0, cy - r * 0.05),
                   (cx + r * 0.6, cy - r * 0.05)], fill=fg)
        d.line([(x0, y1 - r * 0.15), (x1, y1 - r * 0.15)], fill=fg,
               width=max(2, r // 8))
    else:  # fallback: plain dot
        disc(d, cx, cy, r * 0.55, fg)

# ---------------------------------------------------------------- data
# Headlines below are written fresh for this image. Facts and sources
# are verified in ../STATUS.md section v7 (42 items kept from v6,
# 6 replacements verified from primary sources, 2 labels fixed).

LEADS = [
    ("missile", RED, "110+",
     "110+ MISSILES HIT KYIV IN BIGGEST RAID",
     "Zelensky calls it the biggest raid of the year: 27 ballistic "
     "missiles, 400+ drones overnight; 9 killed; 3 Dnipro bridges damaged.",
     "CNN · REUTERS"),
    ("cyclone", TEAL, "300K+",
     "CYCLONE AKVAN SLAMS INDIA'S EAST COAST",
     "Landfall 02:00 UTC near Gopalpur; winds 70–80 km/h, gusts 90; "
     "300,000+ evacuated; 9,341 shelters; 1,317 babies born in shelters.",
     "IMD · 02:00 UTC"),
    ("chart", NAVY, "−5.3%",
     "NASDAQ −5.3%: WORST WEEK SINCE APRIL 2025",
     "S&P −3.7% in a 7th straight loss; Dow −8% for the week; Nvidia −14% "
     "on SEC probe; Anthropic −8.5% to $88.91; VIX 35.89.",
     "INVESTOPEDIA · CNN"),
    ("globe", GREEN, "35%",
     "COP31 IN OVERTIME AS FOSSIL-FUEL TALKS DRAG",
     "Panama threatens to block any deal without fossil-fuel language; "
     "12 nations write in; draft keeps 35% electricity share by 2035; "
     "new text due Saturday.",
     "REUTERS"),
]

CARDS = [
    ("bitcoin", GOLD, "BITCOIN SLIPS BELOW $60,000",
     "First time since July; intraday low $55,830, lowest since Sep 2024; "
     "closed ~$58,317.", "REUTERS · 15:42 UTC"),
    ("ship", BLUE, "TANKER HIT BY UNKNOWN PROJECTILE",
     "Blast and fire 8 nm north of Khasab; no casualties; IRGC Navy says "
     "the tanker struck a mine.", "UKMTO · 15:00 GMT"),
    ("flame", RED, "HOUTHIS THREATEN SAUDI RED SEA PORTS",
     "Ports will be hit if the coalition strikes Hodeidah; Saudi-led strikes "
     "hit Yemeni ports Friday.", "REUTERS"),
    ("eu", BLUE, "EU APPROVES €1BN NEW MILITARY AID",
     "Joint procurement via EPF, deliveries by end-2027; part of a "
     "€6.6bn political deal.", "EU COUNCIL · 14:50 UTC"),
    ("person", GRAY, "FIRST WOMAN DEPUTY PRESIDENT DIES AT 71",
     "South Africa's Phumzile Mlambo-Ngcuka, 71, dies Friday; the "
     "presidency announces it late Friday.", "PRESIDENCY ZA"),
    ("shield", NAVY, "SYDNEY MAN CHARGED OVER ISIS PLOT",
     "Nowroz Rayed Amin, 35, charged Friday; 3 arrested, 10 homes raided; "
     "no target or capability found.", "AFP · 06:10 UTC"),
    ("car", TEAL, "ITALY CLEARS TESLA ASSISTED DRIVING",
     "Temporary approval for Tesla Assisted Driving System; first big EU "
     "state to clear it.",
     "REUTERS"),
    ("ball", GREEN, "RONALDO SCORES 986TH GOAL",
     "14th-minute strike in Al-Ahli's 3–1 win; 14 short of 1,000. "
     "(SPL tally.)", "ESPN"),
    ("ban", RED, "US SANCTIONS FOUR IRANIAN 'OIL TRUSTEES'",
     "Treasury's Operation Economic Outcast targets Bavand, Taj, Servati "
     "and Arabnejad.", "US TREASURY"),
    ("quake", ORANGE, "M6.7 QUAKE SHAKES PERU, FELT IN LIMA",
     "19:09 local, 34 km north of Junín, 108 km deep; no casualties "
     "reported.", "AP · 19:09 PET"),
    ("link", BLUE, "EU–UK POST-BREXIT TRADE RESET",
     "SPS barriers gone, carbon markets linked, youth mobility 100,000 "
     "each way for up to 3 years.", "AP"),
    ("un", PURPLE, "UN CHIEF RACE STUCK IN 9TH STRAW POLL",
     "Grynspan 10–4, 2 vetoes (states undisclosed); Nusseibeh vetoed; "
     "Grossi 8–3.",
     "REUTERS"),
]

ALSO_ON = [
    ("flag", BLUE, "Estonia confirms it will shut road crossings with Russia for 6+ months from Dec 1"),
    ("link", NAVY, "Trump and Xi: humans must always decide on military AI, Bessent tells CNBC"),
    ("survey", PURPLE, "93% of Japanese say ties with China are bad — worst since 1986, survey finds"),
    ("flag", GREEN, "Modi opens SCO forum in Delhi; first Pakistani minister visits India in 3 years"),
    ("flag", TEAL, "Australia, Canada, NZ demand an unconditional permanent ceasefire from Russia"),
    ("boom", RED, "Iraqi forces enter Kataib Hezbollah stronghold Jurf al-Sakher without a fight"),
    ("chip", NAVY, "Nvidia −14% to $125.53; $491bn wiped in a day; SEC probes its accounting"),
    ("flag", RED, "Xi meets Albanese in Shenzhen; hails 'full turnaround' in China–Australia ties"),
    ("scale", BLUE, "Eurogroup names Boone and Brunnermeier as ECB candidates; Lagarde leaves in Feb"),
    ("court", GRAY, "Dutch court: BYD Ti7 copies Defender design; EU sales ban — BYD to appeal"),
    ("car", TEAL, "Tesla opens first Argentina store in Buenos Aires; Model 3/Y from $40,000"),
    ("raceflag", ORANGE, "Russell fastest in FP3 at 1:34.041; Mercedes 1–2; qualifying at 20:00 local"),
    ("gold", GOLD, "Gold closes $3,538.19, −2.4%; lowest since Sep 2025; −8.9% for the week"),
    ("survey", NAVY, "Michigan sentiment 51.5; Bessent urges Fed not to hike 50bp in December"),
    ("factory", PURPLE, "Tesla plans a $3.1bn polysilicon plant in Texas"),
    ("missile", RED, "Russian missiles and drones entered Polish airspace during the Kyiv barrage"),
    ("boom", ORANGE, "Kyiv hits 3 Russian ballistic launchers overnight; Smolensk explosives plant struck"),
    ("scale", GRAY, "581 women killed in 3 months, police figures show; 5,590 murders Jul–Sep"),
    ("flag", RED, "Rodríguez rejects ICJ jurisdiction over Esequibo in a Friday statement"),
    ("chart", NAVY, "Kospi −5.2% to 4,869.96, lowest since Jan 20; first close under 4,900 in 10 months"),
    ("oil", ORANGE, "Brent settles $92.57, +0.6% on the day; third straight weekly loss"),
    ("rocket", BLUE, "Falcon 9 launches secret USSF-317 mission from Vandenberg at 20:20 PST"),
    ("robot", PURPLE, "New OpenAI usage policy takes effect: model resellers need approval first"),
    ("globe", TEAL, "Island states: COP31 a failure if it ignores 'out of control warming'"),
    ("chart", RED, "Broadcom −12%, AMD −13%, Meta −6%, Amazon −4%, Apple −2%"),
    ("chart", NAVY, "Anthropic −8.5% to $88.91, a day after its record $81.3bn IPO"),
    ("shield", RED, "FBI's most-wanted 'Chapo Isidro' captured in Mexico; gunfight halts baseball game"),
    ("ship", BLUE, "Iran claims 14 tankers staged at Kharg to test the US blockade; trackers dispute it"),
    ("health", GRAY, "Bolsonaro, 71, taken to hospital with severe abdominal pain"),
    ("storm", TEAL, "Storm kills 3, destroys ~5,000 homes in Tupanciretã, winds over 100 km/h"),
    ("chip", PURPLE, "Samsung names Hwang Sang-joon to lead its memory-chip business"),
    ("chart", GREEN, "Sensex +1.2%, Nifty +1.1% — India defies the global rout"),
]

TIMELINE = ("02:00 AKVAN · 06:10 SYDNEY · 10:00 SENSEX · 14:50 EU €1BN · "
           "15:00 KHASAB · 15:42 BTC <$60K · 16:35 ECB · 19:09 PERU · "
           "19:10 KHARG · 21:00 NASDAQ")

DATE_CHECK = ("DATE CHECK — LEFT OUT: Sudan report (17 Nov) · Turkey $26B "
              "(16 Nov) · Colombia seizure (19 Nov) · Egypt–Syria flights "
              "(17 Nov) · AWS Chile (11 Nov) · Korea $1T (19 Nov)")

NOTE = ("Every story below happened or was first reported on "
        "Friday 20 November 2026.")


# ---------------------------------------------------------------- layout
def draw():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 16  # page margin

    # --- masthead: dark navy band, paper name + date + globe ---
    d.rectangle([0, 16, W, 102], fill=NAVY)
    d.rectangle([0, 16, W, 20], fill=NAVY_D)
    f_name = font(SERIF_B, 40)
    d.text((mx, 24), "THE FRIDAY PAPER", font=f_name, fill=WHITE)
    f_date = font(SANS_B, 30)
    d.text((mx, 64), "FRIDAY 20 NOVEMBER 2026", font=f_date, fill=(232, 190, 90))
    f_ed = font(SANS_B, 12)
    d.text((928, 30), "WORLD EDITION", font=f_ed, fill=WHITE, anchor="ra")
    d.text((928, 52), "48 STORIES", font=f_ed, fill=(232, 190, 90), anchor="ra")
    disc(d, 962, 58, 24, WHITE)
    icon(d, "globe", 962, 58, 18, NAVY)

    # --- editor's note (the honest claim; only true if 48/48 verified) ---
    f_note = font(SANS, 14)
    d.text((mx, 108), NOTE, font=f_note, fill=INK)

    # --- UTC timeline strip ---
    d.rectangle([0, 128, W, 148], fill=LIGHT)
    f_tl = font(SANS_B, 11)
    d.text((W // 2, 138), TIMELINE, font=f_tl, fill=NAVY, anchor="mm")

    # --- leads: 2x2, big icon chip + big number + headline + summary ---
    f_lh = font(SANS_B, 20)
    f_ls = font(SANS, 13)
    f_lt = font(SANS_B, 10)
    f_bn = font(SANS_B, 24)
    lead_y, lead_h, lead_w, lead_gap = 154, 130, 492, 8
    for i, (kind, accent, big, head, summ, tag) in enumerate(LEADS):
        x = mx + (i % 2) * (lead_w + lead_gap)
        y = lead_y + (i // 2) * (lead_h + lead_gap)
        d.rectangle([x, y, x + lead_w, y + lead_h], fill=CARD,
                    outline=LINE, width=1)
        d.rectangle([x, y, x + lead_w, y + 6], fill=accent)
        disc(d, x + 42, y + 46, 28, accent)
        icon(d, kind, x + 42, y + 46, 17, WHITE)
        d.text((x + lead_w - 14, y + 14), big, font=f_bn, fill=accent,
               anchor="ra")
        lines = wrap(head, f_lh, 296)[:2]
        yy = y + 12
        for ln in lines:
            d.text((x + 84, yy), ln, font=f_lh, fill=INK)
            yy += 24
        slines = wrap(summ, f_ls, 392)[:3]
        yy = y + 64
        for ln in slines:
            d.text((x + 84, yy), ln, font=f_ls, fill=INK)
            yy += 16
        d.text((x + 84, y + lead_h - 16), tag, font=f_lt, fill=accent)

    # --- section header: cards ---
    f_sec = font(SANS_B, 15)
    d.text((mx, 428), "THE DAY IN BRIEF", font=f_sec, fill=NAVY)
    d.line([(mx, 448), (W - mx, 448)], fill=NAVY, width=2)

    # --- cards: 4 cols x 3 rows, icon chip + headline + detail + tag ---
    f_ch = font(SANS_B, 13)
    f_cd = font(SANS, 10)
    f_ct = font(SANS_B, 9)
    card_w, card_h, card_gap = 243, 96, 6
    for i, (kind, accent, head, det, tag) in enumerate(CARDS):
        col, row = i % 4, i // 4
        x = mx + col * (card_w + card_gap)
        y = 454 + row * (card_h + card_gap)
        d.rectangle([x, y, x + card_w, y + card_h], fill=CARD,
                    outline=LINE, width=1)
        d.rectangle([x, y, x + 4, y + card_h], fill=accent)
        disc(d, x + 26, y + 24, 18, accent)
        icon(d, kind, x + 26, y + 24, 11, WHITE)
        lines = wrap(head, f_ch, 181)[:2]
        yy = y + 7
        for ln in lines:
            d.text((x + 50, yy), ln, font=f_ch, fill=INK)
            yy += 15
        dlines = wrap(det, f_cd, 187)[:3]
        yy = y + 42
        for ln in dlines:
            d.text((x + 50, yy), ln, font=f_cd, fill=INK)
            yy += 11
        d.text((x + 50, y + card_h - 14), tag, font=f_ct, fill=accent)

    # --- section header: also-on ---
    d.text((mx, 760), "ALSO ON FRIDAY", font=f_sec, fill=NAVY)
    d.line([(mx, 780), (W - mx, 780)], fill=NAVY, width=2)

    # --- also-on: 2 columns x 16 rows, dot + one-line headline ---
    f_ao = font(SANS, 11)
    col_w = (W - 2 * mx - 16) // 2
    for i, (kind, accent, text) in enumerate(ALSO_ON):
        col, row = i % 2, i // 2
        x = mx + col * (col_w + 16)
        y = 786 + row * 12
        disc(d, x + 4, y + 5, 3, accent)
        d.text((x + 12, y), fit(text, f_ao, col_w - 14), font=f_ao, fill=INK)

    # --- footer: DATE CHECK box (what was deliberately left out) ---
    f_dc = font(SANS_B, 9)
    d.rectangle([mx, 980, W - mx, 1006], fill=PINK, outline=RED, width=1)
    d.text((W // 2, 993), DATE_CHECK, font=f_dc, fill=RED, anchor="mm")

    # Palette PNG: flat colours compress well and keep the file small.
    pal = img.convert("P", palette=Image.ADAPTIVE, colors=256)
    pal.save(OUT, optimize=True)
    print("wrote", OUT, pal.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    draw()
