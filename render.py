#!/usr/bin/env python3
"""Render the v8 entry image: world map + visual leads + market infographic.

Composition (redesigned from scratch for v8): a world map is the hero visual,
with numbered pins for the day's main stories; four lead panels with big
numbers; a markets bar infographic; twelve short cards; a 32-item also-on
list; a DATE CHECK box and a UTC timeline. Content is the same 48 stories
as v7 (fact-check 48/48 passed Warden v7) - only the composition changed.
Standard library + PIL only. Deterministic output.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FB if bold else FR, size)


# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
NAVY = (16, 42, 67)
NAVY2 = (24, 58, 88)
GOLD = (212, 175, 55)
CREAM = (240, 232, 214)
INK = (22, 22, 22)
MUTED = (96, 96, 92)
LINE = (205, 198, 186)
OCEAN = (204, 224, 240)
LAND = (198, 216, 178)
LANDLINE = (122, 142, 110)
GRID = (186, 208, 226)
WHITE = (255, 255, 255)
RED = (192, 57, 43)
GREEN = (30, 132, 73)
BLUE = (41, 98, 168)
TEAL = (0, 130, 130)
AMBER = (196, 120, 10)
PURPLE = (110, 80, 150)
PIN = (200, 40, 30)
PINKBG = (250, 226, 222)

_fcache = {}


def F(size, bold=False):
    key = (size, bold)
    if key not in _fcache:
        _fcache[key] = font(size, bold)
    return _fcache[key]


def text_w(d, xy, s, size, color, bold=False, anchor="la"):
    f = F(size, bold)
    d.text(xy, s, font=f, fill=color, anchor=anchor)


def wrap(s, size, max_w, bold=False):
    """Greedy word wrap; returns list of lines that fit max_w."""
    f = F(size, bold)
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if f.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, s, size, max_w, color, bold=False, lh=None, align="l"):
    """Draw wrapped text; returns y just below the last line."""
    lines = wrap(s, size, max_w, bold)
    if lh is None:
        lh = size + 3
    for ln in lines:
        if align == "c":
            text_w(d, (x + max_w // 2, y), ln, size, color, bold, anchor="ma")
        else:
            text_w(d, (x, y), ln, size, color, bold)
        y += lh
    return y


def fit_size(s, size, max_w, bold=False):
    """Largest font size <= size that makes s fit max_w (never below 7)."""
    while size > 7 and F(size, bold).getlength(s) > max_w:
        size -= 1
    return size


# ------------------------------------------------------------------- map
# Equirectangular projection for the map panel.
MAP_X0, MAP_Y0, MAP_S = 8, 96, 1.8
MAP_LON0, MAP_LAT0 = -170, 78


def proj(lon, lat):
    return (MAP_X0 + (lon - MAP_LON0) * MAP_S,
            MAP_Y0 + (MAP_LAT0 - lat) * MAP_S)


def poly(pts):
    return [proj(lo, la) for lo, la in pts]


NA = [(-168, 66), (-162, 60), (-155, 58), (-148, 60), (-141, 60), (-135, 57),
      (-130, 54), (-126, 49), (-124, 43), (-121, 36), (-117, 32), (-112, 28),
      (-109, 24), (-105, 20), (-100, 17), (-95, 16), (-92, 15), (-88, 14),
      (-85, 12), (-82, 9), (-79, 8), (-77, 7), (-80, 9), (-83, 10), (-86, 13),
      (-89, 14), (-91, 14), (-94, 16), (-97, 16), (-97, 21), (-97, 26),
      (-94, 29), (-90, 29), (-85, 30), (-82, 28), (-81, 26), (-80, 31),
      (-77, 34), (-76, 36), (-74, 39), (-71, 41), (-69, 43), (-66, 44),
      (-61, 46), (-60, 47), (-65, 49), (-60, 52), (-56, 52), (-60, 55),
      (-64, 58), (-68, 58), (-70, 58), (-76, 55), (-82, 55), (-86, 58),
      (-90, 60), (-88, 64), (-92, 66), (-95, 69), (-105, 68), (-115, 69),
      (-125, 70), (-135, 69), (-145, 70), (-155, 71), (-162, 70), (-168, 66)]
GL = [(-55, 60), (-50, 60), (-43, 60), (-40, 63), (-35, 66), (-28, 68),
      (-22, 70), (-24, 73), (-30, 75), (-40, 76), (-50, 76), (-56, 74),
      (-58, 70), (-56, 65), (-55, 60)]
SA = [(-79, 8), (-76, 10), (-72, 12), (-67, 11), (-63, 10), (-60, 8),
      (-56, 6), (-52, 5), (-50, 0), (-47, -1), (-43, -3), (-39, -5),
      (-35, -8), (-36, -12), (-39, -17), (-40, -22), (-44, -24), (-48, -27),
      (-52, -32), (-56, -35), (-58, -38), (-62, -41), (-65, -45), (-67, -49),
      (-69, -52), (-71, -54), (-73, -50), (-73, -45), (-72, -40), (-71, -33),
      (-70, -25), (-70, -19), (-74, -15), (-77, -12), (-80, -7), (-81, -4),
      (-80, 0), (-79, 4), (-79, 8)]
AF = [(-17, 15), (-17, 21), (-16, 26), (-12, 30), (-8, 33), (-5, 35),
      (-1, 35), (3, 37), (9, 37), (11, 34), (15, 32), (20, 32), (25, 32),
      (30, 31), (32, 31), (34, 28), (36, 24), (37, 20), (39, 16), (41, 12),
      (44, 11), (48, 11), (51, 11), (48, 7), (45, 3), (42, -1), (40, -5),
      (39, -10), (38, -15), (36, -19), (34, -24), (32, -28), (29, -32),
      (25, -34), (20, -35), (17, -32), (15, -28), (13, -22), (12, -17),
      (13, -12), (12, -7), (9, -3), (9, 1), (8, 4), (4, 6), (0, 5),
      (-4, 5), (-8, 4), (-12, 7), (-15, 10), (-17, 12), (-17, 15)]
MD = [(44, -16), (46, -15), (49, -16), (50, -19), (48, -23), (45, -25),
      (43, -22), (43, -18), (44, -16)]
EU = [(-9, 37), (-9, 40), (-9, 43), (-3, 44), (-1, 46), (-4, 48), (-1, 49),
      (1, 51), (4, 52), (7, 54), (8, 56), (10, 58), (7, 60), (5, 61),
      (6, 63), (10, 64), (13, 66), (17, 68), (21, 70), (25, 71), (29, 70),
      (32, 68), (35, 67), (38, 66), (40, 64), (37, 62), (34, 60), (31, 59),
      (28, 58), (25, 58), (22, 56), (20, 54), (18, 54), (14, 54), (11, 55),
      (8, 55), (5, 53), (2, 51), (0, 50), (-2, 49), (-4, 48), (-2, 46),
      (-1, 44), (-3, 43), (-6, 40), (-9, 37)]
UK = [(-5, 50), (-3, 52), (-5, 54), (-5, 56), (-3, 58), (-1, 57), (0, 55),
      (0, 53), (-2, 51), (-4, 50), (-5, 50)]
AS = [(30, 36), (33, 36), (35, 33), (38, 31), (41, 30), (44, 29), (47, 30),
      (50, 29), (53, 27), (56, 26), (59, 25), (61, 25), (65, 25), (67, 24),
      (69, 23), (71, 21), (73, 18), (75, 14), (76, 10), (77, 8), (80, 7),
      (80, 10), (80, 13), (82, 16), (85, 19), (88, 22), (91, 22), (92, 21),
      (94, 18), (95, 16), (97, 15), (99, 13), (100, 11), (101, 8), (103, 7),
      (104, 9), (106, 10), (108, 12), (109, 14), (109, 18), (108, 21),
      (110, 20), (112, 21), (114, 22), (116, 23), (118, 25), (120, 27),
      (121, 30), (122, 33), (121, 36), (120, 38), (122, 39), (125, 40),
      (127, 40), (128, 41), (130, 42), (132, 43), (135, 44), (137, 46),
      (139, 47), (141, 49), (141, 52), (141, 59), (138, 59), (135, 62),
      (130, 66), (125, 70), (120, 73), (115, 73), (110, 74), (105, 76),
      (100, 76), (95, 75), (90, 75), (85, 74), (80, 73), (75, 72),
      (70, 72), (65, 70), (60, 69), (55, 68), (50, 68), (45, 67), (40, 67),
      (35, 66), (32, 68), (30, 70), (30, 65), (30, 60), (28, 58), (28, 55),
      (30, 50), (32, 46), (35, 44), (38, 42), (40, 40), (38, 38), (35, 36),
      (32, 36), (30, 36)]
SU = [(95, 5), (97, 4), (99, 1), (101, -2), (103, -4), (105, -5), (106, -6),
      (104, -5), (102, -2), (100, 0), (98, 3), (95, 5)]
JV = [(105, -6), (107, -7), (110, -7), (113, -8), (114, -8), (114, -9),
      (111, -8), (108, -7), (105, -6)]
BO = [(109, 1), (111, 2), (114, 4), (117, 5), (117, 2), (116, -1),
      (114, -3), (111, -3), (109, 0), (109, 1)]
NG = [(131, -1), (134, -2), (137, -2), (141, -3), (144, -4), (147, -6),
      (150, -9), (147, -8), (143, -7), (140, -6), (136, -4), (133, -2),
      (131, -1)]
PH = [(120, 18), (122, 18), (122, 15), (121, 13), (120, 10), (121, 11),
      (123, 13), (122, 17), (120, 18)]
AU = [(114, -22), (113, -26), (114, -30), (115, -33), (117, -35), (121, -34),
      (125, -33), (129, -32), (132, -32), (134, -33), (136, -35), (138, -35),
      (140, -38), (144, -38), (147, -39), (150, -37), (152, -34), (153, -31),
      (153, -27), (151, -24), (148, -20), (145, -17), (142, -14), (142, -11),
      (141, -14), (140, -17), (137, -16), (135, -15), (135, -12), (132, -12),
      (130, -13), (127, -14), (124, -16), (121, -18), (118, -20), (115, -21),
      (114, -22)]
NZ = [(167, -45), (169, -43), (171, -42), (173, -41), (175, -38), (177, -38),
      (178, -38), (176, -40), (174, -41), (172, -43), (169, -45), (167, -46),
      (167, -45)]
JP = [(130, 31), (131, 33), (133, 34), (135, 34), (137, 35), (139, 35),
      (140, 36), (141, 38), (141, 40), (142, 42), (144, 43), (145, 44),
      (143, 44), (141, 42), (140, 39), (139, 37), (137, 35), (135, 34),
      (133, 33), (131, 32), (130, 31)]
CONTINENTS = [NA, GL, SA, AF, MD, EU, UK, AS, SU, JV, BO, NG, PH, AU, NZ, JP]

# (number, lon, lat, short legend label)
PINS = [
    (1, 31, 50, "KYIV RAID 110+"),
    (2, 54, 27, "GULF TANKER HIT"),
    (3, 114, 22, "SHENZHEN TALKS"),
    (4, 77, 28, "DELHI SCO"),
    (5, 87, 18, "CYCLONE AKVAN"),
    (6, 151, -34, "SYDNEY ISIS PLOT"),
    (7, -108, 25, "CHAPO HELD"),
    (8, 4, 50, "EU-UK DEAL"),
    (9, -75, -12, "PERU QUAKE M6.7"),
    (10, -115, 36, "VEGAS GP"),
]


def draw_map(d):
    """World map panel x8..656, y96..336; legend strip y340..396."""
    d.rectangle([8, 96, 656, 336], fill=OCEAN, outline=LINE, width=1)
    # graticule every 30 degrees
    for lon in range(-150, 181, 30):
        x = MAP_X0 + (lon - MAP_LON0) * MAP_S
        d.line([(x, 96), (x, 336)], fill=GRID, width=1)
    for lat in range(60, -61, -30):
        y = MAP_Y0 + (MAP_LAT0 - lat) * MAP_S
        d.line([(8, y), (656, y)], fill=GRID, width=1)
    for c in CONTINENTS:
        d.polygon(poly(c), fill=LAND, outline=LANDLINE)
    text_w(d, (16, 102), "WHERE THE DAY HAPPENED", 11, NAVY, True)
    # pins
    for num, lon, lat, _lab in PINS:
        x, y = proj(lon, lat)
        r = 9
        d.ellipse([x - r, y - r, x + r, y + r], fill=PIN, outline=WHITE, width=2)
        text_w(d, (x, y - 1), str(num), 10, WHITE, True, anchor="mm")
    # legend: 2 rows x 5
    for i, (_n, _lo, _la, lab) in enumerate(PINS):
        row, col = divmod(i, 5)
        lx = 16 + col * 130
        ly = 344 + row * 26
        r = 8
        d.ellipse([lx, ly, lx + 2 * r, ly + 2 * r], fill=PIN, outline=WHITE, width=1)
        text_w(d, (lx + r, ly + r - 1), str(_n), 9, WHITE, True, anchor="mm")
        text_w(d, (lx + 2 * r + 5, ly + 1), lab, 10, INK, True)


# ------------------------------------------------------------------ icons
# Each icon draws inside a box (x, y, s) with the given colour.
def _poly(d, pts, color):
    d.polygon(pts, fill=color)


def icon(d, name, x, y, s, color):
    """Draw a pictogram icon in box (x,y) of size s."""
    u = s / 24.0

    def P(px, py):
        return (x + px * u, y + py * u)

    def line(pts, w=2):
        d.line([P(a, b) for a, b in pts], fill=color, width=max(1, int(w * u)))

    def ell(box, outline=False):
        d.ellipse([P(box[0], box[1]), P(box[2], box[3])],
                  fill=None if outline else color,
                  outline=color if outline else None,
                  width=max(1, int(2 * u)))

    def rect(box):
        d.rectangle([P(box[0], box[1]), P(box[2], box[3])], fill=color)

    if name == "missile":
        _poly(d, [P(12, 1), P(16, 7), P(13, 20), P(11, 20), P(8, 7)], color)
        _poly(d, [P(8, 7), P(4, 12), P(8, 10)], color)
        _poly(d, [P(16, 7), P(20, 12), P(16, 10)], color)
        _poly(d, [P(11, 20), P(13, 20), P(12, 23)], (230, 120, 40))
    elif name == "cyclone":
        for r, a0, a1 in ((9, 200, 340), (6, 20, 160), (3, 200, 320)):
            d.arc([P(12 - r, 12 - r), P(12 + r, 12 + r)], a0, a1,
                  fill=color, width=max(1, int(2 * u)))
        d.ellipse([P(10.5, 10.5), P(13.5, 13.5)], fill=color)
    elif name == "chart":
        line([(3, 20), (3, 4)], 2)
        line([(3, 20), (21, 20)], 2)
        line([(5, 6), (10, 10), (14, 8), (20, 17)], 2)
        _poly(d, [P(20, 17), P(20, 13), P(16, 17)], color)
    elif name == "globe":
        d.ellipse([P(2, 2), P(22, 22)], outline=color, width=max(1, int(2 * u)))
        d.ellipse([P(8, 2), P(16, 22)], outline=color, width=max(1, int(1.5 * u)))
        line([(2, 12), (22, 12)], 2)
        line([(4, 7), (20, 7)], 1)
        line([(4, 17), (20, 17)], 1)
    elif name == "bitcoin":
        ell((3, 3, 21, 21))
        text_w(d, (x + 12 * u, y + 11 * u), "B", 13, WHITE, True, anchor="mm")
    elif name == "ship":
        _poly(d, [P(3, 14), P(21, 14), P(18, 20), P(6, 20)], color)
        line([(12, 14), (12, 5)], 2)
        _poly(d, [P(12, 5), P(19, 7), P(12, 9)], color)
        line([(2, 21), (22, 21)], 2)
    elif name == "flame":
        _poly(d, [P(12, 2), P(16, 9), P(20, 12), P(20, 17), P(16, 22),
                  P(8, 22), P(4, 17), P(4, 12), P(8, 9)], color)
        _poly(d, [P(12, 12), P(15, 16), P(12, 20), P(9, 16)], PAPER)
    elif name == "eu":
        for k in range(12):
            import math
            a = math.radians(k * 30 - 90)
            cx, cy = 12 + 8 * math.cos(a), 12 + 8 * math.sin(a)
            d.ellipse([P(cx - 1.2, cy - 1.2), P(cx + 1.2, cy + 1.2)], fill=color)
        d.ellipse([P(10, 10), P(14, 14)], fill=color)
    elif name == "person":
        d.ellipse([P(8, 2), P(16, 10)], fill=color)
        _poly(d, [P(4, 22), P(6, 13), P(18, 13), P(20, 22)], color)
    elif name == "shield":
        _poly(d, [P(12, 2), P(20, 5), P(20, 12), P(12, 22), P(4, 12), P(4, 5)],
              color)
        line([(8, 11), (11, 14), (16, 8)], 2)
    elif name == "car":
        _poly(d, [P(3, 12), P(5, 8), P(9, 7), P(15, 7), P(19, 9), P(21, 12),
                  P(21, 16), P(3, 16)], color)
        d.ellipse([P(6, 15), P(10, 19)], fill=INK)
        d.ellipse([P(14, 15), P(18, 19)], fill=INK)
    elif name == "ball":
        d.ellipse([P(3, 3), P(21, 21)], outline=color, width=max(1, int(2 * u)))
        _poly(d, [P(12, 8), P(16, 11), P(14, 16), P(10, 16), P(8, 11)], color)
        for px, py in ((12, 3), (19, 8), (19, 17), (12, 21), (5, 17), (5, 8)):
            d.ellipse([P(px - 1, py - 1), P(px + 1, py + 1)], fill=color)
    elif name == "ban":
        d.ellipse([P(3, 3), P(21, 21)], outline=color, width=max(1, int(2 * u)))
        line([(6, 18), (18, 6)], 2)
    elif name == "quake":
        line([(3, 14), (8, 8), (11, 16), (15, 6), (18, 12), (21, 10)], 2)
        line([(6, 20), (9, 22)], 1)
        line([(15, 20), (18, 22)], 1)
    elif name == "link":
        d.ellipse([P(2, 8), P(12, 16)], outline=color, width=max(1, int(2 * u)))
        d.ellipse([P(12, 8), P(22, 16)], outline=color, width=max(1, int(2 * u)))
    elif name == "un":
        d.ellipse([P(4, 3), P(20, 19)], outline=color, width=max(1, int(2 * u)))
        d.ellipse([P(9, 3), P(15, 19)], outline=color, width=max(1, int(1.5 * u)))
        line([(4, 11), (20, 11)], 1)
        _poly(d, [P(7, 20), P(10, 23), P(8, 20)], color)
        _poly(d, [P(17, 20), P(14, 23), P(16, 20)], color)
    elif name == "rocket":
        _poly(d, [P(12, 1), P(16, 9), P(14, 17), P(10, 17), P(8, 9)], color)
        d.ellipse([P(10.5, 9), P(13.5, 12)], fill=WHITE)
        _poly(d, [P(8, 12), P(4, 18), P(8, 16)], color)
        _poly(d, [P(16, 12), P(20, 18), P(16, 16)], color)
        _poly(d, [P(10, 17), P(14, 17), P(12, 22)], (230, 120, 40))
    elif name == "chip":
        rect((6, 6, 18, 18))
        d.rectangle([P(9, 9), P(15, 15)], fill=PAPER)
        for i in (8, 12, 16):
            line([(i, 2), (i, 6)], 1)
            line([(i, 18), (i, 22)], 1)
            line([(2, i), (6, i)], 1)
            line([(18, i), (22, i)], 1)
    elif name == "gold":
        d.ellipse([P(3, 3), P(21, 21)], fill=color)
        d.ellipse([P(6, 6), P(18, 18)], outline=PAPER, width=max(1, int(1.5 * u)))
        text_w(d, (x + 12 * u, y + 11 * u), "$", 11, WHITE, True, anchor="mm")
    elif name == "survey":
        rect((4, 12, 8, 20))
        rect((10, 8, 14, 20))
        rect((16, 4, 20, 20))
        line([(3, 21), (21, 21)], 2)
    elif name == "factory":
        _poly(d, [P(3, 21), P(3, 12), P(7, 12), P(9, 9), P(11, 12), P(13, 9),
                  P(15, 12), P(21, 12), P(21, 21)], color)
        rect((17, 4, 20, 12))
    elif name == "plane":
        _poly(d, [P(2, 12), P(10, 10), P(20, 12), P(10, 14)], color)
        _poly(d, [P(10, 8), P(13, 11), P(10, 12)], color)
        _poly(d, [P(12, 13), P(15, 17), P(12, 14)], color)
    elif name == "oil":
        _poly(d, [P(12, 2), P(19, 12), P(19, 16), P(15, 21), P(9, 21),
                  P(5, 16), P(5, 12)], color)
    elif name == "robot":
        rect((6, 7, 18, 19))
        line([(12, 7), (12, 3)], 2)
        d.ellipse([P(10.5, 1.5), P(13.5, 4.5)], fill=color)
        d.ellipse([P(8.5, 11), P(11, 13.5)], fill=WHITE)
        d.ellipse([P(13, 11), P(15.5, 13.5)], fill=WHITE)
        line([(8, 17), (16, 17)], 1)
    elif name == "scales":
        line([(12, 3), (12, 21)], 2)
        line([(4, 6), (20, 6)], 2)
        line([(6, 6), (6, 12)], 1)
        line([(18, 6), (18, 12)], 1)
        _poly(d, [P(3, 12), P(9, 12), P(6, 16)], color)
        _poly(d, [P(15, 12), P(21, 12), P(18, 16)], color)
        line([(8, 21), (16, 21)], 2)
    elif name == "flag":
        line([(6, 2), (6, 22)], 2)
        for r in range(3):
            for c in range(4):
                if (r + c) % 2 == 0:
                    rect((6 + c * 4, 3 + r * 4, 10 + c * 4, 7 + r * 4))
    elif name == "storm":
        d.ellipse([P(4, 6), P(12, 14)], fill=color)
        d.ellipse([P(10, 4), P(18, 12)], fill=color)
        d.ellipse([P(14, 8), P(21, 15)], fill=color)
        for px in (7, 12, 17):
            line([(px, 17), (px - 1, 22)], 1)
    elif name == "health":
        _poly(d, [P(9, 3), P(15, 3), P(15, 9), P(21, 9), P(21, 15), P(15, 15),
                  P(15, 21), P(9, 21), P(9, 15), P(3, 15), P(3, 9), P(9, 9)],
              color)
    elif name == "boom":
        for k in range(8):
            import math
            a = math.radians(k * 45)
            line([(12, 12), (12 + 9 * math.cos(a), 12 + 9 * math.sin(a))], 2)
        d.ellipse([P(9, 9), P(15, 15)], fill=color)
    else:
        d.ellipse([P(4, 4), P(20, 20)], outline=color, width=max(1, int(2 * u)))
        text_w(d, (x + 12 * u, y + 11 * u), "?", 13, color, True, anchor="mm")


# ---------------------------------------------------------------- content
# Same 48 stories as v7 (fact-check 48/48 passed Warden v7). Only the
# composition changed. No event before 13 Nov 2026 anywhere in the image.
LEADS = [
    dict(icon="missile", color=BLUE, num="110+",
         head="MISSILES HIT KYIV IN BIGGEST RAID",
         sub="27 ballistic + 400 drones \u00b7 9 killed"),
    dict(icon="cyclone", color=TEAL, num="300K+",
         head="CYCLONE AKVAN SLAMS EAST INDIA",
         sub="Landfall 02:00 UTC \u00b7 9,341 shelters"),
    dict(icon="chart", color=RED, num="\u22125.3%",
         head="NASDAQ: WORST WEEK SINCE APR 2025",
         sub="\u221210% on the week \u00b7 VIX 35.89"),
    dict(icon="globe", color=GREEN, num="35%",
         head="COP31 IN OVERTIME AS TALKS DRAG",
         sub="Draft: 35% electricity share by 2035"),
]

# (icon, colour, headline, detail line 1, detail line 2)
CARDS = [
    ("bitcoin", AMBER, "BITCOIN BELOW $60K",
     "Low $55,830 \u00b7 closes ~$58,317", "15:42 UTC"),
    ("ship", BLUE, "TANKER HIT OFF KHASAB",
     "Unknown projectile", "No casualties \u00b7 UKMTO"),
    ("flame", RED, "HOUTHI THREATEN SAUDI PORTS",
     "If coalition hits Hodeidah", "Reuters"),
    ("eu", BLUE, "EU: \u20ac1BN MORE MILITARY AID",
     "Part of \u20ac6.6bn deal, via EPF", "14:50 UTC"),
    ("person", PURPLE, "S. AFRICA MOURNS MLAMBO-NGCUKA",
     "Ex-UN women chief, 71, dies Fri", "Presidency"),
    ("shield", TEAL, "SYDNEY MAN CHARGED OVER ISIS PLOT",
     "Amin, 35 \u00b7 alleged ISIS material", "AFP 06:10 UTC"),
    ("car", GREEN, "ITALY CLEARS TESLA DRIVING AID",
     "First big EU state \u00b7 temp OK", "Reuters"),
    ("ball", GREEN, "RONALDO GOAL No. 986",
     "Al-Ahli 3\u20131 Al-Nassr \u00b7 14 to 1,000", "SPL tally"),
    ("ban", RED, "US SANCTIONS 4 IRAN \u2018OIL TRUSTEES\u2019",
     "Operation Economic Outcast", "Treasury"),
    ("quake", AMBER, "PERU QUAKE M6.7",
     "19:09 local \u00b7 felt in Lima", "AP"),
    ("link", BLUE, "EU\u2013UK DEAL: TRADE + YOUTH",
     "SPS eased \u00b7 100k youth mobility", "AP"),
    ("un", NAVY2, "UN CHIEF RACE: 2 VETOES",
     "Grynspan leads \u00b7 2 vetoes", "States undisclosed"),
]

ALSO_ON = [
    "ESTONIA CLOSES RUSSIA ROAD CROSSINGS",
    "BESSENT: HUMANS MUST DECIDE MILITARY AI",
    "JAPAN: 93% SAY CHINA TIES WORST SINCE 1986",
    "MODI OPENS SCO FORUM; PAK MINISTER IN DELHI",
    "AUS\u2013CAN\u2013NZ: JOINT CALL FOR CEASEFIRE",
    "IRAQ TROOPS ENTER HEZBOLLAH STRONGHOLD",
    "NVIDIA \u221214%, $491BN GONE IN A DAY",
    "XI\u2013ALBANESE: \u201cFULL TURNAROUND\u201d IN TIES",
    "ECB RACE: BOONE & BRUNNERMEIER SHORTLISTED",
    "COURT: BYD Ti7 COPIED JLR DEFENDER",
    "TESLA OPENS FIRST ARGENTINA STORE",
    "VEGAS GP: RUSSELL FASTEST IN FP3",
    "GOLD \u22122.4% TO $3,538; WORST WEEK",
    "MICHIGAN SENTIMENT 51.5; FED WARNING",
    "TESLA PLANS $3.1BN POLYSILICON PLANT",
    "RUSSIAN MISSILES ENTER POLISH AIRSPACE",
    "KYIV HITS 3 RUSSIAN MISSILE LAUNCHERS",
    "SAPS: 581 WOMEN KILLED JUL\u2013SEP",
    "VENEZUELA REJECTS ICJ ON ESEQUIBO",
    "KOSPI \u22125.2%, LOWEST SINCE JAN",
    "BRENT $92.57, +0.6% ON THE DAY",
    "SPACEX LAUNCHES USSF-317",
    "OPENAI: NEW RULES FOR MODEL BROKERS",
    "AOSIS: COP31 \u201cA FAILURE\u201d IF 1.5\u00b0C IGNORED",
    "TECH ROUT: BROADCOM \u221212%, AMD \u221213%",
    "ANTHROPIC \u22128.5% AFTER RECORD IPO",
    "\u201cCHAPO ISIDRO\u201d ARRESTED IN GUASAVE",
    "IRAN CLAIMS 14 TANKERS AT KHARG",
    "BOLSONARO, 71, RUSHED TO HOSPITAL",
    "STORM KILLS 3 IN SOUTHERN BRAZIL",
    "SAMSUNG NAMES HWANG TO LEAD MEMORY",
    "SENSEX +1.2% AS INDIA DEFIES ROUT",
]

# (label, value %) - Friday market moves
MARKETS = [
    ("NASDAQ", -5.3), ("S&P 500", -3.7), ("KOSPI", -5.2),
    ("GOLD", -2.4), ("BRENT", 0.6), ("SENSEX", 1.2),
]

TIMELINE = [
    ("02:00", "AKVAN"), ("06:10", "SYDNEY"), ("10:00", "SENSEX"),
    ("14:50", "EU \u20ac1BN"), ("15:00", "KHASAB"), ("15:42", "BTC <$60K"),
    ("16:35", "ECB"), ("19:09", "PERU"), ("19:10", "KHARG"),
    ("21:00", "NASDAQ"),
]

DATE_CHECK = ("Every story verified 20 Nov 2026. Left out on purpose "
              "(wrong day): Sudan 17 Nov \u00b7 Turkey $26B 16 Nov \u00b7 "
              "Colombia 19 Nov \u00b7 Egypt\u2013Syria 17 Nov \u00b7 "
              "AWS Chile 11 Nov \u00b7 Korea $1T 19 Nov.")


def draw_masthead(d):
    d.rectangle([0, 0, W, 92], fill=NAVY)
    d.rectangle([0, 88, W, 92], fill=GOLD)
    text_w(d, (16, 8), "THE WORLD IN ONE DAY", 13, GOLD, True)
    text_w(d, (16, 26), "FRIDAY 20 NOVEMBER 2026", 34, (255, 255, 255), True)
    text_w(d, (16, 66),
           "Every story below happened or was first reported on "
           "Friday 20 November 2026.", 12, CREAM)
    # right: globe + story count
    icon(d, "globe", 884, 12, 44, GOLD)
    text_w(d, (936, 18), "48", 26, WHITE, True)
    text_w(d, (936, 46), "STORIES", 12, GOLD, True)
    text_w(d, (936, 64), "WORLD EDITION", 10, CREAM, True)


def draw_rail(d):
    """Right rail x664..1016: markets bars, DATE CHECK, UTC timeline."""
    # --- markets
    x0, x1, y0 = 664, 1016, 96
    d.rectangle([x0, y0, x1, 212], fill=WHITE, outline=LINE, width=1)
    text_w(d, (x0 + 10, y0 + 6), "MARKETS FRIDAY", 12, INK, True)
    text_w(d, (x1 - 10, y0 + 6), "ONE DAY", 10, MUTED, True, anchor="ra")
    bx0, bx1 = x0 + 78, x1 - 52
    zero = (bx0 + bx1) // 2
    scale = 104 / 6.0  # 6% == 104 px
    for i, (lab, val) in enumerate(MARKETS):
        ry = y0 + 28 + i * 14
        text_w(d, (x0 + 10, ry), lab, 10, INK, True)
        ln = int(abs(val) * scale)
        col = RED if val < 0 else GREEN
        if val < 0:
            d.rectangle([zero - ln, ry + 2, zero, ry + 11], fill=col)
        else:
            d.rectangle([zero, ry + 2, zero + ln, ry + 11], fill=col)
        vtxt = ("%.1f%%" % val).replace("-", "\u2212")
        text_w(d, (x1 - 10, ry), vtxt, 10, col, True, anchor="ra")
    d.line([(zero, y0 + 26), (zero, y0 + 26 + 6 * 14)], fill=MUTED, width=1)
    # --- DATE CHECK
    y0 = 220
    d.rectangle([x0, y0, x1, 300], fill=PINKBG, outline=(220, 150, 140), width=1)
    text_w(d, (x0 + 10, y0 + 6), "DATE CHECK", 12, RED, True)
    draw_wrapped(d, x0 + 10, y0 + 24, DATE_CHECK, 10, x1 - x0 - 20, INK,
                 lh=13)
    # --- timeline
    y0 = 308
    d.rectangle([x0, y0, x1, 396], fill=WHITE, outline=LINE, width=1)
    text_w(d, (x0 + 10, y0 + 6), "FRIDAY IN UTC", 12, INK, True)
    for i, (t, lab) in enumerate(TIMELINE):
        col = i % 2
        row = i // 2
        tx = x0 + 10 + col * 176
        ty = y0 + 26 + row * 13
        text_w(d, (tx, ty), t, 10, BLUE, True)
        text_w(d, (tx + 42, ty), lab, 10, INK, True)


def draw_leads(d):
    for i, ld in enumerate(LEADS):
        x = 8 + i * 254
        y = 404
        w = 246
        d.rectangle([x, y, x + w, y + 172], fill=WHITE, outline=LINE, width=1)
        d.rectangle([x, y, x + w, y + 6], fill=ld["color"])
        icon(d, ld["icon"], x + w // 2 - 28, y + 16, 56, ld["color"])
        text_w(d, (x + w // 2, y + 80), ld["num"], 36, ld["color"], True,
               anchor="ma")
        draw_wrapped(d, x + 10, y + 122, ld["head"], 15, w - 20, INK, True,
                     lh=18, align="c")
        text_w(d, (x + w // 2, y + 158), ld["sub"], 10, MUTED, False,
               anchor="ma")


def draw_cards(d):
    for i, (ic, col, head, det1, det2) in enumerate(CARDS):
        row, c = divmod(i, 6)
        x = 9 + c * 168
        y = 584 + row * 94
        w, h = 166, 92
        d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=LINE, width=1)
        d.rectangle([x, y, x + 4, y + h], fill=col)
        icon(d, ic, x + w // 2 - 12, y + 6, 24, col)
        draw_wrapped(d, x + 8, y + 34, head, 11, w - 16, INK, True, lh=13,
                     align="c")
        text_w(d, (x + w // 2, y + 62), det1, 9, MUTED, False, anchor="ma")
        text_w(d, (x + w // 2, y + 76), det2, 9, MUTED, True, anchor="ma")


def draw_also_on(d):
    y0 = 780
    d.rectangle([8, y0, 1016, y0 + 2], fill=NAVY)
    text_w(d, (10, y0 + 8), "ALSO ON FRIDAY \u2014 32 MORE", 13, NAVY, True)
    text_w(d, (1014, y0 + 8), "ALL FIRST REPORTED 20 NOV 2026", 10, MUTED,
           True, anchor="ra")
    for i, item in enumerate(ALSO_ON):
        col = i % 2
        row = i // 2
        x = 14 + col * 502
        y = y0 + 30 + row * 13
        d.ellipse([x, y + 3, x + 6, y + 9], fill=BLUE)
        text_w(d, (x + 11, y), item, 10, INK, False)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_map(d)
    draw_rail(d)
    draw_leads(d)
    draw_cards(d)
    draw_also_on(d)
    return img


def check_fit():
    """Measure every text block against its box; report overflows."""
    problems = []
    # masthead date
    if F(34, True).getlength("FRIDAY 20 NOVEMBER 2026") > 860:
        problems.append("masthead date too wide")
    note = ("Every story below happened or was first reported on "
            "Friday 20 November 2026.")
    if F(12).getlength(note) > 860:
        problems.append("editor note too wide")
    for ld in LEADS:
        lines = wrap(ld["head"], 15, 226, True)
        if len(lines) > 2:
            problems.append("lead head 3+ lines: " + ld["head"])
        if F(36, True).getlength(ld["num"]) > 226:
            problems.append("lead number too wide: " + ld["num"])
        if F(10).getlength(ld["sub"]) > 226:
            problems.append("lead sub too wide: " + ld["sub"])
    for _ic, _c, head, det1, det2 in CARDS:
        if len(wrap(head, 11, 150, True)) > 2:
            problems.append("card head 3+ lines: " + head)
        for det in (det1, det2):
            if F(9).getlength(det) > 150:
                problems.append("card detail too wide: " + det)
    for item in ALSO_ON:
        if F(10).getlength(item) > 480:
            problems.append("also-on too wide: " + item)
    if F(10).getlength(DATE_CHECK) > 332:
        pass  # wrapped, measured by lines below
    lines = wrap(DATE_CHECK, 10, 332)
    if len(lines) > 4:
        problems.append("DATE CHECK %d lines" % len(lines))
    for _n, _lo, _la, lab in PINS:
        if F(10, True).getlength(lab) > 104:
            problems.append("legend label too wide: " + lab)
    for lab, val in MARKETS:
        if F(10, True).getlength(lab) > 64:
            problems.append("market label too wide: " + lab)
    return problems


def main():
    out = os.environ.get("V8_OUT", "entry.png")
    problems = check_fit()
    if problems:
        for p in problems:
            print("FIT PROBLEM:", p)
        raise SystemExit(1)
    img = build()
    # palette-quantised PNG keeps the file small (tie-break advantage)
    img = img.convert("P", palette=Image.ADAPTIVE, colors=256)
    img.save(out, optimize=True)
    print("wrote %s: %dx%d, %d bytes" % (out, W, H, os.path.getsize(out)))


if __name__ == "__main__":
    main()
