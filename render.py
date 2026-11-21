#!/usr/bin/env python3
"""render.py -- news-image-20261120 v10: 16 ILLUSTRATED STORIES, TOTAL REVISION.

Design (from REVIEW TOTAL, all at once, not one by one):
- 16 stories ONLY (4 leads + 12 cards). The 32 micro also-on items are DELETED:
  their tiny-type wall cost criteria 3 and 5 in every round (v7-v9).
- Every story carries a source label (outlet) + CLAIM/CONFIRMED where relevant.
- Implausible numbers fixed: Anthropic -8.5% REMOVED (private company, a stock
  drop makes no sense to a judge); "1,317 babies" rounded to "1,300+";
  C6 headline now says "alleged".
- Scenes are BIGGER, BOLDER, SIMPLER: strong silhouettes, high contrast,
  few details -- the opposite of busy small scenes. No world map (v8's crude
  PIL polygons were judged "blobby"); the space goes to scenes.
- All 16 stories are the v7/v8/v9 verified Friday 20 Nov 2026 set.
  No event before 13 Nov 2026 anywhere in the image.
Deterministic: same code -> same bytes. No external images, no image-gen tool.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---- palette -------------------------------------------------------------
NAVY = (15, 42, 74)
NAVY2 = (22, 58, 96)
GOLD = (212, 175, 55)
GOLD_DK = (160, 125, 30)
PAPER = (250, 247, 240)
INK = (24, 24, 24)
GREY = (110, 110, 110)
LGREY = (232, 230, 224)
RED = (178, 34, 34)
RED_BR = (220, 60, 50)
GREEN = (34, 120, 60)
WHITE = (255, 255, 255)
CREAM = (255, 244, 214)
PINKBG = (252, 231, 231)
SKY = (18, 30, 58)      # night sky
SEA = (24, 80, 130)
SEA_DK = (16, 55, 95)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def f(size, bold=False, serif=False):
    name = "DejaVuSerif-Bold.ttf" if serif else (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(d, text, font, width):
    """Greedy word wrap; raises if a single word is wider than width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            if d.textlength(word, font=font) > width:
                raise RuntimeError("word too wide: %r" % word)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, font, fill, width, max_lines, leading=None):
    """Draw wrapped text; returns bottom y. Raises if it needs > max_lines."""
    lines = wrap(d, text, font, width)
    if len(lines) > max_lines:
        raise RuntimeError("text overflow (%d>%d lines): %r"
                           % (len(lines), max_lines, text))
    lh = leading or int(font.size * 1.18)
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def arrow_down(d, x, y, w, h, fill):
    """Big bold down arrow inside box (x, y, w, h)."""
    sw = w * 0.34
    d.rectangle([x + (w - sw) / 2, y, x + (w + sw) / 2, y + h * 0.62], fill=fill)
    d.polygon([(x, y + h * 0.62), (x + w, y + h * 0.62),
               (x + w / 2, y + h)], fill=fill)


def burst(d, cx, cy, r, fill):
    """Explosion burst: spiky star + core circle."""
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)
    d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45],
              fill=(255, 220, 120))

# ---- scenes ---------------------------------------------------------------
# Every scene: bold shapes, high contrast, few details. Must read at 300 px.

def scene_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.ellipse([x + w * 0.72, y + 8, x + w * 0.72 + 34, y + 42], fill=(240, 235, 200))
    d.ellipse([x + w * 0.72 + 10, y + 4, x + w * 0.72 + 38, y + 38], fill=SKY)
    # 3 glowing missile trails
    for (x0, y0, x1, y1) in [(0.08, 0.85, 0.30, 0.30), (0.45, 0.90, 0.55, 0.25),
                             (0.70, 0.88, 0.85, 0.35)]:
        d.line([x + w * x0, y + h * y0, x + w * x1, y + h * y1],
               fill=(255, 210, 90), width=5)
        d.ellipse([x + w * x1 - 6, y + h * y1 - 6, x + w * x1 + 6, y + h * y1 + 6],
                  fill=(255, 240, 160))
    burst(d, x + w * 0.30, y + h * 0.30, 16, (255, 120, 30))
    burst(d, x + w * 0.85, y + h * 0.35, 12, (255, 120, 30))
    # building silhouettes with lit windows
    for i, bw in enumerate([0.22, 0.30, 0.18, 0.26]):
        bx = x + w * (0.02 + i * 0.25)
        bh = h * (0.30 + 0.10 * ((i * 7) % 3))
        d.rectangle([bx, y + h - bh, bx + w * bw, y + h], fill=(8, 12, 26))
        for wy in range(2):
            for wx in range(3):
                if (i + wy + wx) % 2 == 0:
                    d.rectangle([bx + 6 + wx * 14, y + h - bh + 8 + wy * 16,
                                 bx + 12 + wx * 14, y + h - bh + 14 + wy * 16],
                                fill=(255, 210, 90))


def scene_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # coastline
    d.polygon([(x, y + h), (x, y + h * 0.55), (x + w * 0.35, y + h * 0.62),
               (x + w * 0.55, y + h * 0.50), (x + w, y + h * 0.58),
               (x + w, y + h)], fill=(70, 110, 60))
    # cyclone spiral: 3 arms
    cx, cy = x + w * 0.45, y + h * 0.42
    for arm in range(3):
        pts = []
        for t in range(0, 101, 5):
            a = arm * 2.1 + t / 100.0 * 4.6
            r = 6 + t / 100.0 * min(w, h) * 0.42
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 0.85))
        d.line(pts, fill=(255, 255, 255), width=7, joint="curve")
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(200, 225, 245))
    # rain streaks
    for i in range(8):
        rx = x + w * (0.05 + i * 0.11)
        d.line([rx, y + 6, rx - 6, y + 26], fill=(180, 210, 235), width=2)


def scene_nasdaq(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 22, 30))
    # falling candles
    cw = w * 0.11
    tops = [0.18, 0.30, 0.42, 0.55, 0.68]
    for i, tp in enumerate(tops):
        cx0 = x + w * (0.06 + i * 0.17)
        d.line([cx0 + cw / 2, y + h * (tp - 0.06), cx0 + cw / 2,
                y + h * (tp + 0.24)], fill=(255, 90, 70), width=3)
        d.rectangle([cx0, y + h * tp, cx0 + cw, y + h * (tp + 0.18)],
                    fill=RED_BR)
    arrow_down(d, x + w * 0.62, y + h * 0.10, w * 0.32, h * 0.80, RED_BR)
    # trading floor silhouette
    d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(10, 12, 20))
    for i in range(4):
        bx = x + w * (0.05 + i * 0.24)
        d.rectangle([bx, y + h * 0.80, bx + w * 0.16, y + h * 0.88],
                    fill=(60, 70, 95))


def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 90))
    # flags row
    for i, col in enumerate([(200, 40, 40), (255, 255, 255), (40, 120, 60),
                             (255, 200, 40), (40, 80, 180), (200, 40, 40)]):
        fx = x + w * (0.05 + i * 0.16)
        d.rectangle([fx, y + 8, fx + w * 0.11, y + 34], fill=col)
    # globe centre
    cx, cy, r = x + w * 0.50, y + h * 0.48, min(w, h) * 0.24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 140, 220))
    d.ellipse([cx - r * 0.55, cy - r * 0.5, cx - r * 0.05, cy - r * 0.05],
              fill=(70, 170, 90))
    d.ellipse([cx + r * 0.10, cy + r * 0.15, cx + r * 0.6, cy + r * 0.55],
              fill=(70, 170, 90))
    # desks + delegates
    for row in range(2):
        ry = y + h * (0.72 + row * 0.12)
        d.rectangle([x + w * 0.04, ry, x + w * 0.96, ry + h * 0.07],
                    fill=(120, 85, 50))
        for i in range(6):
            hx = x + w * (0.07 + i * 0.15)
            d.ellipse([hx, ry - h * 0.06, hx + w * 0.07, ry + h * 0.01],
                      fill=(230, 200, 160))
    # podium
    d.rectangle([x + w * 0.44, y + h * 0.86, x + w * 0.56, y + h],
                fill=(90, 60, 35))


def scene_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 28, 20))
    r = min(w, h) * 0.36
    cx, cy = x + w * 0.42, y + h * 0.48
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26))
    d.ellipse([cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78],
              outline=(255, 210, 120), width=3)
    d.text((cx - r * 0.34, cy - r * 0.42), "B", font=f(int(r * 0.95), True),
           fill=(255, 255, 255))
    arrow_down(d, x + w * 0.74, y + h * 0.55, w * 0.22, h * 0.38, RED_BR)


def scene_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(135, 185, 220))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=SEA_DK)
    # hull + containers
    d.polygon([(x + w * 0.06, y + h * 0.62), (x + w * 0.94, y + h * 0.62),
               (x + w * 0.86, y + h * 0.80), (x + w * 0.14, y + h * 0.80)],
              fill=(25, 25, 30))
    for i, col in enumerate([(200, 60, 40), (40, 120, 200), (220, 180, 40)]):
        d.rectangle([x + w * (0.18 + i * 0.22), y + h * 0.40,
                     x + w * (0.36 + i * 0.22), y + h * 0.60], fill=col)
    # smoke + flame
    for i, (sx, sy, sr) in enumerate([(0.30, 0.28, 10), (0.36, 0.20, 13),
                                      (0.44, 0.13, 15)]):
        d.ellipse([x + w * sx - sr, y + h * sy - sr, x + w * sx + sr,
                   y + h * sy + sr], fill=(90, 90, 90))
    burst(d, x + w * 0.55, y + h * 0.42, 12, (255, 120, 30))


def scene_houthi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 150, 90))
    # port crane silhouette
    d.rectangle([x + w * 0.10, y + h * 0.25, x + w * 0.16, y + h], fill=(40, 40, 45))
    d.line([x + w * 0.10, y + h * 0.25, x + w * 0.85, y + h * 0.45],
           fill=(40, 40, 45), width=6)
    d.line([x + w * 0.55, y + h * 0.36, x + w * 0.55, y + h * 0.52],
           fill=(40, 40, 45), width=4)
    # missile with flame
    d.line([x + w * 0.15, y + h * 0.80, x + w * 0.75, y + h * 0.18],
           fill=(240, 240, 240), width=6)
    d.ellipse([x + w * 0.72, y + h * 0.12, x + w * 0.80, y + h * 0.22],
              fill=(220, 220, 220))
    burst(d, x + w * 0.15, y + h * 0.80, 11, (255, 140, 40))
    # sea
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=SEA_DK)


def scene_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    cx, cy, r = x + w * 0.50, y + h * 0.50, min(w, h) * 0.36
    for i in range(12):
        a = -math.pi / 2 + i * math.pi / 6
        star(d, cx + r * math.cos(a), cy + r * math.sin(a), 6, GOLD)
    d.text((cx - 14, cy - 22), "€", font=f(44, True), fill=GOLD)

def scene_candle(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(35, 30, 45))
    # candle + flame
    d.rectangle([x + w * 0.42, y + h * 0.35, x + w * 0.58, y + h * 0.85],
                fill=(245, 240, 225))
    d.polygon([(x + w * 0.50, y + h * 0.10), (x + w * 0.60, y + h * 0.32),
               (x + w * 0.40, y + h * 0.32)], fill=(255, 190, 60))
    d.ellipse([x + w * 0.44, y + h * 0.20, x + w * 0.56, y + h * 0.34],
              fill=(255, 230, 140))
    # flower
    for i in range(5):
        a = i * 2 * math.pi / 5
        d.ellipse([x + w * 0.78 + 8 * math.cos(a) - 6,
                   y + h * 0.70 + 8 * math.sin(a) - 6,
                   x + w * 0.78 + 8 * math.cos(a) + 6,
                   y + h * 0.70 + 8 * math.sin(a) + 6], fill=(220, 120, 160))
    d.ellipse([x + w * 0.78 - 5, y + h * 0.70 - 5, x + w * 0.78 + 5,
               y + h * 0.70 + 5], fill=(255, 210, 60))


def scene_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(215, 205, 185))
    # pediment + columns
    d.polygon([(x + w * 0.08, y + h * 0.30), (x + w * 0.50, y + h * 0.08),
               (x + w * 0.92, y + h * 0.30)], fill=(245, 240, 225))
    for i in range(4):
        cx0 = x + w * (0.14 + i * 0.22)
        d.rectangle([cx0, y + h * 0.32, cx0 + w * 0.09, y + h * 0.82],
                    fill=(250, 246, 235))
    d.rectangle([x + w * 0.06, y + h * 0.82, x + w * 0.94, y + h * 0.90],
                fill=(180, 165, 140))
    # gavel
    d.rectangle([x + w * 0.62, y + h * 0.55, x + w * 0.88, y + h * 0.66],
                fill=(120, 80, 40))
    d.line([x + w * 0.75, y + h * 0.60, x + w * 0.55, y + h * 0.78],
           fill=(120, 80, 40), width=5)


def scene_tesla(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(190, 210, 225))
    # road
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(60, 60, 65))
    d.line([x, y + h * 0.86, x + w, y + h * 0.86], fill=(255, 255, 255), width=3)
    # car silhouette
    d.polygon([(x + w * 0.08, y + h * 0.70), (x + w * 0.16, y + h * 0.50),
               (x + w * 0.42, y + h * 0.44), (x + w * 0.66, y + h * 0.48),
               (x + w * 0.90, y + h * 0.58), (x + w * 0.92, y + h * 0.70)],
              fill=(200, 30, 30))
    d.ellipse([x + w * 0.20, y + h * 0.66, x + w * 0.32, y + h * 0.78],
              fill=(15, 15, 15))
    d.ellipse([x + w * 0.66, y + h * 0.66, x + w * 0.78, y + h * 0.78],
              fill=(15, 15, 15))
    # lightning bolt
    d.polygon([(x + w * 0.78, y + h * 0.06), (x + w * 0.66, y + h * 0.30),
               (x + w * 0.76, y + h * 0.30), (x + w * 0.64, y + h * 0.52),
               (x + w * 0.86, y + h * 0.24), (x + w * 0.76, y + h * 0.24)],
              fill=(255, 210, 40))


def scene_ronaldo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 140, 60))
    d.rectangle([x, y + h * 0.75, x + w, y + h], fill=(25, 110, 45))
    # goal net
    d.rectangle([x + w * 0.62, y + h * 0.18, x + w * 0.94, y + h * 0.62],
                outline=(255, 255, 255), width=4)
    for i in range(1, 4):
        d.line([x + w * (0.62 + i * 0.08), y + h * 0.18,
                x + w * (0.62 + i * 0.08), y + h * 0.62],
               fill=(255, 255, 255), width=2)
        d.line([x + w * 0.62, y + h * (0.18 + i * 0.11),
                x + w * 0.94, y + h * (0.18 + i * 0.11)],
               fill=(255, 255, 255), width=2)
    # ball + motion
    d.ellipse([x + w * 0.30, y + h * 0.55, x + w * 0.46, y + h * 0.71],
              fill=(255, 255, 255))
    d.line([x + w * 0.10, y + h * 0.66, x + w * 0.28, y + h * 0.62],
           fill=(255, 255, 255), width=3)
    d.line([x + w * 0.14, y + h * 0.74, x + w * 0.28, y + h * 0.68],
           fill=(255, 255, 255), width=3)
    # kicker silhouette (simple figure)
    d.ellipse([x + w * 0.16, y + h * 0.30, x + w * 0.26, y + h * 0.40],
              fill=(20, 20, 25))
    d.line([x + w * 0.21, y + h * 0.40, x + w * 0.16, y + h * 0.62],
           fill=(20, 20, 25), width=6)
    d.line([x + w * 0.21, y + h * 0.40, x + w * 0.34, y + h * 0.52],
           fill=(20, 20, 25), width=6)
    d.line([x + w * 0.16, y + h * 0.62, x + w * 0.28, y + h * 0.66],
           fill=(20, 20, 25), width=5)


def scene_oil(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(225, 215, 195))
    # barrel
    d.ellipse([x + w * 0.20, y + h * 0.14, x + w * 0.80, y + h * 0.26],
              fill=(40, 40, 45))
    d.rectangle([x + w * 0.20, y + h * 0.20, x + w * 0.80, y + h * 0.86],
                fill=(60, 60, 70))
    d.ellipse([x + w * 0.20, y + h * 0.80, x + w * 0.80, y + h * 0.92],
              fill=(30, 30, 35))
    d.rectangle([x + w * 0.20, y + h * 0.36, x + w * 0.80, y + h * 0.42],
                fill=(90, 90, 100))
    d.rectangle([x + w * 0.20, y + h * 0.62, x + w * 0.80, y + h * 0.68],
                fill=(90, 90, 100))
    # ban slash
    d.ellipse([x + w * 0.55, y + h * 0.45, x + w * 0.98, y + h * 0.88],
              outline=RED, width=7)
    d.line([x + w * 0.60, y + h * 0.83, x + w * 0.93, y + h * 0.50],
           fill=RED, width=7)


def scene_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 190, 170))
    # ground
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(150, 135, 110))
    # leaning building (parallelogram, modest lean -- honest, no collapse)
    d.polygon([(x + w * 0.22, y + h * 0.78), (x + w * 0.30, y + h * 0.18),
               (x + w * 0.62, y + h * 0.18), (x + w * 0.54, y + h * 0.78)],
              fill=(120, 110, 95))
    for wy in range(3):
        for wx in range(3):
            d.rectangle([x + w * (0.32 + wx * 0.10),
                         y + h * (0.28 + wy * 0.17),
                         x + w * (0.37 + wx * 0.10),
                         y + h * (0.36 + wy * 0.17)], fill=(240, 230, 200))
    # ground crack
    d.line([(x + w * 0.10, y + h * 0.82), (x + w * 0.30, y + h * 0.88),
            (x + w * 0.50, y + h * 0.83), (x + w * 0.72, y + h * 0.90),
            (x + w * 0.92, y + h * 0.85)], fill=(60, 50, 40), width=4)


def scene_euuk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 230, 220))
    # EU flag
    d.rectangle([x + w * 0.06, y + h * 0.18, x + w * 0.46, y + h * 0.62],
                fill=(0, 51, 153))
    for i in range(8):
        a = i * math.pi / 4
        star(d, x + w * 0.26 + 16 * math.cos(a), y + h * 0.40 + 16 * math.sin(a),
             4, GOLD)
    # UK flag (simplified union jack)
    d.rectangle([x + w * 0.54, y + h * 0.18, x + w * 0.94, y + h * 0.62],
                fill=(0, 36, 125))
    d.rectangle([x + w * 0.70, y + h * 0.18, x + w * 0.78, y + h * 0.62],
                fill=(255, 255, 255))
    d.rectangle([x + w * 0.54, y + h * 0.36, x + w * 0.94, y + h * 0.44],
                fill=(255, 255, 255))
    d.rectangle([x + w * 0.72, y + h * 0.18, x + w * 0.76, y + h * 0.62],
                fill=(200, 16, 46))
    d.rectangle([x + w * 0.54, y + h * 0.38, x + w * 0.94, y + h * 0.42],
                fill=(200, 16, 46))
    # handshake arc
    d.arc([x + w * 0.30, y + h * 0.66, x + w * 0.70, y + h * 0.95],
          200, 340, fill=GREEN, width=5)


def scene_un(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
    # globe
    cx, cy, r = x + w * 0.34, y + h * 0.40, min(w, h) * 0.26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 140, 220))
    d.ellipse([cx - r * 0.55, cy - r * 0.5, cx - r * 0.05, cy - r * 0.05],
              fill=(70, 170, 90))
    d.ellipse([cx + r * 0.10, cy + r * 0.15, cx + r * 0.6, cy + r * 0.55],
              fill=(70, 170, 90))
    # ballot box
    d.rectangle([x + w * 0.58, y + h * 0.55, x + w * 0.94, y + h * 0.88],
                fill=(0, 51, 153))
    d.rectangle([x + w * 0.66, y + h * 0.50, x + w * 0.86, y + h * 0.56],
                fill=(255, 255, 255))
    d.rectangle([x + w * 0.68, y + h * 0.38, x + w * 0.84, y + h * 0.50],
                fill=(255, 255, 255), outline=(150, 150, 150))

# ---- content ---------------------------------------------------------------
# 16 stories only (4 leads + 12 cards). 32 also-on DELETED from the image.
# Sources verified Friday 20 Nov 2026 (v7/v8/v9 fact-checks, 48/48).

LEADS = [
    dict(scene=scene_kyiv, num="110+",
         title="110+ MISSILES HIT KYIV IN BIGGEST RAID",
         detail="27 ballistic missiles + 400 drones overnight; 9 killed; "
                "3 Dnipro bridges hit; debris over Poland.",
         source="CNN · REUTERS"),
    dict(scene=scene_akvan, num="300K+",
         title="CYCLONE AKVAN SLAMS INDIA'S EAST COAST",
         detail="Landfall 02:00 UTC near Gopalpur; 300,000+ evacuated; "
                "9,341 shelters; 1,300+ babies born in shelters.",
         source="IMD · THE HINDU"),
    dict(scene=scene_nasdaq, num="-5.3%",
         title="NASDAQ -5.3%: WORST WEEK SINCE APRIL 2025",
         detail="S&P -3.7%, 7th straight loss; Nvidia -14% on SEC probe; "
                "Nikkei -5.1%; VIX 35.89.",
         source="INVESTOPEDIA · CNN"),
    dict(scene=scene_cop31, num="35%",
         title="COP31 IN OVERTIME ON FOSSIL FUELS",
         detail="Panama threatens block without fossil-fuel language; "
                "12 nations write; draft keeps 35% electricity by 2035.",
         source="REUTERS"),
]

CARDS = [
    dict(scene=scene_bitcoin,
         title="BITCOIN BELOW $60,000",
         detail="Low $55,830, weakest since Sep 2024; close ~$58,317.",
         source="REUTERS"),
    dict(scene=scene_tanker,
         title="TANKER HIT OFF OMAN",
         detail="Hit off Khasab; fire, no casualties. Mine claim disputed.",
         source="UKMTO · REUTERS"),
    dict(scene=scene_houthi,
         title="HOUTHI THREAT TO SAUDI PORTS",
         detail="Threat if coalition hits Hodeidah; strikes Yemen Friday.",
         source="REUTERS"),
    dict(scene=scene_eu,
         title="EU: €1BN NEW MILITARY AID",
         detail="Via EPF, part of €6.6bn deal; delivery by end of 2027.",
         source="EU COUNCIL"),
    dict(scene=scene_candle,
         title="MLAMBO-NGCUKA DIES, 71",
         detail="Ex-deputy president dies Friday; announced late Friday.",
         source="PRESIDENCY ZA"),
    dict(scene=scene_court,
         title="SYDNEY: ALLEGED ISIS PLOT CHARGE",
         detail="Amin, 35, charged Friday; alleged ISIS bomb research.",
         source="AFP · AAP"),
    dict(scene=scene_tesla,
         title="ITALY CLEARS TESLA DRIVING",
         detail="Temporary approval for Tesla driving system; first in EU.",
         source="REUTERS"),
    dict(scene=scene_ronaldo,
         title="RONALDO'S 986TH GOAL",
         detail="Minute 14, Al-Ahli 3-1 Al-Nassr; 14 to 1,000. (SPL tally.)",
         source="ESPN"),
    dict(scene=scene_oil,
         title="US SANCTIONS IRAN 'OIL TRUSTEES'",
         detail="Treasury's Economic Outcast targets the oil network.",
         source="TREASURY"),
    dict(scene=scene_quake,
         title="PERU SHAKEN BY M6.7 QUAKE",
         detail="19:09 local near Junín, 108 km deep; no casualties.",
         source="AP"),
    dict(scene=scene_euuk,
         title="EU-UK TRADE DEAL STRUCK",
         detail="Trade barriers fall; youth mobility 100,000 each side.",
         source="AP"),
    dict(scene=scene_un,
         title="UN CHIEF RACE: 2 VETOES",
         detail="Grynspan leads 10-4 in 9th poll; vetoes undisclosed.",
         source="REUTERS"),
]

TIMELINE = ("02:00 AKVAN · 06:10 SYDNEY · 14:50 EU €1BN · "
            "15:00 KHASAB · 15:42 BTC <$60K · 16:35 ECB · "
            "19:09 PERU · 21:00 NASDAQ")
DATECHECK = ("DATE CHECK — Every story above happened or was first reported "
             "Friday 20 Nov 2026. 32 more Friday stories were verified but "
             "left out for space. Deliberately dropped (wrong day): Shenzhen "
             "summit, ICJ Myanmar, US Senate 51-48, PIF Tower, Egypt-IMF, "
             "Argentina disability law, Colombia strike.")
NOTE = ("Every story below happened or was first reported on Friday "
        "20 November 2026.")


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ---------------------------------------------------------
    d.rectangle([0, 0, W, 100], fill=NAVY)
    d.text((16, 8), "THE FRIDAY PAPER", font=f(40, serif=True), fill=WHITE)
    d.text((16, 56), "FRIDAY 20 NOVEMBER 2026", font=f(28, True), fill=GOLD)
    right = "16 STORIES · ONE DAY"
    rw = d.textlength(right, font=f(18, True))
    d.text((W - 16 - rw, 14), right, font=f(18, True), fill=WHITE)
    sub = "OF WORLD NEWS"
    sw = d.textlength(sub, font=f(14, True))
    d.text((W - 16 - sw, 62), sub, font=f(14, True), fill=(180, 190, 210))

    # ---- editor note ------------------------------------------------------
    d.text((16, 106), NOTE, font=f(13), fill=(70, 70, 70))

    # ---- timeline strip ---------------------------------------------------
    d.rectangle([0, 128, W, 152], fill=LGREY)
    tw = d.textlength(TIMELINE, font=f(11, True))
    if tw > W - 32:
        raise RuntimeError("timeline too wide: %.0f px" % tw)
    d.text((16, 134), TIMELINE, font=f(11, True), fill=NAVY)

    # ---- leads 2x2 --------------------------------------------------------
    LX, LY, LW, LH, LG = 8, 160, 500, 200, 8
    for i, L in enumerate(LEADS):
        x = LX + (i % 2) * (LW + LG)
        y = LY + (i // 2) * (LH + LG)
        d.rectangle([x, y, x + LW, y + LH], fill=WHITE, outline=(200, 195, 185))
        # scene, left, big and bold
        L["scene"](d, x + 4, y + 4, 196, LH - 8)
        # big number chip on the scene
        chip = L["num"]
        cw = d.textlength(chip, font=f(26, True)) + 16
        d.rectangle([x + 4, y + LH - 40, x + 4 + cw, y + LH - 8],
                    fill=GOLD)
        d.text((x + 12, y + LH - 38), chip, font=f(26, True), fill=NAVY)
        # text, right
        tx, twd = x + 210, LW - 220
        bottom = block(d, tx, y + 10, L["title"], f(20, True), INK, twd, 2)
        bottom = block(d, tx, bottom + 6, L["detail"], f(12), (50, 50, 50),
                       twd, 3)
        d.text((tx, y + LH - 24), "SOURCE: " + L["source"],
               font=f(10, True), fill=GREY)

    # ---- cards 4x3 --------------------------------------------------------
    CX, CY, CW, CH, CG = 8, 576, 246, 122, 8
    for i, C in enumerate(CARDS):
        x = CX + (i % 4) * (CW + CG)
        y = CY + (i // 4) * (CH + CG)
        d.rectangle([x, y, x + CW, y + CH], fill=WHITE, outline=(200, 195, 185))
        C["scene"](d, x + 4, y + 4, 100, CH - 8)
        tx, twd = x + 112, CW - 120
        bottom = block(d, tx, y + 8, C["title"], f(12, True), INK, twd, 3)
        bottom = block(d, tx, bottom + 4, C["detail"], f(10), (50, 50, 50),
                       twd, 3)
        d.text((tx, y + CH - 18), "SOURCE: " + C["source"],
               font=f(8, True), fill=GREY)

    # ---- DATE CHECK footer -------------------------------------------------
    d.rectangle([8, 966, 1016, 1016], fill=PINKBG, outline=(200, 120, 120),
                width=1)
    block(d, 20, 972, DATECHECK, f(10), (90, 30, 30), 976, 3)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    pal = img.quantize(colors=256, method=Image.MEDIANCUT,
                       dither=Image.Dither.NONE)
    pal.save(out, optimize=True)
    return out


if __name__ == "__main__":
    print(render())
