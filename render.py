#!/usr/bin/env python3
"""Draw the Friday 20 November 2026 front page (40 stories, 6 continents).

Deterministic: no network, no clock, no randomness. Run `python3 render.py`
to regenerate entry.png next to this file. Raises if any text overflows its
box or the story count is wrong.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (26, 26, 26)
RED = (179, 35, 27)
NAVY = (20, 33, 61)
GRAY = (107, 107, 107)
LGRAY = (210, 205, 192)
PANEL_BG = (255, 253, 247)
SEA = (188, 216, 234)
LAND = (232, 220, 192)
LAND_LINE = (201, 185, 143)

FDIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FDIR, "dejavu/DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FDIR, "dejavu/DejaVuSerif.ttf")
SERIF_I = os.path.join(FDIR, "noto/NotoSerif-Italic.ttf")
SANS_B = os.path.join(FDIR, "dejavu/DejaVuSans-Bold.ttf")
SANS = os.path.join(FDIR, "dejavu/DejaVuSans.ttf")


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, fnt, width, lh, fill, max_lines):
    lines = wrap(d, text, fnt, width)
    if len(lines) > max_lines:
        raise ValueError("overflow %r -> %d lines (max %d)" % (text, len(lines), max_lines))
    for i, line in enumerate(lines):
        d.text((x, y + i * lh), line, font=fnt, fill=fill)
    return len(lines)


def star(d, cx, cy, r_out, r_in, n, fill):
    import math
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


# ---------------------------------------------------------------- data
STATS = [
    ("300,000+", "EVACUATED IN ODISHA"),
    ("-1,101", "DOW POINTS"),
    ("51-48", "SENATE IRAN VOTE"),
    ("$97.17", "ANTHROPIC CLOSE, +17%"),
    ("90 kmph", "AKVAN PEAK GUSTS"),
]

LEADS = [
    dict(n=1, tag="ASIA \u00b7 WEATHER",
         head="Cyclone Akvan slams into Odisha coast",
         sub="Landfall near Gopalpur, winds to 90 kmph; 300,000 evacuated to shelters.",
         cap="LANDFALL 07:30 IST \u00b7 GOPALPUR"),
    dict(n=2, tag="US \u00b7 IRAN",
         head="Trump puts Iran decision off until 2027",
         sub="Senate rejects war-powers curb, 51-48; Tehran rejects weapons claim.",
         cap="DECISION DEFERRED \u00b7 TO JANUARY 1"),
    dict(n=3, tag="EUROPE \u00b7 UKRAINE WAR",
         head="Kyiv hit by ballistic missiles overnight",
         sub="Three Dnipro bridges damaged; drone hits Kharkiv hospital, 4 hurt.",
         cap="OVERNIGHT STRIKES \u00b7 KYIV"),
]

PANELS = [
    dict(n=4, tag="MIDDLE EAST \u00b7 GULF",
         head="Tanker burns after mine strike; Riyadh tower hit",
         sub="Fire east of Hormuz; Houthi missile blows out PIF tower windows."),
    dict(n=5, tag="US \u00b7 MARKETS",
         head="Wall Street falls 2% as AI rally fades",
         sub="Dow -1,101 to 49,097, below 50,000; S&P's 6th straight loss."),
    dict(n=6, tag="TECH \u00b7 IPO",
         head="Anthropic debuts up 17% on Nasdaq",
         sub="Opened $111.50 on $83 price; closed $97.17."),
    dict(n=7, tag="WORLD \u00b7 JUSTICE",
         head="UN court: Myanmar guilty of Rohingya genocide",
         sub="ICJ's first such ruling against a state; refugees cheer."),
    dict(n=8, tag="CLIMATE \u00b7 COP31",
         head="COP31 draft drops fossil fuels",
         sub="Cut from 144 to 80 paragraphs; $120bn target gone; no deal yet."),
    dict(n=9, tag="EUROPE \u00b7 DIPLOMACY",
         head="Europe ready for Russia talks, leaders say",
         sub="Berlin backs united stance; winter ceasefire on the table."),
    dict(n=10, tag="ITALY \u00b7 SECURITY",
         head="Drones halt flights at Genoa airport",
         sub="Unidentified drones spotted; airport suspends flights."),
    dict(n=11, tag="MIDDLE EAST \u00b7 GAZA",
         head="Israel raids Gaza pocket; Hamas cries violation",
         sub="One-day operation beyond ceasefire line; tunnel destroyed."),
    dict(n=12, tag="OCEANIA \u00b7 SPORT",
         head="Nicholls ton rescues NZ against India",
         sub="113 not out in Wellington; Phillips 94 not out; NZ 243 for 5."),
]

ALSO = [
    "Houthis claim strikes on 4 Saudi targets",
    "Three killed in drone attack on Saratov",
    "One dead, 15 hurt in French flat fire",
    "Israel hits Hezbollah missile site in Lebanon",
    "Girl, 3, rescued 8 hrs after Tbilisi blast",
    "California probes Nvidia over China AI chips",
    "Venezuela signs military deal with US",
    "Trump pardons baseball legend Pete Rose",
    "Fiona the hippo dies at Cincinnati Zoo",
    "Harris meets Macron in Paris",
    "White House names Kirsten Davies cyber chief",
    "Quebecor bids C$31bn for Telus",
    "Japan core inflation hits 2.2% in October",
    "1 in 4 children live in conflict zones",
    "French Greens back M\u00e9lenchon for president",
    "Mob kills crash survivor in Osun, Nigeria",
    "Cumin sodas challenge cola giants in India",
    "Europe: use pledged climate cash for Africa",
    "Voices from besieged Yemeni city \u2014 BBC",
    "Zverev first into ATP Finals semis, Turin",
    "Trump, Xi, Putin hail \u2018peace declaration\u2019",
    "Vance moved off Iran diplomacy brief",
    "Netanyahu presses US for new Iran strikes",
    "Iran rejects US chemical-weapons claim",
    "Bitcoin slips to $62,150",
    "ANC weighs Gauteng power-sharing deal",
    "Sensex, Nifty open lower on Wall St sell-off",
    "Barrett to earn 150th All Blacks cap",
]
assert len(LEADS) == 3 and len(PANELS) == 9 and len(ALSO) == 28
assert len(LEADS) + len(PANELS) + len(ALSO) == 40

# map pins: (x, y) in the 300x192 map box
PINS = {
    1: (212, 81), 2: (72, 57), 3: (172, 40), 4: (192, 74), 5: (86, 48),
    6: (40, 55), 7: (140, 28), 8: (164, 54), 9: (157, 28), 10: (148, 46),
    11: (176, 68), 12: (287, 172),
}


# ------------------------------------------------------- illustrations
def ill_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 238, 247))
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(127, 179, 213))
    cx, cy = x + int(w * 0.60), y + 52
    for r, a0 in [(14, 200), (24, 140), (34, 80), (44, 20)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 250, fill=(255, 255, 255), width=4)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255))
    d.polygon([(x, y + h), (x + 95, y + int(h * 0.55)), (x + 150, y + h)], fill=(232, 220, 192))
    for i in range(9):
        rx = x + 18 + i * 30
        d.line([rx, y + 12, rx - 8, y + 30], fill=(150, 190, 220), width=2)
    for i in range(5):
        wx = x + 170 + i * 26
        d.arc([wx, y + h - 26, wx + 22, y + h - 12], 180, 360, fill=(255, 255, 255), width=2)


def ill_iran(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    bx, by = x + 18, y + h - 58
    d.rectangle([bx, by, bx + 128, by + 58], fill=(245, 244, 238))
    for i in range(5):
        cx0 = bx + 12 + i * 24
        d.rectangle([cx0, by + 18, cx0 + 9, by + 58], fill=NAVY)
    d.polygon([(bx - 6, by + 18), (bx + 134, by + 18), (bx + 64, by - 14)], fill=(245, 244, 238))
    d.ellipse([bx + 44, by - 34, bx + 84, by + 2], fill=(245, 244, 238))
    d.rectangle([bx + 62, by - 52, bx + 66, by - 32], fill=(245, 244, 238))
    d.polygon([(bx + 66, by - 52), (bx + 86, by - 46), (bx + 66, by - 40)], fill=RED)
    d.rounded_rectangle([x + 168, y + 16, x + 276, y + 92], radius=6, fill=(255, 255, 255))
    d.rectangle([x + 168, y + 16, x + 276, y + 38], fill=RED)
    d.text((x + 222, y + 20), "JAN", font=F(SANS_B, 13), fill=(255, 255, 255), anchor="ma")
    d.text((x + 222, y + 42), "1", font=F(SERIF_B, 34), fill=INK, anchor="ma")
    d.text((x + 222, y + 96), "2027", font=F(SANS_B, 20), fill=(255, 255, 255), anchor="ma")


def ill_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(43, 58, 85))
    d.rectangle([x, y + int(h * 0.55), x + w, y + h], fill=(74, 107, 138))
    d.rectangle([x, y + int(h * 0.52), x + w, y + int(h * 0.58)], fill=(245, 197, 66))
    d.rectangle([x, y + 62, x + w, y + 68], fill=(20, 20, 20))
    for px in (x + 40, x + 150, x + 255):
        d.rectangle([px, y + 68, px + 8, y + 96], fill=(20, 20, 20))
        d.line([px + 4, y + 62, px - 26, y + 30], fill=(20, 20, 20), width=2)
        d.line([px + 4, y + 62, px + 34, y + 30], fill=(20, 20, 20), width=2)
    star(d, x + 210, y + 34, 26, 10, 8, (245, 197, 66))
    star(d, x + 210, y + 34, 14, 6, 8, (224, 123, 57))
    star(d, x + 70, y + 22, 15, 6, 8, (245, 197, 66))
    d.line([x + 250, y + 8, x + 285, y + 34], fill=(255, 255, 255), width=2)
    d.line([x + 268, y + 4, x + 296, y + 22], fill=(255, 255, 255), width=2)
    for i in range(4):
        wx = x + 30 + i * 60
        d.arc([wx, y + h - 18, wx + 26, y + h - 6], 180, 360, fill=(255, 255, 255), width=2)


def ill_panel(d, x, y, w, h, n):
    if n == 4:  # gulf: tanker + tower
        d.rectangle([x, y, x + w, y + h], fill=(127, 179, 213))
        d.rectangle([x + 8, y + 34, x + 58, y + 52], fill=(20, 20, 20))
        d.rectangle([x + 40, y + 24, x + 52, y + 34], fill=(20, 20, 20))
        star(d, x + 30, y + 22, 12, 5, 7, (245, 197, 66))
        d.rectangle([x + 66, y + 8, x + 88, y + 58], fill=(120, 120, 120))
        star(d, x + 77, y + 8, 9, 4, 6, RED)
    elif n == 5:  # markets: falling chart
        d.rectangle([x, y, x + w, y + h], fill=(255, 253, 247))
        d.line([(x + 8, y + 14), (x + 30, y + 24), (x + 52, y + 20), (x + 74, y + 44), (x + 88, y + 56)],
               fill=RED, width=4)
        for bx, bh in [(10, 18), (34, 12), (58, 26), (76, 34)]:
            d.rectangle([x + bx, y + h - 8 - bh, x + bx + 12, y + h - 8], fill=RED)
    elif n == 6:  # ipo: rising arrow
        d.rectangle([x, y, x + w, y + h], fill=(230, 243, 230))
        d.line([(x + 12, y + 56), (x + 44, y + 30), (x + 62, y + 38), (x + 84, y + 12)],
               fill=(34, 139, 34), width=5)
        d.polygon([(x + 84, y + 12), (x + 68, y + 12), (x + 84, y + 28)], fill=(34, 139, 34))
        d.text((x + 14, y + 8), "$", font=F(SANS_B, 18), fill=(34, 139, 34))
    elif n == 7:  # justice: courthouse
        d.rectangle([x, y, x + w, y + h], fill=(232, 228, 216))
        d.polygon([(x + 8, y + 26), (x + 88, y + 26), (x + 48, y + 8)], fill=(90, 90, 90))
        for cx0 in (16, 40, 64):
            d.rectangle([x + cx0, y + 30, x + cx0 + 8, y + 60], fill=(90, 90, 90))
        d.rectangle([x + 8, y + 60, x + 88, y + 66], fill=(90, 90, 90))
    elif n == 8:  # cop31: globe
        d.rectangle([x, y, x + w, y + h], fill=(220, 238, 247))
        d.ellipse([x + 24, y + 10, x + 72, y + 58], fill=(74, 144, 190))
        d.ellipse([x + 32, y + 20, x + 46, y + 32], fill=(96, 180, 96))
        d.ellipse([x + 50, y + 38, x + 64, y + 50], fill=(96, 180, 96))
        star(d, x + 80, y + 14, 8, 3, 6, (245, 197, 66))
    elif n == 9:  # diplomacy: three flags
        d.rectangle([x, y, x + w, y + h], fill=(245, 244, 238))
        for i, (c1, c2) in enumerate([((179, 35, 27), (255, 255, 255)),
                                      ((20, 60, 140), (255, 255, 255)),
                                      ((200, 30, 30), (245, 197, 66))]):
            fx = x + 10 + i * 28
            d.rectangle([fx, y + 12, fx + 3, y + 58], fill=(90, 90, 90))
            d.rectangle([fx + 3, y + 12, fx + 25, y + 30], fill=c1)
            d.rectangle([fx + 3, y + 21, fx + 25, y + 30], fill=c2)
    elif n == 10:  # genoa: runway + drone
        d.rectangle([x, y, x + w, y + h], fill=(220, 238, 247))
        d.rectangle([x, y + 44, x + w, y + 58], fill=(90, 90, 90))
        for dx in (12, 38, 64):
            d.rectangle([x + dx, y + 49, x + dx + 14, y + 53], fill=(255, 255, 255))
        d.ellipse([x + 38, y + 16, x + 58, y + 28], fill=(20, 20, 20))
        for rx, ry in [(34, 12), (62, 12), (34, 30), (62, 30)]:
            d.ellipse([x + rx, y + ry, x + rx + 6, y + ry + 6], fill=(20, 20, 20))
        d.line([(x + 76, y + 10), (x + 90, y + 24)], fill=RED, width=4)
        d.line([(x + 90, y + 10), (x + 76, y + 24)], fill=RED, width=4)
    elif n == 11:  # gaza: buildings + smoke
        d.rectangle([x, y, x + w, y + h], fill=(238, 222, 180))
        d.rectangle([x + 10, y + 30, x + 34, y + 62], fill=(120, 110, 90))
        d.rectangle([x + 40, y + 18, x + 62, y + 62], fill=(150, 140, 115))
        d.ellipse([x + 62, y + 8, x + 76, y + 22], fill=(120, 120, 120))
        d.ellipse([x + 70, y + 2, x + 86, y + 18], fill=(150, 150, 150))
        d.rectangle([x + 68, y + 40, x + 88, y + 62], fill=(90, 85, 70))
    elif n == 12:  # cricket: pitch, bat, ball
        d.rectangle([x, y, x + w, y + h], fill=(96, 160, 96))
        d.rectangle([x + 30, y + 6, x + 66, y + 64], fill=(210, 190, 150))
        d.line([(x + 34, y + 14), (x + 62, y + 14)], fill=(255, 255, 255), width=2)
        d.line([(x + 34, y + 56), (x + 62, y + 56)], fill=(255, 255, 255), width=2)
        d.polygon([(x + 44, y + 26), (x + 52, y + 24), (x + 58, y + 44), (x + 50, y + 46)], fill=(150, 100, 50))
        d.ellipse([x + 74, y + 44, x + 82, y + 52], fill=RED)


ILL = {1: ill_cyclone, 2: ill_iran, 3: ill_kyiv}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    polys = [
        # North America
        [(2, 13), (25, 7), (42, 4), (62, 4), (75, 3), (92, 19), (96, 34), (87, 44),
         (79, 59), (75, 72), (67, 81), (61, 87), (54, 81), (46, 66), (37, 52), (37, 37),
         (25, 22), (4, 22)],
        # Greenland
        [(100, 2), (124, 2), (124, 9), (100, 9)],
        # South America
        [(75, 96), (92, 96), (100, 111), (112, 118), (108, 140), (96, 163), (87, 177),
         (83, 190), (79, 170), (83, 140), (75, 118), (75, 103)],
        # Europe
        [(133, 58), (133, 46), (142, 37), (150, 30), (158, 22), (167, 7), (175, 10),
         (167, 22), (165, 44), (158, 52), (150, 55), (142, 58)],
        # UK
        [(138, 32), (142, 28), (144, 36), (140, 40)],
        # Africa
        [(127, 89), (133, 66), (142, 59), (150, 56), (158, 63), (167, 65), (171, 69),
         (177, 93), (184, 94), (182, 111), (175, 126), (171, 140), (165, 160), (158, 163),
         (156, 154), (152, 137), (149, 113), (149, 105), (135, 103), (131, 99)],
        # Asia
        [(175, 10), (192, 7), (217, 0), (242, 3), (267, 4), (292, 7), (292, 22),
         (275, 30), (258, 52), (254, 59), (250, 66), (242, 74), (233, 81), (229, 96),
         (225, 99), (221, 89), (217, 78), (212, 81), (208, 89), (206, 99), (204, 81),
         (200, 74), (192, 74), (187, 69), (183, 66), (179, 66), (177, 59), (175, 52),
         (171, 49), (167, 44)],
        # Australia
        [(237, 129), (250, 129), (260, 130), (267, 145), (269, 152), (267, 167),
         (258, 169), (250, 160), (242, 163), (237, 156), (237, 144)],
    ]
    for p in polys:
        pts = [(x + px, y + py) for px, py in p]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    for px, py in [(233, 100), (240, 104), (228, 106), (282, 168), (286, 176)]:
        d.ellipse([x + px - 2, y + py - 2, x + px + 2, y + py + 2], fill=LAND)
    f_pin = F(SANS_B, 8)
    for n, (px, py) in PINS.items():
        col = RED if n <= 3 else NAVY
        d.ellipse([x + px - 8, y + py - 8, x + px + 8, y + py + 8], fill=col, outline=(255, 255, 255))
        d.text((x + px, y + py), str(n), font=f_pin, fill=(255, 255, 255), anchor="mm")


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28
    CW = W - 2 * M

    # header
    d.text((M, 12), "THE WORLD'S DAY IN PICTURES", font=F(SANS_B, 13), fill=RED)
    d.text((W - M, 14), "ONE-PAGE FRONT \u00b7 EDITION OF FRIDAY", font=F(SANS_B, 11),
           fill=GRAY, anchor="ra")
    d.line([(M, 34), (W - M, 34)], fill=INK, width=2)
    d.text((M, 42), "FRIDAY 20 NOVEMBER 2026", font=F(SERIF_B, 56), fill=INK)
    d.text((M, 108), "Every story on this page happened or was first reported on this day.",
           font=F(SERIF_I, 15), fill=INK)
    d.rectangle([M, 130, W - M, 156], fill=RED)
    d.text((W // 2, 135), "40 STORIES \u00b7 6 CONTINENTS \u00b7 ONE DAY", font=F(SANS_B, 15),
           fill=(255, 255, 255), anchor="ma")

    # stat strip
    col_w = CW / 5.0
    for i, (num, lab) in enumerate(STATS):
        cx = M + col_w * i + col_w / 2
        d.text((cx, 164), num, font=F(SANS_B, 19), fill=RED, anchor="ma")
        d.text((cx, 190), lab, font=F(SANS_B, 9), fill=GRAY, anchor="ma")
        if i:
            d.line([(M + col_w * i, 164), (M + col_w * i, 204)], fill=LGRAY, width=1)
    d.line([(M, 212), (W - M, 212)], fill=LGRAY, width=1)

    # leads
    lead_w, gap = 309, 20
    for i, lead in enumerate(LEADS):
        x = M + i * (lead_w + gap)
        ILL[lead["n"]](d, x, 222, lead_w, 112)
        d.rectangle([x, 314, x + lead_w, 334], fill=INK)
        d.text((x + lead_w // 2, 318), lead["cap"], font=F(SANS_B, 9),
               fill=(255, 255, 255), anchor="ma")
        d.text((x, 344), str(lead["n"]), font=F(SANS_B, 11), fill=RED)
        tw = d.textlength(str(lead["n"]), font=F(SANS_B, 11))
        d.text((x + tw + 6, 344), lead["tag"], font=F(SANS_B, 11), fill=RED)
        block(d, x, 364, lead["head"], F(SERIF_B, 25), lead_w, 28, INK, 3)
        block(d, x, 450, lead["sub"], F(SANS, 12), lead_w, 15, INK, 2)

    # panels 3x3
    pw, ph, pgap = 309, 70, 20
    for r in range(3):
        for c in range(3):
            p = PANELS[r * 3 + c]
            x = M + c * (pw + pgap)
            y = 488 + r * (ph + 6)
            d.rectangle([x, y, x + pw, y + ph], fill=PANEL_BG, outline=LGRAY)
            ill_panel(d, x, y, 96, ph, p["n"])
            tx = x + 96 + 10
            twd = pw - 96 - 10 - 6
            d.text((tx, y + 3), str(p["n"]) + "  " + p["tag"], font=F(SANS_B, 9), fill=RED)
            block(d, tx, y + 16, p["head"], F(SANS_B, 13), twd, 15, INK, 2)
            block(d, tx, y + 47, p["sub"], F(SANS, 10), twd, 12, INK, 2)

    # bottom divider + headers
    d.line([(M, 716), (W - M, 716)], fill=INK, width=2)
    d.text((M, 724), "WHERE IT HAPPENED", font=F(SANS_B, 13), fill=RED)
    d.text((348, 724), "ALSO ON FRIDAY 20 NOVEMBER", font=F(SANS_B, 13), fill=RED)

    # map + legend
    draw_map(d, M, 746, 300, 192)
    ly = 946
    d.ellipse([M, ly + 2, M + 10, ly + 12], fill=RED)
    d.text((M + 14, ly), "Leads 1-3", font=F(SANS, 10), fill=INK)
    d.ellipse([M + 86, ly + 2, M + 96, ly + 12], fill=NAVY)
    d.text((M + 100, ly), "Stories 4-12", font=F(SANS, 10), fill=INK)
    d.text((M, ly + 15), "Pins show where the day's biggest stories happened.",
           font=F(SANS, 9), fill=GRAY)

    # also list, two columns
    f_num = F(SANS_B, 10)
    f_txt = F(SANS, 10)
    for col in range(2):
        cx = 348 + col * 334
        for j in range(14):
            idx = col * 14 + j
            num = 13 + idx
            yy = 746 + j * 16
            d.text((cx, yy), str(num), font=f_num, fill=RED)
            tw = d.textlength(str(num), font=f_num)
            block(d, cx + tw + 5, yy, ALSO[idx], f_txt, 334 - tw - 5 - 8, 13, INK, 1)

    # date check + footer
    d.rectangle([M, 976, W - M, 994], fill=(233, 228, 214))
    d.text((W // 2, 979), "DATE CHECK \u00b7 Every story here happened or was first reported on Friday 20 November 2026.",
           font=F(SANS_B, 10), fill=INK, anchor="ma")
    d.text((M, 1000), "Sources: Reuters, AP, AFP, IMD, ICJ, UN News, Le Monde.",
           font=F(SANS, 9), fill=GRAY)
    d.text((W - M, 1000), "Independent summary; claims attributed. Original drawings.",
           font=F(SANS, 9), fill=GRAY, anchor="ra")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    import base64
    with open(out, "rb") as f:
        raw = f.read()
    b64 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png.b64")
    with open(b64, "w") as f:
        f.write(base64.b64encode(raw).decode("ascii"))
    print("wrote", out, os.path.getsize(out), "bytes")
    print("wrote", b64, os.path.getsize(b64), "bytes")


if __name__ == "__main__":
    build()
