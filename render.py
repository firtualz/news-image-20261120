#!/usr/bin/env python3
"""v12 renderer — news-image-20261120. Fresh design: HERO + THREE LEADS + SCENE GRID + WORLD BRIEF.

One day of world news, Friday 20 November 2026. 48 verified stories:
hero (Kyiv) + 3 leads (Iran sanctions, markets rout, COP31) + 12 illustrated
cards + 32 also-on as a world brief. Drawn from scratch with PIL primitives.
No external images, no network. Deterministic output.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette ---
PAPER = (246, 241, 230)
CARD = (255, 253, 246)
INK = (26, 26, 26)
NAVY = (13, 27, 62)
NAVY2 = (20, 42, 92)
GOLD = (217, 164, 65)
GOLD_D = (176, 124, 32)
RED = (192, 57, 43)
RED_D = (150, 40, 30)
GREEN = (39, 120, 70)
GRAY = (90, 90, 90)
LINE = (200, 192, 175)
WHITE = (255, 255, 255)

F_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def wrap(d, text, f, max_w):
    """Greedy word wrap. Returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_w(d, text, f):
    return d.textlength(text, font=f)


def star5(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def arrow(d, x1, y1, x2, y2, width, color):
    """Thick arrow from (x1,y1) to (x2,y2) with a triangular head."""
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln == 0:
        return
    ux, uy = dx / ln, dy / ln
    px, py = -uy, ux
    hw = width / 2.0
    hl = min(26.0, ln * 0.45)  # head length
    hb = width * 1.9 / 2.0     # head half-width
    bx, by = x2 - ux * hl, y2 - uy * hl
    shaft = [
        (x1 + px * hw, y1 + py * hw),
        (bx + px * hw, by + py * hw),
        (bx + px * hb, by + py * hb),
        (x2, y2),
        (bx - px * hb, by - py * hb),
        (bx - px * hw, by - py * hw),
    ]
    d.polygon(shaft, fill=color)


def eu_flag(d, x, y, w, h):
    """EU flag: blue field, ring of TWELVE gold stars. (v11 drew 6 in rows.)"""
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    cx, cy = x + w / 2.0, y + h / 2.0
    rr = min(w, h) * 0.36
    for i in range(12):
        ang = -math.pi / 2 + i * (2 * math.pi / 12)
        star5(d, cx + rr * math.cos(ang), cy + rr * math.sin(ang),
              max(1.6, min(w, h) * 0.055), (255, 204, 0))


def union_jack(d, x, y, w, h):
    """Union Jack: blue field, white saltire, red saltire, white cross, red cross.
    NOT a Nordic cross (v11 drew Iceland by mistake)."""
    d.rectangle([x, y, x + w, y + h], fill=(1, 33, 105))
    # white saltire (diagonals)
    dw = max(3, int(h * 0.28))
    d.polygon([(x, y), (x + dw, y), (x + w, y + h), (x + w - dw, y + h)], fill=WHITE)
    d.polygon([(x + w, y), (x + w - dw, y), (x, y + h), (x + dw, y + h)], fill=WHITE)
    # red saltire (thinner, centred)
    rw = max(2, int(h * 0.12))
    d.polygon([(x, y), (x + rw, y), (x + w, y + h), (x + w - rw, y + h)], fill=(200, 16, 46))
    d.polygon([(x + w, y), (x + w - rw, y), (x, y + h), (x + rw, y + h)], fill=(200, 16, 46))
    # white cross
    cw, ch = max(3, int(w * 0.20)), max(3, int(h * 0.34))
    d.rectangle([x + w / 2 - cw / 2, y, x + w / 2 + cw / 2, y + h], fill=WHITE)
    d.rectangle([x, y + h / 2 - ch / 2, x + w, y + h / 2 + ch / 2], fill=WHITE)
    # red cross (thinner)
    cw2, ch2 = max(2, int(w * 0.11)), max(2, int(h * 0.20))
    d.rectangle([x + w / 2 - cw2 / 2, y, x + w / 2 + cw2 / 2, y + h], fill=(200, 16, 46))
    d.rectangle([x, y + h / 2 - ch2 / 2, x + w, y + h / 2 + ch2 / 2], fill=(200, 16, 46))


def vgrad(img, box, top, bottom):
    """Vertical gradient fill inside box."""
    x0, y0, x1, y1 = box
    n = max(1, y1 - y0)
    for i in range(n):
        t = i / n
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        ImageDraw.Draw(img).line([(x0, y0 + i), (x1, y0 + i)], fill=c)

# ---------------------------------------------------------------- scenes
def scene_kyiv(img, x, y, w, h):
    """HERO: Kyiv night raid. Sky, moon, missile trails, explosions, skyline,
    river, and a Dnipro bridge with a BROKEN span (the news, not decoration)."""
    vgrad(img, (x, y, x + w, y + h), (8, 14, 40), (28, 46, 92))
    d = ImageDraw.Draw(img)
    rng = random.Random(20261120)
    for _ in range(28):
        sx = x + rng.randint(4, w - 4)
        sy = y + rng.randint(4, int(h * 0.55))
        r = rng.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(220, 220, 240))
    # crescent moon, top right
    mx, my, mr = x + w - 90, y + 26, 17
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(240, 236, 210))
    d.ellipse([mx - mr + 9, my - mr - 3, mx + mr + 9, my + mr - 3], fill=(10, 18, 46))
    # missile trails: three bright streaks diving steeply toward the city
    for (sx, sy, ex, ey) in [(x + 90, y + 8, x + 300, y + 118),
                             (x + 420, y + 4, x + 560, y + 108),
                             (x + 700, y + 10, x + 830, y + 122)]:
        mxp, myp = (sx + ex) / 2, (sy + ey) / 2 - 6
        pts = []
        for t_i in range(21):
            t = t_i / 20.0
            px = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mxp + t * t * ex
            py = (1 - t) ** 2 * sy + 2 * (1 - t) * t * myp + t * t * ey
            pts.append((px, py))
        d.line(pts, fill=(250, 210, 110), width=5)
        d.line(pts, fill=(255, 245, 200), width=2)
        d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(255, 240, 180))
    # skyline silhouette with lit windows
    base = y + h - 46
    rng2 = random.Random(77)
    bx = x
    while bx < x + w - 30:
        bw = rng2.randint(34, 70)
        bh = rng2.randint(22, 58)
        d.rectangle([bx, base - bh, bx + bw, base], fill=(6, 10, 28))
        for wy in range(base - bh + 6, base - 6, 12):
            for wx in range(bx + 6, bx + bw - 6, 12):
                if rng2.random() < 0.45:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 205, 90))
        bx += bw + 4
    # explosions: orange bursts over the rooftops (drawn after the skyline)
    for (ex, ey, r) in [(x + 300, y + 128, 32), (x + 830, y + 132, 36)]:
        for rr, col in [(r, (220, 80, 20)), (int(r * 0.66), (245, 140, 30)),
                        (int(r * 0.38), (255, 210, 90))]:
            d.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=col)
        for k in range(8):
            ang = k * math.pi / 4
            d.polygon([(ex, ey),
                       (ex + (r + 12) * math.cos(ang - 0.12), ey + (r + 12) * math.sin(ang - 0.12)),
                       (ex + (r + 12) * math.cos(ang + 0.12), ey + (r + 12) * math.sin(ang + 0.12))],
                      fill=(245, 140, 30))
    # river band
    d.rectangle([x, base, x + w, y + h], fill=(16, 34, 78))
    d.line([(x, base + 10), (x + w, base + 10)], fill=(70, 110, 180), width=2)
    d.line([(x, base + 26), (x + w, base + 26)], fill=(50, 85, 150), width=2)
    # Dnipro bridge, BROKEN span: left deck level, right deck tilted into water
    by = base - 8
    d.rectangle([x + 120, by - 3, x + 470, by + 3], fill=(120, 120, 130))
    d.polygon([(x + 470, by - 3), (x + 560, by + 26), (x + 560, by + 32),
               (x + 470, by + 3)], fill=(120, 120, 130))
    d.rectangle([x + 660, by - 3, x + 940, by + 3], fill=(120, 120, 130))
    for tx in (x + 150, x + 640, x + 900):
        d.rectangle([tx, by - 26, tx + 6, by + 3], fill=(150, 150, 160))
    d.line([(x + 470, by), (x + 560, by + 28)], fill=(255, 210, 90), width=2)


def scene_sanctions(img, x, y, w, h):
    """C9 lead: oil barrels + sealed official document + red prohibition ring.
    Sanctions paperwork, NOT an attack scene."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(38, 52, 66))
    d.rectangle([x, y, x + w, y + 4], fill=GOLD)
    # oil barrels, left
    for i, bx in enumerate((x + 18, x + 78)):
        d.rectangle([bx, y + 52, bx + 46, y + 108], fill=(24, 24, 26))
        d.ellipse([bx, y + 46, bx + 46, y + 60], fill=(52, 52, 56))
        d.ellipse([bx + 8, y + 49, bx + 38, y + 57], fill=(30, 30, 34))
        d.rectangle([bx, y + 70, bx + 46, y + 76], fill=(70, 70, 76))
        d.rectangle([bx + 6, y + 52, bx + 12, y + 108], fill=(90, 90, 96))
    # official document, centre-right
    dx, dy, dw, dh = x + 148, y + 16, 110, 84
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=(245, 242, 232))
    d.rectangle([dx, dy, dx + dw, dy + dh], outline=(150, 140, 120), width=1)
    d.rectangle([dx + 10, dy + 8, dx + dw - 10, dy + 18], fill=(13, 27, 62))
    for k in range(4):
        d.rectangle([dx + 10, dy + 28 + k * 11, dx + dw - 10 - (k * 12), dy + 33 + k * 11],
                    fill=(170, 165, 150))
    d.ellipse([dx + dw - 30, dy + dh - 28, dx + dw - 8, dy + dh - 6], fill=(150, 40, 30))
    star5(d, dx + dw - 19, dy + dh - 17, 6, (255, 220, 120))
    # red prohibition ring over the document (kept inside the scene box)
    cx, cy, r = dx + dw / 2, dy + dh / 2, 52
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(220, 40, 30), width=9)
    d.line([(cx - r * 0.72, cy + r * 0.72), (cx + r * 0.72, cy - r * 0.72)],
           fill=(220, 40, 30), width=9)


def scene_markets(img, x, y, w, h):
    """L3 lead: falling candles + big red DOWN arrow. Numbers in the panel text:
    Nasdaq -5.3% (worst week since Mar 2020), S&P -3.7% (worst since Apr 2025)."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(18, 20, 26))
    d.rectangle([x, y, x + w, y + 4], fill=RED)
    # grid lines
    for gy in range(y + 22, y + h - 8, 18):
        d.line([(x + 8, gy), (x + w - 8, gy)], fill=(38, 42, 54), width=1)
    # candles descending: 1 green, then 4 red
    candles = [(0.30, 0.42, True), (0.42, 0.58, False), (0.55, 0.72, False),
               (0.68, 0.84, False), (0.80, 0.94, False)]
    cw = 26
    for i, (o, c, up) in enumerate(candles):
        cx0 = x + 22 + i * 58
        top = y + 14 + o * (h - 40)
        bot = y + 14 + c * (h - 40)
        col = (60, 170, 90) if up else (220, 60, 45)
        d.line([(cx0 + cw / 2, top - 8), (cx0 + cw / 2, bot + 8)], fill=col, width=2)
        d.rectangle([cx0, top, cx0 + cw, bot], fill=col)
    # big red down arrow across the chart
    arrow(d, x + 30, y + 16, x + w - 26, y + h - 18, 13, (235, 70, 50))
    d.text((x + 12, y + h - 24), "NASDAQ -5.3%", font=font(F_B, 15), fill=WHITE)
    d.text((x + w - 108, y + 10), "S&P -3.7%", font=font(F_B, 14), fill=(255, 210, 120))


def scene_cop31(img, x, y, w, h):
    """L4 lead: COP31 hall — flags on the back wall, globe centre, delegate tables."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(214, 196, 160))
    d.rectangle([x, y, x + w, y + 4], fill=(39, 120, 70))
    # back wall + row of flags
    d.rectangle([x, y + 4, x + w, y + 62], fill=(186, 166, 130))
    flag_cols = [(200, 16, 46), (0, 51, 153), (39, 120, 70), (217, 164, 65),
                 (120, 60, 140), (220, 120, 30), (30, 90, 140), (180, 40, 60)]
    for i, col in enumerate(flag_cols):
        fx = x + 14 + i * 38
        d.line([(fx + 8, y + 12), (fx + 8, y + 52)], fill=(90, 80, 60), width=2)
        d.rectangle([fx + 8, y + 12, fx + 30, y + 28], fill=col)
    # globe centre
    cx, cy, r = x + w / 2, y + 66, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 110, 180))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(20, 70, 130), width=2)
    d.polygon([(cx - 18, cy - 8), (cx - 2, cy - 18), (cx + 12, cy - 10), (cx + 4, cy + 2),
               (cx - 12, cy + 4)], fill=(70, 150, 80))
    d.polygon([(cx - 6, cy + 12), (cx + 10, cy + 10), (cx + 18, cy + 20), (cx + 2, cy + 24),
               (cx - 12, cy + 18)], fill=(70, 150, 80))
    # delegate tables + heads
    for ty in (y + 88, y + 100):
        d.rectangle([x + 16, ty, x + w - 16, ty + 10], fill=(96, 70, 44))
        for hx in range(x + 30, x + w - 20, 34):
            d.ellipse([hx - 5, ty - 12, hx + 5, ty - 2], fill=(60, 45, 35))
    # podium, left
    d.polygon([(x + 8, y + h - 4), (x + 8, y + 96), (x + 44, y + 96), (x + 44, y + h - 4)],
              fill=(70, 55, 40))


def scene_cyclone(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(28, 78, 128))
    cx, cy = x + w / 2, y + h / 2 - 4
    for r, col in [(34, (235, 240, 250)), (26, (200, 215, 235)), (17, (160, 185, 220))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=300, fill=col, width=6)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(240, 245, 250))
    d.polygon([(x, y + h - 14), (x + 26, y + h - 30), (x + 52, y + h - 16),
               (x + w, y + h - 24), (x + w, y + h), (x, y + h)], fill=(60, 110, 70))
    for i in range(8):
        rx = x + 6 + i * 10
        d.line([(rx, y + 8), (rx - 4, y + 22)], fill=(190, 210, 235), width=2)


def scene_bitcoin(img, x, y, w, h):
    """C1: gold coin + thick RED DOWN arrow (v11 drew it pointing UP)."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(24, 26, 34))
    cx, cy, r = x + 34, y + 36, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 170, 40))
    d.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4], outline=(180, 120, 20), width=2)
    bf = font(F_B, 30)
    d.text((cx - 9, cy - 20), "B", font=bf, fill=(120, 70, 0))
    d.line([(cx - 2, cy - 24), (cx - 2, cy + 24)], fill=(120, 70, 0), width=3)
    d.line([(cx + 5, cy - 24), (cx + 5, cy + 24)], fill=(120, 70, 0), width=3)
    # DOWN arrow: upper-left -> lower-right, head at bottom-right
    arrow(d, x + 52, y + 12, x + w - 8, y + h - 12, 10, (235, 60, 45))


def scene_tanker(img, x, y, w, h):
    """C2: OIL TANKER — long hull, FLAT deck, no containers (v11 drew a container
    ship). Superstructure at stern, derrick + pipes on deck, smoke + flame."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(150, 190, 220))
    d.rectangle([x, y, x + w, y + 26], fill=(120, 165, 205))
    # sea
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(30, 90, 150))
    d.line([(x, y + h - 16), (x + w, y + h - 16)], fill=(120, 180, 230), width=2)
    # hull: long, flat deck line at top, red bottom
    hx, hy = x + 4, y + 34
    d.polygon([(hx, hy), (hx + 72, hy), (hx + 66, hy + 26), (hx + 6, hy + 26)],
              fill=(28, 28, 32))
    d.polygon([(hx + 2, hy + 18), (hx + 70, hy + 18), (hx + 66, hy + 26), (hx + 6, hy + 26)],
              fill=(150, 40, 30))
    # white superstructure block at stern (right)
    d.rectangle([hx + 52, hy - 16, hx + 70, hy], fill=(240, 240, 235))
    d.rectangle([hx + 55, hy - 12, hx + 60, hy - 8], fill=(30, 60, 110))
    d.rectangle([hx + 63, hy - 12, hx + 68, hy - 8], fill=(30, 60, 110))
    # derrick mast mid-deck + pipes on the flat deck
    d.polygon([(hx + 26, hy), (hx + 30, hy - 20), (hx + 34, hy)], fill=(90, 90, 95))
    d.rectangle([hx + 12, hy - 8, hx + 18, hy], fill=(200, 200, 195))
    d.rectangle([hx + 38, hy - 6, hx + 44, hy], fill=(200, 200, 195))
    # smoke + small flame on deck (the fire)
    for (sx, sy, sr) in [(hx + 44, hy - 14, 7), (hx + 48, hy - 24, 9), (hx + 44, hy - 34, 6)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(110, 110, 115))
    d.polygon([(hx + 40, hy), (hx + 46, hy - 12), (hx + 52, hy)], fill=(245, 140, 30))


def scene_houthi(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(40, 44, 60))
    # port crane silhouette
    d.polygon([(x + 8, y + h - 8), (x + 12, y + 30), (x + 18, y + 30), (x + 20, y + h - 8)],
              fill=(20, 20, 26))
    d.polygon([(x + 12, y + 30), (x + 66, y + 18), (x + 66, y + 24), (x + 16, y + 36)],
              fill=(20, 20, 26))
    d.line([(x + 60, y + 24), (x + 60, y + 44)], fill=(20, 20, 26), width=3)
    d.rectangle([x + 56, y + 44, x + 64, y + 52], fill=(20, 20, 26))
    # missile angled up with flame
    d.polygon([(x + 34, y + 66), (x + 40, y + 34), (x + 46, y + 66)], fill=(220, 220, 225))
    d.polygon([(x + 40, y + 34), (x + 44, y + 26), (x + 48, y + 34)], fill=(220, 220, 225))
    d.polygon([(x + 34, y + 66), (x + 40, y + 76), (x + 46, y + 66)], fill=(245, 140, 30))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(24, 60, 90))


def scene_eu(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    cx, cy = x + w / 2, y + h / 2
    rr = 26
    for i in range(12):
        ang = -math.pi / 2 + i * (2 * math.pi / 12)
        star5(d, cx + rr * math.cos(ang), cy + rr * math.sin(ang), 4.5, (255, 204, 0))
    d.text((cx - 11, cy - 13), "€", font=font(F_B, 24), fill=(255, 204, 0))


def scene_candle(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(52, 44, 60))
    cx = x + w / 2
    d.rectangle([cx - 7, y + 34, cx + 7, y + h - 12], fill=(245, 240, 225))
    d.rectangle([cx - 16, y + h - 12, cx + 16, y + h - 6], fill=(200, 170, 90))
    d.polygon([(cx, y + 8), (cx + 7, y + 28), (cx - 7, y + 28)], fill=(255, 190, 60))
    d.ellipse([cx - 3, y + 16, cx + 3, y + 26], fill=(255, 230, 140))
    # flower: purple petals + yellow centre
    fx, fy = x + w - 20, y + h - 22
    for k in range(6):
        ang = k * math.pi / 3
        d.ellipse([fx + 9 * math.cos(ang) - 5, fy + 9 * math.sin(ang) - 5,
                   fx + 9 * math.cos(ang) + 5, fy + 9 * math.sin(ang) + 5],
                  fill=(150, 90, 170))
    d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=(255, 210, 60))


def scene_court(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(210, 200, 175))
    # courthouse: pediment + columns
    d.polygon([(x + 10, y + 26), (x + w / 2, y + 8), (x + w - 10, y + 26)], fill=(120, 100, 80))
    for cx in (x + 18, x + 36, x + 54):
        d.rectangle([cx, y + 28, cx + 7, y + 62], fill=(245, 240, 225))
    d.rectangle([x + 8, y + 62, x + w - 8, y + 68], fill=(120, 100, 80))
    d.rectangle([x + 6, y + 68, x + w - 6, y + h - 8], fill=(180, 165, 140))
    # gavel, diagonal
    d.rectangle([x + 52, y + 44, x + 76, y + 56], fill=(120, 80, 40))
    d.line([(x + 58, y + 56), (x + 72, y + 74)], fill=(90, 60, 30), width=5)


def scene_tesla(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(30, 34, 44))
    # red car, side profile
    d.polygon([(x + 10, y + 52), (x + 22, y + 40), (x + 44, y + 36), (x + 60, y + 40),
               (x + 72, y + 52), (x + 72, y + 60), (x + 10, y + 60)], fill=(200, 30, 30))
    d.polygon([(x + 26, y + 42), (x + 42, y + 39), (x + 54, y + 42), (x + 54, y + 50),
               (x + 26, y + 50)], fill=(180, 210, 230))
    for wx in (x + 24, x + 58):
        d.ellipse([wx - 7, y + 54, wx + 7, y + 68], fill=(20, 20, 22))
        d.ellipse([wx - 3, y + 58, wx + 3, y + 64], fill=(150, 150, 155))
    d.line([(x, y + 70), (x + w, y + 70)], fill=(90, 90, 100), width=2)
    # lightning bolt
    d.polygon([(x + 58, y + 6), (x + 70, y + 6), (x + 62, y + 22), (x + 70, y + 22),
               (x + 54, y + 40), (x + 60, y + 24), (x + 52, y + 24)], fill=(255, 210, 60))


def scene_ronaldo(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(60, 130, 70))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(45, 105, 55))
    # goal frame + net
    d.rectangle([x + w - 30, y + 14, x + w - 6, y + 52], outline=WHITE, width=3)
    for ny in range(y + 20, y + 50, 8):
        d.line([(x + w - 30, ny), (x + w - 6, ny)], fill=(230, 230, 230), width=1)
    # player silhouette kicking
    d.ellipse([x + 22, y + 30, x + 32, y + 40], fill=(20, 20, 26))  # head
    d.line([(x + 27, y + 40), (x + 24, y + 58)], fill=(20, 20, 26), width=6)  # body
    d.line([(x + 24, y + 58), (x + 18, y + 72)], fill=(20, 20, 26), width=5)  # standing leg
    d.line([(x + 24, y + 52), (x + 42, y + 60)], fill=(20, 20, 26), width=5)  # kicking leg
    d.line([(x + 26, y + 44), (x + 14, y + 50)], fill=(20, 20, 26), width=4)  # arm
    # ball mid-flight toward goal
    d.ellipse([x + 48, y + 52, x + 56, y + 60], fill=WHITE)
    d.ellipse([x + 51, y + 55, x + 53, y + 57], fill=INK)


def scene_quake(img, x, y, w, h):
    """C10: STRAIGHT building, ONE small wall crack, FLAT ground, no ground
    cracks, no collapse (v10/v11 exaggerated the damage)."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(190, 200, 210))
    # straight building, perfectly vertical edges
    bx, by, bw, bh = x + 18, y + 14, 44, 52
    d.rectangle([bx, by, bx + bw, by + bh], fill=(150, 140, 125))
    d.rectangle([bx, by, bx + bw, by + 6], fill=(120, 110, 95))
    for wy in range(by + 12, by + bh - 6, 12):
        for wx in (bx + 7, bx + 21, bx + 35):
            d.rectangle([wx, wy, wx + 6, wy + 7], fill=(60, 70, 90))
    # ONE small zigzag crack on the wall only
    d.line([(bx + 30, by + 26), (bx + 34, by + 32), (bx + 30, by + 38), (bx + 35, by + 44)],
           fill=(70, 60, 50), width=2)
    # flat ground, no cracks
    d.rectangle([x, by + bh, x + w, y + h], fill=(110, 100, 80))
    d.line([(x, by + bh), (x + w, by + bh)], fill=(80, 70, 55), width=2)
    # small seismograph trace at bottom
    pts = [(x + 8, y + h - 12), (x + 20, y + h - 12), (x + 26, y + h - 20),
           (x + 32, y + h - 6), (x + 38, y + h - 14), (x + 48, y + h - 12),
           (x + 72, y + h - 12)]
    d.line(pts, fill=(192, 57, 43), width=2)


def scene_eu_uk(img, x, y, w, h):
    """C11: EU flag (12 stars in a ring) + UNION JACK (blue, white+red saltire
    and cross). v11 drew Iceland + a 6-star EU flag."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(230, 225, 210))
    eu_flag(d, x + 5, y + 12, 36, 24)
    union_jack(d, x + 43, y + 12, 36, 24)
    # gold double-arrow linking the two flags (a deal, not a handshake sketch)
    d.line([(x + 12, y + 52), (x + w - 12, y + 52)], fill=GOLD_D, width=3)
    d.polygon([(x + w - 12, y + 52), (x + w - 20, y + 47), (x + w - 20, y + 57)], fill=GOLD_D)
    d.polygon([(x + 12, y + 52), (x + 20, y + 47), (x + 20, y + 57)], fill=GOLD_D)
    d.text((x + 8, y + 60), "DEAL", font=font(F_B, 12), fill=(39, 120, 70))


def scene_un(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 100))
    # globe
    cx, cy, r = x + 30, y + 32, 22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 160, 210))
    d.polygon([(cx - 14, cy - 6), (cx - 2, cy - 14), (cx + 10, cy - 8), (cx + 4, cy + 2),
               (cx - 10, cy + 4)], fill=(70, 150, 80))
    d.polygon([(cx - 4, cy + 8), (cx + 8, cy + 8), (cx + 12, cy + 16), (cx, cy + 18)],
              fill=(70, 150, 80))
    # ballot box + ballot
    d.rectangle([x + 52, y + 44, x + 76, y + 70], fill=(20, 40, 70))
    d.rectangle([x + 58, y + 44, x + 70, y + 47], fill=(240, 240, 235))
    d.polygon([(x + 60, y + 44), (x + 66, y + 30), (x + 72, y + 44)], fill=(240, 240, 235))
    d.text((x + 6, y + h - 18), "10-4", font=font(F_B, 13), fill=(255, 210, 120))

# ---------------------------------------------------------------- content
LEADS = [
    # key, scene fn, accent, headline, detail, source
    ("C9", scene_sanctions, RED,
     "US SANCTIONS 4 IRAN 'OIL TRUSTEES'",
     "Treasury's Operation Economic Outcast targets Bavand, Taj, Servati, Arabnejad.",
     "SOURCE: TREASURY"),
    ("L3", scene_markets, RED,
     "MARKET ROUT: NASDAQ -5.3%, S&P -3.7%",
     "Nasdaq worst week since Mar 2020; S&P worst since Apr 2025; Nvidia -14%.",
     "SOURCE: INVESTOPEDIA · CNN"),
    ("L4", scene_cop31, GREEN,
     "COP31 IN OVERTIME ON FOSSIL FUELS",
     "Panama threatens block; 12 nations write; draft keeps 35% electricity by 2035.",
     "SOURCE: REUTERS"),
]

CARDS = [
    ("L2", scene_cyclone, "CYCLONE AKVAN SLAMS INDIA",
     "300,000+ evacuated; 1,300+ babies born.", "SOURCE: IMD"),
    ("C1", scene_bitcoin, "BITCOIN BELOW $60,000",
     "Low $57,778; close ~$58,317.", "SOURCE: REUTERS"),
    ("C2", scene_tanker, "TANKER HIT OFF KHASAB",
     "Unknown projectile; fire, no casualties.", "SOURCE: UKMTO"),
    ("C3", scene_houthi, "HOUTHIS THREATEN RED SEA PORTS",
     "Threat if coalition hits Hodeidah; strikes Yemen.", "SOURCE: REUTERS"),
    ("C4", scene_eu, "EU: €1BN NEW MILITARY AID",
     "Joint buys via EPF; part of €6.6bn deal.", "SOURCE: EU COUNCIL"),
    ("C5", scene_candle, "MLAMBO-NGCUKA DIES AT 71",
     "South Africa announces death on Friday.", "SOURCE: PRESIDENCY ZA"),
    ("C6", scene_court, "SYDNEY: ALLEGED ISIS PLOT CHARGE",
     "Amin, 35, charged; 3 held, 10 homes searched.", "SOURCE: AFP"),
    ("C7", scene_tesla, "ITALY: FIRST MAJOR EU TESLA APPROVAL",
     "Temporary approval for driving system.", "SOURCE: REUTERS"),
    ("C8", scene_ronaldo, "RONALDO'S 986TH GOAL",
     "Minute 14, Al-Ahli 3-1 Al-Nassr. (SPL tally.)", "SOURCE: ESPN"),
    ("C10", scene_quake, "PERU QUAKE M6.7, LIGHT DAMAGE",
     "34 km north of Junín, 108 km deep; light damage.", "SOURCE: AP"),
    ("C11", scene_eu_uk, "EU–UK DEAL CUTS TRADE BARRIERS",
     "Youth mobility 100,000 each side; ETS linked.", "SOURCE: AP"),
    ("C12", scene_un, "GRYNSPAN LEADS 10-4 IN 9TH POLL",
     "2 vetoes (states undisclosed); deadlock.", "SOURCE: REUTERS"),
]

ALSO_ON = [
    "Estonia to close Russia road crossings for 6+ months from Dec 1 (Reuters)",
    "Trump & Xi: humans must decide military AI use, Bessent says (Reuters)",
    "Japan poll: 93% say China ties bad, worst since 1986 (Kyodo)",
    "Modi opens SCO forum; first Pakistan minister visit in 3 years (PTI)",
    "Australia, Canada, NZ urge unconditional Russia ceasefire (Canada)",
    "Iraqi forces enter Kataeb Hezbollah stronghold, no resistance (AFP)",
    "Nvidia -14% as SEC probes its accounting, $491bn wiped out (Reuters)",
    "Xi meets Albanese in Shenzhen; hails 'full turnaround' (Xinhua)",
    "Eurogroup names Boone, Brunnermeier as ECB board picks (Eurogroup)",
    "Dutch court: BYD Ti7 infringes JLR Defender design; sales halted (Reuters)",
    "Tesla opens first Argentina store in Buenos Aires (Reuters)",
    "Las Vegas GP: Russell fastest in FP3, Mercedes 1–2 (Reuters)",
    "Gold -2.4% to $3,538, worst week since September (Reuters)",
    "Michigan sentiment 51.5; Bessent urges Fed not to hike 50bp (CNBC)",
    "Tesla plans $3.1bn polysilicon plant in Texas (Reuters)",
    "Russian missiles, drones enter Polish airspace in Kyiv barrage (Reuters)",
    "Kyiv hits 3 Russian ballistic launchers, Smolensk plant (ISW)",
    "South Africa crime stats: 581 women killed Jul–Sep (BBC)",
    "Venezuela's Rodríguez rejects ICJ jurisdiction over Esequibo (CANA)",
    "KOSPI -5.2% to 4,869, lowest since January (AJP)",
    "Brent +0.6% to $92.57; third weekly loss in a row (Morningstar)",
    "SpaceX launches secret USSF-317 mission from Vandenberg (USSF)",
    "OpenAI: model-access brokers now need approval first (OpenAI)",
    "Island nations: COP31 fails if it ignores warming (Guardian)",
    "Tech rout: Broadcom -12%, AMD -13%, Meta -6%, Amazon -4% (Motley Fool)",
    "Anthropic -8.5% to $88.91 a day after record IPO (Reuters)",
    "'Chapo Isidro' arrested in Guasave, Sinaloa; shootout (CNN)",
    "Iran claims 14 tankers at Kharg for blockade drill; trackers dispute (ISW)",
    "Bolsonaro, 71, taken to hospital with severe abdominal pain (Reuters)",
    "Storm kills 3, wrecks ~5,000 homes in southern Brazil (EIN)",
    "Samsung names Hwang Sang-joon to lead memory business (Reuters)",
    "Sensex +1.1% to 83,919, defying global sell-off (Moneycontrol)",
]

TIMELINE = ("02:00 AKVAN · 06:10 SYDNEY · 10:00 SENSEX +1.1% · "
            "14:50 EU €1BN · 15:00 KHASAB · 15:42 BTC <$60K · 16:35 ECB · "
            "19:09 PERU · 21:00 NASDAQ")

DATE_CHECK = ("DATE CHECK — Left out on purpose (wrong day): Shenzhen summit · ICJ Myanmar · "
              "US Senate 51–48 · PIF Tower · Egypt–IMF · Argentina disability law · Colombia strike.")

HERO_HEAD = "110+ MISSILES HIT KYIV IN BIGGEST RAID OF THE YEAR"
HERO_DETAIL = "9 killed · 3 Dnipro bridges hit · debris falls in Poland"
HERO_SOURCE = "SOURCE: CNN · REUTERS"


# ---------------------------------------------------------------- layout
def check_fit(img):
    """Measure every text element against its box. Returns list of problems."""
    d = ImageDraw.Draw(img)
    problems = []
    f_h1 = font(F_B, 30)
    f_date = font(F_B, 26)
    f_note = font(F_R, 11)
    # masthead
    if text_w(d, "THE FRIDAY PAPER", f_h1) > 700:
        problems.append("masthead title too wide")
    if text_w(d, "FRIDAY 20 NOVEMBER 2026", f_date) > 700:
        problems.append("masthead date too wide")
    if text_w(d, "Every story below happened or was first reported on Friday 20 November 2026.",
              f_note) > 1000:
        problems.append("editor note too wide")
    # hero headline/detail on 1024-wide strip
    if text_w(d, HERO_HEAD, font(F_B, 21)) > 1000:
        problems.append("hero headline too wide: %d" % text_w(d, HERO_HEAD, font(F_B, 21)))
    if text_w(d, HERO_DETAIL + "  " + HERO_SOURCE, font(F_R, 12)) > 1000:
        problems.append("hero detail too wide")
    # leads: headline 2 lines max, detail 2 lines max, source 1 line
    for key, _fn, _ac, head, det, src in LEADS:
        hl = wrap(d, head, font(F_B, 15), 308)
        if len(hl) > 2:
            problems.append("lead %s headline %d lines: %s" % (key, len(hl), head))
        dl = wrap(d, det, font(F_R, 10), 308)
        if len(dl) > 2:
            problems.append("lead %s detail %d lines" % (key, len(dl)))
        if text_w(d, src, font(F_B, 8)) > 308:
            problems.append("lead %s source too wide" % key)
    # cards: headline 2 lines, detail 2 lines, source 1 line (text width 143)
    for key, _fn, head, det, src in CARDS:
        hl = wrap(d, head, font(F_B, 12), 143)
        if len(hl) > 2:
            problems.append("card %s headline %d lines: %s" % (key, len(hl), head))
        dl = wrap(d, det, font(F_R, 10), 143)
        if len(dl) > 2:
            problems.append("card %s detail %d lines: %s" % (key, len(dl), det))
        if text_w(d, src, font(F_B, 8)) > 143:
            problems.append("card %s source too wide" % key)
    # timeline + date check single lines
    if text_w(d, TIMELINE, font(F_B, 10)) > 1008:
        problems.append("timeline too wide: %d" % text_w(d, TIMELINE, font(F_B, 10)))
    if text_w(d, DATE_CHECK, font(F_R, 9)) > 1008:
        problems.append("date check too wide: %d" % text_w(d, DATE_CHECK, font(F_R, 9)))
    # also-on: one line each, column width 486
    for i, item in enumerate(ALSO_ON):
        wpx = text_w(d, item, font(F_R, 10))
        if wpx > 486:
            problems.append("also-on A%d too wide: %d px" % (i + 1, wpx))
    return problems


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead (0-76) ----
    d.rectangle([0, 0, W, 76], fill=NAVY)
    d.rectangle([16, 74, W - 16, 76], fill=GOLD)
    d.text((16, 8), "THE FRIDAY PAPER", font=font(F_B, 30), fill=WHITE)
    d.text((16, 42), "FRIDAY 20 NOVEMBER 2026", font=font(F_B, 26), fill=GOLD)
    d.text((W - 16 - text_w(d, "48 STORIES · ONE DAY", font(F_B, 16)), 14),
           "48 STORIES · ONE DAY", font=font(F_B, 16), fill=WHITE)
    d.text((W - 16 - text_w(d, "WORLD BRIEFING", font(F_B, 13)), 40),
           "WORLD BRIEFING", font=font(F_B, 13), fill=(200, 210, 235))
    # ---- editor note (76-96) ----
    d.text((16, 80), "Every story below happened or was first reported on Friday 20 November 2026.",
           font=font(F_R, 11), fill=GRAY)

    # ---- HERO: L1 Kyiv (96-300) ----
    scene_kyiv(img, 0, 96, W, 156)
    # translucent dark strip for the hero text
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle([0, 252, W, 300], fill=(6, 10, 28, 215))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((16, 254), HERO_HEAD, font=font(F_B, 21), fill=WHITE)
    d.text((16, 280), HERO_DETAIL + "   —   " + HERO_SOURCE, font=font(F_R, 12), fill=(220, 225, 240))
    # gold chip 110+ inside the strip, right end
    d.rectangle([W - 96, 254, W - 16, 296], fill=GOLD)
    d.text((W - 88, 260), "110+", font=font(F_B, 22), fill=NAVY)

    # ---- THREE LEADS (308-496) ----
    lead_xs = [8, 340, 672]
    for (key, fn, accent, head, det, src), lx in zip(LEADS, lead_xs):
        d.rectangle([lx, 308, lx + 324, 498], fill=CARD, outline=LINE, width=1)
        d.rectangle([lx, 308, lx + 324, 312], fill=accent)
        fn(img, lx + 1, 313, 322, 112)
        d = ImageDraw.Draw(img)
        hy = 429
        for ln in wrap(d, head, font(F_B, 15), 308):
            d.text((lx + 8, hy), ln, font=font(F_B, 15), fill=INK)
            hy += 17
        dy = 462
        for ln in wrap(d, det, font(F_R, 10), 308):
            d.text((lx + 8, dy), ln, font=font(F_R, 10), fill=(60, 60, 60))
            dy += 12
        d.text((lx + 8, 488), src, font=font(F_B, 8), fill=GOLD_D)

    # ---- CARDS (504-776): 4 cols x 3 rows, scene 80x80 left ----
    card_xs = [8, 261, 514, 767]
    card_ys = [504, 596, 688]
    for i, (key, fn, head, det, src) in enumerate(CARDS):
        cx = card_xs[i % 4]
        cy = card_ys[i // 4]
        d.rectangle([cx, cy, cx + 247, cy + 88], fill=CARD, outline=LINE, width=1)
        fn(img, cx + 4, cy + 4, 80, 80)
        d = ImageDraw.Draw(img)
        tx = cx + 92
        hy = cy + 5
        for ln in wrap(d, head, font(F_B, 12), 143):
            d.text((tx, hy), ln, font=font(F_B, 12), fill=INK)
            hy += 14
        dy = cy + 36
        for ln in wrap(d, det, font(F_R, 10), 143):
            d.text((tx, dy), ln, font=font(F_R, 10), fill=(60, 60, 60))
            dy += 12
        d.text((tx, cy + 74), src, font=font(F_B, 8), fill=GOLD_D)

    # ---- timeline strip (784-804) ----
    d.rectangle([0, 784, W, 804], fill=(232, 226, 210))
    tw = text_w(d, TIMELINE, font(F_B, 10))
    d.text(((W - tw) / 2, 789), TIMELINE, font=font(F_B, 10), fill=NAVY)

    # ---- ALSO-ON world brief (808-1002) ----
    d.text((16, 808), "ALSO ON FRIDAY — 32 MORE VERIFIED STORIES",
           font=font(F_B, 12), fill=NAVY)
    d.line([(16, 828), (W - 16, 828)], fill=LINE, width=1)
    col_x = [16, 530]
    for i, item in enumerate(ALSO_ON):
        col = i // 16
        row = i % 16
        ax = col_x[col]
        ay = 834 + row * 11
        d.ellipse([ax, ay + 3, ax + 5, ay + 8], fill=GOLD_D)
        d.text((ax + 10, ay), item, font=font(F_R, 10), fill=INK)

    # ---- DATE CHECK footer (1004-1022) ----
    d.rectangle([0, 1004, W, 1024], fill=(250, 228, 228))
    d.text((16, 1008), DATE_CHECK, font=font(F_R, 9), fill=(120, 40, 30))
    return img


if __name__ == "__main__":
    import sys
    im = Image.new("RGB", (W, H), PAPER)
    problems = check_fit(im)
    if problems:
        print("CHECK_FIT PROBLEMS (%d):" % len(problems))
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print("CHECK_FIT OK")
    out = render()
    pal = out.convert("P", palette=Image.ADAPTIVE, colors=256)
    pal.save("entry.png", optimize=True)
    print("saved entry.png")
