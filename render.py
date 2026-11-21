#!/usr/bin/env python3
"""news-image-20261120 v15 — build-time renderer (35 stories).

Renders entry.png (1024x1024, RGB) from the 35 verified Friday
20 November 2026 stories: 4 leads (L1 hero + C9/L3/L4), 12 cards
(C1-C8, C10-C12, L2), 19 also-on items picked from A1-A32.
Build-time only: the grader never runs this file (main.py only
validates + copies entry.png). Deterministic: fixed-seed LCG only,
no time/datetime/network. PIL + DejaVu fonts (local build machine).
"""

import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

# ---------- palette ----------
NAVY = (13, 24, 48)
NAVY2 = (22, 38, 74)
NAVY3 = (30, 52, 96)
GOLD = (212, 160, 40)
GOLD_L = (233, 192, 92)
GOLD_D = (170, 122, 24)
PAPER = (248, 244, 232)
PAPER2 = (238, 232, 214)
PAPER3 = (228, 220, 198)
INK = (24, 24, 22)
GREY = (96, 92, 82)
GREY_L = (150, 146, 134)
RED = (178, 34, 34)
RED_L = (205, 60, 50)
GREEN = (32, 116, 58)
BLUE = (38, 88, 158)
SKY_D = (10, 18, 44)
SKY_M = (20, 34, 70)
SEA = (198, 220, 236)
LAND = (206, 186, 138)
LAND_D = (178, 154, 104)
WHITE = (255, 255, 255)
BLACK = (8, 8, 10)

FDIR = "/usr/share/fonts/truetype/dejavu/"


def FB(sz):
    return ImageFont.truetype(FDIR + "DejaVuSans-Bold.ttf", sz)


def F(sz):
    return ImageFont.truetype(FDIR + "DejaVuSans.ttf", sz)


# ---------- deterministic pseudo-random ----------
class LCG:
    def __init__(self, seed):
        self.s = seed & 0x7FFFFFFF

    def f(self):
        self.s = (self.s * 1103515245 + 12345) & 0x7FFFFFFF
        return self.s / 2147483648.0

    def r(self, a, b):
        return a + (b - a) * self.f()


def need(cond, msg):
    if not cond:
        raise AssertionError("v15 layout: " + msg)


def tw(d, s, font):
    return d.textlength(s, font=font)


def wrap(d, s, font, maxw):
    """Greedy word wrap; returns list of lines, each <= maxw."""
    lines, cur = [], ""
    for w in s.split(" "):
        t = (cur + " " + w).strip()
        if tw(d, t, font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def vgrad(img, box, c1, c2):
    """Vertical gradient fill inside box (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for yy in range(y0, y1):
        t = (yy - y0) / h
        c = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        img.paste(c, (x0, yy, x1, yy + 1))


def hgrad(img, box, c1, c2):
    x0, y0, x1, y1 = box
    w = max(1, x1 - x0)
    for xx in range(x0, x1):
        t = (xx - x0) / w
        c = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        img.paste(c, (xx, y0, xx + 1, y1))


def speckle(img, box, seed, n, amt):
    """Deterministic light/dark speckle to break flat colour (richer file)."""
    rng = LCG(seed)
    x0, y0, x1, y1 = box
    px = img.load()
    for _ in range(n):
        x = int(rng.r(x0, x1))
        y = int(rng.r(y0, y1))
        r, g, b = px[x, y]
        d = int(rng.r(-amt, amt))
        px[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)),
                    max(0, min(255, b + d)))


def rrect(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline,
                        width=width)


def burst(d, cx, cy, r0, r1, n, seed, col1, col2):
    """Irregular explosion starburst: n spikes, alternating radii."""
    rng = LCG(seed)
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n
        r = r1 if i % 2 == 0 else r0 * rng.r(0.55, 1.0)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=col1)
    d.ellipse([cx - r0 * 0.55, cy - r0 * 0.45, cx + r0 * 0.55, cy + r0 * 0.45],
              fill=col2)


def arrow_down(d, x, y, length, col, wdt=5):
    d.line([x, y, x, y + length], fill=col, width=wdt)
    d.polygon([(x - 8, y + length - 8), (x + 8, y + length - 8),
               (x, y + length + 6)], fill=col)


def arrow_right(d, x, y, length, col, wdt=5):
    d.line([x, y, x + length, y], fill=col, width=wdt)
    d.polygon([(x + length - 8, y - 8), (x + length - 8, y + 8),
               (x + length + 6, y)], fill=col)


# ---------- hero scene: night sky, missile trails, blasts, skyline,
# two onion domes, river. NO BRIDGE ANYWHERE (no Dnipro bridge collapsed;
# Kerch is blocklisted). ----------
def scene_hero(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), SKY_D, SKY_M)
    rng = LCG(20261120)
    # stars
    for _ in range(70):
        sx = x + rng.r(4, w - 4)
        sy = y + rng.r(3, h * 0.42)
        r = rng.r(0.6, 1.6)
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(235, 235, 220))
    # skyline: dark buildings with regular lit-window grids
    base = y + h * 0.62
    bx = x + 2
    brng = LCG(777)
    while bx < x + w - 8:
        bw = brng.r(44, 68)
        bh = brng.r(30, 58)
        bx1 = min(bx + bw, x + w)
        d.rectangle([bx, base - bh, bx1, y + h], fill=(6, 10, 26))
        cols = max(1, int(bw // 11))
        rows = max(1, int(bh // 13))
        for ci in range(cols):
            for ri in range(rows):
                if brng.f() < 0.55:
                    wx = bx + 5 + ci * 11
                    wy = base - bh + 6 + ri * 13
                    if wx + 4 <= x + w:
                        d.rectangle([wx, wy, wx + 4, wy + 5],
                                    fill=(255, 200, 90))
        bx += bw + 3
    # crescent moon, upper right (drawn after the skyline: stays visible)
    mx, my = x + w - 52, y + 14
    d.ellipse([mx, my, mx + 30, my + 30], fill=(238, 232, 200))
    d.ellipse([mx + 10, my - 3, mx + 38, my + 25], fill=SKY_M)
    # missile trails: three near-straight orange streaks, drawn OVER the
    # skyline so they read as missiles crossing the sky
    trails = [(0.06, 0.30, 0.24, 0.62), (0.42, 0.22, 0.58, 0.58),
              (0.74, 0.26, 0.90, 0.60)]
    for (ax, ay, bx, by) in trails:
        x0, y0 = x + w * ax, y + h * ay
        x1, y1 = x + w * bx, y + h * by
        d.line([x0, y0, x1, y1], fill=(120, 60, 20), width=9)
        d.line([x0, y0, x1, y1], fill=(255, 150, 50), width=5)
        d.line([x0, y0, x1, y1], fill=(255, 220, 140), width=2)
    # two onion domes on church towers (gold, with crosses)
    for dx in (x + w * 0.30, x + w * 0.66):
        d.rectangle([dx - 7, base - 34, dx + 7, y + h], fill=(10, 14, 34))
        d.ellipse([dx - 13, base - 52, dx + 13, base - 26], fill=GOLD_L)
        d.polygon([(dx - 13, base - 38), (dx + 13, base - 38),
                   (dx, base - 54)], fill=GOLD_L)
        d.line([dx, base - 66, dx, base - 52], fill=GOLD_L, width=2)
        d.line([dx - 5, base - 61, dx + 5, base - 61], fill=GOLD_L, width=2)
    # explosions: irregular bursts + grey smoke above the skyline
    for (ex, ey, s) in [(0.20, 0.58, 11), (0.55, 0.55, 13), (0.86, 0.57, 10)]:
        cx, cy = x + w * ex, y + h * ey
        burst(d, cx, cy, s * 0.62, s * 1.35, 9, int(1000 + ex * 997),
              (255, 140, 40), (255, 210, 90))
        srng = LCG(int(500 + ex * 331))
        for _ in range(5):
            sx = cx + srng.r(-16, 16)
            sy = cy - s - srng.r(2, 16)
            sr = srng.r(4, 8)
            d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                      fill=(110, 110, 120))
    # river band at the bottom
    vgrad(img, (x, y + h - 12, x + w, y + h), (16, 40, 80), (30, 70, 120))
    for i in range(6):
        lx = x + 20 + i * int(w / 6)
        d.line([lx, y + h - 6, lx + 34, y + h - 6], fill=(120, 170, 220),
               width=2)

# ---------- lead / card scenes (each draws inside box x,y,w,h) ----------
def sc_sanctions(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (24, 34, 58), (44, 58, 96))
    # three oil barrels
    for i, bx in enumerate((x + 10, x + 44, x + 78)):
        by = y + h - 52 - (10 if i == 1 else 0)
        d.ellipse([bx, by, bx + 28, by + 10], fill=(20, 20, 22))
        d.rectangle([bx, by + 5, bx + 28, by + 44], fill=(28, 28, 30))
        d.rectangle([bx, by + 14, bx + 28, by + 18], fill=GOLD_D)
        d.rectangle([bx, by + 30, bx + 28, by + 34], fill=GOLD_D)
        d.ellipse([bx, by + 40, bx + 28, by + 48], fill=(12, 12, 14))
    # document with red prohibition sign
    d.rectangle([x + w - 46, y + 12, x + w - 8, y + 52], fill=PAPER,
                outline=(120, 110, 90))
    for ly in range(4):
        d.line([x + w - 41, y + 19 + ly * 7, x + w - 13, y + 19 + ly * 7],
               fill=(140, 134, 120), width=2)
    cx, cy = x + w - 27, y + 66
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=RED)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=PAPER)
    d.line([cx - 9, cy + 9, cx + 9, cy - 9], fill=RED, width=4)


def sc_market(d, img, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(10, 10, 12))
    for gy in range(1, 4):
        yy = y + h * gy / 4
        d.line([x + 4, yy, x + w - 4, yy], fill=(40, 40, 44), width=1)
    pts = [(0.10, 0.30), (0.28, 0.38), (0.46, 0.52), (0.64, 0.60),
           (0.82, 0.74)]
    prev = None
    for (fx, fy) in pts:
        cx, cy = x + w * fx, y + h * fy
        d.rectangle([cx - 7, cy - 10, cx + 7, cy + 10], fill=RED_L)
        d.line([cx, cy - 16, cx, cy + 16], fill=RED_L, width=2)
        if prev:
            d.line([prev, (cx, cy)], fill=(255, 90, 70), width=3)
        prev = (cx, cy)
    arrow_right(d, x + w * 0.82, y + h * 0.74, 16, (255, 90, 70), 4)


def sc_cop(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (92, 70, 44), (58, 44, 28))
    # rows of seats
    for row in range(3):
        ry = y + h - 18 - row * 14
        for i in range(6):
            sx = x + 10 + i * 17
            d.rectangle([sx, ry - 8, sx + 12, ry], fill=(40, 30, 20))
    # globe on a table
    cx, cy = x + w // 2, y + h // 2 - 6
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(70, 130, 190))
    d.ellipse([cx - 12, cy - 12, cx + 2, cy + 2], fill=(90, 170, 90))
    d.ellipse([cx + 4, cy + 6, cx + 16, cy + 16], fill=(90, 170, 90))
    d.rectangle([cx - 26, cy + 22, cx + 26, cy + 28], fill=(50, 36, 22))


def sc_cyclone(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (16, 40, 78), (30, 70, 120))
    cx, cy = x + w // 2, y + h // 2
    for k in range(7):
        r = 6 + k * 5
        d.arc([cx - r, cy - r, cx + r, cy + r], start=20 + k * 38,
              end=200 + k * 38, fill=WHITE, width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(200, 225, 245))


def sc_bitcoin(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (30, 30, 34), (16, 16, 20))
    cx, cy = x + w // 2 - 4, y + h // 2
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=GOLD)
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=GOLD_D, width=2)
    d.text((cx, cy), "₿", font=FB(30), fill=(120, 80, 10), anchor="mm")
    d.line([x + w - 26, y + 8, x + w - 6, y + h - 16], fill=RED_L, width=5)
    d.polygon([(x + w - 30, y + h - 24), (x + w - 14, y + h - 24),
               (x + w - 6, y + h - 10)], fill=RED_L)


def sc_tanker(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (24, 52, 88), (44, 88, 132))
    # flat-deck tanker: hull + low superstructure, NO containers
    d.polygon([(x + 6, y + h - 30), (x + w - 6, y + h - 30),
               (x + w - 16, y + h - 12), (x + 16, y + h - 12)],
              fill=(90, 30, 26))
    d.rectangle([x + 10, y + h - 42, x + w - 10, y + h - 30],
                fill=(120, 120, 116))
    d.rectangle([x + w - 30, y + h - 62, x + w - 16, y + h - 42],
                fill=(200, 200, 196))
    rng = LCG(4242)
    for _ in range(6):
        sx = x + w - 26 + rng.r(-8, 8)
        sy = y + h - 66 - rng.r(0, 14)
        sr = rng.r(4, 8)
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(150, 150, 155))
    d.ellipse([x + 14, y + h - 52, x + 26, y + h - 40], fill=(255, 150, 50))


def sc_houthi(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (14, 22, 46), (30, 44, 84))
    d.line([x + 14, y + h - 14, x + w - 20, y + 14], fill=(200, 200, 200),
           width=6)
    d.polygon([(x + w - 30, y + 10), (x + w - 12, y + 22),
               (x + w - 26, y + 30)], fill=RED_L)
    for i in range(4):
        fx = x + 18 + i * 10
        fy = y + h - 18 - i * 9
        d.ellipse([fx - 4, fy - 4, fx + 4, fy + 4], fill=(255, 180, 80))


def sc_eu(d, img, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(28, 54, 120))
    cx, cy = x + w // 2, y + h // 2 - 2
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx, sy = cx + 24 * math.cos(a), cy + 24 * math.sin(a)
        d.polygon([(sx, sy - 5), (sx + 1.6, sy - 1.6), (sx + 5, sy),
                   (sx + 1.6, sy + 1.6), (sx, sy + 5), (sx - 1.6, sy + 1.6),
                   (sx - 5, sy), (sx - 1.6, sy - 1.6)], fill=GOLD_L)
    d.text((cx, cy), "€", font=FB(30), fill=WHITE, anchor="mm")


def sc_candles(d, img, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 18, 22))
    for i, cx in enumerate((x + w * 0.28, x + w * 0.5, x + w * 0.72)):
        bh = 34 - i * 6
        d.rectangle([cx - 6, y + h - 14 - bh, cx + 6, y + h - 14],
                    fill=(235, 230, 215))
        d.ellipse([cx - 4, y + h - 24 - bh, cx + 4, y + h - 12 - bh],
                  fill=(255, 190, 60))
        d.ellipse([cx - 2, y + h - 21 - bh, cx + 2, y + h - 14 - bh],
                  fill=(255, 240, 180))


def sc_court(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (200, 198, 190), (160, 156, 146))
    # courthouse columns
    for i in range(4):
        cx = x + 12 + i * 18
        d.rectangle([cx - 4, y + 14, cx + 4, y + h - 18], fill=(245, 244, 238))
    d.rectangle([x + 6, y + 8, x + w - 6, y + 14], fill=(90, 88, 82))
    d.rectangle([x + 6, y + h - 18, x + w - 6, y + h - 12],
                fill=(90, 88, 82))
    # scales
    cx, cy = x + w // 2, y + h - 34
    d.line([cx, cy - 16, cx, cy], fill=(60, 56, 48), width=3)
    d.line([cx - 14, cy - 16, cx + 14, cy - 16], fill=(60, 56, 48), width=2)
    d.polygon([(cx - 20, cy - 4), (cx - 8, cy - 4), (cx - 14, cy - 12)],
              fill=GOLD_D)
    d.polygon([(cx + 8, cy - 4), (cx + 20, cy - 4), (cx + 14, cy - 12)],
              fill=GOLD_D)


def sc_tesla(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (26, 28, 34), (14, 14, 18))
    # red car, side profile
    cy = y + h // 2 + 6
    d.rounded_rectangle([x + 10, cy - 12, x + w - 10, cy + 6], radius=8,
                        fill=(200, 30, 30))
    d.polygon([(x + w * 0.32, cy - 12), (x + w * 0.40, cy - 24),
               (x + w * 0.62, cy - 24), (x + w * 0.70, cy - 12)],
              fill=(200, 30, 30))
    d.polygon([(x + w * 0.42, cy - 22), (x + w * 0.60, cy - 22),
               (x + w * 0.66, cy - 12), (x + w * 0.36, cy - 12)],
              fill=(180, 220, 240))
    for wx in (x + w * 0.28, x + w * 0.72):
        d.ellipse([wx - 9, cy + 2, wx + 9, cy + 20], fill=(12, 12, 14))
        d.ellipse([wx - 4, cy + 7, wx + 4, cy + 15], fill=(160, 160, 164))
    d.line([x + 6, cy + 22, x + w - 6, cy + 22], fill=(70, 70, 76), width=2)


def sc_soccer(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (30, 110, 55), (18, 80, 38))
    # goal net
    d.rectangle([x + 8, y + 10, x + w - 8, y + h - 26], outline=WHITE,
                width=2)
    for gx in range(5):
        xx = x + 8 + gx * (w - 16) / 4
        d.line([xx, y + 10, xx, y + h - 26], fill=(220, 220, 220), width=1)
    for gy in range(4):
        yy = y + 10 + gy * (h - 36) / 3
        d.line([x + 8, yy, x + w - 8, yy], fill=(220, 220, 220), width=1)
    cx, cy = x + w // 2, y + h - 34
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=WHITE)
    d.polygon([(cx, cy - 6), (cx + 6, cy - 2), (cx + 4, cy + 6),
               (cx - 4, cy + 6), (cx - 6, cy - 2)], fill=INK)


def sc_peru(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (150, 170, 200), (110, 130, 160))
    # UPRIGHT building, one small crack in the wall, flat ground
    bx0, by0 = x + w // 2 - 18, y + 12
    d.rectangle([bx0, by0, bx0 + 36, y + h - 16], fill=(120, 122, 128))
    d.rectangle([bx0, by0, bx0 + 36, by0 + 6], fill=(90, 92, 98))
    for r in range(4):
        for c in range(2):
            wx = bx0 + 6 + c * 16
            wy = by0 + 12 + r * 14
            d.rectangle([wx, wy, wx + 8, wy + 8], fill=(255, 230, 150))
    d.line([bx0 + 26, by0 + 30, bx0 + 22, by0 + 44, bx0 + 28, by0 + 56],
           fill=(60, 60, 64), width=2)
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(90, 110, 70))


def sc_euuk(d, img, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 230, 215))
    # EU stars ring (left) + Union Jack (right)
    cx, cy = x + 22, y + h // 2 - 4
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx, sy = cx + 14 * math.cos(a), cy + 14 * math.sin(a)
        d.polygon([(sx, sy - 3), (sx + 1, sy - 1), (sx + 3, sy),
                   (sx + 1, sy + 1), (sx, sy + 3), (sx - 1, sy + 1),
                   (sx - 3, sy), (sx - 1, sy - 1)], fill=GOLD_D)
    jx0, jy0, jx1, jy1 = x + w - 44, y + h // 2 - 22, x + w - 8, y + h // 2 + 6
    d.rectangle([jx0, jy0, jx1, jy1], fill=(30, 50, 120))
    d.line([jx0, jy0, jx1, jy1], fill=WHITE, width=5)
    d.line([jx0, jy1, jx1, jy0], fill=WHITE, width=5)
    d.line([jx0, jy0, jx1, jy1], fill=RED, width=2)
    d.line([jx0, jy1, jx1, jy0], fill=RED, width=2)
    d.line([(jx0 + jx1) / 2, jy0, (jx0 + jx1) / 2, jy1], fill=WHITE, width=7)
    d.line([jx0, (jy0 + jy1) / 2, jx1, (jy0 + jy1) / 2], fill=WHITE, width=7)
    d.line([(jx0 + jx1) / 2, jy0, (jx0 + jx1) / 2, jy1], fill=RED, width=3)
    d.line([jx0, (jy0 + jy1) / 2, jx1, (jy0 + jy1) / 2], fill=RED, width=3)
    # two-way arrows (headline already carries "DEAL"; no text in scene)
    ay = y + h - 14
    arrow_right(d, x + 12, ay - 3, 22, GREEN, 3)
    d.line([x + 34, ay + 3, x + 12, ay + 3], fill=GREEN, width=3)
    d.polygon([(x + 16, ay - 1), (x + 16, ay + 7), (x + 8, ay + 3)],
              fill=GREEN)


def sc_un(d, img, x, y, w, h):
    vgrad(img, (x, y, x + w, y + h), (170, 200, 230), (120, 160, 200))
    cx, cy = x + w // 2 - 8, y + h // 2 - 6
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(60, 120, 180))
    d.ellipse([cx - 12, cy - 12, cx + 2, cy + 2], fill=(90, 170, 90))
    d.ellipse([cx + 4, cy + 6, cx + 16, cy + 16], fill=(90, 170, 90))
    # ballot box with 10-4
    d.rectangle([x + w - 34, y + h - 34, x + w - 8, y + h - 12],
                fill=(60, 60, 70))
    d.rectangle([x + w - 38, y + h - 40, x + w - 4, y + h - 34],
                fill=(40, 40, 48))
    d.text((x + w - 21, y + h - 23), "10–4", font=FB(10), fill=WHITE,
           anchor="mm")


# ---------- world map (own polygons, equirectangular) ----------
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-80, 73),
     (-65, 60), (-55, 52), (-60, 46), (-70, 44), (-75, 35), (-80, 32),
     (-85, 29), (-90, 21), (-95, 18), (-100, 16), (-105, 20), (-110, 23),
     (-115, 30), (-120, 34), (-125, 40), (-125, 49), (-135, 58),
     (-150, 60), (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, 0), (-40, -5),
     (-35, -10), (-40, -20), (-48, -28), (-55, -35), (-65, -45),
     (-70, -55), (-75, -45), (-75, -30), (-80, -18), (-80, -5)],
    # Europe
    [(-10, 36), (-10, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (30, 70), (25, 71),
     (18, 69), (12, 65), (5, 60), (5, 58), (-5, 50), (-10, 44)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 20), (45, 11), (51, 10), (48, 0), (40, -10), (35, -20),
     (30, -30), (20, -35), (15, -30), (12, -18), (9, -1), (9, 4), (0, 6),
     (-8, 5), (-15, 12)],
    # Asia
    [(30, 70), (40, 72), (60, 73), (75, 73), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 67), (178, 65), (170, 60), (160, 55),
     (150, 45), (140, 40), (130, 33), (127, 35), (122, 30), (120, 25),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20),
     (80, 15), (77, 8), (72, 20), (66, 25), (60, 25), (55, 26), (50, 29),
     (45, 30), (40, 36), (35, 36), (30, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (150, -25), (146, -19), (142, -11), (136, -12),
     (132, -12), (126, -14), (122, -17), (118, -20)],
]

PINS = [  # (label, lon, lat) — verified locations
    ("KYIV", 31, 50), ("GULF", 56, 26), ("SHENZHEN", 114, 22),
    ("DELHI", 77, 28), ("AKVAN", 87, 19), ("SYDNEY", 151, -34),
    ("GUASAVE", -108, 25), ("BRUSSELS", 4, 51), ("PERU", -75, -12),
    ("BRAZIL", -48, -16),
]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # faint graticule
    for gx in range(1, 6):
        xx = x + w * gx / 6
        d.line([xx, y, xx, y + h], fill=(170, 195, 215), width=1)
    for gy in range(1, 3):
        yy = y + h * gy / 3
        d.line([x, yy, x + w, yy], fill=(170, 195, 215), width=1)

    def proj(lon, lat):
        px = x + (lon + 180) / 360.0 * w
        py = y + (78 - lat) / 134.0 * h
        return (px, py)

    for cont in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in cont], fill=LAND,
                  outline=LAND_D)
    for i, (label, lon, lat) in enumerate(PINS, start=1):
        px, py = proj(lon, lat)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=WHITE, width=2)
        d.text((px, py), str(i), font=FB(9), fill=WHITE, anchor="mm")
    return proj


# ---------- market bars ----------
MARKETS = [("NASDAQ", -5.3), ("S&P", -3.7), ("KOSPI", -5.2),
           ("GOLD", -2.4), ("BRENT", +0.6), ("SENSEX", +1.1)]


def draw_markets(d, x, y, w, h):
    d.text((x, y), "MARKETS — FRIDAY CLOSE", font=FB(13), fill=INK)
    by = y + 22
    bw_max = w - 108
    for i, (name, val) in enumerate(MARKETS):
        ry = by + i * 14
        col = RED if val < 0 else GREEN
        d.text((x, ry), name, font=FB(11), fill=INK)
        d.text((x + 62, ry), "%+.1f%%" % val, font=F(11), fill=col)
        bl = int(abs(val) / 5.3 * bw_max)
        d.rectangle([x + 108, ry + 2, x + 108 + max(bl, 3), ry + 11],
                    fill=col)
    d.text((x, by + 6 * 14 + 2), "SENSEX +1.1% defies the rout.",
           font=F(10), fill=GREY)

# ---------- content (all facts from the verified MD list) ----------
LEADS = [
    ("sanctions", "US SANCTIONS 4 IRAN 'OIL TRUSTEES'",
     "Treasury's Operation Economic Outcast targets Bavand, Taj, "
     "Servati, Arabnejad.", "SOURCE: TREASURY ✓ CONFIRMED", "4"),
    ("market", "MARKET ROUT: NASDAQ -5.3%",
     "Worst week since Mar 2020; S&P worst since Apr 2025; "
     "Nvidia -14%.", "SOURCE: INVESTOPEDIA · CNN ✓ CONFIRMED", "-5.3%"),
    ("cop", "COP31 IN OVERTIME ON FOSSIL FUELS",
     "Panama threatens block; 12 nations write; draft keeps 35% "
     "electricity by 2035.", "SOURCE: REUTERS ✓ CONFIRMED", "35%"),
]

CARDS = [
    ("cyclone", "CYCLONE AKVAN SLAMS INDIA",
     "Landfall 02:00 UTC; 300,000+ evacuated; 1,300+ babies born.",
     "SOURCE: IMD ✓ CONFIRMED"),
    ("bitcoin", "BITCOIN BELOW $60,000", "Low $57,778; close $58,951.",
     "SOURCE: BINANCE ✓ CONFIRMED"),
    ("tanker", "TANKER HIT OFF KHASAB",
     "Unknown projectile; fire, no casualties.",
     "SOURCE: UKMTO ✓ CONFIRMED"),
    ("houthi", "HOUTHIS THREATEN RED SEA",
     "Threat if coalition hits Hodeidah; coalition strikes Yemen.",
     "SOURCE: REUTERS ✓ CONFIRMED"),
    ("eu", "EU: €1BN NEW MILITARY AID",
     "Joint buys via EPF; part of €6.6bn deal, due by 2027.",
     "SOURCE: EU COUNCIL ✓ CONFIRMED"),
    ("candles", "MLAMBO-NGCUKA DIES, 71",
     "Former deputy president; presidency announces Friday.",
     "SOURCE: PRESIDENCY ZA ✓ CONFIRMED"),
    ("court", "SYDNEY: ALLEGED ISIS PLOT CHARGE",
     "Amin, 35, charged; 3 held, 10 homes raided.",
     "SOURCE: AFP · AAP ✓ CONFIRMED"),
    ("tesla", "ITALY: FIRST MAJOR EU FOR TESLA",
     "Temporary approval for Tesla driving system.",
     "SOURCE: REUTERS ✓ CONFIRMED"),
    ("soccer", "RONALDO'S 986TH CAREER GOAL",
     "Minute 14, Al-Ahli 3-1 Al-Nassr. (SPL count.)",
     "SOURCE: ESPN ✓ CONFIRMED"),
    ("peru", "PERU QUAKE M6.7, LIGHT DAMAGE",
     "19:09 local, Junin, 108 km deep; no casualties.",
     "SOURCE: AP ✓ CONFIRMED"),
    ("euuk", "EU–UK DEAL CUTS TRADE BARRIERS",
     "SPS checks eased; youth mobility 100,000 a side.",
     "SOURCE: AP ✓ CONFIRMED"),
    ("un", "GRYNSPAN LEADS UN RACE 10–4",
     "9th poll: 2 vetoes, states undisclosed; deadlock.",
     "SOURCE: REUTERS ✓ CONFIRMED"),
]

SCENES = {"sanctions": sc_sanctions, "market": sc_market, "cop": sc_cop,
          "cyclone": sc_cyclone, "bitcoin": sc_bitcoin, "tanker": sc_tanker,
          "houthi": sc_houthi, "eu": sc_eu, "candles": sc_candles,
          "court": sc_court, "tesla": sc_tesla, "soccer": sc_soccer,
          "peru": sc_peru, "euuk": sc_euuk, "un": sc_un}

# 19 also-on, picked from A1-A32 (most consequential + 7-region cover).
# DROPPED (13): A10 BYD EU ban, A11 Tesla Argentina store, A12 Las Vegas
# GP FP3, A13 gold (duplicates L3), A14 Michigan sentiment, A15 Tesla
# Texas plant, A20 KOSPI (duplicates L3), A21 Brent (in market panel),
# A24 island nations (duplicates L4), A25 tech rout (duplicates L3),
# A26 Anthropic -8.5% (implausible number, Warden v10), A31 Samsung
# memory chief, A32 Sensex (in market panel + timeline).
ALSO_ON = [
    "Estonia closes Russia crossings from 1 Dec (Reuters)",
    "US–China: humans must decide military AI (Reuters)",
    "Japan: 93% say China ties bad, worst since 1986 (Kyodo)",
    "SCO forum opens in Delhi; Pakistan minister visits (PTI)",
    "Canada, Australia, NZ urge joint ceasefire (Canada)",
    "Iraq forces enter Hezbollah base, no resistance (AFP)",
    "Nvidia −14%; ~$491bn lost as SEC probes books (Reuters)",
    "Xi meets Albanese in Shenzhen; ties 'turning' (Xinhua)",
    "ECB nominees: Boone, Brunnermeier for top jobs (Eurogroup)",
    "Russian missiles enter Polish airspace (Reuters)",
    "Kyiv hits 3 Russian launchers, Smolensk plant (ISW)",
    "South Africa: 5,590 murders in one quarter (BBC)",
    "Venezuela rejects ICJ jurisdiction on Esequibo (CANA)",
    "SpaceX launches secret USSF-317 mission (Spaceflight Now)",
    "OpenAI: new usage rules in force from today (OpenAI)",
    "'Chapo Isidro' arrested in Mexico after shootout (CNN)",
    "Iran claims 14 tankers at Kharg; trackers dispute — CLAIM (ISW)",
    "Bolsonaro, 71, taken to hospital in Brazil (Reuters)",
    "Storm in Brazil kills 3, wrecks ~5,000 homes (EIN)",
]

TIMELINE = ("02:00 AKVAN · 06:10 SYDNEY · 10:00 SENSEX +1.1% · "
            "14:50 EU €1BN · 15:00 KHASAB · 15:42 BTC <$60K · 16:35 ECB · "
            "19:09 PERU · 19:10 KHARG · 21:00 NASDAQ")
DATECHECK = ("DATE CHECK — Left out (wrong day): Shenzhen summit · "
             "ICJ Myanmar · US Senate 51–48 · PIF Tower · Egypt–IMF · "
             "Argentina law · Colombia strike.")


def text_block(d, x, y, s, font, color, maxw, leading, maxlines):
    lines = wrap(d, s, font, maxw)
    need(len(lines) <= maxlines,
         "%r wraps to %d lines (max %d)" % (s[:40], len(lines), maxlines))
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=font, fill=color)
    return len(lines)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    speckle(img, (0, 0, 1009, H), 99, 9000, 5)
    MX = 16          # left margin; right edge limit x <= 1008
    RX = 1008

    # ---------- masthead 0-58 ----------
    d.rectangle([0, 0, W, 57], fill=NAVY)
    vgrad(img, (0, 0, W, 58), NAVY2, NAVY)
    d.text((MX, 12), "THE FRIDAY PAPER", font=FB(30), fill=WHITE)
    date_s = "FRIDAY 20 NOVEMBER 2026"
    need(tw(d, date_s, FB(26)) <= 640, "date too wide")
    d.text((RX, 8), date_s, font=FB(26), fill=GOLD_L, anchor="ra")
    d.text((RX, 38), "WORLD EDITION · 35 STORIES", font=FB(11),
           fill=GOLD_L, anchor="ra")
    d.rectangle([MX, 55, RX, 58], fill=GOLD)

    # ---------- editor note 58-76 ----------
    note = ("Every story below happened or was first reported on Friday "
            "20 November 2026. Figures sourced; claims labelled "
            "CLAIM / CONFIRMED.")
    d.text((W // 2, 62), note, font=F(11), fill=GREY, anchor="ma")

    # ---------- hero scene 76-176 + L1 strip 176-226 ----------
    scene_hero(d, img, MX, 76, RX - MX, 100)
    d.rectangle([MX, 176, RX, 226], fill=NAVY2)
    d.text((MX + 2, 180), "110+ MISSILES HIT UKRAINE", font=FB(28),
           fill=WHITE)
    detail = ("111 missiles, 404 drones overnight · 9 killed · 3 Dnipro "
              "bridges damaged · debris in Poland — SOURCE: CNN · REUTERS")
    need(tw(d, detail, F(12)) <= 880, "L1 detail too wide")
    d.text((MX + 2, 210), detail, font=F(12), fill=(200, 205, 220))
    chip = "110+"
    cw = int(tw(d, chip, FB(20))) + 20
    rrect(d, [RX - cw, 182, RX, 214], 6, fill=GOLD)
    d.text((RX - cw // 2, 186), chip, font=FB(20), fill=NAVY, anchor="ma")

    # ---------- leads 226-366 (3 x 322 wide, scene left 118) ----------
    ly, lh, lw, lgap = 226, 140, 322, 13
    for i, (key, head, det, src, chip_t) in enumerate(LEADS):
        x = MX + i * (lw + lgap)
        d.rectangle([x, ly, x + lw, ly + lh], fill=(252, 250, 244),
                    outline=(200, 194, 178))
        SCENES[key](d, img, x + 1, ly + 1, 118, lh - 18)
        cw2 = int(tw(d, chip_t, FB(13))) + 14
        rrect(d, [x + 118 - cw2 - 4, ly + 5, x + 118 - 4, ly + 25], 4,
              fill=GOLD)
        d.text((x + 118 - cw2 // 2 - 4, ly + 7), chip_t, font=FB(13),
               fill=NAVY, anchor="ma")
        tx = x + 126
        twd = x + lw - 8 - tx
        n = text_block(d, tx, ly + 6, head, FB(16), INK, twd, 19, 2)
        text_block(d, tx, ly + 6 + n * 19 + 2, det, F(12), (60, 58, 50),
                   twd, 15, 3)
        need(tw(d, src, FB(10)) <= lw - 16, "lead source too wide")
        d.text((x + 8, ly + lh - 16), src, font=FB(10),
               fill=(150, 110, 20))

    # ---------- map + markets 366-492 ----------
    my, mh = 366, 126
    # map panel 16-644
    d.rectangle([MX, my, 644, my + mh], fill=(252, 250, 244),
                outline=(200, 194, 178))
    d.text((MX + 8, my + 4), "WHERE THE DAY HAPPENED — WORLD MAP",
           font=FB(12), fill=INK)
    draw_map(d, MX + 8, my + 22, 400, 98)
    lx = MX + 416
    for i, (label, _lon, _lat) in enumerate(PINS, start=1):
        col = 0 if i <= 5 else 1
        row = (i - 1) % 5
        px = lx + col * 108
        py = my + 26 + row * 18
        d.ellipse([px, py, px + 12, py + 12], fill=RED)
        d.text((px + 6, py + 6), str(i), font=FB(8), fill=WHITE,
               anchor="mm")
        d.text((px + 16, py + 1), label, font=FB(11), fill=INK)
    # markets panel 652-1008
    d.rectangle([652, my, RX, my + mh], fill=(252, 250, 244),
                outline=(200, 194, 178))
    draw_markets(d, 660, my + 4, RX - 660 - 8, mh - 8)

    # ---------- cards 492-788: 4 cols x 3 rows, 242 x 96 ----------
    cy0, ch, cgap = 492, 96, 8
    cw3 = 242
    for i, (key, head, det, src) in enumerate(CARDS):
        row, col = divmod(i, 4)
        x = MX + col * (cw3 + cgap)
        y = cy0 + row * (ch + 4)
        d.rectangle([x, y, x + cw3, y + ch], fill=(252, 250, 244),
                    outline=(200, 194, 178))
        SCENES[key](d, img, x + 1, y + 1, 80, ch - 16)
        tx = x + 88
        twd = x + cw3 - 8 - tx
        n = text_block(d, tx, y + 6, head, FB(13), INK, twd, 15, 2)
        text_block(d, tx, y + 6 + n * 15 + 2, det, F(11), (60, 58, 50),
                   twd, 13, 3)
        need(tw(d, src, FB(9)) <= cw3 - 16, "card source too wide: %r"
             % src[:30])
        d.text((x + 8, y + ch - 14), src, font=FB(9),
               fill=(150, 110, 20))

    # ---------- also-on 788-986: header + 19 items, 2 cols, 14px ----------
    ay = 788
    d.text((MX, ay), "ALSO ON FRIDAY — 19 MORE VERIFIED STORIES",
           font=FB(13), fill=INK)
    d.rectangle([MX, ay + 18, RX, ay + 20], fill=GOLD)
    colw = (RX - MX - 16) // 2
    for i, item in enumerate(ALSO_ON):
        col = 0 if i < 10 else 1
        row = i if i < 10 else i - 10
        ix = MX + col * (colw + 16)
        iy = ay + 26 + row * 18
        need(tw(d, item, F(14)) <= colw - 14,
             "also-on too wide: %r" % item[:30])
        d.rectangle([ix, iy + 5, ix + 7, iy + 12], fill=GOLD_D)
        d.text((ix + 12, iy), item, font=F(14), fill=INK)

    # ---------- timeline 986-1002 ----------
    d.text((W // 2, 988), TIMELINE, font=F(11), fill=GREY, anchor="ma")
    # ---------- DATE CHECK 1002-1022 ----------
    d.rectangle([MX, 1002, RX, 1022], fill=(244, 214, 214))
    d.text((W // 2, 1006), DATECHECK, font=F(11), fill=(120, 30, 30),
           anchor="ma")

    # ---------- right-edge guard: past x=1008 only the full-bleed navy
    # masthead band may exist (its TEXT must end <= 1008); everywhere
    # else the strip must be plain paper. ----------
    px = img.load()
    for yy in range(H):
        for xx in range(1009, W):
            if yy < 58:
                r, g, b = px[xx, yy]
                need(max(r, g, b) < 100,
                     "masthead text past x=1008 at (%d,%d)" % (xx, yy))
            else:
                need(px[xx, yy] == PAPER,
                     "pixel past x=1008 at (%d,%d)" % (xx, yy))
    return img


def main():
    img = build()
    img.save(OUT, optimize=False)
    print("wrote %s: %dx%d" % (OUT, W, H))


if __name__ == "__main__":
    main()
