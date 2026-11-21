#!/usr/bin/env python3
"""news-image-20261120 v13 — render.py (written from scratch, PIL stdlib only).

Design kept from v12 ("HERO + THREE LEADS + SCENE GRID + WORLD BRIEF"):
masthead + editor note + full-width hero + 3 leads in a row + 12 cards (4x3)
+ UTC timeline + 32 also-on "world brief" (2 cols) + DATE CHECK.
48 stories, all Friday 20 November 2026 (verified from primary sources).

Warden v12 fixes applied (verified by Warden Phase 1, 21 Nov 23:56 WIB):
 1. HERO: NO broken Dnipro bridge. None of the 3 Dnipro bridges collapsed
    (Podilsko, Darnytskyi, Southern — all only "damaged"; Podilsko reopened
    ~15:00 Kyiv time 20 Nov). Kerch (collapsed night 16-17 Nov) is blocklisted
    and never drawn. Hero = night sky + missile trails + explosions over
    Kyiv rooftops + golden domes + river. No bridge at all.
 2. L1 headline: "110+ MISSILES HIT UKRAINE" (27 ballistic + 84 cruise =
    111 missiles + 404 drones, 19-20 Nov; no official figure for Kyiv hits).
 3. C1 close: "Low $57,778; close $58,951" with SOURCE: BINANCE
    (Finnhub/Binance UTC daily candle O 61986.73 / H 62639.52 /
    L 57778.35 / C 58951.51). $55,830 NEVER used (Saturday 04:13 GMT).
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 227)
PAPER2 = (240, 234, 216)
INK = (26, 26, 26)
MUTE = (90, 86, 74)
NAVY = (15, 28, 56)
NAVY2 = (27, 42, 82)
SLATE = (35, 42, 58)
GOLD = (217, 164, 65)
GOLD_D = (176, 124, 32)
RED = (196, 57, 43)
RED_B = (224, 62, 45)
GREEN = (46, 125, 70)
BLUE = (30, 80, 160)
TEAL = (28, 90, 90)
WHITE = (255, 255, 255)
CREAM = (248, 244, 232)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def text_w(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, text, f, maxw, max_lines):
    """Greedy wrap; returns list of lines or None if it does not fit."""
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if text_w(d, t, f) <= maxw:
            cur = t
        else:
            if not cur:
                return None
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        return None
    return lines


def draw_lines(d, lines, f, x, y, leading, fill):
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=f, fill=fill)


def fit_check(d, items):
    """items: (text, font, maxw, max_lines, label). Raises on overflow."""
    bad = []
    for text, f, maxw, max_lines, label in items:
        if text_w(d, text, f) > maxw and wrap(d, text, f, maxw, max_lines) is None:
            bad.append(label)
    if bad:
        raise SystemExit("check_fit FAILED: " + ", ".join(bad))


# ---------------------------------------------------------------- masthead
def draw_masthead(d):
    d.rectangle([0, 0, W, 76], fill=NAVY)
    d.text((16, 8), "THE FRIDAY PAPER", font=F(FB, 30), fill=WHITE)
    d.text((16, 42), "FRIDAY 20 NOVEMBER 2026", font=F(FB, 28), fill=GOLD)
    f1, f2 = F(FB, 15), F(FB, 13)
    s1 = "48 STORIES \u00b7 ONE DAY"
    s2 = "WORLD BRIEFING"
    d.text((1008 - text_w(d, s1, f1), 12), s1, font=f1, fill=WHITE)
    d.text((1008 - text_w(d, s2, f2), 34), s2, font=f2, fill=GOLD)
    d.rectangle([16, 72, 1008, 74], fill=GOLD)


def draw_editor(d):
    d.text((16, 79), "Every story below happened or was first reported on Friday 20 November 2026.",
           font=F(FR, 13), fill=MUTE)


# ---------------------------------------------------------------- hero scene
def draw_hero(d):
    y0, y1 = 96, 272
    # night sky gradient
    top, bot = (8, 14, 42), (30, 46, 92)
    for y in range(y0, y1):
        t = (y - y0) / (y1 - y0)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    # stars (seeded, deterministic)
    rnd = random.Random(42)
    for _ in range(60):
        x = rnd.randint(8, 1016)
        y = rnd.randint(y0 + 4, 190)
        r = rnd.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 224, 240))
    # crescent moon, top right
    d.ellipse([946, 104, 986, 144], fill=(235, 232, 210))
    d.ellipse([958, 100, 992, 140], fill=(16, 26, 60))
    # missile trails: nearly straight, pale, slight bend
    trails = [((120, 112), (330, 206)), ((470, 106), (625, 202)),
              ((745, 116), (878, 196))]
    for (x1, y1a), (x2, y2a) in trails:
        mx, my = (x1 + x2) // 2, (y1a + y2a) // 2 - 6
        d.line([(x1, y1a), (mx, my), (x2, y2a)], fill=(214, 220, 235), width=3)
        d.ellipse([x2 - 4, y2a - 4, x2 + 4, y2a + 4], fill=(255, 240, 200))
    # explosions over rooftops: irregular bursts (not suns) + smoke
    rnd3 = random.Random(11)
    for (cx, cy, r) in [(330, 206, 22), (625, 202, 24), (878, 196, 17)]:
        for k in range(14):
            a = k * math.pi / 7 + rnd3.uniform(-0.12, 0.12)
            ln = r * (1.55 if k % 2 == 0 else 1.0) * rnd3.uniform(0.9, 1.1)
            x2 = cx + int(ln * math.cos(a))
            y2 = cy + int(ln * math.sin(a))
            d.line([(cx, cy), (x2, y2)], fill=(255, 170, 60), width=3)
        d.ellipse([cx - int(r * 0.8), cy - int(r * 0.55),
                   cx + int(r * 0.8), cy + int(r * 0.55)], fill=(255, 150, 40))
        d.ellipse([cx - int(r * 0.45), cy - int(r * 0.32),
                   cx + int(r * 0.45), cy + int(r * 0.32)], fill=(255, 220, 120))
        d.ellipse([cx - 4, cy - 3, cx + 4, cy + 3], fill=(255, 255, 230))
        # smoke above each burst
        for sx, sy, sr in ((cx - 12, cy - r - 8, 7), (cx + 4, cy - r - 14, 9),
                           (cx + 15, cy - r - 6, 6)):
            d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(96, 100, 118))
    # skyline silhouettes (base y=256), golden domes = Kyiv
    base = 256
    rnd2 = random.Random(7)
    x = 0
    while x < W:
        bw = rnd2.randint(34, 64)
        bh = rnd2.randint(28, 62)
        d.rectangle([x, base - bh, x + bw, base], fill=(10, 15, 34))
        for wy in range(base - bh + 6, base - 4, 10):
            for wx in range(x + 5, x + bw - 4, 12):
                if rnd2.random() < 0.45:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(232, 190, 90))
        x += bw + rnd2.randint(2, 10)
    # golden onion domes on church towers = Kyiv (no bridge anywhere)
    for cx in (430, 700):
        d.rectangle([cx - 13, base - 48, cx + 13, base], fill=(10, 15, 34))
        d.rectangle([cx - 8, base - 38, cx - 4, base - 30], fill=(232, 190, 90))
        d.rectangle([cx + 4, base - 38, cx + 8, base - 30], fill=(232, 190, 90))
        d.ellipse([cx - 15, base - 74, cx + 15, base - 44], fill=(222, 172, 60))
        d.polygon([(cx - 6, base - 70), (cx + 6, base - 70), (cx, base - 82)],
                  fill=(222, 172, 60))
        d.line([(cx, base - 94), (cx, base - 80)], fill=(222, 172, 60), width=2)
        d.line([(cx - 5, base - 89), (cx + 5, base - 89)], fill=(222, 172, 60), width=2)
    # river band at the bottom
    d.rectangle([0, base, W, y1], fill=(13, 27, 61))
    for rx in (90, 260, 480, 660, 840):
        d.rectangle([rx, base + 6, rx + 46, base + 8], fill=(90, 120, 180))
        d.rectangle([rx + 12, base + 11, rx + 40, base + 13], fill=(60, 90, 150))


def draw_hero_strip(d):
    d.rectangle([0, 272, W, 316], fill=SLATE)
    d.text((16, 278), "110+ MISSILES HIT UKRAINE", font=F(FB, 26), fill=WHITE)
    det = ("111 missiles, 404 drones overnight \u00b7 9 killed \u00b7 3 Dnipro bridges "
           "damaged \u00b7 debris in Poland \u2014 SOURCE: CNN \u00b7 REUTERS")
    d.text((16, 304), det, font=F(FR, 12), fill=(200, 205, 215))
    d.rectangle([912, 276, 1008, 312], fill=GOLD)
    s = "110+"
    f = F(FB, 24)
    d.text((960 - text_w(d, s, f) / 2, 281), s, font=f, fill=NAVY)


# ---------------------------------------------------------------- lead scenes
def scene_c9(d, x, y, w, h):
    """US sanctions Iran: oil barrels + sealed document + ban ring (inside)."""
    d.rectangle([x, y, x + w, y + h], fill=(31, 42, 68))
    # oil barrels, left
    for bx in (x + 22, x + 76):
        d.rectangle([bx, y + 30, bx + 44, y + 96], fill=(18, 22, 34))
        d.ellipse([bx, y + 24, bx + 44, y + 38], fill=(40, 46, 62))
        d.rectangle([bx, y + 48, bx + 44, y + 54], fill=GOLD)
        d.rectangle([bx, y + 74, bx + 44, y + 80], fill=GOLD)
    # sealed document, right
    d.rectangle([x + 150, y + 16, x + 282, y + 96], fill=(244, 240, 228))
    d.rectangle([x + 150, y + 16, x + 282, y + 96], outline=(120, 110, 90), width=2)
    for i, ly in enumerate((y + 30, y + 44, y + 58)):
        d.rectangle([x + 162, ly, x + 270, ly + 4], fill=(150, 145, 130))
    d.ellipse([x + 238, y + 66, x + 272, y + 94], fill=RED)
    d.text((x + 248, y + 74), "S", font=F(FB, 14), fill=WHITE)
    # ban ring over document, kept inside the scene
    cx, cy, r = x + 216, y + 56, 46
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED_B, width=9)
    d.line([(cx - 33, cy + 33), (cx + 33, cy - 33)], fill=RED_B, width=9)


def scene_l3(d, x, y, w, h):
    """Market rout: red candles falling + big down arrow."""
    d.rectangle([x, y, x + w, y + h], fill=(13, 13, 13))
    # candles descending left -> right
    tops = [18, 30, 44, 58]
    for i, t in enumerate(tops):
        cx = x + 40 + i * 62
        d.line([(cx + 11, y + t - 8), (cx + 11, y + t + 52)], fill=RED_B, width=2)
        d.rectangle([cx, y + t, cx + 22, y + t + 36], fill=RED_B)
    # big down arrow
    d.line([(x + 30, y + 16), (x + 290, y + 92)], fill=RED_B, width=10)
    d.polygon([(x + 292, y + 96), (x + 262, y + 74), (x + 300, y + 70)],
              fill=RED_B)
    d.text((x + w - 108, y + 8), "S&P -3.7%", font=F(FB, 15), fill=GOLD)


def scene_l4(d, x, y, w, h):
    """COP31: flags over a hall + globe."""
    d.rectangle([x, y, x + w, y + h], fill=(216, 200, 160))
    # small flags across the top
    cols = [(196, 57, 43), (30, 80, 160), (46, 125, 70), (217, 164, 65),
            (120, 120, 120), (224, 120, 40), (30, 80, 160), (196, 57, 43)]
    for i, c in enumerate(cols):
        fx = x + 18 + i * 38
        d.line([(fx + 6, y + 10), (fx + 6, y + 38)], fill=(80, 70, 55), width=2)
        d.rectangle([fx + 6, y + 10, fx + 26, y + 24], fill=c)
    # globe, centre right
    cx, cy, r = x + 215, y + 68, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 110, 180))
    d.ellipse([cx - 14, cy - 18, cx + 4, cy + 2], fill=(80, 170, 90))
    d.ellipse([cx - 2, cy + 8, cx + 18, cy + 24], fill=(80, 170, 90))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(20, 60, 110), width=2)
    # hall rows, bottom
    d.rectangle([x, y + 92, x + w, y + h], fill=(70, 58, 44))
    for i in range(9):
        sx = x + 22 + i * 34
        d.ellipse([sx, y + 96, sx + 12, y + 106], fill=(40, 32, 24))


LEADS = [
    # (headline, detail, source, scene_fn)
    ("US SANCTIONS 4 IRAN 'OIL TRUSTEES'",
     "Treasury's Operation Economic Outcast targets Bavand, Taj, Servati, Arabnejad.",
     "SOURCE: TREASURY", scene_c9),
    ("MARKET ROUT: NASDAQ -5.3%, S&P -3.7%",
     "Nasdaq worst week since Mar 2020; S&P worst since Apr 2025; Nvidia -14%.",
     "SOURCE: INVESTOPEDIA \u00b7 CNN", scene_l3),
    ("COP31 IN OVERTIME ON FOSSIL FUELS",
     "Panama threatens block; 12 nations write; draft keeps 35% electricity by 2035.",
     "SOURCE: REUTERS", scene_l4),
]


def draw_leads(d):
    y0 = 316
    for i, (head, det, src, fn) in enumerate(LEADS):
        x = 16 + i * 335
        w = 322
        fn(d, x, y0, w, 110)
        d.rectangle([x, y0 + 110, x + w, y0 + 196], fill=CREAM)
        d.rectangle([x, y0 + 110, x + w, y0 + 196], outline=(200, 192, 172), width=1)
        hl = wrap(d, head, F(FB, 17), w - 16, 2)
        draw_lines(d, hl, F(FB, 17), x + 8, y0 + 114, 19, INK)
        dl = wrap(d, det, F(FR, 12), w - 16, 2)
        draw_lines(d, dl, F(FR, 12), x + 8, y0 + 152, 14, (60, 58, 50))
        d.text((x + 8, y0 + 180), src, font=F(FB, 10), fill=GOLD_D)


# ---------------------------------------------------------------- card scenes
def s_l2(d, x, y):
    d.rectangle([x, y, x + 80, y + 80], fill=(16, 70, 80))
    cx, cy = x + 40, y + 40
    for r in (30, 22, 14):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=(220, 235, 245), width=4)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255))
    for rx, ry in ((12, 62), (24, 70), (58, 66), (68, 58)):
        d.ellipse([x + rx, y + ry, x + rx + 2, y + ry + 5], fill=(170, 210, 225))


def s_c1(d, x, y):
    d.rectangle([x, y, x + 80, y + 80], fill=(15, 28, 56))
    d.ellipse([x + 14, y + 14, x + 66, y + 66], fill=GOLD)
    d.ellipse([x + 14, y + 14, x + 66, y + 66], outline=(150, 105, 25), width=2)
    d.text((x + 31, y + 22), "B", font=F(FB, 34), fill=(120, 80, 10))
    d.line([(x + 8, y + 12), (x + 68, y + 66)], fill=RED_B, width=7)
    d.polygon([(x + 70, y + 70), (x + 52, y + 58), (x + 72, y + 50)], fill=RED_B)


def s_c2(d, x, y):
    """Oil tanker: long flat-deck hull, stern superstructure, derrick, smoke."""
    d.rectangle([x, y, x + 80, y + 80], fill=(30, 90, 140))
    d.rectangle([x, y + 58, x + 80, y + 80], fill=(18, 60, 100))
    d.rectangle([x + 6, y + 46, x + 74, y + 60], fill=(28, 32, 40))
    d.rectangle([x + 6, y + 46, x + 74, y + 49], fill=(60, 66, 78))
    d.rectangle([x + 58, y + 28, x + 72, y + 46], fill=(240, 240, 235))
    d.line([(x + 20, y + 46), (x + 30, y + 26), (x + 40, y + 46)], fill=(200, 200, 190), width=2)
    d.line([(x + 30, y + 26), (x + 44, y + 34)], fill=(200, 200, 190), width=2)
    for sx, sy, r in ((64, 20, 5), (60, 12, 4), (56, 6, 3)):
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(120, 125, 130))
    d.ellipse([x + 34, y + 36, x + 46, y + 48], fill=(255, 150, 40))
    d.ellipse([x + 38, y + 40, x + 44, y + 46], fill=(255, 220, 120))


def s_c3(d, x, y):
    d.rectangle([x, y, x + 80, y + 80], fill=(35, 42, 58))
    d.polygon([(x + 52, y + 16), (x + 60, y + 22), (x + 30, y + 56), (x + 24, y + 50)],
              fill=(230, 230, 225))
    d.polygon([(x + 52, y + 16), (x + 60, y + 22), (x + 56, y + 28)], fill=RED_B)
    d.polygon([(x + 30, y + 56), (x + 24, y + 50), (x + 16, y + 58)], fill=(180, 180, 175))
    d.line([(x + 64, y + 10), (x + 64, y + 72)], fill=(150, 155, 160), width=3)
    d.line([(x + 44, y + 14), (x + 76, y + 14)], fill=(150, 155, 160), width=3)
    d.line([(x + 70, y + 14), (x + 70, y + 38)], fill=(150, 155, 160), width=2)
    d.rectangle([x + 66, y + 38, x + 74, y + 46], fill=(217, 164, 65))


def s_c4(d, x, y):
    d.rectangle([x, y, x + 80, y + 80], fill=(0, 51, 153))
    cx, cy = x + 40, y + 40
    for k in range(12):
        a = k * math.pi / 6 - math.pi / 2
        d.ellipse([cx + int(26 * math.cos(a)) - 2, cy + int(26 * math.sin(a)) - 2,
                   cx + int(26 * math.cos(a)) + 2, cy + int(26 * math.sin(a)) + 2],
                  fill=GOLD)
    d.text((x + 29, y + 26), "\u20ac", font=F(FB, 30), fill=GOLD)


def s_c5(d, x, y):
    d.rectangle([x, y, x + 80, y + 80], fill=(30, 30, 40))
    for i, cx in enumerate((24, 40, 56)):
        h = 34 - i * 4
        d.rectangle([x + cx - 4, y + 66 - h, x + cx + 4, y + 66], fill=(240, 238, 230))
        d.ellipse([x + cx - 4, y + 54 - h, x + cx + 4, y + 64 - h], fill=(255, 170, 60))
        d.polygon([(x + cx, y + 48 - h), (x + cx - 3, y + 56 - h),
                   (x + cx + 3, y + 56 - h)], fill=(255, 220, 120))
    d.rectangle([x + 12, y + 66, x + 68, y + 70], fill=(90, 80, 65))


def s_c6(d, x, y):
    d.rectangle([x, y, x + 80, y + 80], fill=(24, 44, 80))
    cx = x + 40
    d.line([(cx, y + 12), (cx, y + 62)], fill=GOLD, width=3)
    d.line([(cx - 24, y + 20), (cx + 24, y + 20)], fill=GOLD, width=3)
    d.ellipse([cx - 3, y + 8, cx + 3, y + 14], fill=GOLD)
    for sx in (cx - 24, cx + 24):
        d.line([(sx, y + 20), (sx, y + 40)], fill=GOLD, width=2)
        d.pieslice([sx - 12, y + 40, sx + 12, y + 56], 0, 180, fill=GOLD)
    d.rectangle([cx - 14, y + 62, cx + 14, y + 68], fill=GOLD)


def s_c7(d, x, y):
    d.rectangle([x, y, x + 80, y + 80], fill=(20, 24, 34))
    d.rounded_rectangle([x + 10, y + 42, x + 70, y + 58], radius=6, fill=RED_B)
    d.polygon([(x + 24, y + 42), (x + 30, y + 30), (x + 50, y + 30), (x + 56, y + 42)],
              fill=RED_B)
    d.rectangle([x + 32, y + 33, x + 48, y + 42], fill=(180, 220, 240))
    for wx in (22, 58):
        d.ellipse([x + wx - 7, y + 56, x + wx + 7, y + 70], fill=(10, 10, 10))
        d.ellipse([x + wx - 3, y + 60, x + wx + 3, y + 66], fill=(160, 165, 170))


def s_c8(d, x, y):
    d.rectangle([x, y, x + 80, y + 80], fill=(30, 110, 60))
    d.ellipse([x + 12, y + 22, x + 58, y + 68], fill=WHITE)
    d.ellipse([x + 12, y + 22, x + 58, y + 68], outline=(30, 30, 30), width=2)
    for px, py in ((35, 38), (24, 50), (46, 50), (35, 58)):
        d.polygon([(x + px, y + py - 5), (x + px + 5, y + py - 1),
                   (x + px + 3, y + py + 5), (x + px - 3, y + py + 5),
                   (x + px - 5, y + py - 1)], fill=(30, 30, 30))
    for gx in range(58, 80, 8):
        d.line([(x + gx, y + 6), (x + gx, y + 30)], fill=(255, 255, 255), width=1)
    for gy in range(6, 32, 8):
        d.line([(x + 58, y + gy), (x + 80, y + gy)], fill=(255, 255, 255), width=1)


def s_c10(d, x, y):
    """Peru quake: building UPRIGHT, one small wall crack, FLAT ground."""
    d.rectangle([x, y, x + 80, y + 80], fill=(230, 225, 205))
    d.rectangle([x + 22, y + 12, x + 58, y + 68], fill=(120, 118, 110))
    for wy in range(y + 18, y + 62, 12):
        for wx in (x + 27, x + 41):
            d.rectangle([wx, wy, wx + 8, wy + 7], fill=(70, 90, 120))
    # one small crack in the wall only (no leaning, no ground cracks)
    d.line([(x + 48, y + 30), (x + 45, y + 38), (x + 49, y + 44)], fill=(60, 55, 45), width=2)
    # ground: perfectly horizontal
    d.line([(x + 6, y + 68), (x + 74, y + 68)], fill=(60, 55, 45), width=3)
    d.rectangle([x + 6, y + 68, x + 74, y + 72], fill=(90, 130, 70))


def s_c11(d, x, y):
    d.rectangle([x, y, x + 80, y + 80], fill=(245, 242, 232))
    # EU flag
    d.rectangle([x + 6, y + 10, x + 34, y + 36], fill=(0, 51, 153))
    for k in range(12):
        a = k * math.pi / 6 - math.pi / 2
        px = x + 20 + int(9 * math.cos(a))
        py = y + 23 + int(9 * math.sin(a))
        d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=GOLD)
    # Union Jack (simplified: blue, white saltire + cross, red cross)
    d.rectangle([x + 44, y + 10, x + 74, y + 36], fill=(1, 33, 105))
    d.line([(x + 44, y + 10), (x + 74, y + 36)], fill=WHITE, width=3)
    d.line([(x + 74, y + 10), (x + 44, y + 36)], fill=WHITE, width=3)
    d.line([(x + 59, y + 10), (x + 59, y + 36)], fill=WHITE, width=5)
    d.line([(x + 44, y + 23), (x + 74, y + 23)], fill=WHITE, width=5)
    d.line([(x + 59, y + 10), (x + 59, y + 36)], fill=(200, 16, 46), width=3)
    d.line([(x + 44, y + 23), (x + 74, y + 23)], fill=(200, 16, 46), width=3)
    # double arrow + DEAL
    d.line([(x + 14, y + 52), (x + 66, y + 52)], fill=GOLD_D, width=3)
    d.polygon([(x + 70, y + 52), (x + 62, y + 47), (x + 62, y + 57)], fill=GOLD_D)
    d.polygon([(x + 10, y + 52), (x + 18, y + 47), (x + 18, y + 57)], fill=GOLD_D)
    d.text((x + 26, y + 60), "DEAL", font=F(FB, 13), fill=GREEN)


def s_c12(d, x, y):
    d.rectangle([x, y, x + 80, y + 80], fill=(180, 205, 230))
    cx, cy = x + 30, y + 28
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(90, 150, 200))
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=WHITE, width=2)
    d.ellipse([cx - 8, cy - 22, cx + 8, cy + 22], outline=WHITE, width=1)
    d.line([(cx - 22, cy), (cx + 22, cy)], fill=WHITE, width=1)
    d.rectangle([x + 48, y + 46, x + 72, y + 70], fill=(40, 50, 70))
    d.rectangle([x + 54, y + 46, x + 66, y + 50], fill=(180, 205, 230))
    d.rectangle([x + 8, y + 58, x + 34, y + 74], fill=GOLD)
    d.text((x + 11, y + 61), "10-4", font=F(FB, 11), fill=NAVY)


CARDS = [
    ("CYCLONE AKVAN SLAMS INDIA", "300,000+ evacuated; 1,300+ babies born.",
     "SOURCE: IMD", s_l2),
    ("BITCOIN BELOW $60,000", "Low $57,778; close $58,951.",
     "SOURCE: BINANCE", s_c1),
    ("TANKER HIT OFF KHASAB", "Unknown projectile; fire, no casualties.",
     "SOURCE: UKMTO", s_c2),
    ("HOUTHIS THREATEN RED SEA PORTS", "Threat if coalition hits Hodeidah; strikes Yemen.",
     "SOURCE: REUTERS", s_c3),
    ("EU: \u20ac1BN NEW MILITARY AID", "Joint buys via EPF; part of \u20ac6.6bn deal.",
     "SOURCE: EU COUNCIL", s_c4),
    ("MLAMBO-NGCUKA DIES AT 71", "South Africa announces death on Friday.",
     "SOURCE: PRESIDENCY ZA", s_c5),
    ("SYDNEY: ALLEGED ISIS PLOT CHARGE", "Amin, 35, charged; 3 held, 10 raided.",
     "SOURCE: AFP", s_c6),
    ("ITALY: FIRST MAJOR EU TESLA APPROVAL", "Temporary approval for driving system.",
     "SOURCE: REUTERS", s_c7),
    ("RONALDO'S 986TH GOAL", "Minute 14, Al-Ahli 3-1 Al-Nassr. (SPL tally.)",
     "SOURCE: ESPN", s_c8),
    ("PERU QUAKE M6.7, LIGHT DAMAGE", "34 km north of Jun\u00edn, 108 km deep; no casualties.",
     "SOURCE: AP", s_c10),
    ("EU\u2013UK DEAL CUTS TRADE BARRIERS", "Youth mobility 100,000 each side; ETS linked.",
     "SOURCE: AP", s_c11),
    ("GRYNSPAN LEADS 10-4 IN 9TH POLL", "2 vetoes (states undisclosed); deadlock.",
     "SOURCE: REUTERS", s_c12),
]


def draw_cards(d):
    y0 = 512
    for i, (head, det, src, fn) in enumerate(CARDS):
        col, row = i % 4, i // 4
        x = 16 + col * 250
        y = y0 + row * 88
        d.rectangle([x, y, x + 242, y + 88], fill=CREAM)
        d.rectangle([x, y, x + 242, y + 88], outline=(200, 192, 172), width=1)
        fn(d, x + 4, y + 4)
        tx, tw = x + 92, 142
        hl = wrap(d, head, F(FB, 12), tw, 3)
        draw_lines(d, hl, F(FB, 12), tx, y + 5, 14, INK)
        dl = wrap(d, det, F(FR, 11), tw, 2)
        draw_lines(d, dl, F(FR, 11), tx, y + 48, 13, (60, 58, 50))
        d.text((tx, y + 75), src, font=F(FB, 9), fill=GOLD_D)


# ---------------------------------------------------------------- timeline / also-on / date check
TIMELINE = ("02:00 AKVAN \u00b7 06:10 SYDNEY \u00b7 10:00 SENSEX +1.1% \u00b7 "
            "14:50 EU \u20ac1BN \u00b7 15:00 KHASAB \u00b7 15:42 BTC <$60K \u00b7 "
            "16:35 ECB \u00b7 19:09 PERU \u00b7 21:00 NASDAQ")

ALSO_ON = [
    "Estonia to close Russia road crossings for 6+ months (Reuters)",
    "Trump & Xi: humans must decide military AI use (Reuters)",
    "Japan poll: 93% say China ties bad, worst since 1986 (Kyodo)",
    "Modi opens SCO forum; first Pakistan minister visit in 3 yrs (PTI)",
    "Australia, Canada, NZ urge unconditional ceasefire (Canada)",
    "Iraqi forces enter Kataeb Hezbollah base, no resistance (AFP)",
    "Nvidia -14% as SEC probes accounting; $491bn wiped (Reuters)",
    "Xi meets Albanese in Shenzhen; hails 'full turnaround' (Xinhua)",
    "Eurogroup names Boone, Brunnermeier as ECB board picks (Eurogroup)",
    "The Hague: BYD Ti7 infringes JLR Defender design (Reuters)",
    "Tesla opens first Argentina store in Buenos Aires (Reuters)",
    "Las Vegas GP: Russell fastest in FP3, Mercedes 1-2 (Reuters)",
    "Gold -2.4% to $3,538, worst week since September (Reuters)",
    "Michigan sentiment 51.5; Bessent: Fed must not hike 50bp (CNBC)",
    "Tesla plans $3.1bn polysilicon plant in Texas (Reuters)",
    "Russian missiles enter Polish airspace (Reuters)",
    "Kyiv hits 3 ballistic launchers, Smolensk plant (ISW)",
    "South Africa crime stats: 581 women killed Jul-Sep (BBC)",
    "Venezuela rejects ICJ jurisdiction over Esequibo (CANA)",
    "KOSPI -5.2% to 4,869, lowest since January (AJP)",
    "Brent +0.6% to $92.57; third weekly loss (Morningstar)",
    "SpaceX launches secret USSF-317 from Vandenberg (USSF)",
    "OpenAI: model-access brokers need approval first (OpenAI)",
    "Island nations: COP31 fails if it ignores warming (Guardian)",
    "Tech rout: Broadcom -12%, AMD -13%, Meta -6%, Amazon -4%",
    "Anthropic -8.5% to $88.91 after record IPO (Reuters)",
    "'Chapo Isidro' arrested in Guasave; shootout (CNN)",
    "Iran claims 14 tankers at Kharg; trackers dispute it (ISW)",
    "Bolsonaro, 71, taken to hospital with abdominal pain (Reuters)",
    "Storm kills 3, wrecks ~5,000 homes in southern Brazil (EIN)",
    "Samsung names Hwang Sang-joon to lead memory (Reuters)",
    "Sensex +1.1%, Nifty +1.1% defy global rout (Reuters)",
]

DATE_CHECK = ("DATE CHECK \u2014 Left out (wrong day): Shenzhen summit \u00b7 "
              "ICJ Myanmar \u00b7 Senate 51\u201348 \u00b7 PIF Tower \u00b7 Egypt\u2013IMF \u00b7 "
              "Argentina law \u00b7 Colombia strike.")


def draw_bottom(d):
    # timeline strip
    d.rectangle([0, 776, W, 796], fill=PAPER2)
    d.text((16, 781), TIMELINE, font=F(FR, 11), fill=(70, 66, 55))
    # also-on header
    d.text((16, 799), "ALSO ON FRIDAY \u2014 32 MORE VERIFIED STORIES",
           font=F(FB, 13), fill=INK)
    d.rectangle([330, 808, 1008, 810], fill=GOLD)
    # also-on rows, 2 columns x 16
    f = F(FR, 10)
    for i, item in enumerate(ALSO_ON):
        col, row = i // 16, i % 16
        x = 16 if col == 0 else 520
        y = 816 + row * 11
        d.text((x, y), "\u25c6", font=f, fill=GOLD_D)
        d.text((x + 12, y), item, font=f, fill=(50, 48, 42))
    # date check
    d.text((16, 992), DATE_CHECK, font=F(FB, 11), fill=(120, 40, 30))


# ---------------------------------------------------------------- fit check
def run_fit_check(d):
    items = [
        ("THE FRIDAY PAPER", F(FB, 30), 700, 1, "masthead title"),
        ("FRIDAY 20 NOVEMBER 2026", F(FB, 28), 700, 1, "masthead date"),
        ("48 STORIES \u00b7 ONE DAY", F(FB, 15), 300, 1, "masthead right"),
        ("Every story below happened or was first reported on Friday 20 November 2026.",
         F(FR, 13), 992, 1, "editor note"),
        ("110+ MISSILES HIT UKRAINE", F(FB, 26), 880, 1, "hero headline"),
        ("111 missiles, 404 drones overnight \u00b7 9 killed \u00b7 3 Dnipro bridges "
         "damaged \u00b7 debris in Poland \u2014 SOURCE: CNN \u00b7 REUTERS",
         F(FR, 12), 884, 1, "hero detail"),
        (TIMELINE, F(FR, 11), 992, 1, "timeline"),
        (DATE_CHECK, F(FB, 11), 992, 1, "date check"),
    ]
    for head, det, src, _ in LEADS:
        items.append((head, F(FB, 17), 306, 2, "lead headline: " + head[:20]))
        items.append((det, F(FR, 12), 306, 2, "lead detail: " + det[:20]))
    for head, det, src, _ in CARDS:
        items.append((head, F(FB, 12), 142, 2, "card headline: " + head[:20]))
        items.append((det, F(FR, 11), 142, 2, "card detail: " + det[:20]))
    for it in ALSO_ON:
        items.append((it, F(FR, 10), 470, 1, "also-on: " + it[:25]))
    fit_check(d, items)


# ---------------------------------------------------------------- render
def render(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    run_fit_check(d)
    draw_masthead(d)
    draw_editor(d)
    draw_hero(d)
    draw_hero_strip(d)
    draw_leads(d)
    draw_cards(d)
    draw_bottom(d)
    pal = img.convert("P", palette=Image.ADAPTIVE, colors=256)
    pal.save(out_path, optimize=True)
    return out_path


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    render(out)
    print("wrote", out)
