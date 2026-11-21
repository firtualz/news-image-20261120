#!/usr/bin/env python3
"""render.py — news-image-20261120 v9: ONE DAY, 48 STORIES, SCENE ILLUSTRATIONS.

Draws a 1024x1024 newspaper front page for Friday 20 November 2026.
Every illustration is drawn from PIL primitives in this file (no external
images, no image-generation tool). 4 lead scenes + 12 card scenes = 16
hand-drawn scenes; 32 also-on items in two compact columns.
Content: the same 48 Friday-20-Nov stories verified for v7/v8
(42 kept + 6 replacements); Sensex uses the official close +1.1%.
Deterministic: same code -> same bytes.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---- palette -------------------------------------------------------------
NAVY   = (15, 42, 74)     # masthead
NAVY2  = (22, 58, 96)
GOLD   = (212, 175, 55)
PAPER  = (250, 247, 240)  # page background
INK    = (24, 24, 24)
GREY   = (110, 110, 110)
LGREY  = (232, 230, 224)
RED    = (178, 34, 34)
GREEN  = (34, 120, 60)
WHITE  = (255, 255, 255)
CREAM  = (255, 244, 214)
PINKBG = (252, 231, 231)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def f(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, size)


def wrap(text, font, width):
    """Greedy word wrap; returns list of lines that fit `width` px."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if font.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def star5(d, cx, cy, r_out, r_in, color):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=color)


def burst(d, cx, cy, r, color):
    """12-point starburst (explosion)."""
    pts = []
    for i in range(24):
        r = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 12
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=color)


def glow_line(d, x0, y0, x1, y1):
    """Bright missile trail: wide orange, mid yellow, white core."""
    d.line([x0, y0, x1, y1], fill=(255, 140, 40), width=6)
    d.line([x0, y0, x1, y1], fill=(255, 210, 80), width=3)
    d.line([x0, y0, x1, y1], fill=(255, 255, 240), width=1)


def building_row(d, x0, y_base, heights, w, color, win_color):
    """Row of dark building silhouettes with lit windows."""
    x = x0
    for h in heights:
        d.rectangle([x, y_base - h, x + w, y_base], fill=color)
        for wy in range(y_base - h + 6, y_base - 6, 12):
            for wx in range(x + 4, x + w - 4, 9):
                if (wx + wy) % 17 < 8:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=win_color)
        x += w + 3


def spiral(d, cx, cy, turns, r_max, color, width):
    """Archimedean spiral polyline."""
    pts = []
    steps = int(turns * 72)
    for i in range(steps + 1):
        t = i / steps * turns * 2 * math.pi
        r = r_max * i / steps
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    d.line(pts, fill=color, width=width, joint="curve")


def candle(d, x, y, w, h, color, wick=4):
    d.rectangle([x, y, x + w, y + h], fill=color)
    d.line([x + w // 2, y - wick, x + w // 2, y], fill=(60, 40, 20), width=2)
    d.ellipse([x + w // 2 - 4, y - wick - 9, x + w // 2 + 4, y - wick + 1],
              fill=(255, 200, 60))
    d.ellipse([x + w // 2 - 2, y - wick - 6, x + w // 2 + 2, y - wick],
              fill=(255, 240, 180))

# ---- LEAD SCENES (each ~200x200, must read at 300px) ----------------------

def scene_kyiv(d, x, y, w, h):
    """Night raid over Kyiv: dark sky, missile trails, explosions, skyline."""
    # sky gradient bands
    for i in range(8):
        c = (10 + i * 2, 16 + i * 3, 40 + i * 4)
        d.rectangle([x, y + i * h // 8, x + w, y + (i + 1) * h // 8], fill=c)
    # stars
    for sx, sy, r in [(18, 22, 2), (70, 12, 1), (120, 30, 2), (160, 14, 1),
                      (45, 48, 1), (150, 52, 2), (95, 18, 1), (185, 40, 1)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(255, 255, 220))
    # crescent moon
    d.ellipse([x + w - 42, y + 12, x + w - 14, y + 40], fill=(240, 235, 200))
    d.ellipse([x + w - 36, y + 10, x + w - 10, y + 36], fill=(14, 22, 48))
    # missile trails (from upper left, heading down-right)
    glow_line(d, x + 12, y + 8, x + 96, y + 128)
    glow_line(d, x + 58, y + 4, x + 128, y + 118)
    glow_line(d, x + 108, y + 10, x + 168, y + 122)
    for hx, hy in [(96, 128), (128, 118), (168, 122)]:
        d.ellipse([x + hx - 4, y + hy - 4, x + hx + 4, y + hy + 4],
                  fill=(255, 255, 240))
    # explosions above the skyline
    burst(d, x + 62, y + h - 62, 26, (255, 90, 20))
    burst(d, x + 62, y + h - 62, 16, (255, 180, 60))
    burst(d, x + 62, y + h - 62, 8, (255, 240, 180))
    burst(d, x + 150, y + h - 48, 20, (255, 110, 30))
    burst(d, x + 150, y + h - 48, 12, (255, 190, 80))
    # smoke
    for sx, sy, r in [(40, h - 78, 14), (58, h - 88, 10), (132, h - 66, 12),
                      (168, h - 60, 9)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(120, 120, 130))
    # skyline silhouettes
    building_row(d, x + 4, y + h - 2, [52, 74, 44, 66, 58, 40], 28,
                 (8, 10, 18), (255, 210, 90))


def scene_akvan(d, x, y, w, h):
    """Cyclone spiral over the Bay of Bengal coast."""
    # sea
    d.rectangle([x, y, x + w, y + h], fill=(24, 90, 130))
    for i in range(5):
        d.arc([x - 30 + i * 8, y + h - 46 + i * 10, x + w + 30 - i * 8,
               y + h + 30], 200, 340, fill=(140, 200, 230), width=2)
    # land (coast) bottom-left
    d.polygon([(x, y + h), (x, y + h - 52), (x + 78, y + h - 30),
               (x + 150, y + h - 44), (x + 210, y + h - 18), (x + w, y + h - 26),
               (x + w, y + h)], fill=(196, 164, 110))
    d.polygon([(x, y + h), (x, y + h - 52), (x + 78, y + h - 30),
               (x + 150, y + h - 44)], fill=(90, 140, 70))
    # cyclone: spiral arms over the sea, centred upper-middle
    cx, cy = x + w // 2 + 12, y + 78
    d.ellipse([cx - 88, cy - 88, cx + 88, cy + 88], fill=(52, 120, 160))
    for off in (0, 2.094, 4.189):
        pts = []
        for i in range(61):
            t = off + i / 60 * 4.6
            r = 12 + 72 * i / 60
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        d.line(pts, fill=(255, 255, 255), width=7, joint="curve")
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(230, 245, 250))
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(180, 215, 235))
    # rain streaks
    for rx, ry in [(16, 30), (40, 60), (170, 24), (188, 58), (150, 150),
                   (24, 120)]:
        d.line([x + rx, y + ry, x + rx - 6, y + ry + 14],
               fill=(190, 220, 240), width=2)
    # clouds
    for cx2, cy2, r in [(30, 18, 16), (52, 14, 12), (170, 12, 14)]:
        d.ellipse([x + cx2 - r, y + cy2 - r // 2, x + cx2 + r, y + cy2 + r // 2],
                  fill=(235, 240, 245))


def scene_nasdaq(d, x, y, w, h):
    """Market crash: red candles falling over the exchange floor."""
    # dark board
    d.rectangle([x, y, x + w, y + h], fill=(28, 28, 34))
    # faint grid
    for gy in range(y + 24, y + h - 40, 24):
        d.line([x + 8, gy, x + w - 8, gy], fill=(52, 52, 60), width=1)
    # candles descending left -> right (kept clear of the arrow)
    tops = [46, 62, 84, 108, 132]
    for i, t in enumerate(tops):
        cx0 = x + 14 + i * 30
        col = (40, 160, 90) if i == 0 else (215, 48, 48)
        d.line([cx0 + 9, y + t - 12, cx0 + 9, y + t + 30],
               fill=col, width=2)
        d.rectangle([cx0, y + t, cx0 + 18, y + t + 26], fill=col)
    # slim red down arrow in the clear right half
    d.polygon([(x + 158, y + 92), (x + 174, y + 92), (x + 174, y + 126),
               (x + 192, y + 126), (x + 166, y + 162), (x + 140, y + 126),
               (x + 158, y + 126)], fill=(230, 50, 50))
    d.polygon([(x + 158, y + 92), (x + 174, y + 92), (x + 174, y + 126),
               (x + 192, y + 126), (x + 166, y + 162), (x + 140, y + 126),
               (x + 158, y + 126)], outline=(255, 120, 120), width=2)
    # exchange floor silhouette
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(14, 14, 18))
    for px in range(x + 10, x + w - 10, 34):
        d.rectangle([px, y + h - 52, px + 12, y + h - 34], fill=(14, 14, 18))
    d.rectangle([x + 10, y + h - 56, x + w - 10, y + h - 52],
                fill=(14, 14, 18))
    # ticker screen
    d.rectangle([x + w - 62, y + h - 30, x + w - 10, y + h - 6],
                fill=(180, 30, 30))
    d.text((x + w - 56, y + h - 28), "-5.3%", font=f(11, True),
           fill=(255, 255, 255))


def scene_cop31(d, x, y, w, h):
    """COP31 assembly hall: flags, globe, desks, podium."""
    # hall walls
    d.rectangle([x, y, x + w, y + h], fill=(232, 214, 176))
    d.rectangle([x, y, x + w, y + 34], fill=(120, 60, 40))
    # flags along the back wall
    flag_cols = [(0, 90, 180), (200, 40, 40), (30, 130, 60), (230, 180, 40),
                 (90, 60, 140), (220, 120, 30)]
    for i, col in enumerate(flag_cols):
        fx = x + 14 + i * 32
        d.line([fx, y + 34, fx, y + 62], fill=(90, 70, 50), width=2)
        d.rectangle([fx, y + 38, fx + 22, y + 54], fill=col)
    # globe centre-back, raised clear of the desk rows
    gx, gy, gr = x + w // 2, y + 72, 30
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(40, 110, 180))
    d.ellipse([gx - 14, gy - 20, gx + 2, gy - 2], fill=(70, 160, 80))
    d.ellipse([gx + 4, gy + 6, gx + 20, gy + 22], fill=(70, 160, 80))
    d.ellipse([gx - 20, gy + 8, gx - 6, gy + 18], fill=(70, 160, 80))
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=(20, 60, 110),
              width=2)
    # podium
    d.polygon([(gx - 26, y + h - 52), (gx + 26, y + h - 52),
               (gx + 34, y + h - 6), (gx - 34, y + h - 6)], fill=(90, 50, 30))
    d.rectangle([gx - 26, y + h - 56, gx + 26, y + h - 50], fill=(140, 80, 40))
    # desk rows (perspective trapezoids), below the globe
    for row, (ry, rh, inset) in enumerate([(y + h - 104, 16, 30),
                                           (y + h - 80, 18, 16),
                                           (y + h - 52, 20, 4)]):
        d.polygon([(x + inset, ry), (x + w - inset, ry),
                   (x + w - inset - 6, ry + rh), (x + inset + 6, ry + rh)],
                  fill=(150, 110, 70) if row % 2 == 0 else (130, 95, 60))
        # delegates: small heads
        for dx in range(x + inset + 18, x + w - inset - 18, 26):
            d.ellipse([dx - 5, ry - 10, dx + 5, ry], fill=(240, 200, 160))

# ---- CARD SCENES (each ~58x58, bold shapes only) --------------------------

def scene_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 30, 40))
    d.ellipse([x + 8, y + 8, x + w - 8, y + h - 8], fill=(240, 180, 40))
    d.ellipse([x + 12, y + 12, x + w - 12, y + h - 12], outline=(180, 120, 20),
              width=2)
    d.text((x + 19, y + 14), "B", font=f(26, True), fill=(120, 70, 0))
    d.line([x + 24, y + 12, x + 24, y + h - 12], fill=(120, 70, 0), width=2)
    d.line([x + 32, y + 12, x + 32, y + h - 12], fill=(120, 70, 0), width=2)
    d.polygon([(x + w - 16, y + 6), (x + w - 2, y + 6), (x + w - 9, y + 18)],
              fill=(220, 50, 50))


def scene_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(140, 190, 220))
    d.rectangle([x, y, x + w, y + 14], fill=(250, 220, 160))
    # smoke + flame on deck
    for sx, sy, r in [(30, 16, 7), (38, 10, 5), (24, 10, 4)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(120, 120, 120))
    burst(d, x + 34, y + 24, 9, (255, 120, 30))
    burst(d, x + 34, y + 24, 5, (255, 210, 90))
    # hull
    d.polygon([(x + 4, y + 34), (x + w - 4, y + 34), (x + w - 12, y + 48),
               (x + 12, y + 48)], fill=(150, 40, 30))
    d.rectangle([x + 34, y + 24, x + 46, y + 34], fill=(240, 240, 240))
    # sea
    d.line([x + 2, y + 50, x + w - 2, y + 50], fill=(30, 90, 140), width=3)
    d.line([x + 6, y + 54, x + w - 6, y + 54], fill=(30, 90, 140), width=2)


def scene_houthi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 160, 80))
    d.ellipse([x + w - 22, y + 4, x + w - 4, y + 22], fill=(255, 230, 160))
    # missile diagonal
    d.line([x + 8, y + h - 8, x + 40, y + 12], fill=(80, 80, 90), width=6)
    d.polygon([(x + 40, y + 12), (x + 50, y + 16), (x + 42, y + 22)],
              fill=(80, 80, 90))
    burst(d, x + 8, y + h - 8, 10, (255, 200, 60))
    # port cranes
    d.line([x + 44, y + h, x + 44, y + 30], fill=(40, 40, 50), width=3)
    d.line([x + 44, y + 30, x + 56, y + 34], fill=(40, 40, 50), width=3)
    d.line([x + 52, y + h, x + 52, y + 40], fill=(40, 40, 50), width=2)
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(60, 50, 40))


def scene_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 50, 130))
    for i in range(12):
        a = -math.pi / 2 + i * math.pi / 6
        sx = x + w // 2 + 18 * math.cos(a)
        sy = y + h // 2 + 18 * math.sin(a)
        star5(d, sx, sy, 4, 2, (255, 215, 0))
    d.text((x + 22, y + 18), "€", font=f(22, True), fill=(255, 215, 0))


def scene_memorial(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 36, 52))
    d.ellipse([x + 10, y + 8, x + w - 10, y + h - 8], outline=(150, 130, 170),
              width=2)
    candle(d, x + 24, y + 26, 10, 22, (245, 240, 225))
    # small flower
    d.line([x + 44, y + 48, x + 44, y + 30], fill=(60, 140, 70), width=2)
    for dx, dy in [(44, 26), (38, 30), (50, 30), (40, 24), (48, 24)]:
        d.ellipse([x + dx - 3, y + dy - 3, x + dx + 3, y + dy + 3],
                  fill=(200, 90, 140))


def scene_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 200, 180))
    # pediment + columns
    d.polygon([(x + 6, y + 20), (x + w // 2, y + 8), (x + w - 6, y + 20)],
              fill=(120, 100, 80))
    for cx0 in (14, 26, 38):
        d.rectangle([x + cx0, y + 22, x + cx0 + 5, y + 44], fill=(240, 235, 220))
    d.rectangle([x + 8, y + 44, x + w - 8, y + 48], fill=(120, 100, 80))
    d.rectangle([x + 4, y + 48, x + w - 4, y + 52], fill=(100, 85, 70))
    # gavel
    d.rectangle([x + 40, y + 26, x + 52, y + 32], fill=(90, 60, 30))
    d.line([x + 46, y + 32, x + 54, y + 46], fill=(90, 60, 30), width=3)


def scene_tesla(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 225, 240))
    # road
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(70, 70, 78))
    d.line([x + 4, y + h - 6, x + w - 4, y + h - 6], fill=(255, 255, 255),
           width=2)
    # car silhouette (red)
    d.polygon([(x + 6, y + 38), (x + 12, y + 28), (x + 24, y + 24),
               (x + 38, y + 24), (x + 46, y + 30), (x + 52, y + 38),
               (x + 52, y + 44), (x + 6, y + 44)], fill=(200, 30, 30))
    d.polygon([(x + 16, y + 28), (x + 24, y + 25), (x + 36, y + 25),
               (x + 42, y + 30), (x + 16, y + 30)], fill=(180, 220, 240))
    for wx in (14, 42):
        d.ellipse([x + wx - 5, y + 40, x + wx + 5, y + 50], fill=(20, 20, 20))
        d.ellipse([x + wx - 2, y + 43, x + wx + 2, y + 47], fill=(150, 150, 150))
    # lightning bolt
    d.polygon([(x + 44, y + 6), (x + 52, y + 6), (x + 46, y + 16),
               (x + 52, y + 16), (x + 40, y + 30), (x + 45, y + 17),
               (x + 39, y + 17)], fill=(255, 210, 40))


def scene_ronaldo(d, x, y, w, h):
    # pitch
    d.rectangle([x, y, x + w, y + h], fill=(50, 150, 70))
    d.line([x, y + h - 14, x + w, y + h - 14], fill=(255, 255, 255), width=2)
    # goal posts
    d.rectangle([x + 38, y + 8, x + 40, y + 30], fill=(255, 255, 255))
    d.rectangle([x + 38, y + 8, x + 56, y + 10], fill=(255, 255, 255))
    d.rectangle([x + 54, y + 8, x + 56, y + 30], fill=(255, 255, 255))
    # player figure (red shirt) kicking
    d.ellipse([x + 16, y + 14, x + 24, y + 22], fill=(240, 200, 160))
    d.line([x + 20, y + 22, x + 22, y + 38], fill=(200, 30, 30), width=5)
    d.line([x + 22, y + 26, x + 12, y + 34], fill=(200, 30, 30), width=4)
    d.line([x + 22, y + 26, x + 30, y + 30], fill=(200, 30, 30), width=4)
    d.line([x + 22, y + 38, x + 16, y + 50], fill=(20, 20, 60), width=4)
    d.line([x + 22, y + 38, x + 34, y + 44], fill=(20, 20, 60), width=4)
    # ball mid-flight
    d.ellipse([x + 36, y + 40, x + 44, y + 48], fill=(255, 255, 255))
    d.ellipse([x + 39, y + 43, x + 41, y + 45], fill=(30, 30, 30))


def scene_sanction(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 230, 220))
    # oil barrel
    d.rectangle([x + 18, y + 14, x + 40, y + 48], fill=(40, 40, 46))
    d.rectangle([x + 18, y + 20, x + 40, y + 24], fill=(120, 120, 130))
    d.rectangle([x + 18, y + 40, x + 40, y + 44], fill=(120, 120, 130))
    d.ellipse([x + 18, y + 10, x + 40, y + 18], fill=(70, 70, 80))
    # ban circle + slash
    d.ellipse([x + 8, y + 6, x + 50, y + 52], outline=(210, 30, 30), width=5)
    d.line([x + 12, y + 48, x + 46, y + 10], fill=(210, 30, 30), width=5)


def scene_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 200, 160))
    # tilted buildings
    d.polygon([(x + 6, y + 44), (x + 14, y + 14), (x + 26, y + 16),
               (x + 20, y + 44)], fill=(140, 110, 80))
    d.polygon([(x + 30, y + 44), (x + 36, y + 22), (x + 48, y + 24),
               (x + 44, y + 44)], fill=(110, 85, 60))
    # crack zigzag across the ground
    d.line([(x + 2, y + 46), (x + 14, y + 52), (x + 22, y + 47),
            (x + 34, y + 53), (x + 44, y + 48), (x + 56, y + 52)],
           fill=(60, 40, 20), width=3, joint="curve")
    # dust clouds
    for dx, dy, r in [(12, 30, 6), (44, 34, 7), (30, 26, 5)]:
        d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r],
                  fill=(200, 180, 150))


def scene_euuk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 240, 245))
    # EU flag
    d.line([x + 8, y + 8, x + 8, y + 50], fill=(90, 70, 50), width=2)
    d.rectangle([x + 8, y + 10, x + 26, y + 24], fill=(20, 50, 130))
    for i in range(6):
        a = -math.pi / 2 + i * math.pi / 3
        star5(d, x + 17 + 5 * math.cos(a), y + 17 + 4 * math.sin(a), 2, 1,
              (255, 215, 0))
    # UK flag (simplified)
    d.line([x + 34, y + 8, x + 34, y + 50], fill=(90, 70, 50), width=2)
    d.rectangle([x + 34, y + 10, x + 52, y + 24], fill=(20, 50, 130))
    d.line([x + 34, y + 17, x + 52, y + 17], fill=(255, 255, 255), width=3)
    d.line([x + 43, y + 10, x + 43, y + 24], fill=(255, 255, 255), width=3)
    d.line([x + 34, y + 17, x + 52, y + 17], fill=(200, 30, 30), width=1)
    d.line([x + 43, y + 10, x + 43, y + 24], fill=(200, 30, 30), width=1)
    # handshake arc
    d.arc([x + 10, y + 34, x + 48, y + 54], 0, 180, fill=(40, 120, 60), width=3)


def scene_un(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 225, 240))
    # globe
    d.ellipse([x + 16, y + 4, x + 42, y + 30], fill=(40, 110, 180))
    d.ellipse([x + 22, y + 10, x + 32, y + 18], fill=(70, 160, 80))
    d.ellipse([x + 28, y + 20, x + 38, y + 27], fill=(70, 160, 80))
    # ballot box
    d.rectangle([x + 12, y + 32, x + 46, y + 52], fill=(30, 90, 160))
    d.rectangle([x + 12, y + 32, x + 46, y + 37], fill=(20, 70, 130))
    d.line([x + 24, y + 34, x + 34, y + 34], fill=(10, 40, 80), width=2)
    # ballot paper going in
    d.polygon([(x + 24, y + 18), (x + 34, y + 18), (x + 34, y + 34),
               (x + 24, y + 34)], fill=(255, 255, 255))
    d.line([x + 27, y + 24, x + 31, y + 24], fill=(200, 30, 30), width=2)

# ---- CONTENT (48 stories, Friday 20 Nov 2026) -----------------------------

LEADS = [
    ("UKRAINE · WAR", "110+ MISSILES HIT KYIV IN BIGGEST RAID",
     "110+ MISSILES · 27 BALLISTIC",
     "400+ drones overnight; 9 dead; 3 Dnipro bridges hit; "
     "Russian debris enters Poland.", scene_kyiv, (178, 34, 34)),
    ("INDIA · CYCLONE", "CYCLONE AKVAN SLAMS INDIA'S EAST COAST",
     "300K+ EVACUATED · 02:00 UTC",
     "Landfall near Gopalpur; 9,341 shelters open; "
     "1,317 babies born in shelters.", scene_akvan, (24, 90, 130)),
    ("MARKETS · CRASH", "NASDAQ −5.3%: WORST WEEK SINCE APRIL 2025",
     "S&P −3.7% · KOSPI −5.2%",
     "Gold −2.4% · Brent +0.6% · Sensex +1.1% — Nvidia −14% on SEC "
     "probe; Anthropic −8.5%.", scene_nasdaq, (150, 30, 30)),
    ("CLIMATE · COP31", "COP31 IN OVERTIME AS FOSSIL-FUEL TALKS DRAG",
     "35% ELECTRICITY BY 2035",
     "Panama threatens veto; 12 nations write in; island states: "
     "failure if 1.5°C ignored.", scene_cop31, (90, 110, 40)),
]

CARDS = [
    ("BITCOIN SLIPS BELOW $60,000", "First time since July; low $55,830",
     scene_bitcoin, (240, 180, 40)),
    ("TANKER HIT OFF OMAN COAST", "Unknown projectile; fire, no casualties",
     scene_tanker, (150, 40, 30)),
    ("HOUTHIS THREATEN RED SEA PORTS", "Saudi-led coalition strikes Yemen ports",
     scene_houthi, (220, 100, 40)),
    ("EU APPROVES €1BN UKRAINE AID", "Part of €6.6bn political deal",
     scene_eu, (20, 50, 130)),
    ("SOUTH AFRICA MOURNS MLAMBO-NGCUKA", "Former deputy president dies at 71",
     scene_memorial, (90, 80, 120)),
    ("SYDNEY MAN CHARGED OVER ISIS PLOT", "Alleged ISIS material; car-bomb research",
     scene_court, (120, 100, 80)),
    ("TESLA DRIVER ASSIST CLEARED IN ITALY", "First big EU state to approve",
     scene_tesla, (200, 30, 30)),
    ("RONALDO SCORES GOAL 986", "Al-Ahli 3–1 Al-Nassr (SPL tally)",
     scene_ronaldo, (50, 150, 70)),
    ("US SANCTIONS FOUR IRAN 'OIL TRUSTEES'", "Operation Economic Outcast",
     scene_sanction, (178, 34, 34)),
    ("PERU SHAKEN BY 6.7 QUAKE", "Junín, 108 km deep; no casualties",
     scene_quake, (150, 110, 60)),
    ("EU–UK SUMMIT EASES TRADE", "Youth mobility 100,000 a side",
     scene_euuk, (20, 50, 130)),
    ("UN CHIEF RACE DEADLOCKED", "Grynspan leads; 2 vetoes, states undisclosed",
     scene_un, (30, 90, 160)),
]

ALSO_ON = [
    "Estonia closes Russia crossings from Dec 1",
    "US–China: humans must decide AI arms",
    "Japan: 93% say China ties bad, worst since 1986",
    "SCO forum opens in Delhi; Pakistan minister visits",
    "Canada, Australia, NZ: joint plea for ceasefire",
    "Iraq retakes Hezbollah stronghold, no resistance",
    "Nvidia −14%, ~$491bn lost; SEC probes accounting",
    "Xi meets Albanese in Shenzhen; ties 'turn around'",
    "ECB: Boone & Brunnermeier picked for top jobs",
    "BYD Ti7 banned in EU over Defender design",
    "Tesla opens first Argentina store in Buenos Aires",
    "Las Vegas GP: Russell fastest in FP3",
    "Gold −2.4% to $3,538, lowest since September",
    "Michigan sentiment 51.5; Bessent warns Fed",
    "Tesla plans $3.1bn polysilicon plant in Texas",
    "Russian missiles enter Poland airspace",
    "Kyiv hits 3 Russian launchers, Smolensk plant",
    "South Africa crime stats: 5,590 murders in quarter",
    "Venezuela rejects ICJ ruling on Esequibo",
    "KOSPI −5.2% to 4,869.96, lowest since January",
    "Brent +0.6% to $92.57, third weekly loss",
    "SpaceX launches secret USSF-317 mission",
    "OpenAI: new usage rules take effect today",
    "Island states: COP31 'a failure' if 1.5°C ignored",
    "Tech rout: Broadcom −12%, AMD −13%, Meta −6%",
    "Anthropic −8.5% a day after record IPO",
    "'Chapo Isidro' arrested in Mexico after shootout",
    "Iran claims 14 tankers at Kharg; trackers dispute",
    "Bolsonaro, 71, taken to hospital in Brazil",
    "Brazil storm kills 3, destroys ~5,000 homes",
    "Samsung names Hwang Sang-joon memory chief",
    "Sensex +1.1% against the global tide",
]

TIMELINE = ("02:00 AKVAN · 06:10 SYDNEY · 10:00 SENSEX +1.1% "
            "· 14:50 EU €1BN · 15:00 KHASAB · 15:42 BTC <$60K "
            "· 16:35 ECB · 19:09 PERU · 19:10 KHARG "
            "· 21:00 NASDAQ −5.3%")

NOTE = ("Every story below happened or was first reported "
        "on Friday 20 November 2026.")

DATECHECK = ("Deliberately left out (wrong day): Sudan report "
             "(17 Nov) · Turkey $26bn (16 Nov) · Colombia seizure (19 Nov) · "
             "Egypt–Syria flights (17 Nov) · AWS Chile (11 Nov) · "
             "Korea $1tn (19 Nov).")

ACCENTS = [(178, 34, 34), (24, 90, 130), (150, 110, 40), (34, 120, 60),
           (90, 60, 140), (200, 100, 30)]


def check_fit():
    """Fail loudly if any text overflows its box (measured, not guessed)."""
    problems = []
    if f(30, True).getlength("FRIDAY 20 NOVEMBER 2026") > 620:
        problems.append("date too wide")
    if f(13, True).getlength("WORLD EDITION") > 200:
        problems.append("world edition too wide")
    if f(11).getlength(NOTE) > 1000:
        problems.append("note too wide")
    if f(10, True).getlength(TIMELINE) > 1000:
        problems.append("timeline too wide")
    for kicker, head, stat, detail, _fn, _c in LEADS:
        if len(wrap(head, f(19, True), 290)) > 2:
            problems.append("lead headline >2 lines: " + head)
        if len(wrap(detail, f(11), 290)) > 3:
            problems.append("lead detail >3 lines: " + head)
    for head, detail, _fn, _c in CARDS:
        if len(wrap(head, f(12, True), 176)) > 2:
            problems.append("card headline >2 lines: " + head)
        if len(wrap(detail, f(10), 176)) > 2:
            problems.append("card detail >2 lines: " + head)
    for item in ALSO_ON:
        if f(10).getlength(item) > 486:
            problems.append("also-on too wide: " + item)
    if f(10).getlength(DATECHECK) > 992:
        problems.append("datecheck too wide")
    if problems:
        raise SystemExit("FIT FAIL:\n" + "\n".join(problems))


def render():
    check_fit()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 84], fill=NAVY)
    d.text((16, 8), "THE FRIDAY PAPER", font=f(13, True), fill=GOLD)
    d.text((16, 30), "FRIDAY 20 NOVEMBER 2026", font=f(30, True), fill=GOLD)
    # right side, right-aligned to x=1000 (24 px safe margin)
    we = f(13, True).getlength("WORLD EDITION")
    d.text((1000 - we, 10), "WORLD EDITION", font=f(13, True), fill=WHITE)
    s48 = f(11, True).getlength("48 STORIES · ONE DAY")
    d.text((1000 - s48, 34), "48 STORIES · ONE DAY", font=f(11, True),
           fill=(200, 210, 225))
    d.rectangle([0, 84, W, 86], fill=GOLD)

    # ---- editor's note ---------------------------------------------------
    nw = f(11).getlength(NOTE)
    d.text(((W - nw) // 2, 90), NOTE, font=f(11), fill=(70, 70, 70))

    # ---- timeline strip --------------------------------------------------
    d.rectangle([0, 108, W, 132], fill=LGREY)
    tw = f(10, True).getlength(TIMELINE)
    d.text(((W - tw) // 2, 115), TIMELINE, font=f(10, True), fill=NAVY)

    # ---- leads 2x2 -------------------------------------------------------
    for i, (kicker, head, stat, detail, scene_fn, accent) in enumerate(LEADS):
        px = 8 + (i % 2) * 504
        py = 138 + (i // 2) * 208
        d.rectangle([px, py, px + 506, py + 204], fill=WHITE,
                    outline=(200, 198, 190), width=1)
        d.rectangle([px, py, px + 506, py + 5], fill=accent)
        scene_fn(d, px + 2, py + 7, 200, 195)
        tx = px + 210
        d.text((tx, py + 14), kicker, font=f(11, True), fill=accent)
        y = py + 34
        for line in wrap(head, f(19, True), 290):
            d.text((tx, y), line, font=f(19, True), fill=INK)
            y += 22
        y += 4
        d.text((tx, y), stat, font=f(11, True), fill=accent)
        y += 20
        for line in wrap(detail, f(11), 290):
            d.text((tx, y), line, font=f(11), fill=(50, 50, 50))
            y += 14

    # ---- cards 4x3 -------------------------------------------------------
    for i, (head, detail, scene_fn, accent) in enumerate(CARDS):
        px = 8 + (i % 4) * 253
        py = 560 + (i // 4) * 70
        d.rectangle([px, py, px + 247, py + 64], fill=WHITE,
                    outline=(200, 198, 190), width=1)
        d.rectangle([px, py, px + 4, py + 64], fill=accent)
        scene_fn(d, px + 7, py + 3, 58, 58)
        tx = px + 71
        y = py + 6
        for line in wrap(head, f(12, True), 172):
            d.text((tx, y), line, font=f(12, True), fill=INK)
            y += 14
        y += 1
        for line in wrap(detail, f(10), 172):
            d.text((tx, y), line, font=f(10), fill=(80, 80, 80))
            y += 12

    # ---- also-on ---------------------------------------------------------
    d.text((8, 776), "ALSO ON FRIDAY — 32 MORE STORIES", font=f(11, True),
           fill=NAVY)
    d.line([8, 792, 1016, 792], fill=NAVY, width=1)
    for i, item in enumerate(ALSO_ON):
        col = i % 2
        row = i // 2
        ax = 8 + col * 510
        ay = 798 + row * 10
        d.ellipse([ax, ay + 2, ax + 5, ay + 7], fill=ACCENTS[i % len(ACCENTS)])
        d.text((ax + 10, ay), item, font=f(10), fill=(40, 40, 40))

    # ---- DATE CHECK footer -------------------------------------------------
    d.rectangle([8, 962, 1016, 1018], fill=PINKBG, outline=(200, 120, 120),
                width=1)
    d.text((20, 970), "DATE CHECK", font=f(11, True), fill=RED)
    d.text((20, 988), DATECHECK, font=f(10), fill=(90, 30, 30))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    pal = img.quantize(colors=256, method=Image.MEDIANCUT,
                       dither=Image.Dither.NONE)
    pal.save(out, optimize=True)
    return out


if __name__ == "__main__":
    print(render())
